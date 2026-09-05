"""Builds a chart visualizing the negative-price-floor sweep test (test_negative_price_floor.py):
for each of 2027/2028/2029, how correlation and bias against Brainpool change as AMIRIS's
reported price is clipped at increasingly less-negative floors. Reads directly from the real
sweep output (_floor_sweep_results.csv) - no numbers re-entered by hand. Top row: correlation
(all-hours and excl-shortage). Bottom row: all-hours bias. Makes the honest finding visible at
a glance: correlation stays essentially flat (or gets worse) while bias swings sharply -
confirming the floor is not a meaningful lever, only a bias cosmetic.
"""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd

NAVY = "#1F3A4D"
AMBER = "#D68910"
RED = "#B03A2E"
GREY = "#5A605C"

df = pd.read_csv(r"C:\Users\MuideenOA\Desktop\PyTut\Amiris\_floor_sweep_results.csv")
# "none(-500)" behaves identically to -500 in every row (confirmed: 0 hours clipped) - plot it
# at x=-500 so the baseline sits at the correct, real position on the floor axis.
df["floor_x"] = df["floor"].apply(lambda f: -500 if f == "none(-500)" else int(f))
df = df.sort_values("floor_x")

years = [2027, 2028, 2029]
fig, axes = plt.subplots(2, 3, figsize=(16, 9), sharex=True)

for col, year in enumerate(years):
    sub = df[df["year"] == year]
    baseline = sub[sub["floor"] == "none(-500)"].iloc[0]

    ax = axes[0, col]
    ax.plot(sub["floor_x"], sub["r_all"], marker="o", color=NAVY, linewidth=2, label="All-hours r")
    ax.plot(sub["floor_x"], sub["r_excl"], marker="s", color=AMBER, linewidth=2, label="Excl-shortage r")
    ax.axvline(-500, color=GREY, linestyle=":", linewidth=1)
    ax.scatter([-500], [baseline["r_all"]], color=RED, zorder=5, s=60)
    ax.annotate("current build\n(real -500 engine floor,\nnever actually reached)",
                xy=(-500, baseline["r_all"]), xytext=(-470, baseline["r_all"] - 0.09),
                fontsize=7.5, color=RED, ha="left")
    ax.set_title(f"{year}", fontsize=13, fontweight="bold", color=NAVY)
    ax.set_ylabel("Correlation" if col == 0 else "")
    ax.set_ylim(0.0, 0.75)
    ax.grid(alpha=0.3)
    if col == 0:
        ax.legend(fontsize=8, loc="lower right")

    ax = axes[1, col]
    ax.plot(sub["floor_x"], sub["bias"], marker="o", color="#6C3483", linewidth=2)
    ax.axhline(0, color="black", linewidth=0.8)
    ax.axvline(-500, color=GREY, linestyle=":", linewidth=1)
    ax.set_xlabel("Price floor applied (EUR/MWh)")
    ax.set_ylabel("All-hours bias\n(AMIRIS - Brainpool, EUR/MWh)" if col == 0 else "")
    ax.grid(alpha=0.3)
    ax.set_ylim(-16, 47)

fig.suptitle(
    "Price Floor Sweep (Negative Through Positive): Correlation Only Gets Worse Above -50 EUR/MWh\n"
    "(post-hoc price clip on already-simulated results - not a re-simulation; see caveat in report)",
    fontsize=13.5, fontweight="bold", color=NAVY, y=1.0)
plt.tight_layout()
plt.savefig(r"C:\Users\MuideenOA\Desktop\PyTut\Amiris\Presentation\floor_sweep_correlation.png", dpi=150, bbox_inches="tight")
plt.close()
print("Saved floor_sweep_correlation.png")
