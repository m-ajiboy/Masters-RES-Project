# -*- coding: utf-8 -*-
"""Fetches real German (DE/DE-LU) hourly actual total load for 2011 and 2025, the two
new candidate demand-shape-source years identified by the extended temperature-matching
search (compare_candidate_years_to_2009_extended.py) as better real-weather matches to
2009 than 2016 (the year currently used in the headline scenario). Uses the same
entsoe-py library and token already used for this project's 2023 pull
(fetch_entsoe_2023_data.py); token file is untouched/unmodified, only read."""
import os
import pandas as pd
from entsoe import EntsoePandasClient

TOKEN_FILE = r"C:\Users\MuideenOA\Desktop\PyTut\Amiris\Token.txt"
OUT_DIR = r"C:\Users\MuideenOA\Desktop\PyTut\Amiris\weather2009_raw"
os.makedirs(OUT_DIR, exist_ok=True)

with open(TOKEN_FILE, encoding="utf-8") as f:
    lines = [line.strip() for line in f]
entso_idx = next(i for i, l in enumerate(lines) if "entso" in l.lower())
token = next(l for l in lines[entso_idx + 1:] if l)

client = EntsoePandasClient(api_key=token)


def fetch_year(year, country_code="DE_LU"):
    start = pd.Timestamp(f"{year}-01-01", tz="UTC")
    end = pd.Timestamp(f"{year + 1}-01-01", tz="UTC")
    print(f"Fetching {year} actual load for {country_code}...")
    try:
        s = client.query_load(country_code, start=start, end=end)
    except Exception as e:
        print(f"  FAILED for {country_code}: {e}")
        return None
    if isinstance(s, pd.DataFrame):
        s = s.iloc[:, 0]
    s.index = s.index.tz_localize(None)
    s = s[~s.index.duplicated(keep="first")].sort_index()
    s = s.resample("h").mean()
    out_path = os.path.join(OUT_DIR, f"load_{year}_raw.csv")
    s.to_csv(out_path)
    print(f"  saved {out_path}: {len(s)} rows, {s.isna().sum()} NaN, "
          f"range {s.index.min()} to {s.index.max()}, mean {s.mean():.0f} MW")
    return s


if __name__ == "__main__":
    fetch_year(2025)
    print()
    # 2011 predates DE_LU as a distinct bidding zone (Luxembourg split later); try DE_LU
    # first since entsoe-py may transparently redirect, fall back to plain "DE" if not.
    result_2011 = fetch_year(2011, "DE_LU")
    if result_2011 is None:
        print("Retrying 2011 with plain 'DE' country code...")
        fetch_year(2011, "DE")
