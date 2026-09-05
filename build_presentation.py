"""Builds the supervisor progress-update presentation: tasks from the last meeting, and
everything done since then, up to and including the Feb-29 calendar bug fix."""
from pptx import Presentation
from pptx.util import Inches, Pt, Emu
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
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
    p.font.size = Pt(28)
    p.font.bold = True
    p.font.color.rgb = WHITE
    if subtitle:
        p2 = tf.add_paragraph()
        p2.text = subtitle
        p2.font.size = Pt(14)
        p2.font.color.rgb = RGBColor(200, 210, 218)
    add_page_number(slide)
    return bar


def bullets(slide, items, left=0.55, top=1.35, width=12.2, height=5.8, size=18, color=RGBColor(30, 34, 32)):
    box = slide.shapes.add_textbox(Inches(left), Inches(top), Inches(width), Inches(height))
    tf = box.text_frame
    tf.word_wrap = True
    for i, item in enumerate(items):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        if isinstance(item, tuple):
            text, lvl = item
        else:
            text, lvl = item, 0
        p.text = ("•  " if lvl == 0 else "‒  ") + text
        p.level = 0
        p.font.size = Pt(size if lvl == 0 else size - 2)
        p.font.color.rgb = color if lvl == 0 else GREY
        p.space_after = Pt(10 if lvl == 0 else 6)
        p.font.bold = (lvl == 0)
        if lvl == 1:
            p.font.bold = False
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

    box = slide.shapes.add_textbox(Inches(0.9), Inches(2.3), Inches(11.5), Inches(2.2))
    tf = box.text_frame
    tf.word_wrap = True
    for i, line in enumerate(title.split("\n")):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.text = line
        p.font.size = Pt(36)
        p.font.bold = True
        p.font.color.rgb = WHITE

    box2 = slide.shapes.add_textbox(Inches(0.9), Inches(4.7), Inches(11.5), Inches(2.2))
    tf2 = box2.text_frame
    tf2.word_wrap = True
    for i, line in enumerate(subtitle_lines):
        p = tf2.paragraphs[0] if i == 0 else tf2.add_paragraph()
        p.text = line
        p.font.size = Pt(16)
        p.font.color.rgb = RGBColor(210, 217, 223)
        p.space_after = Pt(6)
    return slide


def section_divider(number, title):
    slide = new_slide()
    bg = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, SLIDE_W, SLIDE_H)
    bg.fill.solid()
    bg.fill.fore_color.rgb = AMBER
    bg.line.fill.background()
    bg.shadow.inherit = False
    box = slide.shapes.add_textbox(Inches(0.9), Inches(3.0), Inches(11.5), Inches(1.5))
    tf = box.text_frame
    p = tf.paragraphs[0]
    p.text = number
    p.font.size = Pt(20)
    p.font.color.rgb = RGBColor(250, 235, 215)
    p2 = tf.add_paragraph()
    p2.text = title
    p2.font.size = Pt(34)
    p2.font.bold = True
    p2.font.color.rgb = WHITE
    add_page_number(slide)
    return slide


def bullet_slide(title, items, subtitle=None):
    slide = new_slide()
    header_bar(slide, title, subtitle)
    bullets(slide, items)
    return slide


def image_slide(title, image_path, caption=None, subtitle=None):
    slide = new_slide()
    header_bar(slide, title, subtitle)
    top = 1.3
    max_h = 5.7 if not caption else 5.2
    picture_fit(slide, image_path, 0.5, top, 12.3, max_h)
    if caption:
        box = slide.shapes.add_textbox(Inches(0.5), Inches(6.75), Inches(12.3), Inches(0.6))
        p = box.text_frame.paragraphs[0]
        p.text = caption
        p.font.size = Pt(13)
        p.font.italic = True
        p.font.color.rgb = GREY
        p.alignment = PP_ALIGN.CENTER
    return slide


def bullets_and_image(title, items, image_path, subtitle=None):
    slide = new_slide()
    header_bar(slide, title, subtitle)
    bullets(slide, items, left=0.5, top=1.35, width=5.6, height=5.7, size=15)
    picture_fit(slide, image_path, 6.3, 1.35, 6.5, 5.7)
    return slide


def table_slide(title, headers, rows, col_widths=None, subtitle=None):
    slide = new_slide()
    header_bar(slide, title, subtitle)
    n_rows = len(rows) + 1
    n_cols = len(headers)
    left, top, width, height = Inches(0.5), Inches(1.4), Inches(12.3), Inches(0.55 * n_rows)
    table_shape = slide.shapes.add_table(n_rows, n_cols, left, top, width, height)
    table = table_shape.table
    if col_widths:
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
            p.font.size = Pt(14)
            p.alignment = PP_ALIGN.CENTER
    for r, row in enumerate(rows, start=1):
        for c, val in enumerate(row):
            cell = table.cell(r, c)
            cell.text = str(val)
            cell.fill.solid()
            cell.fill.fore_color.rgb = LIGHT if r % 2 == 0 else WHITE
            for p in cell.text_frame.paragraphs:
                p.font.size = Pt(13)
                p.font.color.rgb = RGBColor(30, 34, 32)
                p.alignment = PP_ALIGN.CENTER
    return slide


# =============================================================================
# BUILD THE DECK
# =============================================================================

title_slide(
    "Progress Update: AMIRIS vs. Brainpool\nGermany 2027 Electricity Price Model",
    [
        "Supervisor: Rohith Krishnan Bala Krishnan",
        "Presented by: Muideen Oladayo Ajiboye (471583)",
        "Date: 27 August 2026",
    ],
)

bullet_slide("Agenda", [
    "Tasks from the last meeting - status update",
    "What we've done since: building, testing, and validating the Germany 2027 model",
    "Where things stand now",
    "Next steps",
])

# ---- Tasks from last meeting ----
section_divider("PART 1", "Tasks From the Last Meeting")

bullet_slide("Three Tasks From Last Time", [
    "1.  Submit the filled thesis form for endorsement",
    "2.  Load profile comparisons - AMIRIS vs. our different model versions, with charts",
    "3.  Rebuild the 2009 renewable weather profiles",
])

bullet_slide("Task 1: Thesis Form", [
    "Administrative item - status to confirm at this meeting",
])

image_slide(
    "Task 2: Load Profile Comparison",
    rf"{ROOT}\amiris_v1_v2_load_comparison.png",
    caption="AMIRIS's own reference profile vs. V1 (single household-shape demand) vs. V2 (component-split demand)",
)

bullets_and_image(
    "Task 2: What the Comparison Showed",
    [
        "V1 (one shape for all demand): peak too high, unrealistic evening spike",
        "V2 (split into 4 real components): much closer to AMIRIS's own real reference shape",
        "This finding directly motivated switching the whole project to V2",
        "V2 became the foundation for everything that followed",
    ],
    rf"{ROOT}\amiris_v1_v2_load_comparison.png",
)

image_slide(
    "Task 3: 2009 Renewable Weather Profiles",
    rf"{ROOT}\renewable_profile_2009_vs_original.png",
    caption="Real 2009 weather (renewables.ninja) vs. our original profiles - one week detail + full-year duration curves",
)

bullet_slide("Task 3: What We Found", [
    "Brainpool's forecast is built on real 2009 weather - confirmed directly from their published methodology",
    "Rebuilt wind & solar using real 2009 weather data",
    ("Onshore wind and solar: strongly correlated with our original profiles (r = 0.90 and 0.97)", 1),
    ("Offshore wind: no real correlation (r = 0.01) - a genuine, separate gap", 1),
    "This 2009 weather basis was later reused for heat-pump temperature too",
])

# ---- What we've done since ----
section_divider("PART 2", "What We've Done Since")

bullet_slide("The Big Picture", [
    "Built a full AMIRIS model of Germany's 2027 electricity market, from Brainpool's real input data",
    "Compared it hour-by-hour against Brainpool's own real 2027 price forecast",
    "Diagnosed and fixed the gap, one verified step at a time",
    "Tested whether the fixes hold up on years we never tuned for (2028, 2029)",
    "Found and fixed a genuine bug along the way",
])

bullet_slide("Building the Model (V1 -> V2)", [
    "V1: one household-shaped demand curve for all of Germany's electricity use",
    "V2: split demand into 4 real components - base load, heat pumps, electrolysis, e-mobility",
    "Each component shaped using the real data suited to it",
    "Result: shortage hours (the model 'running out of power') fell from 15.9% to 7.5% of the year",
])

image_slide(
    "Fixing the Import Mechanism",
    rf"{ROOT}\ppt_chart_diagnosis.png",
    caption="Diagnosed directly: 64% of shortage hours had ZERO import available - import timing was copied from an unrelated year",
)

bullet_slide("Verifying Our Assumptions Against Reality", [
    "Rather than assume, we checked Brainpool's real published methodology directly",
    "Confirmed: 2009 weather year - correct",
    "Confirmed: Brainpool's real model covers ~30 European countries with price coupling, not one neighbour",
    "Rebuilt our import price as a blend of 11 real neighbouring countries instead of France alone",
    "Result: a small, genuine improvement",
])

bullet_slide("Making Demand \"Smart\"", [
    "Hydrogen production (electrolysis) and EV charging used to draw power flat, every hour",
    "Rebuilt both as price-responsive: they now choose WHEN to draw power",
    "Verified directly: both shift toward cheap and negative-price hours",
    "EV charging result: shortage hours reached ZERO for the first time this project",
    "This is the strongest single result in this whole line of work",
])

image_slide(
    "The Correlation Journey",
    rf"{ROOT}\Presentation\chart_correlation_progression.png",
    caption="How closely AMIRIS tracks Brainpool's real 2027 price, step by step, from initial calibration to the final fix",
)

image_slide(
    "Testing Years We Never Tuned For",
    rf"{ROOT}\Presentation\chart_outofsample_validation.png",
    caption="Built 2028 and 2029 the same way as 2027, with zero re-tuning, using Brainpool's newly-supplied multi-year data",
)

bullet_slide("A Genuine Bug, Found and Fixed", [
    "Checking WHERE 2028/2029 disagreed with Brainpool most revealed a real calendar bug",
    "Our demand shape borrows a real year's usage pattern (2016) and trims it to fit the target year",
    "The trimming method silently misaligned the days of the week for 84% of the year",
    "Present in our main model since it was first built - only now discovered and fixed",
    "Clean result: both 2027 and 2029 improved on accuracy AND average error, with no downside",
])

table_slide(
    "Where We Stand Now",
    ["Build", "Shortage hours", "Mean price", "vs. Brainpool's real 68.04"],
    [
        ["V1, no import", "15.88%", "519 EUR/MWh", "7.6x too high"],
        ["V1, final", "0.83%", "75 EUR/MWh", "almost exact"],
        ["V2, no import", "7.52%", "286 EUR/MWh", "4.2x too high"],
        ["V2, final (all fixes)", "0.02%", "56 EUR/MWh", "close, slightly below"],
    ],
    col_widths=[4.0, 2.7, 2.7, 3.0],
)

image_slide(
    "The Overall Journey",
    rf"{ROOT}\Presentation\chart_overall_progress.png",
    caption="From wildly divergent (7.6x too high, 16% shortage hours) to close to Brainpool's real forecast",
)

bullet_slide("Next Steps", [
    "Decide whether to pursue a full cross-border export model (a large undertaking) - the midday-price gap is the main remaining issue and needs this",
    "Consider whether to update the shortage price (3,000 EUR/MWh) to reflect today's real EU cap (5,000 EUR/MWh)",
    "Investigate WHY the import ceiling behaves differently across years - a real, still-unexplained pattern",
    "Continue folding all findings into the formal thesis documentation",
])

bullet_slide("Questions & Discussion", [])

prs.save(rf"{ROOT}\Presentation\Progress_Report_AMIRIS_2026-08-27.pptx")
print("Saved Progress_Report_AMIRIS_2026-08-27.pptx")
