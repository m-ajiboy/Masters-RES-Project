import pandas as pd

ROOT = r"C:\Users\MuideenOA\Desktop\PyTut\Amiris\examples\backtest"


def load_de(path):
    df = pd.read_csv(path, sep=";")
    df["ts"] = pd.to_datetime(df["TimeStep"])
    return df[df["AgentId"] == 1].set_index("ts")["ElectricityPriceInEURperMWH"]


headline = load_de(rf"{ROOT}\Germany2027_MarketCoupling_ROEFlex\result_Germany2027_MarketCoupling_ROEFlex\DayAheadMarketMultiZone.csv")
xzone = load_de(rf"{ROOT}\Germany2027_MarketCoupling_ROEFlex_CrossZonePrice\result_Germany2027_MarketCoupling_ROEFlex_CrossZonePrice\DayAheadMarketMultiZone.csv")

headline_shortage = set(headline[headline >= 2999.9].index)
xzone_shortage = set(xzone[xzone >= 2999.9].index)

print("Headline shortage hours:", sorted(headline_shortage))
print()
print("CrossZonePrice (final patch) shortage hours:", sorted(xzone_shortage))
print()
print("NEW shortage hours (in xzone, not in headline):", sorted(xzone_shortage - headline_shortage))
print("RESOLVED shortage hours (in headline, not in xzone):", sorted(headline_shortage - xzone_shortage))
