"""Compares AMIRIS's own reference demand profile (Germany2019's real load.csv, the shape
that ships with AMIRIS itself) against our two built 2027 profiles (V1 and V2): a raw
hourly overlay (aligned by hour-of-year position, ignoring the different calendar years)
and a load duration curve (hours sorted by demand, descending)."""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

ROOT = r"C:\Users\MuideenOA\Desktop\PyTut\Amiris"
HOURS = 8760

def load_series(path, sep=";"):
    df = pd.read_csv(path, sep=sep, header=None, names=["ts", "mw"])
    return df["mw"].values[:HOURS]

amiris = load_series(rf"{ROOT}\examples\backtest\Germany2019\timeseries\load.csv")
v1 = load_series(rf"{ROOT}\examples\backtest\Germany2027\timeseries\load_v1_bdew.csv")
v2 = load_series(rf"{ROOT}\examples\backtest\Germany2027_DemandV2\timeseries\load_v2_split.csv")

hour_of_year = np.arange(HOURS)

fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(14, 11))

# ---- Panel 1: raw hourly overlay, aligned by hour-of-year (not actual calendar date) ----
ax1.plot(hour_of_year, amiris, color="#0072B2", linewidth=0.5, alpha=0.85, label=f"AMIRIS own (Germany2019 real) - {amiris.mean():,.0f} MW avg")
ax1.plot(hour_of_year, v1, color="#D55E00", linewidth=0.5, alpha=0.85, label=f"V1 (BDEW-for-everything, 2027) - {v1.mean():,.0f} MW avg")
ax1.plot(hour_of_year, v2, color="#009E73", linewidth=0.5, alpha=0.85, label=f"V2 (component-split, 2027) - {v2.mean():,.0f} MW avg")
ax1.set_xlabel("Hour of year (0 = Jan 1st 00:00, ignoring actual calendar year)")
ax1.set_ylabel("Load (MW)")
ax1.set_title("Raw hourly demand: AMIRIS's own reference profile vs. V1 vs. V2")
ax1.legend(loc="upper right", fontsize=9)
ax1.grid(alpha=0.3)

# ---- Panel 2: load duration curve (sorted descending) ----
pct = 100 * (1 + np.arange(HOURS)) / HOURS
for data, color, label in [
    (amiris, "#0072B2", "AMIRIS own (Germany2019 real)"),
    (v1, "#D55E00", "V1 (BDEW-for-everything)"),
    (v2, "#009E73", "V2 (component-split)"),
]:
    sorted_vals = np.sort(data)[::-1]
    ax2.plot(pct, sorted_vals, color=color, linewidth=2.2, label=label)
ax2.set_xlabel("% of hours in the year, sorted from highest demand to lowest")
ax2.set_ylabel("Load (MW)")
ax2.set_title("Load duration curve")
ax2.legend(loc="upper right", fontsize=9)
ax2.grid(alpha=0.3)

plt.tight_layout()
plt.savefig(rf"{ROOT}\amiris_v1_v2_load_comparison.png", dpi=150)
print("Saved amiris_v1_v2_load_comparison.png")

print(f"\nAMIRIS own (2019 real):  total {amiris.sum()/1e6:.1f} TWh, peak {amiris.max():,.0f} MW, min {amiris.min():,.0f} MW")
print(f"V1 (2027):               total {v1.sum()/1e6:.1f} TWh, peak {v1.max():,.0f} MW, min {v1.min():,.0f} MW")
print(f"V2 (2027):               total {v2.sum()/1e6:.1f} TWh, peak {v2.max():,.0f} MW, min {v2.min():,.0f} MW")
