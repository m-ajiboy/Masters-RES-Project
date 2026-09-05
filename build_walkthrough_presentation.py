"""Builds a broad, comprehensive walkthrough presentation covering every step taken from
24 August through 27 August 2026, based on the four daily session notes. Organized
chronologically by day. Separate, standalone deck from the supervisor progress-update deck."""
from pptx import Presentation
from pptx.util import Inches, Pt, Emu
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN
from pptx.enum.shapes import MSO_SHAPE
from PIL import Image

ROOT = r"C:\Users\MuideenOA\Desktop\PyTut\Amiris"

NAVY = RGBColor(31, 58, 77)
AMBER = RGBColor(165, 105, 31)
GREY = RGBColor(90, 96, 92)
LIGHT = RGBColor(238, 240, 233)
GOOD = RGBColor(58, 107, 71)
BAD = RGBColor(150, 60, 40)
WHITE = RGBColor(255, 255, 255)

SLIDE_W = Inches(13.333)
SLIDE_H = Inches(7.5)

prs = Presentation()
prs.slide_width = SLIDE_W
prs.slide_height = SLIDE_H
BLANK = prs.slide_layouts[6]
PAGE_NUM = [0]


def new_slide():
    PAGE_NUM[0] += 1
    return prs.slides.add_slide(BLANK)


def add_page_number(slide):
    box = slide.shapes.add_textbox(SLIDE_W - Inches(0.7), SLIDE_H - Inches(0.45), Inches(0.5), Inches(0.35))
    p = box.text_frame.paragraphs[0]
    p.text = str(PAGE_NUM[0])
    p.font.size = Pt(11)
    p.font.color.rgb = GREY


def header_bar(slide, title, subtitle=None):
    bar = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, SLIDE_W, Inches(1.05))
    bar.fill.solid()
    bar.fill.fore_color.rgb = NAVY
    bar.line.fill.background()
    tf = bar.text_frame
    tf.margin_left = Inches(0.4)
    tf.margin_top = Inches(0.08)
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = title
    p.font.size = Pt(26)
    p.font.bold = True
    p.font.color.rgb = WHITE
    if subtitle:
        p2 = tf.add_paragraph()
        p2.text = subtitle
        p2.font.size = Pt(13)
        p2.font.color.rgb = RGBColor(200, 210, 218)
    add_page_number(slide)
    return bar


def day_tag(slide, label, color):
    box = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0), Inches(1.05), Inches(2.4), Inches(0.32))
    box.fill.solid()
    box.fill.fore_color.rgb = color
    box.line.fill.background()
    tf = box.text_frame
    tf.margin_left = Inches(0.15)
    tf.margin_top = Inches(0.02)
    p = tf.paragraphs[0]
    p.text = label
    p.font.size = Pt(11)
    p.font.bold = True
    p.font.color.rgb = WHITE


def bullets(slide, items, left=0.55, top=1.55, width=12.2, height=5.6, size=17, color=RGBColor(30, 34, 32)):
    box = slide.shapes.add_textbox(Inches(left), Inches(top), Inches(width), Inches(height))
    tf = box.text_frame
    tf.word_wrap = True
    for i, item in enumerate(items):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        text, lvl = item if isinstance(item, tuple) else (item, 0)
        p.text = ("•  " if lvl == 0 else "‒  ") + text
        p.font.size = Pt(size if lvl == 0 else size - 2)
        p.font.color.rgb = color if lvl == 0 else GREY
        p.space_after = Pt(9 if lvl == 0 else 5)
        p.font.bold = (lvl == 0)
    return box


def picture_fit(slide, path, left, top, max_w, max_h):
    with Image.open(path) as im:
        iw, ih = im.size
    ratio = min(max_w / iw, max_h / ih)
    w, h = iw * ratio, ih * ratio
    x = left + (max_w - w) / 2
    y = top + (max_h - h) / 2
    slide.shapes.add_picture(path, Emu(int(x * 914400)), Emu(int(y * 914400)),
                              width=Emu(int(w * 914400)), height=Emu(int(h * 914400)))


def title_slide(title, subtitle_lines):
    slide = new_slide()
    bg = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, SLIDE_W, SLIDE_H)
    bg.fill.solid()
    bg.fill.fore_color.rgb = NAVY
    bg.line.fill.background()
    bg.shadow.inherit = False
    box = slide.shapes.add_textbox(Inches(0.9), Inches(2.2), Inches(11.5), Inches(2.2))
    tf = box.text_frame
    tf.word_wrap = True
    for i, line in enumerate(title.split("\n")):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.text = line
        p.font.size = Pt(32)
        p.font.bold = True
        p.font.color.rgb = WHITE
    box2 = slide.shapes.add_textbox(Inches(0.9), Inches(4.6), Inches(11.5), Inches(2.2))
    tf2 = box2.text_frame
    tf2.word_wrap = True
    for i, line in enumerate(subtitle_lines):
        p = tf2.paragraphs[0] if i == 0 else tf2.add_paragraph()
        p.text = line
        p.font.size = Pt(15)
        p.font.color.rgb = RGBColor(210, 217, 223)
        p.space_after = Pt(6)
    return slide


def day_divider(day_label, date_label, theme, color):
    slide = new_slide()
    bg = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, SLIDE_W, SLIDE_H)
    bg.fill.solid()
    bg.fill.fore_color.rgb = color
    bg.line.fill.background()
    bg.shadow.inherit = False
    box = slide.shapes.add_textbox(Inches(0.9), Inches(2.7), Inches(11.5), Inches(2.5))
    tf = box.text_frame
    p = tf.paragraphs[0]
    p.text = day_label
    p.font.size = Pt(18)
    p.font.color.rgb = RGBColor(245, 240, 230)
    p2 = tf.add_paragraph()
    p2.text = date_label
    p2.font.size = Pt(34)
    p2.font.bold = True
    p2.font.color.rgb = WHITE
    p3 = tf.add_paragraph()
    p3.text = theme
    p3.font.size = Pt(17)
    p3.font.italic = True
    p3.font.color.rgb = RGBColor(245, 240, 230)
    p3.space_before = Pt(14)
    add_page_number(slide)
    return slide


def bullet_slide(title, items, day="", color=NAVY, subtitle=None):
    slide = new_slide()
    header_bar(slide, title, subtitle)
    if day:
        day_tag(slide, day, color)
        bullets(slide, items, top=1.65)
    else:
        bullets(slide, items)
    return slide


def image_slide(title, image_path, caption=None, day="", color=NAVY, subtitle=None):
    slide = new_slide()
    header_bar(slide, title, subtitle)
    if day:
        day_tag(slide, day, color)
    top = 1.55 if day else 1.3
    max_h = 5.2 if caption else (5.5 if day else 5.7)
    picture_fit(slide, image_path, 0.5, top, 12.3, max_h)
    if caption:
        box = slide.shapes.add_textbox(Inches(0.5), Inches(6.75), Inches(12.3), Inches(0.6))
        p = box.text_frame.paragraphs[0]
        p.text = caption
        p.font.size = Pt(12.5)
        p.font.italic = True
        p.font.color.rgb = GREY
        p.alignment = PP_ALIGN.CENTER
    return slide


def table_slide(title, headers, rows, col_widths, day="", color=NAVY, subtitle=None):
    slide = new_slide()
    header_bar(slide, title, subtitle)
    if day:
        day_tag(slide, day, color)
    top = 1.75 if day else 1.4
    n_rows, n_cols = len(rows) + 1, len(headers)
    table_shape = slide.shapes.add_table(n_rows, n_cols, Inches(0.6), Inches(top), Inches(12.1), Inches(0.55 * n_rows))
    table = table_shape.table
    for i, w in enumerate(col_widths):
        table.columns[i].width = Inches(w)
    for c, htext in enumerate(headers):
        cell = table.cell(0, c)
        cell.text = htext
        cell.fill.solid()
        cell.fill.fore_color.rgb = NAVY
        for p in cell.text_frame.paragraphs:
            p.font.color.rgb = WHITE
            p.font.bold = True
            p.font.size = Pt(13.5)
            p.alignment = PP_ALIGN.CENTER
    for r, row in enumerate(rows, start=1):
        for c, val in enumerate(row):
            cell = table.cell(r, c)
            cell.text = str(val)
            cell.fill.solid()
            cell.fill.fore_color.rgb = LIGHT if r % 2 == 0 else WHITE
            for p in cell.text_frame.paragraphs:
                p.font.size = Pt(12.5)
                p.font.color.rgb = RGBColor(30, 34, 32)
                p.alignment = PP_ALIGN.CENTER
    return slide


DAY_COLORS = {
    "24": RGBColor(58, 107, 71),
    "25": RGBColor(165, 105, 31),
    "26": RGBColor(150, 60, 40),
    "27": RGBColor(42, 82, 130),
}

# =============================================================================
title_slide(
    "Detailed Walkthrough:\nGermany 2027 Model Validation, 24-27 August",
    [
        "Every step, finding, and fix - day by day",
        "Presented by: Muideen Oladayo Ajiboye (471583)",
        "Compiled from daily session notes, 24-27 August 2026",
    ],
)

bullet_slide("Agenda", [
    "Day 1 (24 Aug): Chasing the midday price gap",
    "Day 2 (25 Aug): Making demand smart, and the first out-of-sample tests",
    "Day 3 (26 Aug): Reconsidering a decision, and finding a real bug",
    "Day 4 (27 Aug): Presentation and deep-dive explanations",
    "Overall summary and next steps",
])

# =============================================================================
day_divider("DAY 1", "24 August 2026", "Chasing the Midday Price Gap", DAY_COLORS["24"])

bullet_slide("1. Does Heat-Pump Weather Timing Matter?", [
    "Question: would using real 2009 temperature (instead of a generic typical-year climate profile) for heat-pump demand change the result?",
    "Built and tested it directly",
    "Result: essentially no effect on the overall comparison",
    "Why: heat pumps are under 3% of total demand - too small a slice to move the whole picture, even if modelled perfectly",
], day="DAY 1 - 24 AUG", color=DAY_COLORS["24"])

bullet_slide("2. Diagnosing the Midday Price Gap", [
    "AMIRIS predicts noticeably lower prices than Brainpool specifically around midday",
    "Inspected one real midday hour, agent by agent, to find out why",
    "Finding 1: two renewable subsidy types behave differently under oversupply - one type switches off when prices crash, the other keeps running regardless",
    "Finding 2 (the bigger one): the model has no way to sell EXTRA power abroad - it can only import, never export",
    "When Germany produces more solar/wind than it needs, the only options are: switch off, fill batteries, or let the price crash",
], day="DAY 1 - 24 AUG", color=DAY_COLORS["24"])

bullet_slide("3. Attempting to Build an Export Option", [
    "Tried building a way for the model to sell surplus power abroad, using the closest available tool (built for battery-like devices)",
    "Kept as its own separate, clearly labelled test",
    "Result: it never activated once, in any of the 8,760 hours of the year",
    "Why: the tool only acts when there's an eventual payoff - a device that never sells anything back has no such payoff",
    "Confirmed as a real, structural limit - not a mistake, and not fixed that day",
], day="DAY 1 - 24 AUG", color=DAY_COLORS["24"])

bullet_slide("4. Verifying Assumptions Against Reality", [
    "Two of our biggest assumptions had never actually been confirmed - checked directly rather than continuing to guess",
    "Confirmed: Brainpool's real forecast IS built on real 2009 weather",
    "Found: Brainpool's real model covers ~30 European countries with price coupling - not just one neighbour (we had been using France alone)",
], day="DAY 1 - 24 AUG", color=DAY_COLORS["24"])

bullet_slide("5. A Fairer Stand-In for the Neighbouring Price", [
    "A full 30-country model is far too big a job to replicate",
    "Next best option: blended real prices from all 11 of Germany's actual neighbouring countries, instead of France alone",
    "Result: a small, genuine improvement - France's price alone wasn't wildly different from the 11-country blend to begin with",
], day="DAY 1 - 24 AUG", color=DAY_COLORS["24"])

bullet_slide("6. How Big a Job Would a Real Export Feature Be?", [
    "AMIRIS does have the real tools needed for two markets to trade in both directions",
    "A working example already exists showing how two markets can be connected",
    "But making real use of it means building an entire second, simplified country-model and connecting it properly",
    "Assessment: achievable in principle, but comparable in size to the work that went into the German side in the first place",
], day="DAY 1 - 24 AUG", color=DAY_COLORS["24"])

bullet_slide("7. Checking the Public-Holiday Angle", [
    "Idea: our weekday/weekend fix doesn't know that a Thursday might be a public holiday with much lower real usage",
    "Germany's real 2027 public holidays were checked directly against the price comparison",
    "First look was promising - but didn't hold up under closer checking (controlling for season, comparing against normal day-to-day variation)",
    "Result: a genuine null result - ruled out, not pursued further",
], day="DAY 1 - 24 AUG", color=DAY_COLORS["24"])

# =============================================================================
day_divider("DAY 2", "25 August 2026", "Making Demand Smart, and First Out-of-Sample Tests", DAY_COLORS["25"])

bullet_slide("8. Why 3,000 EUR/MWh for the Shortage Price?", [
    "Question: is this number arbitrary, or does it mean something real?",
    "Researched directly rather than assumed",
    "Confirmed: this is the real, legally-binding EU-wide price ceiling that applied across Europe's electricity markets from November 2017 to May 2022",
    "Our reference year (2019) sits right in the middle of that period - the number was correctly copied from a real regulatory fact",
    "Found: the real ceiling has since risen twice, to 5,000 EUR/MWh today - flagged as worth revisiting, not acted on immediately",
], day="DAY 2 - 25 AUG", color=DAY_COLORS["25"])

bullet_slide("9 & 10. Making Two Demand Pieces \"Smart\"", [
    "Hydrogen production (electrolysis) and EV charging used to draw power flat, every hour, regardless of price",
    "Rebuilt both as their own agents: same total electricity used across the year, but free to choose WHEN",
    "Electrolysis result: shortage hours fell from 4 to 1",
    "EV charging result: shortage hours reached ZERO for the first time in this whole project",
    "Verified directly: both genuinely shift toward cheap and negative-price hours, and specifically the midday sunny-hour surplus",
], day="DAY 2 - 25 AUG", color=DAY_COLORS["25"])

bullet_slide("11. Checking the Big Battery/Storage Units Too", [
    "Question: should these be made \"smart\" the same way?",
    "Checked first: they were already found to be genuinely price-driven by design - no fix needed",
    "But found: the reservoir hydro dam was hitting its own size limit 35% of the year",
    "Tested a bigger size: real, modest improvement, but never fully solves it even at triple the real size",
    "Since the real size is Brainpool's own stated figure, kept as a documented finding rather than a change made to the model",
], day="DAY 2 - 25 AUG", color=DAY_COLORS["25"])

image_slide(
    "12. Finding Out What's Left to Fix",
    rf"{ROOT}\correlation_breakdown_flexbuild.png",
    caption="Re-ran the 'where exactly does the mismatch happen' check on the best-yet model - the midday problem was still there, almost unchanged",
    day="DAY 2 - 25 AUG", color=DAY_COLORS["25"],
)

bullet_slide("13. A New Seasonal Puzzle, Investigated and Ruled Out", [
    "The same check also showed July-October prices consistently further off than any other time of year",
    "Five specific, sensible explanations were checked directly, one at a time: extra solar/wind, different renewable mix, cheaper imports, extra demand, plant maintenance",
    "All five ruled out",
    "What was actually found: Brainpool assumes a steady price climb through summer that our single-country model simply can't see",
    "Traced back to the same known limitation: our model only sees Germany; Brainpool's real tool watches ~30 countries at once",
], day="DAY 2 - 25 AUG", color=DAY_COLORS["25"])

bullet_slide("14. Testing on Years the Model Was Never Tuned For", [
    "New Brainpool data arrived, covering 2028 and 2029 too - a chance to test generalisation",
    "Built 2028 and 2029 the exact same way as 2027 - zero re-tuning of any setting",
    "Genuine surprise: the simulation software doesn't understand true leap years at all",
    "It always treats every year as exactly 365 days, and for a leap year skips December 31st instead of adding a day in February",
    "Every part of the 2028 build was adjusted to work the way the software actually expects",
], day="DAY 2 - 25 AUG", color=DAY_COLORS["25"])

image_slide(
    "15. First Out-of-Sample Result",
    rf"{ROOT}\Presentation\chart_outofsample_validation.png",
    caption="Average price level held up well in both new years; the hour-to-hour matching quality got fuzzier the further from 2027",
    day="DAY 2 - 25 AUG", color=DAY_COLORS["25"],
)

bullet_slide("16. Adopting a Smaller Import Amount", [
    "Question: would re-tuning the import amount specifically for each year recover the lost matching quality?",
    "Tested directly: YES, dramatically - smaller import amounts gave far better hour-to-hour matching for both new years",
    "Decision made: adopt a smaller amount (20,000 MW) for both 2028 and 2029",
    "The original (30,000 MW) results were kept fully on file, not deleted",
], day="DAY 2 - 25 AUG", color=DAY_COLORS["25"])

# =============================================================================
day_divider("DAY 3", "26 August 2026", "Reconsidering a Decision, and Finding a Real Bug", DAY_COLORS["26"])

image_slide(
    "17. A Fuller Check Changes the Picture",
    rf"{ROOT}\Presentation\chart_ceiling_tradeoff.png",
    caption="A third option (15,000 MW) was added, and this time the FULL year was checked, not just the 'ordinary hours only' view",
    day="DAY 3 - 26 AUG", color=DAY_COLORS["26"],
)

bullet_slide("18. Reversing Yesterday's Decision", [
    "The fuller check showed the smaller import amount makes the OVERALL picture worse, not better",
    "More unrealistic 'ran out of power' hours, and the average price badly overshoots Brainpool's real number (up to 53% too high)",
    "Decision: reverted both 2028 and 2029 back to the original 30,000 MW default",
    "All four tested amounts were kept on file - nothing thrown away, full evidence trail preserved",
    "This is exactly the kind of careful, evidence-first process this project has followed throughout",
], day="DAY 3 - 26 AUG", color=DAY_COLORS["26"])

image_slide(
    "19. A Genuine Surprise in the Weekday Pattern",
    rf"{ROOT}\Presentation\chart_weekday_bug.png",
    caption="Checking WHERE 2028/2029 disagreed with Brainpool most revealed real demand numbers with Friday too low, Sunday too high",
    day="DAY 3 - 26 AUG", color=DAY_COLORS["26"],
)

bullet_slide("20. The Root Cause: A Hidden Calendar Bug", [
    "Our demand shape borrows a real year's usage pattern (2016) and trims it to fit the target year",
    "2016 has one extra day (leap year) that has to be removed",
    "The day removed was February 29th - sitting in the MIDDLE of the year",
    "Removing a day from the middle quietly shifts every day after it by one weekday, for the rest of the year (84% of it)",
    "This had been sitting undetected in the project's main 2027 build since it was first built",
    "The fix: remove December 31st instead - the very END of the year, which disturbs nothing before it",
], day="DAY 3 - 26 AUG", color=DAY_COLORS["26"])

table_slide(
    "21. Result: A Clean, Genuine Improvement",
    ["", "2027", "2029"],
    [
        ["Matching quality - before fix", "0.647", "0.349"],
        ["Matching quality - after fix", "0.675", "0.446"],
        ["Average error - before fix", "28.19", "29.59"],
        ["Average error - after fix", "26.91", "29.14"],
    ],
    col_widths=[5.0, 3.4, 3.4],
    day="DAY 3 - 26 AUG", color=DAY_COLORS["26"],
    subtitle="Both matching quality AND average error improved together, with almost no downside",
)

bullet_slide("22. Double-Checking: Was the Ceiling Puzzle Actually the Bug?", [
    "Question: now that the calendar bug is fixed, does the import-amount pattern from Day 2/3 still show up?",
    "Re-ran the same import-amount comparison on the newly-fixed 2029 model",
    "Found: the exact same pattern as before - smaller amounts still give better matching, at the same shortage-hour cost",
    "Fixing the calendar bug gave every import-amount setting a small, genuine boost across the board",
    "Confirmed: these are two real, independent findings - not one mistake masquerading as two",
], day="DAY 3 - 26 AUG", color=DAY_COLORS["26"])

# =============================================================================
day_divider("DAY 4", "27 August 2026", "Presentation and Deep-Dive Explanations", DAY_COLORS["27"])

bullet_slide("23. Building the Supervisor Progress Presentation", [
    "Prepared a full progress-update slide deck covering the last-meeting tasks and everything done since",
    "Structured around: load profile comparisons, 2009 renewable profiles, the smart-demand fixes, out-of-sample testing, and the calendar bug",
    "Later expanded with four additional slides diving deeper into the 2028/2029 story and the bug fix, inserted directly into the already-edited deck without disturbing existing edits",
], day="DAY 4 - 27 AUG", color=DAY_COLORS["27"])

bullet_slide("24. Clarifying: Did We Really Get 2009 Offshore Wind Data?", [
    "Yes - pulled the same way as onshore wind and solar, from a real weather-simulation service",
    "The low match score reported earlier isn't a mistake in that work",
    "There was never a real reference profile for offshore wind to compare against in the first place - a data gap flagged since the very start of the project",
    "Comparing real 2009 weather against a generic placeholder naturally gives a low score - that's expected, not a failure",
], day="DAY 4 - 27 AUG", color=DAY_COLORS["27"])

bullet_slide("25. Clarifying: What Does \"Shaped With Suited Data\" Mean?", [
    "V1's problem: one generic household shape stretched to represent all of Germany's demand - caused an unrealistic evening spike",
    "V2's fix: four separate pieces, each built from the data that actually explains it",
    "Base demand: real historical grid data. Heat pumps: real temperature data. Electrolysis: a steady industrial pattern. EV charging: a typical daily charging curve",
    "Using the right kind of data for each piece, instead of forcing one shape to cover everything",
], day="DAY 4 - 27 AUG", color=DAY_COLORS["27"])

bullet_slide("26. Clarifying: Why 2016 as the Demand-Source Year?", [
    "We don't have real electricity usage data for 2009 itself",
    "But Brainpool's forecast IS built on real 2009 weather - confirmed directly",
    "So: find a year we DO have real usage data for, whose weather most resembled 2009's, and borrow its shape",
    "Checked every candidate year directly rather than guessing - 2016 was the genuine best match",
    "Our own two guesses (2023, then 2019) both turned out to be poor choices - 2023 was actually the worst match of all six years checked",
], day="DAY 4 - 27 AUG", color=DAY_COLORS["27"])

bullet_slide("27. Clarifying: The Three Correlation Numbers", [
    "All-hours: every single hour of the year - can be distorted by a handful of extreme hours",
    "Excluding-shortage (our main, trusted number): the same measurement, leaving out those rare emergency-price hours",
    "Weekday / weekend split: the same trusted number, split further into Monday-Friday and Saturday-Sunday",
    "This detailed split is what twice now has directly led to finding a real, fixable problem",
], day="DAY 4 - 27 AUG", color=DAY_COLORS["27"])

# =============================================================================
image_slide(
    "Overall Summary: The Full Journey",
    rf"{ROOT}\Presentation\chart_overall_progress.png",
    caption="From wildly divergent (7.6x too high, 16% shortage hours) to close to Brainpool's real forecast",
)

image_slide(
    "Overall Summary: Matching Quality Over Time",
    rf"{ROOT}\Presentation\chart_correlation_progression.png",
    caption="Every major fix, in order, and its effect on how closely AMIRIS tracks Brainpool's real price",
)

bullet_slide("What's Still Open", [
    "A full cross-border export model - the midday-price gap is the main remaining issue and needs this",
    "Whether to update the shortage price (3,000 EUR/MWh) to reflect today's real EU cap (5,000 EUR/MWh)",
    "Why the import ceiling behaves so differently across years - a real, still-unexplained pattern",
    "Continuing to fold every finding into the formal thesis documentation",
])

bullet_slide("Questions & Discussion", [])

prs.save(rf"{ROOT}\Presentation\AMIRIS_Detailed_Walkthrough_24-27Aug2026.pptx")
print("Saved AMIRIS_Detailed_Walkthrough_24-27Aug2026.pptx")
