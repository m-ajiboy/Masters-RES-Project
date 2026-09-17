"""2024-base variant of fetch_eurostat_restofeurope.py. Brainpool is understood to use 2024
as its real base year for the export/market-coupling scenarios (per supervisor/project info),
while this project's existing Rest-of-Europe build (Phase 33-38) used 2023. Live-checked
before building this: Eurostat's nrg_cb_e/nrg_inf_epc both return real, non-empty 2024 values
for DE/FR/wind-onshore capacity (confirmed 2026-09-17) - so this is a real data refresh, not a
guess. Same 10 countries, same two datasets, same fallback logic - only the target year and
output folder change (RestOfEurope2024, kept fully separate from RestOfEurope2023)."""
import requests
import json

COUNTRIES = ["AT", "BE", "CH", "CZ", "DK", "FR", "NO", "NL", "PL", "SE"]
YEARS_TRY = ["2024", "2023", "2022"]

OUT_DIR = r"C:\Users\MuideenOA\Desktop\PyTut\Amiris\examples\backtest\RestOfEurope2024\raw_eurostat"
import os
os.makedirs(OUT_DIR, exist_ok=True)


def fetch_demand(country):
    url = "https://ec.europa.eu/eurostat/api/dissemination/statistics/1.0/data/nrg_cb_e"
    for year in YEARS_TRY:
        params = {"format": "JSON", "lang": "EN", "freq": "A", "geo": country, "unit": "GWH",
                   "nrg_bal": "FC", "time": year}
        r = requests.get(url, params=params, timeout=30)
        if r.status_code != 200:
            continue
        d = r.json()
        vals = list(d.get("value", {}).values())
        if vals:
            return year, vals[0]
    return None, None


CAPACITY_TECHS = {
    "C0000": "Coal_and_manufactured_gases",
    "G3000": "Natural_gas",
    "O4000": "Oil",
    "N9000": "Nuclear",
    "RA100": "Hydro_total",
    "RA310": "Wind_onshore",
    "RA320": "Wind_offshore",
    "RA420": "Solar_PV",
    "R5000_W6000": "Biofuels_and_waste",
}


def fetch_capacity_one_tech(country, siec, year):
    url = "https://ec.europa.eu/eurostat/api/dissemination/statistics/1.0/data/nrg_inf_epc"
    params = {"format": "JSON", "lang": "EN", "freq": "A", "geo": country, "unit": "MW",
              "plant_tec": "CAP_NET_ELC", "operator": "TOTAL", "siec": siec, "time": year}
    r = requests.get(url, params=params, timeout=30)
    if r.status_code != 200:
        return None
    d = r.json()
    vals = list(d.get("value", {}).values())
    return vals[0] if vals else None


def fetch_capacity(country):
    for year in YEARS_TRY:
        row = {}
        got_any = False
        for siec, label in CAPACITY_TECHS.items():
            v = fetch_capacity_one_tech(country, siec, year)
            row[label] = v
            if v is not None:
                got_any = True
        if got_any:
            return year, row
    return None, {}


print("=" * 70)
print("DEMAND (annual final electricity consumption, GWh) - 2024 base")
print("=" * 70)
demand_results = {}
for c in COUNTRIES:
    year, val = fetch_demand(c)
    demand_results[c] = (year, val)
    print(f"{c}: year={year}, demand={val}")

with open(os.path.join(OUT_DIR, "demand_annual_GWh.json"), "w") as f:
    json.dump(demand_results, f, indent=2)

print()
print("=" * 70)
print("CAPACITY (installed MW by technology) - 2024 base")
print("=" * 70)
capacity_results = {}
for c in COUNTRIES:
    year, row = fetch_capacity(c)
    capacity_results[c] = {"year": year, **row}
    print(f"{c} (year={year}): {row}")

with open(os.path.join(OUT_DIR, "capacity_MW_by_tech.json"), "w") as f:
    json.dump(capacity_results, f, indent=2)
print(f"\nSaved to {OUT_DIR}")
