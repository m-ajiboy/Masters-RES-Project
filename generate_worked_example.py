"""Generates AMIRIS_Worked_Example.pdf - a single, fully quantitative hour showing how
demand, the conventional fleet, renewables, subsidies, and fuel/CO2 prices combine inside
AMIRIS to produce one market-clearing price. Fleet sizes, efficiency ranges, markup bands,
and fuel-price levels are taken from the real Germany2019 scenario config; the specific hour,
demand figure, capacity factor, and outage values are constructed for illustration - clearly
flagged as such throughout, not claimed as an observed simulation output.
"""
from fpdf import FPDF

NAVY = (31, 58, 77)
AMBER = (165, 105, 31)
GREY = (90, 96, 92)
LIGHT = (238, 240, 233)
GOOD = (58, 107, 71)
BAD = (150, 60, 40)

MARGIN = 16


def money(v):
    return f"{v:,.0f}"


def num(v, d=2):
    return f"{v:,.{d}f}"


class Doc(FPDF):
    def footer(self):
        self.set_y(-13)
        self.set_font("Helvetica", "I", 8)
        self.set_text_color(*GREY)
        self.cell(0, 8, f"AMIRIS Worked Example - Illustrative, Not Observed Output                                                            Page {self.page_no()}", align="C")

    def h1(self, text):
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

    def h2(self, text):
        if self.get_y() > 260:
            self.add_page()
        self.set_font("Helvetica", "B", 10.5)
        self.set_text_color(*AMBER)
        self.ln(1)
        self.multi_cell(0, 5.6, text)
        self.ln(0.5)

    def body(self, text):
        self.set_font("Helvetica", "", 10)
        self.set_text_color(20, 24, 22)
        self.set_x(MARGIN)
        self.multi_cell(0, 5.4, text)
        self.ln(1.5)

    def formula(self, text):
        if self.get_y() > 265:
            self.add_page()
        self.set_font("Courier", "B", 9.5)
        self.set_text_color(*NAVY)
        self.set_fill_color(*LIGHT)
        self.set_x(MARGIN)
        self.multi_cell(0, 6, text, fill=True, align="L")
        self.ln(2)

    def callout(self, label, text, color=AMBER):
        if self.get_y() > 258:
            self.add_page()
        self.set_font("Helvetica", "B", 9.5)
        self.set_text_color(*color)
        self.set_x(MARGIN)
        self.cell(0, 5.5, label, new_x="LMARGIN", new_y="NEXT")
        self.set_font("Helvetica", "I", 9.5)
        self.set_text_color(*GREY)
        self.set_x(MARGIN)
        self.multi_cell(0, 5, text)
        self.ln(2)

    def table(self, headers, rows, widths, align=None):
        if self.get_y() > 235:
            self.add_page()
        align = align or ["L"] * len(headers)
        self.set_font("Helvetica", "B", 8.3)
        self.set_fill_color(*NAVY)
        self.set_text_color(255, 255, 255)
        for h, w, a in zip(headers, widths, align):
            self.cell(w, 7, h, border=0, fill=True, align=a)
        self.ln(7)
        self.set_font("Helvetica", "", 8.3)
        fill = False
        for row in rows:
            self.set_fill_color(*LIGHT) if fill else self.set_fill_color(255, 255, 255)
            if isinstance(row, tuple) and row and row[0] == "__HL__":
                row = row[1]
                self.set_font("Helvetica", "B", 8.3)
                self.set_text_color(*AMBER)
            else:
                self.set_font("Helvetica", "", 8.3)
                self.set_text_color(20, 24, 22)
            y_start = self.get_y()
            x = self.get_x()
            for val, w, a in zip(row, widths, align):
                xc, yc = self.get_x(), self.get_y()
                self.multi_cell(w, 5.3, val, border=0, align=a, fill=True)
                self.set_xy(xc + w, yc)
            self.ln(5.3)
            fill = not fill
        self.ln(2)


pdf = Doc()
pdf.set_margins(MARGIN, 14, MARGIN)
pdf.set_auto_page_break(auto=True, margin=16)
pdf.add_page()

# ---- Title ----
pdf.set_font("Helvetica", "B", 20)
pdf.set_text_color(*NAVY)
pdf.cell(0, 10, "AMIRIS Worked Example - One Hour of the Market", new_x="LMARGIN", new_y="NEXT")
pdf.set_font("Helvetica", "I", 10.5)
pdf.set_text_color(*GREY)
pdf.multi_cell(0, 5.6, "A single, fully quantitative hour showing how demand, the plant fleet, subsidies, and fuel/CO2 prices combine to produce one market price")
pdf.set_font("Helvetica", "", 9)
pdf.set_x(MARGIN)
pdf.cell(0, 6, "Muideen Oladayo Ajiboye  |  28 July 2026", new_x="LMARGIN", new_y="NEXT")
pdf.ln(2)
y = pdf.get_y()
pdf.set_draw_color(*NAVY)
pdf.set_line_width(1)
pdf.line(MARGIN, y, 210 - MARGIN, y)
pdf.ln(4)

pdf.set_font("Helvetica", "B", 9.5)
pdf.set_text_color(*BAD)
pdf.set_x(MARGIN)
pdf.cell(0, 5.5, "Important: this is a constructed teaching example, not a real simulated hour.", new_x="LMARGIN", new_y="NEXT")
pdf.set_font("Helvetica", "", 9.5)
pdf.set_text_color(20, 24, 22)
pdf.multi_cell(0, 5,
    "The fleet sizes, efficiency ranges, markup bands, and fuel-price levels below are the real numbers "
    "from the Germany2019 scenario config. The specific hour, demand figure, wind capacity factor, and "
    "plant outage levels are chosen for this example - they are not read from any actual simulation output "
    "or historical timestamp. Use this to understand the mechanism, not as a citable data point."
)
pdf.ln(2)

# =====================================================================
pdf.h1("The Setup")
pdf.body(
    "One evening hour, winter, no solar output (after sunset), moderate wind. Everything below is computed "
    "from just five ingredients: how much electricity is needed, what capacity is physically available from "
    "each technology this hour, what it costs each technology to produce, what markup each plant type is "
    "willing to add or subtract, and what subsidy renewables are owed."
)

pdf.table(
    ["Ingredient", "Value this hour", "Source"],
    [
        ["Electricity demand", "68,000 MW", "Chosen for this example"],
        ["Wind onshore capacity factor", "0.40 (40% of nameplate)", "Chosen - within the real profile's 0.0-1.0 range"],
        ["Solar capacity factor", "0.0 (after sunset)", "Chosen"],
        ["Nuclear outage factor", "0.05 (5% offline)", "Chosen - within realistic range"],
        ["Lignite outage factor", "0.10 (10% offline)", "Chosen"],
        ["Hard coal outage factor", "0.08 (8% offline)", "Chosen"],
        ["CO2 allowance price", "25.00 EUR/tonne", "Chosen - realistic 2019 EUA level"],
    ],
    [55, 55, 68],
)

# =====================================================================
pdf.h1("Step 1 - Wind Onshore Dispatches First (near-zero cost, subsidised)")
pdf.body(
    "Wind has (near) zero fuel cost, so it always bids first in the merit order. Its dispatched output is "
    "simply its fleet capacity multiplied by this hour's capacity factor:"
)
pdf.formula("Available output = Installed Capacity x Capacity Factor\n= 53,500 MW x 0.40 = 21,400 MW")
pdf.body(
    "It bids at its variable operating cost, which is 0 EUR/MWh. Its real earnings do not depend on that bid "
    "- they come from its Feed-in Tariff (FIT) of 85.00 EUR/MWh, settled separately (Step 6). "
    "Remaining demand after wind: 68,000 - 21,400 = 46,600 MW."
)

# =====================================================================
pdf.h1("Step 2 - Nuclear Dispatches Next (cheap, and willing to bid negative)")
pdf.body("Available output first:")
pdf.formula("Available output = Installed Capacity x (1 - Outage Factor)\n= 9,524 MW x (1 - 0.05) = 9,048 MW")
pdf.body("Then its production cost, using the real formula AMIRIS applies to every conventional fuel type:")
pdf.formula(
    "Marginal Cost = (Fuel Price / Efficiency) + (CO2 Price x CO2 Emissions Factor) + Variable Opex\n"
    "= (2.00 / 0.330) + (25.00 x 0.0) + 0.50\n"
    "= 6.06 + 0.00 + 0.50 = 6.56 EUR/MWh"
)
pdf.body(
    "A trader agent then adds a markup drawn from nuclear's real bidding band (-150 to -100 EUR/MWh) - "
    "reflecting that shutting a nuclear plant down and restarting it costs far more than paying to stay "
    "online. This example draws -120:"
)
pdf.formula("Bid = Marginal Cost + Markup = 6.56 + (-120) = -113.44 EUR/MWh")
pdf.body("Remaining demand after nuclear: 46,600 - 9,048 = 37,552 MW.")

# =====================================================================
pdf.h1("Step 3 - Lignite Dispatches Next")
pdf.formula("Available output = 21,067 MW x (1 - 0.10) = 18,960 MW")
pdf.formula(
    "Marginal Cost = (5.00 / 0.380) + (25.00 x 0.364) + 2.00\n"
    "= 13.16 + 9.10 + 2.00 = 24.26 EUR/MWh"
)
pdf.body("Markup band: -60 to 0 EUR/MWh. This example draws -20:")
pdf.formula("Bid = 24.26 + (-20) = 4.26 EUR/MWh")
pdf.body(
    "18,960 MW is less than the 37,552 MW still needed, so lignite dispatches fully. "
    "Remaining demand: 37,552 - 18,960 = 18,592 MW."
)

# =====================================================================
pdf.h1("Step 4 - Hard Coal Sets the Price (the marginal unit)")
pdf.formula("Available output = 22,458 MW x (1 - 0.08) = 20,661 MW")
pdf.formula(
    "Marginal Cost = (13.00 / 0.4155) + (25.00 x 0.341) + 2.50\n"
    "= 31.29 + 8.53 + 2.50 = 42.32 EUR/MWh"
)
pdf.body("Markup band: -15 to +5 EUR/MWh. This example draws -5:")
pdf.formula("Bid = 42.32 + (-5) = 37.32 EUR/MWh")
pdf.body(
    "Only 18,592 MW of hard coal's 20,661 MW available is actually needed to meet the remaining demand - "
    "hard coal is the last, most expensive unit accepted. Natural gas and oil are never called on this hour; "
    "they stay idle and earn nothing."
)
pdf.callout(
    "This is the marginal unit.",
    "Whichever plant is the last one needed to meet demand sets the price for the ENTIRE market that hour - "
    "every accepted plant, however cheaply it actually bid, gets paid this same price. That is what 'day-ahead "
    "market clearing price' means."
)

# =====================================================================
pdf.h1("The Merit Order Stack, Start to Finish")
pdf.table(
    ["Technology", "Bid (EUR/MWh)", "Dispatched (MW)", "Cumulative (MW)", "Status"],
    [
        ["Wind onshore", "0.00", "21,400", "21,400", "Fully dispatched"],
        ["Nuclear", "-113.44", "9,048", "30,448", "Fully dispatched"],
        ["Lignite", "4.26", "18,960", "49,408", "Fully dispatched"],
        ("__HL__", ["Hard coal", "37.32", "18,592", "68,000", "MARGINAL - sets price"]),
        ["Natural gas / Oil", "n/a", "0", "68,000", "Idle - not needed"],
    ],
    [38, 30, 32, 32, 46],
    align=["L", "R", "R", "R", "L"],
)
pdf.callout("Result:", "Demand (68,000 MW) is met exactly. Clearing price = 37.32 EUR/MWh.", color=GOOD)

# =====================================================================
pdf.h1("Step 5 - Everyone Accepted Gets Paid the SAME Price")
pdf.body(
    "Day-ahead markets (and AMIRIS) use uniform pricing: every accepted plant is paid the clearing price, "
    "not its own bid. This is the single most counter-intuitive mechanic worth having ready for the meeting - "
    "notice nuclear bid -113.44 but is paid +37.32:"
)
pdf.table(
    ["Technology", "MWh this hour", "x Clearing price", "= Revenue (EUR)"],
    [
        ["Wind onshore (market leg)", "21,400", "37.32", money(37.32 * 21400)],
        ["Nuclear", "9,048", "37.32", money(37.32 * 9048)],
        ["Lignite", "18,960", "37.32", money(37.32 * 18960)],
        ["Hard coal", "18,592", "37.32", money(37.32 * 18592)],
    ],
    [55, 35, 35, 45],
    align=["L", "R", "R", "R"],
)

# =====================================================================
pdf.h1("Step 6 - How Wind's Subsidy Actually Settles")
pdf.body(
    "Wind sold 21,400 MWh at the market price of 37.32 EUR/MWh, earning 798,648 EUR from the market alone. "
    "But its FIT guarantees 85.00 EUR/MWh regardless of what the market clears at, so the support scheme "
    "pays the difference:"
)
pdf.formula(
    "FIT top-up = (FIT rate - Market price) x MWh\n"
    "= (85.00 - 37.32) x 21,400 = 47.68 x 21,400 = 1,020,352 EUR"
)
pdf.formula(
    "Total wind revenue = Market revenue + FIT top-up\n"
    "= 798,648 + 1,020,352 = 1,819,000 EUR   (= 85.00 x 21,400, exactly the guaranteed rate)"
)
pdf.body(
    "This is precisely why a subsidised renewable can rationally bid at (or even below) zero: its real income "
    "is decoupled from the market price it helped set."
)

# =====================================================================
pdf.h1("What If Wind Had Been Weaker? (capacity factor 0.40 -> 0.25)")
pdf.body(
    "Same demand, same fleet, only the wind capacity factor changes. This shows how sensitive the clearing "
    "price is to a single input:"
)
pdf.formula("Wind output = 53,500 x 0.25 = 13,375 MW   (8,025 MW less than before)")
pdf.body(
    "That shortfall has to be made up somewhere. Nuclear, lignite, and now ALL of hard coal's available "
    "20,661 MW get fully dispatched, and the remaining gap is covered by natural gas (CCGT) - a technology "
    "that was completely idle in the base case:"
)
pdf.formula(
    "Gas Marginal Cost = (20.00 / 0.5665) + (25.00 x 0.201) + 1.20\n"
    "= 35.30 + 5.03 + 1.20 = 41.53 EUR/MWh   (markup drawn: 0)"
)
pdf.callout(
    "Price impact:",
    "Clearing price rises from 37.32 to 41.53 EUR/MWh (+4.21, about +11%) purely because wind output fell - "
    "a clean illustration of why the generation-profile input is described as the single most critical "
    "renewable data item.",
    color=BAD,
)

# =====================================================================
pdf.h1("Other Things Worth Knowing")
pdf.body(
    "Negative prices only happen when the negatively-bidding block (nuclear here, sometimes joined by "
    "lignite or other must-run plants) is, by itself, LARGER than demand - forcing the market to accept some "
    "negative bids just to place all the electricity that legally must be produced. In this example demand "
    "was high enough that hard coal was still needed, so the price stayed positive despite nuclear's very "
    "negative bid sitting underneath it in the stack."
)
pdf.body(
    "Storage would be watching this same price. If a storage operator's rolling 24-168 hour forecast expects "
    "a materially higher price in a few hours (e.g. tomorrow morning's demand peak), 37.32 EUR/MWh looks "
    "cheap enough to charge into, adding a bit more demand to this hour and a bit more supply to that future "
    "one - it does not see or plan against the whole year at once, only its rolling window."
)
pdf.body(
    "Real AMIRIS is more granular than this example: each fuel type is actually split into several individual "
    "plant 'blocks' (via BlockSizeInMW) with slightly different efficiencies drawn across the Min-Max range, "
    "so the real merit order has many small steps within each technology rather than the single flat bid per "
    "technology shown here. The mechanism is identical - this example just uses one representative bid per "
    "technology to keep the arithmetic readable."
)

# =====================================================================
pdf.h1("Formula Reference")
pdf.formula(
    "Available output (conventional)  =  Installed Capacity x (1 - Outage Factor)\n"
    "Available output (renewable)     =  Installed Capacity x Capacity Factor\n"
    "Marginal Cost                    =  (Fuel Price / Efficiency) + (CO2 Price x CO2 Factor) + Variable Opex\n"
    "Bid Price                        =  Marginal Cost + Markup   (markup drawn from [minMarkup, maxMarkup])\n"
    "Clearing Price                   =  bid of the last (marginal) unit needed to meet demand\n"
    "Settlement (uniform pricing)     =  every accepted unit is paid the Clearing Price, not its own bid\n"
    "FIT top-up                       =  max(0, FIT rate - Clearing Price) x MWh produced\n"
    "Storage round-trip efficiency    =  Charging Efficiency x Discharging Efficiency"
)

pdf.output("AMIRIS_Worked_Example.pdf")
print("Saved AMIRIS_Worked_Example.pdf")
