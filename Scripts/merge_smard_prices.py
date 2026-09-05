"""
Merge the two SMARD.de day-ahead price exports for Germany 2018 into one
continuous hourly series, bridging the DE-AT-LU -> DE-LU bidding zone split
that happened on 2018-10-01.

Input files (SMARD "Day-ahead prices" export, hourly resolution):
    Jan-Oct file: uses the 'DE/AT/LU' column (real values before the split)
    Oct-Dec file: uses the 'Germany/Luxembourg' column (real values after the split)

Output:
    germany_2018_real_prices.csv with columns: Timestamp, price_eur_mwh
"""
import argparse
from pathlib import Path

import pandas as pd

DE_AT_LU_COL = "DE/AT/LU [€/MWh] Calculated resolutions"
DE_LU_COL = "Germany/Luxembourg [€/MWh] Calculated resolutions"
START_COL = "Start date"


def load_smard_csv(path: Path, price_col: str) -> pd.Series:
    df = pd.read_csv(path, sep=";", na_values=["-"])
    timestamps = pd.to_datetime(df[START_COL], format="%b %d, %Y %I:%M %p")
    prices = pd.to_numeric(df[price_col], errors="coerce")
    series = pd.Series(prices.values, index=timestamps, name="price_eur_mwh")
    return series.dropna()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--pre-split",
        default=r"Data\Real Day Ahead Prices\Day Ahead Prices 2018\Day-ahead_prices_201801010000_201810010000_Hour.csv",
        help="Jan-Oct 2018 SMARD export (uses DE/AT/LU column)",
    )
    parser.add_argument(
        "--post-split",
        default=r"Data\Real Day Ahead Prices\Day Ahead Prices 2018\Day-ahead_prices_201810010000_201901010000_Hour.csv",
        help="Oct-Dec 2018 SMARD export (uses Germany/Luxembourg column)",
    )
    parser.add_argument("--output", default="germany_2018_real_prices.csv")
    args = parser.parse_args()

    pre = load_smard_csv(Path(args.pre_split), DE_AT_LU_COL)
    post = load_smard_csv(Path(args.post_split), DE_LU_COL)

    merged = pd.concat([pre, post]).sort_index()
    merged.index.name = "Timestamp"

    duplicates = merged.index.duplicated().sum()
    gap_hours = pd.date_range(merged.index.min(), merged.index.max(), freq="h").difference(merged.index)

    print(f"Pre-split rows (Jan-Sep):  {len(pre)}  [{pre.index.min()} .. {pre.index.max()}]")
    print(f"Post-split rows (Oct-Dec): {len(post)}  [{post.index.min()} .. {post.index.max()}]")
    print(f"Merged rows: {len(merged)}")
    print(f"Duplicate timestamps: {duplicates}")
    print(f"Missing hours in range: {len(gap_hours)}")
    if len(gap_hours) > 0:
        print(gap_hours[:10])

    merged.to_csv(args.output)
    print(f"\nSaved merged series to {args.output}")


if __name__ == "__main__":
    main()
