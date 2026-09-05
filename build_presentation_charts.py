"""Builds three new summary charts for the supervisor progress presentation, using only
already-established, real numbers from this project's own documentation (progress report)."""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

RED = "#B03A2E"
ORANGE = "#D68910"
GREEN = "#1E8449"
BLUE = "#2471A3"
NAVY = "#1F3A4D"

# ---------------------------------------------------------------------------
# Chart 1: overall progress (shortage hours + mean price), updated with final numbers
# ---------------------------------------------------------------------------
fig, axes = plt.subplots(1, 2, figsize=(13, 5.5))

labels = ["V1\nno-import", "V1\nwith-import\n(original)", "V1\nwith-import\n(FINAL)",
          "V2\nno-import", "V2\nwith-import\n(original)", "V2\nfinal\n(all fixes)"]
shortage = [15.88, 11.78, 0.83, 7.52, 5.35, 0.02]
mean_price = [519, 400, 75, 286, 220, 55.5]
colors = [RED, RED, GREEN, ORANGE, ORANGE, GREEN]

axes[0].bar(labels, shortage, color=colors)
for i, v in enumerate(shortage):
    axes[0].text(i, v + 0.3, f"{v:.2f}%", ha="center", fontsize=10)
axes[0].set_ylabel("Shortage hours (%)")
axes[0].set_title("Shortage hours: before vs. after")
axes[0].tick_params(axis="x", labelsize=9)

axes[1].bar(labels, mean_price, color=colors)
for i, v in enumerate(mean_price):
    axes[1].text(i, v + 8, f"{v:.0f}", ha="center", fontsize=10)
axes[1].axhline(68.04, color=NAVY, linestyle="--", label="Brainpool's real forecast (68.04)")
axes[1].set_ylabel("Mean price (EUR/MWh)")
axes[1].set_title("Mean price: before vs. after")
axes[1].legend(fontsize=9)
axes[1].tick_params(axis="x", labelsize=9)

fig.suptitle("Overall progress: from wildly divergent to close to Brainpool", fontsize=15, fontweight="bold", color=NAVY)
plt.tight_layout()
plt.savefig(r"C:\Users\MuideenOA\Desktop\PyTut\Amiris\Presentation\chart_overall_progress.png", dpi=150)
plt.close()

# ---------------------------------------------------------------------------
# Chart 2: correlation progression through the fix history
# ---------------------------------------------------------------------------
fig, ax = plt.subplots(figsize=(11, 5.5))
stages = ["Import ceiling\ncalibrated\n(Phase 8)", "+ Weekday\nalignment fix\n(Phase 11)",
          "+ Smart demand:\nweather-matched year,\nflexible electrolysis\n& EV charging",
          "+ Calendar bug\nfix (FINAL)"]
corr = [0.421, 0.652, 0.647, 0.675]
bar_colors = [RED, ORANGE, ORANGE, GREEN]
bars = ax.bar(stages, corr, color=bar_colors, width=0.55)
for i, v in enumerate(corr):
    ax.text(i, v + 0.015, f"r = {v:.3f}", ha="center", fontsize=12, fontweight="bold")
ax.set_ylim(0, 0.78)
ax.set_ylabel("Correlation with Brainpool's real price (r)")
ax.set_title("How closely AMIRIS now tracks Brainpool's real 2027 price forecast", fontsize=14, fontweight="bold", color=NAVY)
ax.axhline(0, color="black", linewidth=0.8)
plt.tight_layout()
plt.savefig(r"C:\Users\MuideenOA\Desktop\PyTut\Amiris\Presentation\chart_correlation_progression.png", dpi=150)
plt.close()

# ---------------------------------------------------------------------------
# Chart 3: out-of-sample validation, before/after the calendar bug fix
# ---------------------------------------------------------------------------
fig, ax = plt.subplots(figsize=(11, 5.5))
years = ["2027\n(tuned for)", "2028\n(never tuned for)", "2029\n(never tuned for)"]
before = [0.647, 0.446, 0.349]
after = [0.675, 0.446, 0.446]  # 2028 unaffected by the bug (used a different, already-correct method)
x = np.arange(len(years))
width = 0.32
ax.bar(x - width/2, before, width, label="Before calendar bug fix", color="#AAB7B8")
ax.bar(x + width/2, after, width, label="After calendar bug fix", color=GREEN)
for i in range(len(years)):
    ax.text(x[i] - width/2, before[i] + 0.015, f"{before[i]:.3f}", ha="center", fontsize=10)
    ax.text(x[i] + width/2, after[i] + 0.015, f"{after[i]:.3f}", ha="center", fontsize=10)
ax.set_xticks(x)
ax.set_xticklabels(years)
ax.set_ylabel("Correlation with Brainpool's real price (r)")
ax.set_title("Testing on years the model was never tuned for (2028 & 2029)", fontsize=14, fontweight="bold", color=NAVY)
ax.legend(fontsize=10)
ax.set_ylim(0, 0.78)
plt.tight_layout()
plt.savefig(r"C:\Users\MuideenOA\Desktop\PyTut\Amiris\Presentation\chart_outofsample_validation.png", dpi=150)
plt.close()

print("Saved 3 charts to Presentation/")
