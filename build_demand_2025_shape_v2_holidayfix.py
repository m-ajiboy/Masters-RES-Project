# -*- coding: utf-8 -*-
"""Fixes a real, general gap in this project's weekday-shift redating technique (used
since Phase 17), exposed by the 2025-shape crash: a fixed day-of-week shift correctly
aligns ordinary weekdays, but does NOT check whether the shift also happens to move a
real target-year public holiday onto a real ORDINARY working day in the source year. For
the 2025->2027 shift (+2 days), this is confirmed to happen for ALL FIVE of Germany's
2027 weekday national holidays (Neujahr, Karfreitag, Ostermontag, Christi Himmelfahrt,
Pfingstmontag) - none of their shifted source dates are real 2025 holidays. The most
severe case, Neujahr (2027-01-01, day-of-year index 0, no prior simulation history to
smooth into it), is what crashed AMIRIS's storage dispatch optimiser.

Fix: for exactly these 5 real target holidays, replace the mechanically-shifted day's 24
hourly values with the REAL 2025 date of the SAME named holiday (e.g. real 2025-01-01
Neujahr for target 2027-01-01 Neujahr), preserving the real holiday demand character
instead of an ordinary-workday one. Every other day of the year keeps the same pure
mechanical weekday-shift already used for the (crashing) v1 build. This is the same
"borrow the most contextually appropriate real reference point" principle already used
elsewhere in this project (e.g. reusing Germany's own real storage technology
characteristics for the Rest-of-Europe zone, Phase 37)."""
from pathlib import Path
import holidays
import numpy as np
import pandas as pd

from build_demand_feb29fix import build_heat_pumps

ROOT = Path(r"C:\Users\MuideenOA\Desktop\PyTut\Amiris")
RAW_2025_LOAD = ROOT / "weather2009_raw" / "load_2025_raw.csv"
HOURS = 8760
TARGET_INFLEXIBLE_TWH = 604.8502088984375
TARGET_HEATPUMP_TWH = 18.69330319775391
SHIFT_DAYS = 2  # 2025-01-01 Wed -> 2027-01-01 Fri

HOLIDAY_NAME_MAP = {
    # 2027 weekday holiday -> real 2025 date of the same named holiday
    "2027-01-01": "2025-01-01",   # Neujahr
    "2027-03-26": "2025-04-18",   # Karfreitag
    "2027-03-29": "2025-04-21",   # Ostermontag
    "2027-05-06": "2025-05-29",   # Christi Himmelfahrt
    "2027-05-17": "2025-06-09",   # Pfingstmontag
}


def load_real_2025_series():
    df = pd.read_csv(RAW_2025_LOAD, index_col=0, parse_dates=True)
    s = df.iloc[:, 0].astype(float)
    s = s[~s.index.duplicated(keep="first")]
    full_idx = pd.date_range("2025-01-01", periods=HOURS, freq="h")
    s = s.reindex(full_idx).interpolate().ffill().bfill()
    assert s.isna().sum() == 0
    return s


def build_inflexible_base_2025_holidayfix(target_twh):
    s = load_real_2025_series()
    raw = s.values
    shifted = np.roll(raw, -SHIFT_DAYS * 24)

    jan1_2027 = pd.Timestamp("2027-01-01")
    n_fixed = 0
    for tgt_str, src_str in HOLIDAY_NAME_MAP.items():
        tgt_date = pd.Timestamp(tgt_str)
        doy = (tgt_date - jan1_2027).days  # 0-indexed day-of-year in the target array
        src_date = pd.Timestamp(src_str)
        real_holiday_hours = s.loc[src_date:src_date + pd.Timedelta(hours=23)].values
        assert len(real_holiday_hours) == 24, f"expected 24 real hours for {src_str}, got {len(real_holiday_hours)}"
        before = shifted[doy * 24:(doy + 1) * 24].copy()
        shifted[doy * 24:(doy + 1) * 24] = real_holiday_hours
        print(f"  Holiday fix: target {tgt_str} (day-of-year {doy}) now uses real {src_str} "
              f"(mean {real_holiday_hours.mean():.0f} MW, was mean {before.mean():.0f} MW "
              f"from the mechanically-shifted ordinary weekday)")
        n_fixed += 1
    print(f"  {n_fixed} of 5 real 2027 weekday holidays corrected")

    shares = shifted / shifted.sum()
    hourly_mwh = shares * (target_twh * 1_000_000)
    print(f"  Inflexible base 2027 (real 2025 shape, holiday-fixed, shift={SHIFT_DAYS}d): "
          f"rescaled to {target_twh:.2f} TWh (peak {hourly_mwh.max():.0f} MW)")
    return hourly_mwh


def main():
    base = build_inflexible_base_2025_holidayfix(TARGET_INFLEXIBLE_TWH)
    heat = build_heat_pumps(2027, TARGET_HEATPUMP_TWH)
    combined = base + heat
    print(f"Combined total: {combined.sum() / 1e6:.4f} TWh "
          f"(target: {TARGET_INFLEXIBLE_TWH + TARGET_HEATPUMP_TWH:.4f} TWh)")
    print(f"Max hour-to-hour jump in first 48h: "
          f"{pd.Series(combined[:48]).diff().abs().max():.0f} MW "
          f"(was 5610 MW before the fix; original 2016-shape build: 4660 MW)")

    OUT_DIR = ROOT / "examples" / "backtest" / "Germany2027_MarketCoupling_ROEFlex_Demand2025" / "timeseries"
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    idx = pd.date_range("2027-01-01", periods=HOURS, freq="h")
    lines = [f"{ts.strftime('%Y-%m-%d_%H:%M:%S')};{val:.4f}" for ts, val in zip(idx, combined)]
    out_path = OUT_DIR / "load_2027_demand2025shape_holidayfix.csv"
    out_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"Saved {out_path}")


if __name__ == "__main__":
    main()
