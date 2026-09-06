"""Phase 43: generates the agent and contract YAML files for the 9 remaining real country
zones (AT, BE, CZ, DK, NO, NL, PL, SE, CH), using the real numbers computed by
build_all_zones_data.py. Mirrors the exact structure and ID-offset pattern already
hand-written for France (Phase 42) - built programmatically here purely because of the
volume (9 countries x ~10 files each), not because the underlying design differs."""
import json

ROE_ROOT = r"C:\Users\MuideenOA\Desktop\PyTut\Amiris\examples\backtest\RestOfEurope2023"
OUT_ROOT = r"C:\Users\MuideenOA\Desktop\PyTut\Amiris\examples\backtest\Germany2027_MarketCoupling_AllZones"
AGENTS_DIR = rf"{OUT_ROOT}\agents"
CONTRACTS_DIR = rf"{OUT_ROOT}\contracts"

with open(rf"{ROE_ROOT}\allzones_computed_numbers.json") as f:
    DATA = json.load(f)

FULL_NAMES = {"AT": "Austria", "BE": "Belgium", "CZ": "Czech Republic", "DK": "Denmark",
              "NO": "Norway", "NL": "Netherlands", "PL": "Poland", "SE": "Sweden", "CH": "Switzerland"}


def conventionals_agent_yaml(code, d):
    base = d["base"]
    lines = ["Variables:", "  - &portfolioBuildingOffset 60", "", "Agents:"]
    lines.append(f"  # {FULL_NAMES[code]} - real Eurostat 2023 capacity, same efficiency/markup/CO2 "
                  f"assumptions reused from DE's own fleet (Phase 33/42 precedent). Technologies with "
                  f"zero real capacity are simply absent, not zeroed out.")
    fuels = [
        ("HARD_COAL", "coal_mw", 101, 0.338, 0.05, 2.5, 0.339, 0.492, 300.0),
        ("NATURAL_GAS", "gas_mw", 102, 0.202, 0.05, 1.2, 0.516, 0.617, 200.0),
        ("OIL", "oil_mw", 103, 0.266, 0.07, 1.2, 0.311, 0.397, 100.0),
        ("NUCLEAR", "nuclear_mw", 104, 0.0, 0.10, 3.0, 0.33, 0.33, 1000.0),
    ]
    present_fuels = []
    for fuel, key, off, co2, outage, opex, effmin, effmax, block in fuels:
        mw = d[key]
        if mw <= 0:
            continue
        present_fuels.append((fuel, off))
        bsize = min(block, mw) if mw < block else block
        lines.append(f"""
  - Type: PredefinedPlantBuilder
    Id: {base + off}
    Attributes:
      PortfolioBuildingOffsetInSeconds: *portfolioBuildingOffset
      Prototype:
        FuelType: {fuel}
        SpecificCo2EmissionsInTperMWH: {co2}
        OutageFactor: {outage}
        OpexVarInEURperMWH: {opex}
        CyclingCostInEURperMW: 0.0
      Efficiency:
        Minimal: {effmin}
        Maximal: {effmax}
      BlockSizeInMW: {bsize}
      InstalledPowerInMW: {mw}""")
    for fuel, off in present_fuels:
        markup = {"HARD_COAL": (-15, 5), "NATURAL_GAS": (-10, 10), "OIL": (0, 0), "NUCLEAR": (-5, 0)}[fuel]
        lines.append(f"""
  - Type: ConventionalTrader # {fuel} ({code})
    Id: {base + off + 100}
    Attributes:
      minMarkup: {markup[0]}
      maxMarkup: {markup[1]}""")
    for fuel, off in present_fuels:
        lines.append(f"""
  - Type: ConventionalPlantOperator # {fuel} ({code})
    Id: {base + off + 200}""")
    return "\n".join(lines) + "\n", present_fuels


def demand_agent_yaml(code, d):
    return f"""Agents:
  # {FULL_NAMES[code]}'s own real annual demand total ({d["demand_mwh"]:,.0f} MWh, Eurostat 2023),
  # shaped using Germany's own real 2027 demand pattern (same borrowed-shape precedent as
  # every other zone in this build).
  - Type: DemandTrader
    Id: {d["base"] + 500}
    Attributes:
      Loads:
        - ValueOfLostLoad: 3000.0
          DemandSeries: "./timeseries/load_{code.lower()}_2027_shapeFromDE.csv"
"""


def renewables_agent_yaml(code, d):
    base = d["base"]
    lines = ["Agents:"]
    lines.append(f"""  # {FULL_NAMES[code]}'s own dedicated SupportPolicy - NOT shared with any other zone
  # (confirmed required directly in Phase 42: a shared SupportPolicy crashes once more than
  # one zone's exchange sends it Awards).
  - Type: SupportPolicy
    Id: {base + 90}
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
            TsFit: 0.0""")
    if d["has_windon"]:
        lines.append(f"""
  - Type: VariableRenewableOperator
    Id: {base + 401}
    Attributes:
      PolicySet: ROE_WindOnMpvar
      SupportInstrument: MPVAR
      EnergyCarrier: WindOn
      InstalledPowerInMW: {d["windon_mw"]}
      OpexVarInEURperMWH: 0.0
      YieldProfile: "./timeseries/wind_onshore_profile_{code.lower()}_2027.csv" """)
    if d["has_windoff"]:
        lines.append(f"""
  - Type: VariableRenewableOperator
    Id: {base + 402}
    Attributes:
      PolicySet: ROE_WindOffMpvar
      SupportInstrument: MPVAR
      EnergyCarrier: WindOff
      InstalledPowerInMW: {d["windoff_mw"]}
      OpexVarInEURperMWH: 0.0
      YieldProfile: "./timeseries/wind_offshore_profile_{code.lower()}_2027.csv" """)
    if d["has_solar"]:
        lines.append(f"""
  - Type: VariableRenewableOperator
    Id: {base + 403}
    Attributes:
      PolicySet: ROE_SolarMpvar
      SupportInstrument: MPVAR
      EnergyCarrier: PV
      InstalledPowerInMW: {d["solar_mw"]}
      OpexVarInEURperMWH: 0.0
      YieldProfile: "./timeseries/solar_profile_{code.lower()}_2027.csv" """)
    has_ror = d["ror_mw"] > 0
    if has_ror:
        lines.append(f"""
  - Type: VariableRenewableOperator
    Id: {base + 404}
    Attributes:
      PolicySet: Undefined
      SupportInstrument: FIT
      EnergyCarrier: RunOfRiver
      InstalledPowerInMW: {d["ror_mw"]:.2f}
      OpexVarInEURperMWH: 0.0
      YieldProfile: "./timeseries/hydro_profile_restofeurope_FLAT.csv" """)
    if d["has_windon"] or d["has_windoff"] or d["has_solar"]:
        lines.append(f"""
  - Type: RenewableTrader
    Id: {base + 11}
    Attributes:
      ShareOfRevenues: 0.0""")
    if has_ror:
        lines.append(f"""
  - Type: SystemOperatorTrader
    Id: {base + 13}""")
    return "\n".join(lines) + "\n", has_ror


def storage_agent_yaml(code, d):
    base = d["base"]
    pumped_mw = d["pumped_mw"]
    reservoir_mw = d["reservoir_mw"]
    if pumped_mw <= 0 and reservoir_mw <= 0:
        return None
    lines = ["Agents:"]
    if pumped_mw > 0:
        scale = pumped_mw / 33303.20
        energy = 213104.35 * scale
        net = 31638.04 * scale
        initial = energy * 0.5
        res = 6267.78 * scale
        lines.append(f"""  # {FULL_NAMES[code]} Pumped Storage - {pumped_mw:,.1f} MW (30% EU-wide IHA method, Phase 33).
  # Duration/efficiency/power-ratio reused from Germany's own real pumped-hydro figures.
  - Attributes:
      Assessment:
        Type: MIN_SYSTEM_COST
      Bidding:
        SchedulingHorizonInHours: 24
        Type: ENSURE_DISPATCH
      Device:
        ChargingEfficiency: 0.875
        DischargingEfficiency: 0.852
        EnergyContentUpperLimitInMWH: {energy:.2f}
        GrossChargingPowerInMW: {pumped_mw:.2f}
        InitialEnergyContentInMWH: {initial:.2f}
        NetDischargingPowerInMW: {net:.2f}
      StateDiscretisation:
        EnergyResolutionInMWH: {res:.2f}
        PlanningHorizonInHours: 168
        Type: STATE_OF_CHARGE
    Id: {base + 601}
    Type: GenericFlexibilityTrader""")
    if reservoir_mw > 0:
        scale = reservoir_mw / 69904.05
        energy = 7774883.23 * scale
        net = 81787.73 * scale
        initial = energy * 0.5
        res = 6362.42 * scale
        lines.append(f"""
  # {FULL_NAMES[code]} Reservoir Hydro - {reservoir_mw:,.1f} MW (90.2% of conventional hydro, Swiss ratio).
  - Attributes:
      Assessment:
        Type: MIN_SYSTEM_COST
      Bidding:
        SchedulingHorizonInHours: 168
        Type: ENSURE_DISPATCH
      Device:
        ChargingEfficiency: 0.91
        DischargingEfficiency: 0.91
        EnergyContentUpperLimitInMWH: {energy:.2f}
        GrossChargingPowerInMW: {reservoir_mw:.2f}
        InitialEnergyContentInMWH: {initial:.2f}
        NetDischargingPowerInMW: {net:.2f}
      StateDiscretisation:
        EnergyResolutionInMWH: {res:.2f}
        PlanningHorizonInHours: 730
        Type: STATE_OF_CHARGE
    Id: {base + 602}
    Type: GenericFlexibilityTrader""")
    return "\n".join(lines) + "\n"


CONVENTIONALS_CONTRACT_TMPL = """AgentGroups:
  - &builders  [{builders}]
  - &traders   [{traders}]
  - &operators [{operators}]
  - &exchange {exchange}
  - &carbonMarket 3
  - &fuelsMarket {fuelsMarket}
  - &forecaster {forecaster}

Contracts:
  - SenderId: *builders
    ReceiverId: *operators
    ProductName: PowerPlantPortfolio
    FirstDeliveryTime: -60
    Every: 1 year

  - SenderId: *forecaster
    ReceiverId: *traders
    ProductName: ForecastRequest
    FirstDeliveryTime: -26
    Every: 1 hour

  - SenderId: *traders
    ReceiverId: *operators
    ProductName: ForecastRequestForward
    FirstDeliveryTime: -25
    Every: 1 hour

  - SenderId: *operators
    ReceiverId: *fuelsMarket
    ProductName: FuelPriceForecastRequest
    FirstDeliveryTime: -24
    Every: 1 hour

  - SenderId: *operators
    ReceiverId: *carbonMarket
    ProductName: Co2PriceForecastRequest
    FirstDeliveryTime: -24
    Every: 1 hour

  - SenderId: *fuelsMarket
    ReceiverId: *operators
    ProductName: FuelPriceForecast
    FirstDeliveryTime: -23
    Every: 1 hour

  - SenderId: *carbonMarket
    ReceiverId: *operators
    ProductName: Co2PriceForecast
    FirstDeliveryTime: -23
    Every: 1 hour

  - SenderId: *operators
    ReceiverId: *traders
    ProductName: MarginalCostForecast
    FirstDeliveryTime: -22
    Every: 1 hour

  - SenderId: *traders
    ReceiverId: *forecaster
    ProductName: BidsForecast
    FirstDeliveryTime: -21
    Every: 1 hour

  - SenderId: *exchange
    ReceiverId: *traders
    ProductName: GateClosureInfo
    FirstDeliveryTime: -30
    Every: 1 hour

  - SenderId: *traders
    ReceiverId: *operators
    ProductName: GateClosureForward
    FirstDeliveryTime: -9
    Every: 1 hour

  - SenderId: *operators
    ReceiverId: *fuelsMarket
    ProductName: FuelPriceRequest
    FirstDeliveryTime: -3
    Every: 1 hour

  - SenderId: *operators
    ReceiverId: *carbonMarket
    ProductName: Co2PriceRequest
    FirstDeliveryTime: -3
    Every: 1 hour

  - SenderId: *fuelsMarket
    ReceiverId: *operators
    ProductName: FuelPrice
    FirstDeliveryTime: -2
    Every: 1 hour

  - SenderId: *carbonMarket
    ReceiverId: *operators
    ProductName: Co2Price
    FirstDeliveryTime: -2
    Every: 1 hour

  - SenderId: *operators
    ReceiverId: *traders
    ProductName: MarginalCost
    FirstDeliveryTime: -1
    Every: 1 hour

  - SenderId: *traders
    ReceiverId: *exchange
    ProductName: Bids
    FirstDeliveryTime: 0
    Every: 1 hour

  - SenderId: *exchange
    ReceiverId: *traders
    ProductName: Awards
    FirstDeliveryTime: 4
    Every: 1 hour

  - SenderId: *traders
    ReceiverId: *operators
    ProductName: DispatchAssignment
    FirstDeliveryTime: 5
    Every: 1 hour

  - SenderId: *traders
    ReceiverId: *operators
    ProductName: Payout
    FirstDeliveryTime: 6
    Every: 1 hour
"""

DEMAND_CONTRACT_TMPL = """AgentGroups:
  - &exchange {exchange}
  - &forecaster {forecaster}
  - &demandTrader {demandTrader}

Contracts:
  - SenderId: *exchange
    ReceiverId: *demandTrader
    ProductName: GateClosureInfo
    FirstDeliveryTime: -30
    Every: 1 hour

  - SenderId: *forecaster
    ReceiverId: *demandTrader
    ProductName: ForecastRequest
    FirstDeliveryTime: -26
    Every: 1 hour

  - SenderId: *demandTrader
    ReceiverId: *forecaster
    ProductName: BidsForecast
    FirstDeliveryTime: -21
    Every: 1 hour

  - SenderId: *demandTrader
    ReceiverId: *exchange
    ProductName: Bids
    FirstDeliveryTime: 0
    Every: 1 hour

  - SenderId: *exchange
    ReceiverId: *demandTrader
    ProductName: Awards
    FirstDeliveryTime: 4
    Every: 1 hour
"""

RENEWABLES_MPVAR_TMPL = """AgentGroups:
  - &exchange {exchange}
  - &forecaster {forecaster}
  - &marketer {marketer}
  - &renewables [{renewables}]

Contracts:
  - SenderId: *renewables
    ReceiverId: *marketer
    ProductName: SetRegistration
    FirstDeliveryTime: -37
    Every: 1 year

  - SenderId: *forecaster
    ReceiverId: *marketer
    ProductName: ForecastRequest
    FirstDeliveryTime: -26
    Every: 1 hour

  - SenderId: *marketer
    ReceiverId: *renewables
    ProductName: ForecastRequestForward
    FirstDeliveryTime: -25
    Every: 1 hour

  - SenderId: *renewables
    ReceiverId: *marketer
    ProductName: MarginalCostForecast
    FirstDeliveryTime: -22
    Every: 1 hour

  - SenderId: *marketer
    ReceiverId: *forecaster
    ProductName: BidsForecast
    FirstDeliveryTime: -21
    Every: 1 hour

  - SenderId: *exchange
    ReceiverId: *marketer
    ProductName: GateClosureInfo
    FirstDeliveryTime: -30
    Every: 1 hour

  - SenderId: *marketer
    ReceiverId: *renewables
    ProductName: GateClosureForward
    FirstDeliveryTime: -9
    Every: 1 hour

  - SenderId: *renewables
    ReceiverId: *marketer
    ProductName: MarginalCost
    FirstDeliveryTime: -1
    Every: 1 hour

  - SenderId: *marketer
    ReceiverId: *exchange
    ProductName: Bids
    FirstDeliveryTime: 0
    Every: 1 hour

  - SenderId: *exchange
    ReceiverId: *marketer
    ProductName: Awards
    FirstDeliveryTime: 4
    Every: 1 hour

  - SenderId: *marketer
    ReceiverId: *renewables
    ProductName: DispatchAssignment
    FirstDeliveryTime: 5
    Every: 1 hour

  - SenderId: *marketer
    ReceiverId: *renewables
    ProductName: Payout
    FirstDeliveryTime: 2626204
    Every: 1 month
"""

STORAGE_CONTRACT_TMPL = """AgentGroups:
  - &exchange {exchange}
  - &forecaster {forecaster}
  - &storage [{storage}]

Contracts:
  - SenderId: *storage
    ReceiverId: *forecaster
    ProductName: ForecastRegistration
    FirstDeliveryTime: -30
    Every: 1 year

  - SenderId: *storage
    ReceiverId: *forecaster
    ProductName: SensitivityRequest
    FirstDeliveryTime: -21
    Every: 1 hour

  - SenderId: *forecaster
    ReceiverId: *storage
    ProductName: SensitivityForecast
    FirstDeliveryTime: -19
    Every: 1 hour

  - SenderId: *storage
    ReceiverId: *forecaster
    ProductName: NetAward
    FirstDeliveryTime: 6
    Every: 1 hour

  - SenderId: *exchange
    ReceiverId: [*storage, *forecaster]
    ProductName: GateClosureInfo
    FirstDeliveryTime: -30
    Every: 1 hour

  - SenderId: *storage
    ReceiverId: *exchange
    ProductName: Bids
    FirstDeliveryTime: 0
    Every: 1 hour

  - SenderId: *exchange
    ReceiverId: *storage
    ProductName: Awards
    FirstDeliveryTime: 4
    Every: 1 hour
"""

SUPPORTPOLICY_TMPL = """AgentGroups:
  - &exchange {exchange}
  - &policy {policy}
  - &allMarketers [{marketers}]
  - &supportedMarketers [{marketers}]

Contracts:
  - SenderId: *supportedMarketers
    ReceiverId: *policy
    ProductName: SupportInfoRequest
    FirstDeliveryTime: -35
    Every: 1 year

  - SenderId: *policy
    ReceiverId: *supportedMarketers
    ProductName: SupportInfo
    FirstDeliveryTime: -33
    Every: 1 year

  - SenderId: *allMarketers
    ReceiverId: *policy
    ProductName: YieldPotential
    FirstDeliveryTime: 1
    Every: 1 hour

  - SenderId: *exchange
    ReceiverId: *policy
    ProductName: Awards
    FirstDeliveryTime: 4
    Every: 1 hour

  - SenderId: *supportedMarketers
    ReceiverId: *policy
    ProductName: SupportPayoutRequest
    FirstDeliveryTime: 2626200
    Every: 1 month

  - SenderId: *policy
    ReceiverId: *supportedMarketers
    ProductName: SupportPayout
    FirstDeliveryTime: 2626202
    Every: 1 month

  - SenderId: *policy
    ReceiverId: *policy
    ProductName: MarketValueCalculation
    FirstDeliveryTime: 2626204
    Every: 1 month
"""

for code, d in DATA.items():
    base = d["base"]
    exchange, fuelsMarket, forecaster = base + 1, base + 4, base + 6

    conv_yaml, present_fuels = conventionals_agent_yaml(code, d)
    with open(rf"{AGENTS_DIR}\Conventionals{code}.yaml", "w", encoding="utf-8") as f:
        f.write(conv_yaml)

    with open(rf"{AGENTS_DIR}\Demand{code}.yaml", "w", encoding="utf-8") as f:
        f.write(demand_agent_yaml(code, d))

    ren_yaml, has_ror = renewables_agent_yaml(code, d)
    with open(rf"{AGENTS_DIR}\Renewables{code}.yaml", "w", encoding="utf-8") as f:
        f.write(ren_yaml)

    storage_yaml = storage_agent_yaml(code, d)
    if storage_yaml:
        with open(rf"{AGENTS_DIR}\Storage{code}.yaml", "w", encoding="utf-8") as f:
            f.write(storage_yaml)

    # Contracts
    if present_fuels:
        builders = ", ".join(str(base + off) for _, off in present_fuels)
        traders = ", ".join(str(base + off + 100) for _, off in present_fuels)
        operators = ", ".join(str(base + off + 200) for _, off in present_fuels)
        with open(rf"{CONTRACTS_DIR}\conventionals_{code}.yaml", "w", encoding="utf-8") as f:
            f.write(CONVENTIONALS_CONTRACT_TMPL.format(
                builders=builders, traders=traders, operators=operators,
                exchange=exchange, fuelsMarket=fuelsMarket, forecaster=forecaster))

    with open(rf"{CONTRACTS_DIR}\demand_{code}.yaml", "w", encoding="utf-8") as f:
        f.write(DEMAND_CONTRACT_TMPL.format(exchange=exchange, forecaster=forecaster, demandTrader=base + 500))

    mpvar_renewables = []
    if d["has_windon"]:
        mpvar_renewables.append(str(base + 401))
    if d["has_windoff"]:
        mpvar_renewables.append(str(base + 402))
    if d["has_solar"]:
        mpvar_renewables.append(str(base + 403))
    if mpvar_renewables:
        with open(rf"{CONTRACTS_DIR}\renewables_{code}.yaml", "w", encoding="utf-8") as f:
            f.write(RENEWABLES_MPVAR_TMPL.format(
                exchange=exchange, forecaster=forecaster, marketer=base + 11,
                renewables=", ".join(mpvar_renewables)))

    if has_ror:
        with open(rf"{CONTRACTS_DIR}\renewables_systemOperator_{code}.yaml", "w", encoding="utf-8") as f:
            f.write(RENEWABLES_MPVAR_TMPL.format(
                exchange=exchange, forecaster=forecaster, marketer=base + 13,
                renewables=str(base + 404)).replace(
                "ProductName: DispatchAssignment", "ProductName: DispatchAssignment"))  # same template works

    storage_ids = []
    if d["pumped_mw"] > 0:
        storage_ids.append(str(base + 601))
    if d["reservoir_mw"] > 0:
        storage_ids.append(str(base + 602))
    if storage_ids:
        with open(rf"{CONTRACTS_DIR}\storage_{code}.yaml", "w", encoding="utf-8") as f:
            f.write(STORAGE_CONTRACT_TMPL.format(exchange=exchange, forecaster=forecaster, storage=", ".join(storage_ids)))

    marketer_ids = []
    if mpvar_renewables:
        marketer_ids.append(str(base + 11))
    if has_ror:
        marketer_ids.append(str(base + 13))
    if marketer_ids:
        with open(rf"{CONTRACTS_DIR}\supportPolicy_{code}.yaml", "w", encoding="utf-8") as f:
            f.write(SUPPORTPOLICY_TMPL.format(exchange=exchange, policy=base + 90, marketers=", ".join(marketer_ids)))

    print(f"{code}: wrote agent + contract files (fuels={[f for f,_ in present_fuels]}, "
          f"windon={d['has_windon']}, windoff={d['has_windoff']}, solar={d['has_solar']}, "
          f"ror={has_ror}, pumped={d['pumped_mw']>0}, reservoir={d['reservoir_mw']>0})")

print("\nDone - all 9 zones' YAML files generated.")
