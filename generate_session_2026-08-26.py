"""Generates AMIRIS_Session_2026-08-26.pdf - a very simple, plain-language walkthrough of
today's specific conversation: what was asked, and what happened, in the order it happened.
Written for someone with no technical background - no jargon left unexplained, short
sentences, everyday analogies. Separate from the cumulative Progress Report, which is more
technical and covers the whole project. Follows straight on from yesterday's session
(AMIRIS_Session_2026-08-25.pdf), which ended with the decision to adopt a smaller import
amount for 2028 and 2029."""
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
        self.cell(0, 8, f"AMIRIS Session Notes - 26 August 2026                                                                                    Page {self.page_no()}", align="C")

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
pdf.cell(0, 6, "26 August 2026", new_x="LMARGIN", new_y="NEXT")
pdf.ln(2)
y = pdf.get_y()
pdf.set_draw_color(*NAVY)
pdf.set_line_width(1)
pdf.line(MARGIN, y, 210 - MARGIN, y)
pdf.ln(5)

pdf.body(
    "Quick reminder of where yesterday left off: after testing 2028 and 2029 (years the "
    "model was never specifically tuned for), a re-tuning test found that using a smaller "
    "import amount (20,000 instead of 30,000 megawatts) made the model's hour-to-hour "
    "rhythm match Brainpool's real prices much better - so that smaller amount was adopted "
    "for both years. Today picked up right there, by asking for a fuller check before "
    "settling on that decision."
)

# =====================================================================
pdf.h1("1. A more complete comparison, including a third option")
pdf.question("Try 15,000 MW too and compare all three.")
pdf.body(
    "Rather than just comparing the newly-adopted 20,000 setting against the original "
    "30,000, an even smaller option (15,000) was added to the comparison too - and this "
    "time, the FULL picture was checked, not just the 'ordinary hours only' view that's been "
    "used as the main measuring stick throughout this whole project. Conveniently, all three "
    "results already existed from an earlier test, so nothing needed to be re-run - just "
    "compared properly, side by side."
)
pdf.table(
    ["", "15,000 MW", "20,000 MW", "30,000 MW"],
    [
        ["Germany2028: hours it ran out of power", "49", "22", "1"],
        ["Germany2028: average price", "69.22", "59.30", "50.79"],
        ["Germany2029: hours it ran out of power", "116", "63", "8"],
        ["Germany2029: average price", "94.51", "75.51", "55.84"],
    ],
    [70, 40, 40, 40],
)
pdf.result(
    "Finding: the full picture tells a very different story than the narrow one did.",
    "Looking only at 'ordinary hours' (excluding the rare hours where the model ran "
    "completely out of power), the smaller import amounts genuinely did look better - that "
    "part of yesterday's finding was real. But once the FULL year is considered, including "
    "those 'ran out of power' hours, the picture flips: the smaller the import amount, the "
    "WORSE the overall match gets, and the average price ends up badly overshooting "
    "Brainpool's real number - for 2029 at the smallest setting, the model's average price "
    "came out 53% too high. That's because 'ran out of power' hours aren't just excluded "
    "from the count - Brainpool's real forecast barely ever has any, so having 22 to 116 of "
    "them a year is itself a sign the overall picture is getting less realistic, not more.",
    color=BAD,
)
pdf.analogy(
    "picture judging a bus service only by how punctual it is on the routes it actually "
    "completes, while ignoring how often it cancels a route entirely. A service that "
    "cancels more routes might look more 'punctual' on paper for the routes it does run - "
    "but that's not really a better bus service overall. That's what was happening here: "
    "the 'ordinary hours' score looked great, but only because more and more hours were "
    "being quietly excluded as 'the model gave up' hours."
)

# =====================================================================
pdf.h1("2. Deciding what to actually keep")
pdf.question("Yes, fold it in and keep 30,000 MW as the default.")
pdf.body(
    "With the fuller picture in hand, the decision was made to undo yesterday's change and "
    "go back to the original 30,000 setting for both 2028 and 2029, rather than keep the "
    "smaller one."
)
pdf.result(
    "Done - reverted cleanly, with everything kept on file.",
    "Both years are back to their original 30,000 setting as the live, default version. "
    "Nothing from yesterday's exploration was thrown away - all four tested amounts "
    "(15,000, 20,000, 25,000, and 37,650) remain saved separately, so the full evidence "
    "trail - including WHY the smaller amount was tried, and WHY it was ultimately not kept "
    "- is there for anyone who wants to look at it again later.",
    color=GOOD,
)
pdf.body(
    "This closes the loop honestly: a real lever was found and tested, adopted based on the "
    "best information available at the time, and then reconsidered and reversed once a "
    "fuller check turned up something the first check had missed - exactly the kind of "
    "careful, evidence-first process this whole project has followed throughout."
)

# =====================================================================
pdf.h1("3. Looking for what else might be fixable")
pdf.question("What other small adjustments are left to try?")
pdf.body(
    "With the import-amount question settled for now, the natural next move was the same "
    "'where exactly does the mismatch happen' check used many times already this project - "
    "but this time run on 2028 and 2029 specifically, since it had never actually been done "
    "for those two years before."
)
pdf.result(
    "A genuine surprise turned up: the weekday/weekend pattern had flipped compared to 2027.",
    "In 2027, weekdays actually matched Brainpool's real prices BETTER than weekends. In "
    "both 2028 and 2029, that flips hard - weekdays match much WORSE than weekends, and by a "
    "bigger margin than anything seen in 2027. That looked like a real, specific thing worth "
    "chasing, rather than random noise.",
    color=AMBER,
)

# =====================================================================
pdf.h1("4. Chasing the weekday puzzle down to a real bug")
pdf.question("Yes.")
pdf.body(
    "Digging into why weekdays specifically were doing worse turned up something concrete: "
    "checking the model's own demand numbers by real day of the week showed Fridays coming "
    "out unusually LOW and Sundays unusually HIGH - the opposite of what real electricity use "
    "actually looks like (real weekday use is highest, real Sunday use is lowest). That's not "
    "a modelling choice - that's a sign something is actually broken."
)
pdf.result(
    "Found it: a genuine calendar bug, quietly present in the project's own 'best' 2027 build since it was built.",
    "The demand shape for 2027 and 2029 is built by borrowing a real year's worth of German "
    "electricity usage (2016) and stretching or squeezing it to fit the target year. 2016 has "
    "one extra day (a leap year), so that extra day has to be removed to make it fit a normal "
    "year. The day that was being removed was February 29th - a day sitting right in the "
    "MIDDLE of the year. Removing a day from the middle quietly shifts every single day "
    "after it by one day of the week for the rest of the year - so from March onward (10 out "
    "of 12 months), every day of the week was mislabelled. This had been sitting undetected "
    "in the project's main 2027 build since it was first built.",
    color=BAD,
)
pdf.analogy(
    "picture a calendar where someone rips out one page from the middle of the year (say, "
    "March 15th) and just glues the rest of the pages back together without renumbering "
    "anything. From that point on, every date on the calendar quietly lands on the wrong day "
    "of the week for the rest of the year - even though January and February still look "
    "completely correct. The mistake is invisible unless you specifically check a date deep "
    "into the year, which is exactly what the earlier weekday check happened to do."
)

# =====================================================================
pdf.h1("5. Fixing it and checking how much it recovers")
pdf.question("Yes, fix it - rebuild 2027 and 2029, and check the recovery.")
pdf.body(
    "The fix: instead of removing the extra day from the MIDDLE of the year (February), it's "
    "removed from the very END instead (December 31st) - which doesn't disturb anything "
    "before it. This is exactly the trick the 2028 build was already using, for a different "
    "reason, and it never had this problem in the first place. Both 2027 and 2029 were "
    "rebuilt and re-run with this correction."
)
pdf.table(
    ["", "2027: before", "2027: after", "2029: before", "2029: after"],
    [
        ["How closely they move together", "0.647", "0.675", "0.349", "0.446"],
        ["Average error", "28.19", "26.91", "29.59", "29.14"],
    ],
    [70, 40, 40, 40],
)
pdf.result(
    "A genuinely clean win this time - both numbers improve together, with no catch.",
    "Unlike the import-amount question, this wasn't a trade-off - both years got a real, "
    "honest improvement in matching quality AND average error at the same time, with almost "
    "no change in how often the model ran out of power. That combination is exactly what you'd "
    "expect from fixing an actual mistake, rather than just shuffling numbers around.",
    color=GOOD,
)
pdf.question("...and check the ceiling behavior too.")
pdf.body(
    "One more thing worth checking: now that the calendar mistake is fixed, does the strange "
    "'smaller import amount works better' pattern from earlier this week still show up, or "
    "was that pattern itself somehow caused by the calendar bug?"
)
pdf.result(
    "Checked directly: the two issues are completely separate. Fixing one didn't explain the other.",
    "Re-running the same import-amount comparison on the newly-fixed 2029 model found the "
    "exact same pattern as before - smaller import amounts still give noticeably better "
    "hour-to-hour matching, at the same cost of far more 'ran out of power' hours. Fixing the "
    "calendar bug gave every import-amount setting a small, genuine boost across the board, "
    "but it didn't change the underlying shape of that pattern at all. So these are now "
    "confirmed to be two real, independent things going on - not one mistake masquerading as "
    "two.",
    color=NAVY,
)

# =====================================================================
pdf.h1("Where This Leaves Us")
pdf.body("A short, focused day that turned into something bigger - one earlier decision checked more thoroughly and reversed, and then a genuine, previously-undetected bug found and fixed cleanly:")
for line in [
    "- The 'smaller import amount' idea from yesterday looked good on the narrow 'ordinary "
    "hours only' measure, but a fuller check (including the full year and a third option) "
    "showed it makes the OVERALL picture worse, not better - more unrealistic 'ran out of "
    "power' hours, and a badly overshot average price.",
    "- The 2028 and 2029 models are back to their original 30,000 setting, matching every "
    "other year in this project. The smaller-amount exploration is kept as real, useful, "
    "on-file evidence - just not adopted as the answer.",
    "- Checking WHERE 2028 and 2029 specifically disagree with Brainpool (never done before "
    "today) turned up a real, previously undetected calendar bug in how the demand shape is "
    "built - present in the project's main 2027 build the whole time, not just the new "
    "years. It's now fixed for both 2027 and 2029, with a clean improvement in both matching "
    "quality and average error, and no downside.",
    "- Double-checked that this bug wasn't secretly behind the earlier import-amount puzzle - "
    "it isn't. Both are real, separate findings, confirmed independently.",
]:
    pdf.set_x(MARGIN)
    pdf.multi_cell(0, 5.8, line)
pdf.ln(2)
pdf.body(
    "The full technical detail behind today's work has also been folded into the main, more "
    "detailed progress report (AMIRIS_Germany2027_Progress_Report.pdf) as Phases 27 and 28."
)

pdf.output("AMIRIS_Session_2026-08-26.pdf")
print("Saved AMIRIS_Session_2026-08-26.pdf")
