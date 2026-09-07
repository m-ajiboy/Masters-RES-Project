"""Price duration curve: baseline (pre-coupling, Germany2027_Feb29DropFix) vs Phase 37
(best coupled result, Germany2027_MarketCoupling_ROEFlex) vs Brainpool's real 2027 forecast,
each hour's price sorted descending and plotted against its rank - the standard way to show
how a shortage-hour tail shrinks (or doesn't) without needing to look at all 8,760 individual
hours. Directly visualises this project's single best real result."""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import pandas as pd
from brainpool_multiyear_data import load_brainpool_price

ROOT = r"C:\Users\MuideenOA\Desktop\PyTut\Amiris\examples\backtest"
BASELINE = rf"{ROOT}\Germany2027_Feb29DropFix\result_Germany2027_Feb29DropFix\DayAheadMarketSingleZone.csv"
PHASE37 = rf"{ROOT}\Germany2027_MarketCoupling_ROEFlex\result_Germany2027_MarketCoupling_ROEFlex\DayAheadMarketMultiZone.csv"


def load_singlezone(path):
    df = pd.read_csv(path, sep=";")
    df["ts"] = pd.to_datetime(df["TimeStep"])
    return df.set_index("ts")["ElectricityPriceInEURperMWH"]


def load_multizone_de(path):
    df = pd.read_csv(path, sep=";")
    df["ts"] = pd.to_datetime(df["TimeStep"])
    return df[df["AgentId"] == 1].set_index("ts")["ElectricityPriceInEURperMWH"]


baseline = load_singlezone(BASELINE)
phase37 = load_multizone_de(PHASE37)
bp = load_brainpool_price(2027)

joined = pd.DataFrame({"Baseline (pre-coupling)": baseline, "Phase 37 (best coupled result)": phase37,
                        "Brainpool (real forecast)": bp}).dropna()
n = len(joined)

fig, ax = plt.subplots(figsize=(12, 7))

styles = {
    "Baseline (pre-coupling)": {"color": "#96453c", "lw": 2.2, "zorder": 3},
    "Phase 37 (best coupled result)": {"color": "#1f3a4d", "lw": 2.6, "zorder": 4},
    "Brainpool (real forecast)": {"color": "#6b6b6b", "lw": 2.0, "ls": "--", "zorder": 2},
}
for col, style in styles.items():
    sorted_vals = joined[col].sort_values(ascending=False).values
    ax.plot(range(1, n + 1), sorted_vals, label=col, **style)

ax.set_xlabel("Hour rank (1 = highest price of the year)", fontsize=11)
ax.set_ylabel("Price (EUR/MWh)", fontsize=11)
ax.set_title("Price Duration Curve: Before vs. After the Cross-Border Coupling Build (2027)",
             fontsize=14.5, weight="bold", pad=12)
ax.legend(fontsize=11, loc="upper right", frameon=True)
ax.grid(alpha=0.3)
ax.set_xlim(0, n)
ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"{x:,.0f}"))

# Zoomed inset showing the shortage-hour tail in detail (top ~200 hours), since the main
# axes get compressed by the 3,000 EUR/MWh shortage ceiling.
axins = ax.inset_axes([0.42, 0.32, 0.5, 0.45])
for col, style in styles.items():
    sorted_vals = joined[col].sort_values(ascending=False).values
    axins.plot(range(1, n + 1), sorted_vals, **style)
axins.set_xlim(0, 200)
axins.set_ylim(0, 3100)
axins.set_title("Zoomed: the top 200 hours", fontsize=9.5)
axins.grid(alpha=0.3)
axins.tick_params(labelsize=8)

note = (
    f"Baseline: {(baseline >= 2999.9).sum()} shortage hours (price at the 3,000 EUR/MWh ceiling). "
    f"Phase 37 (coupled): {(phase37 >= 2999.9).sum()} shortage hours. "
    f"Brainpool's real forecast: {(bp >= 2999.9).sum()} shortage hours, for reference."
)
fig.text(0.5, 0.01, note, ha="center", fontsize=10, style="italic", color="#3a3a3a")

plt.tight_layout(rect=[0, 0.03, 1, 1])
out_path = r"C:\Users\MuideenOA\Desktop\PyTut\Amiris\chart_price_duration_curve.png"
plt.savefig(out_path, dpi=180, bbox_inches="tight", facecolor="white")
print(f"Saved {out_path}")
print(note)
