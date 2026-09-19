# -*- coding: utf-8 -*-
"""Extends Phase 17's real DWD temperature pull (fetch_candidate_years_temperature.py,
which covered 2015-2019 and 2023) to the remaining candidate demand-source years not yet
tested: 2010-2014 and 2020-2025 (2026 excluded - the real year is not yet complete, so no
full real hourly record exists to pull). Same 4 stations, same source, same method -
extending the search rather than replacing it. Only fetches years not already present in
weather2009_raw."""
import io
import os
import zipfile
import requests
import pandas as pd

OUT_DIR = r"C:\Users\MuideenOA\Desktop\PyTut\Amiris\weather2009_raw"
os.makedirs(OUT_DIR, exist_ok=True)

BASE_URL = "https://opendata.dwd.de/climate_environment/CDC/observations_germany/climate/hourly/air_temperature/historical/"

STATIONS = {
    "04857": "north",
    "00420": "east",
    "03527": "middle",
    "05562": "southwest",
}

YEARS = [2010, 2011, 2012, 2013, 2014, 2020, 2021, 2022, 2024, 2025]


def find_filename(station_id):
    r = requests.get(BASE_URL, timeout=30)
    for line in r.text.splitlines():
        if f"_TU_{station_id}_" in line and ".zip" in line:
            start = line.index('href="') + 6
            end = line.index('"', start)
            return line[start:end]
    raise RuntimeError(f"No file found for station {station_id}")


_cache = {}


def fetch_station_full(station_id):
    if station_id in _cache:
        return _cache[station_id]
    fname = find_filename(station_id)
    print(f"  downloading {fname}")
    r = requests.get(BASE_URL + fname, timeout=60)
    r.raise_for_status()
    with zipfile.ZipFile(io.BytesIO(r.content)) as z:
        product_file = [n for n in z.namelist() if n.startswith("produkt_tu_stunde")][0]
        with z.open(product_file) as f:
            df = pd.read_csv(f, sep=";", encoding="latin1")
    df.columns = [c.strip() for c in df.columns]
    df["ts"] = pd.to_datetime(df["MESS_DATUM"], format="%Y%m%d%H")
    df = df[["ts", "TT_TU"]].rename(columns={"TT_TU": "temp_c"})
    df["temp_c"] = df["temp_c"].replace(-999, pd.NA)
    df = df.set_index("ts").sort_index()
    _cache[station_id] = df
    return df


def main():
    for station_id, region in STATIONS.items():
        print(f"Fetching full history for {region} ({station_id}):")
        full = fetch_station_full(station_id)
        print(f"    real record covers {full.index.min()} to {full.index.max()}")
        for year in YEARS:
            out_path = os.path.join(OUT_DIR, f"temperature_{region}_{year}.csv")
            if os.path.exists(out_path):
                print(f"    {out_path} already exists, skipping")
                continue
            year_data = full[(full.index >= f"{year}-01-01") & (full.index < f"{year+1}-01-01")]
            if len(year_data) == 0:
                print(f"    WARNING: no real data at all for {year} at this station - "
                      f"station record may not extend that far, or (for recent years) "
                      f"the 'historical' dataset may not have been updated yet (check "
                      f"the 'recent' DWD folder as a fallback if this happens)")
                continue
            full_idx = pd.date_range(f"{year}-01-01", end=f"{year}-12-31 23:00", freq="h")
            s = year_data["temp_c"].reindex(full_idx).interpolate().ffill().bfill()
            s.to_csv(out_path)
            print(f"    saved {out_path} ({len(s)} rows, mean {s.mean():.1f} C, "
                  f"{s.isna().sum()} still-NaN after fill)")


if __name__ == "__main__":
    main()
