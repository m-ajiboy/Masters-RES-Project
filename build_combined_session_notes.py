"""Merges every daily session-recap PDF into one single combined document, in chronological
order, with a cover page and a clickable bookmark for each day (so it reads as one document,
not just concatenated files). Each day's original page content/layout is preserved exactly -
no re-transcription, so there is no risk of drift from the real generated content. Re-run
this after adding any new daily recap to rebuild the combined file from scratch."""
from fpdf import FPDF
from pypdf import PdfWriter, PdfReader

ROOT = r"C:\Users\MuideenOA\Desktop\PyTut\Amiris"
NAVY = (31, 58, 77)
GREY = (90, 96, 92)
MARGIN = 15

# Chronological order, (date, display_label)
DAYS = [
    ("2026-08-24", "24 August 2026"),
    ("2026-08-25", "25 August 2026"),
    ("2026-08-26", "26 August 2026"),
    ("2026-08-27", "27 August 2026"),
    ("2026-08-28", "28 August 2026"),
    ("2026-09-01", "1 September 2026"),
    ("2026-09-05", "5 September 2026"),
    ("2026-09-06", "6 September 2026"),
    ("2026-09-07", "7 September 2026"),
]

# ---------------------------------------------------------------------------
# 1. Build a small cover page as its own standalone PDF, matching the same
#    visual style as every daily recap.
# ---------------------------------------------------------------------------
cover = FPDF()
cover.set_margins(MARGIN, 14, MARGIN)
cover.add_page()
cover.set_y(90)
cover.set_font("Helvetica", "B", 26)
cover.set_text_color(*NAVY)
cover.set_x(MARGIN)
cover.multi_cell(0, 12, "AMIRIS Project - Complete Session Notes", align="C")
cover.set_font("Helvetica", "I", 13)
cover.set_text_color(*GREY)
cover.set_x(MARGIN)
cover.multi_cell(0, 7, "Every daily session recap, combined into one document, in order", align="C")
cover.ln(6)
cover.set_font("Helvetica", "", 11)
cover.set_text_color(20, 24, 22)
cover.set_x(MARGIN)
cover.multi_cell(0, 6.5, f"Covers {DAYS[0][1]} through {DAYS[-1][1]}", align="C")
cover.ln(10)
cover.set_font("Helvetica", "", 10)
cover.set_text_color(*GREY)
cover.set_x(MARGIN)
cover.multi_cell(
    0, 5.6,
    "Each day below is its own real, unedited session recap exactly as originally written - "
    "a plain-language walkthrough of what was asked and what happened that day. This combined "
    "document exists purely for convenience (one file instead of nine); the technical "
    "Progress Report remains the authoritative, phase-numbered record of the project.",
    align="C",
)
cover.ln(12)
cover.set_font("Helvetica", "B", 11)
cover.set_text_color(*NAVY)
for date_iso, label in DAYS:
    cover.set_x(MARGIN + 40)
    cover.cell(0, 7, label, new_x="LMARGIN", new_y="NEXT")
cover_path = rf"{ROOT}\_cover_temp.pdf"
cover.output(cover_path)

# ---------------------------------------------------------------------------
# 2. Merge: cover page + each day's full PDF, with a bookmark per day.
# ---------------------------------------------------------------------------
writer = PdfWriter()

cover_reader = PdfReader(cover_path)
for page in cover_reader.pages:
    writer.add_page(page)

for date_iso, label in DAYS:
    day_path = rf"{ROOT}\AMIRIS_Session_{date_iso}.pdf"
    reader = PdfReader(day_path)
    start_page_index = len(writer.pages)
    for page in reader.pages:
        writer.add_page(page)
    writer.add_outline_item(label, start_page_index)
    print(f"Added {label}: {len(reader.pages)} pages (from AMIRIS_Session_{date_iso}.pdf)")

out_path = rf"{ROOT}\AMIRIS_All_Session_Notes.pdf"
with open(out_path, "wb") as f:
    writer.write(f)

print(f"\nSaved {out_path} ({len(writer.pages)} total pages)")

import os
os.remove(cover_path)
