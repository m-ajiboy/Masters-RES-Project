"""Scatter plots of AMIRIS hourly price vs. Brainpool's real 2027 hourly price, one panel
per build tested so far - the visual form of the correlation (r) numbers already computed.
Each point is one hour of the year. A perfectly correlated build would have every point
sitting on the diagonal red reference line."""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import openpyxl
import pandas as pd

ROOT = r"C:\Users\MuideenOA\Desktop\PyTut\Amiris"

wb = openpyxl.load_workbook(rf"{ROOT}\Brainpool 2027 output.xlsx", data_only=True)
ws = wb["Brainpool_output"]
rows = [(r[0], r[2]) for r in ws.iter_rows(min_row=4, values_only=True) if r[0] is not None]
bp = pd.DataFrame(rows, columns=["ts", "bp"]).set_index("ts")
bp.index = pd.to_datetime(bp.index)

BUILDS = {
    "V1 no-import": rf"{ROOT}\examples\backtest\Germany2027\result_Germany2027_rerun\DayAheadMarketSingleZone.csv",
    "V1 with-import (37.65k, FINAL)": rf"{ROOT}\examples\backtest\Germany2027_V1WithImport_Fix\result_V1WithImport_Fix\DayAheadMarketSingleZone.csv",
    "V2 no-import, original weather": rf"{ROOT}\examples\backtest\Germany2027_DemandV2\result_DemandV2_rerun\DayAheadMarketSingleZone.csv",
    "V2 no-import, 2009 weather": rf"{ROOT}\examples\backtest\Germany2027_Weather2009\result_Weather2009\DayAheadMarketSingleZone.csv",
    "V2 with-import (30k), original weather": rf"{ROOT}\examples\backtest\Germany2027_WithImport_Fix\result_WithImport_Fix30k\DayAheadMarketSingleZone.csv",
    "V2 with-import (30k), 2009 weather": rf"{ROOT}\examples\backtest\Germany2027_Weather2009_WithImport\result_Weather2009_WithImport\DayAheadMarketSingleZone.csv",
}

fig, axes = plt.subplots(2, 3, figsize=(16, 10))
axes = axes.flatten()

for ax, (label, path) in zip(axes, BUILDS.items()):
    dam = pd.read_csv(path, sep=";")
    dam["ts"] = pd.to_datetime(dam["TimeStep"])
    dam = dam.set_index("ts")
    joined = bp.join(dam["ElectricityPriceInEURperMWH"]).dropna()
    x = joined["bp"]
    y = joined["ElectricityPriceInEURperMWH"]
    r = x.corr(y)

    ax.scatter(x, y, s=4, alpha=0.25, color="#0072B2", edgecolors="none")
    lim = max(x.max(), min(y.max(), 500))  # cap the diagonal reference at a sane scale
    ax.plot([0, lim], [0, lim], color="#D55E00", linewidth=1.2, linestyle="--", label="perfect match (y=x)")
    ax.set_xlabel("Brainpool price (EUR/MWh)")
    ax.set_ylabel("AMIRIS price (EUR/MWh)")
    ax.set_title(f"{label}\nr = {r:.3f}", fontsize=11)
    ax.legend(fontsize=8, loc="upper left")
    ax.grid(alpha=0.3)

plt.tight_layout()
plt.savefig(rf"{ROOT}\correlation_scatter_all_builds.png", dpi=150)
print("Saved correlation_scatter_all_builds.png")
