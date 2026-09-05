"""Inserts 3 new slides into the supervisor deck, covering the cycling-cost investigation
(Phase 30) - a follow-up test after the price-floor dead end. Positioned right after the
existing "Result: Confirmed Dead End" floor-investigation slide, before "Where We Stand Now".
Preserves every existing slide and prior edits untouched."""
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN
from pptx.enum.shapes import MSO_SHAPE

ROOT = r"C:\Users\MuideenOA\Desktop\PyTut\Amiris"
PPTX_PATH = rf"{ROOT}\Presentation\Progress_Report_AMIRIS_2026-08-27_UPDATED.pptx"

NAVY = RGBColor(31, 58, 77)
AMBER = RGBColor(165, 105, 31)
GREY = RGBColor(90, 96, 92)
LIGHT = RGBColor(238, 240, 233)
GOOD = RGBColor(58, 107, 71)
BAD = RGBColor(150, 60, 40)
WHITE = RGBColor(255, 255, 255)

prs = Presentation(PPTX_PATH)
SLIDE_W = prs.slide_width
SLIDE_H = prs.slide_height
BLANK = prs.slide_layouts[6]

existing_count = len(prs.slides)
print(f"Existing slides: {existing_count}")


def new_slide():
    return prs.slides.add_slide(BLANK)


def add_page_number_placeholder(slide):
    box = slide.shapes.add_textbox(SLIDE_W - Inches(0.7), SLIDE_H - Inches(0.45), Inches(0.5), Inches(0.35))
    p = box.text_frame.paragraphs[0]
    p.text = "0"
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
    add_page_number_placeholder(slide)
    return bar


def bullets(slide, items, left=0.55, top=1.35, width=12.2, height=5.8, size=18, color=RGBColor(30, 34, 32)):
    box = slide.shapes.add_textbox(Inches(left), Inches(top), Inches(width), Inches(height))
    tf = box.text_frame
    tf.word_wrap = True
    for i, item in enumerate(items):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        text, lvl = item if isinstance(item, tuple) else (item, 0)
        p.text = ("•  " if lvl == 0 else "‒  ") + text
        p.font.size = Pt(size if lvl == 0 else size - 2)
        p.font.color.rgb = color if lvl == 0 else GREY
        p.space_after = Pt(10 if lvl == 0 else 6)
        p.font.bold = (lvl == 0)
    return box


def bullet_slide(title, items, subtitle=None):
    slide = new_slide()
    header_bar(slide, title, subtitle)
    bullets(slide, items)
    return slide


def big_stat_slide(title, stat, stat_label, items, subtitle=None):
    slide = new_slide()
    header_bar(slide, title, subtitle)
    box = slide.shapes.add_textbox(Inches(0.55), Inches(1.5), Inches(12.2), Inches(1.6))
    tf = box.text_frame
    p = tf.paragraphs[0]
    p.text = stat
    p.font.size = Pt(54)
    p.font.bold = True
    p.font.color.rgb = BAD
    p.alignment = PP_ALIGN.CENTER
    p2 = tf.add_paragraph()
    p2.text = stat_label
    p2.font.size = Pt(16)
    p2.font.italic = True
    p2.font.color.rgb = GREY
    p2.alignment = PP_ALIGN.CENTER
    bullets(slide, items, top=3.3, height=4.2)
    return slide


# =============================================================================
# 3 new slides: the cycling-cost investigation (Phase 30)
# =============================================================================

bullet_slide(
    "A Follow-Up Idea: Give Power Plants a Real Start-Up Cost",
    [
        "Our model goes negative far more often than Brainpool's real forecast (18-20% of hours vs. under 1%)",
        "Idea: real power plants incur a real cost to shut down and restart - so they sometimes prefer to keep running even at a negative price, rather than switch off",
        "Our model currently gives every plant a shut-down/restart cost of exactly zero - no real reason to avoid shutting off",
        "Unlike the price-cap idea, this is a genuine real-world mechanism, not an artificial adjustment - worth testing properly",
    ],
    subtitle="A genuine mechanism this time, not a cosmetic cap",
)

bullet_slide(
    "What We Did: Sourced a Real Number, Built a Real Test",
    [
        "Found a real, peer-reviewed study on actual power plant start-up costs (Nature Energy, 2017)",
        "Real figures: about EUR50,000-70,000 per start for a large coal/lignite plant, EUR60,000 for a gas plant",
        "Converted these into our model's units and applied them to every plant type",
        "Built this as its own separate model version and ran a full, real simulation - not a shortcut estimate",
    ],
)

big_stat_slide(
    "Result: Zero Difference - a Cleaner Dead End",
    "0 of 8,760 hours",
    "changed price, even by a single cent",
    [
        "The new setting made literally no difference to the result, at any point in the year",
        "Investigated why: the number IS calculated inside the program, but that calculation is never actually connected to the price the plant offers",
        "So this isn't a trade-off to weigh, like the price cap was - the switch simply isn't wired to anything in our version of the model",
        "Confirms: the cross-border export/market-coupling build remains the most promising next step",
    ],
)

new_count = len(prs.slides)
print(f"Slides after adding: {new_count} (added {new_count - existing_count})")

# ---------------------------------------------------------------------------
# Reorder: move the newly-added slides to right after the floor-investigation
# result slide (existing slide 26), before "Where We Stand Now" (existing 27).
# ---------------------------------------------------------------------------
xml_slides = prs.slides._sldIdLst
slide_id_list = list(xml_slides)
n_new = new_count - existing_count
new_slide_elements = slide_id_list[existing_count:]
insertion_index = 26  # 0-indexed: after existing slide 26

for elem in new_slide_elements:
    xml_slides.remove(elem)
for offset, elem in enumerate(new_slide_elements):
    xml_slides.insert(insertion_index + offset, elem)

print(f"Reordered: moved {n_new} new slides to position {insertion_index + 1}")

# ---------------------------------------------------------------------------
# Renumber every page-number textbox across the whole deck.
# ---------------------------------------------------------------------------
renumbered = 0
skipped_slides = []
for i, slide in enumerate(prs.slides, start=1):
    found = False
    for shape in slide.shapes:
        if shape.has_text_frame and shape.text_frame.text.strip().isdigit():
            if shape.left > SLIDE_W - Inches(1.3) and shape.top > SLIDE_H - Inches(0.9):
                shape.text_frame.paragraphs[0].runs[0].text = str(i)
                renumbered += 1
                found = True
                break
    if not found:
        skipped_slides.append(i)

print(f"Renumbered {renumbered} page-number boxes")
if skipped_slides:
    print(f"Slides with no matching page-number box found (left as-is): {skipped_slides}")

try:
    prs.save(PPTX_PATH)
    print(f"Saved (in place): {PPTX_PATH}")
except PermissionError:
    fallback = rf"{ROOT}\Presentation\Progress_Report_AMIRIS_2026-09-01_UPDATED.pptx"
    prs.save(fallback)
    print(f"Original file is open/locked - saved to a new file instead: {fallback}")
