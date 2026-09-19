# -*- coding: utf-8 -*-
"""Rebuilds the 2027 inflexible-base demand component using real 2025 German load data
(fetched fresh via fetch_load_2011_2025.py) instead of the currently-used real 2016 data,
to test whether 2025 - a better real-temperature match to Brainpool's real 2009 weather
basis than 2016 (compare_candidate_years_to_2009_extended.py: monthly RMSE 2.11C vs
2.31C) - produces a better AMIRIS-vs-Brainpool result. Isolates demand-shape-year as the
ONLY variable: rescaled to the exact same real target TWh already used for 2027
(604.8502088984375, from build_combined_feb29fix.py), recombined with the SAME unchanged
real-2009-temperature heat-pump series, electrolysis/e-mobility/every other input left
completely untouched."""
from pathlib import Path
import numpy as np
import pandas as pd

from build_demand_feb29fix import build_heat_pumps

ROOT = Path(r"C:\Users\MuideenOA\Desktop\PyTut\Amiris")
RAW_2025_LOAD = ROOT / "weather2009_raw" / "load_2025_raw.csv"
HOURS = 8760
TARGET_INFLEXIBLE_TWH = 604.8502088984375
TARGET_HEATPUMP_TWH = 18.69330319775391


def build_inflexible_base_2025(target_twh):
    df = pd.read_csv(RAW_2025_LOAD, index_col=0, parse_dates=True)
    s = df.iloc[:, 0].astype(float)
    s = s[~s.index.duplicated(keep="first")]
    full_idx = pd.date_range("2025-01-01", periods=HOURS, freq="h")
    s = s.reindex(full_idx).interpolate().ffill().bfill()
    assert len(s) == HOURS, f"expected {HOURS} hours, got {len(s)}"
    assert s.isna().sum() == 0, f"{s.isna().sum()} unfilled NaN remain"

    # 2025-01-01 was a Wednesday, 2027-01-01 is a Friday - compute the real shift rather
    # than hardcode it, same principle as WEEKDAY_SHIFT_DAYS in build_demand_feb29fix.py.
    src_weekday = pd.Timestamp("2025-01-01").weekday()  # Monday=0 ... Sunday=6
    tgt_weekday = pd.Timestamp("2027-01-01").weekday()
    shift_days = (tgt_weekday - src_weekday) % 7
    print(f"  2025-01-01 weekday={src_weekday}, 2027-01-01 weekday={tgt_weekday}, "
          f"shift={shift_days}d")

    raw = s.values
    shifted = np.roll(raw, -shift_days * 24) if shift_days else raw
    shares = shifted / shifted.sum()
    hourly_mwh = shares * (target_twh * 1_000_000)
    print(f"  Inflexible base 2027 (real 2025 shape, shift={shift_days}d): "
          f"rescaled to {target_twh:.2f} TWh (peak {hourly_mwh.max():.0f} MW)")
    return hourly_mwh


def main():
    base = build_inflexible_base_2025(TARGET_INFLEXIBLE_TWH)
    heat = build_heat_pumps(2027, TARGET_HEATPUMP_TWH)
    combined = base + heat
    print(f"Combined total: {combined.sum() / 1e6:.4f} TWh "
          f"(target: {TARGET_INFLEXIBLE_TWH + TARGET_HEATPUMP_TWH:.4f} TWh)")

    OUT_DIR = ROOT / "examples" / "backtest" / "Germany2027_MarketCoupling_ROEFlex_Demand2025" / "timeseries"
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    idx = pd.date_range("2027-01-01", periods=HOURS, freq="h")
    lines = [f"{ts.strftime('%Y-%m-%d_%H:%M:%S')};{val:.4f}" for ts, val in zip(idx, combined)]
    out_path = OUT_DIR / "load_2027_demand2025shape.csv"
    out_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"Saved {out_path}")


if __name__ == "__main__":
    main()
