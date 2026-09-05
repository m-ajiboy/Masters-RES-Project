"""Generates AMIRIS_Session_2026-08-28.pdf - a very simple, plain-language walkthrough of
today's specific conversation: what was asked, and what happened, in the order it happened.
Written for someone with no technical background - no jargon left unexplained, short
sentences, everyday analogies. Separate from the cumulative Progress Report, which is more
technical and covers the whole project. Follows on from the 27 August session (which ended
with the supervisor presentation Q&A). Today covered building a full plain-language reference
guide to how AMIRIS works, then a supervisor-suggested side investigation into whether a
price floor could improve the model's match to Brainpool."""
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
        self.cell(0, 8, f"AMIRIS Session Notes - 28 August 2026                                                                                    Page {self.page_no()}", align="C")

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
pdf.cell(0, 6, "28 August 2026", new_x="LMARGIN", new_y="NEXT")
pdf.ln(2)
y = pdf.get_y()
pdf.set_draw_color(*NAVY)
pdf.set_line_width(1)
pdf.line(MARGIN, y, 210 - MARGIN, y)
pdf.ln(5)

pdf.body(
    "Today had two parts. First, a big reference document explaining how our model actually "
    "works, from the ground up, so you can answer almost any question about it without having "
    "to look everything up again. Second, a real, tested side-investigation into a specific "
    "idea from your supervisor: could we just stop our model's price from going as deeply "
    "negative as it does?"
)

# =====================================================================
pdf.h1("1. A Complete Guide to How Our Model Works")
pdf.question(
    "I still need a comprehensive detailed easy to understand breakdown of what the inputs "
    "are, how Amiris processes them to give its output, all the components, agents, their "
    "roles... give different example scenarios where import was used, where import was not "
    "used, where Amiris went negative like in summer, etc. I need a better holistic "
    "understanding to be able to answer almost any question."
)
pdf.result(
    "Built a new, standalone reference document: AMIRIS_Explainer.pdf.",
    "This is different from the Progress Report (which tracks what we DID) and the daily "
    "session notes (which track a single day's conversation) - this one explains how the "
    "model ITSELF works, as a lasting reference. It covers what data goes in, what each of the "
    "roughly 30 'actors' in the model actually represents in real life, how a price gets set "
    "each hour, and then walks through five real hours pulled straight from our actual 2027 "
    "results: an ordinary winter evening peak, a genuine 'ran out of power' hour, an "
    "import-heavy hour, and two negative-price summer hours - one at midday from solar, one "
    "from a very windy September morning. Every single number in those five examples was "
    "pulled directly from our real result files and double-checked to make sure supply exactly "
    "balances demand, hour by hour."
)
pdf.analogy(
    "Think of it as the 'owner's manual' for our model - not what we've done with it (that's "
    "the Progress Report), but how it actually runs under the hood, with real worked examples "
    "instead of abstract descriptions."
)

# =====================================================================
pdf.h1("2. Extending the Guide to Cover 2028 and 2029 Too")
pdf.question("Extend it to cover the 2028/2029 builds too.")
pdf.result(
    "Added three more sections to the same document.",
    "Explained what stays exactly the same across all three years we've built (the rules, the "
    "mechanics, the import limit) versus what genuinely changes year to year (power plant "
    "capacities - fossil fuel plants shrinking, renewables and batteries growing, real Brainpool "
    "figures each time). Added four more real worked examples, two each from 2028 and 2029. "
    "Finished with a side-by-side scorecard comparing all three years - how well each one "
    "matches Brainpool's real forecast, and why the match naturally gets a little weaker the "
    "further a year is from 2027, the one year our model was actually tuned against."
)

# =====================================================================
pdf.h1("3. Checking In: Where Do Things Stand?")
pdf.question("From our investigations on how to further improve the price correlations, where are we?")
pdf.result(
    "Gave a full status update: one real fix banked, one big idea tested and honestly rejected, one idea ruled out entirely.",
    "The calendar bug fix (from a few days ago) is a genuine, clean win, already kept. Making "
    "the import limit smaller looked very promising at first (much better day-to-day matching) "
    "but a fuller look showed it made the OVERALL picture worse (way more hours where the model "
    "runs out of power, which real life almost never does) - so we tested it honestly, saw the "
    "full trade-off, and correctly did NOT adopt it. Changing which year's demand pattern we "
    "borrow from turned out to make basically no difference either way. The one big idea left "
    "untested: properly letting the model sell extra power abroad, not just buy it - a bigger "
    "undertaking, saved for later."
)

# =====================================================================
pdf.h1("4. A Smaller Idea First: Capping How Negative Price Can Go")
pdf.question(
    "For the mid-day gap price whereby Amiris is reporting hard negative, before building the "
    "export module, my supervisor wants me to tweak Amiris in such a way that we can set a "
    "limit for how negative it can go... is it possible? If yes, let us try a build separately "
    "for that purpose."
)
pdf.result(
    "Yes, technically possible to investigate - but the honest answer turned out to be no, it doesn't help.",
    "First had to check whether this was even something we could adjust. Opened up the actual "
    "AMIRIS computer program itself (not just our settings file) and found it already has a "
    "hard limit built in: -500 EUR/MWh, matching the real rule used by Europe's actual "
    "electricity exchanges. That number is baked into the program's core, not something we can "
    "change from our own settings - changing it for real would mean editing and rebuilding "
    "AMIRIS itself, a much bigger step. So a smaller, faster test was run first: taking our "
    "model's ALREADY-COMPUTED results and simply adjusting the reported price after the fact, "
    "purely to see if a different limit was even worth the bigger effort."
)
pdf.analogy(
    "It's like checking whether repainting a car would fix a rattling engine, before you take "
    "the whole engine apart - a cheap first check before committing to the expensive one."
)

# =====================================================================
pdf.h1("5. Testing It Properly, Including Your Supervisor's Own Suggestion")
pdf.body(
    "Built and ran the actual test, sweeping every reasonable cap value from -500 all the way "
    "up to +100 EUR/MWh, and made a chart showing the results for all three years side by side."
)
pdf.question("What if we use a positive number, say like 10 EUR/MWh, can there be improvement in the correlation?")
pdf.result(
    "No - tested it directly, and a positive cap makes things clearly worse, not better.",
    "At +10 EUR/MWh specifically, match quality dropped meaningfully in every single year - not "
    "just a tiny wobble. And it got steadily worse the higher the cap went: by +100 EUR/MWh, "
    "match quality had collapsed to a fraction of where it started. The reason: a positive cap "
    "doesn't just touch the negative hours, it also flattens thousands of ordinary hours that "
    "happen to sit between 0 and the cap, destroying real detail the model had actually been "
    "getting right."
)
pdf.result(
    "Overall verdict: a confirmed dead end, at every value tested, in every direction.",
    "The best possible match quality for every single year, at every cap tried, never beat "
    "what our model already produces with no cap at all. This closes out the price-cap idea "
    "honestly - it was worth checking properly (especially since your supervisor asked "
    "specifically), but it simply isn't the answer."
)

# =====================================================================
pdf.h1("6. Getting Ready for the Supervisor Meeting")
pdf.question("Yes, fold it in. / Prepare the update for my supervisor's meeting with this.")
pdf.result(
    "Added the full price-cap investigation to both the technical Progress Report and the supervisor slide deck.",
    "The Progress Report gained a full new section with the real numbers, the chart, and the "
    "honest conclusion. The supervisor deck gained four new slides in plain, presentation-ready "
    "language: why we tested this, what we found inside AMIRIS itself, the actual chart, and a "
    "results table ending in a clear 'confirmed dead end' - including the +10 result you "
    "specifically asked about."
)

# =====================================================================
pdf.h1("7. What Else Is Worth Trying?")
pdf.question("Is there anything else worth trying before the export build on how we can improve the correlation?")
pdf.result(
    "Suggested three ideas, ranked by promise, and recommended starting with the top one.",
    "Top pick: give power plants a real cost for shutting down and restarting - right now they "
    "have zero reason to avoid it, which is unrealistic. Second: make heat pumps 'smart' the "
    "same proven way we already did for hydrogen production and EV charging. Third: re-check "
    "how far below their true cost coal and lignite plants are allowed to bid, a setting that's "
    "never been revisited since the very start of the project. Also flagged an important "
    "lesson from today: a real-sounding mechanism can still turn out to be disconnected from "
    "the actual price once you check the fine print - worth verifying that BEFORE spending time "
    "researching real-world numbers for it."
)
pdf.body(
    "You agreed to test the top idea - the start-up cost - which carried into tomorrow's "
    "session (see AMIRIS_Session_2026-09-01.pdf)."
)

pdf.output(r"C:\Users\MuideenOA\Desktop\PyTut\Amiris\AMIRIS_Session_2026-08-28.pdf")
print("Saved AMIRIS_Session_2026-08-28.pdf")
