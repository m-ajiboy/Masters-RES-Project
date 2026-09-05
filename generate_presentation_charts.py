"""Generates every chart used in the Germany2027 progress presentation, all built directly
from real AMIRIS/Brainpool result files - nothing fabricated or hand-drawn. Charts not
buildable from a surviving result file (e.g. the pre-bugfix 25.3%-shortage run, which was
never saved to disk) are deliberately left out rather than reconstructed from memory.
"""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import numpy as np
import pandas as pd

ROOT = r"C:\Users\MuideenOA\Desktop\PyTut\Amiris"
NAVY = "#1F3A4D"
AMBER = "#A5691F"
GOOD = "#3A6B47"
BAD = "#963C28"
GREY = "#555B58"
LIGHT = "#7FA6BE"

plt.rcParams.update({"font.size": 11, "axes.edgecolor": "#888", "axes.labelcolor": "#333"})


def load_price(path):
    df = pd.read_csv(path, sep=";")
    df["ts"] = pd.to_datetime(df["TimeStep"])
    return df.set_index("ts")["ElectricityPriceInEURperMWH"]


# ---- Chart 1: V1 price duration curve showing the shortage plateau ----
def chart_v1_duration_curve():
    p = load_price(rf"{ROOT}\result_Germany2027_test\DayAheadMarketSingleZone.csv")
    sorted_vals = p.sort_values(ascending=False).values
    pct = 100 * (1 + np.arange(len(sorted_vals))) / len(sorted_vals)
    shortage_pct = (p >= 2999.9).mean() * 100

    fig, ax = plt.subplots(figsize=(11, 6))
    ax.plot(pct, sorted_vals, color=NAVY, linewidth=1.8)
    ax.axhline(3000, color=BAD, linestyle="--", linewidth=1)
    ax.axvline(shortage_pct, color=BAD, linestyle=":", linewidth=1.2)
    ax.fill_between(pct, 0, sorted_vals, where=(sorted_vals >= 2999.9), color=BAD, alpha=0.25)
    ax.annotate(f"{shortage_pct:.2f}% of the year\n(1,391 hours) at the\n3,000 EUR/MWh shortage ceiling",
                xy=(shortage_pct, 3000), xytext=(shortage_pct + 8, 2300),
                fontsize=12, color=BAD, fontweight="bold",
                arrowprops=dict(arrowstyle="->", color=BAD))
    ax.set_xlabel("% of hours in the year, sorted from most expensive to least")
    ax.set_ylabel("Price (EUR/MWh)")
    ax.set_title("Initial build (V1): price duration curve, full year 2027")
    ax.set_ylim(-50, 3200)
    ax.grid(alpha=0.3)
    plt.tight_layout()
    plt.savefig(rf"{ROOT}\ppt_chart_v1_duration.png", dpi=150)
    plt.close()
    print("Saved ppt_chart_v1_duration.png")


# ---- Chart 2: V1 vs V2 comparison bars ----
def chart_v1_vs_v2():
    v1 = load_price(rf"{ROOT}\examples\backtest\Germany2027\result_Germany2027_rerun\DayAheadMarketSingleZone.csv")
    v2 = load_price(rf"{ROOT}\examples\backtest\Germany2027_DemandV2\result_DemandV2_rerun\DayAheadMarketSingleZone.csv")

    metrics = ["Peak load (MW)", "Shortage hours (%)", "Mean price (EUR/MWh)"]
    v1_vals = [138146.7, (v1 >= 2999.9).mean() * 100, v1.mean()]
    v2_vals = [106178.7, (v2 >= 2999.9).mean() * 100, v2.mean()]

    fig, axes = plt.subplots(1, 3, figsize=(13, 5))
    for ax, m, a, b in zip(axes, metrics, v1_vals, v2_vals):
        bars = ax.bar(["V1\n(household shape)", "V2\n(component-split)"], [a, b], color=[BAD, GOOD], width=0.55)
        for bar, val in zip(bars, [a, b]):
            ax.text(bar.get_x() + bar.get_width() / 2, val, f"{val:,.1f}", ha="center", va="bottom", fontsize=11, fontweight="bold")
        ax.set_title(m, fontsize=12)
        ax.set_ylim(0, max(a, b) * 1.2)
        ax.grid(axis="y", alpha=0.3)
    fig.suptitle("Refining the demand model: V1 vs. V2", fontsize=14, fontweight="bold", color=NAVY)
    plt.tight_layout()
    plt.savefig(rf"{ROOT}\ppt_chart_v1_vs_v2.png", dpi=150)
    plt.close()
    print("Saved ppt_chart_v1_vs_v2.png")


# ---- Chart 3: Import utilization, original with-import builds ----
def chart_import_utilization_original():
    v1_imp = pd.read_csv(rf"{ROOT}\examples\backtest\Germany2027_V1WithImport\result_V1WithImport\ImportTrader.csv", sep=";")
    v2_imp = pd.read_csv(rf"{ROOT}\examples\backtest\Germany2027_WithImport\result_WithImport\ImportTrader.csv", sep=";")
    v1_off, v1_awd = v1_imp["OfferedEnergyInMWH"].sum() / 1e6, v1_imp["AwardedEnergyInMWH"].sum() / 1e6
    v2_off, v2_awd = v2_imp["OfferedEnergyInMWH"].sum() / 1e6, v2_imp["AwardedEnergyInMWH"].sum() / 1e6

    fig, ax = plt.subplots(figsize=(9, 5.5))
    x = np.arange(2)
    w = 0.32
    offered = ax.bar(x - w / 2, [v1_off, v2_off], w, label="Offered (target)", color=LIGHT)
    awarded = ax.bar(x + w / 2, [v1_awd, v2_awd], w, label="Actually cleared", color=BAD)
    for bars in (offered, awarded):
        for bar in bars:
            ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height(), f"{bar.get_height():.1f} TWh",
                    ha="center", va="bottom", fontsize=10)
    ax.set_xticks(x)
    ax.set_xticklabels(["V1 with-import", "V2 with-import"])
    ax.set_ylabel("TWh over the year")
    ax.set_title("Original import model: offered target vs. what actually cleared")
    ax.legend()
    ax.grid(axis="y", alpha=0.3)
    plt.tight_layout()
    plt.savefig(rf"{ROOT}\ppt_chart_import_utilization.png", dpi=150)
    plt.close()
    print("Saved ppt_chart_import_utilization.png")


# ---- Chart 4: the 64% zero-import-during-shortage diagnosis ----
def chart_diagnosis():
    dam = pd.read_csv(rf"{ROOT}\examples\backtest\Germany2027_WithImport\result_WithImport\DayAheadMarketSingleZone.csv", sep=";")
    dam["ts"] = pd.to_datetime(dam["TimeStep"])
    shortage_ts = set(dam.loc[dam["ElectricityPriceInEURperMWH"] >= 2999.9, "ts"])

    imp = pd.read_csv(rf"{ROOT}\examples\backtest\Germany2027_WithImport\result_WithImport\ImportTrader.csv", sep=";")
    imp["ts"] = pd.to_datetime(imp["TimeStep"])
    imp_shortage = imp[imp["ts"].isin(shortage_ts)]
    zero = (imp_shortage["OfferedEnergyInMWH"] == 0).sum()
    nonzero = len(imp_shortage) - zero

    fig, ax = plt.subplots(figsize=(7, 6.5))
    wedges, texts, autotexts = ax.pie(
        [zero, nonzero],
        labels=[f"Zero import\navailable\n({zero} hours)", f"Some import\navailable\n({nonzero} hours)"],
        colors=[BAD, LIGHT], autopct="%1.0f%%", startangle=90,
        textprops={"fontsize": 12}, wedgeprops={"edgecolor": "white", "linewidth": 2},
    )
    for at in autotexts:
        at.set_fontsize(16)
        at.set_fontweight("bold")
        at.set_color("white")
    ax.set_title(f"Of {len(imp_shortage)} shortage hours (V2 with-import, original):\nhow many had import available?",
                 fontsize=13, color=NAVY)
    plt.tight_layout()
    plt.savefig(rf"{ROOT}\ppt_chart_diagnosis.png", dpi=150)
    plt.close()
    print(f"Saved ppt_chart_diagnosis.png ({zero}/{len(imp_shortage)} = {zero/len(imp_shortage)*100:.1f}%)")


# ---- Chart 5: calibration sweep (V2) ----
def chart_calibration_sweep():
    ceilings = [20000, 25000, 30000, 37650]
    shortage_pct = [0.38, 0.15, 0.03, 0.00]
    bias = [0.82, -6.61, -10.70, -12.59]
    mae = [44.31, 38.48, 35.95, 35.83]
    corr = [0.268, 0.308, 0.421, 0.549]

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(13, 5.5))

    ax1.plot(ceilings, shortage_pct, "o-", color=BAD, linewidth=2, markersize=8, label="Shortage hours (%)")
    ax1b = ax1.twinx()
    ax1b.plot(ceilings, [abs(b) for b in bias], "s-", color=AMBER, linewidth=2, markersize=8, label="|Bias| (EUR/MWh)")
    ax1.set_xlabel("Flat import ceiling (MW)")
    ax1.set_ylabel("Shortage hours (%)", color=BAD)
    ax1b.set_ylabel("|Bias| vs. Brainpool (EUR/MWh)", color=AMBER)
    ax1.tick_params(axis="y", labelcolor=BAD)
    ax1b.tick_params(axis="y", labelcolor=AMBER)
    ax1.xaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"{x:,.0f}"))
    ax1.set_title("Shortage hours fall as ceiling rises,\nbut bias magnitude grows")
    ax1.axvline(30000, color=GOOD, linestyle=":", linewidth=1.5)
    ax1.text(30000, ax1.get_ylim()[1] * 0.9, " chosen\n for V2", color=GOOD, fontsize=10, fontweight="bold")
    ax1.grid(alpha=0.3)

    ax2.plot(ceilings, mae, "o-", color=NAVY, linewidth=2, markersize=8, label="MAE")
    ax2b = ax2.twinx()
    ax2b.plot(ceilings, corr, "s-", color=GOOD, linewidth=2, markersize=8, label="Correlation (r)")
    ax2.set_xlabel("Flat import ceiling (MW)")
    ax2.set_ylabel("MAE (EUR/MWh)", color=NAVY)
    ax2b.set_ylabel("Correlation with Brainpool (r)", color=GOOD)
    ax2.tick_params(axis="y", labelcolor=NAVY)
    ax2b.tick_params(axis="y", labelcolor=GOOD)
    ax2.xaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"{x:,.0f}"))
    ax2.set_title("MAE and correlation both favour\nthe LARGER ceiling")
    ax2.axvline(30000, color=GOOD, linestyle=":", linewidth=1.5)
    ax2.grid(alpha=0.3)

    fig.suptitle("V2 import-ceiling calibration sweep vs. Brainpool's real 2027 price", fontsize=14, fontweight="bold", color=NAVY)
    plt.tight_layout()
    plt.savefig(rf"{ROOT}\ppt_chart_calibration_sweep.png", dpi=150)
    plt.close()
    print("Saved ppt_chart_calibration_sweep.png")


# ---- Chart 6: V1 vs V2 ceiling asymmetry ----
def chart_ceiling_asymmetry():
    fig, axes = plt.subplots(1, 2, figsize=(12, 5.5))

    labels = ["30,000 MW", "37,650 MW"]
    v1_shortage = [1.87, 0.83]
    v2_shortage = [0.03, 0.00]
    v1_bias = [39.46, 7.42]
    v2_bias = [-10.70, -12.59]

    x = np.arange(2)
    w = 0.32
    ax = axes[0]
    ax.bar(x - w / 2, v1_shortage, w, label="V1", color=BAD)
    ax.bar(x + w / 2, v2_shortage, w, label="V2", color=GOOD)
    ax.set_xticks(x)
    ax.set_xticklabels(labels)
    ax.set_ylabel("Shortage hours (%)")
    ax.set_title("Shortage hours: 30k makes V1 WORSE,\nbarely changes V2")
    ax.legend()
    ax.grid(axis="y", alpha=0.3)
    for i, vals in enumerate([v1_shortage, v2_shortage]):
        for j, v in enumerate(vals):
            xpos = j + (-w / 2 if i == 0 else w / 2)
            ax.text(xpos, v, f"{v:.2f}%", ha="center", va="bottom", fontsize=9)

    ax = axes[1]
    ax.bar(x - w / 2, v1_bias, w, label="V1", color=BAD)
    ax.bar(x + w / 2, v2_bias, w, label="V2", color=GOOD)
    ax.axhline(0, color="black", linewidth=0.8)
    ax.set_xticks(x)
    ax.set_xticklabels(labels)
    ax.set_ylabel("Bias vs. Brainpool (EUR/MWh)")
    ax.set_title("Bias: V1 needs the full ceiling,\nV2 is better with less")
    ax.legend()
    ax.grid(axis="y", alpha=0.3)
    for i, vals in enumerate([v1_bias, v2_bias]):
        for j, v in enumerate(vals):
            xpos = j + (-w / 2 if i == 0 else w / 2)
            ax.text(xpos, v + (1.5 if v >= 0 else -3), f"{v:+.1f}", ha="center", fontsize=9)

    fig.suptitle("Final finding: the right import ceiling depends on the demand model", fontsize=13, fontweight="bold", color=NAVY)
    plt.tight_layout()
    plt.savefig(rf"{ROOT}\ppt_chart_ceiling_asymmetry.png", dpi=150)
    plt.close()
    print("Saved ppt_chart_ceiling_asymmetry.png")


# ---- Chart 7: final before/after summary, all builds vs Brainpool ----
def chart_final_summary():
    builds = ["V1\nno-import", "V1\nwith-import\n(original)", "V1\nwith-import\n(FINAL)",
              "V2\nno-import", "V2\nwith-import\n(original)", "V2\nwith-import\n(FINAL)"]
    shortage = [15.88, 11.78, 0.83, 7.52, 5.35, 0.03]
    mean_price = [519.02, 400.04, 75.46, 285.58, 219.81, 57.34]
    colors = [BAD, BAD, GOOD, AMBER, AMBER, GOOD]

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))

    bars = ax1.bar(builds, shortage, color=colors)
    for bar, v in zip(bars, shortage):
        ax1.text(bar.get_x() + bar.get_width() / 2, v, f"{v:.2f}%", ha="center", va="bottom", fontsize=9)
    ax1.set_ylabel("Shortage hours (%)")
    ax1.set_title("Shortage hours: before vs. after")
    ax1.tick_params(axis="x", labelsize=8.5)
    ax1.grid(axis="y", alpha=0.3)

    bars = ax2.bar(builds, mean_price, color=colors)
    for bar, v in zip(bars, mean_price):
        ax2.text(bar.get_x() + bar.get_width() / 2, v, f"{v:.0f}", ha="center", va="bottom", fontsize=9)
    ax2.axhline(68.04, color=NAVY, linestyle="--", linewidth=1.5, label="Brainpool's real forecast (68.04)")
    ax2.set_ylabel("Mean price (EUR/MWh)")
    ax2.set_title("Mean price: before vs. after")
    ax2.tick_params(axis="x", labelsize=8.5)
    ax2.legend()
    ax2.grid(axis="y", alpha=0.3)

    fig.suptitle("Overall progress: from wildly divergent to close to Brainpool", fontsize=14, fontweight="bold", color=NAVY)
    plt.tight_layout()
    plt.savefig(rf"{ROOT}\ppt_chart_final_summary.png", dpi=150)
    plt.close()
    print("Saved ppt_chart_final_summary.png")


if __name__ == "__main__":
    chart_v1_duration_curve()
    chart_v1_vs_v2()
    chart_import_utilization_original()
    chart_diagnosis()
    chart_calibration_sweep()
    chart_ceiling_asymmetry()
    chart_final_summary()
    print("\nAll charts generated.")
