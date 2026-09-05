"""Builds the import-ceiling trade-off chart for the comprehensive walkthrough presentation,
using the real, already-verified sweep numbers from Phase 25/27 (2028 and 2029, at 15,000 /
20,000 / 30,000 MW)."""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

NAVY = "#1F3A4D"
RED = "#B03A2E"
GREEN = "#1E8449"

ceilings = ["15,000 MW", "20,000 MW", "30,000 MW\n(kept as default)"]
excl_r_2028 = [0.709, 0.705, 0.446]
excl_r_2029 = [0.704, 0.698, 0.349]
shortage_2028 = [49, 22, 1]
shortage_2029 = [116, 63, 8]

fig, axes = plt.subplots(1, 2, figsize=(13, 5.8))

x = np.arange(3)
width = 0.35
axes[0].bar(x - width/2, excl_r_2028, width, label="2028", color=NAVY)
axes[0].bar(x + width/2, excl_r_2029, width, label="2029", color="#5B8FA8")
for i in range(3):
    axes[0].text(x[i]-width/2, excl_r_2028[i]+0.015, f"{excl_r_2028[i]:.3f}", ha="center", fontsize=9)
    axes[0].text(x[i]+width/2, excl_r_2029[i]+0.015, f"{excl_r_2029[i]:.3f}", ha="center", fontsize=9)
axes[0].set_xticks(x)
axes[0].set_xticklabels(ceilings, fontsize=10)
axes[0].set_ylabel("Correlation (ordinary hours only)")
axes[0].set_title("Smaller ceiling = better matching quality")
axes[0].legend()
axes[0].set_ylim(0, 0.82)

axes[1].bar(x - width/2, shortage_2028, width, label="2028", color=RED)
axes[1].bar(x + width/2, shortage_2029, width, label="2029", color="#D68910")
for i in range(3):
    axes[1].text(x[i]-width/2, shortage_2028[i]+2, f"{shortage_2028[i]}", ha="center", fontsize=9)
    axes[1].text(x[i]+width/2, shortage_2029[i]+2, f"{shortage_2029[i]}", ha="center", fontsize=9)
axes[1].set_xticks(x)
axes[1].set_xticklabels(ceilings, fontsize=10)
axes[1].set_ylabel("Hours the model ran out of power")
axes[1].set_title("...but at the cost of far more shortage hours")
axes[1].legend()

fig.suptitle("The Import-Ceiling Trade-Off (why 30,000 MW was kept as the default)", fontsize=15, fontweight="bold", color=NAVY)
plt.tight_layout()
plt.savefig(r"C:\Users\MuideenOA\Desktop\PyTut\Amiris\Presentation\chart_ceiling_tradeoff.png", dpi=150)
plt.close()
print("Saved chart_ceiling_tradeoff.png")
