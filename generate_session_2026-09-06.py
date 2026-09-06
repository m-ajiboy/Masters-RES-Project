"""Generates AMIRIS_Session_2026-09-06.pdf - a very simple, plain-language walkthrough of
this session's conversation: what was asked, and what happened, in the order it happened.
Written for someone with no technical background - no jargon left unexplained, short
sentences, everyday analogies. Separate from the cumulative Progress Report, which is more
technical and covers the whole project. Follows on from the 5 September session (which ended
with the supervisor deck and progress report updated through Phase 40, and the full
market-coupling build's best result standing at Phase 37). This session covered: setting up
real version control for the project (with a real credential catch along the way), then three
more real experiments chasing the very last open thread on the market-coupling work (a
storage test, a single-country pilot, and a full 10-country build that hit and fixed a
genuine engine bug), and finished by bringing both the supervisor deck and the progress
report fully up to date with all of it."""
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
        self.cell(0, 8, f"AMIRIS Session Notes - 6 September 2026                                                                                    Page {self.page_no()}", align="C")

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
pdf.multi_cell(0, 10, "What We Did This Session")
pdf.set_font("Helvetica", "I", 11)
pdf.set_text_color(*GREY)
pdf.set_x(MARGIN)
pdf.multi_cell(0, 5.6, "A simple, no-jargon walkthrough of this session's conversation - what was asked, and what happened")
pdf.set_font("Helvetica", "", 9.5)
pdf.set_x(MARGIN)
pdf.cell(0, 6, "6 September 2026", new_x="LMARGIN", new_y="NEXT")
pdf.ln(2)
y = pdf.get_y()
pdf.set_draw_color(*NAVY)
pdf.set_line_width(1)
pdf.line(MARGIN, y, 210 - MARGIN, y)
pdf.ln(5)

pdf.body(
    "Two parts today. First, properly saving all our work under real version control for "
    "the first time - and catching a real security slip along the way. Second, three more "
    "real experiments chasing the very last open question on the cross-border trading work: "
    "a storage test, a single-country test, and a full 10-country build that hit and fixed a "
    "genuine software bug in AMIRIS itself."
)

# =====================================================================
pdf.h1("1. Setting Up Real Version Control - and Catching a Real Slip")
pdf.question("Commit these changes.")
pdf.result(
    "Found the project had never actually been under its own version control - and stopped before committing a real credential by mistake.",
    "Checking first (rather than just running the commit) turned up two real problems: the "
    "version-control history on this computer covered the ENTIRE home folder, not just this "
    "project, mixing in unrelated personal files - and partway through preparing the commit, "
    "spotted that the file holding our real API access tokens (ENTSO-E, renewables.ninja) was "
    "about to be saved into that history by mistake. Stopped, excluded it properly, and set "
    "up a clean, separate, dedicated history just for this project instead - the safer choice "
    "given what the first option risked."
)
pdf.result(
    "Fixed the author details too, once flagged.",
    "The save was initially credited to the wrong name/email (a leftover default on this "
    "shared computer). Corrected it to the right one and confirmed the save now shows the "
    "right authorship - since this was the very first save in a brand new history, fixing it "
    "in place was clean and safe, with nothing else to disturb."
)
pdf.body(
    "Clarified after a follow-up question: this save exists only on this computer for now, "
    "not on GitHub - nothing has been uploaded anywhere yet. That's a separate, deliberate "
    "next step whenever you're ready for it."
)

# =====================================================================
pdf.h1("2. One More Lead on the Last Open Question")
pdf.question("Continue building out the export module improvements.")
pdf.result(
    "Tested directly whether the other side's own storage was the real limiter - and ruled it out.",
    "The one open thread left: a small number of hours where Germany imports less than it "
    "could, even with room to spare. Checked directly whether the rest of Europe's own "
    "batteries and reservoirs were simply empty during those hours. They weren't - neither "
    "ever came close to its own limit, in either year checked. Rules out 'nothing left to "
    "give' as the explanation, and points more firmly at the trading engine's own internal "
    "logic as the real cause - not yet fully provable without a deeper software change."
)

# =====================================================================
pdf.h1("3. Pushing Further: One Real Country Instead of the Combined Zone")
pdf.question("What of building for each of the countries, maybe we should try that?")
pdf.result(
    "Flagged the real risk first, then built a single-country test as a fair first check.",
    "Warned directly that splitting every country out separately, the same simple way, could "
    "make things WORSE rather than better, based on what the earlier work had already shown. "
    "You agreed a single-country test first was the sensible way to check that before "
    "committing to the bigger build. Built France properly as its own real zone - the "
    "largest economy involved, with enough real data already on hand to do it right."
)
pdf.result(
    "Result: a real step backward, with a clear, understood reason.",
    "The 'ran out of power' hours jumped sharply (7 to 167) once France was split out. "
    "Checked why rather than leaving it a mystery: France's own huge nuclear fleet had been "
    "quietly propping up the WHOLE combined zone's supply. Pulled out on its own, the "
    "remaining combined zone lost that cushion, while France's own leftover cheap power could "
    "no longer reach it either, stuck behind a single narrow border link to Germany.",
    color=BAD,
)

# =====================================================================
pdf.h1("4. Going All the Way: All 10 Real Countries at Once")
pdf.question("Keep digging into the Denmark bug first.")
pdf.result(
    "Built all 10 real neighbouring countries as their own zones - and hit a genuine software bug.",
    "Since one country made things worse for a clear reason, the natural next test was "
    "whether the SAME problem compounds across all 10, or whether something different "
    "happens at full scale. The build itself crashed - and this time, unlike every earlier "
    "problem in this project, the cause wasn't obvious from checking the settings."
)
pdf.result(
    "Tracked it down properly rather than guessing: isolated it to Denmark specifically.",
    "Tested one country at a time. Austria worked perfectly. Denmark, tested the same way, "
    "crashed every time. Checked Denmark's real numbers: its actual hydropower is only "
    "7 megawatts - thousands of times smaller than every other country involved. Proved this "
    "was the real cause, not a coincidence, by testing it twice in each direction: the exact "
    "same setup with just the numbers made bigger ran perfectly, every time; the exact same "
    "setup with the real tiny numbers crashed, every time. Also tried simply leaving "
    "Denmark's hydropower out entirely - that did NOT fix it either, so it had to be "
    "properly patched, not just removed.",
)
pdf.result(
    "Fixed it honestly: a clearly labelled technical workaround, not invented data.",
    "Applied a documented, openly-artificial minimum size to Denmark's (and the "
    "similarly-tiny Netherlands') hydropower, purely so the software could run - clearly "
    "marked in the file itself as NOT representing either country's real hydropower scale. "
    "With that fix in place, the full 10-country build ran cleanly all the way through."
)
pdf.table(
    ["", "Combined zone (best)", "France alone", "All 10 countries"],
    [
        ["'Ran out of power' hours", "7", "167", "120"],
        ["Average price gap, ordinary days", "-2.90", "+9.65", "+4.87"],
        ["Match quality (trustworthiness)", "0.717", "0.716", "0.731 (best yet)"],
    ],
    widths=[62, 40, 38, 42],
)
pdf.result(
    "Result: better than expected, but still not the winning approach.",
    "Genuinely surprising: going all the way to 10 real countries did BETTER than splitting "
    "out just one - likely because Germany can now draw on many countries' cheap power at "
    "once, instead of being stuck behind a single narrow link. But it still falls short of "
    "the original combined-zone approach on the two measures that matter most. Decision: keep "
    "the combined zone as our best, standing result - both new builds are kept as real, "
    "documented evidence, not deleted.",
    color=AMBER,
)

# =====================================================================
pdf.h1("5. Bringing Both Documents Up to Date")
pdf.question("Update the supervisor deck with Phase 43. / Update the daily session-recap PDF too.")
pdf.result(
    "Both the supervisor deck and the technical progress report now reflect all of today's real work.",
    "Added five new slides to the supervisor deck covering the storage test, the France "
    "result, the Denmark bug story, and the final 10-country comparison table - placed right "
    "after the earlier market-coupling section and before the closing summary slides. The "
    "technical progress report already had the full written record of all three experiments "
    "from earlier in the session."
)

pdf.output(r"C:\Users\MuideenOA\Desktop\PyTut\Amiris\AMIRIS_Session_2026-09-06.pdf")
print("Saved AMIRIS_Session_2026-09-06.pdf")
