"""Generates AMIRIS_Session_2026-09-17.pdf - a very simple, plain-language walkthrough of
this session's conversation: what was asked, and what happened, in the order it happened.
Written for someone with no technical background - no jargon left unexplained, short
sentences, everyday analogies. Separate from the cumulative Progress Report, which is more
technical and covers the whole project. This session covered a deadline update, a discussion
of what to try next, and a full real-data rebuild of the Rest-of-Europe zone on a different
base year."""
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
        self.cell(0, 8, f"AMIRIS Session Notes - 17 September 2026                                                                                    Page {self.page_no()}", align="C")

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
pdf.multi_cell(0, 10, "What We Did This Session")
pdf.set_font("Helvetica", "I", 11)
pdf.set_text_color(*GREY)
pdf.set_x(MARGIN)
pdf.multi_cell(0, 5.6, "A simple, no-jargon walkthrough of this session's conversation - what was asked, and what happened")
pdf.set_font("Helvetica", "", 9.5)
pdf.set_x(MARGIN)
pdf.cell(0, 6, "17 September 2026", new_x="LMARGIN", new_y="NEXT")
pdf.ln(2)
y = pdf.get_y()
pdf.set_draw_color(*NAVY)
pdf.set_line_width(1)
pdf.line(MARGIN, y, 210 - MARGIN, y)
pdf.ln(5)

pdf.body(
    "A longer working session covering three things: a deadline update, a discussion of what "
    "to try next with the extra time, and a full, real-data rebuild of one part of the model "
    "prompted by new information about how the commercial forecaster (Brainpool) builds its "
    "own export scenarios."
)

# =====================================================================
pdf.h1("1. Deadline Update, and What's Left to Try")
pdf.question("What else do we have to try, ENTSO-E platform is working fine now.")
pdf.result(
    "Flagged the tight remaining timeline honestly before recommending anything.",
    "At that point the write-up deadline was 6 days away, so the recommendation was to stop "
    "opening new, open-ended experiments and treat the strongest result so far as final, "
    "putting the remaining time into the write-up instead.",
)
pdf.question("There has been call to extend the deadline. I now have January 2027 to complete it. What else should we try?")
pdf.result(
    "With four extra months, revisited the same list and reprioritised.",
    "Recommended two real remaining options: (1) attempting a direct code-level fix inside "
    "AMIRIS's own engine to chase the last unresolved gap (results drifting slightly further "
    "from the real answer the further into the future a year is), and (2) sourcing more "
    "detailed real data between neighbouring countries directly, rather than only through "
    "Germany, for a future attempt at splitting the aggregate Europe zone into individual "
    "countries. Also flagged some smaller, lower-effort items worth doing regardless.",
)

# =====================================================================
pdf.h1("2. A New, Real Question: Which Year's Data Should the Rest-of-Europe Model Be Based On?")
pdf.question("Brainpool uses the 2024 data for the export scenarios, we are using 2023 data pulled from Eurostat, let us consider the 2024 data.")
pdf.result(
    "Checked first whether 2024 data was actually available to use, rather than assuming it.",
    "The Rest-of-Europe part of the model was built using real 2023 figures throughout. Before "
    "committing to rebuild anything, ran a direct, live check against the real data sources - "
    "confirmed 2024 figures were genuinely published and available from both of them.",
)
pdf.analogy(
    "Like double-checking a shop actually has this year's edition in stock before promising a "
    "customer you'll bring it to them - rather than assuming and finding out only after "
    "starting the order."
)

# =====================================================================
pdf.h1("3. Rebuilding the Rest-of-Europe Zone on 2024 Data")
pdf.result(
    "Rebuilt the whole Rest-of-Europe side of the model a second time, changing only the year the real data comes from.",
    "Everything else about how the model works stayed exactly the same - the same countries, "
    "the same real methods for splitting hydro power into different types, the same subsidy "
    "assumptions, the same underlying weather data. Only the underlying real demand, capacity, "
    "and cross-border trading numbers were refreshed to 2024's real figures, so that any "
    "difference in the outcome could be attributed cleanly to the change in year, and nothing "
    "else. Kept as a brand new, separate build alongside the existing one - nothing already "
    "built was touched or overwritten.",
)
pdf.result(
    "An unexpected bonus turned up along the way: a long-standing small gap closed itself.",
    "One neighbouring country's data (Sweden) had failed to download every single time this "
    "project tried, going all the way back to August - a known, documented, honestly-reported "
    "gap. This time it downloaded successfully on the very first attempt, now that the data "
    "source itself is running normally again. This new build is the first in the whole project "
    "to include real data for every single neighbouring country, with no gaps at all.",
    color=GOOD,
)
pdf.result(
    "One small real technical snag found and fixed along the way.",
    "A helper script that fetches Switzerland's data crashed right at the very last step, "
    "while trying to save a small summary file - caused by a timestamp being saved in a format "
    "the summary file doesn't understand. The actual data itself had already saved correctly "
    "moments earlier, so nothing was lost - the summary was simply rebuilt by hand from the "
    "already-saved data.",
    color=BAD,
)

# =====================================================================
pdf.h1("4. The Result: An Honest Comparison")
pdf.body(
    "Ran the new 2024-based build through the model for the full year, then compared it "
    "against both the real Brainpool forecast and against this project's existing best result "
    "(which uses 2023 data)."
)
pdf.table(
    ["What we measure", "2023-based build (existing best)", "2024-based build (new)"],
    [
        ["Hours the model ran short of power", "7", "5"],
        ["How closely prices track Brainpool's (higher = better)", "0.72", "0.71"],
        ["Average size of price mistakes", "16.69", "17.60"],
    ],
    [80, 60, 50],
)
pdf.result(
    "Honest finding: switching to 2024 data did not make the result better - it came out very slightly worse, though still close.",
    "Two of the three measures moved slightly in the wrong direction, though only by a small "
    "amount, not a dramatic swing. The third measure (hours running short of power) actually "
    "improved slightly. Taken together, this is a genuinely useful finding even though it "
    "isn't an improvement: it shows the model's result doesn't depend heavily on which "
    "specific year's Rest-of-Europe data is used, which is reassuring for how trustworthy the "
    "overall result is. The existing 2023-based build remains the project's standing best "
    "result; the new 2024-based build is kept fully saved alongside it as real, documented "
    "evidence of this check, not deleted or discarded.",
    color=NAVY,
)
pdf.analogy(
    "Like re-weighing yourself on a different, more recently-calibrated scale to double-check "
    "yesterday's reading - the new number came back almost the same, just slightly different, "
    "which is actually a good sign that yesterday's reading wasn't a fluke."
)

# =====================================================================
pdf.h1("5. Documentation Updated")
pdf.body(
    "Folded this whole investigation into the main technical Progress Report as its own "
    "numbered phase (Phase 44), including the honest side-by-side comparison table above, so "
    "it stays part of the project's permanent record."
)

pdf.output(r"C:\Users\MuideenOA\Desktop\PyTut\Amiris\AMIRIS_Session_2026-09-17.pdf")
print("Saved AMIRIS_Session_2026-09-17.pdf")
