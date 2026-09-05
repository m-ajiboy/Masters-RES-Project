"""Inserts 4 new slides into the user's already-edited presentation, expanding on the
2028/2029 out-of-sample test and the correlation-recovery bug fix - positioned right after
the existing brief "A Genuine Bug, Found and Fixed" slide (slide 18), before "Where We Stand
Now" (slide 19). Preserves every existing slide and the user's own edits untouched."""
from pptx import Presentation
from pptx.util import Inches, Pt, Emu
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN
from pptx.enum.shapes import MSO_SHAPE
from PIL import Image
import copy

ROOT = r"C:\Users\MuideenOA\Desktop\PyTut\Amiris"
PPTX_PATH = rf"{ROOT}\Presentation\Progress_Report_AMIRIS_2026-08-27.pptx"

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


def picture_fit(slide, path, left, top, max_w, max_h):
    with Image.open(path) as im:
        iw, ih = im.size
    ratio = min(max_w / iw, max_h / ih)
    w, h = iw * ratio, ih * ratio
    x = left + (max_w - w) / 2
    y = top + (max_h - h) / 2
    slide.shapes.add_picture(path, Emu(int(x * 914400)), Emu(int(y * 914400)),
                              width=Emu(int(w * 914400)), height=Emu(int(h * 914400)))


def image_slide(title, image_path, caption=None, subtitle=None):
    slide = new_slide()
    header_bar(slide, title, subtitle)
    max_h = 5.7 if not caption else 5.2
    picture_fit(slide, image_path, 0.5, 1.3, 12.3, max_h)
    if caption:
        box = slide.shapes.add_textbox(Inches(0.5), Inches(6.75), Inches(12.3), Inches(0.6))
        p = box.text_frame.paragraphs[0]
        p.text = caption
        p.font.size = Pt(13)
        p.font.italic = True
        p.font.color.rgb = GREY
        p.alignment = PP_ALIGN.CENTER
    return slide


def bullet_slide(title, items, subtitle=None):
    slide = new_slide()
    header_bar(slide, title, subtitle)
    bullets(slide, items)
    return slide


def table_slide(title, headers, rows, col_widths, subtitle=None):
    slide = new_slide()
    header_bar(slide, title, subtitle)
    n_rows, n_cols = len(rows) + 1, len(headers)
    table_shape = slide.shapes.add_table(n_rows, n_cols, Inches(0.7), Inches(1.6), Inches(11.9), Inches(0.6 * n_rows))
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
            p.font.size = Pt(15)
            p.alignment = PP_ALIGN.CENTER
    for r, row in enumerate(rows, start=1):
        for c, val in enumerate(row):
            cell = table.cell(r, c)
            cell.text = str(val)
            cell.fill.solid()
            cell.fill.fore_color.rgb = LIGHT if r % 2 == 0 else WHITE
            for p in cell.text_frame.paragraphs:
                p.font.size = Pt(14)
                p.font.color.rgb = GOOD if (c > 0 and r == len(rows)) else RGBColor(30, 34, 32)
                p.font.bold = (r == len(rows))
                p.alignment = PP_ALIGN.CENTER
    return slide


# =============================================================================
# 4 new slides: deeper dive into the 2028/2029 test and the correlation recovery
# =============================================================================

bullet_slide(
    "Out-of-Sample Testing: What We Found",
    [
        "Built Germany 2028 and 2029 the exact same way as 2027 - zero re-tuning of any setting",
        "Goal: does the model still work on years it wasn't built for?",
        "Price LEVEL held up well in both new years (average price, average error stayed close)",
        "But hour-to-hour matching quality dropped the further from 2027:",
        ("2027 (tuned for): r = 0.647", 1),
        ("2028 (never tuned for): r = 0.446", 1),
        ("2029 (never tuned for): r = 0.349", 1),
        "This gap became the focus of the next round of investigation",
    ],
    subtitle="Using Brainpool's newly-supplied 2027-2029 data file",
)

image_slide(
    "How We Found the Cause",
    rf"{ROOT}\Presentation\chart_weekday_bug.png",
    caption="Real electricity demand should be highest on weekdays, lowest on Sunday - our model's 2029 demand had this backwards on two days",
)

bullet_slide(
    "The Root Cause: A Hidden Calendar Bug",
    [
        "Our demand shape borrows a real year's usage pattern (2016) and trims it to fit the target year",
        "2016 has one extra day (leap year) that must be removed to fit a normal year",
        "The extra day removed was February 29th - sitting in the MIDDLE of the year",
        "Removing a day from the middle silently shifts every day after it by one weekday, for the rest of the year (10 of 12 months)",
        "This bug had been present in our main 2027 model since it was first built - only found now",
        "The fix: remove December 31st instead - it sits at the END of the year, so nothing after it is disturbed",
    ],
)

table_slide(
    "Result: A Clean, Genuine Improvement",
    ["", "2027", "2029"],
    [
        ["Correlation - before fix", "0.647", "0.349"],
        ["Correlation - after fix", "0.675", "0.446"],
        ["Average error - before fix", "28.19", "29.59"],
        ["Average error - after fix", "26.91", "29.14"],
        ["Improvement", "Both up together", "Both up together"],
    ],
    col_widths=[5.0, 3.4, 3.4],
    subtitle="Both accuracy AND average error improved together, with almost no downside - a genuine bug fix, not a trade-off",
)

new_count = len(prs.slides)
print(f"Slides after adding: {new_count} (added {new_count - existing_count})")

# ---------------------------------------------------------------------------
# Reorder: move the newly-added slides (currently at the end) to right after
# the existing slide 18 ("A Genuine Bug, Found and Fixed"), i.e. new index 18
# (0-indexed) / position 19.
# ---------------------------------------------------------------------------
xml_slides = prs.slides._sldIdLst
slide_id_list = list(xml_slides)
n_new = new_count - existing_count
new_slide_elements = slide_id_list[existing_count:]  # the ones just added, at the end
insertion_index = 18  # 0-indexed: after existing slide 18 ("A Genuine Bug, Found and Fixed")

for elem in new_slide_elements:
    xml_slides.remove(elem)
for offset, elem in enumerate(new_slide_elements):
    xml_slides.insert(insertion_index + offset, elem)

print(f"Reordered: moved {n_new} new slides to position {insertion_index + 1}")

# ---------------------------------------------------------------------------
# Renumber every page-number textbox (bare-digit textboxes) across the whole
# deck to match final slide order.
# ---------------------------------------------------------------------------
renumbered = 0
skipped_slides = []
for i, slide in enumerate(prs.slides, start=1):
    found = False
    for shape in slide.shapes:
        if shape.has_text_frame and shape.text_frame.text.strip().isdigit():
            # Only treat it as a page number if it sits in the bottom-right corner,
            # matching where add_page_number_placeholder puts it.
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
    fallback = rf"{ROOT}\Presentation\Progress_Report_AMIRIS_2026-08-27_UPDATED.pptx"
    prs.save(fallback)
    print(f"Original file is open/locked - saved to a new file instead: {fallback}")
