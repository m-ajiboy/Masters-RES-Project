"""Builds AMIRIS_Progress_Update_Since_Aug27_2026-09-07.pptx: a standalone deck containing
ONLY the work done since the 27 August supervisor presentation, not the full project history.

Starts from a full copy of the continuously-updated comprehensive deck (guaranteeing every
kept slide - real charts, tables, wording - is byte-identical to the carefully-built original,
no re-transcription risk), then removes exactly the slides that were already presented on
27 August (confirmed by diffing against the actual original file,
Progress_Report_AMIRIS_2026-08-27.pptx, which has 22 slides ending at 'A Genuine Bug, Found
and Fixed' / 'Where We Stand Now' / 'The Overall Journey' / 'Next Steps' / 'Questions &
Discussion' - slides 1-18 of the current deck match that original's slides 1-18 exactly).
Retitles the title slide, replaces the agenda for the new scope, and adds a one-slide recap
for orientation.

IMPORTANT ordering rule, learned the hard way twice: every prs.slides.add_slide() call in
this script happens BEFORE any delete_slide() call. Adding a new slide AFTER deleting slides
caused python-pptx to reuse an internal part filename that collided with a still-present
slide, silently corrupting the saved file (confirmed directly via a 'Duplicate name' warning
at save time and a read-back showing one slide's real content replaced by another's, twice -
once for the recap slide, once again for the agenda slide before this was written as one
combined, correctly-ordered pass). All new slides are added and repositioned FIRST; only then
are the old slides deleted, in one final pass from the highest index down."""
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN
from pptx.enum.shapes import MSO_SHAPE

PATH = r"C:\Users\MuideenOA\Desktop\PyTut\Amiris\Presentation\AMIRIS_Progress_Update_Since_Aug27_2026-09-07.pptx"

NAVY = RGBColor(31, 58, 77)
AMBER = RGBColor(165, 105, 31)
GREY = RGBColor(90, 96, 92)
LIGHT = RGBColor(238, 240, 233)
GOOD = RGBColor(58, 107, 71)
BAD = RGBColor(150, 60, 40)
WHITE = RGBColor(255, 255, 255)

prs = Presentation(PATH)
SLIDE_W = prs.slide_width
SLIDE_H = prs.slide_height

print(f"Slides at start: {len(prs.slides)}")

BLANK = prs.slide_layouts[6]


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
    p.font.size = Pt(26)
    p.font.bold = True
    p.font.color.rgb = WHITE
    if subtitle:
        p2 = tf.add_paragraph()
        p2.text = subtitle
        p2.font.size = Pt(14)
        p2.font.color.rgb = RGBColor(200, 210, 218)
    add_page_number_placeholder(slide)
    return bar


def bullets(slide, items, left=0.55, top=1.35, width=12.2, height=5.8, size=18):
    box = slide.shapes.add_textbox(Inches(left), Inches(top), Inches(width), Inches(height))
    tf = box.text_frame
    tf.word_wrap = True
    for i, item in enumerate(items):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.text = "•  " + item
        p.font.size = Pt(size)
        p.font.bold = True
        p.font.color.rgb = RGBColor(30, 34, 32)
        p.space_after = Pt(10)
    return box


def move_last_slide_to(prs, index):
    xml_slides = prs.slides._sldIdLst
    slide_id_list = list(xml_slides)
    elem = slide_id_list[-1]
    xml_slides.remove(elem)
    xml_slides.insert(index, elem)


# ---------------------------------------------------------------------------
# STEP 1: add BOTH new slides (agenda replacement + quick recap) first, and
# position them, before touching any deletion. See module docstring for why.
# ---------------------------------------------------------------------------
agenda_slide = prs.slides.add_slide(BLANK)
header_bar(agenda_slide, "Agenda - Since 27 August")
bullets(agenda_slide, [
    "Quick recap: where we left off",
    "Out-of-sample testing and a genuine bug fix",
    "Three more ideas tested (price floor, cycling cost, lignite markup)",
    "The big build: real cross-border market coupling",
    "Extending to 2028 and 2029",
    "Chasing the last gap: four more real tests",
    "Where we stand now, and next steps",
])
move_last_slide_to(prs, 1)

recap_slide = prs.slides.add_slide(BLANK)
header_bar(recap_slide, "Quick Recap: Where We Left Off on 27 August",
           "For orientation - the full detail is in the comprehensive deck")
bullets(recap_slide, [
    "Built and validated AMIRIS against Brainpool's real 2027 forecast, diagnosing and fixing a genuine import-timing bug",
    "Refined demand modelling and fixed a real weekday/weekend calendar mismatch",
    "Added price-responsive electrolysis and e-mobility - the strongest result at the time, eliminating shortage hours entirely",
    "Correlation to Brainpool's forecast reached 0.647, up from 0.439 at the start of that work",
])
move_last_slide_to(prs, 2)

print(f"Slides after adding new agenda + recap: {len(prs.slides)}")
print("Order check (first 5):", [
    (s.shapes[0].text_frame.text[:40] if s.shapes and s.shapes[0].has_text_frame else "")
    for s in list(prs.slides)[:5]
])

# ---------------------------------------------------------------------------
# STEP 2: retitle slide 0 (title slide) - clear and rebuild cleanly rather
# than editing individual runs (editing runs[0] only left the REST of the
# original multi-run title text still appended, corrupting it last time).
# ---------------------------------------------------------------------------
title_slide = prs.slides[0]
for shape in title_slide.shapes:
    if shape.has_text_frame and "Evaluating AMIRIS" in shape.text_frame.text:
        tf = shape.text_frame
        tf.clear()
        p0 = tf.paragraphs[0]
        p0.text = "AMIRIS Progress Update"
        p0.font.size = Pt(36)
        p0.font.bold = True
        p0.font.color.rgb = WHITE  # title slide has a navy background - NAVY text was invisible
        p1 = tf.add_paragraph()
        p1.text = "What's Changed Since the 27 August Supervisor Meeting"
        p1.font.size = Pt(20)
        p1.font.italic = True
        p1.font.color.rgb = RGBColor(200, 210, 218)  # light enough to read on navy
    elif shape.has_text_frame and "Date:" in shape.text_frame.text and "27 August 2026" in shape.text_frame.text:
        for p in shape.text_frame.paragraphs:
            for run in p.runs:
                if "27 August 2026" in run.text:
                    run.text = run.text.replace("27 August 2026", "7 September 2026")

# ---------------------------------------------------------------------------
# STEP 3: delete the already-presented slides, ALL IN ONE FINAL PASS, from
# the highest index down so indices don't shift under us. After the two
# inserts above, the deck order is:
#   0 = title (edited in place)
#   1 = NEW agenda (keep)
#   2 = NEW quick recap (keep)
#   3 = OLD agenda (delete)
#   4..19 = OLD already-presented Part 1/2 content (delete) - 16 slides
#   20.. = genuinely new content since 27 August (keep)
# That is indices 3 through 19 inclusive = 17 slides to delete.
# ---------------------------------------------------------------------------
def delete_slide(prs, index):
    xml_slides = prs.slides._sldIdLst
    slides = list(xml_slides)
    rId = slides[index].rId
    prs.part.drop_rel(rId)
    xml_slides.remove(slides[index])


for idx in range(19, 2, -1):
    delete_slide(prs, idx)

new_count = len(prs.slides)
print(f"Final slide count: {new_count}")

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

prs.save(PATH)
print(f"Saved: {PATH}")
