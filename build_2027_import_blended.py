"""Builds a BLENDED multi-country import price proxy - an equal-weighted average of real
2023 day-ahead prices across all 11 of Germany's real physical neighbouring bidding zones
(fetch_2023_neighbor_prices.py) - replacing the single-country (France-only) proxy used
until now.

Documented simplification: equal-weighted average, not a true capacity-weighted or
iterative market-coupling blend the way Brainpool's own Power2Sim model actually computes
cross-border prices (confirmed: EU27 + UK + Norway + Switzerland, iterative price
equalisation via interconnector capacity). A full replication of that is out of scope
(the same conclusion reached with the export-sink experiment) - this is a closer
approximation than a single country, not a full match.

The import CEILING (flat MW, calibrated separately per demand version) is unchanged - only
the PRICE series changes here.
"""
from pathlib import Path
import pandas as pd

ROOT = Path(__file__).parent
SRC = ROOT / "examples" / "backtest" / "Germany2023" / "timeseries"

YEAR = 2027
HOURS = 8760

ZONES = ["AT", "BE", "CH", "CZ", "DK_1", "DK_2", "FR", "NO_2", "NL", "PL", "SE_4"]


def build_blended_price():
    prices = []
    for zone in ZONES:
        df = pd.read_csv(SRC / f"raw_price_{zone}_2023.csv", index_col=0)
        prices.append(df["value"].values[:HOURS])
    blended = sum(prices) / len(prices)
    print(f"Blended 2023 price across {len(ZONES)} real neighbouring zones: "
          f"mean={blended.mean():.2f}, min={blended.min():.2f}, max={blended.max():.2f}")
    for zone, p in zip(ZONES, prices):
        print(f"  {zone}: mean={p.mean():.2f}")
    return blended


def write_price(values, out_dir):
    out_dir.mkdir(parents=True, exist_ok=True)
    idx = pd.date_range(f"{YEAR}-01-01", periods=HOURS, freq="h")
    lines = [f"{ts.strftime('%Y-%m-%d_%H:%M:%S')};{v:.4f}" for ts, v in zip(idx, values)]
    (out_dir / "ImportCostInEURperMWH.csv").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"  saved {out_dir / 'ImportCostInEURperMWH.csv'}")


def main():
    blended = build_blended_price()
    for scenario_name in ["Germany2027_ImportBlended"]:
        out_dir = ROOT / "examples" / "backtest" / scenario_name / "timeseries"
        write_price(blended, out_dir)


if __name__ == "__main__":
    main()
