# -*- coding: utf-8 -*-
"""
Pulls real 2023 day-ahead prices for all of DE_LU's actual physical neighbouring bidding
zones from ENTSO-E, to build a BLENDED multi-country import price proxy - replacing the
single-country (France-only) proxy used until now.

Motivation: verified directly (Montel/Energy Brainpool's own published description of their
Power2Sim model) that Brainpool's real forecast covers the EU27, UK, Norway, and
Switzerland, iteratively equalising prices across all of them via cross-border capacity -
not a single neighbouring country. A single-country (France) proxy was always a known
simplification; this builds a closer (still simplified - equal-weighted, not the real
capacity-weighted iterative coupling Brainpool actually runs) approximation using all 11 of
Germany's real physical neighbours.
"""
import os
import pandas as pd
from entsoe import EntsoePandasClient

TOKEN_FILE = r"C:\Users\MuideenOA\Desktop\PyTut\Amiris\Token.txt"
OUT_DIR = r"C:\Users\MuideenOA\Desktop\PyTut\Amiris\examples\backtest\Germany2023\timeseries"
os.makedirs(OUT_DIR, exist_ok=True)

with open(TOKEN_FILE, encoding="utf-8") as f:
    lines = [l.strip() for l in f if l.strip()]
token = lines[lines.index("Entso Token") + 1]

client = EntsoePandasClient(api_key=token)

START = pd.Timestamp("2023-01-01", tz="UTC")
END = pd.Timestamp("2024-01-01", tz="UTC")

# Same 11 real physical neighbouring zones used for the cross-border flow pull earlier
# this project (entsoe.mappings.NEIGHBOURS['DE_LU']).
ZONES = ["AT", "BE", "CH", "CZ", "DK_1", "DK_2", "FR", "NO_2", "NL", "PL", "SE_4"]


def save_series(series, path):
    s = series.copy()
    s.index = s.index.tz_localize(None)
    s = s[~s.index.duplicated(keep="first")].sort_index()
    s = s.resample("h").mean()
    if s.isna().any():
        s = s.interpolate(method="linear")
    s.to_csv(path, header=["value"])
    print(f"  saved {path} ({len(s)} rows, mean {s.mean():.2f})")


print("Fetching real 2023 day-ahead prices for all 11 of DE_LU's real neighbouring zones:")
for zone in ZONES:
    out_path = os.path.join(OUT_DIR, f"raw_price_{zone}_2023.csv")
    if os.path.exists(out_path):
        print(f"  already have {zone}, skipping")
        continue
    try:
        price = client.query_day_ahead_prices(zone, start=START, end=END)
        save_series(price, out_path)
    except Exception as e:
        print(f"  FAILED for {zone}: {e}")

print("\nDone.")
