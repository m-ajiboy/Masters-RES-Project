"""Inserts new slides into the supervisor deck covering everything since Phase 34 - the
market-coupling build: real data sourcing, the first working coupled market, real
transmission data, real storage/subsidy realism (the project's best result), the 2028/2029
extension, and the two honest dead-end investigations chasing the remaining shortage-hour
gap. Positioned right after the existing "Why We're Not Adopting This" slide (32), before
"Where We Stand Now" (33). Preserves every existing slide and prior edits untouched."""
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


def bullet_slide(title, items, subtitle=None):
    slide = new_slide()
    header_bar(slide, title, subtitle)
    bullets(slide, items)
    return slide


def big_stat_slide(title, stat, stat_label, items, subtitle=None, stat_color=GOOD):
    slide = new_slide()
    header_bar(slide, title, subtitle)
    box = slide.shapes.add_textbox(Inches(0.55), Inches(1.5), Inches(12.2), Inches(1.6))
    tf = box.text_frame
    p = tf.paragraphs[0]
    p.text = stat
    p.font.size = Pt(48)
    p.font.bold = True
    p.font.color.rgb = stat_color
    p.alignment = PP_ALIGN.CENTER
    p2 = tf.add_paragraph()
    p2.text = stat_label
    p2.font.size = Pt(16)
    p2.font.italic = True
    p2.font.color.rgb = GREY
    p2.alignment = PP_ALIGN.CENTER
    bullets(slide, items, top=3.3, height=4.2)
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


# =============================================================================
# New slides: the market-coupling build, Phases 34-40
# =============================================================================

bullet_slide(
    "The Big Idea: A Real Two-Way Trading Partner for Germany",
    [
        "Every smaller idea we tested (price cap, start-up cost, bidding floor) came up empty or too limited",
        "The one big lever left untested: let the model properly BUY AND SELL power across the border, not just buy",
        "AMIRIS has a real, working template for exactly this - a second market 'zone' connected to Germany's own, trading both ways",
        "Plan: source real data first, build a first working version, then refine it step by step",
    ],
    subtitle="Moving from the small experiments to the one big remaining idea",
)

bullet_slide(
    "Sourcing Real Data From Scratch for a 'Rest of Europe' Zone",
    [
        "Needed: how much power the rest of Europe uses, what it's generated from, and how much can physically flow across the border",
        "Pulled real 2023 figures (demand, power plant types) for Germany's 10 real neighbouring countries from Eurostat",
        "Pulled real weather-driven wind/solar output the same way we did for Germany's own model",
        "Hit a real multi-day outage on Europe's official cross-border data platform partway through - worked around it with an alternative real source, then went back and finished the job once it recovered",
    ],
    subtitle="Nothing invented - every number traced to a real source",
)

table_slide(
    "The First Working Two-Way Market",
    ["", "Before (import-only)", "First working version"],
    [
        ["Match quality (trustworthy score)", "0.675", "0.739"],
        ["Average price gap", "-11.86", "-30.39"],
    ],
    col_widths=[5.0, 3.7, 3.7],
    subtitle="A real improvement in one measure, a real cost in another - both honestly reported",
    note="Match quality genuinely improved. But the average price moved further from real - explained by a placeholder guess for how much power can flow across the border, and the other side having no storage/flexibility of its own yet.",
)

bullet_slide(
    "Real Border Data Replaces the Guess",
    [
        "The European data platform came back online - immediately used it to replace the placeholder guess",
        "Pulled real, hour-by-hour cross-border flow data for all of Germany's real neighbouring borders",
        "Used that real data to set a genuine, grounded limit on how much power can flow - not a guess",
        "Result: confirmed the match-quality improvement was real, not just luck from an oversized placeholder guess",
    ],
    subtitle="Turning a placeholder into a real, sourced number",
)

big_stat_slide(
    "Adding Real Storage: Our Best Result Yet",
    "Average price within 60 cents",
    "of the real figure - the closest match this entire project has produced",
    [
        "Gave the 'Rest of Europe' side its own real storage (battery-style + reservoir hydro), the same way Germany already has",
        "Gave it real subsidy treatment too, instead of a placeholder zero",
        "Checked directly that the new storage is actually doing real work, not just sitting there unused - confirmed it is",
        "Match quality also stayed strong - a genuine, all-round best result",
    ],
    subtitle="Real storage and real subsidies on both sides of the border",
)

table_slide(
    "Does It Hold Up in Other Years? Testing 2028 and 2029",
    ["", "2028", "2029"],
    [
        ["Match quality: before", "0.446", "0.446"],
        ["Match quality: with two-way trading", "0.718", "0.752"],
        ["Average price gap: with two-way trading", "+6.19", "+26.85"],
    ],
    col_widths=[5.4, 3.5, 3.5],
    subtitle="The same build, tested on years we never tuned it for",
    note="Match quality improved strongly in both years, confirming it isn't a one-year fluke. But the average price gap looked concerning for 2029 - investigated further on the next slide.",
)

bullet_slide(
    "The Real Story: Excellent on Ordinary Days",
    [
        "That '+26.85' number looked like a real step backwards - checked it properly rather than taking it at face value",
        "Found: 88% of that gap comes from just a handful of extreme 'ran out of power' hours",
        "On ordinary days (99%+ of the year), all three years - 2027, 2028, 2029 - are excellent and remarkably consistent",
        "The real, narrower issue: those extreme hours are becoming more frequent the further we get from our home year (2027)",
    ],
    subtitle="A follow-up question corrected a misleading headline number",
)

bullet_slide(
    "Chasing That Gap: Two Honest Dead Ends",
    [
        "Idea 1: scale up the border capacity to keep pace with Germany's own growth - tested directly, did not fix it, made one year worse",
        "Idea 2: check a specific setting inside AMIRIS's own coupling engine - opened up the real program code and found that setting was already unlimited, not the cause",
        "Found one real, unexplained clue instead: Germany's import during these rare hours stays suspiciously flat no matter how much extra capacity is available",
        "Getting to the exact cause would need to edit and rebuild AMIRIS's own program - a bigger step, not yet taken",
    ],
    subtitle="Two well-reasoned ideas, tested properly, both honestly ruled out",
)

table_slide(
    "Where This Leaves Us",
    ["", "2027", "2028", "2029"],
    [
        ["Match quality (with two-way trading)", "0.717", "0.718", "0.752"],
        ["Average price gap, ordinary days only", "-0.59", "+1.08", "+3.21"],
        ["Rare extreme hours (target: near zero)", "7", "17", "76"],
    ],
    col_widths=[5.4, 3.0, 3.0, 3.0],
    subtitle="The real, current state of the two-way trading model across all three years",
    note="Strong, consistent match quality and excellent ordinary-day accuracy across all three years - the core result stands. The one real, still-open gap is the rising frequency of extreme hours the further a year is from 2027.",
)

new_count = len(prs.slides)
print(f"Slides after adding: {new_count} (added {new_count - existing_count})")

# ---------------------------------------------------------------------------
# Reorder: move the newly-added slides to right after the lignite-markup
# result slide (existing slide 32), before "Where We Stand Now" (existing 33).
# ---------------------------------------------------------------------------
xml_slides = prs.slides._sldIdLst
slide_id_list = list(xml_slides)
n_new = new_count - existing_count
new_slide_elements = slide_id_list[existing_count:]
insertion_index = 32  # 0-indexed: after existing slide 32

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
    fallback = rf"{ROOT}\Presentation\Progress_Report_AMIRIS_2026-09-05_UPDATED.pptx"
    prs.save(fallback)
    print(f"Original file is open/locked - saved to a new file instead: {fallback}")
