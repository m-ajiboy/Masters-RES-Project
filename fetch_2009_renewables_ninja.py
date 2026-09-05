# -*- coding: utf-8 -*-
"""
Pulls real 2009 weather-year wind (onshore + offshore) and solar PV capacity factor data
for Germany from the renewables.ninja API, for the "Weather2009" experiment: testing
whether aligning AMIRIS's renewable weather-year with Brainpool's own (reportedly 2009)
weather basis improves correlation with Brainpool's real 2027 price forecast.

Method: renewables.ninja's documented API works per-location (lat/lon + date range), not
as a single "whole of Germany" call with guaranteed year flexibility - so this pulls a
handful of representative coordinates spread across Germany (mirroring Brainpool's own
north/east/middle/southwest regional split used for their solar/wind columns) and averages
them into one national profile per technology, the same regional-averaging approach already
used elsewhere in this build.

Run-of-river is NOT included - renewables.ninja has no hydro data at all (confirmed by
checking their documentation this session).
"""
import os
import time
import requests
import pandas as pd

TOKEN_FILE = r"C:\Users\MuideenOA\Desktop\PyTut\Amiris\Token.txt"
OUT_DIR = r"C:\Users\MuideenOA\Desktop\PyTut\Amiris\weather2009_raw"
os.makedirs(OUT_DIR, exist_ok=True)

with open(TOKEN_FILE, encoding="utf-8") as f:
    lines = [l.strip() for l in f if l.strip()]
token = lines[lines.index("Renewable Ninja Token") + 1]

session = requests.Session()
session.headers = {"Authorization": f"Token {token}"}
API_BASE = "https://www.renewables.ninja/api/data"

# Representative onshore points, mirroring Brainpool's own north/east/middle/southwest split
ONSHORE_POINTS = {
    "north": (53.5, 9.5),      # Schleswig-Holstein
    "east": (52.5, 13.5),      # Brandenburg
    "middle": (50.9, 9.5),     # Hesse
    "southwest": (48.5, 8.8),  # Baden-Wurttemberg
}
# Real German offshore wind zones
OFFSHORE_POINTS = {
    "north_sea": (54.5, 6.5),   # German Bight
    "baltic_sea": (54.6, 13.2), # near Ruegen
}

DATE_FROM, DATE_TO = "2009-01-01", "2009-12-31"


def fetch(url, params, out_name):
    out_path = os.path.join(OUT_DIR, out_name)
    if os.path.exists(out_path):
        print(f"  already have {out_name}, skipping")
        return
    r = session.get(url, params=params)
    r.raise_for_status()
    payload = r.json()
    df = pd.DataFrame.from_dict(payload["data"], orient="index")
    df.index = pd.to_datetime(df.index.astype("int64"), unit="ms")
    df.to_csv(out_path)
    print(f"  saved {out_name} ({len(df)} rows)")
    time.sleep(1.2)  # stay under the 1 request/second burst limit


print("Fetching onshore wind (2009)...")
for region, (lat, lon) in ONSHORE_POINTS.items():
    fetch(f"{API_BASE}/wind",
          {"lat": lat, "lon": lon, "date_from": DATE_FROM, "date_to": DATE_TO,
           "capacity": 1, "dataset": "merra2", "height": 100,
           "turbine": "Vestas V80 2000", "format": "json"},
          f"wind_onshore_{region}_2009.csv")

print("\nFetching offshore wind (2009)...")
for region, (lat, lon) in OFFSHORE_POINTS.items():
    fetch(f"{API_BASE}/wind",
          {"lat": lat, "lon": lon, "date_from": DATE_FROM, "date_to": DATE_TO,
           "capacity": 1, "dataset": "merra2", "height": 100,
           "turbine": "Vestas V164 8000", "format": "json"},
          f"wind_offshore_{region}_2009.csv")

print("\nFetching solar PV (2009)...")
for region, (lat, lon) in ONSHORE_POINTS.items():
    fetch(f"{API_BASE}/pv",
          {"lat": lat, "lon": lon, "date_from": DATE_FROM, "date_to": DATE_TO,
           "capacity": 1, "dataset": "merra2", "system_loss": 0.1,
           "tracking": 0, "tilt": 35, "azim": 180, "format": "json"},
          f"solar_{region}_2009.csv")

print("\nDone.")
