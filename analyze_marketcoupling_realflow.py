"""Compares the real-flow-derived MarketCoupling result (Phase 36) against Phase 34's
placeholder-based coupling result and the pre-coupling baseline, all vs. Brainpool's real
2027 price."""
import pandas as pd
from brainpool_multiyear_data import load_brainpool_price

ROOT = r"C:\Users\MuideenOA\Desktop\PyTut\Amiris\examples\backtest"
REALFLOW = rf"{ROOT}\Germany2027_MarketCoupling_RealFlow\result_Germany2027_MarketCoupling_RealFlow\DayAheadMarketMultiZone.csv"
PLACEHOLDER = rf"{ROOT}\Germany2027_MarketCoupling\result_Germany2027_MarketCoupling\DayAheadMarketMultiZone.csv"
BASELINE = rf"{ROOT}\Germany2027_Feb29DropFix\result_Germany2027_Feb29DropFix\DayAheadMarketSingleZone.csv"


def load_de_multizone(path):
    df = pd.read_csv(path, sep=";")
    df["ts"] = pd.to_datetime(df["TimeStep"])
    de = df[df["AgentId"] == 1].set_index("ts")
    return de


realflow = load_de_multizone(REALFLOW)
placeholder = load_de_multizone(PLACEHOLDER)

baseline_df = pd.read_csv(BASELINE, sep=";")
baseline_df["ts"] = pd.to_datetime(baseline_df["TimeStep"])
baseline = baseline_df.set_index("ts")["ElectricityPriceInEURperMWH"]

bp = load_brainpool_price(2027)

joined = pd.DataFrame({
    "RealFlow": realflow["ElectricityPriceInEURperMWH"],
    "Placeholder": placeholder["ElectricityPriceInEURperMWH"],
    "Baseline": baseline,
    "Brainpool": bp,
}).dropna()

print("=" * 70)
print("STEP 1: Basic price stats")
print("=" * 70)
for label in ["RealFlow", "Placeholder", "Baseline", "Brainpool"]:
    s = joined[label]
    print(f"{label:>12}: mean={s.mean():.2f}, min={s.min():.2f}, max={s.max():.2f}, "
          f"negative hours={len(s[s<0])} ({100*len(s[s<0])/len(s):.1f}%)")

print()
print("=" * 70)
print("STEP 2: Correlation and bias vs. Brainpool - all three builds")
print("=" * 70)
for label in ["Baseline", "Placeholder", "RealFlow"]:
    s = joined[label]
    shortage = s >= 2999.9
    r_all = s.corr(joined["Brainpool"])
    r_excl = s[~shortage].corr(joined.loc[~shortage, "Brainpool"])
    bias = (s - joined["Brainpool"]).mean()
    mae = (s - joined["Brainpool"]).abs().mean()
    print(f"{label:>12}: all-hours r={r_all:.4f}, excl-shortage r={r_excl:.4f}, "
          f"bias={bias:+.2f}, MAE={mae:.2f}, shortage hours={shortage.sum()}")

print()
print("=" * 70)
print("STEP 3: Transmission utilization - real-flow capacity vs. placeholder")
print("=" * 70)
imports = realflow["AwardedNetEnergyFromImportInMWH"]
exports = realflow["AwardedNetEnergyToExportInMWH"]
print(f"Real-flow ceiling: DE->ROE=21,593 MW, ROE->DE=22,012 MW (vs. placeholder's flat 30,000 MW)")
print(f"DE importing from ROE: {len(imports[imports>0])} hours, total {imports.sum():,.0f} MWh, max hour {imports.max():,.0f} MWh")
print(f"DE exporting to ROE: {len(exports[exports>0])} hours, total {exports.sum():,.0f} MWh, max hour {exports.max():,.0f} MWh")
print(f"Hours DE imports AT the real-flow ceiling (>=21,500 MWh): {len(imports[imports>=21500])}")
print(f"Hours DE exports AT the real-flow ceiling (>=21,900 MWh): {len(exports[exports>=21900])}")
