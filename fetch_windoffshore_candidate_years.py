# -*- coding: utf-8 -*-
"""Extends the Phase 9 renewables.ninja wind-offshore pull (real 2009 only, at the same
2 representative German offshore points - North Sea German Bight, Baltic Sea near Ruegen)
to a broader real-year sweep (2010-2025), to check whether some other real weather year
matches Brainpool's own real 2009 weather basis more closely than 2009 does to itself
(trivially perfect) -- more usefully, to check which other real years are CLOSE seconds,
since wind-offshore in the current headline build isn't matched to any particular year at
all (it's just AMIRIS's own bundled 2019-example default). Same MERRA-2 dataset, same
turbine model, same rate-limit discipline as the original 2009 pull."""
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

OFFSHORE_POINTS = {
    "north_sea": (54.5, 6.5),
    "baltic_sea": (54.6, 13.2),
}

YEARS = [2010, 2011, 2012, 2013, 2014, 2015, 2016, 2017, 2018, 2019,
         2020, 2021, 2022, 2023, 2024, 2025]


def fetch(url, params, out_name):
    out_path = os.path.join(OUT_DIR, out_name)
    if os.path.exists(out_path):
        print(f"  already have {out_name}, skipping")
        return True
    r = session.get(url, params=params)
    if r.status_code == 429:
        print(f"  RATE LIMITED on {out_name} - waiting 60s and retrying once")
        time.sleep(60)
        r = session.get(url, params=params)
    try:
        r.raise_for_status()
    except Exception as e:
        print(f"  FAILED {out_name}: {e} -- body: {r.text[:300]}")
        return False
    payload = r.json()
    df = pd.DataFrame.from_dict(payload["data"], orient="index")
    df.index = pd.to_datetime(df.index.astype("int64"), unit="ms")
    df.to_csv(out_path)
    print(f"  saved {out_name} ({len(df)} rows, mean CF {df.iloc[:,0].mean():.4f})")
    time.sleep(1.5)
    return True


for year in YEARS:
    print(f"Fetching offshore wind {year}...")
    for region, (lat, lon) in OFFSHORE_POINTS.items():
        fetch(f"{API_BASE}/wind",
              {"lat": lat, "lon": lon, "date_from": f"{year}-01-01", "date_to": f"{year}-12-31",
               "capacity": 1, "dataset": "merra2", "height": 100,
               "turbine": "Vestas V164 8000", "format": "json"},
              f"wind_offshore_{region}_{year}.csv")

print("\nDone.")
