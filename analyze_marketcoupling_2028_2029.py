"""Analyzes the 2028 and 2029 market-coupling+ROE-flex extensions (Phase 38) against each
year's own pre-coupling baseline and Brainpool's real price for that year."""
import pandas as pd
from brainpool_multiyear_data import load_brainpool_price

ROOT = r"C:\Users\MuideenOA\Desktop\PyTut\Amiris\examples\backtest"

CONFIGS = {
    2028: {
        "coupled": rf"{ROOT}\Germany2028_MarketCoupling_ROEFlex\result_Germany2028_MarketCoupling_ROEFlex\DayAheadMarketMultiZone.csv",
        "baseline": rf"{ROOT}\Germany2028\result_Germany2028\DayAheadMarketSingleZone.csv",
        "storage": rf"{ROOT}\Germany2028_MarketCoupling_ROEFlex\result_Germany2028_MarketCoupling_ROEFlex\GenericFlexibilityTrader.csv",
    },
    2029: {
        "coupled": rf"{ROOT}\Germany2029_MarketCoupling_ROEFlex\result_Germany2029_MarketCoupling_ROEFlex\DayAheadMarketMultiZone.csv",
        "baseline": rf"{ROOT}\Germany2029_Feb29DropFix\result_Germany2029_Feb29DropFix\DayAheadMarketSingleZone.csv",
        "storage": rf"{ROOT}\Germany2029_MarketCoupling_ROEFlex\result_Germany2029_MarketCoupling_ROEFlex\GenericFlexibilityTrader.csv",
    },
}


def load_de_multizone(path):
    df = pd.read_csv(path, sep=";")
    df["ts"] = pd.to_datetime(df["TimeStep"])
    return df[df["AgentId"] == 1].set_index("ts")


def load_singlezone(path):
    df = pd.read_csv(path, sep=";")
    df["ts"] = pd.to_datetime(df["TimeStep"])
    return df.set_index("ts")["ElectricityPriceInEURperMWH"]


for year, cfg in CONFIGS.items():
    print("\n" + "=" * 70)
    print(f"YEAR {year}")
    print("=" * 70)
    coupled = load_de_multizone(cfg["coupled"])
    baseline = load_singlezone(cfg["baseline"])
    bp_full = load_brainpool_price(year)
    bp = bp_full[bp_full.index < f"{year}-12-31"] if year == 2028 else bp_full

    joined = pd.DataFrame({
        "Coupled": coupled["ElectricityPriceInEURperMWH"],
        "Baseline": baseline,
        "Brainpool": bp,
    }).dropna()

    print(f"Hours compared: {len(joined)}")
    for label in ["Baseline", "Coupled", "Brainpool"]:
        s = joined[label]
        print(f"  {label:>10}: mean={s.mean():.2f}, min={s.min():.2f}, max={s.max():.2f}, "
              f"neg hours={len(s[s<0])} ({100*len(s[s<0])/len(s):.1f}%)")

    for label in ["Baseline", "Coupled"]:
        s = joined[label]
        shortage = s >= 2999.9
        r_all = s.corr(joined["Brainpool"])
        r_excl = s[~shortage].corr(joined.loc[~shortage, "Brainpool"])
        bias = (s - joined["Brainpool"]).mean()
        mae = (s - joined["Brainpool"]).abs().mean()
        print(f"  {label:>10}: all-hours r={r_all:.4f}, excl-shortage r={r_excl:.4f}, "
              f"bias={bias:+.2f}, MAE={mae:.2f}, shortage hours={shortage.sum()}")

    # storage dispatch check
    storage = pd.read_csv(cfg["storage"], sep=";")
    storage["ts"] = pd.to_datetime(storage["TimeStep"])
    for agent_id, label in [(9601, "ROE Pumped Storage"), (9602, "ROE Reservoir Hydro")]:
        a = storage[storage["AgentId"] == agent_id]
        charge = a["AwardedChargeEnergyInMWH"]
        discharge = a["AwardedDischargeEnergyInMWH"]
        print(f"  {label}: charge hrs={len(charge[charge>0])} ({charge.sum():,.0f} MWh), "
              f"discharge hrs={len(discharge[discharge>0])} ({discharge.sum():,.0f} MWh)")
