"""Generates AMIRIS_Session_2026-08-24.pdf - a very simple, plain-language walkthrough of
today's specific conversation: what was asked, and what happened, in the order it happened.
Written for someone with no technical background - no jargon left unexplained, short
sentences, everyday analogies. Separate from the cumulative Progress Report, which is more
technical and covers the whole project."""
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
        self.cell(0, 8, f"AMIRIS Session Notes - 24 August 2026                                                                                    Page {self.page_no()}", align="C")

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
pdf.cell(0, 6, "24 August 2026", new_x="LMARGIN", new_y="NEXT")
pdf.ln(2)
y = pdf.get_y()
pdf.set_draw_color(*NAVY)
pdf.set_line_width(1)
pdf.line(MARGIN, y, 210 - MARGIN, y)
pdf.ln(5)

pdf.body(
    "Quick reminder of where things stood coming into today: we have a computer model of "
    "Germany's 2027 electricity market (called AMIRIS), and we're comparing its predicted "
    "prices against a real forecast from a professional energy forecasting company "
    "(Brainpool). The two mostly agree on the overall price level, but don't move up and "
    "down together very closely hour-to-hour - and we've been hunting for fixable reasons "
    "why, one at a time. Today covered three of those hunts."
)

# =====================================================================
pdf.h1("1. Does the year of weather used for heat pumps matter?")
pdf.question("I suggest we try to see the effect of the temperature for the heat pump demand load and see how it affects the result.")
pdf.body(
    "Heat pumps (the electric heating/cooling systems that are part of Germany's future "
    "electricity demand) use more or less power depending on how cold or warm it is outside. "
    "Up to today, our model used a smoothed-out, 'typical' weather pattern for this - not any "
    "specific real year, more like an 'average year' blended together."
)
pdf.body(
    "So the question was: what if we used the temperature that actually happened in a real "
    "year (2009) instead of that blended average? Would that make our model agree better "
    "with Brainpool's forecast?"
)
pdf.body(
    "What was done: found and downloaded real hour-by-hour temperature records from "
    "Germany's official weather service, for four different spots around the country in "
    "2009, averaged them together, and used that instead of the old blended data."
)
pdf.result(
    "What happened: barely any difference.",
    "The real 2009 temperatures were genuinely different (colder cold-snaps, hotter hot "
    "days than the smoothed version) - so the change was real, not a mistake. But it barely "
    "moved the overall comparison with Brainpool at all.",
    color=GREY,
)
pdf.analogy(
    "heat pumps only make up a small slice of Germany's total electricity use (under 3 out "
    "of every 100 units used). Even if you get that one small slice exactly right, it's not "
    "big enough on its own to change the overall picture much - like repainting one small "
    "room perfectly won't change how a whole house looks from the outside."
)

# =====================================================================
pdf.h1("2. Why does AMIRIS predict such low prices around midday?")
pdf.question("Go after the midday solar-bias pattern next.")
pdf.body(
    "Earlier we'd found that AMIRIS predicts noticeably lower prices than Brainpool "
    "specifically around midday - exactly when solar panels are producing the most power. "
    "Rather than guess why, one real midday hour was picked (a sunny day in July) and every "
    "single part of the model was checked at that exact hour: how much power was being made, "
    "by what, and what happened to all of it."
)
pdf.result(
    "Finding 1: two types of solar/wind subsidy behave very differently when there's too much power.",
    "Germany supports renewable energy two different ways. Type A gets a top-up payment on "
    "top of whatever the market price is - so if the market price crashes, Type A plants "
    "would rather switch off than sell at a loss. Type B gets a fixed guaranteed price no "
    "matter what - so Type B plants have no reason to ever switch off. At the hour we "
    "checked, Type A wind power was switched off completely, and Type A solar was cut by a "
    "quarter, while Type B solar kept running at full blast regardless.",
    color=BAD,
)
pdf.result(
    "Finding 2 (the bigger one): our model has no way to sell extra power to other countries.",
    "In real life, when Germany makes more solar and wind power than it needs, a lot of that "
    "extra power gets sold to neighbouring countries. Our model can bring power IN from "
    "neighbours (we built that already) - but it was never given a way to sell power OUT. So "
    "when there's a big midday surplus, the only options are: switch plants off, fill up "
    "batteries, or let the price crash. There's no fourth option (sell it abroad) the way "
    "there would be in real life - and that's very likely why our midday prices go so much "
    "lower than Brainpool's.",
    color=BAD,
)
pdf.analogy(
    "imagine a bakery that makes more bread than the local town can buy some mornings. In "
    "real life, it would just sell the extra loaves to the next town over. Our model's bakery "
    "doesn't have that option - so on a big-batch morning, it either has to throw bread away, "
    "freeze it, or slash the price to nothing to get rid of it locally. That's what's "
    "happening to Germany's midday power surplus in the model."
)

# =====================================================================
pdf.h1("3. Trying to build that missing 'sell abroad' option")
pdf.question("Yes, build it but just like others, keep the build separate for easy tracking of all our models.")
pdf.body(
    "Given the finding above, the obvious next step was: try to add a way for the model to "
    "sell surplus power abroad, and see if that fixes the midday price problem. This was "
    "built as its own separate, clearly labelled test - not mixed in with anything else, so "
    "it's easy to find and compare later."
)
pdf.body(
    "The building block used was the closest thing available: a tool normally used for "
    "batteries and similar flexible equipment, set up to only ever take power IN and never "
    "give it back - representing power leaving the country for good, the way a real export "
    "would."
)
pdf.result(
    "Result: it never did anything, all year long - a real and useful dead end.",
    "This 'export' piece never activated even once, in any of the 8,760 hours of the year - "
    "including the exact midday hour it was built to help with.",
    color=BAD,
)
pdf.analogy(
    "the tool this was built from is designed like a battery: it only bothers charging up if "
    "it can eventually sell that energy back later for a profit. What we tried to build was "
    "the opposite of a battery - something that takes power in and never gives anything back "
    "at all, ever. A tool that only acts when there's an eventual payoff has zero reason to "
    "ever switch on something with no payoff - so it just sat there, unused, the whole year. "
    "This isn't a mistake we made; it's a real limit of the tool we have available. Properly "
    "adding a genuine 'sell to another country' feature would mean building a much bigger "
    "second piece - basically a mini second country-model connected to the first - which is "
    "a much bigger job than what we tried today."
)

# =====================================================================
pdf.h1("4. Checking what Brainpool actually assumes, instead of guessing")
pdf.question("Verify what weather year and import country Brainpool actually uses, can you do that?")
pdf.body(
    "Up to this point, two of our biggest assumptions - that Brainpool bases its wind/solar "
    "numbers on real 2009 weather, and that France is a reasonable stand-in for 'the "
    "neighbouring country' - had never actually been confirmed. They were educated guesses. "
    "So rather than keep building on top of guesses, this was checked directly against "
    "Brainpool's own public information about how their forecasting tool works."
)
pdf.result(
    "Found: the 2009 weather guess was correct.",
    "A direct quote from the company that now owns Brainpool's forecasting tool: 'The "
    "weather year 2009 is used for the modelling.' Confirmed, not assumed.",
    color=GOOD,
)
pdf.result(
    "Found: the 'one neighbouring country' assumption was a bigger simplification than realised.",
    "Brainpool's real model doesn't compare Germany against just one neighbour - it models "
    "roughly 30 European countries together (all of the EU, plus the UK, Norway, and "
    "Switzerland), letting power flow between all of them based on price, the way it "
    "actually works in real life. Our model, by comparison, was only ever comparing Germany "
    "against France alone.",
    color=AMBER,
)

# =====================================================================
pdf.h1("5. Building a fairer stand-in for 'the neighbouring price'")
pdf.question("Yes, build that blended-country import price version.")
pdf.body(
    "Since a full 30-country model is far too big a job to replicate, the next best thing "
    "was built: instead of using France's price alone as our stand-in for 'what the "
    "neighbours would pay,' real prices from all 11 of Germany's actual real neighbouring "
    "countries were pulled and averaged together into one blended price."
)
pdf.result(
    "What happened: a small, genuine improvement.",
    "Not dramatic, but real and in the right direction on more than one measure at once. "
    "The reason it wasn't a bigger jump: it turns out France's price on its own wasn't "
    "wildly different from the blend of all 11 countries to begin with, so there wasn't a "
    "huge amount of 'wrongness' to fix here in the first place.",
    color=GOOD,
)

# =====================================================================
pdf.h1("6. How hard would it be to build a real 'sell abroad' feature?")
pdf.question("What lever do you think we can chase more and how complex is it if we want to set up export in AMIRIS just to see if the gap will close or is it impossible?")
pdf.body(
    "Given the finding above (section 2-3) that our model has no way to export power, the "
    "natural question was: could we actually build that properly, and is it even possible "
    "at all?"
)
pdf.result(
    "Answer: not impossible - but a genuinely big job, one of the biggest still on the table.",
    "AMIRIS does have the real tools needed for two markets to trade properly in both "
    "directions - and there's already a working example built by AMIRIS's own creators "
    "showing exactly how two markets can be connected together. So this is achievable in "
    "principle. But making real use of it would mean building an entire second, simplified "
    "country-model to represent 'Germany's neighbours' and connecting it properly to our "
    "German model - genuinely comparable in size to how much work went into building the "
    "German side in the first place, just simplified. Not a quick add-on.",
    color=AMBER,
)
pdf.body(
    "Given the size of that job, a cheaper check was suggested first before committing to it."
)

# =====================================================================
pdf.h1("7. Checking if public holidays explain part of the remaining gap")
pdf.question("Yes, check the public-holiday angle first.")
pdf.body(
    "One smaller, cheaper idea worth ruling out first: our earlier weekday/weekend fix knows "
    "the difference between a Tuesday and a Saturday, but has no idea that a particular "
    "Thursday might be a public holiday (like Ascension Day) where people actually use much "
    "less electricity than a normal working day. Could that be explaining some of what's "
    "still left unexplained?"
)
pdf.body(
    "Germany's real 2027 public holidays were looked up, and checked directly against how "
    "well our model agreed with Brainpool on exactly those days."
)
pdf.result(
    "First look was promising - but didn't hold up under closer checking.",
    "At first glance, holidays looked much better-behaved than ordinary weekdays. But two "
    "follow-up checks (making sure it wasn't just a coincidence of which months the "
    "holidays happened to fall in, and checking whether the difference was actually bigger "
    "than the normal day-to-day ups and downs prices already have) both suggested this was "
    "likely just ordinary randomness, not a real, repeatable pattern. With only 5 holidays "
    "to look at, there simply isn't enough evidence to say public holidays are a genuine "
    "cause of the remaining gap.",
    color=GREY,
)
pdf.analogy(
    "imagine flipping a coin 5 times and getting heads 4 times - it might look like the "
    "coin is biased, but with so few flips, that's well within what pure chance would "
    "produce anyway. That's roughly the situation here: 5 holidays isn't enough tries to "
    "tell a real effect apart from ordinary luck."
)

# =====================================================================
pdf.h1("8. Is there a better source year for the demand shape than 2023?")
pdf.question(
    "Perhaps if we had the demand profile of 2009, maybe it might help us better... is there "
    "any record of a particular year that was close to 2009... or perhaps we should use the "
    "2019 demand profile, maybe it might yield better result."
)
pdf.body(
    "Almost all of our demand curve (over 9 out of every 10 units of electricity used) has "
    "always been shaped using real 2023 electricity-usage data, stretched or squeezed to fit "
    "2027's total. But Brainpool's wind and solar numbers are based on the real weather that "
    "happened in 2009, not 2023 - so there's a mismatch: our demand and Brainpool's renewables "
    "are effectively pretending to be different years."
)
pdf.body(
    "We can't get real 2009 electricity-usage data (it isn't published in the detail we need). "
    "But the next best thing is: find a year we DO have real usage data for, whose WEATHER "
    "most resembled 2009's. A year with 2009-like weather should produce a demand shape "
    "reasonably similar to what 2009 itself would have looked like."
)
pdf.body(
    "Rather than guess (the user's own suggestion was 2019), real hour-by-hour temperature "
    "was pulled for every year we have usable demand data for - 2015 through 2019, plus 2023 "
    "- and each one was directly compared against real 2009 temperature."
)
pdf.result(
    "Finding: 2023 (used until now) was the WORST match. 2019 (the guess) was second-worst. 2016 was the best.",
    "Checking it properly turned up a surprise: 2023, the year we'd been using all along, "
    "turned out to be the single worst weather match to 2009 of all six years checked. 2019, "
    "the year suggested as a possible improvement, was actually the second-worst. The real "
    "best match was 2016 - a year that hadn't been suggested by either of us, and would never "
    "have been found without actually checking rather than guessing.",
    color=AMBER,
)
pdf.body(
    "The demand shape was rebuilt using real 2016 electricity-usage data instead of 2023, "
    "kept as its own separate, clearly labelled build as always. A small bonus turned up along "
    "the way: 1 January 2016 and 1 January 2027 both happen to fall on a Friday, so - unlike "
    "the 2023 version, which needed a manual adjustment to line weekdays up correctly - this "
    "one lined up naturally with no extra work needed."
)
pdf.result(
    "Result: a real improvement, but a smaller one than it first appears.",
    "The number of hours where the model completely ran out of power fell from 13 to 4 across "
    "the year (better), and the headline 'how well do the two track together' number jumped "
    "noticeably. But most of that jump turned out to be a side-effect of simply having fewer "
    "of those extreme 'ran out of power' hours to distort the picture, rather than the model "
    "genuinely tracking Brainpool better hour-to-hour on ordinary days. On the fairer, "
    "ordinary-hours-only comparison we've relied on all along, the fit barely moved either way. "
    "Still worth keeping - fewer real shortage events is genuine progress on its own - just not "
    "the breakthrough the headline number alone might suggest.",
    color=GOOD,
)
pdf.analogy(
    "picture a company's average commute time. If four employees who each drove 3 hours "
    "one way move closer to the office, the COMPANY average commute time drops a lot - but "
    "that doesn't mean everyone else's ordinary 20-minute commute got any faster. Something "
    "similar happened here: removing a handful of extreme 'ran out of power' hours made the "
    "overall picture look a lot better, without most ordinary hours actually changing much."
)

# =====================================================================
pdf.h1("9. Why does the model charge 3,000 EUR/MWh when it runs out of power?")
pdf.question("Why is Amiris using 3000 Euro for shortage price, why that particular figure?")
pdf.body(
    "Whenever our model can't fully meet demand in a given hour, it charges a ceiling price of "
    "3,000 EUR/MWh for that hour instead - a stand-in for 'the market ran out and someone had "
    "to go without power.' This number has been used in every build so far, carried over from "
    "AMIRIS's own official example scenario without ever checking where it actually came from."
)
pdf.result(
    "Answer: it's not a made-up number. It's the real legal price cap that applied across Europe's electricity markets for several years.",
    "Europe's electricity exchanges (including the German one) all clear their prices "
    "together under one shared set of rules, policed by the EU's energy regulator (ACER). "
    "That regulator set an official, legally binding maximum price of exactly 3,000 EUR/MWh "
    "for the whole system, starting in November 2017. AMIRIS's official example is built "
    "around the year 2019 - which sits right in the middle of the years when 3,000 EUR/MWh "
    "genuinely was the real, legal ceiling everywhere in Europe. So AMIRIS didn't invent this "
    "number - it correctly copied a real regulatory fact for the year it was modelling.",
    color=GOOD,
)
pdf.result(
    "But: the real ceiling has since gone up twice, and our project is modelling a FUTURE year.",
    "After a record price spike in France, regulators raised the real ceiling to 4,000 "
    "EUR/MWh in May 2022. After another price spike in the Baltic countries a few months "
    "later, they raised it again to 5,000 EUR/MWh. There's also now a standing rule that lets "
    "the ceiling climb further on its own if prices keep bumping up against it. Since we're "
    "modelling 2027 - a year that hasn't happened yet - the REAL ceiling that will actually "
    "apply by then is very unlikely to still be 3,000 EUR/MWh; it's already 5,000 today. This "
    "is a genuinely different question from an earlier one we already settled (whether to "
    "artificially LOWER this number just to make our correlation numbers look better, which "
    "we decided against as a form of cheating). Updating this number to match the REAL, "
    "current legal ceiling - because it's simply more accurate for the year we're modelling - "
    "would be a legitimate reason to revisit it, and is now flagged as a possible next step "
    "rather than acted on immediately.",
    color=AMBER,
)
pdf.analogy(
    "think of the 3,000 EUR/MWh figure like a speed limit sign the model copied off an old "
    "highway sign from a few years ago. The number was correct and legal AT THE TIME the sign "
    "was made - it's not fake or invented. But the real, current speed limit on that same "
    "stretch of road has since been raised twice. Nobody did anything wrong by copying the old "
    "sign - but if we're planning for how the road works today rather than a few years ago, "
    "it's worth knowing the sign is out of date."
)

# =====================================================================
pdf.h1("Where This Leaves Us")
pdf.body(
    "A full, productive day - several real findings, one genuine improvement kept, two "
    "honest dead ends ruled out rather than left unresolved:"
)
pdf.set_font("Helvetica", "", 10.5)
pdf.set_text_color(20, 24, 22)
for line in [
    "- Heat-pump weather doesn't matter much - that lead is closed, no need to revisit it.",
    "- The midday gap is very likely explained by Germany having no way to export surplus power "
    "in our model - confirmed as a real, structural limit, not fixed today.",
    "- Brainpool's real weather-year assumption (2009) is now confirmed correct, and their "
    "real cross-border approach (about 30 countries, not one) is now known rather than guessed.",
    "- Blending the import price across 11 real neighbouring countries instead of just France "
    "gave a small, genuine improvement - this change is being kept.",
    "- Building a proper two-way 'export' feature is possible in principle, but a genuinely "
    "large undertaking - a decision on whether it's worth doing is still open.",
    "- Public holidays do not appear to explain the remaining gap - checked and ruled out.",
    "- 2023 (our demand-shape source year) turned out to be the WORST weather match to 2009 "
    "of all six candidate years checked - 2016 was the best. Rebuilding on 2016 cut the "
    "number of shortage hours further and is being kept, though it did not meaningfully "
    "improve ordinary-hour tracking.",
    "- The model's 3,000 EUR/MWh shortage price is confirmed to be a real historical EU "
    "regulatory price cap, correctly copied from AMIRIS's own 2019 example - but the real "
    "cap has since risen to 5,000 EUR/MWh, so it may be worth updating for a 2027 scenario.",
]:
    pdf.set_x(MARGIN)
    pdf.multi_cell(0, 5.8, line)
pdf.ln(2)
pdf.body(
    "All the technical detail behind today's work - the exact numbers, the files, the "
    "scripts used - has also been folded into the main, more detailed progress report "
    "(AMIRIS_Germany2027_Progress_Report.pdf) as Phases 12 through 18, for the full record."
)

pdf.output("AMIRIS_Session_2026-08-24.pdf")
print("Saved AMIRIS_Session_2026-08-24.pdf")
