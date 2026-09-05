"""Builds all agent YAML files for the Germany2027 AMIRIS scenario: Conventionals.yaml,
RenewablesAndPolicy.yaml, Storage.yaml, Demand.yaml, MarketsAndForecast.yaml.

Every value below is either (a) a real Brainpool 2027 figure, (b) a real researched figure
(EEG auction rates, MaStR battery duration), or (c) an AMIRIS-own value used as a documented
gap-fill where neither Brainpool nor external research supplied a number. Each case is labelled
inline. See build_2027_timeseries.py for the corresponding timeseries construction and its
own documented assumptions (fuel price conversions, outage/must-run reuse, profile blending).

KEY DESIGN DECISIONS made while building this file (beyond what was explicitly directed):

1. Solar kept as TWO operator agents, not one blended agent. Grid Feed-in (utility-scale)
   uses AMIRIS's MPVAR mechanism; Prosuming (rooftop) uses FIT. AMIRIS assigns one
   SupportInstrument per operator agent, so the two real subsidy mechanisms cannot be merged
   into a single agent even though their capacity/generation totals were earlier agreed to be
   summed for bookkeeping purposes. This mirrors exactly how AMIRIS's own Germany2019 scenario
   handles multiple solar sub-fleets under one shared trader.

2. Natural gas modelled as ONE combined block (200 MW, AMIRIS's own CCGT efficiency/markup
   band used as representative), not split into CCGT/OCGT as AMIRIS's own examples do, since
   Brainpool supplies only one combined gas capacity figure with no split. Documented
   simplification.

3. Oil and "Other Fossil" merged into one AMIRIS Oil-type block (9.79 GW combined), consistent
   with AMIRIS's own scenario comment that its Oil category already covers "oil, other fossil
   fuels, mixed fossil fuels."

4. Nuclear omitted entirely (0 GW in Brainpool's 2027 figures - consistent with the completed
   2023 phase-out).

5. Brainpool's separate "Reservoir Hydro" capacity (1.54 GW) is modelled as a THIRD storage-like
   GenericFlexibilityTrader agent, not as a weather-driven renewable with a fixed profile.
   Reservoir hydro is operator-dispatched (water release is a choice), unlike run-of-river
   (flow-determined) - this is the physically correct AMIRIS-native modelling choice. Its
   duration (111.2 hours) is borrowed from the two long-duration units originally excluded from
   the battery-duration calculation earlier in this project - which, on reflection, are almost
   certainly AMIRIS's own representation of exactly this kind of seasonal reservoir hydro.

6. "Other Renewables" (8.25 GW) mapped entirely onto AMIRIS's Biogas/biomass agent type,
   since biomass is the dominant real-world component of Germany's "sonstige Erneuerbare"
   statistical bucket. AMIRIS's own Germany2019 example leaves this technology unsupported
   (NoSupportTrader); this build instead applies a real EEG biomass tender clearing rate
   (~197 EUR/MWh, near the published Hoechstwert ceiling, April 2026 BNetzA tender round) via
   MPVAR, since that is a more accurate reflection of reality than AMIRIS's own placeholder -
   flagged here as a deliberate, documented departure from the AMIRIS example convention.

7. Wind offshore's LCOE reference (used for its MPVAR subsidy) has NO real 2027 figure available
   anywhere: BNetzA's 2025 central-site offshore auctions received zero bids and subsequent
   rounds were postponed to 2027 itself. This is a genuine, unresolved gap. AMIRIS's own
   Germany2019 offshore clusters' capacity-weighted LCOE (~187 EUR/MWh) is used as the least-bad
   available placeholder, clearly flagged as such rather than presented as researched fact.
"""
from pathlib import Path

ROOT = Path(__file__).parent
AGENTS_DIR = ROOT / "examples" / "backtest" / "Germany2027" / "agents"


def w(path, text):
    path.write_text(text.strip() + "\n", encoding="utf-8")
    print(f"  wrote {path.name}")


def build_conventionals():
    text = """
Variables:
  - &portfolioBuildingOffset 60

Agents:
  # Lignite - 13.927 GW (Brainpool 2027). Efficiency/opex/markup: AMIRIS own (Germany2019),
  # since Brainpool supplies no plant-level technical parameters. CO2 factor: Brainpool
  # emission_factor sheet (0.407 t/MWh, vs. AMIRIS's own 0.364 - Brainpool's value used).
  - Type: PredefinedPlantBuilder
    Id: 2001
    Attributes:
      PortfolioBuildingOffsetInSeconds: *portfolioBuildingOffset
      Prototype:
        FuelType: LIGNITE
        SpecificCo2EmissionsInTperMWH: 0.407
        OutageFactor: "./timeseries/lignite_outage.csv"
        MustRunFactor: "./timeseries/lignite_must_run.csv"
        OpexVarInEURperMWH: 2.0
        CyclingCostInEURperMW: 0.0
      Efficiency:
        Minimal: 0.3108
        Maximal: 0.45
      BlockSizeInMW: 500.0
      InstalledPowerInMW: 13927.0

  # Hard Coal - 5.504 GW (Brainpool 2027). CO2 factor: Brainpool (0.338 t/MWh).
  - Type: PredefinedPlantBuilder
    Id: 2002
    Attributes:
      PortfolioBuildingOffsetInSeconds: *portfolioBuildingOffset
      Prototype:
        FuelType: HARD_COAL
        SpecificCo2EmissionsInTperMWH: 0.338
        OutageFactor: "./timeseries/hard_coal_outage.csv"
        MustRunFactor: "./timeseries/hard_coal_must_run.csv"
        OpexVarInEURperMWH: 2.5
        CyclingCostInEURperMW: 0.0
      Efficiency:
        Minimal: 0.339
        Maximal: 0.492
      BlockSizeInMW: 300.0
      InstalledPowerInMW: 5504.0

  # Natural Gas - 36.237 GW (Brainpool 2027), modelled as ONE combined block (CCGT+OCGT
  # merged - Brainpool gives no split; AMIRIS's own CCGT efficiency/markup band used as the
  # representative choice). CO2 factor: Brainpool (0.202 t/MWh).
  - Type: PredefinedPlantBuilder
    Id: 2003
    Attributes:
      PortfolioBuildingOffsetInSeconds: *portfolioBuildingOffset
      Prototype:
        FuelType: NATURAL_GAS
        SpecificCo2EmissionsInTperMWH: 0.202
        OutageFactor: "./timeseries/natural_gas_outage.csv"
        MustRunFactor: "./timeseries/natural_gas_must_run.csv"
        OpexVarInEURperMWH: 1.2
        CyclingCostInEURperMW: 0.0
      Efficiency:
        Minimal: 0.516
        Maximal: 0.617
      BlockSizeInMW: 200.0
      InstalledPowerInMW: 36237.0

  # Oil + Other Fossil combined - 1.54 + 8.25 = 9.79 GW (Brainpool 2027). Merged into AMIRIS's
  # Oil category per its own documented convention ("oil, other fossil fuels, mixed fossil
  # fuels"). CO2 factor: Brainpool's Oil factor (0.266 t/MWh) used as the blended proxy, since
  # Brainpool gives no separate factor for "Other Fossil".
  - Type: PredefinedPlantBuilder
    Id: 2005
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
      InstalledPowerInMW: 9790.0

  - Type: ConventionalTrader # LIGNITE
    Id: 1001
    Attributes:
      minMarkup: -60
      maxMarkup: 0
  - Type: ConventionalTrader # HARD_COAL
    Id: 1002
    Attributes:
      minMarkup: -15
      maxMarkup: 5
  - Type: ConventionalTrader # NATURAL_GAS (combined)
    Id: 1003
    Attributes:
      minMarkup: -10
      maxMarkup: 10
  - Type: ConventionalTrader # OIL (+ Other Fossil)
    Id: 1005
    Attributes:
      minMarkup: 0
      maxMarkup: 0

  - Type: ConventionalPlantOperator # LIGNITE
    Id: 501
  - Type: ConventionalPlantOperator # HARD_COAL
    Id: 502
  - Type: ConventionalPlantOperator # NATURAL_GAS (combined)
    Id: 503
  - Type: ConventionalPlantOperator # OIL (+ Other Fossil)
    Id: 505
"""
    w(AGENTS_DIR / "Conventionals.yaml", text)


def build_renewables_and_policy():
    text = """
Agents:
  - Type: RenewableTrader
    Id: 11
    Attributes:
      ShareOfRevenues: 0.0

  - Type: SystemOperatorTrader
    Id: 13

  # Reference values below: EEG-derived where a real 2026 auction/rate exists (Solar
  # Openfield, Wind Onshore, Biomass); AMIRIS's own placeholder LCOE where no real figure is
  # obtainable yet (Wind Offshore - BNetzA's 2025 offshore auctions received zero bids and the
  # next round is postponed to 2027 itself, so no genuine 2027 reference exists anywhere).
  - Type: SupportPolicy
    Id: 90
    Attributes:
      SetSupportData:
        - PolicySet: SolarRooftopFit
          FIT:
            TsFit: 75.0   # EUR/MWh - EEG Section 49 degression schedule extrapolated to 2027.
                          # FLAG: draft EEG-Novelle 2026 (cabinet-approved 29 Jul 2026, not yet
                          # law) proposes ending permanent FIT support for new PV <25kW from
                          # 2027 - this figure assumes current law continues unchanged.
        - PolicySet: RunOfRiverFit
          FIT:
            TsFit: 100.0  # EUR/MWh - AMIRIS's own value (Germany2019); Brainpool gives no
                          # hydro subsidy rate and no EEG hydro-specific rate was researched.
        - PolicySet: SolarOpenfieldMpvar
          MPVAR:
            Lcoe: 49.0    # EUR/MWh - BNetzA solar auction, volume-weighted award value,
                          # March 2026 round (4.94 ct/kWh).
        - PolicySet: WindOnMpvar
          MPVAR:
            Lcoe: 52.0    # EUR/MWh - BNetzA wind-onshore auction trend, Feb-Aug 2026 rounds
                          # (5.06-5.54 ct/kWh), midpoint used as 2027 projection.
        - PolicySet: WindOffMpvar
          MPVAR:
            Lcoe: 187.0   # EUR/MWh - GAP FILL: no real 2027 offshore reference exists (see
                          # note above). AMIRIS's own Germany2019 offshore clusters'
                          # capacity-weighted LCOE used as placeholder.
        - PolicySet: BiomassMpvar
          MPVAR:
            Lcoe: 197.0   # EUR/MWh - BNetzA biomass tender, April 2026 round, cleared near
                          # the published Hoechstwert ceiling (19.43-19.83 ct/kWh) since
                          # undersubscribed. Deliberate departure from AMIRIS's own example,
                          # which leaves biomass unsupported - this is a more realistic figure.

  # Solar Grid Feed-in (utility-scale, ground-mounted) - 119.179 GW (Brainpool 2027).
  # MPVAR per EEG Section 22 (>1MW ground-mounted PV is auction/market-premium, not fixed FIT).
  - Type: VariableRenewableOperator
    Id: 60
    Attributes:
      PolicySet: SolarOpenfieldMpvar
      SupportInstrument: MPVAR
      EnergyCarrier: PV
      InstalledPowerInMW: 119178.868276127
      OpexVarInEURperMWH: 0.0
      YieldProfile: "./timeseries/solar_openfield_profile.csv"

  # Solar Prosuming (rooftop) - 33.706 GW (Brainpool 2027). FIT per EEG Section 49
  # (small-scale rooftop remains fixed-tariff eligible under current law).
  - Type: VariableRenewableOperator
    Id: 61
    Attributes:
      PolicySet: SolarRooftopFit
      SupportInstrument: FIT
      EnergyCarrier: PV
      InstalledPowerInMW: 33706.08139088115
      OpexVarInEURperMWH: 0.0
      YieldProfile: "./timeseries/solar_rooftop_profile.csv"

  # Wind Onshore - 90.232 GW (Brainpool 2027). MPVAR per EEG Section 22/28 (auction-based
  # since 2017).
  - Type: VariableRenewableOperator
    Id: 70
    Attributes:
      PolicySet: WindOnMpvar
      SupportInstrument: MPVAR
      EnergyCarrier: WindOn
      InstalledPowerInMW: 90231.75406367402
      OpexVarInEURperMWH: 0.0
      YieldProfile: "./timeseries/wind_onshore_profile.csv"

  # Wind Offshore - 12.573 GW (Brainpool 2027). Profile: AMIRIS's own, validated against a
  # real independent benchmark (implied 37.1% annual capacity factor sits inside the real
  # German offshore fleet's 37-45% range, per EnergyNumbers.info / Fraunhofer research).
  - Type: VariableRenewableOperator
    Id: 80
    Attributes:
      PolicySet: WindOffMpvar
      SupportInstrument: MPVAR
      EnergyCarrier: WindOff
      InstalledPowerInMW: 12572.84611136014
      OpexVarInEURperMWH: 0.0
      YieldProfile: "./timeseries/wind_offshore_profile.csv"

  # Run-of-River - 4.161 GW (Brainpool 2027). Weather/flow-driven, so modelled as a
  # VariableRenewableOperator like AMIRIS's own convention (not as dispatchable storage,
  # unlike the separate Reservoir Hydro entry in Storage.yaml).
  - Type: VariableRenewableOperator
    Id: 50
    Attributes:
      PolicySet: RunOfRiverFit
      SupportInstrument: FIT
      EnergyCarrier: RunOfRiver
      InstalledPowerInMW: 4160.632493649675
      OpexVarInEURperMWH: 0.0
      YieldProfile: "./timeseries/run_of_river_profile.csv"

  # Other Renewables (mapped to Biomass/biogas, the dominant real component of this category)
  # - 8.25 GW (Brainpool 2027). Dispatch: FROM_FILE, using AMIRIS's own biomass dispatch
  # shape, since Brainpool gives no biomass-specific hourly profile.
  - Type: Biogas
    Id: 52
    Attributes:
      PolicySet: BiomassMpvar
      SupportInstrument: MPVAR
      EnergyCarrier: Biogas
      InstalledPowerInMW: 8250.0
      OpexVarInEURperMWH: 0.0
      DispatchTimeSeries: "./timeseries/biomass_profile.csv"
      OperationMode: FROM_FILE
"""
    w(AGENTS_DIR / "RenewablesAndPolicy.yaml", text)


def build_storage():
    # Pumpspeicher: Brainpool power 8.3776 GW; duration 6.398914741428923h, the capacity-
    # weighted figure computed earlier from AMIRIS's own 16 daily-cycle storage units
    # (excludes the two long-duration outlier units, now understood to represent reservoir
    # hydro - see Reservoir Hydro entry below). Efficiencies: same fleet's blended average.
    pump_power_mw = 8377.599609375
    pump_duration_h = 6.398914741428923
    pump_energy_mwh = pump_power_mw * pump_duration_h

    # Battery: Brainpool power 5.1517 GW; duration 2.0h, per real MaStR-derived research
    # (RWE's Hambach project, 236 MW / 470 MWh, targets 2027 commissioning - the same year as
    # this scenario). Efficiency: standard Li-ion round-trip assumption (~90%, split evenly),
    # since MaStR research gave a duration figure but not an efficiency figure.
    batt_power_mw = 5151.699365501195
    batt_duration_h = 2.0
    batt_energy_mwh = batt_power_mw * batt_duration_h

    # Reservoir Hydro: Brainpool capacity 1.54 GW, modelled as dispatchable storage (see
    # module docstring point 5). Duration and efficiency borrowed from AMIRIS's own long-
    # duration unit (Id 716 in Germany2019: 450 MW / 50,050 MWh = 111.2h, 0.91/0.91
    # efficiency), the smaller and more conservative of the two excluded outlier units.
    res_power_mw = 1540.0
    res_duration_h = 111.22222222222223
    res_energy_mwh = res_power_mw * res_duration_h

    text = f"""
Agents:
  # Pumped Hydro Storage - 8.3776 GW power (Brainpool 2027); {pump_energy_mwh:.1f} MWh energy
  # ({pump_duration_h:.4f}h duration, AMIRIS's own validated pumped-hydro-fleet figure).
  - Attributes:
      Assessment:
        Type: MIN_SYSTEM_COST
      Bidding:
        SchedulingHorizonInHours: 24
        Type: ENSURE_DISPATCH
      Device:
        ChargingEfficiency: 0.875
        DischargingEfficiency: 0.852
        EnergyContentUpperLimitInMWH: {pump_energy_mwh:.2f}
        GrossChargingPowerInMW: {pump_power_mw:.2f}
        InitialEnergyContentInMWH: {pump_energy_mwh / 2:.2f}
        NetDischargingPowerInMW: {pump_power_mw * 0.95:.2f}
      StateDiscretisation:
        EnergyResolutionInMWH: {pump_energy_mwh / 34:.2f}
        PlanningHorizonInHours: 168
        Type: STATE_OF_CHARGE
    Id: 700
    Type: GenericFlexibilityTrader

  # Large-Scale Battery Storage - 5.1517 GW power (Brainpool 2027); {batt_energy_mwh:.1f} MWh
  # energy ({batt_duration_h:.1f}h duration - real MaStR/RWE Hambach-derived research figure,
  # not AMIRIS's own pumped-hydro-skewed value).
  - Attributes:
      Assessment:
        Type: MAX_PROFIT
      Bidding:
        SchedulingHorizonInHours: 24
        Type: STORAGE_CONTENT_VALUE
      Device:
        ChargingEfficiency: 0.95
        DischargingEfficiency: 0.95
        EnergyContentUpperLimitInMWH: {batt_energy_mwh:.2f}
        GrossChargingPowerInMW: {batt_power_mw:.2f}
        InitialEnergyContentInMWH: {batt_energy_mwh / 2:.2f}
        NetDischargingPowerInMW: {batt_power_mw * 0.97:.2f}
      StateDiscretisation:
        EnergyResolutionInMWH: {batt_energy_mwh / 34:.2f}
        PlanningHorizonInHours: 168
        Type: STATE_OF_CHARGE
    Id: 701
    Type: GenericFlexibilityTrader

  # Reservoir Hydro - 1.54 GW power (Brainpool 2027); {res_energy_mwh:.1f} MWh energy
  # ({res_duration_h:.2f}h duration - borrowed from AMIRIS's own long-duration reservoir-type
  # unit, since Brainpool gives no hydro storage energy figure).
  - Attributes:
      Assessment:
        Type: MIN_SYSTEM_COST
      Bidding:
        SchedulingHorizonInHours: 168
        Type: ENSURE_DISPATCH
      Device:
        ChargingEfficiency: 0.91
        DischargingEfficiency: 0.91
        EnergyContentUpperLimitInMWH: {res_energy_mwh:.2f}
        GrossChargingPowerInMW: {res_power_mw:.2f}
        InitialEnergyContentInMWH: {res_energy_mwh * 0.44:.2f}
        NetDischargingPowerInMW: {res_power_mw * 1.17:.2f}
      StateDiscretisation:
        EnergyResolutionInMWH: {res_energy_mwh / 1223:.2f}
        PlanningHorizonInHours: 730
        Type: STATE_OF_CHARGE
    Id: 702
    Type: GenericFlexibilityTrader
"""
    w(AGENTS_DIR / "Storage.yaml", text)
    print(f"    Pumpspeicher: {pump_power_mw:.1f} MW / {pump_energy_mwh:.1f} MWh")
    print(f"    Battery:      {batt_power_mw:.1f} MW / {batt_energy_mwh:.1f} MWh")
    print(f"    Reservoir:    {res_power_mw:.1f} MW / {res_energy_mwh:.1f} MWh")


def build_demand():
    # V1 (BDEW) wired as the active load file for the first build. Swap to load_v2.csv once
    # the component-split version is built, or keep both and diff results.
    text = """
Agents:
  - Type: DemandTrader
    Id: 100
    Attributes:
      Loads:
        - ValueOfLostLoad: 3000.0
          DemandSeries: "./timeseries/load_v1_bdew.csv"
"""
    w(AGENTS_DIR / "Demand.yaml", text)


def build_markets_and_forecast():
    text = """
Agents:
  - Type: DayAheadMarketSingleZone
    Id: 1
    Attributes:
      Clearing: &clearingParameters
        DistributionMethod: SAME_SHARES
      GateClosureInfoOffsetInSeconds: 31

  - Type: CarbonMarket
    Id: 3
    Attributes:
      OperationMode: FIXED
      Co2Prices: "./timeseries/co2_price.csv"

  # Sources: LIGNITE and NUCLEAR fuel costs are AMIRIS's own flat estimates (Nuclear is moot
  # - 0 GW capacity). Hard coal / natural gas / oil: built from Brainpool's Variable_cost
  # sheet with unit conversions - see build_2027_timeseries.py.
  - Type: FuelsMarket
    Id: 4
    Attributes:
      FuelPrices:
        - FuelType: LIGNITE
          Price: 5.00
          ConversionFactor: 1.0
        - FuelType: HARD_COAL
          Price: "./timeseries/hard_coal_price.csv"
          ConversionFactor: 1.0
        - FuelType: NATURAL_GAS
          Price: "./timeseries/natural_gas_price.csv"
          ConversionFactor: 1.0
        - FuelType: OIL
          Price: "./timeseries/oil_price.csv"
          ConversionFactor: 1.0

  - Type: SensitivityForecaster
    Id: 6
    Attributes:
      Clearing: *clearingParameters
      ForecastPeriodInHours: 730
      MultiplierEstimation:
        InitialEstimateWeight: 6
        DecayInterval: 168
"""
    w(AGENTS_DIR / "MarketsAndForecast.yaml", text)


def main():
    AGENTS_DIR.mkdir(parents=True, exist_ok=True)
    print("Conventionals.yaml:")
    build_conventionals()
    print("RenewablesAndPolicy.yaml:")
    build_renewables_and_policy()
    print("Storage.yaml:")
    build_storage()
    print("Demand.yaml:")
    build_demand()
    print("MarketsAndForecast.yaml:")
    build_markets_and_forecast()
    print("\nDone. Files written to:", AGENTS_DIR)


if __name__ == "__main__":
    main()
