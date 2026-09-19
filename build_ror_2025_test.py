# -*- coding: utf-8 -*-
"""Builds a run-of-river-only variant of the headline scenario, replacing AMIRIS's own
bundled run-of-river profile (mean CF 0.3450, source/vintage unclear - confirmed directly
NOT to match real ENTSO-E 2019 data, which has mean CF 0.4157) with the real 2025 ENTSO-E
generation-derived profile (mean CF 0.3767) - the most current complete real year
available (ENTSO-E generation data confirmed only covers 2019-2025 for this PSR type; no
"match Brainpool's 2009 weather basis" criterion applies to hydro, so "most current real
year" is the stated, defensible selection criterion here, not a temperature/weather match).
Isolates run-of-river as the ONLY variable versus the Phase 37 headline."""
from pathlib import Path
import pandas as pd

ROOT = Path(r"C:\Users\MuideenOA\Desktop\PyTut\Amiris")
RAW_DIR = ROOT / "weather2009_raw"
HOURS = 8760
YEAR = 2025
INSTALLED_CAPACITY_MW = 3923.0  # real ENTSO-E 2025 value, fetched alongside the generation data


def main():
    df = pd.read_csv(RAW_DIR / f"ror_generation_{YEAR}.csv", index_col=0, parse_dates=True)
    gen = df.iloc[:, 0].astype(float)
    gen = gen[~gen.index.duplicated(keep="first")]
    full_idx = pd.date_range(f"{YEAR}-01-01", periods=HOURS, freq="h")
    gen = gen.reindex(full_idx).interpolate().ffill().bfill()
    cf = (gen / INSTALLED_CAPACITY_MW).clip(upper=1.0)

    idx = pd.date_range("2027-01-01", periods=HOURS, freq="h")
    lines = [f"{ts.strftime('%Y-%m-%d_%H:%M:%S')};{val:.6f}" for ts, val in zip(idx, cf.values)]

    OUT_DIR = ROOT / "examples" / "backtest" / "Germany2027_MarketCoupling_ROEFlex_RunOfRiver2025" / "timeseries"
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    out_path = OUT_DIR / "run_of_river_profile.csv"
    out_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"Saved {out_path}: mean CF {cf.mean():.4f} (AMIRIS-default baseline: 0.3450)")


if __name__ == "__main__":
    main()
