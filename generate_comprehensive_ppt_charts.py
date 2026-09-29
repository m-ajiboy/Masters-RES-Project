"""Generates the handful of NEW charts needed for the comprehensive all-phases
presentation that are not already covered by generate_presentation_charts.py or
AMIRIS_Project_Charts_AllPhases\\ - specifically Phase 49-51 (weather/demand-year
robustness) and Phase 52 (investigative Java patch). All numbers are copied
directly from AMIRIS_Germany2027_Progress_Report.pdf's own tables (real,
already-computed comparison results) - nothing is recomputed or invented here.
"""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

ROOT = r"C:\Users\MuideenOA\Desktop\PyTut\Amiris"
NAVY = "#1F3A4D"
AMBER = "#A5691F"
GOOD = "#3A6B47"
BAD = "#963C28"
GREY = "#555B58"

plt.rcParams.update({"font.size": 11, "axes.edgecolor": "#888", "axes.labelcolor": "#333"})


# ---- Chart: Phase 49-51 weather/demand-year robustness sweep ----
def chart_weather_year_sweep():
    labels = ["Headline\n(Phase 37)", "Demand-shape\nyear (P49)", "Wind-offshore\nyear (P50)", "Run-of-river\nyear (P51)"]
    shortage = [7, 26, 12, 8]
    bias = [-2.90, -3.53, -4.25, -3.02]
    corr = [0.7168, 0.7104, 0.7124, 0.7149]
    colors = [GOOD, BAD, BAD, AMBER]

    fig, axes = plt.subplots(1, 3, figsize=(14, 5.5))

    ax = axes[0]
    bars = ax.bar(labels, shortage, color=colors)
    for b, v in zip(bars, shortage):
        ax.text(b.get_x() + b.get_width() / 2, v, str(v), ha="center", va="bottom", fontsize=11, fontweight="bold")
    ax.set_title("Shortage hours\n(lower is better)")
    ax.tick_params(axis="x", labelsize=9)
    ax.grid(axis="y", alpha=0.3)

    ax = axes[1]
    bars = ax.bar(labels, [abs(b) for b in bias], color=colors)
    for b, v in zip(bars, bias):
        ax.text(b.get_x() + b.get_width() / 2, abs(v), f"{v:+.2f}", ha="center", va="bottom", fontsize=10)
    ax.set_title("|Bias| vs. Brainpool\n(lower is better)")
    ax.tick_params(axis="x", labelsize=9)
    ax.grid(axis="y", alpha=0.3)

    ax = axes[2]
    bars = ax.bar(labels, corr, color=colors)
    ax.set_ylim(0.65, 0.73)
    for b, v in zip(bars, corr):
        ax.text(b.get_x() + b.get_width() / 2, v, f"{v:.4f}", ha="center", va="bottom", fontsize=10)
    ax.set_title("Excl-shortage correlation\n(higher is better)")
    ax.tick_params(axis="x", labelsize=9)
    ax.grid(axis="y", alpha=0.3)

    fig.suptitle("Phases 49-51: real alternative weather/demand years tested - none beat the headline build",
                 fontsize=13.5, fontweight="bold", color=NAVY)
    plt.tight_layout()
    plt.savefig(rf"{ROOT}\ppt_chart_weatheryear_sweep.png", dpi=150)
    plt.close()
    print("Saved ppt_chart_weatheryear_sweep.png")


# ---- Chart: Phase 52 investigative patch variants ----
def chart_phase52_variants():
    labels = ["Headline\n(Phase 37)", "Both storages,\nalways-on", "+330 EUR/MWh\nthreshold", "+100 EUR/MWh\nthreshold",
              "Reservoir Hydro\nonly (FINAL)", "Res. Hydro only\n+100 threshold"]
    shortage = [7, 8, 10, 10, 6, 10]
    bias = [-2.90, -0.42, -2.88, -1.83, -0.95, -2.13]
    corr = [0.7168, 0.6828, 0.7173, 0.6988, 0.6852, 0.6974]
    colors = [NAVY, BAD, AMBER, AMBER, GOOD, BAD]

    fig, axes = plt.subplots(1, 3, figsize=(15, 5.8))

    ax = axes[0]
    bars = ax.bar(labels, shortage, color=colors)
    for b, v in zip(bars, shortage):
        ax.text(b.get_x() + b.get_width() / 2, v, str(v), ha="center", va="bottom", fontsize=11, fontweight="bold")
    ax.set_title("Shortage hours\n(lower is better)")
    ax.tick_params(axis="x", labelsize=8)
    ax.grid(axis="y", alpha=0.3)

    ax = axes[1]
    bars = ax.bar(labels, [abs(b) for b in bias], color=colors)
    for b, v in zip(bars, bias):
        ax.text(b.get_x() + b.get_width() / 2, abs(v), f"{v:+.2f}", ha="center", va="bottom", fontsize=9.5)
    ax.set_title("|Bias| vs. Brainpool\n(lower is better)")
    ax.tick_params(axis="x", labelsize=8)
    ax.grid(axis="y", alpha=0.3)

    ax = axes[2]
    bars = ax.bar(labels, corr, color=colors)
    ax.set_ylim(0.65, 0.73)
    ax.axhline(0.7168, color=NAVY, linestyle="--", linewidth=1, alpha=0.6)
    for b, v in zip(bars, corr):
        ax.text(b.get_x() + b.get_width() / 2, v, f"{v:.4f}", ha="center", va="bottom", fontsize=9)
    ax.set_title("Excl-shortage correlation\n(higher is better)")
    ax.tick_params(axis="x", labelsize=8)
    ax.grid(axis="y", alpha=0.3)

    fig.suptitle("Phase 52 (investigative only): every patch variant trades one metric for another",
                 fontsize=13.5, fontweight="bold", color=NAVY)
    plt.tight_layout()
    plt.savefig(rf"{ROOT}\ppt_chart_phase52_variants.png", dpi=150)
    plt.close()
    print("Saved ppt_chart_phase52_variants.png")


# ---- Chart: the big-picture journey, mean price toward Brainpool's real value ----
def chart_journey_to_brainpool():
    stages = ["V1\nno-import", "V1 fixed\nimport", "V2\nfixed import", "+ smart\nflexibility",
              "+ market\ncoupling\n(Phase 37)"]
    mean_price = [519.02, 75.46, 57.34, 55.62, 67.45]
    colors = [BAD, AMBER, AMBER, GOOD, GOOD]

    fig, ax = plt.subplots(figsize=(11, 5.8))
    bars = ax.bar(stages, mean_price, color=colors, width=0.55)
    for b, v in zip(bars, mean_price):
        ax.text(b.get_x() + b.get_width() / 2, v, f"{v:.1f}", ha="center", va="bottom", fontsize=12, fontweight="bold")
    ax.axhline(68.04, color=NAVY, linestyle="--", linewidth=2, label="Brainpool's real 2027 forecast (68.04 EUR/MWh)")
    ax.set_ylabel("Mean price across the whole year (EUR/MWh)")
    ax.set_title("The whole journey in one number: mean price converging on Brainpool's real forecast", fontsize=14, color=NAVY, fontweight="bold")
    ax.legend(fontsize=11)
    ax.grid(axis="y", alpha=0.3)
    plt.tight_layout()
    plt.savefig(rf"{ROOT}\ppt_chart_journey_to_brainpool.png", dpi=150)
    plt.close()
    print("Saved ppt_chart_journey_to_brainpool.png")


if __name__ == "__main__":
    chart_weather_year_sweep()
    chart_phase52_variants()
    chart_journey_to_brainpool()
    print("\nAll new comprehensive-deck charts generated.")
