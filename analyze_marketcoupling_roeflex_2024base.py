"""Compares the 2024-base ROE rebuild against the standing-best 2023-base result (Phase 37)
and Brainpool's real 2027 price. Isolates the ROE data-year switch as the only variable."""
import pandas as pd
from brainpool_multiyear_data import load_brainpool_price

ROOT = r"C:\Users\MuideenOA\Desktop\PyTut\Amiris\examples\backtest"
BASE2024 = rf"{ROOT}\Germany2027_MarketCoupling_ROEFlex_2024base\result_Germany2027_MarketCoupling_ROEFlex_2024base\DayAheadMarketMultiZone.csv"
BASE2023 = rf"{ROOT}\Germany2027_MarketCoupling_ROEFlex\result_Germany2027_MarketCoupling_ROEFlex\DayAheadMarketMultiZone.csv"
BASELINE = rf"{ROOT}\Germany2027_Feb29DropFix\result_Germany2027_Feb29DropFix\DayAheadMarketSingleZone.csv"
STORAGE_2024 = rf"{ROOT}\Germany2027_MarketCoupling_ROEFlex_2024base\result_Germany2027_MarketCoupling_ROEFlex_2024base\GenericFlexibilityTrader.csv"


def load_de_multizone(path):
    df = pd.read_csv(path, sep=";")
    df["ts"] = pd.to_datetime(df["TimeStep"])
    de = df[df["AgentId"] == 1].set_index("ts")
    return de


roe2024 = load_de_multizone(BASE2024)
roe2023 = load_de_multizone(BASE2023)

baseline_df = pd.read_csv(BASELINE, sep=";")
baseline_df["ts"] = pd.to_datetime(baseline_df["TimeStep"])
baseline = baseline_df.set_index("ts")["ElectricityPriceInEURperMWH"]

bp = load_brainpool_price(2027)

joined = pd.DataFrame({
    "ROE_2024base": roe2024["ElectricityPriceInEURperMWH"],
    "ROE_2023base_Phase37": roe2023["ElectricityPriceInEURperMWH"],
    "Baseline_NoCoupling": baseline,
    "Brainpool": bp,
}).dropna()

print("=" * 70)
print("STEP 1: Basic price stats")
print("=" * 70)
for label in joined.columns:
    s = joined[label]
    print(f"{label:>22}: mean={s.mean():.2f}, min={s.min():.2f}, max={s.max():.2f}, "
          f"negative hours={len(s[s<0])} ({100*len(s[s<0])/len(s):.1f}%)")

print()
print("=" * 70)
print("STEP 2: Correlation and bias vs. Brainpool - 2024-base vs. standing-best 2023-base")
print("=" * 70)
for label in ["Baseline_NoCoupling", "ROE_2023base_Phase37", "ROE_2024base"]:
    s = joined[label]
    shortage = s >= 2999.9
    r_all = s.corr(joined["Brainpool"])
    r_excl = s[~shortage].corr(joined.loc[~shortage, "Brainpool"])
    bias = (s - joined["Brainpool"]).mean()
    bias_excl = (s[~shortage] - joined.loc[~shortage, "Brainpool"]).mean()
    mae = (s - joined["Brainpool"]).abs().mean()
    mae_excl = (s[~shortage] - joined.loc[~shortage, "Brainpool"]).abs().mean()
    print(f"{label:>22}: all-hours r={r_all:.4f}, excl-shortage r={r_excl:.4f}, "
          f"bias={bias:+.2f}, bias(excl)={bias_excl:+.2f}, MAE={mae:.2f}, MAE(excl)={mae_excl:.2f}, "
          f"shortage hours={shortage.sum()}")

print()
print("=" * 70)
print("STEP 3: Do the 2024-base ROE storage agents dispatch?")
print("=" * 70)
storage = pd.read_csv(STORAGE_2024, sep=";")
storage["ts"] = pd.to_datetime(storage["TimeStep"])
for agent_id, label in [(9601, "ROE Pumped Storage"), (9602, "ROE Reservoir Hydro")]:
    a = storage[storage["AgentId"] == agent_id]
    charge = a["AwardedChargeEnergyInMWH"]
    discharge = a["AwardedDischargeEnergyInMWH"]
    print(f"{label}: charging hours={len(charge[charge>0])}, total charge={charge.sum():,.0f} MWh, "
          f"discharging hours={len(discharge[discharge>0])}, total discharge={discharge.sum():,.0f} MWh")

print()
print("=" * 70)
print("STEP 4: Transmission utilization")
print("=" * 70)
imports = roe2024["AwardedNetEnergyFromImportInMWH"]
exports = roe2024["AwardedNetEnergyToExportInMWH"]
print(f"DE importing from ROE: {len(imports[imports>0])} hours, max hour {imports.max():,.0f} MWh")
print(f"DE exporting to ROE: {len(exports[exports>0])} hours, max hour {exports.max():,.0f} MWh")
