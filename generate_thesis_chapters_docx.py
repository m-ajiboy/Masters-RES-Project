"""Converts Thesis_Chapter_1_2_Draft.md into a formatted .docx following the Hochschule
Nordhausen Master Thesis template conventions established for this project: A4, 1.5 line
spacing, 12pt body text, justified, 2.5cm side/top margins, 2.0cm bottom margin, each main
chapter (H1) starts a new page, max 3 outline levels, Harvard-style references left verbatim.
"""
import re
import sys
from docx import Document
from docx.shared import Pt, Cm, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.section import WD_SECTION

SRC = "Thesis_Chapter_1_2_Draft.md"
FONT = "Times New Roman"


def add_run_with_italics(paragraph, text, base_size=12, italic_default=False, color=None):
    """Splits text on *italic* markers and Harvard-style markers, adding runs accordingly."""
    parts = re.split(r'(\*[^*]+\*)', text)
    for part in parts:
        if not part:
            continue
        italic = italic_default
        content = part
        if part.startswith('*') and part.endswith('*') and len(part) > 1:
            italic = True
            content = part[1:-1]
        run = paragraph.add_run(content)
        run.font.name = FONT
        run.font.size = Pt(base_size)
        run.italic = italic
        if color:
            run.font.color.rgb = color


def build():
    doc = Document()

    style = doc.styles['Normal']
    style.font.name = FONT
    style.font.size = Pt(12)
    pf = style.paragraph_format
    pf.line_spacing = 1.5
    pf.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    pf.space_after = Pt(0)

    section = doc.sections[0]
    section.page_width = Cm(21.0)
    section.page_height = Cm(29.7)
    section.left_margin = Cm(2.5)
    section.right_margin = Cm(2.5)
    section.top_margin = Cm(2.5)
    section.bottom_margin = Cm(2.0)

    lines = open(SRC, encoding="utf-8").read().split("\n")

    first_chapter = True
    i = 0
    in_references = False
    while i < len(lines):
        line = lines[i]
        stripped = line.strip()

        if stripped == "":
            i += 1
            continue
        if stripped == "---":
            i += 1
            continue

        if stripped.startswith("# "):
            title = stripped[2:].strip()
            in_references = title.lower() == "references"
            if not first_chapter:
                doc.add_page_break()
            first_chapter = False
            p = doc.add_paragraph()
            p.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.LEFT
            p.paragraph_format.space_before = Pt(0)
            p.paragraph_format.space_after = Pt(18)
            r = p.add_run(title)
            r.font.name = FONT
            r.font.size = Pt(18)
            r.bold = True
            i += 1
            continue

        if stripped.startswith("### "):
            title = stripped[4:].strip()
            p = doc.add_paragraph()
            p.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.LEFT
            p.paragraph_format.space_before = Pt(14)
            p.paragraph_format.space_after = Pt(6)
            r = p.add_run(title)
            r.font.name = FONT
            r.font.size = Pt(13)
            r.bold = True
            i += 1
            continue

        if stripped.startswith("## "):
            title = stripped[3:].strip()
            p = doc.add_paragraph()
            p.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.LEFT
            p.paragraph_format.space_before = Pt(16)
            p.paragraph_format.space_after = Pt(8)
            r = p.add_run(title)
            r.font.name = FONT
            r.font.size = Pt(14.5)
            r.bold = True
            i += 1
            continue

        # standalone equation-like line (Chapter 2 has one plain-text formula line)
        if "marginal cost = " in stripped and "=" in stripped:
            p = doc.add_paragraph()
            p.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.CENTER
            p.paragraph_format.space_before = Pt(6)
            p.paragraph_format.space_after = Pt(6)
            r = p.add_run(stripped)
            r.font.name = "Courier New"
            r.font.size = Pt(11)
            r.italic = True
            i += 1
            continue

        # regular paragraph
        p = doc.add_paragraph()
        if in_references:
            p.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.LEFT
            p.paragraph_format.space_after = Pt(10)
            p.paragraph_format.first_line_indent = Cm(-1.0)
            p.paragraph_format.left_indent = Cm(1.0)
            add_run_with_italics(p, stripped, base_size=11)
        else:
            p.paragraph_format.first_line_indent = Cm(0)
            p.paragraph_format.space_after = Pt(10)
            add_run_with_italics(p, stripped, base_size=12)
        i += 1

    out_path = sys.argv[1] if len(sys.argv) > 1 else "Thesis_Chapter_1_2.docx"
    doc.save(out_path)
    print(f"Saved: {out_path}")


if __name__ == "__main__":
    build()
