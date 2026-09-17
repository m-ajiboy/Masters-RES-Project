"""Exploratory: quantifies real ERAA 2024 capacity/demand growth for the 9 ROE countries
(2026->2028->2030, Final data version) against this project's current frozen ROE figures
(Phase 44, real 2024 Eurostat snapshot), before committing to a full rebuild."""
import pandas as pd

CAP_PATH = r"C:\Users\MuideenOA\maven-tools\eraa_data\Dashboard_raw data\GenerationCapacities.xlsx"
DEM_PATH = r"C:\Users\MuideenOA\maven-tools\eraa_data\Dashboard_raw data\Aggregated_Demand.xlsx"

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

# --- Capacity ---
cap = pd.read_excel(CAP_PATH, sheet_name="data")
cap = cap[cap["DATA_VERSION"] == "Final"]
cap["COUNTRY"] = cap["MARKET_NODE"].map(NODE_TO_COUNTRY)
cap = cap.dropna(subset=["COUNTRY"])
cap["CATEGORY"] = cap["TECHNOLOGY"].map(TECH_MAP)
mapped = cap.dropna(subset=["CATEGORY"])
unmapped = cap[cap["CATEGORY"].isna()]

print("=" * 70)
print("Technologies present but NOT mapped to a category (real, just not used by this project's existing categories):")
print(sorted(unmapped["TECHNOLOGY"].unique()))
print(f"Unmapped capacity total 2028: {unmapped[unmapped.TARGET_YEAR==2028]['CAPACITY_MW'].sum():,.0f} MW (mostly DSR/batteries/electrolysers - not generation capacity in the sense this project models)")

cap_totals = mapped.groupby(["COUNTRY", "TARGET_YEAR", "CATEGORY"])["CAPACITY_MW"].sum().reset_index()
pivot = cap_totals.groupby(["TARGET_YEAR", "CATEGORY"])["CAPACITY_MW"].sum().unstack()
print("\n" + "=" * 70)
print("REAL ERAA capacity totals, 9 ROE countries, by year and category (MW):")
print("=" * 70)
print(pivot.round(0))

print("\n" + "=" * 70)
print("Grand total installed capacity, 9 countries, by year:")
print(pivot.sum(axis=1).round(0))

# --- Compare 2028 real ERAA total vs. this project's current frozen (2024 Eurostat) total ---
CURRENT_FROZEN_TOTAL_MW = 456513  # Phase 44, real 2024 Eurostat, 9 countries
eraa_2028_total = pivot.loc[2028].sum()
eraa_2026_total = pivot.loc[2026].sum()
print(f"\nCurrent frozen ROE total (2024 Eurostat, used unchanged for 2027/2028/2029): {CURRENT_FROZEN_TOTAL_MW:,.0f} MW")
print(f"Real ERAA 2026 total: {eraa_2026_total:,.0f} MW")
print(f"Real ERAA 2028 total: {eraa_2028_total:,.0f} MW")
print(f"Implied growth 2024(frozen)->2028(real): {eraa_2028_total - CURRENT_FROZEN_TOTAL_MW:+,.0f} MW "
      f"({100*(eraa_2028_total/CURRENT_FROZEN_TOTAL_MW - 1):+.1f}%)")

# --- Demand ---
dem = pd.read_excel(DEM_PATH, sheet_name="Export")
dem = dem[(dem["DATA_VERSION"] == "Final") & (dem["TYPE_WS"] == "Avg")]
dem["COUNTRY"] = dem["MARKET_NODE"].map(NODE_TO_COUNTRY)
dem = dem.dropna(subset=["COUNTRY"])
dem_totals = dem.groupby(["COUNTRY", "TARGET_YEAR"])["DEMAND_TWH"].sum().reset_index()
dem_pivot = dem_totals.groupby("TARGET_YEAR")["DEMAND_TWH"].sum()
print("\n" + "=" * 70)
print("REAL ERAA demand totals, 9 ROE countries, by year (TWh):")
print("=" * 70)
print(dem_pivot.round(1))
CURRENT_FROZEN_DEMAND_TWH = 1158.143  # Phase 44, real 2024 Eurostat
print(f"\nCurrent frozen ROE demand (2024 Eurostat): {CURRENT_FROZEN_DEMAND_TWH:.1f} TWh")
print(f"Real ERAA 2028 demand: {dem_pivot.loc[2028]:.1f} TWh "
      f"({100*(dem_pivot.loc[2028]/CURRENT_FROZEN_DEMAND_TWH - 1):+.1f}% vs. frozen)")

pivot.to_csv(r"C:\Users\MuideenOA\maven-tools\eraa_data\roe9_capacity_by_year_category.csv")
dem_pivot.to_csv(r"C:\Users\MuideenOA\maven-tools\eraa_data\roe9_demand_by_year.csv")
print("\nSaved intermediate CSVs to maven-tools/eraa_data/")
