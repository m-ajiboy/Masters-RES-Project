"""Generates AMIRIS_Brainpool_Data_Glossary.pdf - explains every column header in the
translated Brainpool 2027 workbook (Amiris_Inputdata_EN.xlsx), across all four sheets,
with a plain-language meaning and a real physical example for each.
"""
from fpdf import FPDF

NAVY = (31, 58, 77)
AMBER = (165, 105, 31)
GREY = (90, 96, 92)
LIGHT = (238, 240, 233)

MARGIN = 16
LH = 5.2


class Doc(FPDF):
    def footer(self):
        self.set_y(-13)
        self.set_font("Helvetica", "I", 8)
        self.set_text_color(*GREY)
        self.cell(0, 8, f"Brainpool 2027 Data Glossary                                                                                    Page {self.page_no()}", align="C")

    def h1(self, text):
        if self.get_y() > 255:
            self.add_page()
        self.ln(3)
        self.set_font("Helvetica", "B", 14)
        self.set_text_color(*NAVY)
        self.set_x(MARGIN)
        self.multi_cell(0, 7.5, text)
        y = self.get_y()
        self.set_draw_color(*NAVY)
        self.set_line_width(0.6)
        self.line(MARGIN, y, 210 - MARGIN, y)
        self.ln(4)

    def scope(self, text):
        self.set_font("Helvetica", "I", 9.5)
        self.set_text_color(*GREY)
        self.set_x(MARGIN)
        self.multi_cell(0, 5, text)
        self.ln(2)

    def table(self, headers, rows, widths, align=None):
        align = align or ["L"] * len(headers)

        def draw_header():
            self.set_font("Helvetica", "B", 8.3)
            self.set_fill_color(*NAVY)
            self.set_text_color(255, 255, 255)
            for h, w, a in zip(headers, widths, align):
                self.cell(w, 7, h, border=0, fill=True, align=a)
            self.ln(7)
            self.set_font("Helvetica", "", 8.3)

        if self.get_y() > 235:
            self.add_page()
        draw_header()
        fill = False
        for row in rows:
            line_counts = []
            for val, w in zip(row, widths):
                lines = self.multi_cell(w, LH, val, border=0, align="L", dry_run=True, output="LINES")
                line_counts.append(max(len(lines), 1))
            row_h = max(line_counts) * LH
            if self.get_y() + row_h > 275:
                self.add_page()
                draw_header()
            self.set_fill_color(*LIGHT) if fill else self.set_fill_color(255, 255, 255)
            self.set_text_color(20, 24, 22)
            x_row, y_row = self.get_x(), self.get_y()
            x = x_row
            for w in widths:
                self.rect(x, y_row, w, row_h, style="F")
                x += w
            x = x_row
            for val, w, a in zip(row, widths, align):
                self.set_xy(x, y_row)
                bold = val.startswith("**")
                if bold:
                    val = val[2:]
                    self.set_font("Helvetica", "B", 8.3)
                self.multi_cell(w, LH, val, border=0, align=a, fill=False, max_line_height=LH)
                if bold:
                    self.set_font("Helvetica", "", 8.3)
                self.set_xy(x + w, y_row)
                x += w
            self.set_xy(x_row, y_row + row_h)
            fill = not fill
        self.ln(2)


pdf = Doc()
pdf.set_margins(MARGIN, 14, MARGIN)
pdf.set_auto_page_break(auto=True, margin=16)
pdf.add_page()

# ---- Title ----
pdf.set_font("Helvetica", "B", 19)
pdf.set_text_color(*NAVY)
pdf.set_x(MARGIN)
pdf.multi_cell(0, 9.5, "Brainpool 2027 Data Glossary")
pdf.set_font("Helvetica", "I", 10.5)
pdf.set_text_color(*GREY)
pdf.set_x(MARGIN)
pdf.multi_cell(0, 5.6, "What every column in Amiris_Inputdata_EN.xlsx means, and a real physical example for each")
pdf.set_font("Helvetica", "", 9)
pdf.set_x(MARGIN)
pdf.cell(0, 6, "Muideen Oladayo Ajiboye  |  10 August 2026", new_x="LMARGIN", new_y="NEXT")
pdf.ln(2)
y = pdf.get_y()
pdf.set_draw_color(*NAVY)
pdf.set_line_width(1)
pdf.line(MARGIN, y, 210 - MARGIN, y)
pdf.ln(4)

pdf.set_font("Helvetica", "", 10)
pdf.set_text_color(20, 24, 22)
pdf.set_x(MARGIN)
pdf.multi_cell(0, 5.4,
    "Covers all four sheets in the translated workbook: Capacity, Variable_cost, feedinprofile, and "
    "emission_factor. Facility examples are real, well-known German power stations or installation types, "
    "given to make each header concrete - they illustrate the category, not the specific plant behind "
    "Brainpool's number."
)
pdf.ln(2)

headers3 = ["Header", "What it means", "Example"]
widths3 = [40, 82, 46]

# =====================================================================
pdf.h1("Sheet 1: Capacity - Section A (Gross Electricity Generation Capacity, GW)")
pdf.scope(
    "Power ratings (GW) - the maximum instantaneous output each technology's fleet could produce at any "
    "single moment. A nameplate/stock figure, not tied to how often the plant actually runs."
)
pdf.table(headers3, [
    ["**Year", "The calendar year this scenario represents (2027 throughout this file).", "N/A - a label, not a facility."],
    ["**Nuclear", "Total nameplate output of all operating nuclear reactors. Reads 0 GW here since Germany's last three reactors closed permanently in April 2023.", "A single reactor like Isar 2 (~1,485 MW) before its 2023 shutdown."],
    ["**Lignite", "Total nameplate output of brown-coal power stations burning locally mined lignite.", "Kraftwerk Niederaussem or Kraftwerk Boxberg."],
    ["**Hard Coal", "Total nameplate output of black/hard-coal-fired stations, typically using imported coal.", "Kraftwerk Heyden or a Ruhr-basin coal plant."],
    ["**Natural Gas", "Total nameplate output of gas turbine and combined-cycle (CCGT) power stations.", "Irsching gas-fired power station, one of Europe's most efficient CCGT plants."],
    ["**Oil", "Total nameplate output of oil-fired plants, mostly small peaking or emergency-reserve units today.", "A diesel/oil-fired reserve unit kept for grid emergencies."],
    ["**Other Fossil", "Catch-all for fossil capacity not separately tracked (mixed fuels, industrial by-product gases).", "A steelworks plant burning blast-furnace or coke-oven gas."],
    ["**Reservoir Hydro", "Dammed hydro reservoirs with real storage capability, distinct from run-of-river.", "An Alpine reservoir hydro station in Bavaria."],
    ["**Wind Onshore", "Total nameplate capacity of land-based wind turbines across Germany.", "A wind farm in Schleswig-Holstein."],
    ["**Wind Offshore", "Total nameplate capacity of turbines installed in the North Sea or Baltic Sea.", "Amrumbank West offshore wind farm, North Sea."],
    ["**Run-of-River Hydro", "Hydro plants using continuous river flow without a large storage reservoir.", "Iffezheim run-of-river station on the Rhine."],
    ["**Other Renewables", "Renewable capacity not separately categorised (e.g. geothermal, minor biomass types).", "A geothermal plant in the Bavarian Molasse Basin."],
    ["**Solar (Grid Feed-in)", "Ground-mounted, utility-scale PV parks whose entire output is sold to the grid.", "Meuro Solar Park, built on former lignite mining land in Brandenburg."],
    ["**Solar (Prosumer/Self-consumption)", "Household and commercial rooftop PV; output is partly self-consumed, surplus exported.", "A homeowner's rooftop array feeding excess power back to the grid."],
    ["**Pumped Hydro Storage", "Dammed reservoirs where water is pumped uphill at low prices and released to generate at high prices.", "Goldisthal pumped storage plant, Thuringia."],
    ["**Annual Peak Load", "The single highest hour of system demand across the year - a system metric, not a generation technology.", "The exact hour, likely a winter weekday evening, when Germany's grid draws the most power all year."],
    ["**Large-Scale Battery Storage Power", "Combined charge/discharge power rating of grid-connected battery installations.", "A grid-scale lithium-ion battery site such as the one at Jardelund."],
], widths3)

# =====================================================================
pdf.h1("Sheet 1: Capacity - Section B (Gross Electricity Generation, TWh)")
pdf.scope(
    "Same technology categories as Section A, minus the storage/peak-load rows, but measured as actual "
    "annual energy output rather than instantaneous capacity - how much electricity each fleet really "
    "produced across the year, not how big it is. Same facilities as above; different measurement axis."
)
pdf.table(headers3, [
    ["**Nuclear / Lignite / Hard Coal / Natural Gas / Oil / Other Fossil", "Annual energy actually generated by each conventional fuel type, in terawatt-hours.", "Same plant types as Section A - e.g. Niederaussem's actual yearly output, not its rated capacity."],
    ["**Reservoir Hydro / Wind Onshore / Wind Offshore / Run-of-River Hydro / Other Renewables", "Annual energy actually generated by each renewable/hydro category.", "Same facilities as Section A, measured by what they actually produced, not their nameplate rating."],
    ["**Solar (Grid Feed-in) / Solar (Prosumer/Self-consumption)", "Annual energy generated by utility-scale and rooftop solar respectively.", "See Section A - Meuro Solar Park (Grid Feed-in) vs. a household rooftop array (Prosuming)."],
], widths3)

# =====================================================================
pdf.h1("Sheet 1: Capacity - Section C (Gross Electricity Demand, TWh)")
pdf.scope("How electricity is consumed across the German economy, split into four distinct demand streams.")
pdf.table(headers3, [
    ["**Inflexible Gross Electricity Demand", "Baseline consumption that doesn't shift with price - households, industry, commercial lighting and machinery.", "A factory's production-line motors running on a fixed operating schedule."],
    ["**Electrolysis (Hydrogen Production)", "Electricity consumed by electrolysers splitting water into hydrogen and oxygen for green hydrogen.", "An industrial electrolyser at a steelworks converting to hydrogen-based production."],
    ["**Electric Mobility (EV Charging)", "Electricity consumed charging electric vehicles - home, public, and fleet charging combined.", "A home EV wallbox, or a public fast-charging station."],
    ["**Heat Pumps", "Electricity consumed by heat pumps used for space and water heating, replacing gas boilers.", "An air-source heat pump installed in a residential home."],
    ["**Net Exports", "The balance of cross-border trade. Negative (as in this file, -43.9 TWh) means Germany is a net importer that year.", "N/A - a cross-border trade balance, not a single facility."],
    ["**Pumped Storage Losses", "Energy lost to round-trip inefficiency when charging and discharging pumped hydro storage - extra demand created by the storage cycle itself.", "The energy Goldisthal (see Section A) consumes beyond what it later releases."],
], widths3)

# =====================================================================
pdf.h1("Sheet 2: Variable_cost")
pdf.scope("Monthly commodity prices, exchange rates, and the carbon price - the cost inputs that determine each fuel type's bidding price in the market.")
pdf.table(headers3, [
    ["**Date", "The calendar month each row's prices apply to. Monthly resolution, not hourly - fuel and carbon prices move slowly.", "N/A - a timestamp, not a facility."],
    ["**Hard Coal [USD/tonne]", "International benchmark price for hard coal (e.g. API2 Rotterdam), before conversion to energy-content terms.", "Coal delivered to Rotterdam's ARA (Amsterdam-Rotterdam-Antwerp) trading hub."],
    ["**Crude Oil Brent [USD/barrel]", "The international Brent crude benchmark, used to derive oil-fired generation's fuel cost.", "North Sea Brent crude oil, the standard global oil price reference."],
    ["**Natural Gas TTF (Netherlands hub) [EUR/MWh]", "The Dutch Title Transfer Facility - continental Europe's primary gas trading hub and reference price.", "Gas traded at the TTF virtual hub in the Netherlands."],
    ["**Natural Gas UK NBP [pence/therm]", "The UK's National Balancing Point gas hub price, in a different unit convention (pence per therm) requiring conversion.", "Gas traded at Britain's National Balancing Point."],
    ["**Natural Gas Italy / Spain / Germany [EUR/MWh]", "National gas hub prices for each country, reflecting local basis differentials from the TTF benchmark.", "Germany's THE (Trading Hub Europe) gas price, for the Germany column specifically."],
    ["**USD Exchange Rate [USD/EUR]", "How many US dollars one euro buys - needed to convert the dollar-denominated coal and oil prices into euros.", "N/A - a currency rate, not a facility."],
    ["**GBP Exchange Rate [GBP/EUR]", "The same conversion, for the UK gas price series.", "N/A - a currency rate, not a facility."],
    ["**EUA - EU Emission Allowance [EUR/tCO2]", "The market price of one EU ETS carbon permit - what a fossil generator pays per tonne of CO2 it emits.", "A carbon allowance traded on the EU Emissions Trading System."],
], widths3)

# =====================================================================
pdf.h1("Sheet 3: feedinprofile")
pdf.scope(
    "8,760 hourly capacity factors (fractions between 0 and 1) for solar and wind, split by installation "
    "type and by a four-region simplification of Germany, since weather differs by location and hour."
)
pdf.table(headers3, [
    ["**PV_openfield_[region]", "Hourly capacity factor for ground-mounted, utility-scale solar farms in that region.", "Meuro Solar Park's output as a fraction of its own nameplate capacity, for one region's weather."],
    ["**PV_rooftop_[region]", "Hourly capacity factor for residential/commercial rooftop solar in that region. Runs consistently lower than openfield at the same hour, since rooftop orientation and tilt are fixed by the building rather than optimised.", "A rooftop array's output as a fraction of its own nameplate capacity."],
    ["**Wind_[region]", "Hourly capacity factor for onshore wind turbines in that region.", "A wind farm's output as a fraction of its own nameplate capacity, for one region's weather."],
    ["**Regions: north / east / middle / swest", "A four-quadrant simplification of Germany used to capture that sun and wind availability differ by location at any given hour.", "N/A - a geographic grouping, not a single facility."],
], widths3)

# =====================================================================
pdf.h1("Sheet 4: emission_factor")
pdf.scope("How much CO2 each fuel type releases per unit of electricity produced - fixed values, not a time series.")
pdf.table(headers3, [
    ["**Emission_Natural_Gas", "202 kg CO2 per MWh generated - gas's relatively low emissions intensity per unit of energy.", "Irsching's CO2 output per MWh of electricity sold."],
    ["**Emission_Oil", "266 kg CO2 per MWh generated.", "An oil-fired reserve unit's CO2 output per MWh."],
    ["**Emission_Hard_Coal", "338 kg CO2 per MWh generated.", "Kraftwerk Heyden's CO2 output per MWh."],
    ["**Emission_Lignite", "407 kg CO2 per MWh generated - the highest fossil emission factor here, reflecting lignite's lower energy density and typically older plant designs.", "Niederaussem's CO2 output per MWh."],
    ["**Emission_Electricity_Grid_2025", "269 kg CO2 per MWh - not one plant's factor, but the blended average carbon intensity of Germany's entire electricity mix in 2025. Useful as a system-wide benchmark, not a direct AMIRIS input.", "N/A - a national grid-average figure, not a single facility."],
], widths3)

pdf.output("AMIRIS_Brainpool_Data_Glossary.pdf")
print("Saved AMIRIS_Brainpool_Data_Glossary.pdf")
