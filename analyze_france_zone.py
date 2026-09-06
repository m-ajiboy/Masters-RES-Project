"""Phase 42 analysis: does disaggregating France out of the aggregate ROE zone into its own
real zone improve on Phase 37's single-aggregate-zone result (this project's best-ever:
excl-shortage bias -0.59, MAE 18.99, excl-shortage r 0.717)? Compares the new 3-zone
DE/FR/ROE-9 build directly against that baseline and against Brainpool's real 2027 forecast."""
import pandas as pd
from brainpool_multiyear_data import load_brainpool_price

ROOT = r"C:\Users\MuideenOA\Desktop\PyTut\Amiris\examples\backtest"
BASELINE = rf"{ROOT}\Germany2027_MarketCoupling_ROEFlex\result_Germany2027_MarketCoupling_ROEFlex\DayAheadMarketMultiZone.csv"
NEW = rf"{ROOT}\Germany2027_MarketCoupling_FranceZone\result_Germany2027_MarketCoupling_FranceZone\DayAheadMarketMultiZone.csv"


def load_de(path):
    df = pd.read_csv(path, sep=";")
    df["ts"] = pd.to_datetime(df["TimeStep"])
    return df[df["AgentId"] == 1].set_index("ts")


baseline = load_de(BASELINE)["ElectricityPriceInEURperMWH"]
new = load_de(NEW)["ElectricityPriceInEURperMWH"]
bp = load_brainpool_price(2027)

joined = pd.DataFrame({"Baseline_AggregateROE": baseline, "FranceZone": new, "Brainpool": bp}).dropna()

print(f"Joined hours: {len(joined)}")
for label in ["Baseline_AggregateROE", "FranceZone"]:
    s = joined[label]
    shortage = s >= 2999.9
    r_all = s.corr(joined["Brainpool"])
    r_excl = s[~shortage].corr(joined.loc[~shortage, "Brainpool"])
    bias_all = (s - joined["Brainpool"]).mean()
    bias_excl = (s[~shortage] - joined.loc[~shortage, "Brainpool"]).mean()
    mae_excl = (s[~shortage] - joined.loc[~shortage, "Brainpool"]).abs().mean()
    neg_pct = (s < 0).mean() * 100
    print(f"\n{label}:")
    print(f"  shortage hours: {shortage.sum()}")
    print(f"  mean price: {s.mean():.2f} (Brainpool: {joined['Brainpool'].mean():.2f})")
    print(f"  all-hours r: {r_all:.4f} | excl-shortage r: {r_excl:.4f}")
    print(f"  all-hours bias: {bias_all:+.2f} | excl-shortage bias: {bias_excl:+.2f}")
    print(f"  excl-shortage MAE: {mae_excl:.2f}")
    print(f"  negative-price hours: {neg_pct:.1f}%")

# Check France zone's own internals: is it actually trading, and at a sensible price?
fr = load_de(NEW.replace("DayAheadMarketMultiZone.csv", "DayAheadMarketMultiZone.csv"))
full = pd.read_csv(NEW, sep=";")
full["ts"] = pd.to_datetime(full["TimeStep"])
fr_zone = full[full["AgentId"] == 8001].set_index("ts")
roe_zone = full[full["AgentId"] == 9001].set_index("ts")
print(f"\nFrance zone (8001) own price: mean={fr_zone['ElectricityPriceInEURperMWH'].mean():.2f}, "
      f"min={fr_zone['ElectricityPriceInEURperMWH'].min():.2f}, max={fr_zone['ElectricityPriceInEURperMWH'].max():.2f}")
print(f"ROE-9 zone (9001) own price: mean={roe_zone['ElectricityPriceInEURperMWH'].mean():.2f}, "
      f"min={roe_zone['ElectricityPriceInEURperMWH'].min():.2f}, max={roe_zone['ElectricityPriceInEURperMWH'].max():.2f}")
print(f"\nDE import from FR (mean MWh/hr): {full[full['AgentId']==1]['AwardedNetEnergyFromImportInMWH'].mean():.1f}")
