"""Generates AMIRIS_Germany2027_AllPhases_SlideExplainer.pdf - a short, plain-language
companion document that walks through AMIRIS_Germany2027_Comprehensive_AllPhases.pptx
one slide at a time, explaining in simple terms what each slide shows and why it
matters. Meant to be read alongside the deck (e.g. before presenting it, or by someone
who wasn't in the room), not as a replacement for it.
"""
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
        self.cell(0, 8, f"AMIRIS Germany2027 - All-Phases Slide Explainer                                                                    Page {self.page_no()}", align="C")

    def h1(self, text):
        if self.get_y() > 258:
            self.add_page()
        self.ln(4)
        self.set_font("Helvetica", "B", 15)
        self.set_text_color(*NAVY)
        self.set_x(MARGIN)
        self.multi_cell(0, 7.5, text)
        y = self.get_y()
        self.set_draw_color(*NAVY)
        self.set_line_width(0.7)
        self.line(MARGIN, y, 210 - MARGIN, y)
        self.ln(3)

    def slide_heading(self, number, title):
        if self.get_y() > 262:
            self.add_page()
        self.ln(2)
        self.set_font("Helvetica", "B", 11)
        self.set_text_color(*AMBER)
        self.set_x(MARGIN)
        self.multi_cell(0, 5.6, f"Slide {number}: {title}")
        self.ln(0.5)

    def body(self, text):
        self.set_font("Helvetica", "", 9.8)
        self.set_text_color(20, 24, 22)
        self.set_x(MARGIN)
        self.multi_cell(0, 5.1, text)
        self.ln(2.5)

    def callout(self, text, color=GOOD):
        if self.get_y() > 260:
            self.add_page()
        self.set_font("Helvetica", "I", 9.8)
        self.set_text_color(*color)
        self.set_x(MARGIN)
        self.multi_cell(0, 5.0, text)
        self.ln(2.5)


pdf = Doc()
pdf.set_margins(MARGIN, 14, MARGIN)
pdf.set_auto_page_break(auto=True, margin=16)
pdf.add_page()

# ---- Title ----
pdf.set_font("Helvetica", "B", 18)
pdf.set_text_color(*NAVY)
pdf.set_x(MARGIN)
pdf.multi_cell(0, 9, "AMIRIS Germany2027 - All-Phases Slide Explainer")
pdf.set_font("Helvetica", "I", 10)
pdf.set_text_color(*GREY)
pdf.set_x(MARGIN)
pdf.multi_cell(0, 5.4, "A plain-language, slide-by-slide guide to AMIRIS_Germany2027_Comprehensive_AllPhases.pptx (42 slides)")
pdf.set_font("Helvetica", "", 9)
pdf.set_x(MARGIN)
pdf.cell(0, 6, "Muideen Oladayo Ajiboye", new_x="LMARGIN", new_y="NEXT")
pdf.ln(2)
y = pdf.get_y()
pdf.set_draw_color(*NAVY)
pdf.set_line_width(1)
pdf.line(MARGIN, y, 210 - MARGIN, y)
pdf.ln(4)
pdf.body(
    "This document goes through the comprehensive presentation one slide at a time, in plain "
    "English, so it can be read on its own or used as a quick refresher before presenting the "
    "deck. It does not repeat every number on every slide - just what the slide is showing and "
    "why it matters. For the full figures, see the slide itself or the underlying Progress Report."
)

# =====================================================================
pdf.h1("Opening (Slides 1-3)")
pdf.slide_heading(1, "Title slide")
pdf.body("Introduces the project: comparing AMIRIS (a free, open, research-grade electricity market simulator) against Energy Brainpool (a paid, professional forecaster) for Germany's electricity price in 2027.")
pdf.slide_heading(2, "How This Review Is Organized")
pdf.body("A table of contents. The 52 phases of work are grouped into 8 parts, in roughly the order they happened, ending with a conclusion about which result to adopt.")
pdf.slide_heading(3, "What This Project Is Testing")
pdf.body("Explains the two tools being compared and the ground rule followed throughout: never change a setting just to make the numbers look better - every change needs a real-world reason first. Also explains that failed experiments are reported honestly, not hidden, because knowing what does NOT work is still useful.")

# =====================================================================
pdf.h1("Part 1: Building the Model and Fixing the Big First Gap (Slides 4-10)")
pdf.slide_heading(4, "Part 1 divider")
pdf.body("A section break. Part 1 covers Phases 1-8: getting a first working version of the model running, then fixing its biggest early problem.")
pdf.slide_heading(5, "Phase 1-3: The First Build")
pdf.body("The very first version of the model was built using Brainpool's own real 2027 data. It ran, but 15.9% of the year showed a price of exactly 3,000 EUR/MWh - AMIRIS's built-in signal that supply couldn't meet demand that hour. That's a lot of hours to be \"broken\" - a clear sign something needed fixing, but a necessary starting point.")
pdf.slide_heading(6, "Phase 4: A Smarter Demand Model (V1 vs V2)")
pdf.body("The first version (V1) used one generic household electricity-use pattern for the entire country's demand, which isn't realistic. V2 replaced this with separate, purpose-built patterns for each real type of demand (households, heat pumps, EVs, industry). V2 immediately looked more realistic and had fewer shortage hours.")
pdf.slide_heading(7, "Phase 5-7: Adding Cross-Border Import - and a Real Problem")
pdf.body("An \"import\" agent was added so Germany could buy power from neighbouring countries when short. It helped, but most of the electricity it offered never actually got used. Investigating why revealed that 64% of the shortage hours had literally zero import available at that exact hour - the import schedule was copied from an unrelated year and didn't line up with when this model actually needed it.")
pdf.slide_heading(8, "Phase 8: Fixing and Calibrating the Import Model")
pdf.body("Fixed by making import availability a simple, constant hourly allowance instead of a shaped schedule copied from elsewhere. Then tested several different sizes of that allowance (\"ceiling\") to see which one made the price match Brainpool's real numbers best.")
pdf.slide_heading(9, "Phase 8 (continued): One Size Does Not Fit Both Demand Models")
pdf.body("A subtlety worth knowing: the best import ceiling turned out to be different for V1 and V2. V1's demand shape is more extreme, so it needs a bigger import allowance to stay realistic. This shows the \"right\" setting can depend on other choices made elsewhere in the model.")
pdf.slide_heading(10, "Part 1 Result: From Wildly Divergent to Close to Brainpool")
pdf.body("A before/after summary chart. Shortage hours fell from over 7% of the year to almost none, and the average price came down from nearly 5x too high to within a few EUR/MWh of Brainpool's real number. This was the project's first big win.")

# =====================================================================
pdf.h1("Part 2: Matching Brainpool's Weather and Calendar Assumptions (Slides 11-14)")
pdf.slide_heading(11, "Part 2 divider")
pdf.body("Covers Phases 9-17: making sure the model's underlying assumptions about weather and calendar dates line up with Brainpool's own.")
pdf.slide_heading(12, "Phase 9-11: Real 2009 Weather, and a Calendar Bug")
pdf.body("Brainpool's own model is based on real weather from the year 2009, so this was tested in AMIRIS too. Along the way, a bigger issue was found: the demand data (originally from 2023) didn't line up its days of the week correctly with 2027's calendar, making weekdays and weekends look wrong. Fixing that calendar mismatch genuinely improved how well the two models' patterns matched.")
pdf.slide_heading(13, "Phase 12 & 15: A Null Result, and a Small Real Improvement")
pdf.body("Testing real 2009 temperature data for heat-pump demand made no real difference (heat pumps are a small share of total demand, so this isn't surprising - but it's still useful to confirm). Separately, pricing imported electricity using a blend of 11 real neighbouring countries' prices (instead of just France) gave a small, genuine improvement.")
pdf.slide_heading(14, "Phase 17: Rebuilding Demand on a Closer Weather-Matched Year")
pdf.body("Checked which real historical year's weather most closely resembles 2009 (Brainpool's basis) and found 2016 was the best match of the years with usable data. Rebuilding demand on 2016 gave a real, if modest, improvement and became the new foundation going forward.")

# =====================================================================
pdf.h1("Part 3: Making Demand Smarter - Flexible Storage and Consumers (Slides 15-19)")
pdf.slide_heading(15, "Part 3 divider")
pdf.body("Covers Phases 18-23: researching the model's shortage-price rules, then making some demand types react to price instead of consuming on a fixed schedule.")
pdf.slide_heading(16, "Phase 18-19: Where Does 3,000 EUR/MWh Come From?")
pdf.body("Before changing this number, its origin was researched: it turns out 3,000 EUR/MWh was the REAL European regulatory price cap in effect during AMIRIS's own reference year, so it isn't arbitrary. A newer, higher real cap (5,000 EUR/MWh) was tested directly, and the result was a genuine trade-off (better in one way, worse in another) rather than a clear improvement, so it wasn't adopted.")
pdf.slide_heading(17, "Phase 20-21: Price-Responsive Storage and Consumers")
pdf.body("Two demand types - electrolysis (hydrogen production) and EV charging - were rebuilt so they actually shift their electricity use toward cheap hours and away from expensive ones, instead of using power on a fixed schedule regardless of price. Both changes reduced shortage hours.")
pdf.slide_heading(18, "Phase 21: The Strongest Small Result of This Whole Line of Work")
pdf.body("With smart EV charging added on top of smart electrolysis, shortage hours reached ZERO for the first time in the whole project. This was a clean, verified result - EV charging noticeably shifted from an evening peak to a midday peak, exactly the pattern you'd expect from genuinely price-responsive charging.")
pdf.slide_heading(19, "Phase 22-23: A Real Headroom Test, and a Structural Clue")
pdf.body("Found that Reservoir Hydro storage was hitting its maximum power output 35% of the year. Testing a bigger (hypothetical) power rating helped a little but wasn't adopted, since the real, documented figure is more defensible to keep using. Re-checking where the remaining price gap comes from pointed clearly at one thing: Germany needs the ability to EXPORT power abroad, not just import it - setting up the next major phase of work.")

# =====================================================================
pdf.h1("Part 4: Testing on New Years, and Closing Dead Ends (Slides 20-23)")
pdf.slide_heading(20, "Part 4 divider")
pdf.body("Covers Phases 24-31: checking whether the model still works on years it wasn't tuned for, fixing a real bug, and testing (and rejecting) three more ideas.")
pdf.slide_heading(21, "Phase 24: Out-of-Sample Validation on 2028 and 2029")
pdf.body("The exact same model, with no new tuning, was rebuilt for 2028 and 2029 using Brainpool's data for those years. The average price level still matched reasonably well, but the hour-to-hour pattern-matching got weaker the further the year was from 2027 - an honest, useful finding about the limits of this kind of one-year calibration.")
pdf.slide_heading(22, "Phase 28: A Real Bug Found and Fixed")
pdf.body("A genuine software bug was found: a step that removes 29 February (to fit a leap year's data into a normal year) was silently misaligning every single day from March onward - affecting 84% of the year. Fixing it (by removing 31 December instead) made both 2027 and 2029's results clearly better, with no downside.")
pdf.slide_heading(23, "Phase 29-31: Three Real Dead Ends, Reported Honestly")
pdf.body("Three more plausible ideas were tested and did not work: lowering the negative-price floor, adding a real cost for starting up power plants (turned out not to be connected to anything in this part of AMIRIS), and letting coal plants bid further from their true cost. All three are reported as genuine dead ends rather than left untested or hidden.")

# =====================================================================
pdf.h1("Part 5: The Big Lever - Connecting Germany to the Rest of Europe (Slides 24-28)")
pdf.slide_heading(24, "Part 5 divider")
pdf.body("Covers Phases 32-38: the single biggest structural change in the whole project - properly modelling Germany's electricity trade with its neighbours, not just a simple import allowance.")
pdf.slide_heading(25, "Phase 32-33: Scoping and Sourcing Real Cross-Border Data")
pdf.body("AMIRIS already has a genuine, working feature for connecting multiple market zones together - this was found and studied first. Real demand and generation data for the rest of Europe was then sourced (working around a temporary outage of the usual European data source).")
pdf.slide_heading(26, "Phase 34 & 36: First Coupling, Then Real Transmission Data")
pdf.body("Germany was first connected to a single combined \"Rest of Europe\" zone using a placeholder guess for how much electricity could flow between them. That guess was then replaced with a real number, calculated from actual observed cross-border electricity flows in 2023.")
pdf.slide_heading(27, "Phase 37: The Best Result of the Entire Project")
pdf.body("Rest-of-Europe was given its own realistic storage (batteries, pumped hydro, reservoir hydro) and renewable-energy subsidy rules, matching how Germany's own side of the model is already built. This is the headline result: average price of 67.45 EUR/MWh against Brainpool's real 68.04 EUR/MWh - a very close match - and it remains this project's best, most defensible result.")
pdf.slide_heading(28, "Phase 38: Extending Phase 37 to 2028 and 2029, Unchanged")
pdf.body("The same Phase 37 setup, with nothing re-tuned, was run for 2028 and 2029 too. Price level and pattern-matching both held up well in both new years, showing this is a durable result and not a lucky fit to one specific year.")

# =====================================================================
pdf.h1("Part 6: Stress-Testing the Result From Every Angle (Slides 29-32)")
pdf.slide_heading(29, "Part 6 divider")
pdf.body("Covers Phases 39-48: once Phase 37 looked like the best result, it was deliberately challenged from many different directions to see if anything could beat it.")
pdf.slide_heading(30, "Phase 39-41: Chasing the Out-of-Sample Shortage-Hour Growth")
pdf.body("2028 and 2029 showed more shortage hours than 2027. Three real, sensible explanations were tested directly - none of them turned out to be the cause. This ruling-out process, while it didn't fix anything, was valuable: it narrowed down where the real explanation must be.")
pdf.slide_heading(31, "Phase 42-43: Does Splitting Rest-of-Europe Into Real Countries Help?")
pdf.body("Instead of one combined \"Rest of Europe\" zone, the model was rebuilt with France as its own separate country - and the result got clearly WORSE. Expanding this to all 10 real neighbouring countries improved on the France-only attempt, but still didn't beat the simpler combined-zone version from Phase 37.")
pdf.slide_heading(32, "Phase 44-48: Five More Real Robustness Checks")
pdf.body("A summary table of five further checks: rebuilding on a different data year, confirming there's no hidden software bug behind the shortage-hour growth, testing a real European growth forecast, trying an alternative way of displaying shortage-hour prices, and testing a more realistic web of direct connections between countries. None of them beat Phase 37 outright - each either matched it closely or came with its own trade-off.")

# =====================================================================
pdf.h1("Part 7: Final Robustness Checks - Alternative Weather/Demand Years (Slides 33-34)")
pdf.slide_heading(33, "Part 7 divider")
pdf.body("Covers Phases 49-51: one last round of checking whether a different choice of weather or demand year could have given a better result than the one actually used.")
pdf.slide_heading(34, "Phases 49-51: Three More Real Years Tested, None Better")
pdf.body("Three separate real alternative years were tried - one for overall demand shape, one for wind (offshore), and one for river-based hydropower. In every single case, the result got slightly worse, not better. Three-for-three is about as strong a confirmation as this kind of test can give: the choices already made in Phase 37 were not just lucky.")

# =====================================================================
pdf.h1("Part 8: One Investigative Side-Experiment - Patching AMIRIS's Own Code (Slides 35-37)")
pdf.slide_heading(35, "Part 8 divider")
pdf.body("Covers Phase 52: a separate, investigative experiment that actually opens and modifies AMIRIS's own underlying computer code, done purely to explore an idea and report the finding - not to change the thesis's official result.")
pdf.slide_heading(36, "Phase 52: Why Patch the Code At All?")
pdf.body("Earlier work found that Rest-of-Europe's storage never \"sees\" Germany's price when deciding whether to send power over - it only looks at its own local market. Two attempts to fix this by wiring up existing AMIRIS features didn't work (one made the simulation freeze, one hit an unresolved technical issue). A third attempt - directly editing the relevant piece of code - did work.")
pdf.slide_heading(37, "Phase 52: Every Variant Tested Trades One Metric for Another")
pdf.body("Several versions of the code fix were tried. The best version cut shortage hours from 7 to 6 and made the average price error much smaller, but slightly worsened how well the hour-to-hour pattern matched Brainpool's. The reason: Rest-of-Europe's storage only has a limited amount of energy it can release in one day, so helping more in the morning leaves less available for the evening. This is reported as an interesting technical finding for the department, kept completely separate from the thesis's actual result.")

# =====================================================================
pdf.h1("Conclusion (Slides 38-42)")
pdf.slide_heading(38, "Conclusion divider")
pdf.body("The final section: bringing everything together and making the case for which result to treat as final.")
pdf.slide_heading(39, "The Whole Journey in One Chart")
pdf.body("A single chart showing the average price at each major stage of the project, next to Brainpool's real average price as a reference line. It visually tells the whole story: starting far too high, then steadily converging until Phase 37 lands almost exactly on Brainpool's number.")
pdf.slide_heading(40, "The Case for Adopting Phase 37 as the Final Result")
pdf.body("Summarises why Phase 37 is very likely the best achievable result: every real lever AMIRIS offers has now been tested (52 phases' worth), the remaining small gap has two well-understood real causes (a physical transmission limit, and a genuine limit in how each country's forecaster works), and even the one experiment that DID help (Phase 52) only trades one problem for another rather than removing it.")
pdf.slide_heading(41, "Recommendation")
pdf.callout(
    "Adopt Phase 37 as the project's standing, final result. Further tuning is very unlikely to "
    "improve on it by any meaningful amount, and the remaining gap should be reported as a "
    "well-understood, structural limitation - not an unresolved problem.",
    color=GOOD,
)
pdf.body("Also notes two related, still-open decisions kept deliberately separate from this recommendation: whether to adopt Phase 47's alternative way of displaying shortage-hour prices (a simplification, not a fix), and that Phase 52's code patch remains an investigative side-note for the department, not part of the thesis's own methodology.")
pdf.slide_heading(42, "Thank you")
pdf.body("Closing slide for questions and discussion.")

pdf.output("AMIRIS_Germany2027_AllPhases_SlideExplainer.pdf")
print("Saved AMIRIS_Germany2027_AllPhases_SlideExplainer.pdf")
