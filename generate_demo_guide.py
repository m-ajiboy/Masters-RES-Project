"""Generates AMIRIS_Demo_Guide.pdf - install/run steps for a live physical demonstration,
plus a grounded explanation of which config fields auto-update from new data files versus
which ones require manually editing the YAML, using the real Conventionals.yaml fields and
the actual current state of the Germany2023 build as a live example.
"""
from fpdf import FPDF

NAVY = (31, 58, 77)
AMBER = (165, 105, 31)
GREY = (90, 96, 92)
LIGHT = (238, 240, 233)
GOOD = (58, 107, 71)
BAD = (150, 60, 40)

MARGIN = 16


class Doc(FPDF):
    def footer(self):
        self.set_y(-13)
        self.set_font("Helvetica", "I", 8)
        self.set_text_color(*GREY)
        self.cell(0, 8, f"AMIRIS Install and Demo Guide                                                                                    Page {self.page_no()}", align="C")

    def h1(self, text):
        if self.get_y() > 255:
            self.add_page()
        self.ln(3)
        self.set_font("Helvetica", "B", 13.5)
        self.set_text_color(*NAVY)
        self.cell(0, 8, text, new_x="LMARGIN", new_y="NEXT")
        y = self.get_y()
        self.set_draw_color(*NAVY)
        self.set_line_width(0.6)
        self.line(MARGIN, y, 210 - MARGIN, y)
        self.ln(4)

    def h2(self, text):
        if self.get_y() > 262:
            self.add_page()
        self.set_font("Helvetica", "B", 10.5)
        self.set_text_color(*AMBER)
        self.ln(1)
        self.set_x(MARGIN)
        self.multi_cell(0, 5.6, text)
        self.ln(0.5)

    def body(self, text):
        self.set_font("Helvetica", "", 10)
        self.set_text_color(20, 24, 22)
        self.set_x(MARGIN)
        self.multi_cell(0, 5.4, text)
        self.ln(1.5)

    def step(self, n, title, body_text):
        if self.get_y() > 250:
            self.add_page()
        self.set_font("Helvetica", "B", 10.5)
        self.set_text_color(*NAVY)
        self.set_x(MARGIN)
        self.cell(8, 5.8, f"{n}.")
        self.multi_cell(0, 5.8, title)
        self.set_font("Helvetica", "", 10)
        self.set_text_color(20, 24, 22)
        self.set_x(MARGIN + 8)
        avail_w = 210 - 2 * MARGIN - 8
        self.multi_cell(avail_w, 5.3, body_text)
        self.ln(2)

    def code(self, text):
        if self.get_y() > 265:
            self.add_page()
        self.set_font("Courier", "B", 9.3)
        self.set_text_color(*NAVY)
        self.set_fill_color(*LIGHT)
        self.set_x(MARGIN + 8)
        self.multi_cell(210 - 2 * MARGIN - 8, 5.8, text, fill=True, align="L")
        self.ln(2)

    def callout(self, label, text, color=BAD):
        if self.get_y() > 258:
            self.add_page()
        self.set_font("Helvetica", "B", 9.5)
        self.set_text_color(*color)
        self.set_x(MARGIN)
        self.cell(0, 5.5, label, new_x="LMARGIN", new_y="NEXT")
        self.set_font("Helvetica", "I", 9.5)
        self.set_text_color(*GREY)
        self.set_x(MARGIN)
        self.multi_cell(0, 5, text)
        self.ln(2)

    def table(self, headers, rows, widths, align=None):
        align = align or ["L"] * len(headers)
        LH = 5.3
        self.set_font("Helvetica", "B", 8.3)
        self.set_fill_color(*NAVY)
        self.set_text_color(255, 255, 255)
        if self.get_y() > 235:
            self.add_page()
        for h, w, a in zip(headers, widths, align):
            self.cell(w, 7, h, border=0, fill=True, align=a)
        self.ln(7)
        self.set_font("Helvetica", "", 8.3)
        fill = False
        for row in rows:
            # measure how many lines each cell will wrap to, so the row height fits the tallest cell
            line_counts = []
            for val, w in zip(row, widths):
                lines = self.multi_cell(w, LH, val, border=0, align="L", dry_run=True, output="LINES")
                line_counts.append(max(len(lines), 1))
            row_h = max(line_counts) * LH
            if self.get_y() + row_h > 275:
                self.add_page()
                self.set_font("Helvetica", "B", 8.3)
                self.set_fill_color(*NAVY)
                self.set_text_color(255, 255, 255)
                for h, w, a in zip(headers, widths, align):
                    self.cell(w, 7, h, border=0, fill=True, align=a)
                self.ln(7)
                self.set_font("Helvetica", "", 8.3)
            self.set_fill_color(*LIGHT) if fill else self.set_fill_color(255, 255, 255)
            self.set_text_color(20, 24, 22)
            x_row, y_row = self.get_x(), self.get_y()
            x = x_row
            for w in widths:
                self.rect(x, y_row, w, row_h, style="F")
                x += w
            x = x_row
            for val, w, a in zip(row, widths, align):
                self.set_xy(x, y_row)
                self.multi_cell(w, LH, val, border=0, align=a, fill=False, max_line_height=LH)
                x += w
            self.set_xy(x_row, y_row + row_h)
            fill = not fill
        self.ln(2)


pdf = Doc()
pdf.set_margins(MARGIN, 14, MARGIN)
pdf.set_auto_page_break(auto=True, margin=16)
pdf.add_page()

# ---- Title ----
pdf.set_font("Helvetica", "B", 20)
pdf.set_text_color(*NAVY)
pdf.cell(0, 10, "AMIRIS - Install and Live Demo Guide", new_x="LMARGIN", new_y="NEXT")
pdf.set_font("Helvetica", "I", 10.5)
pdf.set_text_color(*GREY)
pdf.multi_cell(0, 5.6, "Everything needed to install, run, and demonstrate the AMIRIS scenarios this project has already produced")
pdf.set_font("Helvetica", "", 9)
pdf.set_x(MARGIN)
pdf.cell(0, 6, "Muideen Oladayo Ajiboye  |  30 July 2026", new_x="LMARGIN", new_y="NEXT")
pdf.ln(2)
y = pdf.get_y()
pdf.set_draw_color(*NAVY)
pdf.set_line_width(1)
pdf.line(MARGIN, y, 210 - MARGIN, y)
pdf.ln(4)

# =====================================================================
pdf.h1("Part A - One-Time Setup")
pdf.step(1, "Confirm Java is installed",
    "AMIRIS's simulation engine is a Java program. Open PowerShell and run the check below. Any "
    "reasonably recent Java version works (this machine has a well-above-minimum version already).")
pdf.code("java -version")

pdf.step(2, "Confirm the Python environment exists",
    "This project already has a ready-made virtual environment with amirispy (the command-line tool) "
    "and fameio (the scenario compiler/extractor) installed, at:")
pdf.code("C:\\Users\\MuideenOA\\Desktop\\PyTut\\Amiris\\py313env")
pdf.body(
    "If demonstrating on a different machine without this folder, create it fresh instead:"
)
pdf.code("python -m venv py313env\n.\\py313env\\Scripts\\Activate.ps1\npip install amirispy fameio")

pdf.step(3, "Confirm the engine file exists",
    "The actual simulation engine, a single Java file, sits in the project root:")
pdf.code("amiris-core_4.1.2-jar-with-dependencies.jar")

# =====================================================================
pdf.h1("Part B - Every Time You Demo")
pdf.step(1, "Open PowerShell in the project folder",
    "")
pdf.code("cd C:\\Users\\MuideenOA\\Desktop\\PyTut\\Amiris")

pdf.step(2, "Activate the Python environment",
    "You'll see the prompt change to show (py313env) once this works.")
pdf.code(".\\py313env\\Scripts\\Activate.ps1")

pdf.step(3, "Run a scenario",
    "This is the one command that does everything: compiles the scenario, runs the full year hour-by-hour "
    "in the Java engine, then extracts the results back into readable CSVs. Example using the Germany2019 "
    "backtest:")
pdf.code(
    "amiris run --log info `\n"
    "  --scenario \"examples\\backtest\\Germany2019\\scenario.yaml\" `\n"
    "  --jar \"amiris-core_4.1.2-jar-with-dependencies.jar\" `\n"
    "  --output \"result_Germany2019_demo\""
)
pdf.callout(
    "Gotcha - order matters:",
    "--log must come BEFORE the word 'run', not after. Putting it after the subcommand fails silently "
    "with exit code 2 - this has actually happened once already in this project."
)
pdf.body(
    "A full year takes anywhere from under a minute to a few minutes depending on the machine. To demo a "
    "different year, just change the folder name in --scenario and give --output a fresh name so you don't "
    "overwrite an existing result."
)

pdf.step(4, "Show the result",
    "Open the output folder. The file that matters most for a demo is:")
pdf.code("result_Germany2019_demo\\DayAheadMarketSingleZone.csv")
pdf.body(
    "Its ElectricityPriceInEURperMWH column is AMIRIS's simulated hourly electricity price for the whole "
    "year - 8,760 rows. This is the number the entire thesis is built around. metadata.json in the same "
    "folder explains what every column in every CSV means, useful if asked to explain a specific file live."
)

# =====================================================================
pdf.h1("Scenario Inventory - What's Actually Ready Right Now")
pdf.body("Checked directly against the project folder before writing this guide, so this reflects the real current state, not what was originally planned.")
pdf.table(
    ["Scenario", "Status", "Notes"],
    [
        ["Germany 2015-2019", "Ready - already run", "Results exist in result_Germany2015 .. result_Germany2019. Safest choice to demo live."],
        ["Austria 2019", "Ready - not yet run", "Full scenario folder present (examples\\backtest\\Austria2019), never actually executed in this project yet."],
        ["Germany 2023", "NOT ready", "Only the raw input timeseries (load, outages, fuel prices, generation profiles) have been sourced from ENTSO-E/FRED so far. scenario.yaml, schema.yaml, and the agents/contracts folders that actually define the plant fleet do not exist yet - this scenario cannot be run yet."],
        ["Germany 2027 (Brainpool)", "Not started", "Waiting on the data from the supervisor before scenario-building begins."],
    ],
    [42, 42, 106],
)
pdf.callout(
    "Recommendation for the physical demo:",
    "Run Germany2019 live - it is fully built, has already produced validated results once, and is the "
    "scenario this thesis's core findings (the 2018/2019 root-cause analysis) are grounded in.",
    color=GOOD,
)

# =====================================================================
pdf.h1("Troubleshooting Quick List")
pdf.body(
    "- 'exit code 2' immediately on run -> almost always the --log flag placed after run instead of before it.\n"
    "- Output folder error / file appears locked -> something else (Explorer preview, Excel) has a file in "
    "that folder open; close it, or give --output a new folder name.\n"
    "- A plotting script fails mentioning Tk -> matplotlib is trying to open an interactive window; if only "
    "saving a PNG is needed, this is a backend setting, not a real failure - said script simply is not "
    "present in the project folder right now, this note is here in case it gets rebuilt before the meeting."
)

# =====================================================================
pdf.h1("Does AMIRIS Auto-Update From New Input Data, or Does the YAML Need Manual Edits?")
pdf.body(
    "Short answer: it depends on the field, and AMIRIS never reaches out and updates anything on its own - "
    "it only ever reads whatever is sitting in the scenario folder at the moment 'amiris run' is executed. "
    "There are exactly two situations."
)

pdf.h2("Situation 1: the field already points to a file (automatic pickup)")
pdf.body(
    "Several fields in Conventionals.yaml and RenewablesAndPolicy.yaml are not numbers at all - they are a "
    "path to a CSV, e.g. Nuclear's real entry:"
)
pdf.code("OutageFactor: \"./timeseries/nuclear_outage.csv\"\nMustRunFactor: \"./timeseries/nuclear_must_run.csv\"")
pdf.body(
    "For these, no YAML edit is needed at all. Overwrite nuclear_outage.csv with the 2027 outage data, keep "
    "the exact same filename in the exact same timeseries folder, and the next 'amiris run' automatically "
    "picks up the new numbers. This also covers hard coal/gas/oil fuel prices, the CO2 price, and every "
    "renewable YieldProfile - all file references already, all just need the underlying CSV replaced."
)

pdf.h2("Situation 2: the field is a hardcoded number in the YAML (manual edit required)")
pdf.body(
    "Other fields are typed directly into the YAML as a plain number, not a file reference. Nuclear again, "
    "same file:"
)
pdf.code(
    "InstalledPowerInMW: 9524.0\nEfficiency:\n  Minimal: 0.330\n  Maximal: 0.331\nBlockSizeInMW: 900.0\nOpexVarInEURperMWH: 0.5"
)
pdf.body(
    "AMIRIS has no mechanism to notice that Germany's real 2027 nuclear capacity is different (it's not - "
    "the last plants closed in 2023, but this illustrates the mechanic) or that efficiency assumptions have "
    "shifted. These have to be opened and typed in by hand - or by a small script that reads the new figure "
    "and rewrites the YAML value, the same approach already used for the 2023 timeseries pulls."
)

pdf.table(
    ["Field type", "Example", "To update for 2027"],
    [
        ["File-referenced (time series)", "OutageFactor, MustRunFactor, FuelPrices (coal/gas/oil), Co2Prices, YieldProfile", "Just replace the CSV file, same name, same folder. No YAML edit."],
        ["Hardcoded scalar", "InstalledPowerInMW, Efficiency Min/Max, BlockSizeInMW, OpexVarInEURperMWH, SpecificCo2EmissionsInTperMWH, FIT/LCOE rates, storage capacities", "Must manually edit the YAML (or run a small script that does it) - AMIRIS will not pick this up on its own."],
    ],
    [45, 68, 77],
)

pdf.callout(
    "Live proof of this, sitting in the project right now:",
    "The Germany 2023 build shows exactly this split in progress. Its timeseries folder is fully populated "
    "with real ENTSO-E/FRED data - the file-referenced side is done. But its agents\\Conventionals.yaml, "
    "RenewablesAndPolicy.yaml, and Storage.yaml do not exist yet - the hardcoded-scalar side (fleet "
    "capacities, efficiencies, subsidy rates for 2023) still has to be authored by hand, which is exactly "
    "why 2023 cannot be run yet even though its raw data is ready.",
    color=NAVY,
)

pdf.output("AMIRIS_Demo_Guide.pdf")
print("Saved AMIRIS_Demo_Guide.pdf")
