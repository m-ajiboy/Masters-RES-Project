"""Generates AMIRIS_Session_2026-09-07.pdf - a very simple, plain-language walkthrough of
this session's conversation: what was asked, and what happened, in the order it happened.
Written for someone with no technical background - no jargon left unexplained, short
sentences, everyday analogies. Separate from the cumulative Progress Report, which is more
technical and covers the whole project. Follows on from the 6 September session (which ended
with the supervisor deck and progress report both fully updated through Phase 43, and the
project's local save-history committed to this computer for the first time). This short
session covered one thing: actually getting that saved history onto GitHub, including
fixing three separate real technical snags along the way."""
from fpdf import FPDF

NAVY = (31, 58, 77)
AMBER = (165, 105, 31)
GREY = (90, 96, 92)
LIGHT = (238, 240, 233)
GOOD = (58, 107, 71)
BAD = (150, 60, 40)

MARGIN = 15


class Doc(FPDF):
    def footer(self):
        self.set_y(-13)
        self.set_font("Helvetica", "I", 8)
        self.set_text_color(*GREY)
        self.cell(0, 8, f"AMIRIS Session Notes - 7 September 2026                                                                                    Page {self.page_no()}", align="C")

    def h1(self, text):
        if self.get_y() > 255:
            self.add_page()
        self.ln(3)
        self.set_font("Helvetica", "B", 15)
        self.set_text_color(*NAVY)
        self.set_x(MARGIN)
        self.multi_cell(0, 7.5, text)
        y = self.get_y()
        self.set_draw_color(*NAVY)
        self.set_line_width(0.6)
        self.line(MARGIN, y, 210 - MARGIN, y)
        self.ln(4)

    def question(self, text):
        if self.get_y() > 255:
            self.add_page()
        self.set_font("Helvetica", "BI", 10.5)
        self.set_text_color(*AMBER)
        self.set_x(MARGIN)
        self.multi_cell(0, 5.6, f'You asked: "{text}"')
        self.ln(2)

    def body(self, text):
        self.set_font("Helvetica", "", 10.5)
        self.set_text_color(20, 24, 22)
        self.set_x(MARGIN)
        self.multi_cell(0, 5.8, text)
        self.ln(2)

    def result(self, label, text, color=GOOD):
        if self.get_y() > 255:
            self.add_page()
        self.set_font("Helvetica", "B", 10.5)
        self.set_text_color(*color)
        self.set_x(MARGIN)
        self.multi_cell(0, 5.6, label)
        self.set_font("Helvetica", "", 10.5)
        self.set_text_color(20, 24, 22)
        self.set_x(MARGIN)
        self.multi_cell(0, 5.8, text)
        self.ln(3)

    def analogy(self, text):
        if self.get_y() > 250:
            self.add_page()
        self.set_fill_color(*LIGHT)
        self.set_font("Helvetica", "I", 10)
        self.set_text_color(60, 66, 63)
        self.set_x(MARGIN)
        self.multi_cell(180, 5.6, f"In plain terms: {text}", fill=True)
        self.ln(3)


pdf = Doc()
pdf.set_margins(MARGIN, 14, MARGIN)
pdf.set_auto_page_break(auto=True, margin=16)
pdf.add_page()

# ---- Title ----
pdf.set_font("Helvetica", "B", 20)
pdf.set_text_color(*NAVY)
pdf.set_x(MARGIN)
pdf.multi_cell(0, 10, "What We Did This Session")
pdf.set_font("Helvetica", "I", 11)
pdf.set_text_color(*GREY)
pdf.set_x(MARGIN)
pdf.multi_cell(0, 5.6, "A simple, no-jargon walkthrough of this session's conversation - what was asked, and what happened")
pdf.set_font("Helvetica", "", 9.5)
pdf.set_x(MARGIN)
pdf.cell(0, 6, "7 September 2026", new_x="LMARGIN", new_y="NEXT")
pdf.ln(2)
y = pdf.get_y()
pdf.set_draw_color(*NAVY)
pdf.set_line_width(1)
pdf.line(MARGIN, y, 210 - MARGIN, y)
pdf.ln(5)

pdf.body(
    "A short, focused session: getting yesterday's local save-history actually onto GitHub, "
    "where it can be shared or accessed from anywhere. Three separate real technical snags "
    "came up along the way - each one found, explained, and fixed rather than worked around."
)

# =====================================================================
pdf.h1("1. Getting Ready to Push")
pdf.question("Push it to GitHub.")
pdf.result(
    "Checked what was needed first, rather than just attempting it blindly.",
    "This computer had no direct way to create a new project on GitHub by itself, so a real "
    "empty destination was needed first. Checked the total size of everything to be uploaded "
    "(85 megabytes - comfortably fine) before asking you to create a blank project space on "
    "your GitHub account and share its address."
)
pdf.body("You provided the address: github.com/m-ajiboy/Masters-RES-Project.")

# =====================================================================
pdf.h1("2. Snag One: A Broken Security Certificate Setting")
pdf.result(
    "The very first upload attempt failed immediately with a security-certificate error.",
    "The version of the upload tool installed on this computer was pointing at a security "
    "certificate file in a location that didn't actually exist here - a leftover setting from "
    "a different, unrelated program. Found the REAL certificate file's actual location on "
    "this computer and pointed the setting there instead, just for this one project (not "
    "changed machine-wide, to avoid affecting anything else on this shared computer).",
    color=BAD,
)

# =====================================================================
pdf.h1("3. Snag Two: GitHub No Longer Accepts a Plain Password")
pdf.result(
    "The second attempt reached GitHub successfully - but GitHub itself rejected it.",
    "GitHub stopped accepting an ordinary username-and-password login for this kind of "
    "upload some time ago, for security reasons - it now requires either a special access "
    "code or a different, more secure connection method entirely. Explained the two real "
    "options and asked which you'd prefer.",
    color=BAD,
)
pdf.question("git@github.com:m-ajiboy/Masters-RES-Project.git")
pdf.body(
    "You chose the more secure connection method (known as SSH) and confirmed the exact "
    "address to use."
)

# =====================================================================
pdf.h1("4. Snag Three: No Secure Key Existed on This Computer Yet")
pdf.result(
    "Switching connection methods surfaced one more real, expected step: this computer had never been set up for it before.",
    "The secure method works using a matching pair of digital keys - one kept privately on "
    "this computer, one registered with your GitHub account. Neither existed here yet. First "
    "had to safely confirm GitHub's own identity (a standard, one-time check, similar to "
    "confirming you've reached the right website), then generated a brand new key pair and "
    "asked you to register the public half with your GitHub account.",
)
pdf.body("You confirmed once the key had been added to your GitHub account.")

# =====================================================================
pdf.h1("5. Success: Everything Now Genuinely Saved on GitHub")
pdf.result(
    "Verified the new key worked, then completed the upload.",
    "Checked directly that GitHub now recognised this computer before attempting the upload "
    "again, rather than assuming it would work. Both real saved versions of the project "
    "(the original full save, and yesterday's Phase 41-43 work) are now genuinely on GitHub "
    "at github.com/m-ajiboy/Masters-RES-Project - not just on this one computer any more.",
)
pdf.analogy(
    "Like moving from a locked filing cabinet in one office to a proper shared archive - "
    "the first attempt to move the files failed because of a broken address label, the "
    "second because the old-style door key GitHub used to accept isn't allowed any more, and "
    "the third because this particular office had never been issued the new-style key at "
    "all. Each problem was real, found, and fixed in turn - not skipped past."
)
pdf.body(
    "One practical benefit going forward: the secure key generated today should make future "
    "uploads from this computer work smoothly, without needing to repeat any of today's setup."
)

pdf.output(r"C:\Users\MuideenOA\Desktop\PyTut\Amiris\AMIRIS_Session_2026-09-07.pdf")
print("Saved AMIRIS_Session_2026-09-07.pdf")
