"""Compares the three per-fuel markup-band exploratory tests (gas, coal, oil) against the
standing baseline (Phase 37) and Brainpool's real price - same excl-shortage methodology
(shortage hours defined by the BASELINE's own 3,000 EUR/MWh hours) used throughout."""
import pandas as pd
from brainpool_multiyear_data import load_brainpool_price

ROOT = r"C:\Users\MuideenOA\Desktop\PyTut\Amiris\examples\backtest"
BASELINE = rf"{ROOT}\Germany2027_MarketCoupling_ROEFlex\result_Germany2027_MarketCoupling_ROEFlex\DayAheadMarketMultiZone.csv"

TESTS = {
    "Gas (-25/25)": rf"{ROOT}\Germany2027_MarketCoupling_ROEFlex_GasMarkupTest\result_Germany2027_MarketCoupling_ROEFlex_GasMarkupTest\DayAheadMarketMultiZone.csv",
    "Coal (-30/10)": rf"{ROOT}\Germany2027_MarketCoupling_ROEFlex_CoalMarkupTest\result_Germany2027_MarketCoupling_ROEFlex_CoalMarkupTest\DayAheadMarketMultiZone.csv",
    "Oil (-10/15)": rf"{ROOT}\Germany2027_MarketCoupling_ROEFlex_OilMarkupTest\result_Germany2027_MarketCoupling_ROEFlex_OilMarkupTest\DayAheadMarketMultiZone.csv",
}


def load_de(path):
    df = pd.read_csv(path, sep=";")
    df["ts"] = pd.to_datetime(df["TimeStep"])
    return df[df["AgentId"] == 1].set_index("ts")["ElectricityPriceInEURperMWH"]


baseline = load_de(BASELINE)
bp = load_brainpool_price(2027)
shortage_baseline = baseline >= 2999.9

data = {"Baseline": baseline}
for label, path in TESTS.items():
    data[label] = load_de(path)
joined = pd.DataFrame(data).join(bp.rename("Brainpool")).dropna()

print("=" * 90)
print(f"{'Build':<16} {'all_r':>8} {'excl_r':>8} {'bias':>8} {'bias_excl':>10} {'MAE':>8} {'MAE_excl':>9} {'hrs_changed':>12}")
print("=" * 90)
for label in ["Baseline"] + list(TESTS.keys()):
    s = joined[label]
    r_all = s.corr(joined["Brainpool"])
    r_excl = s[~shortage_baseline].corr(joined.loc[~shortage_baseline, "Brainpool"])
    bias = (s - joined["Brainpool"]).mean()
    bias_excl = (s[~shortage_baseline] - joined.loc[~shortage_baseline, "Brainpool"]).mean()
    mae = (s - joined["Brainpool"]).abs().mean()
    mae_excl = (s[~shortage_baseline] - joined.loc[~shortage_baseline, "Brainpool"]).abs().mean()
    hrs_changed = (s.round(4) != joined["Baseline"].round(4)).sum() if label != "Baseline" else 0
    print(f"{label:<16} {r_all:>8.4f} {r_excl:>8.4f} {bias:>+8.2f} {bias_excl:>+10.2f} {mae:>8.2f} {mae_excl:>9.2f} {hrs_changed:>12}")
