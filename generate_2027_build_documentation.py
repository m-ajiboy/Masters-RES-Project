"""Generates AMIRIS_Germany2027_Build_Documentation.pdf - a comprehensive record of every
input used to build the Germany2027 V1 (no-import, BDEW-demand) scenario: where each value
came from, how it was validated, and exactly what was copied, edited, or newly written in
every YAML file. Written directly from the actual build scripts and this session's work,
not reconstructed from memory.
"""
from fpdf import FPDF

NAVY = (31, 58, 77)
AMBER = (165, 105, 31)
GREY = (90, 96, 92)
LIGHT = (238, 240, 233)
GOOD = (58, 107, 71)
BAD = (150, 60, 40)

MARGIN = 15
LH = 5.0


class Doc(FPDF):
    def footer(self):
        self.set_y(-13)
        self.set_font("Helvetica", "I", 8)
        self.set_text_color(*GREY)
        self.cell(0, 8, f"AMIRIS Germany2027 Build Documentation                                                                                    Page {self.page_no()}", align="C")

    def h1(self, text):
        if self.get_y() > 255:
            self.add_page()
        self.ln(3)
        self.set_font("Helvetica", "B", 14)
        self.set_text_color(*NAVY)
        self.set_x(MARGIN)
        self.multi_cell(0, 7.2, text)
        y = self.get_y()
        self.set_draw_color(*NAVY)
        self.set_line_width(0.6)
        self.line(MARGIN, y, 210 - MARGIN, y)
        self.ln(4)

    def h2(self, text):
        if self.get_y() > 262:
            self.add_page()
        self.set_font("Helvetica", "B", 10.5)
        self.set_text_color(*AMBER)
        self.ln(1)
        self.set_x(MARGIN)
        self.multi_cell(0, 5.4, text)
        self.ln(0.5)

    def body(self, text):
        self.set_font("Helvetica", "", 9.5)
        self.set_text_color(20, 24, 22)
        self.set_x(MARGIN)
        self.multi_cell(0, 5.1, text)
        self.ln(1.5)

    def scope(self, text):
        self.set_font("Helvetica", "I", 9)
        self.set_text_color(*GREY)
        self.set_x(MARGIN)
        self.multi_cell(0, 4.9, text)
        self.ln(1.5)

    def code(self, text):
        if self.get_y() > 265:
            self.add_page()
        self.set_font("Courier", "", 8.6)
        self.set_text_color(*NAVY)
        self.set_fill_color(*LIGHT)
        self.set_x(MARGIN)
        self.multi_cell(0, 5.2, text, fill=True, align="L")
        self.ln(2)

    def callout(self, label, text, color=BAD):
        if self.get_y() > 255:
            self.add_page()
        self.set_font("Helvetica", "B", 9)
        self.set_text_color(*color)
        self.set_x(MARGIN)
        self.cell(0, 5.2, label, new_x="LMARGIN", new_y="NEXT")
        self.set_font("Helvetica", "I", 9)
        self.set_text_color(*GREY)
        self.set_x(MARGIN)
        self.multi_cell(0, 4.8, text)
        self.ln(2)

    def table(self, headers, rows, widths, align=None):
        align = align or ["L"] * len(headers)

        def draw_header():
            self.set_font("Helvetica", "B", 7.8)
            self.set_fill_color(*NAVY)
            self.set_text_color(255, 255, 255)
            for hh, ww, aa in zip(headers, widths, align):
                self.cell(ww, 6.5, hh, border=0, fill=True, align=aa)
            self.ln(6.5)
            self.set_font("Helvetica", "", 7.8)

        if self.get_y() > 235:
            self.add_page()
        draw_header()
        fill = False
        for row in rows:
            line_counts = []
            for val, ww in zip(row, widths):
                lines = self.multi_cell(ww, LH, val, border=0, align="L", dry_run=True, output="LINES")
                line_counts.append(max(len(lines), 1))
            row_h = max(line_counts) * LH
            if self.get_y() + row_h > 278:
                self.add_page()
                draw_header()
            self.set_fill_color(*LIGHT) if fill else self.set_fill_color(255, 255, 255)
            self.set_text_color(20, 24, 22)
            x_row, y_row = self.get_x(), self.get_y()
            x = x_row
            for ww in widths:
                self.rect(x, y_row, ww, row_h, style="F")
                x += ww
            x = x_row
            for val, ww, aa in zip(row, widths, align):
                self.set_xy(x, y_row)
                bold = val.startswith("**")
                if bold:
                    val = val[2:]
                    self.set_font("Helvetica", "B", 7.8)
                self.multi_cell(ww, LH, val, border=0, align=aa, fill=False, max_line_height=LH)
                if bold:
                    self.set_font("Helvetica", "", 7.8)
                x += ww
            self.set_xy(x_row, y_row + row_h)
            fill = not fill
        self.ln(2)


pdf = Doc()
pdf.set_margins(MARGIN, 14, MARGIN)
pdf.set_auto_page_break(auto=True, margin=16)
pdf.add_page()

# ---- Title ----
pdf.set_font("Helvetica", "B", 18)
pdf.set_text_color(*NAVY)
pdf.set_x(MARGIN)
pdf.multi_cell(0, 9, "AMIRIS Germany2027 - Build Documentation")
pdf.set_font("Helvetica", "I", 10)
pdf.set_text_color(*GREY)
pdf.set_x(MARGIN)
pdf.multi_cell(0, 5.4, "Every input's origin and validation, and the full record of what was copied, edited, or newly written across every YAML file")
pdf.set_font("Helvetica", "", 9)
pdf.set_x(MARGIN)
pdf.cell(0, 6, "Muideen Oladayo Ajiboye  |  13 August 2026", new_x="LMARGIN", new_y="NEXT")
pdf.ln(2)
y = pdf.get_y()
pdf.set_draw_color(*NAVY)
pdf.set_line_width(1)
pdf.line(MARGIN, y, 210 - MARGIN, y)
pdf.ln(4)

pdf.body(
    "Parts 1-6 cover the first built version of the Germany2027 scenario: no cross-border trade "
    "(gap #5, assumed zero), and a single BDEW-for-everything demand profile (V1). Parts 7-9 "
    "extend this with the two later builds: the component-split demand profile (V2) and the "
    "with-import cross-border variant, and give the full four-way comparison across every "
    "combination now built (V1/V2 demand x no-import/with-import)."
)

# =====================================================================
pdf.h1("How to Read the Source Labels Used Throughout")
pdf.table(
    ["Label", "Meaning"],
    [
        ["**Brainpool (direct)", "Value taken straight from Amiris_Inputdata_EN.xlsx with no conversion."],
        ["**Brainpool (converted)", "Value taken from Brainpool's data but transformed - unit conversion, regional averaging, or capacity-weighted blending - before use."],
        ["**AMIRIS own", "Brainpool supplied nothing for this field. AMIRIS's own validated Germany2019 example scenario value was reused as the gap-fill, per the earlier documented data-gaps decision."],
        ["**Researched (external)", "Neither Brainpool nor AMIRIS's own data covered this. A real external source was looked up this session (EEG/BNetzA auction rates, MaStR battery statistics, renewables.ninja cross-check)."],
        ["**Placeholder (flagged gap)", "No real figure exists anywhere yet (confirmed by research, not assumed). AMIRIS's own example value is used as the least-bad stand-in, explicitly flagged as unresolved."],
    ],
    [44, 136],
)

# =====================================================================
pdf.h1("Part 1 - Timeseries Inputs (the timeseries/ folder)")

pdf.h2("A. Fuel and carbon prices")
pdf.table(
    ["File", "Source", "Method"],
    [
        ["**hard_coal_price.csv", "Brainpool (converted)", "USD/tonne to EUR/MWh(thermal): divide by the file's own monthly USD/EUR rate, then by 8.141 MWh/tonne (standard hard-coal calorific equivalent, ~29.3 GJ/t)."],
        ["**oil_price.csv", "Brainpool (converted)", "USD/barrel to EUR/MWh(thermal): divide by the monthly USD/EUR rate, then by 1.70 MWh/barrel (~5.8 MMBtu/barrel, standard Brent equivalent)."],
        ["**natural_gas_price.csv", "Brainpool (direct)", "'Natural Gas Germany [EUR/MWh]' column used as-is - already the correct unit."],
        ["**co2_price.csv", "Brainpool (direct)", "'EUA - EU Emission Allowance [EUR/tCO2]' column used as-is - already AMIRIS's expected unit."],
        ["**Lignite fuel price (in MarketsAndForecast.yaml, not a file)", "AMIRIS own", "Flat 5.00 EUR/MWh. Brainpool's Variable_cost sheet has no lignite series at all - realistic, since lignite is domestically mined and not internationally traded like hard coal/gas/oil."],
        ["**Nuclear fuel price", "N/A", "Omitted entirely - 0 GW nuclear capacity in Brainpool's 2027 figures (post phase-out)."],
    ],
    [41, 39, 100],
)
pdf.callout(
    "Format note (verified before building, not assumed):",
    "AMIRIS's own fuel-price files use monthly timestamps with fameio interpolating between them - "
    "confirmed by inspecting hard_coal_price.csv in the existing Germany2019 scenario before writing "
    "any conversion code. This meant Brainpool's monthly data could be written directly into the same "
    "format with no resampling needed.",
    color=NAVY,
)

pdf.h2("B. Outage and must-run factors")
pdf.table(
    ["Files", "Source", "Method"],
    [
        ["**lignite_outage.csv, lignite_must_run.csv, hard_coal_outage.csv, hard_coal_must_run.csv, natural_gas_outage.csv, natural_gas_must_run.csv", "AMIRIS own", "Brainpool supplies no outage data (correctly - unplanned 2027 outages cannot be known in 2026). AMIRIS's own validated 2015-2019 files reused, with every timestamp's calendar year shifted (2019->2027, 2020->2028, 2021->2029, later also 2018->2026 once that edge case was found - see Part 3), values and month/day/time otherwise untouched."],
        ["**Oil outage", "AMIRIS own", "A flat 0.07 (7%) figure, not a file - matches AMIRIS's own Germany2019 convention for this fuel type."],
    ],
    [68, 29, 83],
)

pdf.h2("C. Renewable generation profiles")
pdf.table(
    ["File", "Source", "Method"],
    [
        ["**solar_openfield_profile.csv", "Brainpool (converted)", "Regional average of the four PV_openfield_[north/east/middle/swest] columns in the feedinprofile sheet, per hour. Feeds the Grid Feed-in solar agent."],
        ["**solar_rooftop_profile.csv", "Brainpool (converted)", "Regional average of the four PV_rooftop_[region] columns. Feeds the Prosuming solar agent. Kept separate from openfield rather than blended into one profile - see Part 4."],
        ["**wind_onshore_profile.csv", "Brainpool (converted)", "Regional average of the four Wind_[region] columns."],
        ["**wind_offshore_profile.csv", "AMIRIS own, validated", "Brainpool gives capacity but no offshore-specific shape (only generic Wind_[region] columns, used for onshore). AMIRIS's own profile reused, redated to 2027. Validated: implies a 37.1% annual capacity factor, which sits inside the real German offshore fleet's 37-45% range (EnergyNumbers.info, Fraunhofer research this session)."],
        ["**run_of_river_profile.csv", "AMIRIS own", "Brainpool gives a Run-of-River capacity figure but no hourly shape. AMIRIS's own profile reused, redated to 2027."],
        ["**other_res_profile.csv", "AMIRIS own", "Built but not currently referenced by any 2027 agent - Brainpool's 'Other Renewables' was mapped entirely onto the Biomass profile instead (see Part 4). Kept on disk for a possible future split."],
        ["**biomass_profile.csv", "AMIRIS own", "Brainpool gives an 'Other Renewables' capacity figure but no dispatch shape. AMIRIS's own FROM_FILE dispatch profile reused, redated to 2027."],
    ],
    [39, 37, 104],
)

pdf.h2("D. Demand (load_v1_bdew.csv)")
pdf.table(
    ["Component", "Value", "Source"],
    [
        ["Inflexible base demand", "604.85 TWh", "Brainpool (direct)"],
        ["Electrolysis (hydrogen)", "14.97 TWh", "Brainpool (direct)"],
        ["Electric mobility (EV charging)", "17.81 TWh", "Brainpool (direct)"],
        ["Heat pumps", "18.69 TWh", "Brainpool (direct)"],
        ["**Combined total used", "**656.32 TWh", "**Sum of the four rows above"],
    ],
    [68, 39, 73],
)
pdf.body(
    "Method: demandlib's BDEW ElecSlp.get_scaled_power_profiles({'h0': 656,320,000 MWh}) - the real "
    "BDEW Standardlastprofil methodology (12 representative daily curves by season and day-type, H0's "
    "day-of-year dynamization applied automatically), at native 15-minute resolution, resampled to "
    "hourly to match AMIRIS's expected input. A round-trip check confirmed the built file's hourly "
    "values sum back to exactly 656.32 TWh."
)
pdf.callout(
    "Two figures deliberately excluded from the total:",
    "Net Exports (a cross-border trade balance, out of scope for this no-import build per gap #5) and "
    "Pumped Storage Losses (already implicit in the storage agents' own charging/discharging "
    "efficiency in Storage.yaml - adding it separately would double-count).",
    color=NAVY,
)

# =====================================================================
pdf.h1("Part 2 - Conventional Fleet (Conventionals.yaml)")
pdf.table(
    ["Field", "Lignite", "Hard Coal", "Nat. Gas", "Oil + Other Fossil"],
    [
        ["**Capacity (MW)", "13,927 (Brainpool)", "5,504 (Brainpool)", "36,237 (Brainpool)", "9,790 (Brainpool: 1,540 Oil + 8,250 Other Fossil, merged)"],
        ["**Block size (MW)", "500 (AMIRIS own)", "300 (AMIRIS own)", "200 (AMIRIS own)", "100 (AMIRIS own)"],
        ["**Efficiency range", "0.3108-0.45 (AMIRIS own)", "0.339-0.492 (AMIRIS own)", "0.516-0.617 (AMIRIS own CCGT range, used as representative)", "0.311-0.397 (AMIRIS own)"],
        ["**Variable opex (EUR/MWh)", "2.0 (AMIRIS own)", "2.5 (AMIRIS own)", "1.2 (AMIRIS own)", "1.2 (AMIRIS own)"],
        ["**Markup band (EUR/MWh)", "-60 to 0 (AMIRIS own)", "-15 to 5 (AMIRIS own)", "-10 to 10 (AMIRIS own CCGT band)", "0 to 0 (AMIRIS own)"],
        ["**CO2 factor (t/MWh)", "0.407 (Brainpool)", "0.338 (Brainpool)", "0.202 (Brainpool)", "0.266 (Brainpool Oil factor, used as proxy for the merged category)"],
    ],
    [31, 38, 38, 38, 35],
)
pdf.callout(
    "New gap surfaced while building (not in the original 5-item list):",
    "Brainpool's Variable_cost sheet covers fuel commodity prices, not per-fuel-type variable OPERATING "
    "cost (a separate concept - non-fuel O&M per MWh). AMIRIS's own opex figures were carried over for "
    "all four categories, consistent with the established 'AMIRIS fills gaps Brainpool doesn't cover' "
    "approach, but this specific gap had not been explicitly flagged before now.",
    color=BAD,
)
pdf.body(
    "Two simplifications, both documented rather than silently made: natural gas is modelled as ONE "
    "combined block (CCGT+OCGT merged) since Brainpool gives only one gas capacity figure with no "
    "technology split; and Oil is merged with 'Other Fossil' into a single AMIRIS Oil-type block, "
    "consistent with AMIRIS's own scenario comment that its Oil category already covers 'oil, other "
    "fossil fuels, mixed fossil fuels.'"
)

# =====================================================================
pdf.h1("Part 3 - Renewable Fleet and Subsidies (RenewablesAndPolicy.yaml)")
pdf.table(
    ["Agent", "Capacity", "Support mechanism", "Reference rate", "Rate source"],
    [
        ["Solar Openfield (Grid Feed-in)", "119,179 MW (Brainpool)", "MPVAR", "49 EUR/MWh", "Researched: BNetzA solar auction, March 2026 round (4.94 ct/kWh volume-weighted award)."],
        ["Solar Rooftop (Prosuming)", "33,706 MW (Brainpool)", "FIT", "75 EUR/MWh", "Researched: EEG Section 49 degression schedule extrapolated to 2027. FLAGGED: draft EEG-Novelle 2026 (cabinet-approved 29 Jul 2026, not yet law) proposes ending this support for new PV <25kW from 2027."],
        ["Wind Onshore", "90,232 MW (Brainpool)", "MPVAR", "52 EUR/MWh", "Researched: BNetzA wind-onshore auctions, Feb-Aug 2026 rounds (5.06-5.54 ct/kWh), midpoint."],
        ["Wind Offshore", "12,573 MW (Brainpool)", "MPVAR", "187 EUR/MWh", "PLACEHOLDER (flagged gap): no real 2027 figure exists anywhere - BNetzA's 2025 offshore auctions received zero bids and the next round is postponed to 2027 itself. AMIRIS's own Germany2019 offshore clusters' capacity-weighted LCOE used as the least-bad stand-in."],
        ["Run-of-River", "4,161 MW (Brainpool)", "FIT", "100 EUR/MWh", "AMIRIS own - no EEG hydro-specific rate was found; AMIRIS's own Germany2019 value reused."],
        ["Biomass (proxy for 'Other Renewables')", "8,250 MW (Brainpool)", "MPVAR", "197 EUR/MWh", "Researched: BNetzA biomass tender, April 2026 round, cleared near the published ceiling (19.43-19.83 ct/kWh, undersubscribed)."],
    ],
    [33, 26, 20, 22, 79],
)
pdf.callout(
    "Design correction made mid-build:",
    "Solar was originally planned as one blended agent (per an earlier decision to sum Grid Feed-in and "
    "Prosuming totals). This had to be reversed: AMIRIS assigns one SupportInstrument per operator agent, "
    "and Grid Feed-in (MPVAR) and Prosuming (FIT) use genuinely different mechanisms, so they cannot "
    "share one agent. Kept as two agents instead, each with its own real capacity and profile - which "
    "mirrors exactly how AMIRIS's own Germany2019 scenario handles multiple solar sub-fleets under one "
    "shared trader.",
    color=NAVY,
)
pdf.callout(
    "Deliberate departure from AMIRIS's own example:",
    "AMIRIS's Germany2019 scenario leaves biomass completely unsupported (routed through "
    "NoSupportTrader). This build instead gives it a real EEG-researched MPVAR rate (197 EUR/MWh), since "
    "that is a more accurate reflection of how German biomass is actually subsidised - a conscious "
    "improvement on AMIRIS's own placeholder, not an oversight.",
    color=GOOD,
)
pdf.body(
    "Reservoir Hydro (1,540 MW, Brainpool) is NOT in this file - it is modelled as a dispatchable "
    "storage agent instead of a weather-driven renewable, since reservoir hydro output is an operator "
    "choice (when to release water), unlike run-of-river (flow-determined). See Part 4."
)
pdf.body(
    "'Other Renewables' (8,250 MW, Brainpool) was mapped entirely onto the Biomass agent rather than "
    "split further, since biomass is the dominant real-world component of Germany's 'sonstige "
    "Erneuerbare' statistical bucket - a documented simplification, not a literal Brainpool breakdown."
)

# =====================================================================
pdf.h1("Part 4 - Storage Fleet (Storage.yaml)")
pdf.table(
    ["Agent", "Power (Brainpool)", "Duration", "Energy capacity", "Efficiency (charge/discharge)"],
    [
        ["Pumped Hydro (Pumpspeicher)", "8,377.6 MW", "6.399 h - AMIRIS own, capacity-weighted average across AMIRIS's own 16 daily-cycle Germany2019 storage units", "53,607.5 MWh", "87.5% / 85.2% - same AMIRIS-own fleet average"],
        ["Large-Scale Battery", "5,151.7 MW", "2.0 h - Researched (MaStR-derived): RWE's Hambach project, 236 MW / 470 MWh, targets 2027 commissioning - the same year as this scenario", "10,303.4 MWh", "95% / 95% - standard Li-ion round-trip assumption (no German-specific efficiency statistic was found; duration was researched, efficiency was not)"],
        ["Reservoir Hydro", "1,540.0 MW", "111.22 h - AMIRIS own, borrowed from the long-duration outlier unit originally excluded from the pumped-hydro duration calculation - understood, on reflection, to represent exactly this kind of seasonal Alpine reservoir", "171,282.2 MWh", "91% / 91% - same AMIRIS-own unit"],
    ],
    [26, 22, 53, 26, 53],
)
pdf.body(
    "MaStR access itself: the Marktstammdatenregister's bulk XML download and web-search CSV export are "
    "public with no login required; only its automated API needs registration (same low-friction pattern "
    "as the ENTSO-E token obtained earlier in this project). The battery duration figure was sourced from "
    "a third party (Modo Energy) that aggregates MaStR project-level data, not from a raw MaStR pull."
)

# =====================================================================
pdf.h1("Part 5 - YAML File Construction: What Was Copied, Edited, or Written New")

pdf.table(
    ["File", "Status", "What was actually done"],
    [
        ["**schema.yaml", "Copied unchanged", "Generic AMIRIS agent-type schema, identical across all scenarios - no scenario-specific data, so copied directly from Germany2019 with no edits."],
        ["**scenario.yaml", "Written new", "New Metadata block (runId 'Germany2027', description noting the data provenance and no-import assumption). Simulation window set to 2026-12-31_23:58:00 to 2027-12-31_23:58:00. The PolicySet StringSet enum was replaced with this scenario's six actual subsidy scheme names (SolarRooftopFit, RunOfRiverFit, SolarOpenfieldMpvar, WindOnMpvar, WindOffMpvar, BiomassMpvar) - AMIRIS validates PolicySet values against this list, so Germany2019's own names would not have matched."],
        ["**agents/Conventionals.yaml", "Written new", "Four fuel-type blocks (Lignite, Hard Coal, Natural Gas, Oil+Other Fossil) built from the Part 2 table above. Nuclear's builder/trader/operator triad and the separate OCGT block were both omitted entirely, rather than left at zero, since AMIRIS has no real use for a zero-capacity plant builder."],
        ["**agents/RenewablesAndPolicy.yaml", "Written new", "Six VariableRenewableOperator/Biogas agents, one shared RenewableTrader (MPVAR) and one shared SystemOperatorTrader (FIT), and a SupportPolicy agent carrying the six researched/gap-filled reference rates from Part 3."],
        ["**agents/Storage.yaml", "Written new", "Three GenericFlexibilityTrader agents (Pumpspeicher, Battery, Reservoir Hydro) built from the Part 4 table. Pumpspeicher and Reservoir use MIN_SYSTEM_COST/ENSURE_DISPATCH (matching AMIRIS's own convention for large legacy hydro); Battery uses MAX_PROFIT/STORAGE_CONTENT_VALUE (matching AMIRIS's own convention for merchant-style assets)."],
        ["**agents/Demand.yaml", "Written new", "One DemandTrader pointing at load_v1_bdew.csv, ValueOfLostLoad kept at AMIRIS's own 3,000 EUR/MWh (the price ceiling seen whenever the market cannot fully meet demand)."],
        ["**agents/MarketsAndForecast.yaml", "Written new", "DayAheadMarketSingleZone, CarbonMarket, FuelsMarket, and SensitivityForecaster agents, wired to the Part 1 timeseries files. Structurally identical to Germany2019's version except the fuel-price file references and the removal of the Nuclear fuel-price entry."],
    ],
    [43, 25, 112],
)

pdf.table(
    ["Contract file", "Status", "What was actually done"],
    [
        ["**contracts/conventionals.yaml", "Copied, then edited", "AgentGroups builder/trader/operator ID lists trimmed to [2001,2002,2003,2005] / [1001,1002,1003,1005] / [501,502,503,505] - dropping the Nuclear (2000/1000/500) and OCGT (2004/1004/504) slots. All timing/product-name contract logic below the AgentGroups block is generic and was left untouched."],
        ["**contracts/demand.yaml", "Copied unchanged", "References only Id 100 (DemandTrader), which is identical in this build - no edit needed."],
        ["**contracts/renewables_renewableTrader.yaml", "Copied, then edited", "Renewables ID list trimmed to [60, 70, 80, 52] - the four MPVAR-marketed agents (Solar Openfield, Wind Onshore, Wind Offshore, Biomass)."],
        ["**contracts/renewables_systemOperator.yaml", "Copied, then edited", "Renewables ID list trimmed to [61, 50] - the two FIT-marketed agents (Solar Rooftop, Run-of-River)."],
        ["**contracts/renewables_noSupport.yaml", "NOT created", "Germany2019's version routes Biogas/Other through the NoSupportTrader. This build gives every renewable category a real subsidy mechanism (see Part 3), so nothing routes through NoSupportTrader (Id 12) at all - the file, and the agent, were both omitted."],
        ["**contracts/storage.yaml", "Copied, then edited", "Storage ID list trimmed from Germany2019's eighteen units down to this build's three: [700, 701, 702]."],
        ["**contracts/supportPolicy.yaml", "Copied, then edited", "allMarketers trimmed from [11, 12, 13] to [11, 13], matching the removal of NoSupportTrader above."],
    ],
    [49, 27, 104],
)

pdf.h2("Agent ID numbering scheme")
pdf.body(
    "Reused Germany2019's own per-category ID ranges wherever a directly matching category existed "
    "(builders 2000s, traders 1000s, conventional operators 500s, renewable operators 50-83, storage "
    "700s, market/system agents 1/3/4/6, demand 100), simply omitting the slots for categories this "
    "build doesn't use (Nuclear, OCGT, NoSupportTrader) rather than renumbering everything from "
    "scratch. This kept the trimmed contract files a close, easily-checked diff against the originals "
    "instead of a full rewrite."
)

# =====================================================================
pdf.h1("Part 6 - Validation and QA Performed")

pdf.h2("Before writing any code")
pdf.body(
    "Inspected AMIRIS's own existing timeseries files (hard_coal_price.csv, co2_price.csv, "
    "nuclear_outage.csv, load.csv, scenario.yaml, every agents/*.yaml and contracts/*.yaml file) to "
    "confirm the exact timestamp format, delimiter, and resolution fameio expects, rather than "
    "assuming a format and risking a rebuild later."
)

pdf.h2("Structural validation")
pdf.body(
    "Ran the scenario through amirispy's actual compile step (amiris run), which converts the YAML into "
    "a protobuf input file before the Java engine executes it - this surfaces structural/schema errors "
    "within seconds, before committing to a multi-minute full simulation."
)

pdf.h2("Bug 1 found and fixed: missing SupportInstrument on the Biogas agent")
pdf.code(
    "Exception in thread \"main\" java.lang.RuntimeException: BiomassMpvar: Policy not\n"
    "configured for instrument null\n"
    "    at agents.policy.SetPolicies.register(SetPolicies.java:64)"
)
pdf.body(
    "Cause: AMIRIS's own Germany2019 Biogas entry never needed a SupportInstrument attribute, because "
    "it routes through NoSupportTrader (no subsidy). This build gives Biogas a real MPVAR subsidy (Part "
    "3), which requires that attribute to be explicit - it was missing from the first draft. Fixed by "
    "adding 'SupportInstrument: MPVAR' to the agent."
)

pdf.h2("Bug 2 found and fixed: four renewable profiles never redated to 2027")
pdf.body(
    "The scenario compiled and ran successfully after Bug 1's fix, but the result was not physically "
    "plausible: 25.3% of all 8,760 hours cleared at the 3,000 EUR/MWh shortage price ceiling. Diagnosis, "
    "not guesswork: picked a specific shortage hour (2027-01-16 18:00) and checked every agent's actual "
    "award at that hour. Total awarded energy across conventional, renewable, and storage agents matched "
    "the load served exactly - ruling out a bidding/market-clearing bug and confirming a genuine supply "
    "shortfall. Wind Offshore, Run-of-River, and Biomass all showed exactly zero at that hour despite no "
    "physical reason to be zero simultaneously; checking their source CSVs directly showed the cause: "
    "wind_offshore_profile.csv, run_of_river_profile.csv, other_res_profile.csv, and biomass_profile.csv "
    "had been copied from Germany2019 with their original 2019 timestamps intact, never redated to 2027 "
    "like the outage files were - so their data never overlapped this scenario's simulated calendar year "
    "at all. Fixed by applying the same redate function already used for the outage files to these four "
    "profiles as well."
)
pdf.callout(
    "Result after the fix:",
    "Shortage hours fell from 25.3% to 15.9% of the year (2,216 to 1,391 hours), and negative prices "
    "appeared for the first time (108 hours) - a healthy sign, since AMIRIS's own example scenarios "
    "structurally cannot produce negative prices at all (see the 2018/2019 backtest root-cause findings "
    "earlier in this project).",
    color=GOOD,
)

pdf.h2("Remaining shortage pattern: diagnosed as expected V1 behaviour, not a bug")
pdf.body(
    "Broke the remaining 1,391 shortage hours down by month and hour-of-day. 71% (995 hours) fall in "
    "the 18:00-21:00 evening window, worst in December and August. This is the textbook signature of a "
    "household evening demand spike - consistent with V1's known, deliberate simplification of applying "
    "one BDEW household (H0) load shape to the entire economy's demand, including industrial load, EV "
    "charging, and heat pumps, none of which actually follow a household's evening ramp. This is "
    "reported as a finding for the V2 (component-split) build to address, not chased further as a bug "
    "in this V1 build."
)

# =====================================================================
pdf.h1("Part 7 - Demand Profile V2 (Component-Split Build)")
pdf.body(
    "V1 applied a single BDEW household (H0) Standardlastprofil to the entire 656.32 TWh combined demand "
    "total. V2 replaces this with a purpose-built shape for each of Brainpool's four demand components "
    "separately, then sums them (build_2027_demand_v2_split.py)."
)
pdf.table(
    ["Component", "Value", "Method"],
    [
        ["**Inflexible base", "604.85 TWh", "Real 2023 ENTSO-E national load shape (examples/backtest/Germany2023/timeseries/load.csv, pulled this project from the ENTSO-E Transparency Platform), rescaled hour-by-hour so the annual total matches the 2027 target. Keeps the real seasonal/hour-of-day pattern; day-of-week alignment between 2023 and 2027 is not preserved (a documented simplification)."],
        ["**Heat pumps", "18.69 TWh", "demandlib's BDEW HeatBuilding profile (temperature-driven Standardlastprofil methodology), driven by real DWD Test Reference Year climate data bundled with demandlib itself, averaged across all 15 German climate regions for a national series (mean 8.5C, range -3.9C to 24.9C). Simplification: treats heat-pump electrical demand as directly proportional to heat demand, i.e. assumes a constant coefficient-of-performance (COP) across the year rather than modelling the real efficiency drop in cold weather."],
        ["**Electrolysis", "14.97 TWh", "Flat, constant hourly profile (1,708 MW every hour) - industrial electrolysers are typically run close to constant for efficiency."],
        ["**E-mobility", "17.81 TWh", "An assumed, documented daily charging shape - evening-peaked (weights rising through the afternoon to a peak around 18:00, matching typical unmanaged/home-dominant EV charging patterns), repeated identically every day. No seasonal or weekday/weekend variation is modelled - the least standardised of the four components, since no real German EV charging load-curve dataset was available to reshape instead."],
    ],
    [30, 25, 125],
)
pdf.callout(
    "Round-trip check:",
    "Combined total = 656.3172 TWh against a 656.3167 TWh target - matches to within rounding. Combined "
    "peak load = 106,178.7 MW, versus V1's 138,146.7 MW and Brainpool's own stated Annual Peak Load of "
    "119,001 MW - V2 sits much closer to the real target, though still below it, since the four "
    "components' individual peaks do not all coincide in the same hour.",
    color=GOOD,
)
pdf.h2("Result: V2 materially reduces V1's shortage problem")
pdf.table(
    ["Metric", "V1 (BDEW-for-everything)", "V2 (component-split)"],
    [
        ["**Peak load", "138,146.7 MW", "106,178.7 MW"],
        ["**Shortage hours (>=3000 EUR/MWh)", "1,391 (15.88%)", "659 (7.52%)"],
        ["**Negative-price hours", "108 (1.23%)", "884 (10.09%)"],
        ["**Mean price", "519.02 EUR/MWh", "285.58 EUR/MWh"],
        ["**Median price", "67.52 EUR/MWh", "77.19 EUR/MWh"],
    ],
    [56, 62, 62],
)
pdf.body(
    "This confirms the diagnosis made at the end of Part 6: V1's shortage hours were concentrated in the "
    "18:00-21:00 evening window because a household evening-peak shape had been applied to the whole "
    "economy's demand. Spreading the heat-pump, electrolysis, and EV components across their own, less "
    "peaky shapes removes most of that artificial peak, cutting shortage hours by more than half and "
    "mean price by 45%. The new build (examples/backtest/Germany2027_DemandV2/, referencing "
    "load_v2_split.csv) compiled and ran with the same zero-error validation as V1."
)

# =====================================================================
pdf.h1("Part 8 - With-Import Cross-Border Variant (ImportTrader)")
pdf.body(
    "Gap #5 assumed zero cross-border trade for the first build. This variant captures it: Brainpool's "
    "Capacity sheet gives 'Net Exports' = -43.90 TWh for 2027, i.e. Germany is projected to be a NET "
    "IMPORTER of 43.90 TWh - the same direction as the real 2023 outturn, where Germany was a net "
    "importer for the first time in decades (24.4 TWh net, computed from real ENTSO-E cross-border flow "
    "data pulled for this build)."
)
pdf.callout(
    "Scope limitation, by design:",
    "AMIRIS's ImportTrader agent type (schema.yaml, and AMIRIS's own SimpleCoupled demo scenario, used "
    "as the real wiring template) can only ADD supply to the market - offering imported energy as an "
    "extra bid. There is no ExportTrader for a single, uncoupled market zone, so this variant captures "
    "only the import side of cross-border trade. Modelling Germany's real export flows as well would "
    "require a full multi-zone MarketCoupling setup, which was judged out of scope for this build.",
    color=NAVY,
)
pdf.table(
    ["Attribute", "Method"],
    [
        ["**AvailableEnergyForImport", "Real 2023 net cross-border flow (total physical imports minus total physical exports, both pulled per-hour for DE_LU from the ENTSO-E Transparency Platform, summed across all 11 neighbouring zones: AT, BE, CH, CZ, DK_1, DK_2, FR, NO_2, NL, PL, SE_4), clipped to zero (only the 5,014 hours Germany was a real net importer are usable), then rescaled so the annual total matches Brainpool's 43.90 TWh 2027 target. Preserves the real historical timing of import need rather than inventing a shape."],
        ["**ImportCostInEURperMWH", "Real 2023 French day-ahead price (mean 96.86, min -134.94, max 276.12 EUR/MWh), used as a proxy for import cost. France is Germany's largest, single most stable interconnector partner (large, steady nuclear baseload) - a documented simplification standing in for a flow-weighted mix of all 11 neighbouring price zones."],
    ],
    [45, 135],
)
pdf.h2("Finding: realized import volume falls well short of the offered 43.90 TWh")
pdf.body(
    "AMIRIS's ImportTrader is a genuine price-competing bid, not a forced quantity: it only clears in "
    "hours where the German market price would otherwise exceed the French price offered that hour. The "
    "market only actually dispatched a fraction of what was offered:"
)
pdf.table(
    ["Build", "Offered", "Awarded (cleared)", "Utilization"],
    [
        ["V1 demand + import", "43.90 TWh", "12.33 TWh", "28.09%"],
        ["V2 demand + import", "43.90 TWh", "7.40 TWh", "16.87%"],
    ],
    [56, 40, 44, 40],
)
pdf.callout(
    "Reported as a finding, not a bug (explicit decision):",
    "This gap demonstrates a real, meaningful divergence between Brainpool's fixed net-import ASSUMPTION "
    "(a top-down forecaster's exogenous balance figure) and AMIRIS's endogenous, price-competitive "
    "DISPATCH of that same import capacity (an agent-based market clearing outcome). V1's peakier demand "
    "shape pushes German prices above the French benchmark more often, so more of the offered import "
    "volume clears there (28.09%) than in V2 (16.87%), even though V2 is otherwise the more realistic "
    "demand build. This asymmetry is itself a useful methodological data point for the thesis's central "
    "AMIRIS-vs-Brainpool comparison.",
    color=GOOD,
)
pdf.h2("Market impact of the imports that do clear")
pdf.table(
    ["Metric", "V1 no-import", "V1 with-import", "V2 no-import", "V2 with-import"],
    [
        ["**Shortage hours", "15.88%", "11.78%", "7.52%", "5.35%"],
        ["**Negative-price hours", "1.23%", "1.68%", "10.09%", "14.60%"],
        ["**Mean price (EUR/MWh)", "519.02", "400.04", "285.58", "219.81"],
    ],
    [40, 35, 35, 35, 35],
)
pdf.body(
    "Even the partial import volume that clears does real work: it relieves scarcity (shortage hours "
    "fall in both demand versions) and pulls the mean price down materially (23-32%). Negative-price "
    "hours rise slightly with imports in both cases, since the French price series itself goes negative "
    "in some hours (min -134.94 EUR/MWh), occasionally adding cheap/negative-priced import supply on top "
    "of an already renewables-saturated German hour."
)
pdf.body(
    "New scenario folders: examples/backtest/Germany2027_WithImport/ (V2 demand + import) and "
    "examples/backtest/Germany2027_V1WithImport/ (V1 demand + import), both compiled and ran with zero "
    "errors, agent Id 112, wired per AMIRIS's own SimpleCoupled demo contract pattern."
)

# =====================================================================
pdf.h1("Part 9 - Four-Way Version Matrix: Full Comparison")
pdf.body(
    "All four combinations of the originally planned 2x2 build matrix (demand V1/V2 x no-import/with-"
    "import) are now built, compiled, and simulated end to end."
)
pdf.table(
    ["Build", "Peak load", "Shortage hrs", "Negative hrs", "Mean price", "Import cleared"],
    [
        ["**V1, no-import", "138,146.7 MW", "15.88%", "1.23%", "519.02", "n/a"],
        ["**V1, with-import", "138,146.7 MW", "11.78%", "1.68%", "400.04", "12.33 / 43.90 TWh"],
        ["**V2, no-import", "106,178.7 MW", "7.52%", "10.09%", "285.58", "n/a"],
        ["**V2, with-import", "106,178.7 MW", "5.35%", "14.60%", "219.81", "7.40 / 43.90 TWh"],
    ],
    [34, 30, 26, 26, 26, 38],
)
pdf.body(
    "Reading across the matrix: demand shape (V1 vs V2) is the dominant driver of shortage relief - "
    "moving from V1 to V2 alone cuts shortage hours from 15.88% to 7.52% (no-import) and from 11.78% to "
    "5.35% (with-import). Cross-border imports are a smaller, second-order effect on top of that, but "
    "still meaningfully reduce both shortage frequency and mean price within either demand version. "
    "Folder locations: Germany2027 (V1 no-import), Germany2027_DemandV2 (V2 no-import), "
    "Germany2027_WithImport (V2 with-import), Germany2027_V1WithImport (V1 with-import)."
)

# =====================================================================
pdf.h1("Part 10 - Complete List of Open Flags Across All Builds")
pdf.table(
    ["#", "Flag", "Where it lives"],
    [
        ["1", "Wind offshore subsidy rate (187 EUR/MWh) is an AMIRIS-own placeholder - no real 2027 figure exists anywhere yet, confirmed by research, not assumed.", "RenewablesAndPolicy.yaml, SupportPolicy WindOffMpvar"],
        ["2", "Solar rooftop FIT (75 EUR/MWh) assumes current EEG law continues; a draft 2026 reform (not yet passed) would end this support for new installations <25kW from 2027.", "RenewablesAndPolicy.yaml, SupportPolicy SolarRooftopFit"],
        ["3", "Natural gas modelled as one combined CCGT+OCGT block - Brainpool gives no technology split.", "Conventionals.yaml"],
        ["4", "Oil and Other Fossil merged into one AMIRIS Oil-type block; the combined CO2 factor uses Oil's own value as a proxy, since Brainpool gives no separate 'Other Fossil' factor.", "Conventionals.yaml"],
        ["5", "Variable operating cost (opex) for all four conventional categories uses AMIRIS's own values - Brainpool's Variable_cost sheet covers commodity fuel prices, not plant O&M cost, and this gap was not in the original 5-item gap list.", "Conventionals.yaml"],
        ["6", "Battery efficiency (95%/95%) is a standard Li-ion assumption, not a researched German-specific figure - only duration was independently researched (MaStR/RWE Hambach).", "Storage.yaml"],
        ["7", "'Other Renewables' assumed to be entirely biomass, with no split for the minor geothermal/other component AMIRIS's own schema would otherwise support separately.", "RenewablesAndPolicy.yaml"],
        ["8", "RESOLVED by V2: V1's demand shape produced a peak (138.1 GW) well above Brainpool's stated Annual Peak Load (119.0 GW). V2's component-split build closes most of this gap (106.2 GW) - confirmed by simulation, not just expected.", "load_v1_bdew.csv vs load_v2_split.csv"],
        ["9", "Heat-pump profile (V2) assumes a constant coefficient-of-performance (COP) across the year - does not model the real efficiency drop in cold weather, which would make the electrical profile even peakier in winter than modelled.", "build_2027_demand_v2_split.py"],
        ["10", "E-mobility profile (V2) is an assumed daily shape, not sourced from real EV charging data, with no seasonal or weekday/weekend variation - the least standardised of the four V2 demand components.", "build_2027_demand_v2_split.py"],
        ["11", "Import cost uses a single-neighbour proxy (real French day-ahead price), not a flow-weighted mix of all 11 of DE_LU's actual neighbouring price zones.", "build_2027_import.py, ImportCostInEURperMWH.csv"],
        ["12", "With-import builds model only the import side of cross-border trade - no ExportTrader exists for a single, uncoupled market zone, so Germany's real export flows are not represented at all.", "agents/Import.yaml"],
        ["13", "Realized import volume (7.40-12.33 TWh) falls well short of the offered/Brainpool-target 43.90 TWh, since AMIRIS's ImportTrader is a genuine price-competing bid rather than a forced quantity. Reported as a deliberate methodological finding, not corrected to force full dispatch.", "ImportTrader.csv result output"],
    ],
    [8, 111, 61],
)

import sys
OUT_NAME = sys.argv[1] if len(sys.argv) > 1 else "AMIRIS_Germany2027_Build_Documentation.pdf"
pdf.output(OUT_NAME)
print(f"Saved {OUT_NAME}")
