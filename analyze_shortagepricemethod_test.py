"""Compares the ShortagePriceMethod=LastSupplyPrice exploratory test against the standing
baseline (Phase 37, default ValueOfLostLoad) and Brainpool's real price."""
import pandas as pd
from brainpool_multiyear_data import load_brainpool_price

ROOT = r"C:\Users\MuideenOA\Desktop\PyTut\Amiris\examples\backtest"
BASELINE = rf"{ROOT}\Germany2027_MarketCoupling_ROEFlex\result_Germany2027_MarketCoupling_ROEFlex\DayAheadMarketMultiZone.csv"
TEST = rf"{ROOT}\Germany2027_MarketCoupling_ROEFlex_LastSupplyPrice\result_Germany2027_MarketCoupling_ROEFlex_LastSupplyPrice\DayAheadMarketMultiZone.csv"


def load_de(path):
    df = pd.read_csv(path, sep=";")
    df["ts"] = pd.to_datetime(df["TimeStep"])
    return df[df["AgentId"] == 1].set_index("ts")["ElectricityPriceInEURperMWH"]


baseline = load_de(BASELINE)
test = load_de(TEST)
bp = load_brainpool_price(2027)
joined = pd.DataFrame({"Baseline_VoLL": baseline, "Test_LastSupplyPrice": test, "Brainpool": bp}).dropna()

print("=" * 70)
print("Basic stats")
print("=" * 70)
for label in joined.columns:
    s = joined[label]
    print(f"{label:>22}: mean={s.mean():.2f} min={s.min():.2f} max={s.max():.2f}")

print()
print("=" * 70)
print("Correlation / bias / MAE vs. Brainpool")
print("=" * 70)
for label in ["Baseline_VoLL", "Test_LastSupplyPrice"]:
    s = joined[label]
    shortage_baseline = joined["Baseline_VoLL"] >= 2999.9  # use baseline's own shortage-hour definition throughout, for a fair excl-shortage comparison
    r_all = s.corr(joined["Brainpool"])
    r_excl = s[~shortage_baseline].corr(joined.loc[~shortage_baseline, "Brainpool"])
    bias = (s - joined["Brainpool"]).mean()
    bias_excl = (s[~shortage_baseline] - joined.loc[~shortage_baseline, "Brainpool"]).mean()
    mae = (s - joined["Brainpool"]).abs().mean()
    mae_excl = (s[~shortage_baseline] - joined.loc[~shortage_baseline, "Brainpool"]).abs().mean()
    own_shortage = (s >= 2999.9).sum()
    print(f"{label:>22}: all_r={r_all:.4f} excl_r={r_excl:.4f} bias={bias:+.2f} bias_excl={bias_excl:+.2f} "
          f"mae={mae:.2f} mae_excl={mae_excl:.2f} own_hours_at_3000={own_shortage}")

print()
print("=" * 70)
print("What happened during the baseline's 7 shortage hours specifically")
print("=" * 70)
shortage_hours = joined[joined["Baseline_VoLL"] >= 2999.9]
print(shortage_hours[["Baseline_VoLL", "Test_LastSupplyPrice", "Brainpool"]])
