"""Generates a complete visual record of the project's evolution: for every real milestone
build from inception to Phase 43, a price duration curve and a correlation scatter chart
against Brainpool's real forecast, saved into its own numbered subfolder under
AMIRIS_Project_Charts_AllPhases/ - plus one overall progress dashboard tracking correlation,
bias, MAE, and mean price across the whole chronological sequence.

Scope decision: over 50 real result files exist across this project (many are near-duplicate
sensitivity-sweep values, e.g. the import-ceiling sweep at 15k/20k/25k/30k/37650 MW, or the
lignite-markup sweep at -60/-40/-20/-10). Rather than one subfolder per sweep VALUE (which
would bury the real narrative in near-identical repeats), each sweep is treated as ONE
milestone stage with its own multi-value comparison chart, matching how Phase 29/31 already
documented them. The chronological list below matches the Progress Report's own phase
structure - every real, distinct build that represents a genuine step in the project, not
every file on disk."""
import os
import json
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import numpy as np
import pandas as pd
from brainpool_multiyear_data import load_brainpool_price

ROOT = r"C:\Users\MuideenOA\Desktop\PyTut\Amiris\examples\backtest"
OUT_ROOT = r"C:\Users\MuideenOA\Desktop\PyTut\Amiris\AMIRIS_Project_Charts_AllPhases"

NAVY = "#1f3a4d"
RED = "#96453c"
GREY = "#6b6b6b"
GOOD = "#3a6b47"


def load_price(path, fmt, agent_id=1):
    df = pd.read_csv(path, sep=";")
    df["ts"] = pd.to_datetime(df["TimeStep"])
    if fmt == "multi":
        df = df[df["AgentId"] == agent_id]
    return df.set_index("ts")["ElectricityPriceInEURperMWH"]


# ---------------------------------------------------------------------------
# Milestone list: (folder_id, display_name, year, csv_path, format)
# Chronological, matching the Progress Report's own phase numbering.
# ---------------------------------------------------------------------------
MILESTONES = [
    ("01_V1_NoImport", "Phase 2: V1 - No Import", 2027,
     rf"{ROOT}\Germany2027\result_Germany2027_rerun\DayAheadMarketSingleZone.csv", "single"),
    ("02_V1_WithImport_Original", "Phase 5: V1 - Original (Flawed) Import", 2027,
     rf"{ROOT}\Germany2027_V1WithImport\result_V1WithImport\DayAheadMarketSingleZone.csv", "single"),
    ("03_V1_WithImport_Fixed", "Phase 8: V1 - Fixed/Calibrated Import (Final V1)", 2027,
     rf"{ROOT}\Germany2027_V1WithImport_Fix\result_V1WithImport_Fix30k\DayAheadMarketSingleZone.csv", "single"),
    ("04_V2_NoImport", "Phase 4: V2 - Component-Split Demand, No Import", 2027,
     rf"{ROOT}\Germany2027_DemandV2\result_DemandV2_rerun\DayAheadMarketSingleZone.csv", "single"),
    ("05_V2_WithImport_Original", "Phase 5: V2 - Original (Flawed) Import", 2027,
     rf"{ROOT}\Germany2027_WithImport\result_WithImport\DayAheadMarketSingleZone.csv", "single"),
    ("06_V2_WithImport_Fixed", "Phase 8: V2 - Fixed/Calibrated Import (30,000 MW)", 2027,
     rf"{ROOT}\Germany2027_WithImport_Fix\result_WithImport_Fix30k\DayAheadMarketSingleZone.csv", "single"),
    ("07_Weather2009_WithImport", "Phase 9: Real 2009 Weather Year + Import", 2027,
     rf"{ROOT}\Germany2027_Weather2009_WithImport\result_Weather2009_WithImport\DayAheadMarketSingleZone.csv", "single"),
    ("08_Weekday_Fix", "Phase 11: Weekday/Weekend Calendar Fix", 2027,
     rf"{ROOT}\Germany2027_DemandV2Weekday_WithImport\result_DemandV2Weekday_WithImport\DayAheadMarketSingleZone.csv", "single"),
    ("09_HeatPump2009", "Phase 12: Real 2009 Heat-Pump Temperature (Null Result)", 2027,
     rf"{ROOT}\Germany2027_HeatPump2009_WithImport\result_HeatPump2009_WithImport\DayAheadMarketSingleZone.csv", "single"),
    ("10_ImportBlended", "Phase 15: 11-Country Blended Import Price", 2027,
     rf"{ROOT}\Germany2027_ImportBlended\result_ImportBlended\DayAheadMarketSingleZone.csv", "single"),
    ("11_Demand2016Base", "Phase 17: Demand Rebuilt on Real 2016 Weather-Matched Year", 2027,
     rf"{ROOT}\Germany2027_Demand2016Base\result_Demand2016Base\DayAheadMarketSingleZone.csv", "single"),
    ("12_FlexElectrolysis", "Phase 20: Price-Responsive Electrolysis", 2027,
     rf"{ROOT}\Germany2027_FlexElectrolysis\result_FlexElectrolysis\DayAheadMarketSingleZone.csv", "single"),
    ("13_FlexEMobility", "Phase 21: + Price-Responsive E-Mobility", 2027,
     rf"{ROOT}\Germany2027_FlexEMobility\result_FlexEMobility\DayAheadMarketSingleZone.csv", "single"),
    ("14_Feb29DropFix", "Phase 28: Feb-29-Drop Weekday Bug Fixed (Best Pre-Coupling Result)", 2027,
     rf"{ROOT}\Germany2027_Feb29DropFix\result_Germany2027_Feb29DropFix\DayAheadMarketSingleZone.csv", "single"),
    ("15_CyclingCostTest", "Phase 30: Real Start-Up/Cycling Cost (Confirmed No Effect)", 2027,
     rf"{ROOT}\Germany2027_CyclingCostTest\result_Germany2027_CyclingCostTest\DayAheadMarketSingleZone.csv", "single"),
    ("16_LigniteMarkup_m60_baseline", "Phase 31: Lignite Markup -60 (Baseline)", 2027,
     rf"{ROOT}\Germany2027_LigniteMarkupTest\result_Germany2027_LigniteMarkupTest\DayAheadMarketSingleZone.csv", "single"),
    ("17_MarketCoupling_Placeholder", "Phase 34: First Market Coupling (Placeholder Transmission)", 2027,
     rf"{ROOT}\Germany2027_MarketCoupling\result_Germany2027_MarketCoupling\DayAheadMarketMultiZone.csv", "multi"),
    ("18_MarketCoupling_RealFlow", "Phase 36: Market Coupling, Real-Flow Transmission", 2027,
     rf"{ROOT}\Germany2027_MarketCoupling_RealFlow\result_Germany2027_MarketCoupling_RealFlow\DayAheadMarketMultiZone.csv", "multi"),
    ("19_MarketCoupling_ROEFlex", "Phase 37: + Real ROE Storage/Subsidy (BEST RESULT OVERALL)", 2027,
     rf"{ROOT}\Germany2027_MarketCoupling_ROEFlex\result_Germany2027_MarketCoupling_ROEFlex\DayAheadMarketMultiZone.csv", "multi"),
    ("20_MarketCoupling_FranceZone", "Phase 42: France Disaggregated Alone (Real Step Backward)", 2027,
     rf"{ROOT}\Germany2027_MarketCoupling_FranceZone\result_Germany2027_MarketCoupling_FranceZone\DayAheadMarketMultiZone.csv", "multi"),
    ("21_MarketCoupling_AllZones", "Phase 43: All 10 Real Countries Disaggregated", 2027,
     rf"{ROOT}\Germany2027_MarketCoupling_AllZones\result_Germany2027_MarketCoupling_AllZones\DayAheadMarketMultiZone.csv", "multi"),
]

# 2028/2029 out-of-sample milestones (own chronological sub-sequence)
MILESTONES_2028 = [
    ("22_2028_Initial_OOS", "Phase 24: 2028 Out-of-Sample (Initial, No Re-Tuning)", 2028,
     rf"{ROOT}\Germany2028\result_Germany2028\DayAheadMarketSingleZone.csv", "single"),
    ("23_2028_MarketCoupling_ROEFlex", "Phase 38: 2028 Market Coupling (ROEFlex)", 2028,
     rf"{ROOT}\Germany2028_MarketCoupling_ROEFlex\result_Germany2028_MarketCoupling_ROEFlex\DayAheadMarketMultiZone.csv", "multi"),
]
MILESTONES_2029 = [
    ("24_2029_Initial_OOS", "Phase 24: 2029 Out-of-Sample (Initial, No Re-Tuning)", 2029,
     rf"{ROOT}\Germany2029\result_Germany2029\DayAheadMarketSingleZone.csv", "single"),
    ("25_2029_Feb29DropFix", "Phase 28: 2029 Feb-29-Drop Bug Fixed", 2029,
     rf"{ROOT}\Germany2029_Feb29DropFix\result_Germany2029_Feb29DropFix\DayAheadMarketSingleZone.csv", "single"),
    ("26_2029_MarketCoupling_ROEFlex", "Phase 38: 2029 Market Coupling (ROEFlex)", 2029,
     rf"{ROOT}\Germany2029_MarketCoupling_ROEFlex\result_Germany2029_MarketCoupling_ROEFlex\DayAheadMarketMultiZone.csv", "multi"),
]

ALL_MILESTONES = MILESTONES + MILESTONES_2028 + MILESTONES_2029

print(f"Total milestones: {len(ALL_MILESTONES)}")

# ---------------------------------------------------------------------------
# Per-milestone: compute stats, save price-duration curve + scatter chart.
# ---------------------------------------------------------------------------
rows = []
bp_cache = {}

for folder_id, name, year, path, fmt in ALL_MILESTONES:
    if not os.path.exists(path):
        print(f"SKIP (file not found): {name} -> {path}")
        continue
    if year not in bp_cache:
        bp_cache[year] = load_brainpool_price(year)
    bp = bp_cache[year]

    amiris = load_price(path, fmt)
    joined = pd.DataFrame({"AMIRIS": amiris, "Brainpool": bp}).dropna()
    if len(joined) == 0:
        print(f"SKIP (no overlapping hours): {name}")
        continue

    s, b = joined["AMIRIS"], joined["Brainpool"]
    shortage = s >= 2999.9
    stats = {
        "id": folder_id, "name": name, "year": year, "n_hours": len(joined),
        "mean_price": s.mean(), "brainpool_mean": b.mean(),
        "bias_all": (s - b).mean(), "mae_all": (s - b).abs().mean(),
        "rmse_all": np.sqrt(((s - b) ** 2).mean()),
        "corr_all": s.corr(b),
        "shortage_hours": int(shortage.sum()),
        "shortage_pct": 100 * shortage.mean(),
        "negative_pct": 100 * (s < 0).mean(),
    }
    if (~shortage).sum() > 1:
        stats["bias_excl"] = (s[~shortage] - b[~shortage]).mean()
        stats["mae_excl"] = (s[~shortage] - b[~shortage]).abs().mean()
        stats["corr_excl"] = s[~shortage].corr(b[~shortage])
    else:
        stats["bias_excl"] = stats["bias_all"]
        stats["mae_excl"] = stats["mae_all"]
        stats["corr_excl"] = stats["corr_all"]
    rows.append(stats)

    out_dir = os.path.join(OUT_ROOT, folder_id)
    os.makedirs(out_dir, exist_ok=True)

    # --- Price duration curve ---
    fig, ax = plt.subplots(figsize=(9, 5.5))
    n = len(joined)
    ax.plot(range(1, n + 1), s.sort_values(ascending=False).values, color=NAVY, lw=1.8, label="AMIRIS")
    ax.plot(range(1, n + 1), b.sort_values(ascending=False).values, color=GREY, lw=1.6, ls="--", label="Brainpool (real)")
    ax.set_xlabel("Hour rank (all hours sorted highest price -> lowest)", fontsize=10)
    ax.set_ylabel("Price (EUR/MWh)", fontsize=10)
    ax.set_title(f"{name}\nPrice Duration Curve ({year})", fontsize=12, weight="bold")
    ax.legend(fontsize=10)
    ax.grid(alpha=0.3)
    ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"{x:,.0f}"))
    fig.text(0.5, 0.01,
              f"Mean: {stats['mean_price']:.1f} (Brainpool: {stats['brainpool_mean']:.1f}) | "
              f"Excl-shortage bias: {stats['bias_excl']:+.2f} | Excl-shortage MAE: {stats['mae_excl']:.2f} | "
              f"Excl-shortage r: {stats['corr_excl']:.3f} | Shortage hours: {stats['shortage_hours']}",
              ha="center", fontsize=8.5, style="italic", color="#3a3a3a")
    plt.tight_layout(rect=[0, 0.04, 1, 1])
    plt.savefig(os.path.join(out_dir, "price_duration_curve.png"), dpi=150, facecolor="white")
    plt.close(fig)

    # --- Scatter correlation chart ---
    fig, ax = plt.subplots(figsize=(6.5, 6.5))
    shortage_mask = s >= 2999.9
    ax.scatter(b[~shortage_mask], s[~shortage_mask], s=6, alpha=0.35, color=NAVY, label="Ordinary hours")
    if shortage_mask.any():
        ax.scatter(b[shortage_mask], s[shortage_mask], s=14, alpha=0.7, color=RED, label="Shortage hours (3,000 EUR/MWh)")
    lims = [min(b.min(), s.min()) - 20, max(b.max(), s.max()) + 20]
    ax.plot(lims, lims, color="#999999", lw=1, ls=":", label="Perfect match (y=x)")
    ax.set_xlim(lims)
    ax.set_ylim(lims)
    ax.set_xlabel("Brainpool real price (EUR/MWh)", fontsize=10)
    ax.set_ylabel("AMIRIS price (EUR/MWh)", fontsize=10)
    ax.set_title(f"{name}\nAMIRIS vs. Brainpool ({year})", fontsize=12, weight="bold")
    ax.legend(fontsize=8.5, loc="upper left")
    ax.grid(alpha=0.3)
    ax.set_aspect("equal")
    plt.tight_layout()
    plt.savefig(os.path.join(out_dir, "correlation_scatter.png"), dpi=150, facecolor="white")
    plt.close(fig)

    print(f"OK: {name} -> r_excl={stats['corr_excl']:.3f}, bias_excl={stats['bias_excl']:+.2f}, "
          f"mae_excl={stats['mae_excl']:.2f}, shortage={stats['shortage_hours']}")

stats_df = pd.DataFrame(rows)
stats_df.to_csv(os.path.join(OUT_ROOT, "all_milestones_statistics.csv"), index=False)
print(f"\nSaved statistics table: {os.path.join(OUT_ROOT, 'all_milestones_statistics.csv')}")
print(f"Milestones charted: {len(stats_df)}")
