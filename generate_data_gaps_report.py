"""Generates AMIRIS_2027_Data_Gaps_and_LoadProfile.pdf - documents every identified gap in the
Brainpool 2027 dataset, the chosen AMIRIS-consistent fix for each, a real-world alternative
source where one exists, and a full explanation of the BDEW/demandlib load-profile methodology
including why it's not the efficient choice here and what to do instead.
"""
from fpdf import FPDF

NAVY = (31, 58, 77)
AMBER = (165, 105, 31)
GREY = (90, 96, 92)
LIGHT = (238, 240, 233)
GOOD = (58, 107, 71)
BAD = (150, 60, 40)

MARGIN = 16
LH = 5.3


class Doc(FPDF):
    def footer(self):
        self.set_y(-13)
        self.set_font("Helvetica", "I", 8)
        self.set_text_color(*GREY)
        self.cell(0, 8, f"AMIRIS 2027 Scenario - Data Gaps and Load Profile Methodology                                              Page {self.page_no()}", align="C")

    def h1(self, text):
        if self.get_y() > 255:
            self.add_page()
        self.ln(3)
        self.set_font("Helvetica", "B", 13.5)
        self.set_text_color(*NAVY)
        self.set_x(MARGIN)
        self.multi_cell(0, 7, text)
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

    def code(self, text):
        if self.get_y() > 265:
            self.add_page()
        self.set_font("Courier", "B", 9.2)
        self.set_text_color(*NAVY)
        self.set_fill_color(*LIGHT)
        self.set_x(MARGIN)
        self.multi_cell(0, 5.6, text, fill=True, align="L")
        self.ln(2)

    def callout(self, label, text, color=BAD):
        if self.get_y() > 255:
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

        def draw_header():
            self.set_font("Helvetica", "B", 8.2)
            self.set_fill_color(*NAVY)
            self.set_text_color(255, 255, 255)
            for h, w, a in zip(headers, widths, align):
                self.cell(w, 7, h, border=0, fill=True, align=a)
            self.ln(7)
            self.set_font("Helvetica", "", 8.2)

        if self.get_y() > 235:
            self.add_page()
        draw_header()
        fill = False
        for row in rows:
            line_counts = []
            for val, w in zip(row, widths):
                lines = self.multi_cell(w, LH, val, border=0, align="L", dry_run=True, output="LINES")
                line_counts.append(max(len(lines), 1))
            row_h = max(line_counts) * LH
            if self.get_y() + row_h > 275:
                self.add_page()
                draw_header()
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
pdf.set_font("Helvetica", "B", 18.5)
pdf.set_text_color(*NAVY)
pdf.set_x(MARGIN)
pdf.multi_cell(0, 9, "AMIRIS 2027 Scenario - Data Gaps, Fixes, and the Load Profile Question")
pdf.set_font("Helvetica", "I", 10.5)
pdf.set_text_color(*GREY)
pdf.set_x(MARGIN)
pdf.multi_cell(0, 5.6, "What the Brainpool 2027 dataset doesn't cover, how we intend to fill each gap, and a proper walkthrough of the BDEW/demandlib load-profile method")
pdf.set_font("Helvetica", "", 9)
pdf.set_x(MARGIN)
pdf.cell(0, 6, "Muideen Oladayo Ajiboye  |  31 July 2026", new_x="LMARGIN", new_y="NEXT")
pdf.ln(2)
y = pdf.get_y()
pdf.set_draw_color(*NAVY)
pdf.set_line_width(1)
pdf.line(MARGIN, y, 210 - MARGIN, y)
pdf.ln(4)

# =====================================================================
pdf.h1("Overview - Every Gap, at a Glance")
pdf.table(
    ["Gap", "Chosen fix (AMIRIS-consistent)", "Real alternative, if not using AMIRIS's own"],
    [
        ["Conventional plant outages/must-run", "Reuse AMIRIS's own real outage/must-run time series per fuel type (from the validated 2015-2019 scenarios) as the 2027 assumption.", "None credible exists for unplanned outages 3 years out - even a 'real' source would just be another assumption. Long-lead planned maintenance is sometimes in TYNDP/Netzentwicklungsplan filings, but coverage this far ahead is thin."],
        ["Wind offshore generation shape", "Reuse AMIRIS's own wind_offshore_profile.csv shape, rescaled to Brainpool's 12.57 GW offshore figure.", "renewables.ninja (Imperial College/ETH Zurich) generates synthetic capacity-factor series for any country/technology/weather-year from reanalysis data - a genuine independent source."],
        ["Renewable subsidy/support rates", "Reuse AMIRIS's own example FIT/MPVAR rates as a placeholder, OR default all renewables to pure marginal-cost bidding (0 EUR/MWh) as the simplest documented assumption.", "Germany's EEG (Erneuerbare-Energien-Gesetz) publishes legally mandated FIT/premium degression schedules; Bundesnetzagentur publishes actual auction-cleared strike prices. This is the stronger option if time allows - it's real, not assumed."],
        ["Storage energy capacity (GW to MWh)", "Derive a duration (hours) from AMIRIS's own 2019 storage fleet, apply it to Brainpool's GW figures. Full working below.", "Bundesnetzagentur's MaStR (Marktstammdatenregister) registers individual German storage projects with both power AND energy capacity - a real, authoritative alternative, especially for battery storage specifically (see caveat below)."],
        ["Cross-border trade / imports", "Assume none - Germany modelled as a standalone market, matching AMIRIS's own example-scenario convention.", "TYNDP (ENTSO-E's Ten-Year Network Development Plan) and Germany's Netzentwicklungsplan publish assumed cross-border transfer capacities for future scenario years, if this gets revisited later."],
    ],
    [42, 78, 70],
)

# =====================================================================
pdf.h1("1. Conventional Plant Outage / Must-Run Factors")
pdf.body(
    "Nothing in the Brainpool file addresses this at all. For a genuinely future year like 2027, this "
    "isn't really fixable with 'real' data anyway - nobody can know in 2026 which specific coal unit will "
    "trip in March 2027. Even a commercial forecaster's outage assumption is itself a modelled estimate, "
    "not an observation. Given that, reusing AMIRIS's own already-validated outage/must-run time series "
    "per fuel type (the same files used successfully in the 2015-2019 backtest) is not a weaker choice than "
    "any alternative - it's an equally honest assumption, and it keeps this one variable held constant "
    "against the model's own past behaviour, which is useful for interpreting any 2027 divergence."
)

# =====================================================================
pdf.h1("2. Wind Offshore Generation Shape")
pdf.body(
    "Brainpool gives an offshore wind capacity figure (12.57 GW) but the feed-in profile sheet only has "
    "generic 'Wind_north/east/middle/swest' columns - no offshore-specific shape. AMIRIS's own example "
    "scenarios already include a dedicated wind_offshore_profile.csv; reusing that shape, rescaled to "
    "Brainpool's capacity figure, is the direct fix."
)
pdf.callout(
    "If an independent check is wanted:",
    "renewables.ninja can generate a synthetic German offshore capacity-factor series from weather "
    "reanalysis data for a chosen year - useful as a sanity check against AMIRIS's own profile, or as the "
    "primary source if we want the shape to come from outside AMIRIS entirely.",
    color=NAVY,
)

# =====================================================================
pdf.h1("3. Renewable Subsidy / Support Rates")
pdf.body(
    "Not present in the Brainpool file. Two honest options: reuse AMIRIS's own example FIT/MPVAR rates as "
    "placeholders (fastest, but slightly circular - AMIRIS validating against AMIRIS's own assumptions), or "
    "default every renewable to bid at pure marginal cost with no subsidy top-up at all (simpler, and "
    "arguably more honest about what we don't know, though it changes bidding behaviour compared to the "
    "validated 2015-2019 scenarios)."
)
pdf.callout(
    "Stronger real alternative:",
    "Germany's EEG law publishes legally mandated FIT/premium degression schedules years in advance, and "
    "Bundesnetzagentur publishes actual cleared strike prices from recent renewable auctions. Since these "
    "are legislated, not forecast, a 2027 rate can genuinely be looked up rather than assumed - worth the "
    "extra effort if time allows, since it removes this gap entirely rather than papering over it.",
    color=GOOD,
)

# =====================================================================
pdf.h1("4. Storage Energy Capacity - Converting Brainpool's GW to AMIRIS's MWh")
pdf.body(
    "Brainpool gives Pumpspeicher and Grossbatteriespeicher only as power (GW) - how fast they can "
    "charge/discharge, not how many hours they can sustain it. AMIRIS needs the energy capacity (MWh) "
    "directly. The fix: derive a typical duration (hours = MWh / MW) from AMIRIS's own real storage fleet, "
    "then multiply Brainpool's GW figure by that duration."
)
pdf.h2("The actual calculation, done against AMIRIS's real Germany2019 fleet")
pdf.body(
    "Germany2019's Storage.yaml defines 18 individual storage units. 16 of them share a 24-hour scheduling "
    "horizon (day-to-day cycling storage); the remaining 2 use a 168-hour horizon with vastly larger energy-"
    "to-power ratios (111 and 550 hours) - almost certainly representing seasonal reservoir storage, not "
    "day-cycling batteries or pumped hydro, and excluded from this calculation for that reason."
)
pdf.code(
    "Summed across the 16 daily-cycle units:\n"
    "  Total power   = 8,514.1 MW\n"
    "  Total energy  = 54,481 MWh\n"
    "  Duration      = 54,481 / 8,514.1 = 6.40 hours   (capacity-weighted)\n"
    "  Range         = 2.87 h (smallest unit) to 17.50 h (largest unit)\n\n"
    "  Average charging efficiency    = 87.5%\n"
    "  Average discharging efficiency = 85.2%\n"
    "  Implied round-trip efficiency  = 87.5% x 85.2% = 74.6%"
)
pdf.body("Applying the 6.40-hour duration to Brainpool's 2027 power figures:")
pdf.code(
    "Pumpspeicher:            not given in GW in the sample above - apply the same formula:\n"
    "  Energy (MWh) = Power (GW) x 1,000 x 6.40\n\n"
    "Grossbatteriespeicher (5.15 GW example figure from the Capacity sheet):\n"
    "  Energy = 5.15 x 1,000 x 6.40 = 32,960 MWh"
)
pdf.callout(
    "Important caveat - this duration is a poor fit for modern batteries:",
    "AMIRIS's 2019-vintage storage fleet almost certainly represents mostly pumped hydro - Germany had very "
    "little grid-scale battery storage in 2019. Real modern battery projects are typically sized for 1-4 "
    "hours of duration (often specifically 2 hours, driven by arbitrage/frequency-response economics), not "
    "6.4 hours. Using AMIRIS's blended figure for Pumpspeicher is defensible; using it for Grossbatteriespeicher "
    "is a real, documented simplification that likely overstates battery energy capacity.",
    color=BAD,
)
pdf.callout(
    "Better real alternative for the battery figure specifically:",
    "Bundesnetzagentur's MaStR (Marktstammdatenregister) registers individual German storage installations "
    "with both power and energy capacity - since battery projects are a newer, well-documented asset class, "
    "pulling real project-level duration statistics from MaStR would directly fix this rather than "
    "borrowing a pumped-hydro-era number. Flagging this as worth doing before the number goes into results, "
    "not just before the meeting.",
    color=GOOD,
)

# =====================================================================
pdf.h1("5. Cross-Border Trade - Assumed None")
pdf.body(
    "Brainpool's file does include a real figure - Net Exports of -43.9 TWh, meaning Germany is a net "
    "importer in this 2027 scenario - which is exactly the kind of number the ImportTrader mechanism "
    "discussed earlier could use. For this round, the decision is to NOT use it: keep Germany modelled as a "
    "standalone market, matching AMIRIS's own example-scenario convention, so this comparison isolates the "
    "same variables the 2015-2019 backtest already isolated. The Net Exports figure stays available for a "
    "later, explicit cross-border experiment rather than being folded in now."
)

# =====================================================================
pdf.add_page()
pdf.h1("The Load Profile Question, Properly Explained")
pdf.body(
    "Brainpool's demand figures (604.85 TWh inflexible + 14.97 electrolysis + 17.81 e-mobility + 18.69 heat "
    "pumps) are annual totals. AMIRIS needs 8,760 hourly values. Two methods were suggested: bdew.de "
    "(manual) and demandlib (Python package, part of the oemof energy-modelling toolkit). Both implement "
    "the same underlying method - BDEW's Standard Load Profile (Standardlastprofil, SLP) methodology - "
    "just by hand versus in code."
)

pdf.h2("What a BDEW Standard Load Profile actually is")
pdf.body(
    "BDEW publishes, for each customer class (H0 = households, G0-G6 = various commercial types, L0/L1/L2 "
    "= agricultural), a table of normalised quarter-hourly values, referenced to a customer using exactly "
    "1,000 kWh per year. There are 3 day-types (weekday, Saturday, Sunday/holiday) times 4 seasons (winter, "
    "summer, and two transition periods), giving 12 representative 96-point daily curves per customer class."
)

pdf.h2("The computation, step by step")
pdf.body(
    "1. For every calendar day of the target year, look up its season and day-type, and take the matching "
    "96-point representative curve.\n"
    "2. For H0 specifically, apply an additional 'dynamization' adjustment - a smooth day-of-year function "
    "that corrects the fact that households don't actually jump between 4 discrete seasonal blocks the way "
    "the raw table implies; they drift continuously. (The exact published coefficients for this function "
    "should be pulled from BDEW's own publication or demandlib's source directly rather than quoted from "
    "memory here - the concept matters more than memorising the polynomial.)\n"
    "3. Concatenate all 365 (or 366) days into one continuous series - 35,040 quarter-hour values.\n"
    "4. Compute a single scaling factor: your real target annual total, divided by the reference total the "
    "raw normalised curve sums to.\n"
    "5. Multiply every single quarter-hour value by that one scaling factor.\n"
    "6. Average every 4 consecutive quarter-hours down to hourly, to match AMIRIS's resolution."
)

pdf.h2("A worked numeric example (illustrative values, to show the mechanism)")
pdf.body(
    "Say one particular winter-weekday quarter-hour in the raw H0 table reads 65 W per 1,000 kWh of annual "
    "reference consumption (an illustrative figure, not a quoted real BDEW constant):"
)
pdf.code(
    "Target annual demand      = 604,850,000 MWh  =  604,850,000,000 kWh\n"
    "Reference annual demand   = 1,000 kWh   (what the raw table is normalised against)\n\n"
    "Scaling factor  =  604,850,000,000 / 1,000  =  604,850,000\n\n"
    "That quarter-hour's actual value  =  65 W  x  604,850,000\n"
    "                                   =  39,315,250,000 W\n"
    "                                   =  39,315.25 MW  for that one 15-minute interval"
)
pdf.body(
    "The same scaling factor is applied to all 35,040 quarter-hours, then every 4 are averaged into one "
    "hourly value - that's the entire mechanism, repeated 8,760 times."
)

pdf.h2("Why this isn't the efficient choice for our specific case")
pdf.body(
    "A single BDEW profile (H0, or any other) represents one customer CLASS's behavioural rhythm - "
    "households peak in the evening and go quiet on weekends; industry runs flatter across weekday daytime "
    "shifts and barely changes for weekends. Germany's real national demand is a mix of both, with "
    "industry making up close to half of consumption. Using H0 alone for a national total systematically "
    "overweights residential rhythm and underweights industrial rhythm - the resulting national shape "
    "would not resemble how Germany's grid actually behaves.\n\n"
    "Blending multiple BDEW classes by their national consumption share would fix that partially, but it's "
    "still a synthetic reconstruction built from average assumptions - it would not capture real weather-"
    "driven demand swings, actual holiday effects, or genuine industrial production variation the way an "
    "actually observed national load curve does. And this project already has a proven, working pipeline "
    "for pulling real German national hourly demand directly from ENTSO-E (used successfully for the 2023 "
    "build) - reconstructing a synthetic approximation of something we can source as a real observation is "
    "solving an already-solved problem, and solving it less accurately."
)

pdf.callout(
    "Where BDEW/demandlib genuinely does earn its place:",
    "Heat pumps specifically. Brainpool separated Warmepumpen out as its own 18.69 TWh figure precisely "
    "because heat-pump load behaves differently - it is strongly temperature-driven, peaking on cold winter "
    "mornings and evenings - and its share of total demand is growing fast as adoption increases, so an old "
    "real load curve's heating-related bump reflects mostly gas heating, not the much larger heat-pump load "
    "expected by 2027. demandlib's temperature-dependent heat-pump profile is built for exactly this, and "
    "using it here is not redundant - there is no equivalent real historical shape to borrow instead.",
    color=GOOD,
)

pdf.h2("My recommendation")
pdf.body(
    "Don't apply one BDEW/demandlib profile to the whole demand total. Shape each of Brainpool's four "
    "demand components separately, matching the tool to what each one actually needs:\n\n"
    "- Inflexible base demand (604.85 TWh) -> rescale a real recent German national hourly load curve "
    "(ENTSO-E, same method already proven for 2023) to this total.\n"
    "- Heat pumps (18.69 TWh) -> demandlib's temperature-dependent heat-pump profile - the one place this "
    "tool is the right fit.\n"
    "- Electrolysis (14.97 TWh) -> a near-flat assumption, since industrial electrolysers typically run "
    "close to constant for efficiency; documented explicitly as an assumption.\n"
    "- E-mobility (17.81 TWh) -> the least standardised of the four; requires picking and documenting an "
    "assumed shape (e.g. evening-peak, unless smart-charging is assumed instead).\n\n"
    "Sum the four resulting hourly series into one final load curve for AMIRIS. More work than one blanket "
    "profile, but it uses the exact split Brainpool already gave us, rather than discarding it before we've "
    "used it."
)

pdf.output("AMIRIS_2027_Data_Gaps_and_LoadProfile.pdf")
print("Saved AMIRIS_2027_Data_Gaps_and_LoadProfile.pdf")
