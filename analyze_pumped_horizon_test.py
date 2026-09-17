"""Checks whether widening ROE Pumped Storage's scheduling horizon reduces the physical
shortage-hour count, resolves the 3 targeted 2027-12-17 hours, or changes its depletion
pattern - plus overall correlation/bias/MAE impact vs. baseline and Brainpool."""
import pandas as pd
from brainpool_multiyear_data import load_brainpool_price

ROOT = r"C:\Users\MuideenOA\Desktop\PyTut\Amiris\examples\backtest"
BASE_DIR = rf"{ROOT}\Germany2027_MarketCoupling_ROEFlex\result_Germany2027_MarketCoupling_ROEFlex"
TEST_DIR = rf"{ROOT}\Germany2027_MarketCoupling_ROEFlex_PumpedHorizonTest\result_Germany2027_MarketCoupling_ROEFlex_PumpedHorizonTest"


def load_de(path):
    df = pd.read_csv(path, sep=";")
    df["ts"] = pd.to_datetime(df["TimeStep"])
    return df[df["AgentId"] == 1].set_index("ts")["ElectricityPriceInEURperMWH"]


baseline = load_de(rf"{BASE_DIR}\DayAheadMarketMultiZone.csv")
test = load_de(rf"{TEST_DIR}\DayAheadMarketMultiZone.csv")
bp = load_brainpool_price(2027)
joined = pd.DataFrame({"Baseline": baseline, "Test": test, "Brainpool": bp}).dropna()

shortage_baseline_hours = set(joined[joined["Baseline"] >= 2999.9].index)
shortage_test_hours = set(joined[joined["Test"] >= 2999.9].index)

print(f"Baseline shortage hours: {len(shortage_baseline_hours)}")
print(f"Test shortage hours: {len(shortage_test_hours)}")
print(f"Resolved (was shortage, now isn't): {sorted(shortage_baseline_hours - shortage_test_hours)}")
print(f"New (wasn't shortage, now is): {sorted(shortage_test_hours - shortage_baseline_hours)}")
print()

shortage_baseline_mask = joined["Baseline"] >= 2999.9
for label in ["Baseline", "Test"]:
    s = joined[label]
    r_all = s.corr(joined["Brainpool"])
    r_excl = s[~shortage_baseline_mask].corr(joined.loc[~shortage_baseline_mask, "Brainpool"])
    bias = (s - joined["Brainpool"]).mean()
    bias_excl = (s[~shortage_baseline_mask] - joined.loc[~shortage_baseline_mask, "Brainpool"]).mean()
    mae = (s - joined["Brainpool"]).abs().mean()
    mae_excl = (s[~shortage_baseline_mask] - joined.loc[~shortage_baseline_mask, "Brainpool"]).abs().mean()
    print(f"{label:>10}: all_r={r_all:.4f} excl_r={r_excl:.4f} bias={bias:+.2f} bias_excl={bias_excl:+.2f} "
          f"mae={mae:.2f} mae_excl={mae_excl:.2f}")

print()
print("Price at the baseline's 7 shortage hours, before vs after:")
print(joined.loc[sorted(shortage_baseline_hours), ["Baseline", "Test", "Brainpool"]])

print()
print("=" * 70)
print("Pumped Storage (9601) state at the 3 targeted hours, before vs after")
print("=" * 70)
target_hours = [pd.Timestamp("2027-12-17 06:00:00"), pd.Timestamp("2027-12-17 07:00:00"), pd.Timestamp("2027-12-17 08:00:00")]

for label, res_dir in [("BASELINE", BASE_DIR), ("TEST", TEST_DIR)]:
    storage = pd.read_csv(rf"{res_dir}\GenericFlexibilityTrader.csv", sep=";")
    storage["ts"] = pd.to_datetime(storage["TimeStep"])
    pumped = storage[storage["AgentId"] == 9601].set_index("ts")
    print(f"\n{label}:")
    for ts in target_hours:
        if ts in pumped.index:
            row = pumped.loc[ts]
            print(f"  {ts}: stored={row['StoredEnergyInMWH']:.1f} MWh, "
                  f"discharge={row['AwardedDischargeEnergyInMWH']:.1f} MWh, "
                  f"charge={row['AwardedChargeEnergyInMWH']:.1f} MWh")
