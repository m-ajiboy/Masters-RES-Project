"""BUG FIX: rebuilds the inflexible-base demand component for 2027 and 2029, correcting a
real weekday-alignment bug found by re-running the granular breakdown on the out-of-sample
years. Phase 17's method dropped Feb 29 from the leap-year 2016 source to get a clean 365-day
series for non-leap target years - but Feb 29 sits in the MIDDLE of the year, so removing it
creates a 2-real-day gap between Feb 28 and Mar 1, silently shifting every day from March 1
onward (84% of the year) one weekday off from its intended target. Verified directly: source
array position 59 (meant to represent 2027-03-01, a Monday) actually contained real
2016-03-01 data - a Tuesday.

2028's build accidentally avoided this bug entirely by dropping Dec 31 instead (to satisfy a
different, unrelated FAME leap-year requirement) - Dec 31 sits at the END of the array, so
removing it shortens the tail without creating any mid-year discontinuity. This fix applies
that same, already-proven technique to 2027 and 2029: drop Dec 31 instead of Feb 29.

Since dropping Dec 31 doesn't touch the array's start, the existing weekday shifts (derived
purely from each target year's Jan-1 weekday) remain correct: 0 days for 2027 (both
2016-01-01 and 2027-01-01 are Fridays), 3 days for 2029 (2016-01-01 Fri -> 2016-01-04 Mon
matches 2029-01-01 Mon).
"""
from pathlib import Path
import numpy as np
import pandas as pd
from demandlib import bdew

ROOT = Path(r"C:\Users\MuideenOA\Desktop\PyTut\Amiris")
SRC_2016_LOAD = ROOT / "examples" / "backtest" / "Germany2016" / "timeseries" / "load.csv"
RAW_2009_DIR = ROOT / "weather2009_raw"
REGIONS = ["north", "east", "middle", "southwest"]
HOURS = 8760

WEEKDAY_SHIFT_DAYS = {2027: 0, 2029: 3}


def build_inflexible_base_fixed(year, target_twh):
    df = pd.read_csv(SRC_2016_LOAD, sep=";", header=None, names=["ts", "mw"])
    df["ts"] = pd.to_datetime(df["ts"], format="%Y-%m-%d_%H:%M:%S")
    df = df[(df["ts"] >= "2016-01-01") & (df["ts"] < "2017-01-01")]

    # Fill the pre-existing Dec-31-2016 gap in AMIRIS's own file FIRST (nearest-neighbour,
    # copy of Dec 30), same as every other build - then drop Dec 31 (not Feb 29) to get a
    # clean, gap-free 365-day Jan1-Dec30 real-calendar sequence.
    full_days = pd.date_range("2016-01-01", "2016-12-31").date
    present_days = set(df["ts"].dt.date.unique())
    missing_days = [d for d in full_days if d not in present_days]
    if missing_days:
        dec30 = df[df["ts"].dt.date == pd.Timestamp("2016-12-30").date()].copy()
        for missing_day in missing_days:
            fill = dec30.copy()
            fill["ts"] = fill["ts"].apply(lambda t: t.replace(year=missing_day.year, month=missing_day.month, day=missing_day.day))
            df = pd.concat([df, fill], ignore_index=True)
        df = df.sort_values("ts").reset_index(drop=True)

    raw = df["mw"].values[:HOURS]  # truncate to first 8760 hours = Jan1-Dec30 2016, drops only Dec31
    assert len(raw) == HOURS, f"expected {HOURS} hours, got {len(raw)}"

    shift_days = WEEKDAY_SHIFT_DAYS[year]
    shifted = np.roll(raw, -shift_days * 24) if shift_days else raw
    shares = shifted / shifted.sum()
    hourly_mwh = shares * (target_twh * 1_000_000)
    print(f"  [FIXED] Inflexible base {year} (real 2016 data, Dec-31 dropped instead of "
          f"Feb-29, shift={shift_days}d): rescaled to {target_twh:.2f} TWh "
          f"(peak {hourly_mwh.max():.0f} MW)")
    return hourly_mwh


def _load_2009_station_temp(region):
    df = pd.read_csv(RAW_2009_DIR / f"temperature_{region}_2009.csv", index_col=0, parse_dates=True)
    full_idx = pd.date_range("2009-01-01", periods=8760, freq="h")
    s = df["temp_c"].reindex(full_idx).astype(float).interpolate().ffill().bfill()
    return s.values


def build_heat_pumps(year, target_twh):
    temps = [_load_2009_station_temp(r) for r in REGIONS]
    national_temp = np.mean(temps, axis=0)
    idx = pd.date_range(f"{year}-01-01", periods=HOURS, freq="h")
    temp_series = pd.Series(national_temp, index=idx)
    house = bdew.HeatBuilding(
        idx, temperature=temp_series, shlp_type="EFH", building_class=1, wind_class=0,
        annual_heat_demand=target_twh * 1_000_000_000, ww_incl=True, name=f"heat_pumps_{year}_fixed",
    )
    hourly_mwh = house.get_bdew_profile().values / 1000.0
    print(f"  Heat pumps {year} (real 2009 temperature): scaled to {target_twh:.2f} TWh "
          f"(peak {hourly_mwh.max():.0f} MW)")
    return hourly_mwh
