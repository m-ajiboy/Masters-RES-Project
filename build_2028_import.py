"""Builds the import mechanism for Germany2028 - reused COMPLETELY UNCHANGED from the
calibrated Germany2027 fixes, no re-tuning: the same flat 30,000 MW ceiling (Phase 8), and
the same 11-country equal-weighted real-2023 blended price proxy (Phase 15).

CORRECTED from an earlier version: AMIRIS's FAME framework represents every year as exactly
365 days/8760 hours (even leap years - Dec 31 is omitted, see build_2028_timeseries.py's
docstring for the full explanation). The real 2023 source data is itself a normal non-leap
365-day/8760-hour year, so it maps directly and positionally onto FAME's 2028 calendar with
no adjustment needed at all - simpler than originally thought."""
from pathlib import Path
import numpy as np
import pandas as pd

ROOT = Path(__file__).parent
SRC = ROOT / "examples" / "backtest" / "Germany2023" / "timeseries"
OUT = ROOT / "examples" / "backtest" / "Germany2028" / "timeseries"
OUT.mkdir(parents=True, exist_ok=True)

YEAR = 2028
HOURS = 8760
CEILING_MW = 30000.0
ZONES = ["AT", "BE", "CH", "CZ", "DK_1", "DK_2", "FR", "NO_2", "NL", "PL", "SE_4"]


def main():
    prices = []
    for zone in ZONES:
        df = pd.read_csv(SRC / f"raw_price_{zone}_2023.csv", index_col=0)
        vals = df["value"].values[:HOURS]
        assert len(vals) == HOURS, f"{zone}: expected {HOURS} hours, got {len(vals)}"
        prices.append(vals)
    blended = sum(prices) / len(prices)
    print(f"Blended 2023 price across {len(ZONES)} real neighbouring zones: "
          f"mean={blended.mean():.2f}, min={blended.min():.2f}, max={blended.max():.2f}")

    idx = pd.date_range(f"{YEAR}-01-01", periods=HOURS, freq="h")
    price_lines = [f"{ts.strftime('%Y-%m-%d_%H:%M:%S')};{v:.4f}" for ts, v in zip(idx, blended)]
    (OUT / "ImportCostInEURperMWH.csv").write_text("\n".join(price_lines) + "\n", encoding="utf-8")
    print(f"  saved {OUT / 'ImportCostInEURperMWH.csv'}")

    ceiling_lines = [f"{ts.strftime('%Y-%m-%d_%H:%M:%S')};{CEILING_MW:.4f}" for ts in idx]
    (OUT / "AvailableEnergyForImport.csv").write_text("\n".join(ceiling_lines) + "\n", encoding="utf-8")
    print(f"  saved {OUT / 'AvailableEnergyForImport.csv'} (flat {CEILING_MW:.0f} MW, unchanged from Phase 8)")


if __name__ == "__main__":
    main()
