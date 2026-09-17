"""Computes and writes the four ROE-specific agent YAML files for
Germany2027_MarketCoupling_ROEFlex_2024base, replicating Phase 37's exact methodology
(compute_roe_storage_split.py) on real 2024 Eurostat + ENTSO-E data instead of 2023's.

Deliberately isolates ONE variable (the ROE data-year basis) from everything else: same
9-Eurostat-country + Switzerland-ENTSO-E-backfill coverage, same 30% IHA pumped-storage
share, same Switzerland reservoir:run-of-river ratio methodology (recomputed from
Switzerland's own 2024 figures, not reused from 2023), same DE-sourced duration/efficiency/
charge-discharge technology characteristics (these are engineering properties of the
technology, not tied to any particular year), same BNetzA-sourced subsidy Lcoe reference
values (Germany's own, unaffected by the ROE data-year change), same coal/gas/oil markup
bands. Only the underlying capacity and demand NUMBERS change.
"""
import json

ROE_DIR = r"C:\Users\MuideenOA\Desktop\PyTut\Amiris\examples\backtest\RestOfEurope2024"

with open(rf"{ROE_DIR}\restofeurope_aggregate_summary.json") as f:
    agg = json.load(f)
with open(rf"{ROE_DIR}\entsoe_backfill_summary.json") as f:
    backfill = json.load(f)

cap = agg["capacity_MW_by_tech"]
ch_cap = backfill["ch_capacity_MW"]

# --- Conventionals (9-country Eurostat only, same coverage as the 2023 build - CH's
#     nuclear/thermal capacity was never added to this bucket in Phase 37 either, so this
#     replicates that exactly for a clean year-only comparison) ---
COAL_MW = cap["Coal_and_manufactured_gases"]
GAS_MW = cap["Natural_gas"]
OIL_MW = cap["Oil"]
NUCLEAR_MW = cap["Nuclear"]
print(f"Conventionals (2024, 9-country Eurostat): coal={COAL_MW:,.3f} gas={GAS_MW:,.3f} "
      f"oil={OIL_MW:,.3f} nuclear={NUCLEAR_MW:,.3f}")

# --- Renewables: wind onshore/offshore, solar - straight 9-country Eurostat sums ---
WIND_ON_MW = cap["Wind_onshore"]
WIND_OFF_MW = cap["Wind_offshore"]
SOLAR_MW = cap["Solar_PV"]
print(f"Renewables (2024): wind_on={WIND_ON_MW:,.3f} wind_off={WIND_OFF_MW:,.3f} solar={SOLAR_MW:,.3f}")

# --- Hydro split: 9-country Eurostat Hydro_total + CH's real 2024 hydro (all 3 types) ---
CH_PUMPED_MW = ch_cap["Hydro Pumped Storage"]
CH_RESERVOIR_MW = ch_cap["Hydro Water Reservoir"]
CH_ROR_MW = ch_cap["Hydro Run-of-river and poundage"]
CH_TOTAL_HYDRO_MW = CH_PUMPED_MW + CH_RESERVOIR_MW + CH_ROR_MW

TOTAL_HYDRO_MW = cap["Hydro_total"] + CH_TOTAL_HYDRO_MW
print(f"\nHydro: 9-country Eurostat={cap['Hydro_total']:,.3f} + CH 2024 total={CH_TOTAL_HYDRO_MW:,.3f} "
      f"= {TOTAL_HYDRO_MW:,.3f} MW (2023 build: 110,769.344 MW)")

PUMPED_SHARE = 46 / 153  # IHA 2023, real EU-wide figure, unchanged (not a Germany/ROE-specific number)
CONVENTIONAL_SHARE = 1 - PUMPED_SHARE

RESERVOIR_FRACTION = CH_RESERVOIR_MW / (CH_RESERVOIR_MW + CH_ROR_MW)
ROR_FRACTION = CH_ROR_MW / (CH_RESERVOIR_MW + CH_ROR_MW)
print(f"CH 2024 reservoir:RoR ratio = {RESERVOIR_FRACTION:.4f} : {ROR_FRACTION:.4f} "
      f"(2023 build used {5588.0/(5588.0+604.5):.4f} : {604.5/(5588.0+604.5):.4f})")

pumped_mw = TOTAL_HYDRO_MW * PUMPED_SHARE
conventional_mw = TOTAL_HYDRO_MW * CONVENTIONAL_SHARE
reservoir_mw = conventional_mw * RESERVOIR_FRACTION
run_of_river_mw = conventional_mw * ROR_FRACTION
print(f"\nPumped storage: {pumped_mw:,.2f} MW")
print(f"Reservoir hydro: {reservoir_mw:,.2f} MW")
print(f"Run-of-river: {run_of_river_mw:,.2f} MW")
print(f"Check sum: {pumped_mw + reservoir_mw + run_of_river_mw:,.2f} (should equal {TOTAL_HYDRO_MW:,.2f})")

# --- Technology characteristics reused unchanged from DE's own real, calibrated figures
#     (engineering properties, not tied to any particular data-year) ---
DE_PUMPED_DURATION_H = 53607.55 / 8377.60
DE_RESERVOIR_DURATION_H = 171282.22 / 1540.00
DE_PUMPED_CHARGE_MW = 8377.60
DE_PUMPED_DISCHARGE_MW = 7958.72
DE_RESERVOIR_CHARGE_MW = 1540.00
DE_RESERVOIR_DISCHARGE_MW = 1801.80

pumped_energy_mwh = pumped_mw * DE_PUMPED_DURATION_H
reservoir_energy_mwh = reservoir_mw * DE_RESERVOIR_DURATION_H
pumped_net_discharge = pumped_mw * (DE_PUMPED_DISCHARGE_MW / DE_PUMPED_CHARGE_MW)
reservoir_net_discharge = reservoir_mw * (DE_RESERVOIR_DISCHARGE_MW / DE_RESERVOIR_CHARGE_MW)
energy_res_pumped = pumped_energy_mwh / 34
energy_res_reservoir = reservoir_energy_mwh / 1222

print(f"\nPumped: EnergyContentUpperLimitInMWH={pumped_energy_mwh:,.2f} "
      f"InitialEnergyContentInMWH={pumped_energy_mwh/2:,.2f} "
      f"NetDischargingPowerInMW={pumped_net_discharge:,.2f} "
      f"EnergyResolutionInMWH={energy_res_pumped:,.2f}")
print(f"Reservoir: EnergyContentUpperLimitInMWH={reservoir_energy_mwh:,.2f} "
      f"InitialEnergyContentInMWH={reservoir_energy_mwh/2:,.2f} "
      f"NetDischargingPowerInMW={reservoir_net_discharge:,.2f} "
      f"EnergyResolutionInMWH={energy_res_reservoir:,.2f}")

# --- Total demand (for the DemandRestOfEurope.yaml comment only - the actual number is
#     already baked into the timeseries file by build_restofeurope_demand_shape_2024.py) ---
print(f"\nTotal demand: {agg['total_demand_GWh']*1000:,.0f} MWh (2023 build: 1,139,270,364 MWh)")

# ============================================================================
# Write the four agent YAML files
# ============================================================================
OUT_DIR = r"C:\Users\MuideenOA\Desktop\PyTut\Amiris\examples\backtest\Germany2027_MarketCoupling_ROEFlex_2024base\agents"

conventionals_yaml = f"""Variables:
  - &portfolioBuildingOffset 60

Agents:
  # Coal (2024-base rebuild: real Eurostat 'Coal_and_manufactured_gases', {COAL_MW:,.3f} MW,
  # 9 countries - same construction as Phase 37, real 2024 data instead of 2023).
  - Type: PredefinedPlantBuilder
    Id: 9101
    Attributes:
      PortfolioBuildingOffsetInSeconds: *portfolioBuildingOffset
      Prototype:
        FuelType: HARD_COAL
        SpecificCo2EmissionsInTperMWH: 0.338
        OutageFactor: 0.05
        OpexVarInEURperMWH: 2.5
        CyclingCostInEURperMW: 0.0
      Efficiency:
        Minimal: 0.339
        Maximal: 0.492
      BlockSizeInMW: 300.0
      InstalledPowerInMW: {COAL_MW:.3f}

  # Natural Gas (real Eurostat 2024, {GAS_MW:,.3f} MW).
  - Type: PredefinedPlantBuilder
    Id: 9102
    Attributes:
      PortfolioBuildingOffsetInSeconds: *portfolioBuildingOffset
      Prototype:
        FuelType: NATURAL_GAS
        SpecificCo2EmissionsInTperMWH: 0.202
        OutageFactor: 0.05
        OpexVarInEURperMWH: 1.2
        CyclingCostInEURperMW: 0.0
      Efficiency:
        Minimal: 0.516
        Maximal: 0.617
      BlockSizeInMW: 200.0
      InstalledPowerInMW: {GAS_MW:.3f}

  # Oil (real Eurostat 2024, {OIL_MW:,.3f} MW).
  - Type: PredefinedPlantBuilder
    Id: 9103
    Attributes:
      PortfolioBuildingOffsetInSeconds: *portfolioBuildingOffset
      Prototype:
        FuelType: OIL
        SpecificCo2EmissionsInTperMWH: 0.266
        OutageFactor: 0.07
        OpexVarInEURperMWH: 1.2
        CyclingCostInEURperMW: 0.0
      Efficiency:
        Minimal: 0.311
        Maximal: 0.397
      BlockSizeInMW: 100.0
      InstalledPowerInMW: {OIL_MW:.3f}

  # Nuclear (real Eurostat 2024, {NUCLEAR_MW:,.3f} MW - dominated by France's fleet).
  - Type: PredefinedPlantBuilder
    Id: 9104
    Attributes:
      PortfolioBuildingOffsetInSeconds: *portfolioBuildingOffset
      Prototype:
        FuelType: NUCLEAR
        SpecificCo2EmissionsInTperMWH: 0.0
        OutageFactor: 0.10
        OpexVarInEURperMWH: 3.0
        CyclingCostInEURperMW: 0.0
      Efficiency:
        Minimal: 0.33
        Maximal: 0.33
      BlockSizeInMW: 1000.0
      InstalledPowerInMW: {NUCLEAR_MW:.3f}

  - Type: ConventionalTrader # HARD_COAL (ROE)
    Id: 9201
    Attributes:
      minMarkup: -15
      maxMarkup: 5
  - Type: ConventionalTrader # NATURAL_GAS (ROE)
    Id: 9202
    Attributes:
      minMarkup: -10
      maxMarkup: 10
  - Type: ConventionalTrader # OIL (ROE)
    Id: 9203
    Attributes:
      minMarkup: 0
      maxMarkup: 0
  - Type: ConventionalTrader # NUCLEAR (ROE)
    Id: 9204
    Attributes:
      minMarkup: -5
      maxMarkup: 0

  - Type: ConventionalPlantOperator # HARD_COAL (ROE)
    Id: 9301
  - Type: ConventionalPlantOperator # NATURAL_GAS (ROE)
    Id: 9302
  - Type: ConventionalPlantOperator # OIL (ROE)
    Id: 9303
  - Type: ConventionalPlantOperator # NUCLEAR (ROE)
    Id: 9304
"""
with open(rf"{OUT_DIR}\ConventionalsRestOfEurope.yaml", "w", encoding="utf-8") as f:
    f.write(conventionals_yaml)
print(f"\nSaved {OUT_DIR}\\ConventionalsRestOfEurope.yaml")

demand_yaml = f"""Agents:
  # Rest-of-Europe aggregate demand - real annual total ({agg['total_demand_GWh']*1000:,.0f} MWh,
  # Eurostat 2024, 9 countries), shaped using Germany's own real 2027 demand pattern (same
  # documented simplification as Phase 33/37 - Eurostat has no hourly resolution, so the SHAPE
  # is borrowed while the TOTAL is real Rest-of-Europe data).
  - Type: DemandTrader
    Id: 9500
    Attributes:
      Loads:
        - ValueOfLostLoad: 3000.0
          DemandSeries: "./timeseries/load_restofeurope_2027_shapeFromDE.csv"
"""
with open(rf"{OUT_DIR}\DemandRestOfEurope.yaml", "w", encoding="utf-8") as f:
    f.write(demand_yaml)
print(f"Saved {OUT_DIR}\\DemandRestOfEurope.yaml")

renewables_yaml = f"""Agents:
  # Real subsidy realism (unchanged from Phase 37): genuine RenewableTrader + MPVAR
  # SupportPolicy, Germany's own real BNetzA-auction-sourced 2026 support levels reused as
  # the best available real EU reference point (unaffected by the ROE data-year change).
  - Type: RenewableTrader
    Id: 9011
    Attributes:
      ShareOfRevenues: 0.0

  - Type: SystemOperatorTrader
    Id: 9013

  - Type: SupportPolicy
    Id: 9090
    Attributes:
      SetSupportData:
        - PolicySet: ROE_WindOnMpvar
          MPVAR:
            Lcoe: 52.0   # EUR/MWh - Germany's own real BNetzA wind-onshore auction trend
        - PolicySet: ROE_WindOffMpvar
          MPVAR:
            Lcoe: 52.0   # EUR/MWh - reused from onshore, no separate ROE figure researched
        - PolicySet: ROE_SolarMpvar
          MPVAR:
            Lcoe: 49.0   # EUR/MWh - Germany's own real BNetzA solar-openfield auction
        - PolicySet: Undefined
          FIT:
            TsFit: 0.0   # unsubsidised - used by run-of-river hydro below (9404).

  # Wind onshore - {WIND_ON_MW:,.3f} MW (real Eurostat 2024, 9 countries). Yield profile: real
  # 2009 weather (renewables.ninja), capacity-weighted with 2024 capacity weights.
  - Type: VariableRenewableOperator
    Id: 9401
    Attributes:
      PolicySet: ROE_WindOnMpvar
      SupportInstrument: MPVAR
      EnergyCarrier: WindOn
      InstalledPowerInMW: {WIND_ON_MW:.3f}
      OpexVarInEURperMWH: 0.0
      YieldProfile: "./timeseries/wind_onshore_profile_restofeurope_2027.csv"

  # Wind offshore - {WIND_OFF_MW:,.3f} MW (real Eurostat 2024, 5 countries with real offshore capacity).
  - Type: VariableRenewableOperator
    Id: 9402
    Attributes:
      PolicySet: ROE_WindOffMpvar
      SupportInstrument: MPVAR
      EnergyCarrier: WindOff
      InstalledPowerInMW: {WIND_OFF_MW:.3f}
      OpexVarInEURperMWH: 0.0
      YieldProfile: "./timeseries/wind_offshore_profile_restofeurope_2027.csv"

  # Solar PV - {SOLAR_MW:,.3f} MW (real Eurostat 2024, 9 countries; openfield/rooftop not split).
  - Type: VariableRenewableOperator
    Id: 9403
    Attributes:
      PolicySet: ROE_SolarMpvar
      SupportInstrument: MPVAR
      EnergyCarrier: PV
      InstalledPowerInMW: {SOLAR_MW:.3f}
      OpexVarInEURperMWH: 0.0
      YieldProfile: "./timeseries/solar_profile_restofeurope_2027.csv"

  # Run-of-river hydro ONLY - {run_of_river_mw:,.2f} MW. Split out of the real 2024
  # Eurostat+ENTSO-E Hydro_total ({TOTAL_HYDRO_MW:,.1f} MW) using the same real EU-wide
  # pumped-storage share (30%, IHA 2023) plus Switzerland's real 2024 ENTSO-E
  # reservoir:run-of-river ratio ({RESERVOIR_FRACTION:.4f}:{ROR_FRACTION:.4f}) as the only
  # real per-technology reference point available for this aggregate. Still a flat 40%
  # capacity-factor placeholder for the profile itself (Eurostat gives no real weather-driven
  # run-of-river shape) - unchanged from Phase 34/37.
  - Type: VariableRenewableOperator
    Id: 9404
    Attributes:
      PolicySet: Undefined
      SupportInstrument: FIT
      EnergyCarrier: RunOfRiver
      InstalledPowerInMW: {run_of_river_mw:.2f}
      OpexVarInEURperMWH: 0.0
      YieldProfile: "./timeseries/hydro_profile_restofeurope_FLAT.csv"
"""
with open(rf"{OUT_DIR}\RenewablesRestOfEurope.yaml", "w", encoding="utf-8") as f:
    f.write(renewables_yaml)
print(f"Saved {OUT_DIR}\\RenewablesRestOfEurope.yaml")

storage_yaml = f"""Agents:
  # ROE Pumped Storage (2024-base rebuild) - {pumped_mw:,.2f} MW. Split out of the real 2024
  # Eurostat+ENTSO-E Hydro_total ({TOTAL_HYDRO_MW:,.1f} MW) using the real EU-wide
  # pumped-storage share (30%, 46/153 GW, IHA 2023 - unchanged, not a country/year-specific
  # figure). Duration/efficiency/charge-discharge ratios reused from Germany's own real,
  # already-calibrated pumped-hydro figures as technology characteristics (unchanged from
  # Phase 37). See build_roeflex_2024_agents.py for the full calculation.
  - Attributes:
      Assessment:
        Type: MIN_SYSTEM_COST
      Bidding:
        SchedulingHorizonInHours: 24
        Type: ENSURE_DISPATCH
      Device:
        ChargingEfficiency: 0.875
        DischargingEfficiency: 0.852
        EnergyContentUpperLimitInMWH: {pumped_energy_mwh:.2f}
        GrossChargingPowerInMW: {pumped_mw:.2f}
        InitialEnergyContentInMWH: {pumped_energy_mwh/2:.2f}
        NetDischargingPowerInMW: {pumped_net_discharge:.2f}
      StateDiscretisation:
        EnergyResolutionInMWH: {energy_res_pumped:.2f}
        PlanningHorizonInHours: 168
        Type: STATE_OF_CHARGE
    Id: 9601
    Type: GenericFlexibilityTrader

  # ROE Reservoir Hydro (2024-base rebuild) - {reservoir_mw:,.2f} MW. The conventional
  # (non-pumped) 70% of ROE's real 2024 hydro total, split into reservoir vs. run-of-river
  # using Switzerland's real 2024 ENTSO-E capacity-by-type ratio ({RESERVOIR_FRACTION:.4f} :
  # {ROR_FRACTION:.4f}) - the only real per-technology reference point available for this
  # aggregate. Duration/efficiency/charge-discharge ratios reused from Germany's own real
  # reservoir-hydro figures, unchanged from Phase 37.
  - Attributes:
      Assessment:
        Type: MIN_SYSTEM_COST
      Bidding:
        SchedulingHorizonInHours: 168
        Type: ENSURE_DISPATCH
      Device:
        ChargingEfficiency: 0.91
        DischargingEfficiency: 0.91
        EnergyContentUpperLimitInMWH: {reservoir_energy_mwh:.2f}
        GrossChargingPowerInMW: {reservoir_mw:.2f}
        InitialEnergyContentInMWH: {reservoir_energy_mwh/2:.2f}
        NetDischargingPowerInMW: {reservoir_net_discharge:.2f}
      StateDiscretisation:
        EnergyResolutionInMWH: {energy_res_reservoir:.2f}
        PlanningHorizonInHours: 730
        Type: STATE_OF_CHARGE
    Id: 9602
    Type: GenericFlexibilityTrader
"""
with open(rf"{OUT_DIR}\StorageRestOfEurope.yaml", "w", encoding="utf-8") as f:
    f.write(storage_yaml)
print(f"Saved {OUT_DIR}\\StorageRestOfEurope.yaml")

print("\nAll four 2024-base ROE agent YAML files written.")
