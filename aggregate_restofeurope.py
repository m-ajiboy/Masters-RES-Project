"""Aggregates the real Eurostat demand and capacity data fetched by
fetch_eurostat_restofeurope.py into a single 'Rest of Europe' composite - the interim
zone for the market-coupling scoping (Phase 32), built while ENTSO-E's API is down.
Covers 9 of Germany's 10 real neighbouring countries (all real 2023 Eurostat data);
Switzerland is a confirmed, documented gap (not covered by this Eurostat dataset at all -
not an EU member, does not report under Regulation 1099/2008) - flagged for ENTSO-E
backfill once that API is back up.
"""
import json

RAW_DIR = r"C:\Users\MuideenOA\Desktop\PyTut\Amiris\examples\backtest\RestOfEurope2023\raw_eurostat"

with open(rf"{RAW_DIR}\demand_annual_GWh.json") as f:
    demand = json.load(f)
with open(rf"{RAW_DIR}\capacity_MW_by_tech.json") as f:
    capacity = json.load(f)

COVERED = [c for c in demand if demand[c][1] is not None]
MISSING = [c for c in demand if demand[c][1] is None]

print("=" * 70)
print(f"Covered countries (real 2023 Eurostat data): {COVERED}")
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
    "source": "Eurostat nrg_cb_e (demand, FC) and nrg_inf_epc (capacity, CAP_NET_ELC), real 2023 annual data",
    "total_demand_GWh": total_demand_gwh,
    "capacity_MW_by_tech": totals,
    "per_country_demand_GWh": {c: demand[c][1] for c in COVERED},
    "per_country_capacity_MW": {c: {k: v for k, v in capacity[c].items() if k != "year"} for c in COVERED},
}
with open(rf"{RAW_DIR}\..\restofeurope_aggregate_summary.json", "w") as f:
    json.dump(summary, f, indent=2)
print(f"\nSaved aggregate summary to examples\\backtest\\RestOfEurope2023\\restofeurope_aggregate_summary.json")
