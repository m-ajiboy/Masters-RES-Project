"""Generates AMIRIS_Germany2027_Build_Documentation.docx - the Word version of the build
documentation, with an embedded chart demonstrating the hard coal price conversion.
"""
from docx import Document
from docx.shared import Pt, Cm, RGBColor, Inches
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml.ns import qn
from docx.oxml import OxmlElement

NAVY = RGBColor(0x1F, 0x3A, 0x4D)
AMBER = RGBColor(0xA5, 0x69, 0x1F)
GREY = RGBColor(0x55, 0x5B, 0x58)
GOOD = RGBColor(0x3A, 0x6B, 0x47)
BAD = RGBColor(0x96, 0x3C, 0x28)
WHITE = RGBColor(0xFF, 0xFF, 0xFF)
FONT = "Calibri"


def shade(cell, hex_color):
    tcPr = cell._tc.get_or_add_tcPr()
    shd = OxmlElement('w:shd')
    shd.set(qn('w:val'), 'clear')
    shd.set(qn('w:color'), 'auto')
    shd.set(qn('w:fill'), hex_color)
    tcPr.append(shd)


def style_run(run, size=9.5, bold=False, italic=False, color=None):
    run.font.size = Pt(size)
    run.font.bold = bold
    run.font.italic = italic
    run.font.name = FONT
    if color:
        run.font.color.rgb = color


def h1(doc, text):
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(16)
    p.paragraph_format.space_after = Pt(6)
    r = p.add_run(text)
    style_run(r, size=15, bold=True, color=NAVY)
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


def h2(doc, text):
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(10)
    p.paragraph_format.space_after = Pt(4)
    r = p.add_run(text)
    style_run(r, size=11, bold=True, color=AMBER)
    return p


def body(doc, text, italic=False, color=None):
    p = doc.add_paragraph()
    p.paragraph_format.space_after = Pt(8)
    r = p.add_run(text)
    style_run(r, size=10, italic=italic, color=color or RGBColor(20, 24, 22))
    return p


def callout(doc, label, text, color=BAD):
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(2)
    p.paragraph_format.space_after = Pt(1)
    r = p.add_run(label)
    style_run(r, size=9.5, bold=True, color=color)
    p2 = doc.add_paragraph()
    p2.paragraph_format.space_after = Pt(8)
    r2 = p2.add_run(text)
    style_run(r2, size=9.5, italic=True, color=GREY)


def table(doc, headers, rows, widths_cm):
    t = doc.add_table(rows=1, cols=len(headers))
    t.alignment = WD_TABLE_ALIGNMENT.LEFT
    t.style = 'Table Grid'
    hdr = t.rows[0].cells
    for i, h in enumerate(headers):
        hdr[i].text = ""
        p = hdr[i].paragraphs[0]
        r = p.add_run(h)
        style_run(r, size=8.5, bold=True, color=WHITE)
        shade(hdr[i], "1F3A4D")
        p.paragraph_format.space_after = Pt(2)
        p.paragraph_format.space_before = Pt(2)
    for row_data in rows:
        cells = t.add_row().cells
        for i, val in enumerate(row_data):
            cells[i].text = ""
            p = cells[i].paragraphs[0]
            bold_first = val.startswith("**")
            if bold_first:
                val = val[2:]
            r = p.add_run(val)
            style_run(r, size=8.5, bold=bold_first, color=NAVY if bold_first else None)
            p.paragraph_format.space_after = Pt(2)
            p.paragraph_format.space_before = Pt(2)
    t.autofit = False
    for row in t.rows:
        for idx, w in enumerate(widths_cm):
            row.cells[idx].width = Cm(w)
    for idx, w in enumerate(widths_cm):
        t.columns[idx].width = Cm(w)
    doc.add_paragraph().paragraph_format.space_after = Pt(4)
    return t


doc = Document()
style = doc.styles['Normal']
style.font.name = FONT
style.font.size = Pt(10)

section = doc.sections[0]
section.left_margin = Cm(1.8)
section.right_margin = Cm(1.8)
section.top_margin = Cm(1.6)
section.bottom_margin = Cm(1.6)

# ---- Title ----
p = doc.add_paragraph()
r = p.add_run("AMIRIS Germany2027 - Build Documentation")
style_run(r, size=20, bold=True, color=NAVY)
p.paragraph_format.space_after = Pt(2)

p = doc.add_paragraph()
r = p.add_run("Every input's origin and validation, and the full record of what was copied, edited, or newly written across every YAML file")
style_run(r, size=11, italic=True, color=GREY)
p.paragraph_format.space_after = Pt(4)

p = doc.add_paragraph()
r = p.add_run("Muideen Oladayo Ajiboye  |  13 August 2026")
style_run(r, size=9, color=GREY)
p.paragraph_format.space_after = Pt(10)

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

body(doc, "Parts 1-6 cover the first built version of the Germany2027 scenario: no cross-border trade (gap #5, "
          "assumed zero), and a single BDEW-for-everything demand profile (V1). Parts 7-9 extend this with the "
          "two later builds: the component-split demand profile (V2) and the with-import cross-border variant, "
          "and give the full four-way comparison across every combination now built (V1/V2 demand x "
          "no-import/with-import).")

# =====================================================================
h1(doc, "How to Read the Source Labels Used Throughout")
table(doc,
    ["Label", "Meaning"],
    [
        ["**Brainpool (direct)", "Value taken straight from Amiris_Inputdata_EN.xlsx with no conversion."],
        ["**Brainpool (converted)", "Value taken from Brainpool's data but transformed - unit conversion, regional averaging, or capacity-weighted blending - before use."],
        ["**AMIRIS own", "Brainpool supplied nothing for this field. AMIRIS's own validated Germany2019 example scenario value was reused as the gap-fill."],
        ["**Researched (external)", "Neither Brainpool nor AMIRIS's own data covered this. A real external source was looked up (EEG/BNetzA auction rates, MaStR battery statistics, renewables.ninja cross-check)."],
        ["**Placeholder (flagged gap)", "No real figure exists anywhere yet (confirmed by research, not assumed). AMIRIS's own example value used as the least-bad stand-in."],
    ],
    [4.2, 12.6],
)

# =====================================================================
h1(doc, "Part 1 - Timeseries Inputs (the timeseries/ folder)")
h2(doc, "A. Fuel and carbon prices, worked example: hard coal")
body(doc, "The chart below demonstrates the conversion pipeline end to end for hard coal - Brainpool's raw "
          "monthly USD/tonne series (top) transformed into the EUR/MWh(thermal) series actually written into "
          "hard_coal_price.csv (bottom), using the formula: EUR/MWh = (USD/tonne ÷ that month's USD-per-EUR "
          "exchange rate) ÷ 8.141 MWh/tonne (the standard hard-coal calorific equivalent, ~29.3 GJ/t). "
          "January 2027: 90.90 USD/t at a rate of 1.1794 USD/EUR converts to 9.47 EUR/MWh.")
doc.add_picture("hard_coal_conversion_chart.png", width=Cm(15.5))
doc.add_paragraph().paragraph_format.space_after = Pt(6)

table(doc,
    ["File", "Source", "Method"],
    [
        ["**hard_coal_price.csv", "Brainpool (converted)", "See worked example above."],
        ["**oil_price.csv", "Brainpool (converted)", "Same method: USD/barrel ÷ USD/EUR rate ÷ 1.70 MWh/barrel (~5.8 MMBtu/barrel, standard Brent equivalent)."],
        ["**natural_gas_price.csv", "Brainpool (direct)", "'Natural Gas Germany [EUR/MWh]' column used as-is - already the correct unit."],
        ["**co2_price.csv", "Brainpool (direct)", "'EUA - EU Emission Allowance [EUR/tCO2]' column used as-is."],
        ["**Lignite fuel price", "AMIRIS own", "Flat 5.00 EUR/MWh. Brainpool has no lignite series - realistic, since lignite is domestically mined, not internationally traded."],
        ["**Nuclear fuel price", "N/A", "Omitted - 0 GW capacity (post phase-out)."],
    ],
    [4.0, 3.4, 9.4],
)

h2(doc, "B. Outage and must-run factors")
table(doc,
    ["Files", "Source", "Method"],
    [
        ["**lignite/hard_coal/natural_gas _outage.csv, _must_run.csv", "AMIRIS own", "Brainpool supplies no outage data. AMIRIS's own validated 2015-2019 files reused, calendar years shifted to 2027/2028/2029, values and month/day/time untouched."],
        ["**Oil outage", "AMIRIS own", "Flat 0.07 (7%), not a file - matches AMIRIS's own convention."],
    ],
    [6.0, 3.0, 7.8],
)

h2(doc, "C. Renewable generation profiles")
table(doc,
    ["File", "Source", "Method"],
    [
        ["**solar_openfield/rooftop_profile.csv", "Brainpool (converted)", "Regional average of the four PV_[type]_[region] columns per hour."],
        ["**wind_onshore_profile.csv", "Brainpool (converted)", "Regional average of the four Wind_[region] columns."],
        ["**wind_offshore_profile.csv", "AMIRIS own, validated", "No Brainpool shape exists. Implies 37.1% CF, inside the real 37-45% range (EnergyNumbers.info, Fraunhofer)."],
        ["**run_of_river_profile.csv", "AMIRIS own", "No Brainpool shape exists. AMIRIS's own profile reused, redated."],
        ["**biomass_profile.csv", "AMIRIS own", "No Brainpool shape exists. AMIRIS's own FROM_FILE dispatch profile reused, redated."],
    ],
    [5.0, 3.6, 8.2],
)

h2(doc, "D. Demand (load_v1_bdew.csv)")
table(doc,
    ["Component", "Value", "Source"],
    [
        ["Inflexible base demand", "604.85 TWh", "Brainpool (direct)"],
        ["Electrolysis (hydrogen)", "14.97 TWh", "Brainpool (direct)"],
        ["Electric mobility (EV charging)", "17.81 TWh", "Brainpool (direct)"],
        ["Heat pumps", "18.69 TWh", "Brainpool (direct)"],
        ["**Combined total used", "**656.32 TWh", "**Sum of the four rows above"],
    ],
    [6.5, 3.5, 6.8],
)
body(doc, "Method: demandlib's BDEW ElecSlp.get_scaled_power_profiles({'h0': 656,320,000 MWh}) - the BDEW "
          "Standardlastprofil methodology at 15-minute resolution, resampled to hourly. A round-trip check "
          "confirmed the file's hourly values sum back to exactly 656.32 TWh.")

# =====================================================================
h1(doc, "Part 2 - Conventional Fleet (Conventionals.yaml)")
table(doc,
    ["Field", "Lignite", "Hard Coal", "Nat. Gas", "Oil + Other Fossil"],
    [
        ["**Capacity (MW)", "13,927", "5,504", "36,237", "9,790 (1,540+8,250)"],
        ["**Block size (MW)", "500", "300", "200", "100"],
        ["**Efficiency", "0.3108-0.45", "0.339-0.492", "0.516-0.617", "0.311-0.397"],
        ["**Opex (EUR/MWh)", "2.0", "2.5", "1.2", "1.2"],
        ["**Markup band", "-60 to 0", "-15 to 5", "-10 to 10", "0 to 0"],
        ["**CO2 (t/MWh)", "0.407", "0.338", "0.202", "0.266"],
    ],
    [3.0, 3.4, 3.4, 3.4, 3.4],
)
callout(doc, "New gap surfaced while building:",
    "Brainpool's Variable_cost sheet covers fuel commodity prices, not variable OPERATING cost. "
    "AMIRIS's own opex figures were carried over for all four categories.")

# =====================================================================
h1(doc, "Part 3 - Renewable Fleet and Subsidies (RenewablesAndPolicy.yaml)")
table(doc,
    ["Agent", "Capacity", "Mechanism", "Rate", "Source"],
    [
        ["Solar Openfield", "119,179 MW", "MPVAR", "49 EUR/MWh", "BNetzA solar auction, Mar 2026"],
        ["Solar Rooftop", "33,706 MW", "FIT", "75 EUR/MWh", "EEG S49 degression, extrapolated - FLAGGED draft 2026 reform risk"],
        ["Wind Onshore", "90,232 MW", "MPVAR", "52 EUR/MWh", "BNetzA wind auctions, Feb-Aug 2026"],
        ["Wind Offshore", "12,573 MW", "MPVAR", "187 EUR/MWh", "PLACEHOLDER - no real 2027 figure exists"],
        ["Run-of-River", "4,161 MW", "FIT", "100 EUR/MWh", "AMIRIS own"],
        ["Biomass", "8,250 MW", "MPVAR", "197 EUR/MWh", "BNetzA biomass tender, Apr 2026"],
    ],
    [3.4, 3.0, 2.4, 3.0, 4.8],
)

# =====================================================================
h1(doc, "Part 4 - Storage Fleet (Storage.yaml)")
table(doc,
    ["Agent", "Power", "Duration", "Energy", "Efficiency"],
    [
        ["Pumped Hydro", "8,377.6 MW", "6.399h - AMIRIS own", "53,607.5 MWh", "87.5%/85.2%"],
        ["Battery", "5,151.7 MW", "2.0h - MaStR/RWE Hambach", "10,303.4 MWh", "95%/95%"],
        ["Reservoir Hydro", "1,540.0 MW", "111.22h - AMIRIS own", "171,282.2 MWh", "91%/91%"],
    ],
    [3.4, 3.0, 4.0, 3.4, 2.8],
)

# =====================================================================
h1(doc, "Part 5 - YAML File Construction")
table(doc,
    ["File", "Status", "What was done"],
    [
        ["**schema.yaml", "Copied unchanged", "Generic AMIRIS agent-type schema, no scenario-specific data."],
        ["**scenario.yaml", "Written new", "New Metadata, 2026-12-31 to 2027-12-31 window, PolicySet enum replaced with this build's six scheme names."],
        ["**Conventionals.yaml", "Written new", "Four fuel-type blocks. Nuclear and OCGT omitted entirely."],
        ["**RenewablesAndPolicy.yaml", "Written new", "Six operator agents, shared traders, SupportPolicy with six researched/gap-filled rates."],
        ["**Storage.yaml", "Written new", "Three GenericFlexibilityTrader agents."],
        ["**Demand.yaml", "Written new", "One DemandTrader, ValueOfLostLoad 3,000 EUR/MWh."],
        ["**MarketsAndForecast.yaml", "Written new", "Market/carbon/fuel/forecaster agents wired to Part 1 files."],
    ],
    [4.2, 3.2, 9.4],
)

table(doc,
    ["Contract file", "Status", "What was done"],
    [
        ["**conventionals.yaml", "Copied, edited", "ID lists trimmed to drop Nuclear and OCGT."],
        ["**demand.yaml", "Copied unchanged", "No edit needed."],
        ["**renewables_renewableTrader.yaml", "Copied, edited", "Trimmed to [60,70,80,52] - MPVAR agents."],
        ["**renewables_systemOperator.yaml", "Copied, edited", "Trimmed to [61,50] - FIT agents."],
        ["**renewables_noSupport.yaml", "NOT created", "Nothing routes through NoSupportTrader in this build."],
        ["**storage.yaml", "Copied, edited", "Trimmed to [700,701,702]."],
        ["**supportPolicy.yaml", "Copied, edited", "allMarketers trimmed to [11,13]."],
    ],
    [5.2, 3.2, 8.4],
)

# =====================================================================
h1(doc, "Part 6 - Validation and QA Performed")
body(doc, "Inspected AMIRIS's own existing timeseries files and YAMLs to confirm exact formats before writing "
          "any conversion code. Ran the scenario through amirispy's compile step (surfaces structural errors in "
          "seconds) before committing to a multi-minute full simulation.")

h2(doc, "Bug 1: missing SupportInstrument on the Biogas agent")
body(doc, 'Exception: "BiomassMpvar: Policy not configured for instrument null". Cause: AMIRIS\'s own Biogas '
          "entry never needed this attribute (routes through NoSupportTrader). This build gives it a real "
          "MPVAR subsidy, which requires the attribute explicitly. Fixed by adding SupportInstrument: MPVAR.")

h2(doc, "Bug 2: four renewable profiles never redated to 2027")
body(doc, "25.3% of hours cleared at the 3,000 EUR/MWh shortage ceiling. Diagnosis: picked a specific shortage "
          "hour and checked every agent's award - total awarded energy matched load served exactly, ruling out "
          "a bidding bug. Wind Offshore, Run-of-River, and Biomass all showed zero simultaneously; their source "
          "files still had 2019 timestamps, never redated, so they never overlapped the simulated calendar. "
          "Fixed by redating all four. Shortage hours fell to 15.9%, and negative prices appeared for the "
          "first time (108 hours).")

h2(doc, "Remaining shortage pattern: expected V1 behaviour, not a bug")
body(doc, "71% of remaining shortage hours fall in the 18:00-21:00 evening window - the signature of applying "
          "one household BDEW profile to the whole economy's demand. Reported as a V2 target, not chased "
          "further here.")

# =====================================================================
h1(doc, "Part 7 - Demand Profile V2 (Component-Split Build)")
body(doc, "V1 applied a single BDEW household (H0) Standardlastprofil to the entire 656.32 TWh combined demand "
          "total. V2 replaces this with a purpose-built shape for each of Brainpool's four demand components "
          "separately, then sums them (build_2027_demand_v2_split.py).")
table(doc,
    ["Component", "Value", "Method"],
    [
        ["**Inflexible base", "604.85 TWh", "Real 2023 ENTSO-E national load shape, rescaled hour-by-hour so the annual total matches the 2027 target. Keeps the real seasonal/hour-of-day pattern; day-of-week alignment between 2023 and 2027 is not preserved (a documented simplification)."],
        ["**Heat pumps", "18.69 TWh", "demandlib's BDEW HeatBuilding profile (temperature-driven), driven by real DWD Test Reference Year climate data bundled with demandlib, averaged across all 15 German climate regions (mean 8.5C, range -3.9C to 24.9C). Simplification: assumes a constant coefficient-of-performance (COP) across the year rather than modelling the real efficiency drop in cold weather."],
        ["**Electrolysis", "14.97 TWh", "Flat, constant hourly profile (1,708 MW every hour) - industrial electrolysers typically run close to constant for efficiency."],
        ["**E-mobility", "17.81 TWh", "An assumed, documented daily charging shape - evening-peaked (peak around 18:00), repeated identically every day. No seasonal or weekday/weekend variation modelled - the least standardised of the four components."],
    ],
    [3.2, 2.6, 11.2],
)
callout(doc, "Round-trip check:",
    "Combined total = 656.3172 TWh against a 656.3167 TWh target - matches to within rounding. Combined peak "
    "load = 106,178.7 MW, versus V1's 138,146.7 MW and Brainpool's own stated Annual Peak Load of 119,001 MW.",
    color=GOOD)
h2(doc, "Result: V2 materially reduces V1's shortage problem")
table(doc,
    ["Metric", "V1 (BDEW-for-everything)", "V2 (component-split)"],
    [
        ["**Peak load", "138,146.7 MW", "106,178.7 MW"],
        ["**Shortage hours (>=3000 EUR/MWh)", "1,391 (15.88%)", "659 (7.52%)"],
        ["**Negative-price hours", "108 (1.23%)", "884 (10.09%)"],
        ["**Mean price", "519.02 EUR/MWh", "285.58 EUR/MWh"],
        ["**Median price", "67.52 EUR/MWh", "77.19 EUR/MWh"],
    ],
    [5.6, 5.6, 5.8],
)
body(doc, "This confirms the diagnosis from Part 6: V1's shortage hours were concentrated in the 18:00-21:00 "
          "evening window because a household evening-peak shape had been applied to the whole economy's "
          "demand. Spreading the heat-pump, electrolysis, and EV components across their own, less peaky "
          "shapes removes most of that artificial peak, cutting shortage hours by more than half and mean "
          "price by 45%. New build: examples/backtest/Germany2027_DemandV2/, referencing load_v2_split.csv.")

# =====================================================================
h1(doc, "Part 8 - With-Import Cross-Border Variant (ImportTrader)")
body(doc, "Gap #5 assumed zero cross-border trade for the first build. This variant captures it: Brainpool's "
          "Capacity sheet gives 'Net Exports' = -43.90 TWh for 2027, i.e. Germany is projected to be a NET "
          "IMPORTER of 43.90 TWh - the same direction as the real 2023 outturn, where Germany was a net "
          "importer for the first time in decades (24.4 TWh net, from real ENTSO-E cross-border flow data "
          "pulled for this build).")
callout(doc, "Scope limitation, by design:",
    "AMIRIS's ImportTrader agent type can only ADD supply to the market. There is no ExportTrader for a "
    "single, uncoupled market zone, so this variant captures only the import side of cross-border trade. "
    "Modelling Germany's real export flows would require a full multi-zone MarketCoupling setup, judged out "
    "of scope for this build.",
    color=NAVY)
table(doc,
    ["Attribute", "Method"],
    [
        ["**AvailableEnergyForImport", "Real 2023 net cross-border flow (total physical imports minus exports, DE_LU vs all 11 neighbouring zones), clipped to zero (only the 5,014 real net-import hours are usable), rescaled to Brainpool's 43.90 TWh 2027 target. Preserves the real historical timing of import need."],
        ["**ImportCostInEURperMWH", "Real 2023 French day-ahead price (mean 96.86, min -134.94, max 276.12 EUR/MWh) as an import-cost proxy - France is Germany's largest, most stable single interconnector partner."],
    ],
    [4.5, 12.0],
)
h2(doc, "Finding: realized import volume falls well short of the offered 43.90 TWh")
body(doc, "AMIRIS's ImportTrader is a genuine price-competing bid, not a forced quantity - it only clears in "
          "hours where the German price would otherwise exceed the French price offered that hour.")
table(doc,
    ["Build", "Offered", "Awarded (cleared)", "Utilization"],
    [
        ["V1 demand + import", "43.90 TWh", "12.33 TWh", "28.09%"],
        ["V2 demand + import", "43.90 TWh", "7.40 TWh", "16.87%"],
    ],
    [5.6, 3.6, 4.6, 2.6],
)
callout(doc, "Reported as a finding, not a bug (explicit decision):",
    "This gap demonstrates a real divergence between Brainpool's fixed net-import ASSUMPTION and AMIRIS's "
    "endogenous, price-competitive DISPATCH of that same import capacity. V1's peakier demand shape pushes "
    "German prices above the French benchmark more often, so more of the offered import volume clears there "
    "(28.09%) than in V2 (16.87%), even though V2 is otherwise the more realistic demand build.",
    color=GOOD)
h2(doc, "Market impact of the imports that do clear")
table(doc,
    ["Metric", "V1 no-import", "V1 with-import", "V2 no-import", "V2 with-import"],
    [
        ["**Shortage hours", "15.88%", "11.78%", "7.52%", "5.35%"],
        ["**Negative-price hours", "1.23%", "1.68%", "10.09%", "14.60%"],
        ["**Mean price (EUR/MWh)", "519.02", "400.04", "285.58", "219.81"],
    ],
    [3.8, 3.2, 3.2, 3.2, 3.2],
)
body(doc, "Even the partial import volume that clears does real work: it relieves scarcity and pulls the mean "
          "price down materially (23-32%). Negative-price hours rise slightly with imports, since the French "
          "price series itself goes negative in some hours (min -134.94 EUR/MWh). New folders: "
          "examples/backtest/Germany2027_WithImport/ (V2+import) and examples/backtest/Germany2027_V1WithImport/ "
          "(V1+import), both compiled and ran with zero errors, agent Id 112.")

# =====================================================================
h1(doc, "Part 9 - Four-Way Version Matrix: Full Comparison")
body(doc, "All four combinations of the originally planned 2x2 build matrix (demand V1/V2 x no-import/with-"
          "import) are now built, compiled, and simulated end to end.")
table(doc,
    ["Build", "Peak load", "Shortage hrs", "Negative hrs", "Mean price", "Import cleared"],
    [
        ["**V1, no-import", "138,146.7 MW", "15.88%", "1.23%", "519.02", "n/a"],
        ["**V1, with-import", "138,146.7 MW", "11.78%", "1.68%", "400.04", "12.33 / 43.90 TWh"],
        ["**V2, no-import", "106,178.7 MW", "7.52%", "10.09%", "285.58", "n/a"],
        ["**V2, with-import", "106,178.7 MW", "5.35%", "14.60%", "219.81", "7.40 / 43.90 TWh"],
    ],
    [3.2, 2.8, 2.4, 2.4, 2.2, 3.2],
)
body(doc, "Demand shape (V1 vs V2) is the dominant driver of shortage relief - moving from V1 to V2 alone cuts "
          "shortage hours from 15.88% to 7.52% (no-import) and from 11.78% to 5.35% (with-import). "
          "Cross-border imports are a smaller, second-order effect on top of that, but still meaningfully "
          "reduce both shortage frequency and mean price within either demand version.")

# =====================================================================
h1(doc, "Part 10 - Complete List of Open Flags Across All Builds")
table(doc,
    ["#", "Flag"],
    [
        ["1", "Wind offshore subsidy (187 EUR/MWh) is a placeholder - no real 2027 figure exists anywhere."],
        ["2", "Solar rooftop FIT (75 EUR/MWh) assumes current EEG law continues; draft 2026 reform may end it."],
        ["3", "Natural gas modelled as one combined CCGT+OCGT block."],
        ["4", "Oil and Other Fossil merged; CO2 factor uses Oil's own value as proxy."],
        ["5", "Variable opex uses AMIRIS's own values for all four conventional categories."],
        ["6", "Battery efficiency (95%/95%) is a standard Li-ion assumption, not researched."],
        ["7", "'Other Renewables' assumed entirely biomass, no split for minor geothermal component."],
        ["8", "RESOLVED by V2: V1's peak (138.1 GW) exceeded Brainpool's stated peak (119.0 GW); V2 closes most of this gap (106.2 GW) - confirmed by simulation."],
        ["9", "Heat-pump profile (V2) assumes constant COP across the year - does not model the real efficiency drop in cold weather."],
        ["10", "E-mobility profile (V2) is an assumed daily shape, not sourced from real data, no seasonal/weekday variation."],
        ["11", "Import cost uses a single-neighbour proxy (real French price), not a flow-weighted mix of all 11 neighbouring zones."],
        ["12", "With-import builds model only the import side of cross-border trade - no ExportTrader for a single, uncoupled zone."],
        ["13", "Realized import volume (7.40-12.33 TWh) falls well short of the offered/Brainpool-target 43.90 TWh - a deliberate methodological finding, not forced to full dispatch."],
    ],
    [1.0, 15.8],
)

doc.save("AMIRIS_Germany2027_Build_Documentation.docx")
print("Saved AMIRIS_Germany2027_Build_Documentation.docx")
