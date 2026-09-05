"""Builds the 'smoking gun' chart for the presentation: real 2029 demand by day of week,
before vs after the Feb-29-drop calendar bug fix. Numbers are the actual verified values
computed earlier this project."""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

NAVY = "#1F3A4D"
RED = "#96603C"
GREEN = "#1E8449"

days = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
before = [78257.0, 79349.7, 78742.6, 77518.7, 69286.3, 64237.8, 74122.7]
after = [76261.5, 78714.6, 79398.9, 78614.1, 77315.5, 67584.4, 63664.0]

x = np.arange(len(days))
width = 0.35
fig, ax = plt.subplots(figsize=(11, 6.2))
ax.bar(x - width/2, before, width, label="Before fix (bug present)", color=RED)
ax.bar(x + width/2, after, width, label="After fix", color=GREEN)
ax.set_xticks(x)
ax.set_xticklabels(days, fontsize=13)
ax.set_ylabel("Average demand (MW)")
ax.set_title("The Smoking Gun: 2029 Demand by Day of Week", fontsize=16, fontweight="bold", color=NAVY, pad=55)
ax.set_ylim(0, 95000)
ax.legend(fontsize=11, loc="upper center", bbox_to_anchor=(0.5, 1.14), ncol=2, frameon=False)
ax.annotate("Friday too low,\nSunday too high (the bug)", xy=(4.2, 69700), xytext=(1.4, 87000),
            fontsize=10.5, ha="center", color=RED, fontweight="bold",
            arrowprops=dict(arrowstyle="->", color=RED, lw=1.5))
ax.annotate("Fixed: clean weekday-high,\nweekend-low pattern restored", xy=(5.35, 68000), xytext=(5.3, 87000),
            fontsize=10.5, ha="center", color=GREEN, fontweight="bold",
            arrowprops=dict(arrowstyle="->", color=GREEN, lw=1.5))
plt.tight_layout()
plt.savefig(r"C:\Users\MuideenOA\Desktop\PyTut\Amiris\Presentation\chart_weekday_bug.png", dpi=150)
plt.close()
print("Saved chart_weekday_bug.png")
