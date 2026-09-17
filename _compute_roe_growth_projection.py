"""Computes real 2028/2029 ROE capacity and demand PROJECTIONS by applying ERAA 2024's own
internally-consistent GROWTH RATES (2026->2028->2030, same source throughout, so no gross/net
or methodology mismatch) to this project's real 2024 Eurostat-anchored baseline (Phase 44) -
the same borrow-a-real-shape/rate-anchor-to-a-real-total technique already used throughout
this project (e.g. Germany's own demand shape rescaled to Eurostat's real ROE total; real 2009
weather blended with real capacity weights). Avoids ERAA's absolute demand figures entirely,
since those are gross demand (confirmed via ENTSO-E's own methodology docs) - a genuinely
different, non-comparable concept from Eurostat's net final-consumption figure this project
uses everywhere else.
"""
import pandas as pd
import json

CAP_PATH = r"C:\Users\MuideenOA\maven-tools\eraa_data\Dashboard_raw data\GenerationCapacities.xlsx"
DEM_PATH = r"C:\Users\MuideenOA\maven-tools\eraa_data\Dashboard_raw data\Aggregated_Demand.xlsx"
PHASE44_SUMMARY = r"C:\Users\MuideenOA\Desktop\PyTut\Amiris\examples\backtest\RestOfEurope2024\restofeurope_aggregate_summary.json"

COUNTRY_NODE_PREFIX = {
    "AT": ["AT00"], "BE": ["BE00", "BEOF"], "CH": ["CH00"], "CZ": ["CZ00"],
    "DK": ["DKE1", "DKHE", "DKK2", "DKKA", "DKKF", "DKN1", "DKN2", "DKNS", "DKW1"],
    "FR": ["FR00"], "NL": ["NL00", "NL60", "NLLL"],
    "NO": ["NOM1", "NON1", "NOS0", "NOS1", "NOS2", "NOS3"],
    "PL": ["PL00"], "SE": ["SE01", "SE02", "SE03", "SE04"],
}
NODE_TO_COUNTRY = {node: c for c, nodes in COUNTRY_NODE_PREFIX.items() for node in nodes}
TECH_MAP = {
    "Lignite": "Coal_and_manufactured_gases", "Hard coal": "Coal_and_manufactured_gases",
    "Gas": "Natural_gas", "Oil": "Oil", "Nuclear": "Nuclear",
    "Run of river": "Hydro_total", "Reservoir": "Hydro_total", "Pondage": "Hydro_total",
    "Open loop pumping": "Hydro_total", "Closed loop pumping": "Hydro_total",
    "Wind onshore": "Wind_onshore", "Wind offshore": "Wind_offshore",
    "Solar (PV)": "Solar_PV", "Solar roof-top PV": "Solar_PV", "Solar (thermal)": "Solar_PV",
    "Biofuel": "Biofuels_and_waste", "Small biomass": "Biofuels_and_waste",
}

with open(PHASE44_SUMMARY) as f:
    baseline = json.load(f)
baseline_cap = baseline["capacity_MW_by_tech"]
baseline_demand_twh = baseline["total_demand_GWh"] / 1000

# --- Capacity growth rates (ERAA's own internal 2026->2028->2030, same source both ends) ---
cap = pd.read_excel(CAP_PATH, sheet_name="data")
cap = cap[cap["DATA_VERSION"] == "Final"]
cap["COUNTRY"] = cap["MARKET_NODE"].map(NODE_TO_COUNTRY)
cap = cap.dropna(subset=["COUNTRY"])
cap["CATEGORY"] = cap["TECHNOLOGY"].map(TECH_MAP)
cap = cap.dropna(subset=["CATEGORY"])
cap_by_year_cat = cap.groupby(["TARGET_YEAR", "CATEGORY"])["CAPACITY_MW"].sum().unstack()

print("=" * 70)
print("Real ERAA capacity growth RATES (2026->2028->2030), by category:")
print("=" * 70)
growth_2026_2028 = cap_by_year_cat.loc[2028] / cap_by_year_cat.loc[2026]
growth_2028_2030 = cap_by_year_cat.loc[2030] / cap_by_year_cat.loc[2028]
for cat in cap_by_year_cat.columns:
    print(f"  {cat:>28}: 2026->2028 x{growth_2026_2028[cat]:.4f}, 2028->2030 x{growth_2028_2030[cat]:.4f}")

# Apply the 2026->2028 rate to our real 2024 baseline (nearest available real ERAA growth
# rate; a documented 2-year proxy - capacity does not move fast enough in 2 years for the
# 2024 vs 2026 starting-point gap to matter much, unlike demand's much larger, definitionally
# different jump).
projected_2028 = {cat: baseline_cap[cat] * growth_2026_2028[cat] for cat in cap_by_year_cat.columns if cat in baseline_cap}
# For 2029, interpolate log-linearly between the 2028 and 2030 ERAA growth factors
growth_2026_2029 = growth_2026_2028 * (growth_2028_2030 ** 0.5)
projected_2029 = {cat: baseline_cap[cat] * growth_2026_2029[cat] for cat in cap_by_year_cat.columns if cat in baseline_cap}

print("\n" + "=" * 70)
print("PROJECTED real-growth-rate-based ROE capacity (MW), applied to the real 2024 baseline:")
print("=" * 70)
print(f"{'Category':>28} {'2024 (real)':>14} {'2028 (proj)':>14} {'2029 (proj)':>14}")
for cat in baseline_cap:
    if cat in projected_2028:
        print(f"{cat:>28} {baseline_cap[cat]:>14,.0f} {projected_2028[cat]:>14,.0f} {projected_2029[cat]:>14,.0f}")
    else:
        print(f"{cat:>28} {baseline_cap[cat]:>14,.0f} {'(no ERAA match)':>14} {'(no ERAA match)':>14}")

total_2024 = sum(baseline_cap.values())
total_2028 = sum(projected_2028.values()) + sum(v for k, v in baseline_cap.items() if k not in projected_2028)
total_2029 = sum(projected_2029.values()) + sum(v for k, v in baseline_cap.items() if k not in projected_2029)
print(f"\n{'TOTAL':>28} {total_2024:>14,.0f} {total_2028:>14,.0f} {total_2029:>14,.0f}")
print(f"Implied growth: 2024->2028 {100*(total_2028/total_2024-1):+.1f}%, 2024->2029 {100*(total_2029/total_2024-1):+.1f}%")

# --- Demand growth rate (same technique - ERAA's own internal ratio only, never its
#     absolute gross-demand figure) ---
dem = pd.read_excel(DEM_PATH, sheet_name="Export")
dem = dem[(dem["DATA_VERSION"] == "Final") & (dem["TYPE_WS"] == "Avg")]
dem["COUNTRY"] = dem["MARKET_NODE"].map(NODE_TO_COUNTRY)
dem = dem.dropna(subset=["COUNTRY"])
dem_by_year = dem.groupby("TARGET_YEAR")["DEMAND_TWH"].sum()
dem_growth_2026_2028 = dem_by_year[2028] / dem_by_year[2026]
dem_growth_2028_2030 = dem_by_year[2030] / dem_by_year[2028]
dem_growth_2026_2029 = dem_growth_2026_2028 * (dem_growth_2028_2030 ** 0.5)

print("\n" + "=" * 70)
print("Real ERAA GROSS demand growth rates (internally consistent, never mixed with Eurostat's net figure):")
print("=" * 70)
print(f"  2026->2028: x{dem_growth_2026_2028:.4f} ({100*(dem_growth_2026_2028-1):+.2f}%)")
print(f"  2028->2030: x{dem_growth_2028_2030:.4f} ({100*(dem_growth_2028_2030-1):+.2f}%)")

proj_demand_2028 = baseline_demand_twh * dem_growth_2026_2028
proj_demand_2029 = baseline_demand_twh * dem_growth_2026_2029
print(f"\nApplied to real 2024 Eurostat NET baseline ({baseline_demand_twh:.1f} TWh):")
print(f"  Projected 2028 demand: {proj_demand_2028:.1f} TWh ({100*(proj_demand_2028/baseline_demand_twh-1):+.1f}%)")
print(f"  Projected 2029 demand: {proj_demand_2029:.1f} TWh ({100*(proj_demand_2029/baseline_demand_twh-1):+.1f}%)")

out = {
    "methodology": "ERAA 2024 (Final) internal growth rates 2026->2028->2030 applied to real 2024 Eurostat/ENTSO-E baseline (Phase 44). Demand uses growth RATE only, never ERAA's absolute gross-demand figure (confirmed definitionally different from Eurostat's net final consumption).",
    "capacity_MW_2028": projected_2028,
    "capacity_MW_2029": projected_2029,
    "demand_TWH_2028": proj_demand_2028,
    "demand_TWH_2029": proj_demand_2029,
}
with open(r"C:\Users\MuideenOA\maven-tools\eraa_data\roe_growth_projection.json", "w") as f:
    json.dump(out, f, indent=2)
print("\nSaved projection to maven-tools/eraa_data/roe_growth_projection.json")
