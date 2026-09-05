"""
Extract a single-column real day-ahead price series from one SMARD.de export
(for years with no mid-year bidding-zone split, e.g. 2015-2017 and 2019+).

For 2015-2017: use --column "DE/AT/LU [EUR/MWh] Calculated resolutions"
For 2019+:     use --column "Germany/Luxembourg [EUR/MWh] Calculated resolutions"
(Note: the actual header uses the Euro sign; pass exactly what's in your file's
header row if this default doesn't match - see printed columns on error.)

Usage:
    python extract_smard_prices.py --input "Data\\Real Day Ahead Prices\\Day Ahead Prices 2015\\<file>.csv" ^
        --column "DE/AT/LU [EUR/MWh] Calculated resolutions" --output germany_2015_real_prices.csv
"""
import argparse
from pathlib import Path

import pandas as pd

START_COL = "Start date"


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True)
    parser.add_argument("--column", required=True, help="Exact column header to extract")
    parser.add_argument("--output", required=True)
    args = parser.parse_args()

    df = pd.read_csv(Path(args.input), sep=";", na_values=["-"])
    if args.column not in df.columns:
        print("Column not found. Available columns:")
        for c in df.columns:
            print(f"  {c!r}")
        raise SystemExit(1)

    timestamps = pd.to_datetime(df[START_COL], format="%b %d, %Y %I:%M %p")
    prices = pd.to_numeric(df[args.column], errors="coerce")
    series = pd.Series(prices.values, index=timestamps, name="price_eur_mwh").dropna()
    series = series[~series.index.duplicated(keep="first")]
    series.index.name = "Timestamp"

    gap_hours = pd.date_range(series.index.min(), series.index.max(), freq="h").difference(series.index)
    print(f"Rows: {len(series)}  [{series.index.min()} .. {series.index.max()}]")
    print(f"Missing hours in range: {len(gap_hours)}")
    if len(gap_hours) > 0:
        print(gap_hours[:10])

    series.to_csv(args.output)
    print(f"Saved: {args.output}")


if __name__ == "__main__":
    main()
