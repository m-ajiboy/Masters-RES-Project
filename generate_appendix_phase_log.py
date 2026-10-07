"""Generates Appendix_A_ExperimentalPhaseLog.docx - a condensed, formal-register table
summarising all 52 phases of this project's experimental work, for review as a candidate
thesis appendix. One row per phase: what was tested, and the result. Full narrative detail
remains in AMIRIS_Germany2027_Progress_Report.pdf/.docx; this is a terse reference table only.
"""
import docx
from docx.shared import Pt, Cm, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml.ns import qn
from docx.oxml import OxmlElement

NAVY = RGBColor(0x1F, 0x3A, 0x4D)

PHASES = [
    (1, "Resolve five identified gaps in Brainpool's supplied 2027 input data (outages/must-run, offshore wind profile, renewable subsidy rates, battery storage duration, cross-border trade).",
     "All five resolved using AMIRIS's own reference data or independent research; cross-border trade deferred to a dedicated later build."),
    (2, "Build V1: full conventional and renewable fleet with a single BDEW household load profile applied to total demand, no cross-border import.",
     "Market cleared, but shortage pricing (3,000 EUR/MWh) occurred in 15.9% of hours."),
    (3, "Produce build documentation (input provenance, methodology Q&A).",
     "Documentation completed; no simulation result."),
    (4, "Build V2: replace the single demand profile with four separately shaped components (base load, heat pumps, electrolysis, e-mobility).",
     "Shortage hours fell from 15.9% to 7.5%."),
    (5, "Add an ImportTrader sized to Brainpool's stated net-import figure, shaped by 2023 cross-border flow data, to both V1 and V2.",
     "Shortage hours fell further, but only 7-12% of the intended import volume actually cleared the market."),
    (6, "Obtain Brainpool's real 2027 hourly price forecast and compare it against all four builds.",
     "AMIRIS's mean price was 3-7x Brainpool's; on the 92-95% of hours without a shortage, price levels were already close."),
    (7, "Diagnose the cause of the mean-price gap by inspecting a real shortage hour agent-by-agent.",
     "64% of shortage hours had zero import available; the import schedule was copied from an unrelated year."),
    (8, "Replace the shaped import series with a flat, market-determined hourly ceiling; calibrate the ceiling against Brainpool's price.",
     "V1 shortage hours 11.8% to 0.83%, mean price 400 to 75 EUR/MWh; V2 shortage hours 5.4% to 0.03%, mean price 220 to 57 EUR/MWh."),
    (9, "Test Brainpool's own reported 2009 weather-year basis for wind/solar, in place of AMIRIS's default.",
     "Mixed: closest-ever average price match (within 0.51 EUR/MWh) when combined with the import fix, but day-to-day pattern-matching did not improve."),
    (10, "Split the AMIRIS-Brainpool comparison by month, hour-of-day, and weekday/weekend to localise the residual gap.",
     "Found a approximately 39 EUR/MWh systematic weekday-vs-weekend gap, traced to unaligned calendar days in the demand-building step."),
    (11, "Shift the 2023 source data by five days so weekdays align with the 2027 calendar.",
     "The weekday/weekend gap narrowed by two-thirds; correlation and mean error both improved on trusted hours."),
    (12, "Replace generic climate-normal temperature with real 2009 hourly DWD temperature for the heat-pump demand component.",
     "No material effect (heat pumps are under 3% of total demand) - reported as a null result."),
    (13, "Inspect a real midday hour agent-by-agent to diagnose the midday price gap.",
     "Found differential renewable curtailment behaviour across subsidy types, and that the model has no mechanism to export surplus power abroad."),
    (14, "Build and test an experimental one-way virtual export device.",
     "Never activated across the simulated year; confirmed AMIRIS, as configured, cannot represent cross-border export without structural changes."),
    (15, "Verify Brainpool's published weather-year and model-scope assumptions; rebuild the import price as an 11-country real blend.",
     "2009 weather-year assumption confirmed correct; Brainpool's own model covers 30 countries. The 11-country blend gave a small, genuine improvement."),
    (16, "Test whether Germany's 2027 public holidays explain the residual price gap.",
     "An initial apparent pattern did not survive controlling for season and normal day-to-day variation - a genuine null result."),
    (17, "Identify the closest real weather-matched demand-source year to 2009 (candidates: 2015-2019, 2023) and rebuild demand on it.",
     "2016 was the best match (2023 the worst). Rebuilding on 2016 reduced shortage hours further; the trustworthy excl-shortage fit stayed flat."),
    (18, "Research the regulatory origin of AMIRIS's 3,000 EUR/MWh default shortage price.",
     "Confirmed as the real EU/ACER harmonised day-ahead price cap in force November 2017-May 2022, covering AMIRIS's own 2019 reference year."),
    (19, "Test the effect of raising the shortage price to the current real EU cap (5,000 EUR/MWh).",
     "Bias improved slightly, but all-hours correlation worsened (0.439 to 0.317); the excl-shortage comparison was unaffected either way. Not adopted."),
    (20, "Rebuild electrolysis as a price-responsive GenericFlexibilityTrader agent instead of flat demand.",
     "Shortage hours fell (4 to 1); all-hours correlation improved (0.439 to 0.553); excl-shortage correlation essentially unchanged."),
    (21, "Apply the same price-responsive pattern to e-mobility (smart charging).",
     "Shortage hours reached zero for the first time in the project; trustworthy correlation improved (0.640 to 0.647), a verified, non-artefactual result."),
    (22, "Test Reservoir Hydro's power-rating sensitivity (doubling/tripling its real 1.54 GW figure).",
     "Modest, consistent gains at each step, but the power-cap constraint (hit 35% of the year) never fully cleared even at 3x. Reported as a finding, not adopted."),
    (23, "Re-run the granular month/hour/weekday breakdown; investigate a newly observed July-October seasonal bias.",
     "The midday gap remained dominant despite added flexibility. Five candidate causes for the seasonal bias were ruled out; traced to the known single-zone-vs-30-country structural limitation."),
    (24, "Validate out-of-sample on 2028 and 2029 using Brainpool's newly supplied multi-year data, with no re-tuning.",
     "Price level held up across both years; correlation weakened with distance from the calibration year (0.647, 0.446, 0.349). A real AMIRIS leap-year limitation was also found and documented."),
    (25, "Isolate the out-of-sample correlation loss: test the import-ceiling value and the demand-source year as candidate causes.",
     "A full ceiling sweep found smaller ceilings give better 2028/2029 correlation but at a large shortage-hour cost; the demand-source year was ruled out as a driver."),
    (26, "Adopt a smaller (20,000 MW) import ceiling for 2028/2029, following the Phase 25 trade-off.",
     "Excl-shortage correlation improved sharply (to 0.705/0.698); adopted as a deliberate, documented exception to reusing the 2027 configuration unchanged."),
    (27, "Re-examine the Phase 26 adoption using all-hours statistics, not only excl-shortage.",
     "All-hours correlation and bias both worsened at smaller ceilings. 30,000 MW was re-adopted as the default for both years; the 20,000 MW results remain preserved as documented evidence."),
    (28, "Investigate a reversed weekday/weekend correlation pattern found in the 2028/2029 re-run of the Phase 10 breakdown.",
     "Found and fixed a genuine bug: dropping 29 February from the leap-year demand source misaligned every day from March onward (84% of the year). Clean improvement for 2027 and 2029, no trade-off."),
    (29, "Investigate a negative price floor as a lighter alternative to full market coupling, at the supervisor's suggestion.",
     "Confirmed the -500 EUR/MWh floor is hard-coded in AMIRIS's compiled engine. No tested floor value, including the supervisor's own suggested +10 EUR/MWh, improved correlation. Confirmed dead end."),
    (30, "Test a real, literature-sourced plant start-up/cycling cost for conventional generators.",
     "Output was byte-identical to the baseline across all 8,760 hours; the parameter is computed internally by AMIRIS but never reaches the single-zone bid-price logic. Confirmed dead end."),
    (31, "Sweep lignite's negative-bidding markup band (-60 to -10 EUR/MWh) against Germany's real negative-price frequency.",
     "Bias, MAE, and negative-hour frequency improved modestly and consistently as the band narrowed; the trustworthy excl-shortage correlation stayed flat. A working lever that does not move the key metric."),
    (32, "Scope a market-coupling build: study AMIRIS's own two-zone template; confirm real cross-border capacity data availability.",
     "Confirmed as a genuine, working AMIRIS mechanism. Scope decision: build one aggregate Rest-of-Europe zone first."),
    (33, "Source real Rest-of-Europe demand/capacity data (ENTSO-E, then Eurostat after an ENTSO-E outage).",
     "Confirmed a genuine multi-day ENTSO-E platform outage; substituted real Eurostat 2023 data for 9 of 10 neighbouring countries. Switzerland flagged as a confirmed data gap."),
    (34, "Build the first working market-coupling scenario, using a placeholder transmission capacity.",
     "Excl-shortage correlation rose to 0.7394 with 1 shortage hour - the first evidence coupling was worth pursuing, pending a real transmission figure."),
    (35, "Backfill real cross-border flow data and Switzerland's figures once the ENTSO-E outage resolved.",
     "Real 2023 bilateral flow data obtained for both directions of the DE-ROE link; the Swiss data gap closed."),
    (36, "Replace the Phase 34 placeholder with the real flow-derived transmission capacity.",
     "Shortage hours rose to 26, but excl-shortage correlation barely moved (0.7394 to 0.7288), confirming the Phase 34 gain was not a placeholder-capacity artefact."),
    (37, "Add real Rest-of-Europe storage (pumped/reservoir hydro) and renewable subsidy realism, mirroring Germany's own build.",
     "Mean price 67.45 EUR/MWh (Brainpool: 68.04); excl-shortage bias -2.90, MAE 16.69, correlation 0.72. The project's best result and the thesis's reference build."),
    (38, "Extend the Phase 37 build unchanged to 2028 and 2029 (frozen Rest-of-Europe methodology).",
     "Excl-shortage correlation held up well in both new years (0.7181, 0.7518); shortage hours grew with distance from 2027 (7, 17, 76)."),
    (39, "Test scaling the transmission ceiling to each year's own demand growth as a fix for rising out-of-sample shortage hours.",
     "Made 2028 worse. Rejected."),
    (40, "Test MarketCoupling's configurable per-iteration energy-shift limit as a candidate cause.",
     "Confirmed already effectively unlimited by default; tested directly and also rejected."),
    (41, "Test whether Rest-of-Europe's own storage runs physically dry during out-of-sample shortage hours.",
     "Storage never exceeded approximately 25% of its own discharge power during these hours. Rejected."),
    (42, "Disaggregate France from the aggregate Rest-of-Europe pool as its own named zone (star topology).",
     "Shortage hours rose sharply (7 to 167); bias worsened to +9.65. A genuine, informative negative result against unnecessary disaggregation."),
    (43, "Disaggregate all 10 real neighbouring countries (star topology), testing the Phase 42 prediction at full scale.",
     "Found and fixed a genuine AMIRIS engine bug (sub-scale dispatch failure). Result improved on the France-only pilot (shortage 167 to 120) but still fell short of Phase 37's simpler approach."),
    (44, "Rebuild the Rest-of-Europe zone on real 2024 data as a robustness check, isolating the data year as the only variable.",
     "Close to, but not better than, Phase 37 (correlation 0.7168 to 0.7066; shortage hours improved slightly, 7 to 5)."),
    (45, "Instrument AMIRIS's own source code at every exit point in the coupling algorithm; test against all 76 real 2029 shortage hours.",
     "Hypothesis of a hidden engine bug refuted: every stop traced to a legitimate cause (72% real supply exhaustion, 18% transmission ceiling, 9% a correctness guard)."),
    (46, "Source a real ENTSO-E ERAA growth trajectory for Rest-of-Europe demand/capacity/transmission, replacing the frozen 2024 snapshot.",
     "Mixed: 2028 shortage hours improved (17 to 10); 2029 worsened (76 to 89), traced to a genuine real-world decline in dispatchable capacity."),
    (47, "Test an alternative shortage-pricing convention (ShortagePriceMethod=LastSupplyPrice); diagnose the root cause of every remaining shortage hour.",
     "All-hours correlation rose from 0.3003 to 0.7167 with excl-shortage metrics unchanged. 4 of 7 shortage hours found transmission-ceiling-bound; the other 3 traced to forecaster blindness in Rest-of-Europe's storage agent."),
    (48, "Add 12 real bilateral Rest-of-Europe transmission links (24 directional) on top of the Phase 43 star topology.",
     "Shortage hours fell further (120 to 95); correlation stayed flat (0.7311 to 0.7297). Mesh outperforms star, but not Phase 37's aggregate approach."),
    (49, "Test a real, temperature-matched alternative demand-shape year against the Phase 37 reference.",
     "Every trusted metric moved the wrong way (shortage 7 to 26; correlation 0.7168 to 0.7104). Rejected."),
    (50, "Sweep 16 real years of wind-offshore weather data; test the single most promising candidate.",
     "Every trusted metric again moved the wrong way (shortage 7 to 12; correlation 0.7168 to 0.7124). Rejected."),
    (51, "Test a real alternative run-of-river hydro weather year, completing the renewable weather-year sweep.",
     "A near-wash, marginally worse on every metric (shortage 7 to 8). Completes a three-for-three negative result confirming Phase 37's choices were not fortuitous."),
    (52, "Patch AMIRIS's own Java source code directly to test whether Rest-of-Europe's storage could be made aware of Germany's shortage price (investigative only, not adopted into the thesis methodology).",
     "Best variant: shortage hours 7 to 6, bias -2.90 to -0.95; correlation/MAE remained slightly worse than the headline build in every variant tested, bounded by Rest-of-Europe storage's finite daily energy budget."),
]


def shade_cell(cell, hex_color):
    tcPr = cell._tc.get_or_add_tcPr()
    shd = OxmlElement("w:shd")
    shd.set(qn("w:val"), "clear")
    shd.set(qn("w:color"), "auto")
    shd.set(qn("w:fill"), hex_color)
    tcPr.append(shd)


d = docx.Document()
section = d.sections[0]
section.left_margin = Cm(2.5)
section.right_margin = Cm(2.5)
section.top_margin = Cm(2.5)
section.bottom_margin = Cm(2.5)
style = d.styles["Normal"]
style.font.name = "Times New Roman"
style.font.size = Pt(11)

note = d.add_paragraph()
r = note.add_run(
    "EDITORIAL NOTE (remove before submission): Draft candidate appendix, condensed from "
    "AMIRIS_Germany2027_Progress_Report.pdf/.docx into a single table, one row per phase, in "
    "formal register, for review before deciding whether to include it in the thesis. If "
    "adopted, renumber as Appendix A (or per the HSN template's own appendix convention), add "
    "a cross-reference from the relevant point in Chapter 3/4/5, and add it to the Table of "
    "Contents and (if used) the List of Tables."
)
r.italic = True
r.font.size = Pt(9)
r.font.color.rgb = RGBColor(0x80, 0x00, 0x00)

h = d.add_paragraph()
h.add_run("Appendix A: Experimental Phase Log").bold = True
d.paragraphs[-1].runs[0].font.size = Pt(16)
d.paragraphs[-1].runs[0].font.color.rgb = NAVY

intro = d.add_paragraph()
intro.add_run(
    "Table A.1 summarises, in chronological order, every distinct test or build phase carried "
    "out in the course of developing and validating the AMIRIS Germany 2027-2029 scenario "
    "described in Chapters 3-5, including phases whose result was negative or null. It is "
    "provided for transparency and reproducibility; the full narrative account, including the "
    "reasoning behind each design decision, is given in the relevant section of Chapters 3-6. "
    "Phase 52 is reported for completeness as an investigative finding only and was not adopted "
    "into the thesis's own methodology (see Section 6.x)."
)
intro.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY

cap = d.add_paragraph()
cap.add_run("Table A.1: Condensed log of all 52 experimental phases.").italic = True
cap.runs[0].font.size = Pt(10)

table = d.add_table(rows=1, cols=3)
table.style = "Table Grid"
table.alignment = WD_TABLE_ALIGNMENT.CENTER
widths = [Cm(1.5), Cm(7.0), Cm(7.5)]
headers = ["Phase", "Intervention / test", "Result"]
for i, htext in enumerate(headers):
    cell = table.rows[0].cells[i]
    cell.text = ""
    p = cell.paragraphs[0]
    run = p.add_run(htext)
    run.bold = True
    run.font.color.rgb = RGBColor(0xFF, 0xFF, 0xFF)
    run.font.size = Pt(10)
    shade_cell(cell, "1F3A4D")
    cell.width = widths[i]

for num, intervention, result in PHASES:
    row = table.add_row().cells
    row[0].text = str(num)
    row[0].paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.CENTER
    row[1].text = intervention
    row[2].text = result
    for c, w in zip(row, widths):
        c.width = w
        for p in c.paragraphs:
            for r in p.runs:
                r.font.size = Pt(9.5)

OUT = r"C:\Users\MuideenOA\Desktop\PyTut\Amiris\Write up\Thesis_Chapters_v1\Appendix_A_ExperimentalPhaseLog.docx"
d.save(OUT)
print(f"Saved {OUT}")
print(f"{len(PHASES)} phases written.")
