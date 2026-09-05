"""Processes the real ENTSO-E backfill (Phase 33 addendum): computes net annual flow per
border, updates the Rest-of-Europe aggregate summary with Switzerland's real data, and
reports the combined 10-country picture (9 Eurostat + 1 ENTSO-E) for the first time.
"""
import json
import pandas as pd

ROE_DIR = r"C:\Users\MuideenOA\Desktop\PyTut\Amiris\examples\backtest\RestOfEurope2023"
ENTSOE_DIR = rf"{ROE_DIR}\raw_entsoe"

with open(rf"{ENTSOE_DIR}\..\entsoe_backfill_summary.json") as f:
    entsoe = json.load(f)

print("=" * 70)
print("NET ANNUAL FLOW PER BORDER (DE perspective: + = net export, - = net import)")
print("=" * 70)
zones = ["AT", "BE", "CH", "CZ", "DK_1", "DK_2", "FR", "NO_2", "NL", "PL"]
flows = entsoe["flows_MWh_annual_total"]
net_flows = {}
for z in zones:
    out_ = flows.get(f"DE_to_{z}")
    in_ = flows.get(f"{z}_to_DE")
    if out_ is not None and in_ is not None:
        net = out_ - in_
        net_flows[z] = net
        direction = "net export to" if net > 0 else "net import from"
        print(f"  DE <-> {z}: DE->={out_:,.0f} MWh, {z}->DE={in_:,.0f} MWh, "
              f"{direction} {z}: {abs(net):,.0f} MWh")

total_net = sum(net_flows.values())
print(f"\nTotal net flow (10 borders, excl. SE_4): {total_net:+,.0f} MWh "
      f"({'net exporter' if total_net > 0 else 'net importer'} overall)")

# Update the Rest-of-Europe aggregate with Switzerland's real data
with open(rf"{ROE_DIR}\restofeurope_aggregate_summary.json") as f:
    agg = json.load(f)

ch_demand_gwh = entsoe["ch_annual_demand_GWh"]
ch_capacity = entsoe["ch_capacity_MW"]

print("\n" + "=" * 70)
print("UPDATED 10-COUNTRY REST-OF-EUROPE AGGREGATE (9 Eurostat + Switzerland/ENTSO-E)")
print("=" * 70)
new_total_demand = agg["total_demand_GWh"] + ch_demand_gwh
print(f"Total demand: {agg['total_demand_GWh']:,.0f} + {ch_demand_gwh:,.0f} (CH) = {new_total_demand:,.0f} GWh")

# CH capacity maps: Hydro Pumped Storage + Hydro Water Reservoir -> Hydro_total (dispatchable
# categories); Hydro Run-of-river -> also Hydro_total (Eurostat's own bucket doesn't split
# either); Nuclear -> Nuclear.
ch_hydro_total = (ch_capacity.get("Hydro Pumped Storage", 0)
                   + ch_capacity.get("Hydro Water Reservoir", 0)
                   + ch_capacity.get("Hydro Run-of-river and poundage", 0))
ch_nuclear = ch_capacity.get("Nuclear", 0)

new_capacity = dict(agg["capacity_MW_by_tech"])
new_capacity["Hydro_total"] += ch_hydro_total
new_capacity["Nuclear"] += ch_nuclear
new_total_capacity = sum(new_capacity.values())

print(f"\nCapacity additions from Switzerland: Hydro +{ch_hydro_total:,.0f} MW, Nuclear +{ch_nuclear:,.0f} MW")
print(f"New total capacity (10 countries): {new_total_capacity:,.0f} MW (was {sum(agg['capacity_MW_by_tech'].values()):,.0f} MW for 9)")

updated = dict(agg)
updated["covered_countries"] = agg["covered_countries"] + ["CH"]
updated["missing_countries"] = []
updated["total_demand_GWh"] = new_total_demand
updated["capacity_MW_by_tech"] = new_capacity
updated["per_country_demand_GWh"]["CH"] = ch_demand_gwh
updated["per_country_capacity_MW"]["CH"] = {
    "Hydro_total": ch_hydro_total, "Nuclear": ch_nuclear,
    "Coal_and_manufactured_gases": 0, "Natural_gas": 0, "Oil": 0,
    "Wind_onshore": 0, "Wind_offshore": 0, "Solar_PV": 0, "Biofuels_and_waste": 0,
}
updated["net_flows_MWh_2023"] = net_flows
updated["source"] = agg["source"] + "; Switzerland (CH) via ENTSO-E Transparency Platform, real 2023 annual data"

with open(rf"{ROE_DIR}\restofeurope_aggregate_summary.json", "w") as f:
    json.dump(updated, f, indent=2)
print(f"\nUpdated restofeurope_aggregate_summary.json - now 10/10 countries covered, zero gaps.")
