"""Compares the real-growth-projected 2028/2029 ROE builds against the standing frozen-ROE
out-of-sample results and Brainpool's real price."""
import pandas as pd
from brainpool_multiyear_data import load_brainpool_price

ROOT = r"C:\Users\MuideenOA\Desktop\PyTut\Amiris\examples\backtest"


def load_de(path):
    df = pd.read_csv(path, sep=";")
    df["ts"] = pd.to_datetime(df["TimeStep"])
    return df[df["AgentId"] == 1].set_index("ts")["ElectricityPriceInEURperMWH"]


for year, frozen_folder, growth_folder in [
    (2028, "Germany2028_MarketCoupling_ROEFlex", "Germany2028_MarketCoupling_ROEFlex_Growth"),
    (2029, "Germany2029_MarketCoupling_ROEFlex", "Germany2029_MarketCoupling_ROEFlex_Growth"),
]:
    frozen = load_de(rf"{ROOT}\{frozen_folder}\result_{frozen_folder}\DayAheadMarketMultiZone.csv")
    growth = load_de(rf"{ROOT}\{growth_folder}\result_{growth_folder}\DayAheadMarketMultiZone.csv")
    bp = load_brainpool_price(year)
    joined = pd.DataFrame({"Frozen": frozen, "Growth": growth, "Brainpool": bp}).dropna()

    print("=" * 70)
    print(f"{year}")
    print("=" * 70)
    for label in ["Frozen", "Growth"]:
        s = joined[label]
        shortage = s >= 2999.9
        r_all = s.corr(joined["Brainpool"])
        r_excl = s[~shortage].corr(joined.loc[~shortage, "Brainpool"])
        bias = (s - joined["Brainpool"]).mean()
        bias_excl = (s[~shortage] - joined.loc[~shortage, "Brainpool"]).mean()
        mae = (s - joined["Brainpool"]).abs().mean()
        mae_excl = (s[~shortage] - joined.loc[~shortage, "Brainpool"]).abs().mean()
        print(f"{label:>8}: mean={s.mean():.2f} shortage_hrs={shortage.sum()} "
              f"all_r={r_all:.4f} excl_r={r_excl:.4f} bias={bias:+.2f} bias_excl={bias_excl:+.2f} "
              f"mae={mae:.2f} mae_excl={mae_excl:.2f}")
    print()
