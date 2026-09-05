"""Compares the ROE-storage/subsidy result (Phase 37) against Phase 36's real-flow-transmission
result and the pre-coupling baseline, all vs. Brainpool's real 2027 price. Also checks whether
the new ROE storage agents actually dispatch (i.e. genuinely help smooth scarcity), not just
exist on paper."""
import pandas as pd
from brainpool_multiyear_data import load_brainpool_price

ROOT = r"C:\Users\MuideenOA\Desktop\PyTut\Amiris\examples\backtest"
ROEFLEX = rf"{ROOT}\Germany2027_MarketCoupling_ROEFlex\result_Germany2027_MarketCoupling_ROEFlex\DayAheadMarketMultiZone.csv"
REALFLOW = rf"{ROOT}\Germany2027_MarketCoupling_RealFlow\result_Germany2027_MarketCoupling_RealFlow\DayAheadMarketMultiZone.csv"
BASELINE = rf"{ROOT}\Germany2027_Feb29DropFix\result_Germany2027_Feb29DropFix\DayAheadMarketSingleZone.csv"
ROEFLEX_STORAGE = rf"{ROOT}\Germany2027_MarketCoupling_ROEFlex\result_Germany2027_MarketCoupling_ROEFlex\GenericFlexibilityTrader.csv"


def load_de_multizone(path):
    df = pd.read_csv(path, sep=";")
    df["ts"] = pd.to_datetime(df["TimeStep"])
    de = df[df["AgentId"] == 1].set_index("ts")
    return de


roeflex = load_de_multizone(ROEFLEX)
realflow = load_de_multizone(REALFLOW)

baseline_df = pd.read_csv(BASELINE, sep=";")
baseline_df["ts"] = pd.to_datetime(baseline_df["TimeStep"])
baseline = baseline_df.set_index("ts")["ElectricityPriceInEURperMWH"]

bp = load_brainpool_price(2027)

joined = pd.DataFrame({
    "ROEFlex": roeflex["ElectricityPriceInEURperMWH"],
    "RealFlow": realflow["ElectricityPriceInEURperMWH"],
    "Baseline": baseline,
    "Brainpool": bp,
}).dropna()

print("=" * 70)
print("STEP 1: Basic price stats")
print("=" * 70)
for label in ["ROEFlex", "RealFlow", "Baseline", "Brainpool"]:
    s = joined[label]
    print(f"{label:>12}: mean={s.mean():.2f}, min={s.min():.2f}, max={s.max():.2f}, "
          f"negative hours={len(s[s<0])} ({100*len(s[s<0])/len(s):.1f}%)")

print()
print("=" * 70)
print("STEP 2: Correlation and bias vs. Brainpool - all builds")
print("=" * 70)
for label in ["Baseline", "RealFlow", "ROEFlex"]:
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
print("STEP 3: Do the new ROE storage agents actually dispatch?")
print("=" * 70)
storage = pd.read_csv(ROEFLEX_STORAGE, sep=";")
storage["ts"] = pd.to_datetime(storage["TimeStep"])
for agent_id, label in [(9601, "ROE Pumped Storage"), (9602, "ROE Reservoir Hydro")]:
    a = storage[storage["AgentId"] == agent_id]
    charge = a["AwardedChargeEnergyInMWH"]
    discharge = a["AwardedDischargeEnergyInMWH"]
    print(f"{label}: charging hours={len(charge[charge>0])}, total charge={charge.sum():,.0f} MWh, "
          f"discharging hours={len(discharge[discharge>0])}, total discharge={discharge.sum():,.0f} MWh")

print()
print("=" * 70)
print("STEP 4: Transmission utilization - did ROE flexibility reduce ceiling-hugging?")
print("=" * 70)
imports = roeflex["AwardedNetEnergyFromImportInMWH"]
exports = roeflex["AwardedNetEnergyToExportInMWH"]
print(f"DE importing from ROE: {len(imports[imports>0])} hours, max hour {imports.max():,.0f} MWh")
print(f"DE exporting to ROE: {len(exports[exports>0])} hours, max hour {exports.max():,.0f} MWh")
print(f"Hours DE imports AT the real-flow ceiling (>=21,500 MWh): {len(imports[imports>=21500])}")
print(f"Hours DE exports AT the real-flow ceiling (>=21,900 MWh): {len(exports[exports>=21900])}")
