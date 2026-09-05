"""Compares the 2009-weather renewable profiles (renewables.ninja) against what they
replaced: Brainpool's own regional-averaged profiles for wind onshore and solar, and
AMIRIS's own reused profile for wind offshore (Brainpool never supplied an offshore-
specific shape - established earlier in this build). One-week raw zoom plus a full-year
duration curve for each of the three technologies."""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

ROOT = r"C:\Users\MuideenOA\Desktop\PyTut\Amiris"
HOURS = 8760

def load_series(path):
    df = pd.read_csv(path, sep=";", header=None, names=["ts", "cf"])
    df["ts"] = pd.to_datetime(df["ts"], format="%Y-%m-%d_%H:%M:%S")
    return df.set_index("ts")["cf"].values[:HOURS]

ORIGINAL_DIR = rf"{ROOT}\examples\backtest\Germany2027_DemandV2\timeseries"
NEW_DIR = rf"{ROOT}\examples\backtest\Germany2027_Weather2009\timeseries"

TECHS = [
    ("wind_onshore_profile.csv", "Wind onshore", "Brainpool (regional average)"),
    ("wind_offshore_profile.csv", "Wind offshore", "AMIRIS own (reused, no Brainpool shape exists)"),
    ("solar_openfield_profile.csv", "Solar (openfield)", "Brainpool (regional average)"),
]

idx = pd.date_range("2027-01-01", periods=HOURS, freq="h")
week_mask = (idx >= pd.Timestamp("2027-01-11")) & (idx < pd.Timestamp("2027-01-18"))
pct = 100 * (1 + np.arange(HOURS)) / HOURS

fig, axes = plt.subplots(3, 2, figsize=(15, 14))

for row, (fname, label, orig_label) in enumerate(TECHS):
    original = load_series(rf"{ORIGINAL_DIR}\{fname}")
    new = load_series(rf"{NEW_DIR}\{fname}")
    r = np.corrcoef(original, new)[0, 1]

    ax_week = axes[row, 0]
    ax_week.plot(idx[week_mask], original[week_mask], color="#0072B2", linewidth=1.6, label=f"Original ({orig_label})")
    ax_week.plot(idx[week_mask], new[week_mask], color="#D55E00", linewidth=1.6, label="2009 weather (renewables.ninja)")
    ax_week.set_title(f"{label} - one week (11-17 Jan 2027)")
    ax_week.set_ylabel("Capacity factor")
    ax_week.legend(fontsize=8)
    ax_week.grid(alpha=0.3)
    ax_week.tick_params(axis="x", rotation=25)

    ax_dur = axes[row, 1]
    ax_dur.plot(pct, np.sort(original)[::-1], color="#0072B2", linewidth=1.8, label=f"Original ({orig_label})")
    ax_dur.plot(pct, np.sort(new)[::-1], color="#D55E00", linewidth=1.8, label="2009 weather (renewables.ninja)")
    ax_dur.set_title(f"{label} - duration curve, full year, r={r:.3f}")
    ax_dur.set_xlabel("% of hours, sorted descending")
    ax_dur.set_ylabel("Capacity factor")
    ax_dur.legend(fontsize=8)
    ax_dur.grid(alpha=0.3)

    print(f"{label}: original mean CF={original.mean():.3f}, 2009 mean CF={new.mean():.3f}, "
          f"hour-to-hour correlation r={r:.3f}")

plt.tight_layout()
plt.savefig(rf"{ROOT}\renewable_profile_2009_vs_original.png", dpi=150)
print("\nSaved renewable_profile_2009_vs_original.png")
