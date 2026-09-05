# -*- coding: utf-8 -*-
"""
Pulls real 2009 hourly air temperature data for Germany from DWD's (German Weather
Service) public Climate Data Center - free, no login/token required, unlike ENTSO-E or
renewables.ninja. Used to rebuild V2's heat-pump demand component with real 2009 weather
instead of the generic "Test Reference Year" (TRY) typical-year climate data it currently
uses - completing the Weather2009 experiment for the one demand component that IS
genuinely weather-driven (the other components: inflexible base is real-2023-shaped,
electrolysis is flat, e-mobility is an assumed shape - none of those are affected by a
weather-year choice).

Same 4-region approach already used for the wind/solar 2009 pull (renewables.ninja), for
methodological consistency - picked the real DWD station closest to each of those same
target coordinates.
"""
import io
import os
import zipfile
import requests
import pandas as pd

OUT_DIR = r"C:\Users\MuideenOA\Desktop\PyTut\Amiris\weather2009_raw"
os.makedirs(OUT_DIR, exist_ok=True)

BASE_URL = "https://opendata.dwd.de/climate_environment/CDC/observations_germany/climate/hourly/air_temperature/historical/"

# station_id -> (region label, filename) - found by matching the same target coordinates
# used for the wind/solar 2009 pull against DWD's real station list.
STATIONS = {
    "04857": "north",       # Mittelnkirchen-Hohenfelde, 53.55N 9.61E
    "00420": "east",        # Berlin-Marzahn, 52.54N 13.56E
    "03527": "middle",      # Neukirchen-Hauptschwenda, 50.89N 9.41E
    "05562": "southwest",   # Neubulach-Oberhaugstett, 48.65N 8.68E
}


def find_filename(station_id):
    r = requests.get(BASE_URL, timeout=30)
    for line in r.text.splitlines():
        if f"_TU_{station_id}_" in line and ".zip" in line:
            start = line.index('href="') + 6
            end = line.index('"', start)
            return line[start:end]
    raise RuntimeError(f"No file found for station {station_id}")


def fetch_station(station_id, region):
    out_path = os.path.join(OUT_DIR, f"temperature_{region}_2009.csv")
    if os.path.exists(out_path):
        print(f"  already have {region} ({station_id}), skipping")
        return

    fname = find_filename(station_id)
    print(f"  {region} ({station_id}): downloading {fname}")
    r = requests.get(BASE_URL + fname, timeout=60)
    r.raise_for_status()

    with zipfile.ZipFile(io.BytesIO(r.content)) as z:
        product_file = [n for n in z.namelist() if n.startswith("produkt_tu_stunde")][0]
        with z.open(product_file) as f:
            df = pd.read_csv(f, sep=";", encoding="latin1")

    df.columns = [c.strip() for c in df.columns]
    df["ts"] = pd.to_datetime(df["MESS_DATUM"], format="%Y%m%d%H")
    df = df[(df["ts"] >= "2009-01-01") & (df["ts"] < "2010-01-01")]
    df = df[["ts", "TT_TU"]].rename(columns={"TT_TU": "temp_c"})
    df["temp_c"] = df["temp_c"].replace(-999, pd.NA)  # DWD's missing-value code
    df = df.set_index("ts").sort_index()
    df["temp_c"] = df["temp_c"].interpolate()  # fill any small data gaps

    df.to_csv(out_path)
    print(f"    saved {out_path} ({len(df)} rows, mean {df['temp_c'].mean():.1f} C)")


def main():
    print("Fetching real 2009 hourly temperature data from DWD (free, no login):")
    for station_id, region in STATIONS.items():
        fetch_station(station_id, region)
    print("\nDone.")


if __name__ == "__main__":
    main()
