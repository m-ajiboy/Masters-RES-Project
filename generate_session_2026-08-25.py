"""Generates AMIRIS_Session_2026-08-25.pdf - a very simple, plain-language walkthrough of
today's specific conversation: what was asked, and what happened, in the order it happened.
Written for someone with no technical background - no jargon left unexplained, short
sentences, everyday analogies. Separate from the cumulative Progress Report, which is more
technical and covers the whole project. Follows straight on from yesterday's session
(AMIRIS_Session_2026-08-24.pdf), which ended on the question of why AMIRIS uses 3,000
EUR/MWh for its shortage price."""
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
        self.cell(0, 8, f"AMIRIS Session Notes - 25 August 2026                                                                                    Page {self.page_no()}", align="C")

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
pdf.cell(0, 6, "25 August 2026", new_x="LMARGIN", new_y="NEXT")
pdf.ln(2)
y = pdf.get_y()
pdf.set_draw_color(*NAVY)
pdf.set_line_width(1)
pdf.line(MARGIN, y, 210 - MARGIN, y)
pdf.ln(5)

pdf.body(
    "Quick reminder of where yesterday's conversation left off: we'd just confirmed that "
    "AMIRIS's 3,000 EUR/MWh shortage price is not an arbitrary number - it's the real, "
    "legally-binding price ceiling the whole European electricity market operated under from "
    "late 2017 to mid-2022, and that the REAL ceiling has since been raised twice, to "
    "5,000 EUR/MWh. Today picked up directly from that: would actually updating our model to "
    "use 5,000 instead of 3,000 make things better or worse?"
)

# =====================================================================
pdf.h1("1. Would raising the shortage price to 5,000 help or hurt?")
pdf.question("Updating it to 5000 will worsen our mean price and likely reduce our correlation more, right?")
pdf.body(
    "A fair and sharp question - and rather than answer it by reasoning it out on paper, it "
    "was tested directly on real numbers from yesterday's best build: the handful of hours "
    "where the model already runs out of power (currently priced at 3,000 EUR/MWh) were "
    "relabelled to 5,000 EUR/MWh instead, and every comparison number was recalculated to see "
    "what actually happens."
)
pdf.table(
    ["Measure", "At 3,000 (now)", "At 5,000 (test)"],
    [
        ["Average price", "56.17", "57.09"],
        ["How far off Brainpool's average", "-11.87", "-10.95"],
        ["How closely they move together", "0.439", "0.317"],
    ],
    [80, 50, 50],
)
pdf.result(
    "Half right, half wrong - and both halves make sense once you look at why.",
    "The average price: it actually gets SLIGHTLY BETTER, not worse. Our model already runs "
    "a bit lower than Brainpool's on average, so nudging a few extreme hours up a little "
    "brings the year's average a little closer to Brainpool's, not further away.",
    color=GOOD,
)
pdf.result(
    "But the 'how closely they move together' number does get worse, as you suspected.",
    "Here's why: on checking Brainpool's own real price during those exact same few hours, "
    "it turned out Brainpool was only showing about 115-130 EUR/MWh at that time - nothing "
    "close to an emergency price. So our model calling those hours a full-blown shortage at "
    "3,000 EUR/MWh was already a mismatch with what Brainpool shows. Pushing our number up "
    "to 5,000 makes that same mismatch even bigger, not smaller - which is exactly the kind "
    "of thing that drags the 'move together' score down.",
    color=AMBER,
)
pdf.body(
    "One more important detail: this effect is confined entirely to the handful of hours "
    "involved. The main, more trustworthy comparison we've used throughout this whole project "
    "- which sets aside those rare 'ran out of power' hours and looks only at ordinary hours "
    "- doesn't move at all, either way. Nothing about how well the model tracks Brainpool on "
    "a normal day changes."
)
pdf.analogy(
    "picture a company where most employees' pay didn't change, but a couple of very "
    "high earners got a further raise. The company's AVERAGE pay would go up (closer to some "
    "target you're comparing it to, say) - but if you're checking whether pay rises and "
    "falls TRACK a colleague's pay at another company hour by hour, those two outliers now "
    "stick out even further from everyone else, which makes the overall 'do these two "
    "move together' picture look worse, even though nothing changed for most people."
)
pdf.body(
    "Bottom line: updating this number to match today's real regulatory price ceiling would "
    "still be a legitimate, defensible choice - it's not the same as artificially lowering "
    "the number just to make a correlation score look better, which was already ruled out "
    "earlier in this project as a form of cheating. But it's worth knowing upfront that doing "
    "so would make one commonly-checked number (the all-hours correlation) look worse for "
    "reasons that have nothing to do with the model actually getting worse - so if this "
    "change is made later, that number moving in the 'wrong' direction shouldn't be read as "
    "a step backward."
)

# =====================================================================
pdf.h1("2. Building the 'small adjustment' before the big export project")
pdf.question("Yes, build it but keep the build separate.")
pdf.body(
    "Earlier in this project (see the previous progress report) we'd found that our model has "
    "no way to sell surplus midday solar power to other countries the way Germany really does "
    "- and that properly fixing that would be a huge job. Before committing to that huge job, "
    "one much smaller idea was suggested: hydrogen production (called 'electrolysis' - using "
    "electricity to split water into hydrogen and oxygen) makes up about 15 out of every "
    "1,000 units of Germany's total electricity use in our model. Until today, our model had "
    "this hydrogen production drawing exactly the same amount of electricity every single "
    "hour, all year round - never more, never less."
)
pdf.body(
    "In real life, hydrogen producers don't have to run flat like that - they can choose to "
    "run harder when electricity is cheap (or even free, on a very sunny, windy day) and ease "
    "off when it's expensive. Today's build gave our model's hydrogen producer that same "
    "freedom - while still making it use the exact same total amount of electricity across "
    "the year as before, just letting it choose WHEN."
)
pdf.result(
    "How it was built: reusing a real, already-proven pattern - not inventing something new.",
    "AMIRIS's own official example library already contains a working example of exactly this "
    "kind of flexible, one-directional consumer (used there for things like electric vehicle "
    "charging). This build followed that same proven pattern for our hydrogen producer instead "
    "of trying to reuse the leftover pieces from the failed 'sell power abroad' attempt from "
    "earlier this project - which is important, because that earlier attempt failed for a "
    "specific, well-understood reason (nothing was ever forcing it to act). This new build "
    "does have something forcing it to act: a constant, ongoing 'must eventually produce this "
    "much hydrogen' requirement, exactly like a real hydrogen plant has real customers to "
    "supply.",
    color=GOOD,
)
pdf.body(
    "Rather than just assume the new hydrogen producer was behaving correctly, its actual "
    "hour-by-hour behaviour was checked directly against real output data from the simulation:"
)
pdf.table(
    ["Check performed", "Result"],
    [
        ["Total electricity used all year", "14.94 of the targeted 14.97 trillion watt-hours - essentially unchanged"],
        ["Does it use more when price is low?", "Yes - more than double the usage in the cheapest hours vs. the most expensive"],
        ["What does it do during free/negative-price hours?", "Runs at its highest rate of the entire year"],
        ["What time of day does it run hardest?", "9am-1pm - exactly the sunny, midday surplus window flagged earlier"],
    ],
    [90, 90],
)
pdf.result(
    "Result: it works exactly as intended - a real, verified success, not just a hopeful guess.",
    "The number of hours our model completely ran out of power fell further (from 4 to 1 for "
    "the whole year). The main headline 'how closely do the two match' number improved "
    "noticeably (from 0.439 to 0.553). But - in the same honest pattern seen with several "
    "earlier changes this project - most of that improvement traces back to there simply "
    "being fewer of those rare 'ran out of power' hours dragging the picture around, not the "
    "model suddenly agreeing much better with Brainpool on an ordinary day. On the fairer, "
    "ordinary-hours-only comparison, the number barely moved at all (0.645 to 0.640).",
    color=AMBER,
)
pdf.analogy(
    "picture a factory that used to run its noisiest, most power-hungry machine at the exact "
    "same speed 24 hours a day, whether electricity was cheap or expensive that hour. Today, "
    "it was given a smart dial: still has to make the same amount of product by year's end, "
    "but now speeds up when power is cheap and slows down when it's expensive - exactly the "
    "kind of thing a real factory manager would actually do. Checking the dial afterward "
    "confirmed it really was being used this way, not just sitting there unused like a "
    "dashboard light that looks like it works but doesn't."
)
pdf.body(
    "This is a genuinely different outcome from the failed 'sell power abroad' attempt "
    "described in the previous progress report - that one never worked at all; this one "
    "works exactly as designed, even though its effect on the main headline number the "
    "project cares about is still modest rather than a breakthrough."
)

# =====================================================================
pdf.h1("3. Doing the same thing for electric-vehicle charging")
pdf.question("Now let's try e-mobility smart-charging the same way.")
pdf.body(
    "Since the hydrogen-producer fix above worked so well, the obvious next candidate was "
    "electric-vehicle charging - the second-biggest 'flexible' slice of Germany's electricity "
    "use in our model (about 18 out of every 1,000 units, similar in size to the hydrogen "
    "piece). Until today, our model assumed EVs get charged the way most people actually do "
    "today: mostly in the evening, after work, all piling on to the grid at once - what's "
    "called 'unmanaged' charging in the real world."
)
pdf.body(
    "'Smart charging' is the alternative real EV owners are increasingly offered: let the "
    "charger itself decide when to actually draw power (e.g. overnight, or during a sunny "
    "afternoon) as long as the car is topped up by the time it's needed - rather than blindly "
    "charging the moment it's plugged in, right when everyone else's evening also spikes "
    "electricity demand. This was built the same way as the hydrogen piece: its own separate, "
    "clearly labelled agent, still required to use the exact same total amount of electricity "
    "over the year, just free to choose WHEN."
)
pdf.body("The same real-behaviour checks were run again to make sure it wasn't just assumed to work:")
pdf.table(
    ["Check performed", "Result"],
    [
        ["Total electricity used all year", "17.80 of the targeted 17.81 trillion watt-hours - essentially unchanged"],
        ["Does it use more when price is low?", "Yes - nearly double the usage in the cheapest hours vs. the most expensive"],
        ["What time did it used to peak (old shape)?", "6pm - the old 'everyone plugs in after work' assumption"],
        ["What time does it peak now?", "9am-1pm, and it specifically AVOIDS 5pm-7pm - a genuine flip, not a small tweak"],
    ],
    [90, 90],
)
pdf.result(
    "Result: the best outcome of this whole project so far - and this time it's not just an illusion of fewer bad hours.",
    "The number of hours our model completely ran out of power dropped to ZERO for the first "
    "time ever in this project. That matters for a subtle but important reason: earlier "
    "improvements (including today's hydrogen result) looked good mostly because they had "
    "fewer of those rare 'ran out of power' hours dragging the picture around - like removing "
    "a couple of extreme outliers from an average. With zero such hours left here, there's "
    "nothing left to remove - so when the 'how closely do the two match' number still improved "
    "(from 0.640 to 0.647), that's a genuine, real improvement in ordinary-day tracking, not a "
    "side effect. One small honest downside: the average price came out very slightly further "
    "below Brainpool's than before - shifting demand toward the cheapest hours nudges the "
    "yearly average down a touch, even while the shape matches better.",
    color=GOOD,
)
pdf.analogy(
    "picture a household that used to run its washing machine and EV charger right when "
    "everyone gets home from work and dinner needs cooking too - the classic 'evening rush' "
    "that strains a whole neighbourhood's electricity supply at once. Now imagine that same "
    "household using a smart plug that waits until midday, when the neighbour's solar panels "
    "are flooding the local grid with cheap power, or late at night when hardly anyone else "
    "is using electricity. Nothing about how much the household uses changes - just when. "
    "Checking the smart plug's actual log confirmed it really is doing this, not just sitting "
    "there with a green light that means nothing."
)

# =====================================================================
pdf.h1("4. Trying the same smart-charging idea on the big battery/reservoir units")
pdf.question("Let's try smart-charging the battery storage agents too.")
pdf.body(
    "Our model has three big storage units representing Germany's pumped-hydro plants, "
    "grid-scale batteries, and reservoir hydro dams. The natural next question was: could "
    "these be given the same 'choose when to use electricity' upgrade as hydrogen production "
    "and EV charging?"
)
pdf.result(
    "First, a check - and it turned out these three were never 'flat' or 'dumb' to begin with.",
    "Unlike hydrogen production and EV charging (which used to draw electricity the same "
    "every hour, no matter the price), these three storage units have always been built to "
    "buy and sell electricity based on price - that is quite literally their entire job "
    "(charge when cheap, sell back when expensive). Checking their actual behaviour confirmed "
    "this: all three already buy far more electricity in the cheapest hours than the most "
    "expensive ones, exactly as they should. So there was no 'unmanaged' version of these to "
    "fix - applying the same upgrade again would just be rebuilding something that already "
    "works.",
    color=GOOD,
)
pdf.body(
    "But the same check turned up something else worth following up: one of the three - the "
    "reservoir hydro dams - was running into its own size limit surprisingly often. For "
    "35 out of every 100 hours in the year, it wanted to draw more power than its stated "
    "capacity (1.54 gigawatts) actually allows. The other two storage units almost never hit "
    "their own limits. This raised a fair question: is the reservoir dam's size holding the "
    "model back?"
)
pdf.result(
    "One important honesty check before testing this: that 1.54 GW figure is a REAL number from Brainpool, not something our model made up.",
    "This matters a lot. Earlier levers we adjusted (like the import limit) were things our "
    "own model had gotten wrong or guessed badly. This one is different: 1.54 gigawatts is "
    "Brainpool's own stated real-world capacity assumption for German reservoir hydro in "
    "2027. So testing a bigger number here isn't 'fixing a mistake' - it's asking a 'what if' "
    "question about a number that was already correct as given. That distinction was kept "
    "front and center in how this was tested and reported.",
    color=AMBER,
)
pdf.body("With that caveat clearly noted, the size was tested at double and triple the real figure, keeping everything else about the dam (like its total storage size) unchanged:")
pdf.table(
    ["Test", "How closely the two match", "Average error", "Still hitting its limit"],
    [
        ["Real size (1.54 GW)", "0.647", "28.19", "35% of the year"],
        ["Double size (3.08 GW)", "0.650", "27.36", "32% of the year"],
        ["Triple size (4.62 GW)", "0.656", "26.76", "30% of the year"],
    ],
    [70, 40, 35, 35],
)
pdf.result(
    "Result: a real but modest improvement - and even tripling the size doesn't fully solve it.",
    "Every measure got a little better as the dam was made bigger, confirming its size really "
    "is holding things back somewhat, not just an illusion. But the improvement is small, and "
    "even at three times the real size, the dam is STILL running into its limit 30% of the "
    "year - there's no size at which the problem cleanly goes away, it just eases gradually. "
    "Given that 1.54 GW is Brainpool's own real assumption, the right call is to keep using "
    "their real number rather than adopt an artificially bigger one - so this is being kept "
    "as a documented finding (how much this specific real-world limit is costing us) rather "
    "than a change to the model.",
    color=NAVY,
)
pdf.analogy(
    "picture a single checkout lane at a busy supermarket that's genuinely too narrow for "
    "the rush-hour crowd - adding a second lane clearly helps, and a third helps a bit more. "
    "But if the store's actual, real floor plan only allows for one lane, the right answer "
    "isn't to imagine two extra lanes into existence - it's to note honestly that the single "
    "lane is a real bottleneck, while still working with the store you actually have."
)

# =====================================================================
pdf.h1("5. Finding out what's left to fix, and investigating a new seasonal puzzle")
pdf.question("What other small adjustments are left before the export project?")
pdf.body(
    "Rather than guess at what to try next, the same 'where exactly does the mismatch happen' "
    "check used earlier this project (the one that originally found the weekday/weekend gap "
    "and the midday solar problem) was re-run on today's best-yet model - now with both the "
    "hydrogen and EV fixes in place."
)
pdf.result(
    "Finding: the midday problem is still there, almost unchanged - a clear signal.",
    "Even with two genuinely working demand-shifting fixes now in place, the midday gap "
    "barely moved (still crashing to about 41 units below Brainpool's price around 11am). "
    "There is simply far more midday sunny-day surplus than what we've built can soak up. "
    "This is now good, solid evidence that we've gotten about as much out of 'shift demand "
    "around' as we're going to - the real fix for this specific piece would be giving the "
    "model a genuine way to sell power abroad, the bigger project flagged earlier.",
    color=BAD,
)
pdf.body(
    "But the same check also turned up something we hadn't looked at before: prices in "
    "July through October are consistently much further below Brainpool's than in any other "
    "part of the year."
)
pdf.question("Yes, dig into the seasonal pattern next.")
pdf.body(
    "Five specific, sensible-sounding explanations were checked directly against the actual "
    "data, one at a time, rather than guessing which one was right:"
)
pdf.table(
    ["Possible explanation", "Checked? Result"],
    [
        ["Extra solar/wind power that summer", "Ruled out - totals are steady all year round"],
        ["More solar vs. wind mix in that window", "Ruled out - similar mix in months with small AND big gaps"],
        ["Cheaper imported power available", "Ruled out - import was actually among the cheapest all year"],
        ["Extra demand in that window", "Ruled out - similar demand to nearby months with a small gap"],
        ["Power plants offline for summer maintenance", "Ruled out - no dip in available plant capacity"],
    ],
    [110, 70],
)
pdf.result(
    "What was actually found: Brainpool assumes a steady price climb through summer that our model simply doesn't produce.",
    "Brainpool's price rises smoothly and predictably from May all the way to September, "
    "roughly the same small step up every single month. Our model's price does nothing of "
    "the sort - it just sits flat and a bit noisy through that whole stretch, then jumps up "
    "in October. That points to the same root cause flagged earlier: Brainpool's real "
    "forecasting tool watches roughly 30 countries at once - their reservoirs draining over "
    "summer, their scheduled power-plant maintenance, their gas-storage refilling season - "
    "and none of that is visible to a model that only looks at Germany on its own.",
    color=GREY,
)
pdf.analogy(
    "picture trying to predict a single shop's daily takings using only that shop's own "
    "till receipts, when the real reason takings rise every month from May to September is "
    "that a big regional festival season is building up across the whole area, drawing in "
    "more visitors month by month. The shop's own numbers alone will never reveal that "
    "pattern - you'd need to be watching the whole region, not just the one till, to see it "
    "coming."
)
pdf.body(
    "This was a genuinely useful 'nothing new to fix here' result: five specific, reasonable "
    "guesses were checked and ruled out one by one, rather than settling for the first one "
    "that sounded plausible - and what's left points back to the same big, already-known "
    "limitation (a single-country model can't see what a 30-country one can), not a new, "
    "smaller thing we've somehow missed."
)

# =====================================================================
pdf.h1("6. Testing the model on two brand-new years it has never seen")
pdf.question("I have put a new Brainpool file, named Amiris input data 2027-2029. It has the 2028-2029 data. The aim is to see if our various models are consistent with the other years.")
pdf.body(
    "Everything built so far has been carefully tuned to match one specific year: 2027. A "
    "fair question naturally follows: does any of that tuning actually generalise, or does it "
    "only work because it was built to match 2027 specifically? With Brainpool's new file "
    "covering 2028 and 2029 too, this could finally be tested properly - build those two "
    "years the exact same way, changing nothing about HOW anything is calculated, and see how "
    "close the results land to Brainpool's real forecasts for those years."
)
pdf.result(
    "A genuine surprise along the way: the simulation software itself doesn't understand leap years.",
    "2028 has 366 days in real life. Trying to run a full 366-day simulation failed outright, "
    "with the software itself explaining why: it always treats every year as exactly 365 "
    "days, and for a leap year it simply skips the 31st of December rather than adding the "
    "extra day in February. This wasn't something wrong with anything built here - it's a "
    "genuine limitation of the underlying tool, discovered only by hitting it head-on. Once "
    "understood, every part of the 2028 build was adjusted to work the same way the software "
    "itself expects.",
    color=AMBER,
)
pdf.result(
    "A second surprise: the 'smart EV charging' idea hit a real limit for 2029's numbers specifically.",
    "The 2029 build initially failed for a different reason: the smart-charging EV agent's "
    "'buffer' (how much slack it has to shift its charging around) was too tight for that "
    "year's specific price pattern, and the software's own planning engine gave up trying to "
    "find a workable schedule. Giving it a bigger buffer - not changing HOW it decides when to "
    "charge, just how much wiggle room it has - fixed it. This is flagged honestly as a "
    "practical engineering fix, not a case of quietly tweaking the model to get a better "
    "answer.",
    color=AMBER,
)
pdf.body("With both builds finally running, here's how well each year's results matched Brainpool's real forecast for that year, without changing any of the tuning:")
pdf.table(
    ["", "2027 (tuned for)", "2028 (never seen)", "2029 (never seen)"],
    [
        ["How closely they move together", "0.647", "0.446", "0.349"],
        ["Average error", "28.19", "28.71", "29.59"],
    ],
    [70, 40, 40, 40],
)
pdf.result(
    "Result: the average price level holds up well; the hour-to-hour rhythm gradually loses accuracy the further out you go.",
    "The 'average error' number barely moves across all three years - the model isn't "
    "drifting off in overall scale just because it's looking at an unfamiliar year. But the "
    "'how closely they move together' number drops steadily and noticeably each year further "
    "from 2027. In plain terms: teach the model the general shape of 2027's electricity "
    "market, and it still gets the BIG PICTURE right a year or two later - but its grasp of "
    "the exact hour-by-hour ups and downs gets a bit fuzzier the further it drifts from the "
    "year it was actually tuned on. This is a genuinely useful, honest result either way - a "
    "real limit worth knowing about, not a failure to hide.",
    color=NAVY,
)
pdf.analogy(
    "picture memorising a friend's weekly routine down to the hour - when they usually eat "
    "lunch, when they go for a run, when they're free for a call. A year later, you'd still "
    "correctly guess they're a 'morning person' or 'night owl' overall (the big picture holds "
    "up), but the exact hour they now eat lunch might have shifted, since routines drift over "
    "time even when the general character of the person hasn't changed."
)

# =====================================================================
# =====================================================================
pdf.h1("7. Would re-tuning the import amount fix the 2028/2029 gap?")
pdf.question("Would per-year recalibration recover the lost correlation?")
pdf.body(
    "A fair follow-up question after seeing 2028 and 2029's hour-to-hour matching come out "
    "weaker than 2027's: the import-volume number (30,000 megawatts) was originally tuned "
    "specifically for 2027 and never rechecked since. Could simply re-tuning that one number "
    "for each new year bring the matching quality back up?"
)
pdf.question("Yes, run that.")
pdf.body(
    "Rather than guess, the same tuning exercise used for 2027 (trying several different "
    "import amounts and checking which one matches Brainpool's real price best) was repeated "
    "for both 2028 and 2029."
)
pdf.result(
    "Big surprise: the answer flipped completely, and recovers a lot - but at a real cost.",
    "For 2027, MORE imported power gave a BETTER match. For 2028 and 2029, it's the exact "
    "opposite: LESS imported power gives a dramatically better match - taking the 'how "
    "closely do they move together' score from around 0.35-0.45 up to about 0.70. But that "
    "improvement comes from a trade: with less import available, the model runs out of power "
    "far more often (up to 116 hours a year, versus 1-8 today) - and Brainpool's own real "
    "forecast barely ever runs out of power at all. So this isn't a free win - it's swapping "
    "better hour-to-hour tracking for a less realistic overall picture.",
    color=NAVY,
)
pdf.question("...however, rebuild 2028 and 2029 with the V2 (2023 demand load) with import, let us see what the result will be.")
pdf.body(
    "One more idea worth ruling out at the same time: maybe it's not the import amount at "
    "all, but the choice to base demand on 2016 (picked earlier for matching 2009's weather) "
    "that's behind the weaker matching. So both years were rebuilt a second way - keeping "
    "everything else the same, but switching the demand shape back to the ORIGINAL recipe "
    "(based on real 2023 usage data) to see if that closes the gap instead."
)
pdf.result(
    "Result: the demand-year choice turns out to barely matter either way - a genuine dead end, ruled out cleanly.",
    "Switching back to the 2023-based demand shape moved the matching score by only a "
    "hair - very slightly worse for 2028, very slightly better for 2029 - nowhere near the "
    "size of the import-amount effect. In other words: the 2016 weather-matching choice made "
    "earlier was a reasonable one and isn't secretly hurting anything - the real story behind "
    "the weaker 2028/2029 matching is specifically about how much power is allowed to be "
    "imported, not about which year's usage pattern shapes the demand.",
    color=GOOD,
)
pdf.analogy(
    "picture tuning a thermostat to a house's exact insulation on a mild spring day, then "
    "assuming that same setting will keep the house comfortable in the dead of winter. The "
    "thermostat itself still works exactly the same way - the real question is just whether "
    "last spring's specific setting still makes sense for a very different season. That "
    "turned out to be the case here for the import amount specifically, not for the choice of "
    "which past year's usage pattern to borrow the demand shape from."
)

# =====================================================================
pdf.h1("8. Deciding to actually make the change")
pdf.question("Adopt the smaller ceiling for 2028 and 2029 anyway.")
pdf.body(
    "After seeing the trade-off (better hour-to-hour matching, but many more 'ran out of "
    "power' hours), the decision was made to go ahead with the smaller import amount for both "
    "years anyway. Between the two smallest options tested, 20,000 megawatts was picked over "
    "15,000 specifically: it gives almost exactly the same improvement in matching quality "
    "(barely any difference), while cutting the number of 'ran out of power' hours by more "
    "than half compared to going even smaller."
)
pdf.result(
    "This is now a real, permanent change - the first and only place in this whole project where a fix was deliberately un-done for a later year.",
    "Every other setting carried into 2028 and 2029 stayed exactly as originally tuned for "
    "2027 - only this one number was knowingly changed, and only after the trade-off was "
    "reported and a deliberate decision was made. The original (30,000 megawatt) results for "
    "both years are kept safely on file, side by side with the new ones, so nothing from "
    "before was lost or overwritten.",
    color=GOOD,
)

pdf.h1("Where This Leaves Us")
pdf.body(
    "A short but very productive day - one open question closed with a real measurement, two "
    "genuinely working new pieces added to the model, one honest 'checked, not adopted' "
    "finding, the model's first-ever test against years it wasn't built for, and one "
    "deliberate, flagged change finally adopted:"
)
for line in [
    "- Raising the shortage price to match today's real 5,000 EUR/MWh regulatory cap would "
    "very slightly IMPROVE the average-price comparison, but make the all-hours correlation "
    "number look worse - both explainable, neither acted on yet.",
    "- Hydrogen production (electrolysis) can now choose WHEN to use its electricity instead "
    "of drawing it flat every hour - verified to genuinely favour cheap and free/negative-"
    "price hours, specifically the midday sunny-hour surplus flagged earlier this project. "
    "Its effect on the main headline number was modest, though - mostly explained by fewer "
    "'ran out of power' hours rather than better ordinary-day tracking.",
    "- Electric-vehicle charging got the same smart-charging treatment, and did even better: "
    "the model now has ZERO hours all year where it runs out of power - the first time this "
    "whole project has reached that. Because there are no more extreme hours left to distort "
    "the picture, the improved match with Brainpool this time is a real, verified improvement "
    "in ordinary-day tracking, not an illusion caused by removing a few bad hours.",
    "- Small honest downside on the EV result: the average price came out very slightly "
    "further below Brainpool's than before, since shifting demand toward cheap hours nudges "
    "the yearly average down a touch even as the shape matches better.",
    "- The big battery/reservoir storage units were checked and found to already be genuinely "
    "price-driven by design - no fix needed there. But the reservoir hydro dam was found "
    "hitting its own size limit 35% of the year. Testing a bigger size showed a real, if "
    "modest, improvement that never fully disappears even at triple the size - and since the "
    "real size is Brainpool's own stated figure, this was kept as a documented finding rather "
    "than a change actually made to the model.",
    "- Checking WHERE the remaining gap sits confirmed the midday problem is still the "
    "dominant issue and barely moved despite two working demand-shifting fixes - strong "
    "evidence that the next real lever is the export project, not further demand-side "
    "tweaks.",
    "- A newly-noticed July-October seasonal gap was investigated: five specific, sensible "
    "explanations were checked and ruled out one by one. What's left points back to the same "
    "known limitation (our model only sees Germany; Brainpool's real tool watches roughly 30 "
    "countries at once) rather than a new, separately fixable problem.",
    "- The model was tested against 2028 and 2029 - years it was never tuned for - using "
    "Brainpool's newly-supplied data, with zero changes to any of the tuning. The average "
    "price level held up well in both years; the hour-to-hour rhythm gradually got fuzzier "
    "the further from 2027 (0.647 down to 0.446 down to 0.349). Along the way, a genuine "
    "limitation of the simulation software itself was discovered (it doesn't understand real "
    "leap years) and worked around cleanly.",
    "- Chasing that 2028/2029 gap further: re-tuning the import amount specifically for each "
    "year recovers a lot of the lost matching quality (up to 0.70), but only by accepting far "
    "more 'ran out of power' hours than Brainpool's own forecast ever shows. Switching the "
    "demand shape back to the original 2023-based recipe, by contrast, barely changed "
    "anything either way - ruling that out as the cause.",
    "- The decision was then made to actually adopt the smaller import amount (20,000 "
    "megawatts) for both years anyway, accepting the trade-off knowingly. This is the only "
    "place in the whole project where a 2027 setting was deliberately changed for a later "
    "year - done openly, with the original results kept safely alongside the new ones.",
]:
    pdf.set_x(MARGIN)
    pdf.multi_cell(0, 5.8, line)
pdf.ln(2)
pdf.body(
    "The full technical detail behind all of today's items - the exact hour-by-hour numbers "
    "used to test them - has also been folded into the main, more detailed progress report "
    "(AMIRIS_Germany2027_Progress_Report.pdf) as Phases 19 through 26."
)

pdf.output("AMIRIS_Session_2026-08-25.pdf")
print("Saved AMIRIS_Session_2026-08-25.pdf")
