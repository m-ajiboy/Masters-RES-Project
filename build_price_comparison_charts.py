"""Builds a comprehensive set of price comparison charts: AMIRIS (our model) vs Brainpool's
real price, for each of 2027, 2028, 2029, using the most accurate build available for each
year. Covers full-year overlay, a zoomed detail window, correlation scatter, price duration
curves, and a monthly bias comparison across all three years."""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import numpy as np
import pandas as pd

from brainpool_multiyear_data import load_brainpool_price

ROOT = r"C:\Users\MuideenOA\Desktop\PyTut\Amiris"
OUT = rf"{ROOT}\Presentation"

AMIRIS_COLOR = "#2471A3"
BP_COLOR = "#D68910"
NAVY = "#1F3A4D"

RESULTS = {
    2027: rf"{ROOT}\examples\backtest\Germany2027_Feb29DropFix\result_Germany2027_Feb29DropFix\DayAheadMarketSingleZone.csv",
    2028: rf"{ROOT}\examples\backtest\Germany2028\result_Germany2028\DayAheadMarketSingleZone.csv",
    2029: rf"{ROOT}\examples\backtest\Germany2029_Feb29DropFix\result_Germany2029_Feb29DropFix\DayAheadMarketSingleZone.csv",
}
LABELS = {2027: "2027 (final, bug-fixed)", 2028: "2028 (out-of-sample)", 2029: "2029 (final, bug-fixed)"}


def load_amiris(path):
    dam = pd.read_csv(path, sep=";")
    dam["ts"] = pd.to_datetime(dam["TimeStep"])
    return dam.set_index("ts")["ElectricityPriceInEURperMWH"]


data = {}
for year in (2027, 2028, 2029):
    bp_full = load_brainpool_price(year)
    bp = bp_full[bp_full.index < f"{year}-12-31"] if year == 2028 else bp_full
    amiris = load_amiris(RESULTS[year])
    joined = pd.DataFrame({"AMIRIS": amiris, "Brainpool": bp}).dropna()
    data[year] = joined
    r = joined["AMIRIS"].corr(joined["Brainpool"])
    print(f"{year}: {len(joined)} hours, r={r:.4f}, AMIRIS mean={joined['AMIRIS'].mean():.2f}, "
          f"Brainpool mean={joined['Brainpool'].mean():.2f}")

# =============================================================================
# Figure 1: full-year overlay, one panel per year
# =============================================================================
fig, axes = plt.subplots(3, 1, figsize=(15, 12), sharex=False)
for ax, year in zip(axes, (2027, 2028, 2029)):
    d = data[year]
    ax.plot(d.index, d["Brainpool"], color=BP_COLOR, linewidth=0.6, label="Brainpool (real forecast)", alpha=0.9)
    ax.plot(d.index, d["AMIRIS"], color=AMIRIS_COLOR, linewidth=0.6, label="AMIRIS (our model)", alpha=0.75)
    r = d["AMIRIS"].corr(d["Brainpool"])
    shortage = d["AMIRIS"] >= 2999.9
    # cap the y-axis using the 99.5th percentile of BOTH series (Brainpool has its own rare
    # extreme hours too), so a handful of outliers from either side don't flatten the rest
    cap = max(d["AMIRIS"].quantile(0.995), d["Brainpool"].quantile(0.995)) * 1.3
    n_off = int(((d["AMIRIS"] > cap) | (d["Brainpool"] > cap)).sum())
    ax.set_ylim(top=cap)
    if n_off > 0:
        ax.text(0.99, 0.95, f"+ {n_off} extreme hour(s) off-scale (up to "
                f"{max(d['AMIRIS'].max(), d['Brainpool'].max()):.0f} EUR/MWh)",
                transform=ax.transAxes, ha="right", va="top", fontsize=9, color="#B03A2E", fontweight="bold")
    ax.set_title(f"{LABELS[year]} - full year (r = {r:.3f})", fontsize=13, fontweight="bold", color=NAVY)
    ax.set_ylabel("EUR/MWh")
    ax.legend(loc="upper left", fontsize=9)
    ax.grid(alpha=0.3)
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%b"))
fig.suptitle("Full-Year Price Comparison: AMIRIS vs. Brainpool", fontsize=16, fontweight="bold", color=NAVY, y=1.0)
plt.tight_layout()
plt.savefig(rf"{OUT}\price_fullyear_overlay.png", dpi=150, bbox_inches="tight")
plt.close()
print("Saved price_fullyear_overlay.png")

# =============================================================================
# Figure 2: zoomed 3-week detail window (same calendar window each year, mid-January
# through early February - a period with real winter demand/price volatility)
# =============================================================================
fig, axes = plt.subplots(3, 1, figsize=(15, 12))
for ax, year in zip(axes, (2027, 2028, 2029)):
    d = data[year]
    window = d[(d.index >= f"{year}-01-08") & (d.index < f"{year}-01-29")]
    ax.plot(window.index, window["Brainpool"], color=BP_COLOR, linewidth=1.6, label="Brainpool (real forecast)", marker="")
    ax.plot(window.index, window["AMIRIS"], color=AMIRIS_COLOR, linewidth=1.6, label="AMIRIS (our model)", marker="")
    # cap the y-axis to keep ordinary-hour detail visible even if a shortage spike (3,000
    # EUR/MWh) falls inside this window - annotate it instead of letting it dominate the scale
    normal_max = max(window["Brainpool"].max(), window.loc[window["AMIRIS"] < 2999.9, "AMIRIS"].max())
    spikes = window[window["AMIRIS"] >= 2999.9]
    if len(spikes) > 0:
        cap = normal_max * 1.25
        ax.set_ylim(top=cap)
        for spike_ts in spikes.index:
            ax.annotate(f"shortage spike\n(3,000 EUR/MWh)\n{spike_ts.strftime('%d %b, %H:%M')}",
                        xy=(spike_ts, cap * 0.97), xytext=(spike_ts, cap * 0.75),
                        fontsize=9, ha="center", color="#B03A2E", fontweight="bold",
                        arrowprops=dict(arrowstyle="->", color="#B03A2E"))
    ax.set_title(f"{LABELS[year]} - three-week detail (8-28 Jan)", fontsize=13, fontweight="bold", color=NAVY)
    ax.set_ylabel("EUR/MWh")
    ax.legend(loc="upper right", fontsize=9)
    ax.grid(alpha=0.3)
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%d %b"))
fig.suptitle("Zoomed Detail: Where Do the Two Series Move Together, and Where Do They Diverge?", fontsize=15, fontweight="bold", color=NAVY, y=1.0)
plt.tight_layout()
plt.savefig(rf"{OUT}\price_zoomed_detail.png", dpi=150, bbox_inches="tight")
plt.close()
print("Saved price_zoomed_detail.png")

# =============================================================================
# Figure 3: correlation scatter, one panel per year
# =============================================================================
fig, axes = plt.subplots(1, 3, figsize=(16, 5.5))
for ax, year in zip(axes, (2027, 2028, 2029)):
    d = data[year]
    shortage = d["AMIRIS"] >= 2999.9
    ax.scatter(d.loc[~shortage, "Brainpool"], d.loc[~shortage, "AMIRIS"], s=4, alpha=0.25, color=AMIRIS_COLOR, label="Ordinary hours")
    if shortage.sum() > 0:
        ax.scatter(d.loc[shortage, "Brainpool"], d.loc[shortage, "AMIRIS"], s=30, color="#B03A2E", label=f"Shortage hours ({shortage.sum()})", zorder=5)
    ax.plot([0, 350], [0, 350], color="grey", linestyle="--", linewidth=1, label="Perfect match line")
    ax.set_xlim(-100, 350)
    ax.set_ylim(-100, 3100)
    r_all = d["Brainpool"].corr(d["AMIRIS"])
    r_excl = d.loc[~shortage, "Brainpool"].corr(d.loc[~shortage, "AMIRIS"])
    ax.set_title(f"{year}\nall-hours r={r_all:.3f}, ordinary-hours r={r_excl:.3f}", fontsize=12, fontweight="bold", color=NAVY)
    ax.set_xlabel("Brainpool real price (EUR/MWh)")
    if year == 2027:
        ax.set_ylabel("AMIRIS price (EUR/MWh)")
    ax.legend(fontsize=8, loc="upper left")
    ax.grid(alpha=0.3)
fig.suptitle("Correlation Scatter: How Closely Does AMIRIS Track Brainpool's Real Price?", fontsize=15, fontweight="bold", color=NAVY)
plt.tight_layout()
plt.savefig(rf"{OUT}\price_correlation_scatter.png", dpi=150, bbox_inches="tight")
plt.close()
print("Saved price_correlation_scatter.png")

# =============================================================================
# Figure 4: price duration curves (sorted descending), overlay per year
# =============================================================================
fig, axes = plt.subplots(1, 3, figsize=(16, 5.5))
for ax, year in zip(axes, (2027, 2028, 2029)):
    d = data[year]
    amiris_sorted = np.sort(d["AMIRIS"].values)[::-1]
    bp_sorted = np.sort(d["Brainpool"].values)[::-1]
    pct = np.linspace(0, 100, len(amiris_sorted))
    ax.plot(pct, bp_sorted, color=BP_COLOR, linewidth=2, label="Brainpool (real)")
    ax.plot(pct, amiris_sorted, color=AMIRIS_COLOR, linewidth=2, label="AMIRIS (ours)")
    ax.set_title(f"{year}", fontsize=13, fontweight="bold", color=NAVY)
    ax.set_xlabel("% of hours, sorted highest to lowest")
    if year == 2027:
        ax.set_ylabel("Price (EUR/MWh)")
    ax.legend(fontsize=9)
    ax.grid(alpha=0.3)
    ax.set_ylim(-120, 500)
fig.suptitle("Price Duration Curves: Comparing the Full Shape of the Price Distribution", fontsize=15, fontweight="bold", color=NAVY)
plt.tight_layout()
plt.savefig(rf"{OUT}\price_duration_curves.png", dpi=150, bbox_inches="tight")
plt.close()
print("Saved price_duration_curves.png")

# =============================================================================
# Figure 5: monthly average bias, all three years overlaid
# =============================================================================
fig, ax = plt.subplots(figsize=(12, 6))
colors = {2027: "#1E8449", 2028: "#B03A2E", 2029: "#2471A3"}
for year in (2027, 2028, 2029):
    d = data[year].copy()
    shortage = d["AMIRIS"] >= 2999.9
    clean = d[~shortage]
    clean = clean.assign(month=clean.index.month)
    monthly_bias = clean.groupby("month").apply(lambda g: (g["AMIRIS"] - g["Brainpool"]).mean())
    ax.plot(monthly_bias.index, monthly_bias.values, marker="o", linewidth=2, color=colors[year], label=str(year))
ax.axhline(0, color="black", linewidth=0.8)
ax.set_xlabel("Month")
ax.set_ylabel("Bias: AMIRIS - Brainpool (EUR/MWh)")
ax.set_title("Monthly Bias Pattern, All Three Years (ordinary hours only)", fontsize=15, fontweight="bold", color=NAVY)
ax.set_xticks(range(1, 13))
ax.legend(fontsize=11, title="Year")
ax.grid(alpha=0.3)
plt.tight_layout()
plt.savefig(rf"{OUT}\price_monthly_bias_allyears.png", dpi=150, bbox_inches="tight")
plt.close()
print("Saved price_monthly_bias_allyears.png")

print("\nAll price comparison charts saved to Presentation/")
