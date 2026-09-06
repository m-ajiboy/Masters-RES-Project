"""Inserts new slides covering Phase 41-43 into the supervisor deck: the ROE storage
depletion test (ruled out), the France-only pilot (a real dead end with a clear cause), and
the full 10-zone disaggregation (a genuine engine bug found and fixed, and a more nuanced
result than predicted). Positioned after the existing "Where This Leaves Us" slide (41,
closing out the Phase 34-40 arc) and before "Where We Stand Now" (42). Follows the exact
same header_bar/bullets/table_slide/big_stat_slide helper pattern and raw XML _sldIdLst
insertion technique used in every prior slide-addition script this project."""
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
            p.font.size = Pt(13)
            p.alignment = PP_ALIGN.CENTER
    for r, row in enumerate(rows, start=1):
        for c, val in enumerate(row):
            cell = table.cell(r, c)
            cell.text = str(val)
            cell.fill.solid()
            cell.fill.fore_color.rgb = LIGHT if r % 2 == 0 else WHITE
            for p in cell.text_frame.paragraphs:
                p.font.size = Pt(12)
                p.font.color.rgb = RGBColor(30, 34, 32)
                p.font.bold = (c == 0)
                p.alignment = PP_ALIGN.CENTER
    if note:
        box = slide.shapes.add_textbox(Inches(0.7), Inches(1.5 + 0.55 * n_rows + 0.2), Inches(11.9), Inches(1.2))
        p = box.text_frame.paragraphs[0]
        p.text = note
        p.font.size = Pt(13)
        p.font.italic = True
        p.font.color.rgb = GREY
    return slide


def bullet_slide(title, items, subtitle=None):
    slide = new_slide()
    header_bar(slide, title, subtitle)
    bullets(slide, items)
    return slide


# =============================================================================
# New slides: Phase 41 (ROE storage), Phase 42 (France pilot), Phase 43 (full disaggregation)
# =============================================================================

bullet_slide(
    "One More Lead: Could the Other Side's Own Storage Explain the Gap?",
    [
        "The one open thread from before: a small number of extreme hours where Germany imports less than it could, even with spare capacity available",
        "Tested directly using data already on hand: is the rest of Europe's own storage running physically empty during those hours?",
        "Checked both battery-style storage and reservoir hydro on the other side of the border - neither ever comes close to its own physical limit, in either year tested",
        "Rules out 'the other side simply has nothing left to give' - strengthens the case that the real limiter is inside the model's own internal trading logic, not a real-world capacity constraint anywhere",
    ],
    subtitle="A real, testable idea - checked and ruled out",
)

bullet_slide(
    "Pushing Further: Replacing the Combined Zone With a Real Named Country",
    [
        "Everything so far treated 'the rest of Europe' as one combined stand-in - the next real question: does splitting out a real neighbour by name do any better?",
        "Chose France as the test case: the largest single economy involved, and the one country with enough real, already-sourced data to build immediately",
        "Built it properly: France's own real power plants, real demand, real weather-driven renewables, and a real border link to Germany - not a shortcut",
    ],
    subtitle="Testing whether more realism helps, or whether the combined approach was already the right call",
)

table_slide(
    "Result: A Real Step Backward - With a Clear, Understood Reason",
    ["", "Combined zone (best result)", "France split out separately"],
    [
        ["'Ran out of power' hours", "7", "167"],
        ["Average price gap on ordinary days", "-2.90", "+9.65"],
    ],
    col_widths=[5.4, 4.0, 4.0],
    subtitle="Splitting France out on its own made things worse, not better",
    note="Real, checked reason: France's own huge nuclear fleet used to help keep the WHOLE combined pool well-supplied. Pulled out on its own, the remaining combined zone lost that cushion and became genuinely short more often - while France's own surplus, now only linked directly to Germany by a narrow border, couldn't reach the rest of Europe to help there either.",
)

bullet_slide(
    "Going All the Way: All 10 Real Neighbouring Countries at Once",
    [
        "Since one real country made things worse for a clear, understood reason, the natural next test: does the SAME problem get worse - or does something different happen - once every real neighbour is split out?",
        "Built all 10 real countries as their own separate zones - the largest build of the whole project",
        "Hit a genuine, hard technical bug along the way: the model's own dispatch engine broke down for one specific country (Denmark) - traced directly to Denmark's real hydro power being far too small in absolute terms for the model to handle reliably",
        "Fixed with a clearly labelled, honestly-flagged technical workaround (not real data) - confirmed the fix worked, then completed the full 10-country run",
    ],
    subtitle="A genuine engineering problem, found, diagnosed, and fixed along the way",
)

table_slide(
    "Result: Better Than Expected - But Still Not the Winning Approach",
    ["", "Combined zone (best)", "France alone", "All 10 countries"],
    [
        ["'Ran out of power' hours", "7", "167", "120"],
        ["Average price gap, ordinary days", "-2.90", "+9.65", "+4.87"],
        ["Match quality (trustworthiness)", "0.717", "0.716", "0.731 (best yet)"],
    ],
    col_widths=[5.0, 3.5, 3.5, 3.5],
    subtitle="Splitting into all 10 real countries beat the single-country attempt on every measure but one",
    note="Genuinely surprising: going all the way to 10 real countries actually did BETTER than splitting out just one - likely because Germany can now draw on many countries' cheap power at once, instead of being stuck behind one narrow link. But it still doesn't beat the original combined-zone approach on the two measures that matter most. Decision: keep the combined zone as our best, standing result.",
)

new_count = len(prs.slides)
print(f"Slides after adding: {new_count} (added {new_count - existing_count})")

# ---------------------------------------------------------------------------
# Reorder: move new slides to right after "Where This Leaves Us" (existing 41),
# before "Where We Stand Now" (existing 42).
# ---------------------------------------------------------------------------
xml_slides = prs.slides._sldIdLst
slide_id_list = list(xml_slides)
n_new = new_count - existing_count
new_slide_elements = slide_id_list[existing_count:]
insertion_index = 41  # 0-indexed: after existing slide 41

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
    fallback = rf"{ROOT}\Presentation\Progress_Report_AMIRIS_2026-09-06_UPDATED.pptx"
    prs.save(fallback)
    print(f"Original file is open/locked - saved to a new file instead: {fallback}")
