import json

ROE_ROOT = r"C:\Users\MuideenOA\Desktop\PyTut\Amiris\examples\backtest\RestOfEurope2023"
with open(rf"{ROE_ROOT}\allzones_computed_numbers.json") as f:
    DATA = json.load(f)

FULL_NAMES = {"AT": "Austria", "BE": "Belgium", "CZ": "Czech Republic", "DK": "Denmark",
              "NO": "Norway", "NL": "Netherlands", "PL": "Poland", "SE": "Sweden", "CH": "Switzerland"}

de_transmission_lines = []
market_blocks = []

for code, d in DATA.items():
    base = d["base"]
    de_transmission_lines.append(
        f'        - MarketZone: {code}\n          CapacityInMW: "./timeseries/transfer_DEto{code}_realflow.csv"')

    if code == "NL":
        continue  # NL already placed by hand, reusing the freed-up ROE Id block

    market_blocks.append(f"""
  #############################################
  # Zone {code} ({FULL_NAMES[code]}) - Phase 43
  #############################################
  - Type: DayAheadMarketMultiZone
    Id: {base + 1}
    Attributes:
      Clearing:
        DistributionMethod: SAME_SHARES
      GateClosureInfoOffsetInSeconds: 31
      MarketZone: {code}
      Transmission:
        - MarketZone: DE
          CapacityInMW: "./timeseries/transfer_{code}toDE_realflow.csv"

  - Type: FuelsMarket
    Id: {base + 4}
    Attributes:
      FuelPrices:
        - FuelType: NUCLEAR
          Price: 5.00
          ConversionFactor: 1.0
        - FuelType: HARD_COAL
          Price: "./timeseries/hard_coal_price_restofeurope_2027.csv"
          ConversionFactor: 1.0
        - FuelType: NATURAL_GAS
          Price: "./timeseries/natural_gas_price_restofeurope_2027.csv"
          ConversionFactor: 1.0
        - FuelType: OIL
          Price: "./timeseries/oil_price_restofeurope_2027.csv"
          ConversionFactor: 1.0

  - Type: SensitivityForecaster
    Id: {base + 6}
    Attributes:
      Clearing:
        DistributionMethod: SAME_SHARES
      ForecastPeriodInHours: 730
      MultiplierEstimation:
        InitialEstimateWeight: 6
        DecayInterval: 168""")

print("=== DE TRANSMISSION BLOCK (append to DE's Transmission list) ===")
print("\n".join(de_transmission_lines))

print("\n\n=== MARKET BLOCKS (insert before 'Market Coupling coordinator') ===")
print("".join(market_blocks))

print("\n\n=== MARKET COUPLING AGENT GROUP ===")
markets = [1, 8001] + [d["base"] + 1 for d in DATA.values()]
print(f"  - &markets  [{', '.join(str(m) for m in markets)}]")

print("\n\n=== MARKETZONE STRINGSET VALUES ===")
zones = ["DE", "FR"] + list(DATA.keys())
print(f"    Values: [{', '.join(repr(z) for z in zones)}]")

# Save the market blocks text to a file for easy insertion
with open(r"C:\Users\MuideenOA\Desktop\PyTut\Amiris\_allzones_market_blocks.txt", "w", encoding="utf-8") as f:
    f.write("".join(market_blocks))
with open(r"C:\Users\MuideenOA\Desktop\PyTut\Amiris\_allzones_de_transmission.txt", "w", encoding="utf-8") as f:
    f.write("\n".join(de_transmission_lines))
