"""Phase 43 analysis: does full disaggregation (all 10 real named neighbour zones, star
topology) confirm Phase 42's prediction that extending the star-topology approach spreads
the same failure mode rather than fixing it? Compares against Phase 37 (aggregate ROE, best
result) and Phase 42 (single-country France pilot)."""
import pandas as pd
from brainpool_multiyear_data import load_brainpool_price

ROOT = r"C:\Users\MuideenOA\Desktop\PyTut\Amiris\examples\backtest"
PHASE37 = rf"{ROOT}\Germany2027_MarketCoupling_ROEFlex\result_Germany2027_MarketCoupling_ROEFlex\DayAheadMarketMultiZone.csv"
PHASE42 = rf"{ROOT}\Germany2027_MarketCoupling_FranceZone\result_Germany2027_MarketCoupling_FranceZone\DayAheadMarketMultiZone.csv"
PHASE43 = rf"{ROOT}\Germany2027_MarketCoupling_AllZones\result_Germany2027_MarketCoupling_AllZones\DayAheadMarketMultiZone.csv"


def load_de(path):
    df = pd.read_csv(path, sep=";")
    df["ts"] = pd.to_datetime(df["TimeStep"])
    return df[df["AgentId"] == 1].set_index("ts")["ElectricityPriceInEURperMWH"]


phase37 = load_de(PHASE37)
phase42 = load_de(PHASE42)
phase43 = load_de(PHASE43)
bp = load_brainpool_price(2027)

joined = pd.DataFrame({
    "Phase37_AggregateROE": phase37,
    "Phase42_FranceOnly": phase42,
    "Phase43_AllZones": phase43,
    "Brainpool": bp,
}).dropna()

print(f"Joined hours: {len(joined)}\n")
for label in ["Phase37_AggregateROE", "Phase42_FranceOnly", "Phase43_AllZones"]:
    s = joined[label]
    shortage = s >= 2999.9
    r_all = s.corr(joined["Brainpool"])
    r_excl = s[~shortage].corr(joined.loc[~shortage, "Brainpool"])
    bias_all = (s - joined["Brainpool"]).mean()
    bias_excl = (s[~shortage] - joined.loc[~shortage, "Brainpool"]).mean()
    mae_excl = (s[~shortage] - joined.loc[~shortage, "Brainpool"]).abs().mean()
    neg_pct = (s < 0).mean() * 100
    print(f"{label}:")
    print(f"  shortage hours: {shortage.sum()}")
    print(f"  mean price: {s.mean():.2f} (Brainpool: {joined['Brainpool'].mean():.2f})")
    print(f"  all-hours r: {r_all:.4f} | excl-shortage r: {r_excl:.4f}")
    print(f"  all-hours bias: {bias_all:+.2f} | excl-shortage bias: {bias_excl:+.2f}")
    print(f"  excl-shortage MAE: {mae_excl:.2f}")
    print(f"  negative-price hours: {neg_pct:.1f}%\n")
