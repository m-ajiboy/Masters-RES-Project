import pandas as pd

ROOT = r"C:\Users\MuideenOA\Desktop\PyTut\Amiris\examples\backtest"

def load_agent(path, agent_id):
    df = pd.read_csv(path, sep=";")
    df["ts"] = pd.to_datetime(df["TimeStep"])
    return df[df["AgentId"] == agent_id].set_index("ts")

for label, path in [
    ("Headline", rf"{ROOT}\Germany2027_MarketCoupling_ROEFlex\result_Germany2027_MarketCoupling_ROEFlex\GenericFlexibilityTrader.csv"),
    ("CrossZonePrice", rf"{ROOT}\Germany2027_MarketCoupling_ROEFlex_CrossZonePrice\result_Germany2027_MarketCoupling_ROEFlex_CrossZonePrice\GenericFlexibilityTrader.csv"),
]:
    print(f"\n=== {label} ===")
    for agent_id in [9601, 9602]:
        d = load_agent(path, agent_id)
        window = d.loc["2027-12-17 04:00:00":"2027-12-17 10:00:00"]
        print(f"\nAgent {agent_id}:")
        cols = ["AwardedDischargeEnergyInMWH", "OfferedDischargePriceInEURperMWH", "StoredEnergyInMWH", "ElectricityPricePredictionInEURperMWH"]
        print(window[cols].to_string())
