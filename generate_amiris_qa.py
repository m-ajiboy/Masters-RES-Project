"""Generates AMIRIS-QA.pdf - direct, detailed answers to a batch of clarification questions
raised while reviewing the Progress Report and supervisor deck. Every answer here is grounded
in the actual code/data, re-verified at the time of writing (not recalled from memory alone):
the import-ceiling implementation was confirmed directly from Import.yaml, the lignite bidding
formula and cycling-cost dead end from decompiled AMIRIS bytecode, the offshore-wind
correlation numbers and the import/export worked example from re-running the real analysis
scripts against the real result data."""
from fpdf import FPDF

NAVY = (31, 58, 77)
AMBER = (165, 105, 31)
GREY = (90, 96, 92)
LIGHT = (238, 240, 233)
GOOD = (58, 107, 71)
BAD = (150, 60, 40)

MARGIN = 15


class Doc(FPDF):
    def footer(self):
        self.set_y(-13)
        self.set_font("Helvetica", "I", 8)
        self.set_text_color(*GREY)
        self.cell(0, 8, f"AMIRIS Q&A - Clarifications on the Progress Report and Supervisor Deck                                    Page {self.page_no()}", align="C")

    def h1(self, text):
        if self.get_y() > 255:
            self.add_page()
        self.ln(3)
        self.set_font("Helvetica", "B", 14.5)
        self.set_text_color(*NAVY)
        self.set_x(MARGIN)
        self.multi_cell(0, 7, text)
        y = self.get_y()
        self.set_draw_color(*NAVY)
        self.set_line_width(0.6)
        self.line(MARGIN, y, 210 - MARGIN, y)
        self.ln(3.5)

    def question(self, text):
        if self.get_y() > 255:
            self.add_page()
        self.set_font("Helvetica", "BI", 10)
        self.set_text_color(*AMBER)
        self.set_x(MARGIN)
        self.multi_cell(0, 5.4, f'You asked: "{text}"')
        self.ln(2)

    def body(self, text):
        if self.get_y() > 260:
            self.add_page()
        self.set_font("Helvetica", "", 10.3)
        self.set_text_color(20, 24, 22)
        self.set_x(MARGIN)
        self.multi_cell(0, 5.6, text)
        self.ln(2)

    def subhead(self, text):
        if self.get_y() > 258:
            self.add_page()
        self.set_font("Helvetica", "B", 10.5)
        self.set_text_color(*NAVY)
        self.set_x(MARGIN)
        self.multi_cell(0, 5.6, text)
        self.ln(1)

    def callout(self, label, text, color=NAVY):
        if self.get_y() > 250:
            self.add_page()
        self.set_font("Helvetica", "B", 10.3)
        self.set_text_color(*color)
        self.set_x(MARGIN)
        self.multi_cell(0, 5.5, label)
        self.set_font("Helvetica", "", 10.3)
        self.set_text_color(20, 24, 22)
        self.set_x(MARGIN)
        self.multi_cell(0, 5.6, text)
        self.ln(2.5)

    def bullet(self, text, indent=0):
        if self.get_y() > 260:
            self.add_page()
        self.set_font("Helvetica", "", 10.3)
        self.set_text_color(20, 24, 22)
        self.set_x(MARGIN + indent)
        marker = "-  " if indent else "*  "
        self.multi_cell(0, 5.5, marker + text)
        self.ln(0.5)

    def table(self, headers, rows, widths):
        if self.get_y() > 240:
            self.add_page()
        self.set_x(MARGIN)
        self.set_font("Helvetica", "B", 9)
        self.set_fill_color(*NAVY)
        self.set_text_color(255, 255, 255)
        for h, w in zip(headers, widths):
            self.cell(w, 6.5, h, border=0, align="C", fill=True)
        self.ln()
        self.set_font("Helvetica", "", 9)
        for i, row in enumerate(rows):
            self.set_x(MARGIN)
            self.set_fill_color(*LIGHT) if i % 2 == 0 else self.set_fill_color(255, 255, 255)
            self.set_text_color(20, 24, 22)
            for cell, w in zip(row, widths):
                self.cell(w, 6, str(cell), border=0, align="C", fill=True)
            self.ln()
        self.ln(3)


pdf = Doc()
pdf.set_margins(MARGIN, 14, MARGIN)
pdf.set_auto_page_break(auto=True, margin=16)
pdf.add_page()

# ---- Title ----
pdf.set_font("Helvetica", "B", 20)
pdf.set_text_color(*NAVY)
pdf.set_x(MARGIN)
pdf.multi_cell(0, 10, "AMIRIS Q&A")
pdf.set_font("Helvetica", "I", 11.5)
pdf.set_text_color(*GREY)
pdf.set_x(MARGIN)
pdf.multi_cell(0, 5.8, "Direct, detailed answers to clarification questions raised while reviewing the Progress Report and supervisor deck")
pdf.set_font("Helvetica", "", 9.5)
pdf.set_x(MARGIN)
pdf.cell(0, 6, "9 September 2026", new_x="LMARGIN", new_y="NEXT")
pdf.ln(2)
y = pdf.get_y()
pdf.set_draw_color(*NAVY)
pdf.set_line_width(1)
pdf.line(MARGIN, y, 210 - MARGIN, y)
pdf.ln(5)
pdf.body(
    "Every answer below was checked directly against the real code, agent configuration files, "
    "or result data at the time of writing - not answered from memory alone. Where a figure or "
    "formula is stated, it was re-confirmed (re-reading the actual file, or re-running the "
    "actual analysis script) rather than assumed to still be accurate."
)

# =====================================================================
pdf.h1("1. How the Import Model Was Fixed and Calibrated")
pdf.question("How did we fix and calibrate the import model? Explain the code tweaked or process gone through.")
pdf.subhead("The bug (Phase 7)")
pdf.body(
    "The original import availability was not a flat ceiling - it was shaped hour-by-hour "
    "from real 2023 cross-border flow TIMING. Checking a real shortage hour directly showed "
    "the import trader offering 0 MW at exactly the hour AMIRIS ran short. Checked "
    "systematically: 301 of 469 shortage hours (64%) had zero import available - because "
    "2023's real flow pattern has no relationship to when this synthetic 2027 build happens "
    "to run short."
)
pdf.subhead("The fix (build_2027_import_fix.py)")
pdf.body(
    "Decoupled import availability from any historical timing entirely. AvailableEnergyForImport.csv "
    "became a flat constant (e.g. 30000.0000 every single hour), and ImportCostInEURperMWH.csv kept "
    "the real 2023 French day-ahead price series unchanged - so the CEILING is fixed, but how "
    "much of it actually gets used each hour is a genuine market outcome (AMIRIS's ImportTrader "
    "only imports when it is cheaper than domestic generation)."
)
pdf.subhead("Calibration")
pdf.body(
    "Swept 20,000 / 25,000 / 30,000 / 37,650 MW ceilings against Brainpool's real price. Found "
    "V1 and V2 needed DIFFERENT ceilings - V2 (better demand model) settled on 30,000 MW; V1 "
    "(cruder demand, higher structural peak) needed the full 37,649.98 MW (the real observed "
    "peak single-hour German gross import in 2023). Picked by MAE/correlation, not bias alone, "
    "since bias can hide poor hour-to-hour tracking behind cancelling errors."
)

# =====================================================================
pdf.h1("2. The Weekday/Weekend Mismatch")
pdf.question('"Found and fixed a weekday/weekend mismatch" - explain the mismatch and how it was fixed.')
pdf.subhead("The mismatch")
pdf.body(
    "The granular breakdown (Phase 10) found weekday hours biased -22.78 EUR/MWh vs. "
    "Brainpool, weekend hours +16.18 - a ~39 EUR/MWh systematic gap, even though correlation "
    "WITHIN each group was strong (0.64+). That pattern means the demand shape's calendar was "
    "misaligned, not that the shape itself was wrong."
)
pdf.subhead("Root cause")
pdf.body(
    "The 2023 source data was mapped onto 2027 POSITIONALLY - hour 1 of 2023 became hour 1 of "
    "2027, regardless of actual weekday. 2023-01-01 was a Sunday; 2027-01-01 is a Friday. So "
    "every 'weekday' in the model's calendar was actually built from a mix of real weekdays "
    "and weekends."
)
pdf.subhead("The fix (build_2027_demand_v2_weekday.py)")
pdf.body(
    "Shifted the 2023 source data by 5 days (120 hours, a circular roll) so 2023-01-06 (a "
    "Friday) becomes the new start - aligning every subsequent day's real weekday with the "
    "corresponding 2027 day. One tiny documented imperfection: the last ~5 days of the year "
    "wrap around a day off (365 mod 7 = 1), affecting under 0.1% of the year."
)

# =====================================================================
pdf.h1("3. The Two Subsidy Types and Their Oversupply Behaviour")
pdf.question('"Two solar/wind subsidy types behave very differently under oversupply" - what is the subsidy type and what was their behaviour?')
pdf.body("AMIRIS supports two real subsidy mechanisms, and this project uses both:")
pdf.bullet("MPVAR (market premium, variable) - the plant bids into the market like anyone else, gets whatever the market clears at, and receives a top-up subsidy on top. Under oversupply (very cheap or negative prices), MPVAR plants have a real incentive to CURTAIL - bidding high enough to get skipped rather than accept a near-zero or negative market price.")
pdf.bullet("FIT (feed-in tariff) - the plant gets a fixed, guaranteed price regardless of the market price. It has no incentive to curtail under oversupply - it just runs and gets paid its fixed rate.")
pdf.callout(
    "Found by inspecting a real midday hour agent-by-agent (Phase 13):",
    "MPVAR-subsidised renewables curtailed under the midday glut, FIT-subsidised ones did not "
    "- meaning FIT capacity kept adding to the oversupply exactly when it was already worst. "
    "(In this build: solar rooftop and run-of-river use FIT; wind onshore/offshore and solar "
    "openfield use MPVAR - matching Germany's real subsidy split.)",
)

# =====================================================================
pdf.h1("4. The Public Holiday Check")
pdf.question('"Checked public holidays" - what did we do, in terms of code, analysis, etc?')
pdf.body(
    "No separate saved build - this was a statistical check against the EXISTING price "
    "comparison, not a new simulation. Used Python's 'holidays' reference library to get "
    "Germany's 5 real nationwide 2027 public holidays that fall on a weekday (New Year's Day, "
    "Good Friday, Easter Monday, Ascension Day, Whit Monday), then compared AMIRIS-vs-"
    "Brainpool bias on those specific days against ordinary days."
)
pdf.callout(
    "First look was promising, but two follow-up checks killed it:",
    "(1) Controlling for month - all 5 holidays fall in Jan/Mar/May, months that already have "
    "smaller bias regardless of holidays, and New Year's Day actually looked WORSE than an "
    "ordinary January weekday once controlled. (2) Checking whether any holiday's bias sat "
    "meaningfully outside the normal day-to-day spread within its own month - none did. "
    "Genuine null result, not pursued further.",
    color=BAD,
)

# =====================================================================
pdf.h1("5. How 2016 Was Identified as the Closest Weather Match to 2009")
pdf.question("What did we do to know that 2016 weather data was the closest to 2009, how did we get that?")
pdf.body(
    "Pulled real hourly temperature (DWD, four German weather stations: north/east/middle/"
    "southwest) for 2009 and every candidate year with real German demand data available "
    "(2015-2019, 2023). Scored each candidate against 2009 on four measures: annual mean "
    "temperature, heating-degree-days, monthly-pattern RMSE, and hour-to-hour correlation."
)
pdf.callout(
    "Result:",
    "2023 (the year in use until then) was the WORST match of all six (monthly RMSE 3.37 C, "
    "HDD deficit -508). 2016 was the best (RMSE 2.31 C, HDD deficit -40). Full ranking: "
    "2016 < 2018 < 2017 < 2015 < 2019 < 2023 - notably, 2019 (which had been suggested as an "
    "alternative) was actually the second-worst.",
    color=GOOD,
)

# =====================================================================
pdf.h1("6. The Correlation Types Used Throughout the Project")
pdf.question("Define all the correlation types we have been considering, all hours, exclusive shortage, etc.")
pdf.bullet("All-hours correlation - every one of the 8,760 hours included. Problem: a handful of extreme shortage-price hours (near 3,000 EUR/MWh) can swing this a lot even when ordinary-hour tracking barely changed - a repeatedly-confirmed outlier-leverage artifact.")
pdf.bullet("Excl-shortage correlation - the same calculation with hours at the 3,000 EUR/MWh ceiling removed first. This became the project's trusted metric specifically because it is not distorted by those outliers.")
pdf.bullet("Weekday vs. weekend correlation - a split used to diagnose the calendar-alignment bug (Phase 10-11).")
pdf.bullet("Hour-to-hour correlation on a specific input series - e.g. the renewables.ninja cross-checks (r=0.90 onshore wind, r=0.97 solar, r=0.01 offshore wind) - a different use of the same statistic, checking two INPUT profiles against each other rather than AMIRIS's output against Brainpool's.")
pdf.bullet('"Match quality" in the supervisor deck is just plain language for excl-shortage correlation.')

# =====================================================================
pdf.h1("7. Building Price-Responsive Electrolysis and E-Mobility")
pdf.question('How did we build the "Built price-responsive electrolysis" and "Built price-responsive e-mobility (smart charging)"?')
pdf.body(
    "Both use the exact same real, proven pattern - a GenericFlexibilityTrader modelled as a "
    "one-way flexible consumer (the same pattern AMIRIS's own SectorCoupling demo uses for "
    "EVs/heat pumps):"
)
pdf.bullet("NetDischargingPowerInMW: 0 - never sells back to the grid, pure consumption.")
pdf.bullet("NetInflowPowerInMW - a constant negative drain representing the mandatory annual energy draw (electrolysis: -1,708.45 MW average = 14.966 TWh/yr; e-mobility: -2,032.78 MW average = 17.807 TWh/yr) - continuously depleting an internal energy buffer.")
pdf.bullet("An internal buffer (EnergyContentUpperLimitInMWH) that must be periodically recharged - electrolysis: 100,000 MWh (~2.4 days of slack); e-mobility: 40,000 MWh (~0.8 days - deliberately smaller, since EVs have real drivers who need their cars, unlike an industrial electrolyser).")
pdf.bullet("Assessment: MAX_PROFIT - the agent CHOOSES WHEN to recharge within its buffer's slack, preferring cheap/negative-price hours over a flat draw.")
pdf.callout(
    "Verified directly:",
    "Electrolysis hit 14.94 of 14.97 TWh target, peaking 09:00-13:00 (the exact midday "
    "surplus window); e-mobility hit 17.80 of 17.81 TWh, flipping from the old evening-peak "
    "'unmanaged charging' shape to a 09:00-13:00 peak / 17:00-19:00 trough - genuine "
    "behavioural change, not just a minor shift. E-mobility alone eliminated shortage hours "
    "completely for the first time in the project.",
    color=GOOD,
)

# =====================================================================
pdf.h1("8. Recap: The Seasonal Gap Investigation (Phase 23)")
pdf.question("Give a recap of the seasonal gaps we investigated and how we investigated it.")
pdf.body(
    "Re-ran the month/hour/weekday breakdown after the demand-side fixes were in place, to "
    "see where the REMAINING gap concentrated. Found three things: (1) the midday gap was "
    "still dominant (-41 EUR/MWh at 11:00) and barely moved despite ~33 TWh/year of new "
    "flexible demand - there is simply more midday surplus than that much shiftable demand "
    "can absorb; (2) weekday/weekend gap had shrunk to ~21 EUR/MWh but was not fully closed; "
    "(3) a NEW finding - a July-October seasonal bias (-17 to -23 EUR/MWh vs. -5 to -12 the "
    "rest of the year)."
)
pdf.callout(
    "For the seasonal gap, five specific causes were checked directly and ruled out one by one:",
    "Renewable output totals (stable, no anomaly), solar/wind mix (similar in both small-gap "
    "and large-gap months), import price level (actually cheap in Jul-Oct, not high), base "
    "demand levels (similar to May-June, which has a small gap), conventional plant "
    "availability (flat all year in this model). What the data DID show: Brainpool's real "
    "price climbs smoothly from May to September while AMIRIS's stays flat - traced to the "
    "same structural cause flagged earlier: Brainpool's real methodology couples ~30 "
    "countries' reservoir drawdown, outages, and gas-storage dynamics; a single-zone Germany "
    "model has no mechanism to reproduce that.",
    color=GREY,
)

# =====================================================================
pdf.h1("9. Cycling/Start-Up Cost, Explained Simply")
pdf.question('"Tested giving conventional plants a real start-up/cycling cost" - what is cycling/start-up cost? Explain the headline result in a simpler term.')
pdf.subhead("What it is")
pdf.body(
    "The real cost a power plant incurs turning off and back on - thermal stress, fuel for "
    "reheating, wear. A plant with a genuine start-up cost has a real incentive to keep "
    "running at a small loss (even bidding slightly negative) rather than shut down and pay "
    "to restart later."
)
pdf.subhead("Real numbers sourced")
pdf.body(
    "A peer-reviewed study (Roques/Hach et al., Nature Energy 2017) gave real figures - "
    "roughly EUR50,000-70,000 per start for a large lignite/coal block, EUR60,000 for gas - "
    "converted into AMIRIS's units (62.5/87.5/120 EUR/MW)."
)
pdf.callout(
    "Simple result:",
    "Built and ran the actual test. The output came back BYTE-IDENTICAL to the baseline - "
    "every one of the 8,760 hours, to the cent. Why: AMIRIS's own code genuinely calculates "
    "this cost internally, but that calculation is never actually plugged into the number a "
    "power plant offers when it bids into the market. Like flipping a light switch that was "
    "never wired to anything - the switch is real, the calculation happens, but nothing "
    "downstream ever uses it.",
    color=BAD,
)

# =====================================================================
pdf.h1("10. Data Gap Sources, and the Offshore Wind Cross-Check")
pdf.question("Provide the sources for the external data used to resolve data gaps, and how did we verify AMIRIS's wind offshore profile with renewables.ninja?")
pdf.body(
    "Real external sources used throughout: EEG (Erneuerbare-Energien-Gesetz, Germany's "
    "renewable law) and BNetzA (Bundesnetzagentur) auction data for subsidy rates; MaStR "
    "(Marktstammdatenregister) for battery storage duration; DWD (German weather service) "
    "for real temperature; renewables.ninja for real 2009 wind/solar weather; ENTSO-E and "
    "Eurostat for cross-border data (later, the market-coupling build)."
)
pdf.subhead("Offshore wind verification, specifically")
pdf.body(
    "Brainpool never supplied its own offshore shape at all - AMIRIS's own example "
    "wind_offshore_profile.csv was reused as a placeholder from the very start. The "
    "'verification' was comparing that reused placeholder against a genuine, independent "
    "real-2009-weather offshore profile pulled from renewables.ninja."
)
pdf.table(
    ["Technology", "Has a real Brainpool shape?", "Correlation vs. real 2009 weather"],
    [
        ["Wind onshore", "Yes", "r = 0.896"],
        ["Solar (openfield)", "Yes", "r = 0.968"],
        ["Wind offshore", "No - AMIRIS's own placeholder reused", "r = 0.012"],
    ],
    [65, 65, 60],
)
pdf.callout(
    "Honest finding:",
    "Offshore wind's correlation is essentially zero, even though the average capacity factor "
    "was in a similar ballpark (0.371 vs. 0.469). Offshore wind's shape is the one genuinely "
    "unverified assumption in the whole renewable build - flagged as such rather than glossed "
    "over.",
    color=AMBER,
)

# =====================================================================
pdf.h1("11. Where the Import Ceiling Is Actually Set")
pdf.question("The import ceiling tweaks - how were we implementing it? Are we setting the limit in the schema or scenario file, or just using a timeseries file?")
pdf.callout(
    "Confirmed directly from the agent file (Import.yaml):",
    "It is a plain ImportTrader agent whose AvailableEnergyForImport attribute points to a "
    "TIMESERIES CSV FILE, not a scalar value in the schema or scenario file. AMIRIS's schema "
    "does not offer a 'constant ceiling' attribute option - even a flat ceiling has to be "
    "written out as the same number repeated for all 8,760 hours (confirmed: "
    "AvailableEnergyForImport.csv literally contains '30000.0000' on every line). "
    "ImportCostInEURperMWH.csv is the same pattern, holding the real French day-ahead price "
    "series.",
    color=NAVY,
)

# =====================================================================
pdf.h1("12. The Lignite Bidding Formula")
pdf.question("What is the lignite bidding formula?")
pdf.callout(
    "Decompiled directly from ConventionalTrader.prepareBids:",
    "For each generation block: bid price = marginal cost + a linearly-interpolated markup, "
    "where the markup runs from minMarkup (applied to the cheapest block in the fleet) to "
    "maxMarkup (applied to the most expensive block). Lignite's minMarkup was -60 EUR/MWh - "
    "the widest negative-bidding allowance of any fuel (gas: -10, hard coal: -15) - confirmed "
    "as a genuine, working mechanism (unlike the cycling cost).",
    color=NAVY,
)
pdf.callout(
    "One caveat found in the same decompilation:",
    "Lignite's own marginal cost means even the full -60 markup can only push the bid to "
    "roughly -15 to -25 EUR/MWh - the deeper troughs actually observed (-66 to -85) come from "
    "a DIFFERENT mechanism: blocks tagged MustRunFactor bid at a flat -500 EUR/MWh regardless "
    "of markup.",
    color=AMBER,
)

# =====================================================================
pdf.h1("13. Data Sourced for the Market-Coupling Export Build")
pdf.question("What data did we source for the market coupling export build?")
pdf.bullet("Real Eurostat data (nrg_cb_e for demand, nrg_inf_epc for generation capacity by technology) for 9 of Germany's 10 real neighbours.")
pdf.bullet("Switzerland backfilled via ENTSO-E (Eurostat has no non-EU coverage).")
pdf.bullet("renewables.ninja for real 2009-weather wind/solar profiles per country, capacity-weighted.")
pdf.bullet("ENTSO-E cross-border physical flow data (after working through a real multi-day platform outage) to derive real transmission capacity.")
pdf.bullet("IHA 2023's real EU-wide pumped-storage share (30%) and Switzerland's real reservoir:run-of-river ratio (90.2:9.8) for the hydro storage split.")
pdf.bullet("Germany's own real BNetzA-auction subsidy levels, reused as the best available reference point (no separate per-country subsidy scheme was researched).")

# =====================================================================
pdf.h1("14. Every Export/Market-Coupling Variant Actually Tried")
pdf.question("Explain clearly all the various things/models we tried with export - placeholder, combining 10 countries, building each country individually, etc.")
pdf.callout("Phase 34 - Placeholder transmission",
            "First working two-zone build, a flat 30,000 MW guess (reused from the old import ceiling) for the border capacity.")
pdf.callout("Phase 36 - Real-flow transmission",
            "Replaced the guess with a real number derived from actual 2023 ENTSO-E flow data (98th percentile of hourly flow, ~21,600-22,000 MW).")
pdf.callout("Phase 37 - Real storage + subsidy (BEST RESULT)",
            "Gave the combined 'Rest of Europe' zone real battery/reservoir storage and real subsidy treatment instead of a placeholder zero.", color=GOOD)
pdf.callout("Phase 42 - France disaggregated alone",
            "Split France out of the combined zone into its own real, separately-modelled zone. Made things WORSE (shortage hours 7 to 167) - France's nuclear fleet had been propping up the whole combined pool.", color=BAD)
pdf.callout("Phase 43 - All 10 real countries disaggregated",
            "Went all the way. Better than France-alone but still short of the combined-zone result on the metrics that matter most - so the combined 'Rest of Europe' approach (Phase 37) remains the standing best build.", color=AMBER)

# =====================================================================
pdf.h1("15. How the Two-Way Market Works: One Import Hour, One Export Hour (Real Data, Phase 37)")
pdf.question("How does the 2-way market work with the export? Set up an example of an hour that had export and another hour that had import.")
pdf.table(
    ["", "Import hour: 2027-12-31, 18:00", "Export hour: 2027-10-19, 11:00"],
    [
        ["Germany's own price", "153.92 EUR/MWh", "-32.11 EUR/MWh"],
        ["Rest-of-Europe price", "88.79 EUR/MWh", "64.97 EUR/MWh"],
        ["Germany imported", "22,011.7 MWh", "0 MWh"],
        ["Germany exported", "0 MWh", "21,593.4 MWh"],
    ],
    [55, 68, 68],
)
pdf.callout(
    "Import hour explained:",
    "Germany's own price was much higher than the Rest-of-Europe price, so Germany imported "
    "22,011.7 MWh - essentially the ENTIRE available transmission capacity that hour (the "
    "real ceiling was 22,012 MW) - because it was clearly cheaper to buy from across the "
    "border than to run its own more expensive generation.",
)
pdf.callout(
    "Export hour explained:",
    "Germany's own price was actually NEGATIVE (a real midday oversupply hour - cheap solar/"
    "wind flooding the market) while the Rest-of-Europe price was still positive, so Germany "
    "exported 21,593.4 MWh - again essentially the full available capacity in that direction "
    "(21,593 MW) - because it was more profitable to sell the surplus abroad than to let it "
    "go to waste or push the domestic price even more negative.",
)
pdf.callout(
    "Across the full year:",
    "4,920 hours had some import, 3,752 had some export - the model genuinely trades in both "
    "directions depending on which side is cheaper that hour, which is the entire point of "
    "the two-way coupling versus the old one-way import-only model.",
    color=GOOD,
)

pdf.output(r"C:\Users\MuideenOA\Desktop\PyTut\Amiris\AMIRIS-QA.pdf")
print("Saved AMIRIS-QA.pdf")
