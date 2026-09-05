"""Generates AMIRIS_Session_2026-09-01.pdf - a very simple, plain-language walkthrough of
today's specific conversation: what was asked, and what happened, in the order it happened.
Written for someone with no technical background - no jargon left unexplained, short
sentences, everyday analogies. Separate from the cumulative Progress Report, which is more
technical and covers the whole project. Follows on from the 28 August session (the price-cap
investigation and the idea shortlist). Today covered two more correlation-improvement tests
(one a dead end, one a real-but-limited lever), then the first scoping steps for the big
cross-border export/market-coupling build."""
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
        self.cell(0, 8, f"AMIRIS Session Notes - 1 September 2026                                                                                    Page {self.page_no()}", align="C")

    def h1(self, text):
        if self.get_y() > 255:
            self.add_page()
        self.ln(3)
        self.set_font("Helvetica", "B", 15)
        self.set_text_color(*NAVY)
        self.set_x(MARGIN)
        self.multi_cell(0, 7.5, text)
        y = self.get_y()
        self.set_draw_color(*NAVY)
        self.set_line_width(0.6)
        self.line(MARGIN, y, 210 - MARGIN, y)
        self.ln(4)

    def question(self, text):
        if self.get_y() > 255:
            self.add_page()
        self.set_font("Helvetica", "BI", 10.5)
        self.set_text_color(*AMBER)
        self.set_x(MARGIN)
        self.multi_cell(0, 5.6, f'You asked: "{text}"')
        self.ln(2)

    def body(self, text):
        self.set_font("Helvetica", "", 10.5)
        self.set_text_color(20, 24, 22)
        self.set_x(MARGIN)
        self.multi_cell(0, 5.8, text)
        self.ln(2)

    def result(self, label, text, color=GOOD):
        if self.get_y() > 255:
            self.add_page()
        self.set_font("Helvetica", "B", 10.5)
        self.set_text_color(*color)
        self.set_x(MARGIN)
        self.multi_cell(0, 5.6, label)
        self.set_font("Helvetica", "", 10.5)
        self.set_text_color(20, 24, 22)
        self.set_x(MARGIN)
        self.multi_cell(0, 5.8, text)
        self.ln(3)

    def analogy(self, text):
        if self.get_y() > 250:
            self.add_page()
        self.set_fill_color(*LIGHT)
        self.set_font("Helvetica", "I", 10)
        self.set_text_color(60, 66, 63)
        self.set_x(MARGIN)
        self.multi_cell(180, 5.6, f"In plain terms: {text}", fill=True)
        self.ln(3)

    def table(self, headers, rows, widths):
        if self.get_y() > 240:
            self.add_page()
        self.set_x(MARGIN)
        self.set_font("Helvetica", "B", 9.5)
        self.set_fill_color(*NAVY)
        self.set_text_color(255, 255, 255)
        for h, w in zip(headers, widths):
            self.cell(w, 7, h, border=0, align="C", fill=True)
        self.ln()
        self.set_font("Helvetica", "", 9.5)
        for i, row in enumerate(rows):
            self.set_x(MARGIN)
            self.set_fill_color(*LIGHT) if i % 2 == 0 else self.set_fill_color(255, 255, 255)
            self.set_text_color(20, 24, 22)
            for cell, w in zip(row, widths):
                self.cell(w, 6.5, str(cell), border=0, align="C", fill=True)
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
pdf.multi_cell(0, 10, "What We Did Today")
pdf.set_font("Helvetica", "I", 11)
pdf.set_text_color(*GREY)
pdf.set_x(MARGIN)
pdf.multi_cell(0, 5.6, "A simple, no-jargon walkthrough of today's conversation - what was asked, and what happened")
pdf.set_font("Helvetica", "", 9.5)
pdf.set_x(MARGIN)
pdf.cell(0, 6, "1 September 2026", new_x="LMARGIN", new_y="NEXT")
pdf.ln(2)
y = pdf.get_y()
pdf.set_draw_color(*NAVY)
pdf.set_line_width(1)
pdf.line(MARGIN, y, 210 - MARGIN, y)
pdf.ln(5)

pdf.body(
    "Today finished off the small-idea testing from the last session (two more real tests, "
    "one a dead end and one a real-but-limited lever), then made a start on properly planning "
    "the big remaining idea: letting the model sell extra power abroad, not just buy it."
)

# =====================================================================
pdf.h1("1. Testing a Real Start-Up Cost for Power Plants")
pdf.question("Yes, test the cycling cost idea.")
pdf.result(
    "Sourced a real number from a genuine published study, built a separate test, and ran it.",
    "Real power plants cost real money to shut down and restart, so they sometimes keep "
    "running even at a low price rather than switch off. Our model currently gives every plant "
    "a shut-down cost of exactly zero. Found a real, peer-reviewed study on actual German "
    "power plant start-up costs and used its real figures (roughly EUR50,000-70,000 per start "
    "for a large coal/lignite plant, EUR60,000 for a gas plant, converted into our model's "
    "units). Built this as its own separate model version, kept completely apart from every "
    "other version, and ran a full simulation."
)
pdf.result(
    "Result: zero difference, at any point in the whole year.",
    "Every single one of the 8,760 hours of the year came out at EXACTLY the same price, to "
    "the cent, with or without the new setting. Investigated why by looking inside AMIRIS's "
    "own program: the number IS genuinely calculated somewhere inside it, but that calculation "
    "is never actually connected to the price a power plant offers when it bids into the "
    "market. So this setting exists in the program but simply isn't wired up to anything that "
    "matters here - a cleaner, more conclusive dead end than the price-cap idea from "
    "yesterday, since there's no trade-off to weigh at all.",
    color=BAD,
)
pdf.analogy(
    "Like flipping a light switch on a wall that was never actually connected to any wire - "
    "the switch is real, but nothing happens when you use it."
)

# =====================================================================
pdf.h1("2. Trying Something That Actually Works: Lignite's Bidding Floor")
pdf.question("Yes, source a real value and test it.")
pdf.result(
    "Checked the mechanism FIRST this time, learning from yesterday's surprise.",
    "Before spending time researching a number, opened up the exact formula our model uses to "
    "set a power plant's price - and this time confirmed it really is connected. Our model "
    "currently lets lignite (brown coal) plants bid as low as -60 EUR/MWh below their true "
    "cost, by far the most generous allowance of any fuel type. There's no published real-world "
    "figure for this exact setting, so instead anchored the test to something we could look up: "
    "how often Germany's REAL electricity market actually goes negative (3-5% of the time), "
    "compared to our model's much higher 18%."
)
pdf.result(
    "Result: tested four values (-60, -40, -20, -10) - a real effect, but not on the number that matters.",
    "This time 6,218 of the year's 8,760 hours changed price - proof the setting really is "
    "connected, a genuine difference from the cycling-cost test. The average price gap to "
    "Brainpool and how often we go negative both improved a little as the setting was "
    "narrowed - small, real, welcome improvements. But our main trustworthy score for how well "
    "the model's DAY-TO-DAY SHAPE matches Brainpool's barely moved at all across every single "
    "value tested. A simpler-looking overall score did jump around a lot, but not in a "
    "sensible, step-by-step way - which is exactly the kind of misleading pattern we've caught "
    "before in this project, caused by a handful of unusual hours, not real improvement.",
    color=AMBER,
)
pdf.result(
    "Decision: a real, working idea - just not one worth adopting.",
    "Both new tests, and the price-cap test from yesterday, are now fully written up in the "
    "Progress Report and added as new slides in the supervisor deck. Between the three, we've "
    "now properly tested every reasonably-sized idea available - which makes the case for the "
    "one big remaining option (cross-border export) considerably stronger."
)

# =====================================================================
pdf.h1("3. Starting to Plan the Big One: Selling Power Abroad")
pdf.question("Let's start scoping the export/market-coupling build.")
pdf.result(
    "Found AMIRIS's own real, ready-made template for exactly this, and worked out what a genuine version would actually require.",
    "AMIRIS comes with a working example of two market 'zones' trading with each other in both "
    "directions, not just one buying from the other like our current setup. Studied it closely: "
    "it needs our existing single market swapped for a two-way version, a small 'coupling' "
    "referee agent added to match up both sides, and - the big piece - an entire SECOND "
    "country-scale model built alongside ours, with its own power plants, its own renewable "
    "energy, and its own demand, plus real hour-by-hour data on how much power can physically "
    "flow between the two. Confirmed that real data for the cross-border capacity part does "
    "exist and is freely available (the same kind of official European source already used for "
    "our import numbers)."
)
pdf.analogy(
    "Everything we've built so far is one country with a mailbox that can only receive "
    "packages (imports). This next step is building a second country next door AND installing "
    "a two-way road between them - a much bigger undertaking than any adjustment tried so far, "
    "which is exactly why it was saved for last."
)
pdf.body(
    "This is just the start of the planning - no building has begun yet. The next step is a "
    "specific scoping question about how big to make that 'second country': one simplified "
    "combined stand-in for the rest of Europe (matching how our import numbers already work), "
    "or several real, separately-modelled neighbouring countries (more realistic, but "
    "considerably more work). This decision will shape how big an undertaking the whole build "
    "turns out to be."
)

pdf.output(r"C:\Users\MuideenOA\Desktop\PyTut\Amiris\AMIRIS_Session_2026-09-01.pdf")
print("Saved AMIRIS_Session_2026-09-01.pdf")
