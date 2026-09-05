"""Generates a chart showing the hard coal price conversion pipeline: Brainpool's raw
USD/tonne series alongside the converted EUR/MWh series actually written into
hard_coal_price.csv, for the Germany2027 build documentation.
"""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import openpyxl
from pathlib import Path

ROOT = Path(__file__).parent
XLSX = ROOT / "Amiris_Inputdata_EN.xlsx"

wb = openpyxl.load_workbook(XLSX, data_only=True)
ws = wb["Variable_cost"]
headers = [c.value for c in ws[1]]
headers[0] = "Date"

dates, usd_tonne, usd_eur, eur_mwh = [], [], [], []
COAL_MWH_PER_TONNE = 8.141

for r in ws.iter_rows(min_row=3, values_only=True):
    row = dict(zip(headers, r))
    if row["Date"] is None:
        continue
    dates.append(row["Date"])
    usd_tonne.append(row["Hard Coal [USD/tonne]"])
    usd_eur.append(row["USD Exchange Rate [USD/EUR]"])
    eur_mwh.append((row["Hard Coal [USD/tonne]"] / row["USD Exchange Rate [USD/EUR]"]) / COAL_MWH_PER_TONNE)

fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(7.5, 6.2), sharex=True)
fig.suptitle("Hard Coal Price Conversion: Brainpool 2027 Data → AMIRIS Input", fontsize=12, fontweight="bold")

ax1.plot(dates, usd_tonne, marker="o", color="#8a5a2b", linewidth=2, markersize=4)
ax1.set_ylabel("USD / tonne", fontsize=10)
ax1.set_title("Step 1: Brainpool's raw series (hard_coal_price.csv, before conversion)", fontsize=9.5, loc="left")
ax1.grid(alpha=0.3)

ax2.plot(dates, eur_mwh, marker="o", color="#1f3a4d", linewidth=2, markersize=4)
ax2.set_ylabel("EUR / MWh (thermal)", fontsize=10)
ax2.set_title("Step 2: Converted series actually written to hard_coal_price.csv\n"
              "(EUR/MWh = [USD/tonne ÷ USD-per-EUR rate] ÷ 8.141 MWh/tonne)", fontsize=9.5, loc="left")
ax2.grid(alpha=0.3)
ax2.xaxis.set_major_formatter(mdates.DateFormatter("%b %Y"))
fig.autofmt_xdate()

plt.tight_layout(rect=[0, 0, 1, 0.95])
out_path = ROOT / "hard_coal_conversion_chart.png"
plt.savefig(out_path, dpi=180)
print(f"Saved {out_path}")
print(f"Jan 2027: {usd_tonne[0]:.2f} USD/t, rate {usd_eur[0]:.4f} USD/EUR -> {eur_mwh[0]:.2f} EUR/MWh")
