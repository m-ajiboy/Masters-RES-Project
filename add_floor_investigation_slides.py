"""Inserts 4 new slides into the supervisor deck, covering the negative-price-floor
investigation (Phase 29) - the supervisor's own suggestion to test a price floor as a cheaper
alternative to full market coupling. Positioned right after the existing "Result: A Clean,
Genuine Improvement" slide (slide 22, the calendar-bug-fix result), before "Where We Stand
Now" (slide 23) - the same position pattern used for the earlier 2028/2029 slide insertion.
Preserves every existing slide and prior edits untouched."""
from pptx import Presentation
from pptx.util import Inches, Pt, Emu
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN
from pptx.enum.shapes import MSO_SHAPE
from PIL import Image

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


def table_slide(title, headers, rows, col_widths, subtitle=None, note=None):
    slide = new_slide()
    header_bar(slide, title, subtitle)
    n_rows, n_cols = len(rows) + 1, len(headers)
    table_shape = slide.shapes.add_table(n_rows, n_cols, Inches(0.7), Inches(1.5), Inches(11.9), Inches(0.55 * n_rows))
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
            p.font.size = Pt(14)
            p.alignment = PP_ALIGN.CENTER
    for r, row in enumerate(rows, start=1):
        for c, val in enumerate(row):
            cell = table.cell(r, c)
            cell.text = str(val)
            cell.fill.solid()
            is_last = (r == len(rows))
            cell.fill.fore_color.rgb = LIGHT if r % 2 == 0 else WHITE
            for p in cell.text_frame.paragraphs:
                p.font.size = Pt(13)
                p.font.color.rgb = BAD if (c > 0 and is_last) else RGBColor(30, 34, 32)
                p.font.bold = is_last
                p.alignment = PP_ALIGN.CENTER
    if note:
        box = slide.shapes.add_textbox(Inches(0.7), Inches(1.5 + 0.55 * n_rows + 0.2), Inches(11.9), Inches(1.0))
        p = box.text_frame.paragraphs[0]
        p.text = note
        p.font.size = Pt(13)
        p.font.italic = True
        p.font.color.rgb = GREY
    return slide


# =============================================================================
# 4 new slides: the negative-price-floor investigation (Phase 29)
# =============================================================================

bullet_slide(
    "A Cheaper Idea First: Can We Just Cap How Negative Price Goes?",
    [
        "Before committing to the much bigger cross-border export/market-coupling build, tested a smaller idea first",
        "Our model reports very negative prices in summer (too much solar/wind) far more often than Brainpool's real forecast does",
        "Question: what if we simply limited how negative AMIRIS is allowed to report a price - would that alone close some of the correlation gap?",
        "First step: check whether this is even something we can configure",
    ],
    subtitle="A supervisor-suggested quick test, before the bigger investment",
)

bullet_slide(
    "What We Found: The Floor Already Exists - Inside AMIRIS Itself",
    [
        "Opened up AMIRIS's actual underlying program (not just our settings file) to check",
        "Found AMIRIS already has a hard limit: -500 EUR/MWh, built directly into the program's core",
        "This isn't arbitrary - it matches the real limit used by Europe's actual electricity exchanges",
        "It is NOT something we can change from our scenario settings - changing it means editing and rebuilding AMIRIS's own program, a much bigger step",
        "So a smaller, faster test was run first: adjust the REPORTED price after the fact, purely to see if a different limit was even worth the bigger effort",
    ],
)

image_slide(
    "Testing Every Floor From -500 to +100 EUR/MWh",
    rf"{ROOT}\Presentation\floor_sweep_correlation.png",
    caption="Top: match quality (correlation) barely moves across most of the range, then gets worse. Bottom: average price gap improves toward the floor, then overshoots badly past about +30.",
)

table_slide(
    "Result: Confirmed Dead End - Including the Suggested +10 EUR/MWh",
    ["", "2027", "2028", "2029"],
    [
        ["Current model (no cap)", "0.515", "0.394", "0.475"],
        ["Best negative cap found (-50)", "0.515", "0.396", "0.475"],
        ["Cap at +10 EUR/MWh (tested directly)", "0.444", "0.354", "0.461"],
        ["Cap at +100 EUR/MWh", "0.096", "0.100", "0.396"],
    ],
    col_widths=[5.2, 3.0, 3.0, 3.0],
    subtitle="Match-quality score (correlation) for each cap tested - higher is better",
    note="No cap value, in either direction, improves match quality - a real, capped result at +10 makes it clearly worse. "
         "Confirmed: the bigger cross-border export/market-coupling build remains the most promising next step.",
)

new_count = len(prs.slides)
print(f"Slides after adding: {new_count} (added {new_count - existing_count})")

# ---------------------------------------------------------------------------
# Reorder: move the newly-added slides (currently at the end) to right after
# existing slide 22 ("Result: A Clean, Genuine Improvement"), before slide 23
# ("Where We Stand Now"), i.e. new index 22 (0-indexed) / position 23.
# ---------------------------------------------------------------------------
xml_slides = prs.slides._sldIdLst
slide_id_list = list(xml_slides)
n_new = new_count - existing_count
new_slide_elements = slide_id_list[existing_count:]
insertion_index = 22  # 0-indexed: after existing slide 22

for elem in new_slide_elements:
    xml_slides.remove(elem)
for offset, elem in enumerate(new_slide_elements):
    xml_slides.insert(insertion_index + offset, elem)

print(f"Reordered: moved {n_new} new slides to position {insertion_index + 1}")

# ---------------------------------------------------------------------------
# Renumber every page-number textbox across the whole deck to match final order.
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
