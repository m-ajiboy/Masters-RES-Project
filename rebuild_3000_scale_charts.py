"""Rebuilds every price chart in this project whose y-axis has to span up to the 3,000
EUR/MWh shortage ceiling, using a broken y-axis instead of a single 0-3000+ linear scale:
a tall bottom panel covering -50 to 400 EUR/MWh with gridlines every 50 EUR/MWh (where
almost every real hour actually sits), and a thin top panel showing only the 3,000 ceiling
itself. This makes the fine detail in ordinary-hour price movements visible, which a plain
500-point-interval linear axis was compressing into a few pixels. All outputs are saved
into Charts_50pt_BrokenAxis/ (new, separate from every original chart folder - nothing
original is overwritten).

Covers: the two price charts embedded in Chapter 5 of the thesis (full-year headline
overlay, the 17 Dec 2027 shortage-day spike), every one of the 26 real milestone builds'
price-duration curves (AMIRIS_Project_Charts_AllPhases/), and the two standalone
duration-curve charts (ppt_chart_v1_duration.png, chart_price_duration_curve.png).
"""
import os
import matplotlib
matplotlib.use("Agg")
import matplotlib.dates as mdates
import matplotlib.ticker as mticker
import numpy as np
import pandas as pd
from brainpool_multiyear_data import load_brainpool_price
from broken_axis_chart import plot_broken_price_chart

ROOT = r"C:\Users\MuideenOA\Desktop\PyTut\Amiris"
BACKTEST = rf"{ROOT}\examples\backtest"
OUT_ROOT = rf"{ROOT}\Charts_50pt_BrokenAxis"
os.makedirs(OUT_ROOT, exist_ok=True)

NAVY = "#1F3A4D"
AMBER = "#A5691F"
GREY = "#6B6B6B"
TEAL = "#2E7D6B"


def load_singlezone(path):
    df = pd.read_csv(path, sep=";")
    df["ts"] = pd.to_datetime(df["TimeStep"])
    return df.set_index("ts")["ElectricityPriceInEURperMWH"]


def load_multizone(path, agent_id=1):
    df = pd.read_csv(path, sep=";")
    df["ts"] = pd.to_datetime(df["TimeStep"])
    return df[df["AgentId"] == agent_id].set_index("ts")["ElectricityPriceInEURperMWH"]


# =============================================================================
# 1. Thesis Chapter 5, Figure 5.1: headline build vs. Brainpool, full year 2027
# =============================================================================
print("1. Full-year headline overlay (thesis Figure 5.1)...")
phase37 = load_multizone(rf"{BACKTEST}\Germany2027_MarketCoupling_ROEFlex\result_Germany2027_MarketCoupling_ROEFlex\DayAheadMarketMultiZone.csv")
bp27 = load_brainpool_price(2027)
joined = pd.DataFrame({"AMIRIS": phase37, "Brainpool": bp27}).dropna()

series = {
    "Energy Brainpool (2027 forecast)": (joined.index, joined["Brainpool"].values),
    "AMIRIS (Germany2027_MarketCoupling_ROEFlex)": (joined.index, joined["AMIRIS"].values),
}
styles = {
    "Energy Brainpool (2027 forecast)": dict(color=NAVY, linewidth=0.7, alpha=0.9),
    "AMIRIS (Germany2027_MarketCoupling_ROEFlex)": dict(color=AMBER, linewidth=0.7, alpha=0.85),
}


def month_ticks(ax):
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%b"))
    ax.xaxis.set_major_locator(mdates.MonthLocator())


plot_broken_price_chart(
    series, styles,
    title="Germany 2027: AMIRIS headline build vs. Energy Brainpool, full year",
    xlabel="", ylabel="Day-ahead price (EUR/MWh)",
    out_path=rf"{OUT_ROOT}\Thesis_Ch5_Fig5.1_FullYear_HeadlineVsBrainpool.png",
    legend_loc="upper left", xtick_fn=month_ticks, figsize=(12, 6.5),
)
print("   Saved.")

# =============================================================================
# 2. Thesis Chapter 5, Figure 5.4: 17 Dec 2027 shortage-day spike, DE vs ROE
# =============================================================================
print("2. 17 Dec 2027 DE vs ROE spike day (thesis Figure 5.4)...")
de = load_multizone(rf"{BACKTEST}\Germany2027_MarketCoupling_ROEFlex\result_Germany2027_MarketCoupling_ROEFlex\DayAheadMarketMultiZone.csv", agent_id=1)
roe = load_multizone(rf"{BACKTEST}\Germany2027_MarketCoupling_ROEFlex\result_Germany2027_MarketCoupling_ROEFlex\DayAheadMarketMultiZone.csv", agent_id=9001)
day = pd.DataFrame({"DE": de, "ROE": roe}).loc["2027-12-17"]

series = {
    "Germany (AMIRIS actual)": (day.index, day["DE"].values),
    "Rest-of-Europe (AMIRIS actual)": (day.index, day["ROE"].values),
}
styles = {
    "Germany (AMIRIS actual)": dict(color=AMBER, linewidth=2.2, marker="o", markersize=5),
    "Rest-of-Europe (AMIRIS actual)": dict(color=TEAL, linewidth=2.2, marker="s", markersize=5),
}


def hour_ticks(ax):
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%H:%M"))
    ax.xaxis.set_major_locator(mdates.HourLocator(interval=3))


plot_broken_price_chart(
    series, styles,
    title="17 December 2027: Germany's price spike vs. Rest-of-Europe's own price",
    xlabel="", ylabel="Price (EUR/MWh)",
    out_path=rf"{OUT_ROOT}\Thesis_Ch5_Fig5.4_Dec17_SpikeVsROE.png",
    legend_loc="upper right", xtick_fn=hour_ticks, figsize=(11.5, 6.5),
    shade=(pd.Timestamp("2027-12-17 06:00:00"), pd.Timestamp("2027-12-17 09:00:00"), "3 unresolved\nshortage hours"),
)
print("   Saved.")

# =============================================================================
# 3. All 26 real milestone builds: price duration curve (AMIRIS_Project_Charts_AllPhases)
# =============================================================================
print("3. All 26 milestone price-duration curves...")

MILESTONES = [
    ("01_V1_NoImport", "Phase 2: V1 - No Import", 2027,
     rf"{BACKTEST}\Germany2027\result_Germany2027_rerun\DayAheadMarketSingleZone.csv", "single"),
    ("02_V1_WithImport_Original", "Phase 5: V1 - Original (Flawed) Import", 2027,
     rf"{BACKTEST}\Germany2027_V1WithImport\result_V1WithImport\DayAheadMarketSingleZone.csv", "single"),
    ("03_V1_WithImport_Fixed", "Phase 8: V1 - Fixed/Calibrated Import (Final V1)", 2027,
     rf"{BACKTEST}\Germany2027_V1WithImport_Fix\result_V1WithImport_Fix30k\DayAheadMarketSingleZone.csv", "single"),
    ("04_V2_NoImport", "Phase 4: V2 - Component-Split Demand, No Import", 2027,
     rf"{BACKTEST}\Germany2027_DemandV2\result_DemandV2_rerun\DayAheadMarketSingleZone.csv", "single"),
    ("05_V2_WithImport_Original", "Phase 5: V2 - Original (Flawed) Import", 2027,
     rf"{BACKTEST}\Germany2027_WithImport\result_WithImport\DayAheadMarketSingleZone.csv", "single"),
    ("06_V2_WithImport_Fixed", "Phase 8: V2 - Fixed/Calibrated Import (30,000 MW)", 2027,
     rf"{BACKTEST}\Germany2027_WithImport_Fix\result_WithImport_Fix30k\DayAheadMarketSingleZone.csv", "single"),
    ("07_Weather2009_WithImport", "Phase 9: Real 2009 Weather Year + Import", 2027,
     rf"{BACKTEST}\Germany2027_Weather2009_WithImport\result_Weather2009_WithImport\DayAheadMarketSingleZone.csv", "single"),
    ("08_Weekday_Fix", "Phase 11: Weekday/Weekend Calendar Fix", 2027,
     rf"{BACKTEST}\Germany2027_DemandV2Weekday_WithImport\result_DemandV2Weekday_WithImport\DayAheadMarketSingleZone.csv", "single"),
    ("09_HeatPump2009", "Phase 12: Real 2009 Heat-Pump Temperature (Null Result)", 2027,
     rf"{BACKTEST}\Germany2027_HeatPump2009_WithImport\result_HeatPump2009_WithImport\DayAheadMarketSingleZone.csv", "single"),
    ("10_ImportBlended", "Phase 15: 11-Country Blended Import Price", 2027,
     rf"{BACKTEST}\Germany2027_ImportBlended\result_ImportBlended\DayAheadMarketSingleZone.csv", "single"),
    ("11_Demand2016Base", "Phase 17: Demand Rebuilt on Real 2016 Weather-Matched Year", 2027,
     rf"{BACKTEST}\Germany2027_Demand2016Base\result_Demand2016Base\DayAheadMarketSingleZone.csv", "single"),
    ("12_FlexElectrolysis", "Phase 20: Price-Responsive Electrolysis", 2027,
     rf"{BACKTEST}\Germany2027_FlexElectrolysis\result_FlexElectrolysis\DayAheadMarketSingleZone.csv", "single"),
    ("13_FlexEMobility", "Phase 21: + Price-Responsive E-Mobility", 2027,
     rf"{BACKTEST}\Germany2027_FlexEMobility\result_FlexEMobility\DayAheadMarketSingleZone.csv", "single"),
    ("14_Feb29DropFix", "Phase 28: Feb-29-Drop Weekday Bug Fixed (Best Pre-Coupling Result)", 2027,
     rf"{BACKTEST}\Germany2027_Feb29DropFix\result_Germany2027_Feb29DropFix\DayAheadMarketSingleZone.csv", "single"),
    ("15_CyclingCostTest", "Phase 30: Real Start-Up/Cycling Cost (Confirmed No Effect)", 2027,
     rf"{BACKTEST}\Germany2027_CyclingCostTest\result_Germany2027_CyclingCostTest\DayAheadMarketSingleZone.csv", "single"),
    ("16_LigniteMarkup_m60_baseline", "Phase 31: Lignite Markup -60 (Baseline)", 2027,
     rf"{BACKTEST}\Germany2027_LigniteMarkupTest\result_Germany2027_LigniteMarkupTest\DayAheadMarketSingleZone.csv", "single"),
    ("17_MarketCoupling_Placeholder", "Phase 34: First Market Coupling (Placeholder Transmission)", 2027,
     rf"{BACKTEST}\Germany2027_MarketCoupling\result_Germany2027_MarketCoupling\DayAheadMarketMultiZone.csv", "multi"),
    ("18_MarketCoupling_RealFlow", "Phase 36: Market Coupling, Real-Flow Transmission", 2027,
     rf"{BACKTEST}\Germany2027_MarketCoupling_RealFlow\result_Germany2027_MarketCoupling_RealFlow\DayAheadMarketMultiZone.csv", "multi"),
    ("19_MarketCoupling_ROEFlex", "Phase 37: + Real ROE Storage/Subsidy (BEST RESULT OVERALL)", 2027,
     rf"{BACKTEST}\Germany2027_MarketCoupling_ROEFlex\result_Germany2027_MarketCoupling_ROEFlex\DayAheadMarketMultiZone.csv", "multi"),
    ("20_MarketCoupling_FranceZone", "Phase 42: France Disaggregated Alone (Real Step Backward)", 2027,
     rf"{BACKTEST}\Germany2027_MarketCoupling_FranceZone\result_Germany2027_MarketCoupling_FranceZone\DayAheadMarketMultiZone.csv", "multi"),
    ("21_MarketCoupling_AllZones", "Phase 43: All 10 Real Countries Disaggregated", 2027,
     rf"{BACKTEST}\Germany2027_MarketCoupling_AllZones\result_Germany2027_MarketCoupling_AllZones\DayAheadMarketMultiZone.csv", "multi"),
]
MILESTONES_2028 = [
    ("22_2028_Initial_OOS", "Phase 24: 2028 Out-of-Sample (Initial, No Re-Tuning)", 2028,
     rf"{BACKTEST}\Germany2028\result_Germany2028\DayAheadMarketSingleZone.csv", "single"),
    ("23_2028_MarketCoupling_ROEFlex", "Phase 38: 2028 Market Coupling (ROEFlex)", 2028,
     rf"{BACKTEST}\Germany2028_MarketCoupling_ROEFlex\result_Germany2028_MarketCoupling_ROEFlex\DayAheadMarketMultiZone.csv", "multi"),
]
MILESTONES_2029 = [
    ("24_2029_Initial_OOS", "Phase 24: 2029 Out-of-Sample (Initial, No Re-Tuning)", 2029,
     rf"{BACKTEST}\Germany2029\result_Germany2029\DayAheadMarketSingleZone.csv", "single"),
    ("25_2029_Feb29DropFix", "Phase 28: 2029 Feb-29-Drop Bug Fixed", 2029,
     rf"{BACKTEST}\Germany2029_Feb29DropFix\result_Germany2029_Feb29DropFix\DayAheadMarketSingleZone.csv", "single"),
    ("26_2029_MarketCoupling_ROEFlex", "Phase 38: 2029 Market Coupling (ROEFlex)", 2029,
     rf"{BACKTEST}\Germany2029_MarketCoupling_ROEFlex\result_Germany2029_MarketCoupling_ROEFlex\DayAheadMarketMultiZone.csv", "multi"),
]
ALL_MILESTONES = MILESTONES + MILESTONES_2028 + MILESTONES_2029

OUT_PHASES = rf"{OUT_ROOT}\AllPhases"
os.makedirs(OUT_PHASES, exist_ok=True)
bp_cache = {}
n_done = 0
for folder_id, name, year, path, fmt in ALL_MILESTONES:
    if not os.path.exists(path):
        print(f"   SKIP (file not found): {name}")
        continue
    if year not in bp_cache:
        bp_cache[year] = load_brainpool_price(year)
    bp = bp_cache[year]
    amiris = load_multizone(path) if fmt == "multi" else load_singlezone(path)
    joined = pd.DataFrame({"AMIRIS": amiris, "Brainpool": bp}).dropna()
    if len(joined) == 0:
        print(f"   SKIP (no overlap): {name}")
        continue

    n = len(joined)
    s_sorted = joined["AMIRIS"].sort_values(ascending=False).values
    b_sorted = joined["Brainpool"].sort_values(ascending=False).values
    rank = np.arange(1, n + 1)

    series = {
        "AMIRIS": (rank, s_sorted),
        "Brainpool (real)": (rank, b_sorted),
    }
    styles = {
        "AMIRIS": dict(color=NAVY, linewidth=1.8),
        "Brainpool (real)": dict(color=GREY, linewidth=1.6, linestyle="--"),
    }
    s, b = joined["AMIRIS"], joined["Brainpool"]
    shortage = s >= 2999.9
    bias_excl = (s[~shortage] - b[~shortage]).mean() if (~shortage).sum() > 1 else (s - b).mean()
    mae_excl = (s[~shortage] - b[~shortage]).abs().mean() if (~shortage).sum() > 1 else (s - b).abs().mean()
    corr_excl = s[~shortage].corr(b[~shortage]) if (~shortage).sum() > 1 else s.corr(b)
    note = (f"Mean: {s.mean():.1f} (Brainpool: {b.mean():.1f}) | Excl-shortage bias: {bias_excl:+.2f} | "
            f"Excl-shortage MAE: {mae_excl:.2f} | Excl-shortage r: {corr_excl:.3f} | Shortage hours: {int(shortage.sum())}")

    out_dir = os.path.join(OUT_PHASES, folder_id)
    os.makedirs(out_dir, exist_ok=True)
    plot_broken_price_chart(
        series, styles,
        title=f"{name}\nPrice Duration Curve ({year})",
        xlabel="Hour rank (all hours sorted highest price -> lowest)",
        ylabel="Price (EUR/MWh)",
        out_path=os.path.join(out_dir, "price_duration_curve.png"),
        note=note, figsize=(10, 6),
    )
    n_done += 1
    print(f"   OK: {name}")

print(f"   {n_done}/{len(ALL_MILESTONES)} milestone duration curves rebuilt.")

# =============================================================================
# 4. ppt_chart_v1_duration.png (V1 no-import, used in the all-phases deck)
# =============================================================================
print("4. ppt_chart_v1_duration.png...")
p = load_singlezone(rf"{ROOT}\result_Germany2027_test\DayAheadMarketSingleZone.csv")
n = len(p)
sorted_vals = p.sort_values(ascending=False).values
rank = np.arange(1, n + 1)
shortage_pct = (p >= 2999.9).mean() * 100
series = {"AMIRIS (V1, no import)": (rank, sorted_vals)}
styles = {"AMIRIS (V1, no import)": dict(color=NAVY, linewidth=1.8)}
plot_broken_price_chart(
    series, styles,
    title=f"Initial build (V1): price duration curve, full year 2027\n{shortage_pct:.2f}% of the year ({int((p >= 2999.9).sum())} hours) at the 3,000 EUR/MWh shortage ceiling",
    xlabel="Hour rank (sorted highest price -> lowest)",
    ylabel="Price (EUR/MWh)",
    out_path=rf"{OUT_ROOT}\ppt_chart_v1_duration.png",
    figsize=(10.5, 6.3),
)
print("   Saved.")

# =============================================================================
# 5. chart_price_duration_curve.png (baseline vs Phase 37 vs Brainpool)
# =============================================================================
print("5. chart_price_duration_curve.png (baseline vs Phase 37 vs Brainpool)...")
baseline = load_singlezone(rf"{BACKTEST}\Germany2027_Feb29DropFix\result_Germany2027_Feb29DropFix\DayAheadMarketSingleZone.csv")
phase37_de = load_multizone(rf"{BACKTEST}\Germany2027_MarketCoupling_ROEFlex\result_Germany2027_MarketCoupling_ROEFlex\DayAheadMarketMultiZone.csv")
bp = load_brainpool_price(2027)
joined3 = pd.DataFrame({
    "Baseline (pre-coupling)": baseline,
    "Phase 37 (best coupled result)": phase37_de,
    "Brainpool (real forecast)": bp,
}).dropna()
n = len(joined3)
rank = np.arange(1, n + 1)
series = {}
styles = {}
style_map = {
    "Baseline (pre-coupling)": dict(color="#96453c", linewidth=2.0),
    "Phase 37 (best coupled result)": dict(color=NAVY, linewidth=2.4),
    "Brainpool (real forecast)": dict(color=GREY, linewidth=1.8, linestyle="--"),
}
for col in joined3.columns:
    series[col] = (rank, joined3[col].sort_values(ascending=False).values)
    styles[col] = style_map[col]
note = (f"Baseline: {(baseline >= 2999.9).sum()} shortage hours. "
        f"Phase 37 (coupled): {(phase37_de >= 2999.9).sum()} shortage hours. "
        f"Brainpool's real forecast: {(bp >= 2999.9).sum()} shortage hours, for reference.")
plot_broken_price_chart(
    series, styles,
    title="Price Duration Curve: Before vs. After the Cross-Border Coupling Build (2027)",
    xlabel="Hour rank - all 8,760 hours of the year, sorted highest (rank 1) to lowest",
    ylabel="Price (EUR/MWh)",
    out_path=rf"{OUT_ROOT}\chart_price_duration_curve.png",
    note=note, figsize=(12, 7),
)
print("   Saved.")

print(f"\nAll broken-axis charts saved under {OUT_ROOT}")
