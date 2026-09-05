"""Pulls real 2009 weather-year wind (onshore + offshore) and solar PV capacity factor data
for the Rest-of-Europe aggregate zone from renewables.ninja - one representative coordinate
per country (mirroring the same per-point regional approach already used for Germany's own
2009 profiles, fetch_2009_renewables_ninja.py), then blends them into capacity-weighted
Rest-of-Europe profiles per technology using the real Eurostat capacity figures (Phase 33) as
weights. 2009 chosen for consistency with this project's own established real weather-basis
year (Brainpool's own confirmed methodology, Phase 9/15) - not an arbitrary choice.

Offshore wind is only fetched for the 5 countries with real, non-zero offshore capacity in
the Eurostat data (BE, DK, FR, NL, SE) - AT, CZ, NO, PL all show 0 MW offshore in the real
2023 snapshot.
"""
import os
import time
import json
import requests
import pandas as pd

TOKEN_FILE = r"C:\Users\MuideenOA\Desktop\PyTut\Amiris\Token.txt"
OUT_DIR = r"C:\Users\MuideenOA\Desktop\PyTut\Amiris\examples\backtest\RestOfEurope2023\raw_renewables_ninja"
os.makedirs(OUT_DIR, exist_ok=True)

with open(TOKEN_FILE, encoding="utf-8") as f:
    lines = [l.strip() for l in f if l.strip()]
token = lines[lines.index("Renewable Ninja Token") + 1]

session = requests.Session()
session.headers = {"Authorization": f"Token {token}"}
API_BASE = "https://www.renewables.ninja/api/data"

# One representative onshore/solar point per country (simplification, consistent with this
# being an aggregate zone - not a per-region split the way Germany's own build used).
COUNTRY_POINTS = {
    "AT": (47.8, 16.5),   # Burgenland (Austria's real wind belt)
    "BE": (50.85, 4.35),  # Brussels area
    "CZ": (50.08, 14.43), # Prague area
    "DK": (56.0, 10.0),   # central Denmark
    "FR": (47.0, 2.0),    # central France
    "NO": (60.0, 8.0),    # southern Norway
    "NL": (52.3, 5.5),    # central Netherlands
    "PL": (52.0, 19.0),   # central Poland
    "SE": (59.0, 15.0),   # south-central Sweden
}
OFFSHORE_COUNTRIES = ["BE", "DK", "FR", "NL", "SE"]
OFFSHORE_POINTS = {
    "BE": (51.6, 2.8), "DK": (55.5, 7.7), "FR": (49.9, 2.0),
    "NL": (52.6, 4.0), "SE": (56.2, 15.5),
}

DATE_FROM, DATE_TO = "2009-01-01", "2009-12-31"


def fetch(url, params, out_name):
    out_path = os.path.join(OUT_DIR, out_name)
    if os.path.exists(out_path):
        print(f"  already have {out_name}, skipping")
        return
    r = session.get(url, params=params)
    if r.status_code != 200:
        print(f"  FAILED {out_name}: {r.status_code} {r.text[:200]}")
        return
    payload = r.json()
    df = pd.DataFrame.from_dict(payload["data"], orient="index")
    df.index = pd.to_datetime(df.index.astype("int64"), unit="ms")
    df.to_csv(out_path)
    print(f"  saved {out_name} ({len(df)} rows)")
    time.sleep(1.2)


print("Fetching onshore wind (2009), one point per country...")
for country, (lat, lon) in COUNTRY_POINTS.items():
    fetch(f"{API_BASE}/wind",
          {"lat": lat, "lon": lon, "date_from": DATE_FROM, "date_to": DATE_TO,
           "capacity": 1, "dataset": "merra2", "height": 100,
           "turbine": "Vestas V80 2000", "format": "json"},
          f"wind_onshore_{country}_2009.csv")

print("\nFetching offshore wind (2009), 5 countries with real offshore capacity...")
for country in OFFSHORE_COUNTRIES:
    lat, lon = OFFSHORE_POINTS[country]
    fetch(f"{API_BASE}/wind",
          {"lat": lat, "lon": lon, "date_from": DATE_FROM, "date_to": DATE_TO,
           "capacity": 1, "dataset": "merra2", "height": 100,
           "turbine": "Vestas V164 8000", "format": "json"},
          f"wind_offshore_{country}_2009.csv")

print("\nFetching solar PV (2009), one point per country...")
for country, (lat, lon) in COUNTRY_POINTS.items():
    fetch(f"{API_BASE}/pv",
          {"lat": lat, "lon": lon, "date_from": DATE_FROM, "date_to": DATE_TO,
           "capacity": 1, "dataset": "merra2", "system_loss": 0.1,
           "tracking": 0, "tilt": 35, "azim": 180, "format": "json"},
          f"solar_{country}_2009.csv")

print("\nDone.")
