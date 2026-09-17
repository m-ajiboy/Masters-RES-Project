"""2024-base variant of aggregate_restofeurope.py. Aggregates the real 2024 Eurostat demand
and capacity data into a single Rest-of-Europe composite, same 9-country coverage (Switzerland
backfilled separately via ENTSO-E, same as the 2023 build)."""
import json

RAW_DIR = r"C:\Users\MuideenOA\Desktop\PyTut\Amiris\examples\backtest\RestOfEurope2024\raw_eurostat"

with open(rf"{RAW_DIR}\demand_annual_GWh.json") as f:
    demand = json.load(f)
with open(rf"{RAW_DIR}\capacity_MW_by_tech.json") as f:
    capacity = json.load(f)

COVERED = [c for c in demand if demand[c][1] is not None]
MISSING = [c for c in demand if demand[c][1] is None]

print("=" * 70)
print(f"Covered countries (real 2024 Eurostat data): {COVERED}")
print(f"Missing (documented gap, needs ENTSO-E backfill): {MISSING}")
print("=" * 70)

total_demand_gwh = sum(demand[c][1] for c in COVERED)
print(f"\nTotal aggregate annual demand ({len(COVERED)} countries): {total_demand_gwh:,.0f} GWh "
      f"= {total_demand_gwh/1000:,.1f} TWh")

techs = list(next(iter(capacity.values())).keys())
techs.remove("year")
print("\nAggregate installed capacity by technology (MW):")
totals = {}
for tech in techs:
    total = sum(capacity[c].get(tech) or 0 for c in COVERED)
    totals[tech] = total
    print(f"  {tech:>28}: {total:>10,.0f} MW")

total_cap = sum(totals.values())
print(f"\n  {'TOTAL':>28}: {total_cap:>10,.0f} MW")

summary = {
    "covered_countries": COVERED,
    "missing_countries": MISSING,
    "source": "Eurostat nrg_cb_e (demand, FC) and nrg_inf_epc (capacity, CAP_NET_ELC), real 2024 annual data",
    "total_demand_GWh": total_demand_gwh,
    "capacity_MW_by_tech": totals,
    "per_country_demand_GWh": {c: demand[c][1] for c in COVERED},
    "per_country_capacity_MW": {c: {k: v for k, v in capacity[c].items() if k != "year"} for c in COVERED},
}
with open(rf"{RAW_DIR}\..\restofeurope_aggregate_summary.json", "w") as f:
    json.dump(summary, f, indent=2)
print(f"\nSaved aggregate summary to examples\\backtest\\RestOfEurope2024\\restofeurope_aggregate_summary.json")
