# -*- coding: utf-8 -*-
"""Fetches real German hourly run-of-river generation (ENTSO-E, PSR B11) for every year
the API actually has data for (confirmed directly: 2015-2018 return NoMatchingDataError,
2019-2025 work), converts to a 0-1 capacity-factor profile using each year's own real
installed run-of-river capacity (also fetched, not assumed constant). No "match Brainpool's
2009 weather basis" criterion applies here - unlike solar/wind-onshore, Brainpool's own
documented methodology says nothing about a specific weather-year basis for hydro, so this
is an open, exploratory multi-year comparison rather than a matching exercise."""
import os
import pandas as pd
from entsoe import EntsoePandasClient

TOKEN_FILE = r"C:\Users\MuideenOA\Desktop\PyTut\Amiris\Token.txt"
OUT_DIR = r"C:\Users\MuideenOA\Desktop\PyTut\Amiris\weather2009_raw"
os.makedirs(OUT_DIR, exist_ok=True)

with open(TOKEN_FILE, encoding="utf-8") as f:
    lines = [l.strip() for l in f]
entso_idx = next(i for i, l in enumerate(lines) if "entso" in l.lower())
token = next(l for l in lines[entso_idx + 1:] if l)

client = EntsoePandasClient(api_key=token)
YEARS = [2019, 2020, 2021, 2022, 2023, 2024, 2025]


def fetch_year(year):
    start = pd.Timestamp(f"{year}-01-01", tz="UTC")
    end = pd.Timestamp(f"{year + 1}-01-01", tz="UTC")
    print(f"Fetching {year} run-of-river generation + installed capacity...")
    gen = client.query_generation("DE_LU", start=start, end=end, psr_type="B11")
    if isinstance(gen, pd.DataFrame):
        gen = gen.iloc[:, 0]
    gen.index = gen.index.tz_localize(None)
    gen = gen[~gen.index.duplicated(keep="first")].sort_index()
    gen = gen.resample("h").mean()

    cap = client.query_installed_generation_capacity(
        "DE_LU", start=start, end=end, psr_type="B11")
    cap_mw = float(cap.iloc[0, 0]) if hasattr(cap, "iloc") else float(cap)

    out_path = os.path.join(OUT_DIR, f"ror_generation_{year}.csv")
    gen.to_csv(out_path)
    print(f"  saved {out_path}: {len(gen)} rows, {gen.isna().sum()} NaN, "
          f"real installed capacity {cap_mw:.1f} MW, mean generation {gen.mean():.0f} MW "
          f"(implied mean CF {gen.mean()/cap_mw:.4f})")
    return gen, cap_mw


if __name__ == "__main__":
    results = {}
    for year in YEARS:
        try:
            results[year] = fetch_year(year)
        except Exception as e:
            print(f"  FAILED for {year}: {type(e).__name__}: {e}")
    print("\nDone.", len(results), "of", len(YEARS), "years fetched successfully.")
