"""Inserts a new 'what are the four versions' slide into the EXISTING, already-edited
AMIRIS_Germany2027_Progress_Presentation.pptx (does not regenerate the deck - opens the
current file in place, so the user's own edits/deletions are preserved). Inserted right
after the 'Roadmap of This Work' slide, since the four versions are referenced throughout
everything that follows. Renumbers the footer page numbers on every slide so they stay
consistent after the insertion.
"""
from pptx import Presentation
from pptx.util import Inches, Pt, Emu
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN
from pptx.enum.shapes import MSO_SHAPE
import copy

import sys
PATH = r"C:\Users\MuideenOA\Desktop\PyTut\Amiris\AMIRIS_Germany2027_Progress_Presentation.pptx"
OUT_PATH = sys.argv[1] if len(sys.argv) > 1 else PATH

NAVY = RGBColor(0x1F, 0x3A, 0x4D)
AMBER = RGBColor(0xA5, 0x69, 0x1F)
GREY = RGBColor(0x55, 0x5B, 0x58)
GOOD = RGBColor(0x3A, 0x6B, 0x47)
BAD = RGBColor(0x96, 0x3C, 0x28)
WHITE = RGBColor(0xFF, 0xFF, 0xFF)
LIGHT_BG = RGBColor(0xF2, 0xF3, 0xEF)

SLIDE_W = Inches(13.333)
SLIDE_H = Inches(7.5)

prs = Presentation(PATH)
BLANK = prs.slide_layouts[6]


def add_bg(slide, color=WHITE):
    shape = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, SLIDE_W, SLIDE_H)
    shape.fill.solid()
    shape.fill.fore_color.rgb = color
    shape.line.fill.background()
    shape.shadow.inherit = False
    slide.shapes._spTree.remove(shape._element)
    slide.shapes._spTree.insert(2, shape._element)
    return shape


def add_title(slide, text, color=NAVY):
    box = slide.shapes.add_textbox(Inches(0.5), Inches(0.28), Inches(12.3), Inches(0.7))
    tf = box.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    r = p.add_run()
    r.text = text
    r.font.size = Pt(28)
    r.font.bold = True
    r.font.color.rgb = color
    r.font.name = "Calibri"
    line = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0.5), Inches(1.15), Inches(12.3), Pt(2.5))
    line.fill.solid()
    line.fill.fore_color.rgb = color
    line.line.fill.background()
    line.shadow.inherit = False


def add_footer(slide, n):
    box = slide.shapes.add_textbox(Inches(0.5), Inches(7.15), Inches(12.3), Inches(0.3))
    p = box.text_frame.paragraphs[0]
    r = p.add_run()
    r.text = f"AMIRIS Germany2027 Progress  |  {n}"
    r.font.size = Pt(9)
    r.font.italic = True
    r.font.color.rgb = GREY
    p.alignment = PP_ALIGN.CENTER


def cell(slide, left, top, width, height, header, body_lines, header_color):
    box = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, left, top, width, height)
    box.fill.solid()
    box.fill.fore_color.rgb = LIGHT_BG
    box.line.color.rgb = header_color
    box.line.width = Pt(1.5)
    box.shadow.inherit = False
    tf = box.text_frame
    tf.word_wrap = True
    tf.margin_left = Inches(0.18)
    tf.margin_right = Inches(0.18)
    tf.margin_top = Inches(0.12)
    p = tf.paragraphs[0]
    r = p.add_run()
    r.text = header
    r.font.bold = True
    r.font.size = Pt(15)
    r.font.color.rgb = header_color
    for line in body_lines:
        p2 = tf.add_paragraph()
        p2.space_before = Pt(4)
        r2 = p2.add_run()
        r2.text = line
        r2.font.size = Pt(12)
        r2.font.color.rgb = RGBColor(0x14, 0x18, 0x16)


# ---- Build the new slide ----
new_slide = prs.slides.add_slide(BLANK)  # always appended to the end for now
add_bg(new_slide)
add_title(new_slide, "The Four Model Versions")

sub = new_slide.shapes.add_textbox(Inches(0.5), Inches(1.28), Inches(12.3), Inches(0.4))
p = sub.text_frame.paragraphs[0]
r = p.add_run()
r.text = "Two demand models x two cross-border assumptions - referenced throughout everything that follows"
r.font.size = Pt(14)
r.font.italic = True
r.font.color.rgb = GREY

# Column headers
col_labels = ["No cross-border trade", "With cross-border trade (ImportTrader)"]
col_left = [Inches(3.55), Inches(8.4)]
for label, left in zip(col_labels, col_left):
    box = new_slide.shapes.add_textbox(left, Inches(1.85), Inches(4.6), Inches(0.4))
    p = box.text_frame.paragraphs[0]
    p.alignment = PP_ALIGN.CENTER
    r = p.add_run()
    r.text = label
    r.font.bold = True
    r.font.size = Pt(14)
    r.font.color.rgb = NAVY

# Row headers (rotated-feel via simple left labels)
row_labels = [
    ("V1", "BDEW demand: one household\nprofile applied to the WHOLE\neconomy's demand"),
    ("V2", "Component-split demand:\nreal base load + heat-pump +\nelectrolysis + EV shapes"),
]
row_top = [Inches(2.35), Inches(4.75)]
for (tag, desc), top in zip(row_labels, row_top):
    box = new_slide.shapes.add_textbox(Inches(0.5), top, Inches(2.9), Inches(2.2))
    tf = box.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    r = p.add_run()
    r.text = tag
    r.font.bold = True
    r.font.size = Pt(20)
    r.font.color.rgb = NAVY
    p2 = tf.add_paragraph()
    p2.space_before = Pt(4)
    r2 = p2.add_run()
    r2.text = desc
    r2.font.size = Pt(11.5)
    r2.font.color.rgb = GREY

# The four cells
cell_w, cell_h = Inches(4.6), Inches(2.25)
cell(new_slide, Inches(3.55), Inches(2.3), cell_w, cell_h,
     "V1, no-import",
     ["The first, simplest build.", "Shortage hours: 15.88%", "Mean price: 519 EUR/MWh"],
     BAD)
cell(new_slide, Inches(8.4), Inches(2.3), cell_w, cell_h,
     "V1, with-import",
     ["BDEW demand + import added.", "Final ceiling: 37,650 MW (flat)", "Shortage hours: 0.83%", "Mean price: 75 EUR/MWh"],
     AMBER)
cell(new_slide, Inches(3.55), Inches(4.7), cell_w, cell_h,
     "V2, no-import",
     ["Refined demand, no import.", "Shortage hours: 7.52%", "Mean price: 286 EUR/MWh"],
     AMBER)
cell(new_slide, Inches(8.4), Inches(4.7), cell_w, cell_h,
     "V2, with-import  (FINAL)",
     ["Refined demand + import,", "calibrated. Ceiling: 30,000 MW", "Shortage hours: 0.03%", "Mean price: 57 EUR/MWh",
      "Closest to Brainpool's real", "forecast of 68 EUR/MWh"],
     GOOD)

# ---- Move the new slide to right after "Roadmap of This Work" ----
def slide_title_text(slide):
    for shape in slide.shapes:
        if shape.has_text_frame and shape.text_frame.text.strip():
            return shape.text_frame.text.strip().split("\n")[0]
    return ""


xml_slides = prs.slides._sldIdLst
slides_list = list(xml_slides)
titles = [slide_title_text(s) for s in prs.slides]
insert_after_idx = next(i for i, t in enumerate(titles) if t == "Roadmap of This Work")

new_slide_pos = len(slides_list) - 1  # it was appended last
new_elem = slides_list[new_slide_pos]
xml_slides.remove(new_elem)
xml_slides.insert(insert_after_idx + 1, new_elem)

# ---- Renumber every footer to match the new slide order ----
for i, slide in enumerate(prs.slides, start=1):
    for shape in slide.shapes:
        if shape.has_text_frame and "AMIRIS Germany2027 Progress" in shape.text_frame.text:
            shape.text_frame.paragraphs[0].runs[0].text = f"AMIRIS Germany2027 Progress  |  {i}"
            break

prs.save(OUT_PATH)
print(f"Inserted 'The Four Model Versions' slide at position {insert_after_idx + 2} of {len(xml_slides)}")
print(f"Saved to {OUT_PATH}")
