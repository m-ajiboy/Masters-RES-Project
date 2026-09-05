"""Builds the import mechanism for Germany2029 - reused COMPLETELY UNCHANGED from the
calibrated Germany2027 fixes, no re-tuning: the same flat 30,000 MW ceiling (Phase 8), and
the same 11-country equal-weighted real-2023 blended price proxy (Phase 15). 2029 is a normal
non-leap year, so the real-2023 source (also non-leap) maps directly, no adjustment needed."""
from pathlib import Path
import pandas as pd

ROOT = Path(__file__).parent
SRC = ROOT / "examples" / "backtest" / "Germany2023" / "timeseries"
OUT = ROOT / "examples" / "backtest" / "Germany2029" / "timeseries"
OUT.mkdir(parents=True, exist_ok=True)

YEAR = 2029
HOURS = 8760
CEILING_MW = 30000.0
ZONES = ["AT", "BE", "CH", "CZ", "DK_1", "DK_2", "FR", "NO_2", "NL", "PL", "SE_4"]


def main():
    prices = []
    for zone in ZONES:
        df = pd.read_csv(SRC / f"raw_price_{zone}_2023.csv", index_col=0)
        vals = df["value"].values[:HOURS]
        assert len(vals) == HOURS
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
