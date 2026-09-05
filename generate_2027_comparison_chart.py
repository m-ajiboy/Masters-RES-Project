"""Builds the AMIRIS-vs-Brainpool 2027 comparison chart: a price duration curve (top)
showing how AMIRIS's shortage-hour ceiling pricing dominates the mean, and monthly
average prices (bottom) showing the underlying price LEVEL tracks reasonably well."""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd

ROOT = r"C:\Users\MuideenOA\Desktop\PyTut\Amiris"
df = pd.read_csv(rf"{ROOT}\comparison_2027_aligned.csv", index_col=0, parse_dates=True)

COLORS = {
    "brainpool_price": "#1F3A4D",
    "V1 no-import": "#963C28",
    "V1 with-import": "#C97B4A",
    "V2 no-import": "#3A6B47",
    "V2 with-import": "#5FA86B",
}
LABELS = {
    "brainpool_price": "Brainpool 2027 forecast",
    "V1 no-import": "AMIRIS V1, no-import",
    "V1 with-import": "AMIRIS V1, with-import",
    "V2 no-import": "AMIRIS V2, no-import",
    "V2 with-import": "AMIRIS V2, with-import",
}

fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(13, 11))

# ---- Top: price duration curve (capped at 500 EUR/MWh to keep the interesting region visible) ----
for col in ["brainpool_price", "V1 no-import", "V1 with-import", "V2 no-import", "V2 with-import"]:
    sorted_vals = df[col].sort_values(ascending=False).values
    pct = 100 * (1 + pd.RangeIndex(len(sorted_vals))) / len(sorted_vals)
    ax1.plot(pct, sorted_vals, label=LABELS[col], color=COLORS[col], linewidth=1.4)
ax1.axhline(3000, color="grey", linestyle=":", linewidth=1)
ax1.text(50, 3050, "AMIRIS Value of Lost Load ceiling (3,000 EUR/MWh)", fontsize=8, color="grey")
ax1.set_ylim(-100, 3200)
ax1.set_xlabel("% of hours, sorted descending")
ax1.set_ylabel("EUR/MWh")
ax1.set_title("Price duration curve, full year 2027 — AMIRIS's shortage-hour ceiling dominates its own mean")
ax1.legend(loc="upper right", fontsize=9)
ax1.grid(alpha=0.3)

# ---- Bottom: monthly average price, EXCLUDING AMIRIS shortage hours (a fair level comparison) ----
monthly = pd.DataFrame(index=range(1, 13))
for col in ["brainpool_price", "V1 no-import", "V1 with-import", "V2 no-import", "V2 with-import"]:
    mask = df[col] < 2999.9
    s = df.loc[mask, col]
    monthly[col] = s.groupby(s.index.month).mean()
for col in monthly.columns:
    ax2.plot(monthly.index, monthly[col], marker="o", label=LABELS[col], color=COLORS[col], linewidth=1.6)
ax2.set_xticks(range(1, 13))
ax2.set_xlabel("Month, 2027")
ax2.set_ylabel("EUR/MWh")
ax2.set_title("Monthly average price, excluding AMIRIS shortage hours — the underlying price LEVEL comparison")
ax2.legend(loc="upper left", fontsize=9)
ax2.grid(alpha=0.3)

plt.tight_layout()
plt.savefig(rf"{ROOT}\amiris_brainpool_2027_comparison_chart.png", dpi=150)
print(f"Saved {ROOT}\\amiris_brainpool_2027_comparison_chart.png")
