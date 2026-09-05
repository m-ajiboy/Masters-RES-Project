"""Documents the fuel-price plan for the Rest-of-Europe zone. Coal, gas, and oil are
internationally-traded commodities with roughly uniform European benchmark prices (unlike
demand, which is nationally idiosyncratic) - so Germany's own real hourly price series
(already built from Brainpool's Variable_cost sheet) are reused directly, copied alongside
this zone's other real data. Nuclear is new for this zone (Germany has 0 GW, post
phase-out) - sourced a real 2023 figure: $5.32/MWh fuel cost (Nuclear Energy Institute /
Electric Utility Cost Group, 2023 US fleet average - the most current, specific real "fuel
cost" figure found; European-specific 2023 data was not available, this is the closest real
reference), converted at ~0.92 EUR/USD to ~4.90 EUR/MWh, rounded to a flat 5.0 EUR/MWh -
treated as flat (not hourly) since nuclear fuel cost is inherently stable, the same
treatment already given to lignite's own flat 5.0 EUR/MWh placeholder in Germany's build.
"""
import json

plan = {
    "HARD_COAL": {
        "source": "Reused directly from Germany2027_Feb29DropFix/timeseries/hard_coal_price.csv",
        "file": "hard_coal_price_restofeurope_2027.csv",
        "rationale": "Internationally-traded commodity - same European benchmark applies across the zone.",
    },
    "NATURAL_GAS": {
        "source": "Reused directly from Germany2027_Feb29DropFix/timeseries/natural_gas_price.csv",
        "file": "natural_gas_price_restofeurope_2027.csv",
        "rationale": "Internationally-traded commodity (European TTF-linked benchmark) - same price applies across the zone.",
    },
    "OIL": {
        "source": "Reused directly from Germany2027_Feb29DropFix/timeseries/oil_price.csv",
        "file": "oil_price_restofeurope_2027.csv",
        "rationale": "Internationally-traded commodity (global oil benchmark) - same price applies across the zone.",
    },
    "NUCLEAR": {
        "source": "Real 2023 US fleet average (NEI/EUCG): $5.32/MWh fuel cost, converted at ~0.92 EUR/USD",
        "value_EUR_per_MWh": 5.0,
        "type": "flat (not hourly)",
        "rationale": "Nuclear fuel cost is inherently stable, unlike traded fossil fuels - same flat "
                     "treatment already used for lignite's own 5.0 EUR/MWh in Germany's build. "
                     "European-specific 2023 data was not found; this is the closest real reference "
                     "(most current, specific real fuel-cost figure located).",
    },
    "COAL_LIGNITE_SPLIT_NOTE": "Eurostat's 'Coal_and_manufactured_gases' capacity figure (29,855 MW "
        "for the zone, dominated by Poland's 27,017 MW) does not distinguish lignite from hard coal "
        "the way Germany's own build does. Documented simplification: the whole bucket uses the "
        "HARD_COAL price series - splitting out a lignite-specific portion would need more granular "
        "per-country data than is currently available.",
}

OUT = r"C:\Users\MuideenOA\Desktop\PyTut\Amiris\examples\backtest\RestOfEurope2023\fuel_prices_plan.json"
with open(OUT, "w") as f:
    json.dump(plan, f, indent=2)
print(f"Saved {OUT}")
for fuel, info in plan.items():
    if fuel == "COAL_LIGNITE_SPLIT_NOTE":
        continue
    print(f"\n{fuel}: {info.get('value_EUR_per_MWh', 'real hourly series, see file')}")
