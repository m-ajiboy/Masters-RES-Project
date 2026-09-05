"""Generates AMIRIS_Meeting_Prep_QA.pdf - answers to the user's questions about how
AMIRIS aggregates and uses each input data category, grounded directly in the actual
Germany2019 scenario config (Conventionals.yaml, RenewablesAndPolicy.yaml, Storage.yaml,
MarketsAndForecast.yaml, schema.yaml), plus anticipated follow-up questions for the
supervisor meeting.
"""
from fpdf import FPDF

NAVY = (31, 58, 77)
AMBER = (165, 105, 31)
GREY = (90, 96, 92)
LINE = (210, 213, 203)
LIGHT = (238, 240, 233)

MARGIN = 16


class QA(FPDF):
    def header(self):
        pass

    def footer(self):
        self.set_y(-13)
        self.set_font("Helvetica", "I", 8)
        self.set_text_color(*GREY)
        self.cell(0, 8, f"AMIRIS Meeting Prep - Q&A                                                                                    Page {self.page_no()}", align="C")

    def section_title(self, text):
        if self.get_y() > 255:
            self.add_page()
        self.ln(3)
        self.set_font("Helvetica", "B", 13.5)
        self.set_text_color(*NAVY)
        self.cell(0, 8, text, new_x="LMARGIN", new_y="NEXT")
        y = self.get_y()
        self.set_draw_color(*NAVY)
        self.set_line_width(0.6)
        self.line(MARGIN, y, 210 - MARGIN, y)
        self.ln(4)

    def scope_note(self, text):
        self.set_font("Helvetica", "I", 9.5)
        self.set_text_color(*GREY)
        self.multi_cell(0, 5, text)
        self.ln(1)

    def qa(self, question, answer):
        if self.get_y() > 250:
            self.add_page()
        self.set_font("Helvetica", "B", 10.5)
        self.set_text_color(*AMBER)
        self.multi_cell(0, 5.6, "Q: " + question)
        self.set_font("Helvetica", "", 10)
        self.set_text_color(20, 24, 22)
        self.set_x(MARGIN)
        self.multi_cell(0, 5.4, answer)
        self.ln(3)

    def mini_table(self, headers, rows, widths):
        if self.get_y() > 240:
            self.add_page()
        self.set_font("Helvetica", "B", 8.5)
        self.set_fill_color(*NAVY)
        self.set_text_color(255, 255, 255)
        x0 = self.get_x()
        y0 = self.get_y()
        for h, w in zip(headers, widths):
            self.cell(w, 7, h, border=0, fill=True, align="L")
        self.ln(7)
        self.set_font("Helvetica", "", 8.5)
        self.set_text_color(20, 24, 22)
        fill = False
        for row in rows:
            self.set_fill_color(*LIGHT) if fill else self.set_fill_color(255, 255, 255)
            x_start = self.get_x()
            y_start = self.get_y()
            max_h = 5.2
            cell_lines = []
            for val, w in zip(row, widths):
                lines = self.multi_cell(w, 5.2, val, border=0, align="L", dry_run=True, output="LINES")
                cell_lines.append(len(lines))
            max_h = max(max(cell_lines), 1) * 5.2
            for val, w in zip(row, widths):
                xc, yc = self.get_x(), self.get_y()
                self.multi_cell(w, 5.2, val, border=0, align="L", fill=True)
                self.set_xy(xc + w, yc)
            self.ln(max_h)
            fill = not fill
        self.ln(2)

    def bullets(self, items):
        self.set_font("Helvetica", "", 10)
        self.set_text_color(20, 24, 22)
        for it in items:
            self.set_x(MARGIN)
            self.cell(4, 5.4, "-")
            self.multi_cell(0, 5.4, it)
        self.ln(1)


pdf = QA()
pdf.set_margins(MARGIN, 14, MARGIN)
pdf.set_auto_page_break(auto=True, margin=16)
pdf.add_page()

# ---- Title block ----
pdf.set_font("Helvetica", "B", 21)
pdf.set_text_color(*NAVY)
pdf.cell(0, 10, "AMIRIS Input Data - Meeting Prep Q&A", new_x="LMARGIN", new_y="NEXT")
pdf.set_font("Helvetica", "I", 11)
pdf.set_text_color(*GREY)
pdf.multi_cell(0, 6, "How AMIRIS actually measures, aggregates, and uses each input - worked from the real Germany2019 scenario files")
pdf.set_font("Helvetica", "", 9)
pdf.cell(0, 6, "Muideen Oladayo Ajiboye  |  28 July 2026", new_x="LMARGIN", new_y="NEXT")
pdf.set_draw_color(*NAVY)
pdf.set_line_width(1)
pdf.ln(2)
y = pdf.get_y()
pdf.line(MARGIN, y, 210 - MARGIN, y)
pdf.ln(4)

pdf.set_font("Helvetica", "", 10)
pdf.set_text_color(20, 24, 22)
pdf.multi_cell(0, 5.4,
    "Every answer below is checked against the actual configuration files AMIRIS uses to run "
    "Germany2019 (Conventionals.yaml, RenewablesAndPolicy.yaml, Storage.yaml, MarketsAndForecast.yaml, "
    "schema.yaml) - not general assumptions about how such models usually work. Section headers match "
    "the categories in AMIRIS_Input_Data_Requirements.docx."
)
pdf.ln(2)

# =====================================================================
pdf.section_title("Electricity Demand - quick confirmation")
pdf.qa(
    "Is hourly load the total for all of Germany, or per region/utility?",
    "Total for the whole country, one number per hour (8,760 values/year). AMIRIS does not split demand "
    "by region or utility in these scenarios - it is a single national load curve that the entire market "
    "has to clear against."
)

# =====================================================================
pdf.section_title("B. Conventional Fleet (worked example: Nuclear)")
pdf.scope_note("Applies identically to Lignite, Hard Coal, Natural Gas, and Oil - only the numbers differ.")

pdf.qa(
    "Is installed capacity for the whole nuclear fleet, or one plant?",
    "The whole fleet. In the real scenario file, Nuclear's InstalledPowerInMW is 9,524 MW - that is every "
    "German nuclear plant added together, not one reactor."
)

pdf.qa(
    "You said typical block size answers that installed capacity is for the whole plant - is efficiency "
    "then an average value across the whole fleet?",
    "No - and this is the one place your instinct doesn't carry over. Efficiency is NOT a single average. "
    "It is supplied as a range: Efficiency.Minimal and Efficiency.Maximal (for Nuclear: 0.330 to 0.331 - a "
    "very tight range since German nuclear plants were all similar; for Lignite it's 0.311 to 0.45, a much "
    "wider spread since that fleet mixes old and modern plants). "
    "Here is what AMIRIS actually does with the three numbers together: it takes the fleet total "
    "(9,524 MW), divides it into individual simulated plants of BlockSizeInMW each (900 MW for nuclear, "
    "so about 10-11 separate plant units), and assigns each of those simulated units a DIFFERENT "
    "efficiency interpolated across the Minimal-to-Maximal range. The result is a realistic merit order "
    "within one fuel type - some nuclear-equivalent blocks are slightly cheaper to run than others - "
    "rather than treating the whole fleet as one uniform machine."
)

pdf.qa(
    "For variable operating cost, CO2 emissions factor, and outage - are those per plant, or an average "
    "for the whole fleet?",
    "All three are a single shared value (or single shared time series, for outage) applied identically to "
    "every simulated plant of that fuel type. They are not measured per real individual plant and then "
    "averaged - they are one assumed representative number for the entire category. For Nuclear specifically: "
    "OpexVarInEURperMWH = 0.5 EUR/MWh, SpecificCo2EmissionsInTperMWH = 0.0 (no combustion), and outage comes "
    "from a shared time series (nuclear_outage.csv) used by every nuclear block alike. So: efficiency is the "
    "one field that varies plant-to-plant within a fuel type; opex, CO2 factor, and outage do not."
)

pdf.mini_table(
    ["Field", "Applies to", "What it actually means"],
    [
        ["Installed capacity", "Whole fleet", "Total MW, all real plants of that fuel type summed together."],
        ["Block size", "A modelling choice, not data", "The size AMIRIS slices the fleet total into to create individual simulated plants."],
        ["Efficiency (Min/Max)", "Whole fleet, as a spread", "A range - individual simulated plants get different efficiency values across it."],
        ["Variable operating cost", "Whole fleet, one shared number", "The same assumed cost applied to every simulated plant of that type."],
        ["CO2 emissions factor", "Whole fleet, one shared number", "The same assumed factor applied to every simulated plant of that type."],
        ["Outage / must-run", "Whole fleet, one shared time series", "The same availability profile applied to every simulated plant of that type."],
    ],
    [38, 40, 96],
)

pdf.qa(
    "What do the resolution phrases actually mean - 'one value/year or per capacity change', "
    "'one value or range per fuel type', 'one value per fuel type'?",
    "'One value/year (or per capacity change)' - installed capacity: usually a single static number for the "
    "simulated year, updated only if capacity genuinely changed mid-year (e.g. a plant retiring). "
    "'One value or range per fuel type' - efficiency: exactly one Min/Max pair covering that whole fuel "
    "category (if you only have a single average efficiency number, that's fine - set Minimal = Maximal = "
    "that number; the range simply collapses to a point). "
    "'One value per fuel type' - opex, CO2 factor, block size: exactly one number for that entire category, "
    "with no further breakdown needed."
)

pdf.qa(
    "What's the difference between 'outage' and 'must-run' - aren't they opposites?",
    "They're independent, not opposites. Outage factor = the share of that fleet that is broken down or "
    "under maintenance and CANNOT produce, even if the market wants it to. Must-run factor = the share of "
    "that fleet that is forced to keep running (and sell into the market) for technical or grid-stability "
    "reasons, even if the market price is too low to justify it economically - e.g. a coal plant that also "
    "supplies district heating can't simply shut off in summer. One is a floor on availability, the other "
    "is a floor on output, and a fleet can have both figures active in the same hour."
)

pdf.qa(
    "What if we don't know Brainpool's typical block size or exact efficiency spread?",
    "Not a blocker. If block size is unknown, set it equal to the total installed capacity - the fleet then "
    "simulates as one big unit rather than several smaller ones (less bidding granularity, but AMIRIS will "
    "still run). If only one efficiency number is available rather than a range, use it for both Minimal and "
    "Maximal, as above."
)

# =====================================================================
pdf.section_title("C. Renewable Fleet (worked example: Wind)")
pdf.scope_note("Applies identically to Solar, Biomass, Run-of-river hydro, and Other renewables.")

pdf.qa(
    "Is installed capacity for the whole wind fleet, or one plant?",
    "Whole fleet - but split further by subsidy vintage/scheme, not lumped into one number. In the real "
    "scenario, wind onshore is not one entry - it's a FIT group plus five separate MPVAR 'clusters', each "
    "with its own InstalledPowerInMW (e.g. one cluster is 3,848 MW, another is 14,670 MW). Each cluster "
    "represents turbines built under a similar subsidy vintage. So the honest answer is: not the whole fleet "
    "as a single number, and not individual turbines either - it's grouped by subsidy cohort."
)

pdf.qa(
    "For generation profile, is that the energy actually generated per hour, for one plant or the total?",
    "Neither, exactly - it's a CAPACITY FACTOR, a plain fraction between 0 and 1, and it is shared across "
    "every cluster of that technology (all wind-onshore clusters use the exact same profile file, since they "
    "experience the same physical wind). AMIRIS multiplies this fraction by each cluster's own installed "
    "capacity to get that cluster's actual available MW that hour. So the profile itself is technology-wide, "
    "not per-cluster and not per-turbine; only the installed-capacity number differs by cluster."
)

pdf.qa(
    "Is the capacity factor relative to the day's own peak - e.g. if the windiest hour of the day is noon, "
    "is that hour recorded as 1.0 and other hours a percentage of that?",
    "No - and this is worth correcting before the meeting, since it's an easy assumption to make. The "
    "capacity factor is an ABSOLUTE physical measure, not rescaled per day: it is real output achieved divided "
    "by the turbine's nameplate installed capacity, driven by actual wind speed against the turbine's power "
    "curve. A value of 1.0 means wind speed reached or exceeded the turbine's rated wind speed that hour - "
    "full nameplate output - and this can happen (or fail to happen) on any hour of any day depending on "
    "real weather, completely independent of what other hours that same day looked like. In the actual "
    "profile data, values sit anywhere from about 0.0 (calm) up toward 1.0 (very windy), hour by hour, with "
    "no daily rescaling at all - so the 'noon = 1.0' framing isn't how it works."
)

pdf.qa(
    "How does AMIRIS actually use the subsidy figure?",
    "It depends on which support instrument applies, and both types appear in the real scenario:\n"
    "FIT (feed-in tariff) - the plant is guaranteed a fixed EUR/MWh for every unit it produces, paid "
    "separately from the market. This means it can profitably clear the market even at a market price of "
    "zero or below, since its real income comes from the tariff, not the market price. Example: wind onshore "
    "FIT is 85.0 EUR/MWh.\n"
    "MPVAR (variable market premium) - a more modern scheme. The plant sells at the real market price, then "
    "gets a top-up equal to the gap between its assumed cost (LCOE) and the market's realised average price "
    "for that period. Example: one wind-onshore MPVAR cluster has an LCOE of 70.58 EUR/MWh. "
    "Both schemes push the same behaviour: subsidised renewables can rationally bid at or near zero, since "
    "their real earnings are topped up separately, which is exactly why they clear first in the merit order."
)

# =====================================================================
pdf.section_title("D. Storage (worked example: Battery)")

pdf.qa(
    "Is storage modelled as one combined national total, or individual units?",
    "Individual, explicitly - more so than any other category. The real Germany2019 scenario models 18 "
    "separate storage agents, each with its own power capacity, energy capacity, and efficiencies, competing "
    "independently in the market rather than pooled into one 'Germany storage' number. If Brainpool's data "
    "only has an aggregate storage total, that's usable too (as one combined unit) - but if you can get a "
    "breakdown by a few major categories (e.g. pumped hydro vs. batteries), that maps more faithfully onto "
    "how AMIRIS actually represents it."
)

pdf.qa(
    "Explain round-trip efficiency better - is it one number?",
    "In AMIRIS it is actually two separate numbers, not one combined figure: ChargingEfficiency (share of "
    "grid electricity that actually ends up stored when charging) and DischargingEfficiency (share of stored "
    "energy that actually reaches the grid when discharging). One real storage unit in the scenario has "
    "ChargingEfficiency 0.848 and DischargingEfficiency 0.778 - round-trip efficiency is simply those two "
    "multiplied together (0.848 x 0.778 = about 66%). If Brainpool only supplies one combined round-trip "
    "number, the standard workaround is to take its square root and use that same value for both the "
    "charging and discharging legs, since AMIRIS's schema expects both."
)

# =====================================================================
pdf.section_title("E. Fuel and Carbon Prices")

pdf.qa(
    "How are these actually used inside AMIRIS - what's the mechanism?",
    "They feed directly into each plant's bidding price through a standard merit-order cost formula: "
    "marginal cost (EUR per MWh of electricity) = [fuel price / efficiency] + [CO2 price x CO2 emissions "
    "factor], plus the fuel type's variable operating cost. A trader agent for that fuel type then adds a "
    "markup on top of this marginal cost (a random amount within a set range, e.g. Hard Coal bids "
    "marginal-cost minus 15 to plus 5 EUR/MWh) to form the actual bid submitted to the market. This is "
    "exactly why an efficient, low-carbon plant like nuclear bids cheaply (and can even go negative, since "
    "its markup range is allowed to be strongly negative), while an inefficient gas peaker bids high."
)

pdf.qa(
    "Are all four prices treated the same way, or do some come from real markets?",
    "Two different treatments appear in the real scenario. Hard coal, natural gas, oil, and CO2 all use "
    "real time-series prices (sourced from public market data, changing month to month or day to day). "
    "Nuclear and lignite fuel costs, by contrast, are flat constants set once for the whole year (2.00 and "
    "5.00 EUR/MWh respectively) - because there is no liquid public market for uranium or lignite the way "
    "there is for coal, gas, oil, and carbon permits, so these are treated as fixed internal cost estimates "
    "rather than market-quoted series."
)

# =====================================================================
pdf.section_title("Other Questions Likely to Come Up")
pdf.scope_note("Not yet asked, but plausible follow-ups given the direction of the meeting.")

pdf.bullets([
    "Cross-border trade - does Brainpool's model allow imports/exports with neighbouring countries, or "
    "treat Germany as standalone? AMIRIS, as currently configured, treats Germany as a closed market with "
    "no cross-border flow - already a confirmed source of price gap from the 2018 backtest, worth raising "
    "proactively rather than waiting to be asked.",
    "Bidding behaviour - does Brainpool assume plants bid strictly at production cost, or with a strategic "
    "margin? AMIRIS assumes a margin (the markup ranges described above), which is one lever available if a "
    "gap needs explaining later.",
    "Negative prices - does Brainpool's price output include negative hours at all, and if so how often? "
    "AMIRIS can produce them (nuclear/lignite markup ranges go negative) but only when a subsidised "
    "renewable or inflexible plant is the marginal bidder.",
    "Is demand price-responsive, or fixed regardless of price? In these scenarios, demand is exogenous and "
    "inelastic - the load curve does not change in response to the simulated price, only supply-side bidding "
    "does.",
    "Does storage see the whole year in advance, or does it plan blind? Storage optimises over a rolling "
    "24-to-168-hour window using price forecasts, not perfect year-ahead foresight - worth mentioning if "
    "asked how 'smart' the storage dispatch really is.",
    "Will currency, per-unit basis, and time zone match? Brainpool figures need to be in EUR (not another "
    "currency), per MWh (not per kWh), and on the same clock convention AMIRIS timeseries use - this exact "
    "class of mismatch (SMARD's DE/AT/LU vs DE/LU zone split, 15-minute vs hourly resolution) already caused "
    "real problems earlier in this project and is worth flagging as something to check early, not late.",
    "What is the actual deliverable at the end of this exercise? A single AMIRIS run for the agreed year, "
    "compared three ways: AMIRIS's simulated price vs. Brainpool's price vs. the real historical price - with "
    "any gap traced to a specific, named cause rather than left as an unexplained number.",
])

pdf.output("AMIRIS_Meeting_Prep_QA.pdf")
print("Saved AMIRIS_Meeting_Prep_QA.pdf")
