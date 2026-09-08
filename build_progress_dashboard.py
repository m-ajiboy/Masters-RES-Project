"""Builds the overall 'progress dashboard' - correlation, bias, MAE, and mean price tracked
across the full chronological sequence of real milestones, from the very first V1 no-import
build through Phase 43. Reads all_milestones_statistics.csv (built by
build_all_phase_charts.py) rather than re-computing anything, so the numbers are guaranteed
consistent with the individual per-milestone charts."""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import pandas as pd

OUT_ROOT = r"C:\Users\MuideenOA\Desktop\PyTut\Amiris\AMIRIS_Project_Charts_AllPhases"
df = pd.read_csv(rf"{OUT_ROOT}\all_milestones_statistics.csv")

NAVY = "#1f3a4d"
RED = "#96453c"
GOOD = "#3a6b47"
AMBER = "#a5691f"
GREY = "#6b6b6b"

# Split into the main 2027 chronological line vs the 2028/2029 out-of-sample lines
main_2027 = df[df["year"] == 2027].reset_index(drop=True)
oos_2028 = df[df["year"] == 2028].reset_index(drop=True)
oos_2029 = df[df["year"] == 2029].reset_index(drop=True)

def short_label(id_str, name_str):
    """Builds a unique x-axis label from the milestone id ('21_MarketCoupling_AllZones' ->
    '21') plus its real phase number - using the id's own numeric prefix instead of just the
    phase number avoids collisions where two different milestones share one phase number
    (e.g. Phase 5 covers both the V1 and V2 import builds; Phase 24 covers both 2028 and
    2029's initial out-of-sample runs) - confirmed as a real mislabeling bug found by
    inspecting the first rendered chart directly, where two same-labelled points were
    actually two different real builds."""
    num = id_str.split("_")[0]
    phase = name_str.split(":")[0].replace("Phase ", "P")
    return f"{num} ({phase})"


# Short, GUARANTEED-unique x-axis labels: milestone id number + real phase number together.
main_2027["short_label"] = [short_label(i, n) for i, n in zip(main_2027["id"], main_2027["name"])]

fig, axes = plt.subplots(2, 2, figsize=(16, 11))
x = range(len(main_2027))

panels = [
    (axes[0, 0], "corr_excl", "Correlation to Brainpool (excl-shortage hours)", GOOD, None),
    (axes[0, 1], "bias_excl", "Bias vs. Brainpool, EUR/MWh (excl-shortage hours)", RED, 0),
    (axes[1, 0], "mae_excl", "MAE vs. Brainpool, EUR/MWh (excl-shortage hours)", AMBER, None),
    (axes[1, 1], "mean_price", "Mean Price, EUR/MWh (AMIRIS vs. real Brainpool)", NAVY, None),
]

for ax, col, title, color, hline in panels:
    ax.plot(x, main_2027[col], marker="o", markersize=4, color=color, lw=1.8)
    if hline is not None:
        ax.axhline(hline, color="#999999", lw=1, ls=":")
    if col == "mean_price":
        ax.plot(x, main_2027["brainpool_mean"], color=GREY, lw=1.5, ls="--", label="Brainpool real mean (68.04)")
        ax.legend(fontsize=9)
    ax.set_title(title, fontsize=12, weight="bold")
    ax.set_xticks(list(x))
    ax.set_xticklabels(main_2027["short_label"], rotation=90, fontsize=7.5)
    ax.grid(alpha=0.3)
    ax.set_xlim(-0.5, len(main_2027) - 0.5)

fig.suptitle("Project Progress, 2027: Every Real Milestone From Inception to Phase 43",
             fontsize=16, weight="bold", y=0.995)
plt.tight_layout(rect=[0, 0, 1, 0.97])
plt.savefig(rf"{OUT_ROOT}\progress_dashboard_2027.png", dpi=170, facecolor="white")
plt.close(fig)
print(f"Saved progress_dashboard_2027.png ({len(main_2027)} milestones)")

# Shortage-hours panel on its own (log-scale friendly, very different range than the others)
fig, ax = plt.subplots(figsize=(14, 5.5))
ax.plot(x, main_2027["shortage_hours"], marker="o", markersize=4, color=RED, lw=1.8)
ax.set_title("Shortage Hours (Price at the 3,000 EUR/MWh Ceiling), 2027", fontsize=13, weight="bold")
ax.set_xticks(list(x))
ax.set_xticklabels(main_2027["short_label"], rotation=90, fontsize=8)
ax.grid(alpha=0.3)
ax.set_ylabel("Shortage hours (count, out of 8,760)")
ax.set_xlim(-0.5, len(main_2027) - 0.5)
plt.tight_layout()
plt.savefig(rf"{OUT_ROOT}\progress_dashboard_2027_shortage_hours.png", dpi=170, facecolor="white")
plt.close(fig)
print("Saved progress_dashboard_2027_shortage_hours.png")

# --- Out-of-sample (2028/2029) progress: fewer milestones, side by side ---
# IMPORTANT: 2028 skipped a milestone 2029 has (no separate Feb-29-drop-fix build was needed
# for 2028 - Phase 28's write-up notes 2028 already used the Dec-31-drop approach from the
# start, for an unrelated reason). Plotting both series against a shared RAW INDEX (0,1,2...)
# silently misaligned 2028's 2nd point under 2029's "Phase 28" label when it was actually
# 2028's Phase 38 result - a real mislabelling bug, confirmed by inspecting the first
# rendered chart directly. Fixed by plotting against each point's REAL phase number instead
# of its position, so a genuinely skipped milestone leaves a real gap rather than a
# mislabelled point.
def extract_phase_num(name_str):
    return int(name_str.split(":")[0].replace("Phase ", ""))


oos_2028["phase_num"] = oos_2028["name"].apply(extract_phase_num)
oos_2029["phase_num"] = oos_2029["name"].apply(extract_phase_num)
all_phase_nums = sorted(set(oos_2028["phase_num"]) | set(oos_2029["phase_num"]))

fig, axes = plt.subplots(1, 3, figsize=(17, 5.5))
metrics = [("corr_excl", "Correlation (excl-shortage)", GOOD),
           ("bias_excl", "Bias, EUR/MWh (excl-shortage)", RED),
           ("mae_excl", "MAE, EUR/MWh (excl-shortage)", AMBER)]
for ax, (col, title, color) in zip(axes, metrics):
    ax.plot(oos_2028["phase_num"], oos_2028[col], marker="o", color=NAVY, lw=2, label="2028")
    ax.plot(oos_2029["phase_num"], oos_2029[col], marker="s", color=AMBER, lw=2, label="2029")
    if col == "bias_excl":
        ax.axhline(0, color="#999999", lw=1, ls=":")
    ax.set_title(title, fontsize=11.5, weight="bold")
    ax.set_xticks(all_phase_nums)
    ax.set_xticklabels([f"Phase {p}" for p in all_phase_nums], rotation=25, fontsize=8, ha="right")
    ax.grid(alpha=0.3)
    ax.legend(fontsize=9)

fig.suptitle("Out-of-Sample Progress: 2028 and 2029 (Never Re-Tuned, Same Fixes as 2027)",
             fontsize=15, weight="bold")
plt.tight_layout(rect=[0, 0, 1, 0.94])
plt.savefig(rf"{OUT_ROOT}\progress_dashboard_2028_2029.png", dpi=170, facecolor="white")
plt.close(fig)
print("Saved progress_dashboard_2028_2029.png")

print("\nDone.")
