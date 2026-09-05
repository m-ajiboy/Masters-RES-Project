"""Breaks the AMIRIS-vs-Brainpool correlation down by month, hour-of-day, and weekday/weekend
for the CURRENT BEST build (Germany2027_FlexEMobility: 2016-base demand, real 2009 heat-pump
temperature, 30,000 MW import ceiling, 11-country blended import price, price-responsive
electrolysis, price-responsive/smart-charging e-mobility - zero shortage hours all year) - to
find WHERE the remaining tracking gap concentrates now that the weekday-alignment, import,
demand-year, and demand-flexibility fixes are all in place, rather than guessing at the next
lever. Follows the exact same method as the original Phase 10 breakdown
(plot_correlation_breakdown.py), pointed at the new best result - previous breakdown outputs
are left untouched."""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import openpyxl
import pandas as pd

ROOT = r"C:\Users\MuideenOA\Desktop\PyTut\Amiris"

wb = openpyxl.load_workbook(rf"{ROOT}\Brainpool 2027 output.xlsx", data_only=True)
ws = wb["Brainpool_output"]
rows = [(r[0], r[2]) for r in ws.iter_rows(min_row=4, values_only=True) if r[0] is not None]
bp = pd.DataFrame(rows, columns=["ts", "bp"]).set_index("ts")
bp.index = pd.to_datetime(bp.index)

dam = pd.read_csv(rf"{ROOT}\examples\backtest\Germany2027_FlexEMobility\result_FlexEMobility\DayAheadMarketSingleZone.csv", sep=";")
dam["ts"] = pd.to_datetime(dam["TimeStep"])
dam = dam.set_index("ts")

joined = bp.join(dam["ElectricityPriceInEURperMWH"]).dropna()
joined.columns = ["bp", "amiris"]
joined["month"] = joined.index.month
joined["hour"] = joined.index.hour
joined["weekday"] = joined.index.dayofweek < 5  # Mon-Fri = True

shortage_mask = joined["amiris"] >= 2999.9
print(f"Total hours: {len(joined)}, shortage hours: {shortage_mask.sum()}")
clean = joined[~shortage_mask]
print(f"Overall (excl-shortage) r={clean['bp'].corr(clean['amiris']):.4f}, "
      f"bias={(clean['amiris']-clean['bp']).mean():+.2f}, "
      f"mae={(clean['amiris']-clean['bp']).abs().mean():.2f}\n")

# ---- By month ----
month_stats = clean.groupby("month").apply(
    lambda g: pd.Series({
        "r": g["bp"].corr(g["amiris"]),
        "bias": (g["amiris"] - g["bp"]).mean(),
        "mae": (g["amiris"] - g["bp"]).abs().mean(),
    }), include_groups=False
)
print("=== By month ===")
print(month_stats.round(2).to_string())

# ---- By hour of day ----
hour_stats = clean.groupby("hour").apply(
    lambda g: pd.Series({
        "r": g["bp"].corr(g["amiris"]),
        "bias": (g["amiris"] - g["bp"]).mean(),
        "mae": (g["amiris"] - g["bp"]).abs().mean(),
    }), include_groups=False
)
print("\n=== By hour of day ===")
print(hour_stats.round(2).to_string())

# ---- Weekday vs weekend ----
print("\n=== Weekday vs weekend ===")
for is_weekday, label in [(True, "Weekday"), (False, "Weekend")]:
    g = clean[clean["weekday"] == is_weekday]
    r = g["bp"].corr(g["amiris"])
    bias = (g["amiris"] - g["bp"]).mean()
    mae = (g["amiris"] - g["bp"]).abs().mean()
    print(f"{label}: n={len(g)}  r={r:.3f}  bias={bias:+.2f}  mae={mae:.2f}")

# ---- Chart ----
fig, axes = plt.subplots(2, 2, figsize=(14, 10))

axes[0, 0].bar(month_stats.index, month_stats["r"], color="#0072B2")
axes[0, 0].set_title("Correlation (r) by month")
axes[0, 0].set_xlabel("Month")
axes[0, 0].set_ylabel("r")
axes[0, 0].axhline(clean["bp"].corr(clean["amiris"]), color="#D55E00", linestyle="--", label="full-year avg")
axes[0, 0].legend(fontsize=8)
axes[0, 0].grid(alpha=0.3)

axes[0, 1].bar(month_stats.index, month_stats["bias"], color="#009E73")
axes[0, 1].set_title("Bias (AMIRIS - Brainpool) by month")
axes[0, 1].set_xlabel("Month")
axes[0, 1].set_ylabel("EUR/MWh")
axes[0, 1].axhline(0, color="black", linewidth=0.8)
axes[0, 1].grid(alpha=0.3)

axes[1, 0].bar(hour_stats.index, hour_stats["r"], color="#0072B2")
axes[1, 0].set_title("Correlation (r) by hour of day")
axes[1, 0].set_xlabel("Hour (0-23)")
axes[1, 0].set_ylabel("r")
axes[1, 0].axhline(clean["bp"].corr(clean["amiris"]), color="#D55E00", linestyle="--", label="full-year avg")
axes[1, 0].legend(fontsize=8)
axes[1, 0].grid(alpha=0.3)

axes[1, 1].bar(hour_stats.index, hour_stats["bias"], color="#009E73")
axes[1, 1].set_title("Bias (AMIRIS - Brainpool) by hour of day")
axes[1, 1].set_xlabel("Hour (0-23)")
axes[1, 1].set_ylabel("EUR/MWh")
axes[1, 1].axhline(0, color="black", linewidth=0.8)
axes[1, 1].grid(alpha=0.3)

fig.suptitle("Where does AMIRIS-vs-Brainpool tracking break down NOW?\n(current best build: 2016-base demand + import blend + flex electrolysis + smart EV charging, zero shortage hours)",
             fontsize=13, fontweight="bold")
plt.tight_layout()
plt.savefig(rf"{ROOT}\correlation_breakdown_flexbuild.png", dpi=150)
print("\nSaved correlation_breakdown_flexbuild.png")
