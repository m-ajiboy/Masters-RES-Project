"""Compares the mesh-topology AllZones rebuild against Phase 43 (star topology) and Phase 37
(single aggregate zone) - testing Phase 45's diagnosis that the star topology, not
disaggregation itself, was the real cause of Phase 42/43's stranded-surplus problem."""
import pandas as pd
from brainpool_multiyear_data import load_brainpool_price

ROOT = r"C:\Users\MuideenOA\Desktop\PyTut\Amiris\examples\backtest"

BUILDS = {
    "Phase37_Aggregate": rf"{ROOT}\Germany2027_MarketCoupling_ROEFlex\result_Germany2027_MarketCoupling_ROEFlex\DayAheadMarketMultiZone.csv",
    "Phase43_Star": rf"{ROOT}\Germany2027_MarketCoupling_AllZones\result_Germany2027_MarketCoupling_AllZones\DayAheadMarketMultiZone.csv",
    "Mesh": rf"{ROOT}\Germany2027_MarketCoupling_AllZones_Mesh\result_Germany2027_MarketCoupling_AllZones_Mesh\DayAheadMarketMultiZone.csv",
}


def load_de(path):
    df = pd.read_csv(path, sep=";")
    df["ts"] = pd.to_datetime(df["TimeStep"])
    return df[df["AgentId"] == 1].set_index("ts")["ElectricityPriceInEURperMWH"]


bp = load_brainpool_price(2027)
series = {label: load_de(path) for label, path in BUILDS.items()}
joined = pd.DataFrame(series).join(bp.rename("Brainpool")).dropna()

print("=" * 90)
print(f"{'Build':<20} {'mean':>9} {'shortage_hrs':>13} {'all_r':>8} {'excl_r':>8} {'bias_excl':>10} {'mae_excl':>9}")
print("=" * 90)
for label in BUILDS:
    s = joined[label]
    shortage = s >= 2999.9
    r_all = s.corr(joined["Brainpool"])
    r_excl = s[~shortage].corr(joined.loc[~shortage, "Brainpool"])
    bias_excl = (s[~shortage] - joined.loc[~shortage, "Brainpool"]).mean()
    mae_excl = (s[~shortage] - joined.loc[~shortage, "Brainpool"]).abs().mean()
    print(f"{label:<20} {s.mean():>9.2f} {shortage.sum():>13} {r_all:>8.4f} {r_excl:>8.4f} "
          f"{bias_excl:>+10.2f} {mae_excl:>9.2f}")

print()
print("Brainpool reference: mean=68.04, shortage_hrs=0")
