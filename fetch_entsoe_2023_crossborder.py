# -*- coding: utf-8 -*-
"""
Pulls real 2023 cross-border data for the Germany2027 "with-import" scenario
variant, via the ENTSO-E Transparency Platform:

  1. Total physical imports INTO DE_LU, hourly (all neighbouring zones summed)
  2. Total physical exports FROM DE_LU, hourly (all neighbouring zones summed)
  3. French day-ahead price, hourly - used as the import cost proxy. France is
     Germany's largest and most stable single interconnector partner (large,
     steady nuclear baseload); using its real price series is a documented
     simplification standing in for a full flow-weighted mix of all 11 of
     DE_LU's neighbouring zones (AT, BE, CH, CZ, DK_1, DK_2, FR, NO_2, NL, PL,
     SE_4), which would require a full multi-zone MarketCoupling setup.

Net physical flow = imports - exports. Only the hours where this is positive
(Germany a net importer that hour) are usable by AMIRIS's ImportTrader, since
it can only add supply, not remove/absorb it (there is no ExportTrader agent
type for a single, uncoupled market zone) - so the real 2023 shape is clipped
at zero before being rescaled to Brainpool's 2027 target.
"""
import os
import pandas as pd
from entsoe import EntsoePandasClient

TOKEN_FILE = r"C:\Users\MuideenOA\Desktop\PyTut\Amiris\Entso Token.txt"
OUT_DIR = r"C:\Users\MuideenOA\Desktop\PyTut\Amiris\examples\backtest\Germany2023\timeseries"
os.makedirs(OUT_DIR, exist_ok=True)

with open(TOKEN_FILE, encoding="utf-8") as f:
    token = [line.strip() for line in f if line.strip()][-1]

client = EntsoePandasClient(api_key=token)

START = pd.Timestamp("2023-01-01", tz="UTC")
END = pd.Timestamp("2024-01-01", tz="UTC")


def save_series(series, path):
    s = series.copy()
    s.index = s.index.tz_localize(None)
    s = s[~s.index.duplicated(keep="first")].sort_index()
    s = s.resample("h").mean()
    if s.isna().any():
        s = s.interpolate(method="linear")
    s.to_csv(path, header=["value"])
    print(f"Saved {path} ({len(s)} rows)")


print("Fetching DE_LU total imports (all borders)...")
imports = client.query_physical_crossborder_allborders(
    "DE_LU", start=START, end=END, export=False, per_hour=True
)
imports_total = imports.sum(axis=1) if isinstance(imports, pd.DataFrame) else imports
save_series(imports_total, os.path.join(OUT_DIR, "raw_imports_total_2023.csv"))

print("Fetching DE_LU total exports (all borders)...")
exports = client.query_physical_crossborder_allborders(
    "DE_LU", start=START, end=END, export=True, per_hour=True
)
exports_total = exports.sum(axis=1) if isinstance(exports, pd.DataFrame) else exports
save_series(exports_total, os.path.join(OUT_DIR, "raw_exports_total_2023.csv"))

print("Fetching FR day-ahead price...")
fr_price = client.query_day_ahead_prices("FR", start=START, end=END)
save_series(fr_price, os.path.join(OUT_DIR, "raw_fr_price_2023.csv"))

print("\nDone.")
