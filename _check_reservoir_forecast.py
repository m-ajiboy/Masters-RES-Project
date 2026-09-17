"""Checks what ROE Reservoir Hydro's OWN price forecast said for the 3 unresolved shortage
hours (2027-12-17 06:00-08:00), using the already-existing Phase 37 baseline result - no new
simulation needed. If the forecaster simply failed to predict the spike, that fully explains
why the agent chose not to hold back reserve for it."""
import pandas as pd

ROOT = r"C:\Users\MuideenOA\Desktop\PyTut\Amiris\examples\backtest\Germany2027_MarketCoupling_ROEFlex\result_Germany2027_MarketCoupling_ROEFlex"

storage = pd.read_csv(rf"{ROOT}\GenericFlexibilityTrader.csv", sep=";")
storage["ts"] = pd.to_datetime(storage["TimeStep"])

dam = pd.read_csv(rf"{ROOT}\DayAheadMarketMultiZone.csv", sep=";")
dam["ts"] = pd.to_datetime(dam["TimeStep"])
de_actual = dam[dam["AgentId"] == 1].set_index("ts")["ElectricityPriceInEURperMWH"]
roe_actual = dam[dam["AgentId"] == 9001].set_index("ts")["ElectricityPriceInEURperMWH"]

target_hours = [pd.Timestamp(f"2027-12-17 {h:02d}:00:00") for h in range(0, 24)]

reservoir = storage[storage["AgentId"] == 9602].set_index("ts")
pumped = storage[storage["AgentId"] == 9601].set_index("ts")

print("Reservoir Hydro's OWN forecasted price vs. the REAL actual ROE price, all of 2027-12-17:")
print(f"{'Hour':<21} {'Forecast':>10} {'Actual ROE':>12} {'Actual DE':>11} {'Stored MWh':>12} {'Discharge':>11}")
for ts in target_hours:
    if ts in reservoir.index:
        row = reservoir.loc[ts]
        actual_roe = roe_actual.get(ts, float("nan"))
        actual_de = de_actual.get(ts, float("nan"))
        print(f"{str(ts):<21} {row['ElectricityPricePredictionInEURperMWH']:>10.2f} "
              f"{actual_roe:>12.2f} {actual_de:>11.2f} {row['StoredEnergyInMWH']:>12.1f} "
              f"{row['AwardedDischargeEnergyInMWH']:>11.1f}")

print()
print("Same for Pumped Storage:")
print(f"{'Hour':<21} {'Forecast':>10} {'Actual ROE':>12} {'Actual DE':>11} {'Stored MWh':>12} {'Discharge':>11}")
for ts in target_hours:
    if ts in pumped.index:
        row = pumped.loc[ts]
        actual_roe = roe_actual.get(ts, float("nan"))
        actual_de = de_actual.get(ts, float("nan"))
        print(f"{str(ts):<21} {row['ElectricityPricePredictionInEURperMWH']:>10.2f} "
              f"{actual_roe:>12.2f} {actual_de:>11.2f} {row['StoredEnergyInMWH']:>12.1f} "
              f"{row['AwardedDischargeEnergyInMWH']:>11.1f}")

# Also check the preceding week - was there a real opportunity to hold back reserve earlier?
print()
print("Reservoir Hydro stored energy trajectory, 2027-12-10 through 2027-12-17 (daily at 06:00):")
for day in range(10, 18):
    ts = pd.Timestamp(f"2027-12-{day:02d} 06:00:00")
    if ts in reservoir.index:
        print(f"  {ts}: stored={reservoir.loc[ts, 'StoredEnergyInMWH']:,.1f} MWh, "
              f"forecast={reservoir.loc[ts, 'ElectricityPricePredictionInEURperMWH']:.2f}")
