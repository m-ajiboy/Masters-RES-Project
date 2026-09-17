"""Compares the ForecastError exploratory test against the standing baseline (Phase 37) and
Brainpool's real price - including shortage-hour count, since that is the specific thing
being tracked across this whole investigation."""
import pandas as pd
from brainpool_multiyear_data import load_brainpool_price

ROOT = r"C:\Users\MuideenOA\Desktop\PyTut\Amiris\examples\backtest"
BASELINE = rf"{ROOT}\Germany2027_MarketCoupling_ROEFlex\result_Germany2027_MarketCoupling_ROEFlex\DayAheadMarketMultiZone.csv"
TEST = rf"{ROOT}\Germany2027_MarketCoupling_ROEFlex_ForecastErrorTest\result_Germany2027_MarketCoupling_ROEFlex_ForecastErrorTest\DayAheadMarketMultiZone.csv"


def load_de(path):
    df = pd.read_csv(path, sep=";")
    df["ts"] = pd.to_datetime(df["TimeStep"])
    return df[df["AgentId"] == 1].set_index("ts")["ElectricityPriceInEURperMWH"]


baseline = load_de(BASELINE)
test = load_de(TEST)
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
    hrs_changed = (s.round(4) != joined["Baseline"].round(4)).sum() if label != "Baseline" else 0
    print(f"{label:>10}: all_r={r_all:.4f} excl_r={r_excl:.4f} bias={bias:+.2f} bias_excl={bias_excl:+.2f} "
          f"mae={mae:.2f} mae_excl={mae_excl:.2f} hrs_changed={hrs_changed}")

print()
print("Price at the baseline's 7 shortage hours, before vs after:")
print(joined.loc[sorted(shortage_baseline_hours), ["Baseline", "Test", "Brainpool"]])
