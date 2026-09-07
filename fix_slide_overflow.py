"""Fixes two real rendering bugs found via visual inspection of the exported slide images,
confirmed by diagnose_slide_overflow.py, applied directly to the master deck (the single
source of truth every deliverable file is copied/derived from):

1. Tables whose column widths summed to more than the available slide width, causing them to
   visibly run off the right edge - proportionally rescaled to fit within 11.9in (matching
   the width every table_slide() helper originally intended).
2. Textboxes (almost entirely the italic 'note' captions under tables/big-stats) that had
   word_wrap left at its default (not explicitly enabled) - rendered as one long unwrapped
   line running off the slide instead of wrapping within their box. Enabled word_wrap on
   every one found.

Both bugs trace to the same root cause across many separate slide-adding scripts written
over the course of this project: the shared 'note' textbox helper never set word_wrap=True,
and several table_slide() calls used column-width lists that summed to more than the box's
actual available width."""
from pptx import Presentation

PATH = r"C:\Users\MuideenOA\Desktop\PyTut\Amiris\Presentation\Progress_Report_AMIRIS_2026-08-27_UPDATED.pptx"
TARGET_TABLE_WIDTH_IN = 11.9

prs = Presentation(PATH)

tables_fixed = 0
textboxes_fixed = 0

for i, slide in enumerate(prs.slides, start=1):
    for shape in slide.shapes:
        # Fix 1: rescale overflowing table columns proportionally
        if shape.has_table:
            table = shape.table
            total_w_in = sum(col.width for col in table.columns) / 914400
            if total_w_in > TARGET_TABLE_WIDTH_IN + 0.05:
                scale = TARGET_TABLE_WIDTH_IN / total_w_in
                for col in table.columns:
                    col.width = int(col.width * scale)
                tables_fixed += 1
                print(f"Slide {i}: rescaled table from {total_w_in:.2f}in to "
                      f"{TARGET_TABLE_WIDTH_IN:.2f}in (scale factor {scale:.3f})")

        # Fix 2: enable word_wrap on any sizeable textbox missing it
        if shape.has_text_frame and not shape.has_table:
            tf = shape.text_frame
            text = tf.text.strip()
            if len(text) >= 60 and tf.word_wrap is not True:
                tf.word_wrap = True
                textboxes_fixed += 1
                print(f"Slide {i}: enabled word_wrap on textbox ({text[:50]!r}...)")

print(f"\nFixed {tables_fixed} overflowing tables and {textboxes_fixed} non-wrapping textboxes.")

prs.save(PATH)
print(f"Saved: {PATH}")
