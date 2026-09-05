"""Generates AMIRIS_Input_Data_Requirements.docx - a lean, table-first version
of the data request for Energy Brainpool cross-reference, for email to the supervisor.
"""
import sys
from docx import Document
from docx.shared import Pt, Cm, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml.ns import qn
from docx.oxml import OxmlElement

NAVY = RGBColor(0x1F, 0x3A, 0x4D)
AMBER = RGBColor(0xA5, 0x69, 0x1F)
GREY = RGBColor(0x55, 0x5B, 0x58)
WHITE = RGBColor(0xFF, 0xFF, 0xFF)

FONT = "Calibri"


def set_cell_shading(cell, hex_color):
    tcPr = cell._tc.get_or_add_tcPr()
    shd = OxmlElement('w:shd')
    shd.set(qn('w:val'), 'clear')
    shd.set(qn('w:color'), 'auto')
    shd.set(qn('w:fill'), hex_color)
    tcPr.append(shd)


def set_col_widths(table, widths_cm):
    table.autofit = False
    for row in table.rows:
        for idx, w in enumerate(widths_cm):
            row.cells[idx].width = Cm(w)
    for idx, w in enumerate(widths_cm):
        table.columns[idx].width = Cm(w)


def style_run(run, size=10.5, bold=False, italic=False, color=None, font=FONT):
    run.font.size = Pt(size)
    run.font.bold = bold
    run.font.italic = italic
    run.font.name = font
    if color:
        run.font.color.rgb = color


def add_heading(doc, text, level=1, color=NAVY, size=15, space_before=16, space_after=6):
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(space_before)
    p.paragraph_format.space_after = Pt(space_after)
    if level == 1:
        p.paragraph_format.border_bottom = None
    run = p.add_run(text)
    style_run(run, size=size, bold=True, color=color)
    if level == 1:
        pPr = p._p.get_or_add_pPr()
        pbdr = OxmlElement('w:pBdr')
        bottom = OxmlElement('w:bottom')
        bottom.set(qn('w:val'), 'single')
        bottom.set(qn('w:sz'), '8')
        bottom.set(qn('w:space'), '4')
        bottom.set(qn('w:color'), '1F3A4D')
        pbdr.append(bottom)
        pPr.append(pbdr)
    return p


def add_scope_note(doc, text):
    p = doc.add_paragraph()
    p.paragraph_format.space_after = Pt(8)
    run = p.add_run(text)
    style_run(run, size=10, italic=True, color=GREY)
    return p


def add_table(doc, headers, rows, widths_cm):
    table = doc.add_table(rows=1, cols=len(headers))
    table.alignment = WD_TABLE_ALIGNMENT.LEFT
    table.style = 'Table Grid'

    hdr_cells = table.rows[0].cells
    for i, h in enumerate(headers):
        hdr_cells[i].text = ""
        p = hdr_cells[i].paragraphs[0]
        run = p.add_run(h)
        style_run(run, size=9.5, bold=True, color=WHITE)
        set_cell_shading(hdr_cells[i], "1F3A4D")
        p.paragraph_format.space_after = Pt(2)
        p.paragraph_format.space_before = Pt(2)

    for row_data in rows:
        cells = table.add_row().cells
        for i, val in enumerate(row_data):
            cells[i].text = ""
            p = cells[i].paragraphs[0]
            run = p.add_run(val)
            bold_first = (i == 0)
            style_run(run, size=9.5, bold=bold_first, color=NAVY if bold_first else None)
            p.paragraph_format.space_after = Pt(2)
            p.paragraph_format.space_before = Pt(2)

    set_col_widths(table, widths_cm)
    doc.add_paragraph().paragraph_format.space_after = Pt(4)
    return table


def build():
    doc = Document()

    # base style
    style = doc.styles['Normal']
    style.font.name = FONT
    style.font.size = Pt(10.5)

    section = doc.sections[0]
    section.left_margin = Cm(1.8)
    section.right_margin = Cm(1.8)
    section.top_margin = Cm(1.6)
    section.bottom_margin = Cm(1.6)

    # Title block
    p = doc.add_paragraph()
    run = p.add_run("AMIRIS Input Data Requirements")
    style_run(run, size=22, bold=True, color=NAVY)
    p.paragraph_format.space_after = Pt(2)

    p = doc.add_paragraph()
    run = p.add_run("Data needed to cross-reference against the department's Energy Brainpool holdings")
    style_run(run, size=11.5, italic=True, color=GREY)
    p.paragraph_format.space_after = Pt(4)

    p = doc.add_paragraph()
    run = p.add_run("Muideen Oladayo Ajiboye  |  27 July 2026")
    style_run(run, size=9.5, color=GREY)
    p.paragraph_format.space_after = Pt(10)

    pPr = p._p.get_or_add_pPr()

    # divider
    divider = doc.add_paragraph()
    divider.paragraph_format.space_after = Pt(10)
    pBdr = OxmlElement('w:pBdr')
    bottom = OxmlElement('w:bottom')
    bottom.set(qn('w:val'), 'single')
    bottom.set(qn('w:sz'), '16')
    bottom.set(qn('w:space'), '1')
    bottom.set(qn('w:color'), '1F3A4D')
    pBdr.append(bottom)
    divider._p.get_or_add_pPr().append(pBdr)

    # Purpose (one tight paragraph, no preamble essay)
    p = doc.add_paragraph()
    run = p.add_run(
        "To test whether AMIRIS can reproduce the department's Energy Brainpool price results, "
        "we need to run AMIRIS on the same assumptions Brainpool used for an agreed year (e.g. 2019). "
        "Below is everything AMIRIS needs as input, grouped by category. For each item: the unit it "
        "should be in, the time resolution required, and what it is."
    )
    style_run(run, size=10.5)
    p.paragraph_format.space_after = Pt(4)

    p = doc.add_paragraph()
    run = p.add_run(
        "Please mark each row as available / partially available / not available in Brainpool's data. "
        "Where not available, AMIRIS's own sourced data will be substituted and documented as a limitation."
    )
    style_run(run, size=10.5)
    p.paragraph_format.space_after = Pt(2)

    headers = ["Data item", "Unit", "Resolution", "What it is"]
    widths = [3.6, 2.6, 3.2, 7.6]

    # A. Demand
    add_heading(doc, "A.  Electricity Demand")
    add_table(doc, headers, [
        ["Hourly load", "MW (or MWh/h)", "Hourly - 8,760 values/yr",
         "Total German electricity demand to be met each hour."],
    ], widths)

    # B. Conventional
    add_heading(doc, "B.  Conventional Fleet")
    add_scope_note(doc, "Needed separately for each of: Nuclear, Lignite, Hard coal, Natural gas, Oil.")
    add_table(doc, headers, [
        ["Installed capacity", "MW", "One value/yr (or per capacity change)",
         "Total capacity of that fuel type's fleet."],
        ["Efficiency", "% (LHV basis)", "One value or range per fuel type",
         "Share of fuel energy converted to electricity."],
        ["Typical block size", "MW per plant", "One value per fuel type",
         "Size of a single plant, used to split the fleet into individual units."],
        ["Variable operating cost", "EUR/MWh", "One value per fuel type",
         "Non-fuel cost of running the plant one more hour."],
        ["CO2 emissions factor", "t CO2/MWh", "One value per fuel type",
         "CO2 released per unit of electricity produced."],
        ["Outage / availability", "% unavailable", "Hourly if possible; monthly/seasonal acceptable",
         "Share of the fleet offline for maintenance or breakdown."],
    ], widths)

    # C. Renewables
    add_heading(doc, "C.  Renewable Fleet")
    add_scope_note(doc, "Needed separately for each of: Solar PV, Wind onshore, Wind offshore, Biomass, Run-of-river hydro, Other renewables.")
    add_table(doc, headers, [
        ["Installed capacity", "MW", "One value/yr (or per capacity change)",
         "Maximum possible output; split by subsidy vintage/scheme if available."],
        ["Generation profile", "MW/h or capacity factor (0-1)", "Hourly - 8,760 values/yr (most critical item)",
         "Actual weather-driven output shape, not just the capacity total."],
        ["Subsidy / support scheme", "EUR/MWh or scheme parameters", "One value per technology/vintage",
         "Fixed tariff or market top-up paid to the plant owner."],
    ], widths)
    p = doc.add_paragraph()
    run = p.add_run(
        "Note: Generation profile is the item most likely to be missing. If Brainpool only holds capacity "
        "totals, AMIRIS's own weather-driven profiles will convert them to hourly output - please confirm "
        "specifically whether an hourly (or monthly/seasonal) shape exists, separate from capacity."
    )
    style_run(run, size=9.5, italic=True, color=GREY)
    p.paragraph_format.space_after = Pt(6)

    # D. Storage
    add_heading(doc, "D.  Storage (Batteries, Pumped Hydro, etc.)")
    add_table(doc, headers, [
        ["Power capacity", "MW", "One value/yr", "Maximum charge/discharge rate."],
        ["Energy capacity", "MWh", "One value/yr", "Total amount storable."],
        ["Round-trip efficiency", "%", "One value", "Share of stored energy recovered on discharge."],
        ["Number of operators", "count", "One value, if available", "Single pooled operator vs. several competing ones."],
    ], widths)

    # E. Fuel & carbon prices
    add_heading(doc, "E.  Fuel and Carbon Prices")
    add_table(doc, headers, [
        ["Hard coal price", "EUR/MWh (thermal)", "Monthly or quarterly", "Cost of coal delivered to the plant, per unit of energy content."],
        ["Natural gas price", "EUR/MWh (thermal)", "Monthly or quarterly", "Cost of gas delivered to the plant, per unit of energy content."],
        ["Oil price", "EUR/MWh (thermal)", "Monthly or quarterly", "Cost of oil delivered to the plant, per unit of energy content."],
        ["CO2 allowance price", "EUR/tonne CO2", "Monthly or quarterly", "EU ETS carbon permit price."],
    ], widths)

    # F. Structural questions - short, bulleted, not a table (qualitative, not raw data)
    add_heading(doc, "F.  Also Needed: Modelling Assumptions")
    p = doc.add_paragraph()
    run = p.add_run("Not raw data, but assumptions behind Brainpool's numbers that affect the comparison:")
    style_run(run, size=10.5)
    p.paragraph_format.space_after = Pt(4)

    bullets = [
        "Cross-border trade - did Brainpool model import/export with neighbouring countries, or Germany standalone? (AMIRIS is currently standalone - a known source of price gap from our 2018 backtest.)",
        "Bidding behaviour - plants bid at production cost, or with a strategic markup?",
        "Negative prices - does Brainpool's output include them, and roughly how often?",
    ]
    for b in bullets:
        bp = doc.add_paragraph(style='List Bullet')
        run = bp.add_run(b)
        style_run(run, size=10)
        bp.paragraph_format.space_after = Pt(3)

    # Footer / next step
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(14)
    run = p.add_run(
        "Next: once reviewed, we build the AMIRIS scenario using Brainpool's assumptions wherever supplied, "
        "run it, and compare against Brainpool's price and the real historical price for that year."
    )
    style_run(run, size=10, italic=True, color=GREY)

    out_path = sys.argv[1] if len(sys.argv) > 1 else "AMIRIS_Input_Data_Requirements.docx"
    doc.save(out_path)
    print(f"Saved: {out_path}")


if __name__ == "__main__":
    build()
