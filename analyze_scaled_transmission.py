"""Phase 39 analysis: does scaling the DE<->ROE transmission capacity by DE's own real
demand growth recover 2027-level shortage-hour counts for 2028/2029? Compares unscaled
(Phase 38) vs scaled (Phase 39) vs baseline, both all-hours and excl-shortage."""
import pandas as pd
from brainpool_multiyear_data import load_brainpool_price

ROOT = r"C:\Users\MuideenOA\Desktop\PyTut\Amiris\examples\backtest"

CONFIGS = {
    2028: {
        "unscaled": rf"{ROOT}\Germany2028_MarketCoupling_ROEFlex\result_Germany2028_MarketCoupling_ROEFlex\DayAheadMarketMultiZone.csv",
        "scaled": rf"{ROOT}\Germany2028_MarketCoupling_ROEFlex_ScaledTransmission\result_Germany2028_MarketCoupling_ROEFlex_ScaledTransmission\DayAheadMarketMultiZone.csv",
        "baseline": rf"{ROOT}\Germany2028\result_Germany2028\DayAheadMarketSingleZone.csv",
    },
    2029: {
        "unscaled": rf"{ROOT}\Germany2029_MarketCoupling_ROEFlex\result_Germany2029_MarketCoupling_ROEFlex\DayAheadMarketMultiZone.csv",
        "scaled": rf"{ROOT}\Germany2029_MarketCoupling_ROEFlex_ScaledTransmission\result_Germany2029_MarketCoupling_ROEFlex_ScaledTransmission\DayAheadMarketMultiZone.csv",
        "baseline": rf"{ROOT}\Germany2029_Feb29DropFix\result_Germany2029_Feb29DropFix\DayAheadMarketSingleZone.csv",
    },
}


def load_de_multizone(path):
    df = pd.read_csv(path, sep=";")
    df["ts"] = pd.to_datetime(df["TimeStep"])
    return df[df["AgentId"] == 1].set_index("ts")["ElectricityPriceInEURperMWH"]


def load_singlezone(path):
    df = pd.read_csv(path, sep=";")
    df["ts"] = pd.to_datetime(df["TimeStep"])
    return df.set_index("ts")["ElectricityPriceInEURperMWH"]


for year, cfg in CONFIGS.items():
    print("\n" + "=" * 70)
    print(f"YEAR {year}")
    print("=" * 70)
    unscaled = load_de_multizone(cfg["unscaled"])
    scaled = load_de_multizone(cfg["scaled"])
    baseline = load_singlezone(cfg["baseline"])
    bp_full = load_brainpool_price(year)
    bp = bp_full[bp_full.index < f"{year}-12-31"] if year == 2028 else bp_full

    joined = pd.DataFrame({"Unscaled": unscaled, "Scaled": scaled, "Baseline": baseline, "Brainpool": bp}).dropna()

    for label in ["Baseline", "Unscaled", "Scaled"]:
        s = joined[label]
        shortage = s >= 2999.9
        r_all = s.corr(joined["Brainpool"])
        r_excl = s[~shortage].corr(joined.loc[~shortage, "Brainpool"])
        bias_all = (s - joined["Brainpool"]).mean()
        bias_excl = (s[~shortage] - joined.loc[~shortage, "Brainpool"]).mean()
        mae_excl = (s[~shortage] - joined.loc[~shortage, "Brainpool"]).abs().mean()
        print(f"{label:>10}: shortage_hrs={shortage.sum():>3}, all-hours r={r_all:.4f}, excl-shortage r={r_excl:.4f}, "
              f"all-hours bias={bias_all:+.2f}, excl-shortage bias={bias_excl:+.2f}, excl-shortage MAE={mae_excl:.2f}")
