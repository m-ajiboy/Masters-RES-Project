import pandas as pd
path = r"C:\Users\MuideenOA\Desktop\PyTut\Amiris\examples\backtest\Germany2027_MarketCoupling_ROEFlex\result_Germany2027_MarketCoupling_ROEFlex\DayAheadMarketMultiZone.csv"
df = pd.read_csv(path, sep=";")
df["ts"] = pd.to_datetime(df["TimeStep"])
de = df[df["AgentId"] == 1].set_index("ts")
roe = df[df["AgentId"] == 9001].set_index("ts")

# A clean IMPORT hour: DE price notably higher than ROE price, decent import volume, no shortage
imp_candidates = de[(de["AwardedNetEnergyFromImportInMWH"] > 5000) & (de["ElectricityPriceInEURperMWH"] < 500)]
imp_candidates = imp_candidates.assign(roe_price=roe.loc[imp_candidates.index, "ElectricityPriceInEURperMWH"])
imp_candidates = imp_candidates.assign(gap=imp_candidates["ElectricityPriceInEURperMWH"] - imp_candidates["roe_price"])
imp_hour = imp_candidates.sort_values("gap", ascending=False).iloc[0]
print("=== IMPORT HOUR (DE buying from ROE) ===")
print(imp_hour[["ElectricityPriceInEURperMWH", "AwardedNetEnergyFromImportInMWH", "AwardedNetEnergyToExportInMWH", "roe_price"]])
print("Timestamp:", imp_hour.name)

# A clean EXPORT hour: DE price notably lower than ROE price, decent export volume
exp_candidates = de[(de["AwardedNetEnergyToExportInMWH"] > 5000)]
exp_candidates = exp_candidates.assign(roe_price=roe.loc[exp_candidates.index, "ElectricityPriceInEURperMWH"])
exp_candidates = exp_candidates.assign(gap=exp_candidates["roe_price"] - exp_candidates["ElectricityPriceInEURperMWH"])
exp_hour = exp_candidates.sort_values("gap", ascending=False).iloc[0]
print("\n=== EXPORT HOUR (DE selling to ROE) ===")
print(exp_hour[["ElectricityPriceInEURperMWH", "AwardedNetEnergyFromImportInMWH", "AwardedNetEnergyToExportInMWH", "roe_price"]])
print("Timestamp:", exp_hour.name)

print("\nTotal export hours in year:", (de["AwardedNetEnergyToExportInMWH"] > 0).sum())
print("Total import hours in year:", (de["AwardedNetEnergyFromImportInMWH"] > 0).sum())
