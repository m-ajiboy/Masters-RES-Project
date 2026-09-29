"""Generates AMIRIS_Germany2027_Progress_Report.docx - a Word version of the same
Progress Report content produced by generate_2027_progress_report.py.

Rather than retype ~3,300 lines of report text a second time (and risk the two
documents drifting apart), this script takes the ORIGINAL script's source code,
swaps out only its FPDF-based `Doc` class for a python-docx-based `Doc` class
with the same method names (h1, body, table, callout, bullet, picture, plus the
handful of raw title-block calls it makes directly), and then executes the
unchanged rest of the file. Every word of content comes straight from
generate_2027_progress_report.py - only the rendering backend differs.
"""
from docx import Document
from docx.shared import Pt, Cm, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml.ns import qn
from docx.oxml import OxmlElement

SOURCE_PATH = "generate_2027_progress_report.py"
OUT_PATH = "AMIRIS_Germany2027_Progress_Report.docx"

NEW_DOC_CLASS_SOURCE = '''
from docx import Document as _Document
from docx.shared import Pt as _Pt, Cm as _Cm, RGBColor as _RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH as _WD_ALIGN_PARAGRAPH
from docx.oxml.ns import qn as _qn
from docx.oxml import OxmlElement as _OxmlElement
import os as _os


def _rgb(t):
    return _RGBColor(*t)


def _shade(cell, hex_color):
    tcPr = cell._tc.get_or_add_tcPr()
    shd = _OxmlElement("w:shd")
    shd.set(_qn("w:val"), "clear")
    shd.set(_qn("w:color"), "auto")
    shd.set(_qn("w:fill"), hex_color)
    tcPr.append(shd)


def _bottom_rule(paragraph, size_eighths, color_hex):
    pPr = paragraph._p.get_or_add_pPr()
    pBdr = _OxmlElement("w:pBdr")
    bottom = _OxmlElement("w:bottom")
    bottom.set(_qn("w:val"), "single")
    bottom.set(_qn("w:sz"), str(size_eighths))
    bottom.set(_qn("w:space"), "4")
    bottom.set(_qn("w:color"), color_hex)
    pBdr.append(bottom)
    pPr.append(pBdr)


NAVY_HEX = "1F3A4D"
LIGHT_HEX = "EEF0E9"


class Doc:
    """python-docx backed stand-in for the FPDF-based Doc class above, matching
    every method name/signature this report script actually calls."""

    def __init__(self):
        self.doc = _Document()
        style = self.doc.styles["Normal"]
        style.font.name = "Calibri"
        style.font.size = _Pt(10)
        section = self.doc.sections[0]
        section.left_margin = _Cm(1.6)
        section.right_margin = _Cm(1.6)
        section.top_margin = _Cm(1.5)
        section.bottom_margin = _Cm(1.6)
        footer_p = section.footer.paragraphs[0]
        footer_p.alignment = _WD_ALIGN_PARAGRAPH.CENTER
        run = footer_p.add_run("AMIRIS Germany2027 Progress Report")
        run.font.size = _Pt(8)
        run.font.italic = True
        run.font.color.rgb = _rgb(GREY)
        self._font_style = ""
        self._font_size = 12
        self._text_color = (0, 0, 0)

    # ---- Minimal FPDF-compatibility shims (used only by the manual title block) ----
    def set_margins(self, *a, **k):
        pass

    def set_auto_page_break(self, *a, **k):
        pass

    def add_page(self):
        pass

    def set_font(self, family, style="", size=12):
        self._font_style = style
        self._font_size = size

    def set_text_color(self, *rgb):
        self._text_color = rgb

    def set_draw_color(self, *rgb):
        pass

    def set_line_width(self, w):
        pass

    def set_fill_color(self, *rgb):
        pass

    def set_x(self, x):
        pass

    def set_xy(self, x, y):
        pass

    def get_x(self):
        return 0

    def get_y(self):
        return 0

    def rect(self, *a, **k):
        pass

    def ln(self, h=None):
        pass

    def _title_para(self, text):
        p = self.doc.add_paragraph()
        p.paragraph_format.space_after = _Pt(4)
        bold = "B" in self._font_style
        italic = "I" in self._font_style
        run = p.add_run(text)
        run.font.size = _Pt(self._font_size)
        run.font.bold = bold
        run.font.italic = italic
        run.font.color.rgb = _rgb(self._text_color)
        return p

    def multi_cell(self, w, h, text, **kwargs):
        self._title_para(text)

    def cell(self, w, h, text, **kwargs):
        self._title_para(text)

    def line(self, x1, y1, x2, y2):
        p = self.doc.add_paragraph()
        p.paragraph_format.space_after = _Pt(10)
        _bottom_rule(p, 18, NAVY_HEX)

    def image(self, path, x=None, w=None):
        if _os.path.exists(path):
            self.doc.add_picture(path, width=_Cm(16))

    # ---- Content-level helpers (the ones the report body actually uses) ----
    def h1(self, text):
        p = self.doc.add_paragraph()
        p.paragraph_format.space_before = _Pt(16)
        p.paragraph_format.space_after = _Pt(4)
        p.paragraph_format.keep_with_next = True
        run = p.add_run(text)
        run.font.size = _Pt(15)
        run.font.bold = True
        run.font.color.rgb = _rgb(NAVY)
        _bottom_rule(p, 10, NAVY_HEX)

    def h2(self, text):
        p = self.doc.add_paragraph()
        p.paragraph_format.space_before = _Pt(6)
        p.paragraph_format.space_after = _Pt(2)
        run = p.add_run(text)
        run.font.size = _Pt(11.5)
        run.font.bold = True
        run.font.color.rgb = _rgb(AMBER)

    def body(self, text):
        p = self.doc.add_paragraph()
        p.paragraph_format.space_after = _Pt(8)
        run = p.add_run(text)
        run.font.size = _Pt(10.5)
        run.font.color.rgb = _RGBColor(20, 24, 22)

    def bullet(self, text):
        p = self.doc.add_paragraph(style="List Bullet")
        p.paragraph_format.space_after = _Pt(4)
        run = p.add_run(text)
        run.font.size = _Pt(10.5)
        run.font.color.rgb = _RGBColor(20, 24, 22)

    def picture(self, path, caption=None, width=180):
        if _os.path.exists(path):
            self.doc.add_picture(path, width=_Cm(16))
        else:
            self.body(f"[figure not found: {path}]")
        if caption:
            p = self.doc.add_paragraph()
            p.paragraph_format.space_after = _Pt(8)
            run = p.add_run(caption)
            run.font.size = _Pt(9)
            run.font.italic = True
            run.font.color.rgb = _rgb(GREY)

    def callout(self, label, text, color=None):
        if color is None:
            color = BAD
        p1 = self.doc.add_paragraph()
        p1.paragraph_format.space_before = _Pt(4)
        p1.paragraph_format.space_after = _Pt(1)
        r1 = p1.add_run(label)
        r1.font.bold = True
        r1.font.size = _Pt(10)
        r1.font.color.rgb = _rgb(color)
        p2 = self.doc.add_paragraph()
        p2.paragraph_format.space_after = _Pt(8)
        r2 = p2.add_run(text)
        r2.font.italic = True
        r2.font.size = _Pt(10)
        r2.font.color.rgb = _rgb(GREY)

    def table(self, headers, rows, widths, align=None):
        total_w = sum(widths)
        n = len(headers)
        t = self.doc.add_table(rows=1, cols=n)
        t.style = "Table Grid"
        t.autofit = False
        hdr_cells = t.rows[0].cells
        for i, htext in enumerate(headers):
            p = hdr_cells[i].paragraphs[0]
            run = p.add_run(htext)
            run.font.bold = True
            run.font.size = _Pt(8.5)
            run.font.color.rgb = _RGBColor(255, 255, 255)
            _shade(hdr_cells[i], NAVY_HEX)
            hdr_cells[i].width = _Cm(16 * widths[i] / total_w)
        for ridx, row in enumerate(rows):
            cells = t.add_row().cells
            for i, val in enumerate(row):
                bold = val.startswith("**")
                if bold:
                    val = val[2:]
                p = cells[i].paragraphs[0]
                run = p.add_run(val)
                run.font.size = _Pt(8.5)
                run.font.bold = bold
                cells[i].width = _Cm(16 * widths[i] / total_w)
                if ridx % 2 == 1:
                    _shade(cells[i], LIGHT_HEX)
        self.doc.add_paragraph().paragraph_format.space_after = _Pt(4)

    def output(self, path):
        self.doc.save(path)

    def save(self, path):
        self.doc.save(path)

'''


def main():
    src = open(SOURCE_PATH, encoding="utf-8").read()

    start_marker = "class Doc(FPDF):"
    end_marker = "\npdf = Doc()"
    start_idx = src.index(start_marker)
    end_idx = src.index(end_marker)

    header = src[:start_idx].replace("from fpdf import FPDF\n", "")
    rest = src[end_idx:]

    new_source = header + NEW_DOC_CLASS_SOURCE + rest
    new_source = new_source.replace(
        '"AMIRIS_Germany2027_Progress_Report.pdf"',
        '"AMIRIS_Germany2027_Progress_Report.docx"',
    )

    exec(compile(new_source, "generated_docx_report.py", "exec"), {"__name__": "__main__"})


if __name__ == "__main__":
    main()
