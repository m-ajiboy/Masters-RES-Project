import pandas as pd
path = r"C:\Users\MuideenOA\Desktop\PyTut\Amiris\examples\backtest\Germany2029_MarketCoupling_ROEFlex\result_Germany2029_MarketCoupling_ROEFlex\DayAheadMarketMultiZone.csv"
df = pd.read_csv(path, sep=";")
df["ts"] = pd.to_datetime(df["TimeStep"])
de = df[df["AgentId"] == 1]
shortage = de[de["ElectricityPriceInEURperMWH"] >= 2999.9]
print(f"{len(shortage)} shortage hours in 2029")
for ts in shortage["ts"]:
    print(ts)
