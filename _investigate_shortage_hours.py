"""Investigates the real mechanism behind each of the 7 physical shortage hours in the
Phase 37 baseline (Germany2027_MarketCoupling_ROEFlex): DE's own demand and domestic supply
margin, import usage relative to the transmission ceiling, and ROE storage state - to find
the REAL cause before proposing any fix (not just changing how the price is displayed)."""
import pandas as pd

ROOT = r"C:\Users\MuideenOA\Desktop\PyTut\Amiris\examples\backtest\Germany2027_MarketCoupling_ROEFlex\result_Germany2027_MarketCoupling_ROEFlex"

dam = pd.read_csv(rf"{ROOT}\DayAheadMarketMultiZone.csv", sep=";")
dam["ts"] = pd.to_datetime(dam["TimeStep"])
de = dam[dam["AgentId"] == 1].set_index("ts")
roe = dam[dam["AgentId"] == 9001].set_index("ts")

shortage_hours = de[de["ElectricityPriceInEURperMWH"] >= 2999.9].index
print(f"{len(shortage_hours)} real shortage hours in the Phase 37 baseline:\n")

demand = pd.read_csv(rf"{ROOT}\DemandTrader.csv", sep=";")
demand["ts"] = pd.to_datetime(demand["TimeStep"])

storage = pd.read_csv(rf"{ROOT}\GenericFlexibilityTrader.csv", sep=";")
storage["ts"] = pd.to_datetime(storage["TimeStep"])

TRANSMISSION_CEILING = 22012.0  # ROE->DE, Phase 35/36 real-flow-derived

for ts in shortage_hours:
    de_row = de.loc[ts]
    roe_row = roe.loc[ts]
    imports = de_row.get("AwardedNetEnergyFromImportInMWH", 0)
    print("=" * 80)
    print(f"{ts}")
    print(f"  DE price: {de_row['ElectricityPriceInEURperMWH']:.2f} | ROE price: {roe_row['ElectricityPriceInEURperMWH']:.2f}")
    print(f"  DE pre-coupling price: {de_row['PreCouplingElectricityPriceInEURperMWH']:.2f} | "
          f"pre-coupling awarded: {de_row['PreCouplingTotalAwardedPowerInMW']:,.1f} MW | "
          f"post-coupling awarded: {de_row['AwardedEnergyInMWH']:,.1f} MW")
    print(f"  DE imports from ROE: {imports:,.1f} MWh "
          f"({'AT CEILING' if imports >= TRANSMISSION_CEILING * 0.995 else 'below ceiling'}, "
          f"ceiling={TRANSMISSION_CEILING:,.0f})")

    de_demand_rows = demand[(demand["ts"] == ts)]
    if not de_demand_rows.empty:
        req = de_demand_rows["RequestedEnergyInMWH"].sum() if "RequestedEnergyInMWH" in de_demand_rows.columns else None
        awd = de_demand_rows["AwardedEnergyInMWH"].sum() if "AwardedEnergyInMWH" in de_demand_rows.columns else None
        print(f"  DE demand requested: {req}, awarded: {awd}"
              f"{'  <== UNSERVED DEMAND' if req is not None and awd is not None and req - awd > 0.01 else ''}")

    roe_storage = storage[(storage["ts"] == ts) & (storage["AgentId"].isin([9601, 9602]))]
    for _, srow in roe_storage.iterrows():
        label = "ROE Pumped Storage" if srow["AgentId"] == 9601 else "ROE Reservoir Hydro"
        print(f"  {label}: discharge={srow.get('AwardedDischargeEnergyInMWH', 'n/a')}, "
              f"charge={srow.get('AwardedChargeEnergyInMWH', 'n/a')}, "
              f"stored={srow.get('StoredEnergyInMWH', 'n/a')}")
    print()
