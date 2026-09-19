import pandas as pd
from brainpool_multiyear_data import load_brainpool_price

ROOT = r"C:\Users\MuideenOA\Desktop\PyTut\Amiris\examples\backtest"


def load_de(path):
    df = pd.read_csv(path, sep=";")
    df["ts"] = pd.to_datetime(df["TimeStep"])
    return df[df["AgentId"] == 1].set_index("ts")["ElectricityPriceInEURperMWH"]


bp = load_brainpool_price(2027)
headline = load_de(rf"{ROOT}\Germany2027_MarketCoupling_ROEFlex\result_Germany2027_MarketCoupling_ROEFlex\DayAheadMarketMultiZone.csv")
demand2025 = load_de(rf"{ROOT}\Germany2027_MarketCoupling_ROEFlex_Demand2025\result_Germany2027_MarketCoupling_ROEFlex_Demand2025\DayAheadMarketMultiZone.csv")

print(f"{'Build':28s} {'mean':>8s} {'shortage':>9s} {'excl_r':>8s} {'excl_bias':>10s} {'excl_mae':>9s} {'neg%':>6s}")
for label, s in [("Headline (2016-shape)", headline), ("Demand2025 (holiday-fixed)", demand2025)]:
    joined = pd.DataFrame({"AMIRIS": s, "Brainpool": bp}).dropna()
    shortage = joined["AMIRIS"] >= 2999.9
    excl = joined[~shortage]
    r_excl = excl["AMIRIS"].corr(excl["Brainpool"])
    bias_excl = (excl["AMIRIS"] - excl["Brainpool"]).mean()
    mae_excl = (excl["AMIRIS"] - excl["Brainpool"]).abs().mean()
    neg_pct = (joined["AMIRIS"] < 0).mean() * 100
    print(f"{label:28s} {s.mean():8.2f} {shortage.sum():9d} {r_excl:8.4f} {bias_excl:+10.2f} {mae_excl:9.2f} {neg_pct:6.1f}")

print(f"{'Brainpool reference':28s} {bp.mean():8.2f} {0:9d}")
