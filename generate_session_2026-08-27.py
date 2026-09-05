"""Generates AMIRIS_Session_2026-08-27.pdf - a very simple, plain-language walkthrough of
today's specific conversation: what was asked, and what happened, in the order it happened.
Written for someone with no technical background - no jargon left unexplained, short
sentences, everyday analogies. Separate from the cumulative Progress Report, which is more
technical and covers the whole project. Follows straight on from yesterday's session
(AMIRIS_Session_2026-08-26.pdf), which ended with the calendar bug fix. Today's session
covered building the supervisor progress presentation, then answering a set of follow-up
questions about specific things in it - captured here in full."""
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
        self.cell(0, 8, f"AMIRIS Session Notes - 27 August 2026                                                                                    Page {self.page_no()}", align="C")

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
pdf.cell(0, 6, "27 August 2026", new_x="LMARGIN", new_y="NEXT")
pdf.ln(2)
y = pdf.get_y()
pdf.set_draw_color(*NAVY)
pdf.set_line_width(1)
pdf.line(MARGIN, y, 210 - MARGIN, y)
pdf.ln(5)

pdf.body(
    "Today started with preparing a supervisor progress-update presentation covering "
    "everything done since the last meeting, then adding extra slides on the 2028/2029 "
    "testing and the calendar bug fix. That presentation then raised a number of good "
    "follow-up questions about specific things it mentioned - this note captures each "
    "answer in full, plain-language detail."
)

# =====================================================================
pdf.h1("1. Did we actually get a 2009 offshore wind profile?")
pdf.question("You said 'Offshore wind: no real correlation (r = 0.01) - a genuine, separate gap'. Were we able to get offshore wind from 2009? What steps did we take to get those 2009 profiles?")
pdf.result(
    "Yes - we did successfully pull a real 2009 offshore wind profile. The low correlation isn't a failure of that pull; it's because there was nothing real to compare it against in the first place.",
    "The steps taken to get all three 2009 weather profiles (onshore wind, offshore wind, "
    "and solar) were the same: we used a public weather-simulation service called "
    "renewables.ninja, which turns real historical weather records into realistic hour-by-"
    "hour wind and solar output estimates. We needed an access token for this service - the "
    "first one we had on file turned out to be invalid, so a new one was generated and that "
    "one worked. We then downloaded hourly output for real 2009 weather, covering the same "
    "regional split (north, east, middle, southwest Germany) used elsewhere in this project, "
    "and averaged those into one national profile - matching how Brainpool's own data was "
    "structured. One technical snag along the way: the service returns its timestamps in an "
    "unusual format (raw computer time-codes rather than plain dates), which needed a small "
    "fix to read correctly.",
    color=GOOD,
)
pdf.body(
    "Once we had the 2009 data, we compared it against what our model was already using, to "
    "see how similar the patterns were. For onshore wind and solar, that comparison was "
    "meaningful because Brainpool had actually supplied us with a real regional profile to "
    "compare against - and the two matched well (onshore wind 90% similar, solar 97% "
    "similar)."
)
pdf.result(
    "Offshore wind was different: there was no real Brainpool profile to compare it to at all.",
    "Brainpool's own data never included a real offshore wind shape in the first place - "
    "this was flagged as a data gap right at the very start of this project. So the "
    "'original' profile our model had been using for offshore wind was never a real weather "
    "pattern to begin with - it was a generic, reused example shape borrowed from AMIRIS's "
    "own software, included only because something had to go there. When we compared our "
    "real 2009 offshore data against that generic placeholder, of course they barely "
    "matched (1%) - we were comparing a real year's actual weather against something that "
    "was never meant to represent any specific year at all. This isn't a mistake in how we "
    "pulled the 2009 data; it's an honest reflection of a data gap that was already known "
    "and documented, now made visible in a chart.",
    color=AMBER,
)
pdf.analogy(
    "imagine checking how well a photo of today's actual weather matches a generic stock "
    "photo of 'a cloudy day' used as a placeholder because no real photo was available. Of "
    "course they won't match closely - the stock photo was never a picture of any real day "
    "in the first place. That doesn't mean today's photo is wrong; it just means there was "
    "nothing real to compare it against."
)

# =====================================================================
pdf.h1("2. What does \"each component shaped with the data suited to it\" mean?")
pdf.question("\"Each component shaped using the real data suited to it\" for V2, what do you mean by this?")
pdf.body(
    "This refers to how our second demand model (V2) was built, and what specifically made "
    "it better than the first attempt (V1)."
)
pdf.result(
    "V1's problem: one single shape was stretched to represent everything.",
    "V1 used a single, generic household electricity-usage shape (a standard curve normally "
    "used to represent ordinary homes) and applied that ONE shape to represent ALL of "
    "Germany's electricity use - homes, industry, heat pumps, electric vehicles, hydrogen "
    "production, everything at once. That produced an unrealistic result: an exaggerated "
    "evening spike (since household usage peaks sharply in the evening) that doesn't "
    "actually match how a whole country's electricity use really behaves.",
    color=BAD,
)
pdf.result(
    "V2's fix: four separate pieces, each built from the data that actually explains it.",
    "V2 split total demand into four real components, and built each one using the kind of "
    "data that actually drives that specific type of usage:",
    color=GOOD,
)
pdf.table(
    ["Component", "Share", "Built using"],
    [
        ["Base demand", "~92%", "Real historical German grid usage data (a real past year)"],
        ["Heat pumps", "~3%", "Real outdoor temperature data (colder = more heating)"],
        ["Electrolysis", "~2%", "A steady, round-the-clock industrial pattern"],
        ["EV charging", "~3%", "A typical daily home-charging pattern"],
    ],
    [45, 25, 120],
)
pdf.body(
    "The key idea: heat-pump electricity use is mainly driven by TEMPERATURE, not by "
    "generic household habits - so it needed real temperature data, not a household usage "
    "curve, to be represented properly. The bulk of demand (everyday economic activity) is "
    "best represented by real historical grid data, not a household curve either. Using the "
    "right kind of data for each piece, instead of forcing one generic shape to cover "
    "everything, is what 'shaped using the data suited to it' means."
)
pdf.analogy(
    "picture trying to predict a whole city's water usage using only one household's water "
    "bill, scaled up. It would miss the fact that a hospital's water use follows a totally "
    "different pattern from a factory's, which is different again from a school's. A much "
    "better approach is to model the hospital, the factory, and the school separately, each "
    "using the kind of information that actually explains THEIR usage - then add them "
    "together. That is exactly what V2 does for electricity demand."
)

# =====================================================================
pdf.h1("3. How did we make demand \"smart\", and what did it actually get us?")
pdf.question("The Making Demand Smart slide: Explain further how we achieved it and what benefit it added.")
pdf.body(
    "This covers two of the components from the table above: hydrogen production "
    "(electrolysis) and EV charging. Both used to draw electricity at a completely flat, "
    "constant rate, every single hour of the year, regardless of price. Today's question "
    "asked for more detail on exactly HOW that was changed, and WHY it actually mattered."
)
pdf.result(
    "How: each was rebuilt as its own separate, independent decision-maker inside the model.",
    "Both were pulled out of the main demand total and rebuilt as their own agents, using a "
    "tool AMIRIS already provides for battery-like devices. Two key ingredients made this "
    "work: first, a firm, non-negotiable requirement to use a certain total amount of "
    "electricity across the year (the same total as before - nothing about how MUCH "
    "electricity they use changed). Second, freedom to decide WHEN, hour by hour, to "
    "actually draw that electricity, based on which hours are cheapest. The model doesn't "
    "just assume this happens - it has to genuinely work out the cheapest way to hit its "
    "required total, the same way a real factory manager would.",
    color=GOOD,
)
pdf.body(
    "This is different from an earlier attempt (trying to let the model sell EXTRA power "
    "abroad) that never worked, because that attempt had no firm requirement forcing it to "
    "ever act - it was free to just do nothing, and it did. Electrolysis and EV charging "
    "both have a genuine, real reason to act: they must hit their yearly total one way or "
    "another."
)
pdf.result(
    "Verified it actually works, not just assumed it: checked the real hour-by-hour numbers directly.",
    "Hydrogen production's electricity use now moves in the opposite direction to price - "
    "using more when price drops. EV charging shows an even clearer change: it now peaks "
    "in the late morning to early afternoon (exactly when solar power creates a midday "
    "surplus) and drops to its lowest point in the early evening - precisely the time it "
    "used to peak, back when it was still following the old, unmanaged pattern. That's a "
    "genuine behavioural flip, not just a small nudge.",
    color=GOOD,
)
pdf.result(
    "The benefit: fewer hours where the model runs out of power, and a genuinely more realistic picture.",
    "Hydrogen production's fix alone cut the number of 'ran out of power' hours from 4 down "
    "to 1 for the year. EV charging's fix went further still: the number of 'ran out of "
    "power' hours reached ZERO for the first time in this whole project. That matters "
    "beyond just being a nice round number - with zero such hours, there is nothing left to "
    "quietly distort the headline comparison score, so when that score also improved, it's "
    "a real, trustworthy improvement, not a side effect of hiding a few bad hours. On top of "
    "that, this change makes the model behave more like the real world: real hydrogen "
    "producers and real EV smart-chargers genuinely do shift their usage to cheap hours "
    "today, so this isn't just a numbers trick - it's the model catching up to a real "
    "behaviour it was missing.",
    color=GOOD,
)
pdf.analogy(
    "picture a factory that used to run its biggest, most power-hungry machine at exactly "
    "the same speed 24 hours a day, no matter the cost. Today, it was given a smart dial: "
    "it still has to make the same amount of product by year's end, but now it's free to "
    "speed up when electricity is cheap and slow down when it's expensive - exactly what a "
    "sensible real factory manager would do. Checking the dial's actual log afterward "
    "confirmed it really was being used this way, not just sitting there doing nothing "
    "useful."
)

# =====================================================================
pdf.h1("4. The calendar bug: what it was, and how we fixed it")
pdf.question("Explain the calendar bug fix, what the bug is and how we fixed it.")
pdf.body(
    "Our demand shape is built by borrowing a real past year's worth of German electricity "
    "usage (2016 - explained further in the next section) and reshaping it to fit our "
    "target year (2027 or 2029). 2016 happens to be a leap year - it has 366 days, one more "
    "than a normal year. To make it fit a normal 365-day target year, exactly one day had "
    "to be removed from the 2016 data."
)
pdf.result(
    "The bug: the day removed was February 29th - sitting right in the MIDDLE of the year.",
    "February 29th is the 'extra' leap day, so removing it seemed like the obvious choice. "
    "But it sits in the middle of the calendar, not at the edge. When a day is removed from "
    "the middle of a year-long sequence and the rest is simply read straight through "
    "afterward, EVERY day from that point onward quietly lands one weekday later than it "
    "actually should. Concretely: real February 28th, 2016 was a Sunday. The real day right "
    "after the removed Feb 29th is March 1st - a Tuesday. But our code was treating that "
    "March 1st data as if it directly followed the Sunday, effectively mislabelling it. "
    "That one-day drift then continues, uncorrected, all the way through to December 31st - "
    "affecting 10 of the year's 12 months, roughly 84% of the whole year.",
    color=BAD,
)
pdf.body(
    "This bug had been sitting undetected in our main model since it was first built with "
    "this 2016-based approach. The reason it wasn't caught earlier: the one check that was "
    "done at the time only confirmed that January 1st lined up on the correct day of the "
    "week for both years - which it did, since January and most of February come BEFORE "
    "the point where the bug kicks in. The check simply never looked far enough into the "
    "year to notice anything wrong."
)
pdf.result(
    "How we found it: a strange, reversed pattern in the 2028/2029 results led us to check the model's own numbers directly.",
    "While testing 2028 and 2029, we noticed weekdays were matching Brainpool's real prices "
    "noticeably WORSE than weekends - the opposite of the pattern seen in 2027. That was "
    "unusual enough to investigate directly rather than dismiss as random noise. Checking "
    "the model's own demand numbers by real day of the week showed something clearly wrong: "
    "Friday demand was coming out unusually LOW, and Sunday demand unusually HIGH - the "
    "opposite of how real electricity use actually behaves (real usage is highest on "
    "weekdays and lowest on Sunday). That mismatch was the direct clue that something "
    "concrete was broken, not just an ordinary modelling imperfection.",
    color=AMBER,
)
pdf.result(
    "The fix: remove December 31st instead of February 29th.",
    "December 31st sits at the very END of the year rather than the middle. Removing the "
    "very last day of a sequence doesn't disturb anything that comes before it - every "
    "earlier day keeps its correct real-world weekday alignment, all the way through. This "
    "is exactly the same trick our 2028 model was already using successfully, for a "
    "completely different, unrelated technical reason - which is also why 2028 never had "
    "this particular bug in the first place, only 2027 and 2029 did.",
    color=GOOD,
)
pdf.body(
    "After making this fix and rebuilding both affected years, the result was a clean, "
    "genuine improvement: both 2027 and 2029 got noticeably better at matching Brainpool's "
    "real prices, AND their average error got smaller too, at the same time - with almost "
    "no downside. That combination (two good things improving together, not one improving "
    "at the other's expense) is exactly the kind of result you'd expect from fixing a real "
    "mistake, rather than just shuffling settings around."
)
pdf.analogy(
    "picture a calendar where someone rips out one page from the middle of the year - say, "
    "March 15th - and just glues the remaining pages back together without renumbering "
    "anything. From that point on, every date on the calendar quietly lands on the wrong "
    "day of the week for the rest of the year, even though January and early March still "
    "look completely fine. Now imagine fixing it by instead tearing out December 31st - the "
    "very last page - which causes no such problem, since nothing comes after it to get "
    "thrown off."
)

# =====================================================================
pdf.h1("5. Why did we choose 2016 as the demand-source year?")
pdf.question("\"Our demand shape borrows a real year's usage pattern (2016) and trims it to fit the target year\" - remind me again why we chose the 2016 demand profile, I think it was the closest we could get due to similar temperature with 2009, right?")
pdf.result(
    "Correct - that is exactly why 2016 was chosen, and it was checked directly rather than assumed.",
    "We don't have real electricity USAGE data for 2009 itself - that information simply "
    "isn't published in the detail we'd need. But we do know Brainpool's own real forecast "
    "is built using real WEATHER from 2009 (confirmed directly from their own published "
    "methodology). Since weather - especially temperature - is one of the biggest real "
    "drivers of how much electricity a country uses hour by hour, the reasoning was: if we "
    "can find a year we DO have real usage data for, whose weather closely resembled 2009's, "
    "that year's usage SHAPE is a reasonable stand-in for what 2009 itself would probably "
    "have looked like.",
    color=GOOD,
)
pdf.body(
    "Rather than guess at which year might be the closest match, every year we have real "
    "German usage data for (2015 through 2019, and 2023) was checked directly: real "
    "hour-by-hour temperature data was pulled for each of those years and compared against "
    "real 2009 temperature, using several measures at once - overall average temperature, "
    "how cold the year was in total (a standard heating measure), how closely the "
    "month-by-month pattern matched, and how closely the hour-by-hour ups and downs matched."
)
pdf.table(
    ["Year", "How it compared to 2009's weather"],
    [
        ["2016", "Best match of all six years checked"],
        ["2018", "Second-best"],
        ["2017", "Third"],
        ["2015", "Fourth"],
        ["2019", "Second-WORST match"],
        ["2023 (used until then)", "WORST match of all six"],
    ],
    [45, 145],
)
pdf.result(
    "A genuinely useful check: our own two guesses (2023, and later 2019) both turned out to be poor choices.",
    "2023 - the year we had been using up to that point, mostly for convenience since it "
    "was already available - turned out to be the single WORST weather match to 2009 of "
    "all six years checked. Separately, when 2019 was suggested as a possibly better "
    "candidate, checking it directly showed it was actually the SECOND-WORST match, not a "
    "good one at all. 2016, which nobody had specifically suggested beforehand, turned out "
    "to be the genuine best match - only found by checking every candidate properly instead "
    "of assuming.",
    color=AMBER,
)
pdf.body(
    "A small bonus turned up along the way, though it wasn't the reason for the choice: "
    "2016 is also a leap year, and January 1st, 2016 happens to fall on the same day of the "
    "week as January 1st, 2027 (both Fridays) - a genuine coincidence that made the "
    "calendar-alignment step simpler for the 2027 build specifically."
)
pdf.analogy(
    "picture trying to guess how busy a beach was on a specific day years ago, when no "
    "attendance records survive - but you do know it was a particularly hot, sunny day. "
    "Rather than guess at random, you could check which OTHER day, from years you do have "
    "attendance records for, had the most similar weather - hot and sunny in the same way - "
    "and use THAT day's real attendance as your best available estimate. That's the same "
    "logic used here: find the closest weather match among the years we actually have real "
    "data for, and borrow its shape."
)

# =====================================================================
pdf.h1("6. All-hours, weekday, and weekend correlation - what do they each mean?")
pdf.question("Explain all hour correlation, weekday and weekend correlation.")
pdf.body(
    "These are three versions of the same basic measurement - how closely our model's "
    "prices move up and down together with Brainpool's real prices - just computed over "
    "different slices of the year. This measurement (called 'correlation') has been the "
    "main scorecard used throughout this whole project to judge whether the model is really "
    "getting the SHAPE of the price pattern right, not just the average level."
)
pdf.result(
    "ALL-HOURS correlation: every single hour of the year, no exceptions.",
    "This uses all 8,760 hours in the year, including the rare hours where the model "
    "completely 'ran out of power' and got stuck at a fixed emergency price. The problem: "
    "even a small handful of those extreme hours can noticeably drag this number around, "
    "even when the model is actually tracking very well on ordinary days. It's a bit like "
    "how one very unusual data point can throw off a simple average.",
    color=GREY,
)
pdf.result(
    "EXCLUDING-SHORTAGE correlation (our main, trusted number): the same measurement, but leaving out those rare emergency-price hours.",
    "This is the number relied on most heavily throughout this whole project, because it "
    "isn't distorted by a handful of extreme hours - it gives an honest picture of how well "
    "the model tracks Brainpool's price on a NORMAL day, which is what we actually care "
    "about most.",
    color=GOOD,
)
pdf.result(
    "WEEKDAY correlation and WEEKEND correlation: splitting that trusted number further, into Monday-Friday hours and Saturday-Sunday hours, calculated separately.",
    "This is a more detailed, zoomed-in version of the same check - instead of one single "
    "score for the whole year, we get two scores: one for how well weekdays track, and one "
    "for how well weekends track. This matters because our demand-building process "
    "specifically tries to line up real weekdays and real weekends between the borrowed "
    "source year and the target year - so if THAT alignment is ever done wrong, it shows up "
    "as a clear, specific gap between the weekday score and the weekend score, rather than "
    "just a vague overall problem. This exact split is what first revealed the original "
    "weekday-alignment issue much earlier in this project, and it's also what led directly "
    "to discovering this session's calendar bug.",
    color=AMBER,
)
pdf.analogy(
    "imagine grading a student's exam three different ways: an overall grade across every "
    "question (some of which might be unusually tricky outlier questions that don't "
    "reflect their real understanding); a fairer overall grade that sets aside those few "
    "outlier questions; and then two separate mini-grades - one for just the maths "
    "questions, one for just the language questions. That last, more detailed split doesn't "
    "just tell you THAT something needs improving - it tells you exactly WHERE to look. "
    "That's exactly the role the weekday/weekend split plays here."
)

# =====================================================================
pdf.h1("Where This Leaves Us")
pdf.body("A day spent explaining, in full plain-language detail, several things the new presentation touched on only briefly:")
for line in [
    "- Confirmed: we did successfully pull real 2009 offshore wind data. Its low match score "
    "isn't a mistake in that work - it's because there was never a real reference profile "
    "for offshore wind to compare it against in the first place, a data gap flagged since "
    "the very start of this project.",
    "- Clarified what 'shaped using the data suited to it' means for V2: four demand pieces, "
    "each built from the real data that actually explains that piece (grid history, "
    "temperature, industrial patterns, charging patterns) - not one generic shape stretched "
    "to cover everything.",
    "- Explained the 'smart demand' fix in full: both hydrogen production and EV charging "
    "were rebuilt to freely choose WHEN to draw their required electricity, verified "
    "directly to now favour cheap hours, delivering fewer 'ran out of power' hours (down to "
    "zero for EV charging) and a genuinely more realistic model.",
    "- Walked through the calendar bug in full: removing a leap day from the MIDDLE of the "
    "year (Feb 29) silently broke weekday alignment for 84% of the year; fixed by removing "
    "the LAST day of the year (Dec 31) instead.",
    "- Confirmed and explained why 2016 was chosen as the demand-source year: the closest "
    "real weather match to 2009 among every year checked - found by testing directly, not "
    "guessing (both 2023 and 2019 turned out to be poor choices).",
    "- Explained the three correlation numbers used throughout this project: all-hours (can "
    "be distorted by rare extreme hours), excluding-shortage (the trusted main number), and "
    "the weekday/weekend split (the detailed version that has twice now led directly to "
    "finding a real, fixable problem).",
]:
    pdf.set_x(MARGIN)
    pdf.multi_cell(0, 5.8, line)
pdf.ln(2)
pdf.body(
    "These explanations are recorded here in full for reference alongside the presentation "
    "built earlier today, which covers the same material in a much more condensed, "
    "slide-ready form."
)

pdf.output("AMIRIS_Session_2026-08-27.pdf")
print("Saved AMIRIS_Session_2026-08-27.pdf")
