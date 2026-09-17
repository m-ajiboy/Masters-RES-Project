"""Writes the four ROE-specific agent YAML files for the 2028/2029 Growth scenarios, using
the real ERAA-growth-rate-projected capacity numbers. Storage split methodology (30% IHA
pumped-storage share + Switzerland's real reservoir:run-of-river ratio) is UNCHANGED from
Phase 37/44 - deliberately isolating capacity/demand/transmission GROWTH as the only new
variable, not re-deriving the split methodology itself. CH's own 2024 ratio is reused as a
technology-characteristic constant (same treatment as storage duration/efficiency)."""
import json

with open(r"C:\Users\MuideenOA\maven-tools\eraa_data\roe_growth_projection.json") as f:
    growth = json.load(f)
with open(r"C:\Users\MuideenOA\Desktop\PyTut\Amiris\examples\backtest\RestOfEurope2024\entsoe_backfill_summary.json") as f:
    ch = json.load(f)["ch_capacity_MW"]

CH_PUMPED_MW = ch["Hydro Pumped Storage"]
CH_RESERVOIR_MW = ch["Hydro Water Reservoir"]
CH_ROR_MW = ch["Hydro Run-of-river and poundage"]
RESERVOIR_FRACTION = CH_RESERVOIR_MW / (CH_RESERVOIR_MW + CH_ROR_MW)
ROR_FRACTION = CH_ROR_MW / (CH_RESERVOIR_MW + CH_ROR_MW)
PUMPED_SHARE = 46 / 153
CONVENTIONAL_SHARE = 1 - PUMPED_SHARE

DE_PUMPED_DURATION_H = 53607.55 / 8377.60
DE_RESERVOIR_DURATION_H = 171282.22 / 1540.00
DE_PUMPED_CHARGE_MW = 8377.60
DE_PUMPED_DISCHARGE_MW = 7958.72
DE_RESERVOIR_CHARGE_MW = 1540.00
DE_RESERVOIR_DISCHARGE_MW = 1801.80


def build_year(year, out_scenario_folder):
    cap = growth[f"capacity_MW_{year}"]
    demand_twh = growth[f"demand_TWH_{year}"]
    OUT_DIR = rf"C:\Users\MuideenOA\Desktop\PyTut\Amiris\examples\backtest\{out_scenario_folder}\agents"

    total_hydro = cap["Hydro_total"]
    pumped_mw = total_hydro * PUMPED_SHARE
    conventional_mw = total_hydro * CONVENTIONAL_SHARE
    reservoir_mw = conventional_mw * RESERVOIR_FRACTION
    run_of_river_mw = conventional_mw * ROR_FRACTION

    pumped_energy_mwh = pumped_mw * DE_PUMPED_DURATION_H
    reservoir_energy_mwh = reservoir_mw * DE_RESERVOIR_DURATION_H
    pumped_net_discharge = pumped_mw * (DE_PUMPED_DISCHARGE_MW / DE_PUMPED_CHARGE_MW)
    reservoir_net_discharge = reservoir_mw * (DE_RESERVOIR_DISCHARGE_MW / DE_RESERVOIR_CHARGE_MW)
    energy_res_pumped = pumped_energy_mwh / 34
    energy_res_reservoir = reservoir_energy_mwh / 1222

    print(f"\n{year}: Hydro_total={total_hydro:,.0f} MW -> pumped={pumped_mw:,.0f}, "
          f"reservoir={reservoir_mw:,.0f}, run_of_river={run_of_river_mw:,.0f} MW")

    conventionals_yaml = f"""Variables:
  - &portfolioBuildingOffset 60

Agents:
  # Coal (real ERAA-growth-projected {year}, {cap['Coal_and_manufactured_gases']:,.3f} MW, 9 countries).
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
      InstalledPowerInMW: {cap['Coal_and_manufactured_gases']:.3f}

  # Natural Gas (real ERAA-growth-projected {year}, {cap['Natural_gas']:,.3f} MW).
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
      InstalledPowerInMW: {cap['Natural_gas']:.3f}

  # Oil (real ERAA-growth-projected {year}, {cap['Oil']:,.3f} MW).
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
      InstalledPowerInMW: {cap['Oil']:.3f}

  # Nuclear (real ERAA-growth-projected {year}, {cap['Nuclear']:,.3f} MW).
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
      InstalledPowerInMW: {cap['Nuclear']:.3f}

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

    demand_yaml = f"""Agents:
  # Rest-of-Europe aggregate demand - real ERAA-growth-rate-projected {year} total
  # ({demand_twh*1000:,.0f} MWh), applied to the real 2024 Eurostat baseline (see
  # build_roeflex_growth_timeseries.py). Shape still borrowed from Germany's own real {year}
  # demand pattern.
  - Type: DemandTrader
    Id: 9500
    Attributes:
      Loads:
        - ValueOfLostLoad: 3000.0
          DemandSeries: "./timeseries/load_restofeurope_{year}_shapeFromDE.csv"
"""
    with open(rf"{OUT_DIR}\DemandRestOfEurope.yaml", "w", encoding="utf-8") as f:
        f.write(demand_yaml)

    renewables_yaml = f"""Agents:
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
            Lcoe: 52.0
        - PolicySet: ROE_WindOffMpvar
          MPVAR:
            Lcoe: 52.0
        - PolicySet: ROE_SolarMpvar
          MPVAR:
            Lcoe: 49.0
        - PolicySet: Undefined
          FIT:
            TsFit: 0.0

  # Wind onshore - real ERAA-growth-projected {year}, {cap['Wind_onshore']:,.3f} MW.
  - Type: VariableRenewableOperator
    Id: 9401
    Attributes:
      PolicySet: ROE_WindOnMpvar
      SupportInstrument: MPVAR
      EnergyCarrier: WindOn
      InstalledPowerInMW: {cap['Wind_onshore']:.3f}
      OpexVarInEURperMWH: 0.0
      YieldProfile: "./timeseries/wind_onshore_profile_restofeurope_{year}.csv"

  # Wind offshore - real ERAA-growth-projected {year}, {cap['Wind_offshore']:,.3f} MW.
  - Type: VariableRenewableOperator
    Id: 9402
    Attributes:
      PolicySet: ROE_WindOffMpvar
      SupportInstrument: MPVAR
      EnergyCarrier: WindOff
      InstalledPowerInMW: {cap['Wind_offshore']:.3f}
      OpexVarInEURperMWH: 0.0
      YieldProfile: "./timeseries/wind_offshore_profile_restofeurope_{year}.csv"

  # Solar PV - real ERAA-growth-projected {year}, {cap['Solar_PV']:,.3f} MW.
  - Type: VariableRenewableOperator
    Id: 9403
    Attributes:
      PolicySet: ROE_SolarMpvar
      SupportInstrument: MPVAR
      EnergyCarrier: PV
      InstalledPowerInMW: {cap['Solar_PV']:.3f}
      OpexVarInEURperMWH: 0.0
      YieldProfile: "./timeseries/solar_profile_restofeurope_{year}.csv"

  # Run-of-river hydro - {run_of_river_mw:,.2f} MW, split from the real ERAA-growth-projected
  # {year} Hydro_total ({total_hydro:,.1f} MW) using the same 30% IHA pumped-storage share and
  # Switzerland's real reservoir:run-of-river ratio as Phase 37/44 (technology-characteristic
  # constants, not re-derived for this growth investigation).
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

    storage_yaml = f"""Agents:
  # ROE Pumped Storage (real ERAA-growth-projected {year}) - {pumped_mw:,.2f} MW.
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

  # ROE Reservoir Hydro (real ERAA-growth-projected {year}) - {reservoir_mw:,.2f} MW.
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

    print(f"Saved all 4 ROE agent YAML files for {year} -> {OUT_DIR}")


build_year(2028, "Germany2028_MarketCoupling_ROEFlex_Growth")
build_year(2029, "Germany2029_MarketCoupling_ROEFlex_Growth")
