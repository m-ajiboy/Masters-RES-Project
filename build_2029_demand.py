"""Builds the demand components for Germany2029 - second out-of-sample validation build, no
re-tuning. 2029 is NOT a leap year, so this uses the ORIGINAL Germany2027-style handling of
the 2016 source (drop real Feb-29-2016, keep a clean 365-real-calendar-day mapping) rather
than Germany2028's drop-Dec-31 approach - FAME's 2029 is a normal Jan1-Dec31 calendar.

Weekday alignment: 2016-01-01 is a Friday; 2029-01-01 is a Monday. Shift = 3 days (72 hours).
"""
from pathlib import Path
import numpy as np
import pandas as pd
from demandlib import bdew

from brainpool_multiyear_data import ROOT, get_demand_components

HOURS = 8760
YEAR = 2029
SRC_2016_LOAD = ROOT / "examples" / "backtest" / "Germany2016" / "timeseries" / "load.csv"
RAW_2009_DIR = ROOT / "weather2009_raw"
REGIONS = ["north", "east", "middle", "southwest"]
OUT = ROOT / "examples" / "backtest" / "Germany2029" / "timeseries"
OUT.mkdir(parents=True, exist_ok=True)

WEEKDAY_SHIFT_HOURS = 3 * 24  # 2016-01-01 (Fri) -> 2016-01-04 (Mon) matches 2029-01-01 (Mon)


def build_inflexible_base_2029(target_twh):
    df = pd.read_csv(SRC_2016_LOAD, sep=";", header=None, names=["ts", "mw"])
    df["ts"] = pd.to_datetime(df["ts"], format="%Y-%m-%d_%H:%M:%S")
    df = df[(df["ts"] >= "2016-01-01") & (df["ts"] < "2017-01-01")]
    df = df[~((df["ts"].dt.month == 2) & (df["ts"].dt.day == 29))]  # drop leap day

    full_days = pd.date_range("2016-01-01", "2016-12-31").date
    full_days = [d for d in full_days if not (d.month == 2 and d.day == 29)]
    present_days = set(df["ts"].dt.date.unique())
    missing_days = [d for d in full_days if d not in present_days]
    if missing_days:
        print(f"  Filling {len(missing_days)} missing day(s) in the 2016 source data "
              f"(nearest-neighbour): {missing_days}")
        dec30 = df[df["ts"].dt.date == pd.Timestamp("2016-12-30").date()].copy()
        for missing_day in missing_days:
            fill = dec30.copy()
            fill["ts"] = fill["ts"].apply(lambda t: t.replace(year=missing_day.year, month=missing_day.month, day=missing_day.day))
            df = pd.concat([df, fill], ignore_index=True)
        df = df.sort_values("ts").reset_index(drop=True)

    raw = df["mw"].values[:HOURS]
    assert len(raw) == HOURS, f"expected {HOURS} hours, got {len(raw)}"

    shifted = np.roll(raw, -WEEKDAY_SHIFT_HOURS)
    shares = shifted / shifted.sum()
    target_mwh = target_twh * 1_000_000
    hourly_mwh = shares * target_mwh
    print(f"  Inflexible base (real 2016 data, Feb-29 dropped, shifted 3 days so weekdays "
          f"match 2029): rescaled to {target_twh:.2f} TWh (new peak {hourly_mwh.max():.0f} MW)")
    return hourly_mwh


def _load_2009_station_temp(region):
    df = pd.read_csv(RAW_2009_DIR / f"temperature_{region}_2009.csv", index_col=0, parse_dates=True)
    full_idx = pd.date_range("2009-01-01", periods=8760, freq="h")
    s = df["temp_c"].reindex(full_idx).astype(float).interpolate().ffill().bfill()
    return s.values


def build_heat_pumps_2029(target_twh):
    temps = [_load_2009_station_temp(r) for r in REGIONS]
    national_temp = np.mean(temps, axis=0)
    idx = pd.date_range(f"{YEAR}-01-01", periods=HOURS, freq="h")
    temp_series = pd.Series(national_temp, index=idx)

    house = bdew.HeatBuilding(
        idx,
        temperature=temp_series,
        shlp_type="EFH",
        building_class=1,
        wind_class=0,
        annual_heat_demand=target_twh * 1_000_000_000,
        ww_incl=True,
        name="heat_pumps_2029",
    )
    profile_kwh = house.get_bdew_profile()
    hourly_mwh = profile_kwh.values / 1000.0
    print(f"  Heat pumps (real 2009 temperature): mean {national_temp.mean():.1f} C, "
          f"scaled to {target_twh:.2f} TWh (peak {hourly_mwh.max():.0f} MW)")
    return hourly_mwh


def main():
    comp = get_demand_components(YEAR)
    print(f"Brainpool 2029 demand components (TWh): {comp}\n")

    print("Building demand WITHOUT electrolysis/e-mobility (handled by separate flex agents):")
    base = build_inflexible_base_2029(comp["inflexible"])
    heat = build_heat_pumps_2029(comp["heat_pumps"])

    combined_mwh = base + heat
    combined_total_twh = combined_mwh.sum() / 1_000_000
    remaining_target = comp["inflexible"] + comp["heat_pumps"]
    print(f"\nCombined total: {combined_total_twh:.4f} TWh (target: {remaining_target:.4f} TWh)")
    print(f"Electrolysis ({comp['electrolysis']:.4f} TWh) and e-mobility ({comp['e_mobility']:.4f} TWh) "
          f"handled by separate agents.")

    idx = pd.date_range(f"{YEAR}-01-01", periods=HOURS, freq="h")
    lines = [f"{ts.strftime('%Y-%m-%d_%H:%M:%S')};{val:.4f}" for ts, val in zip(idx, combined_mwh)]
    out_path = OUT / "load_2029_base.csv"
    out_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"\nSaved {out_path}")


if __name__ == "__main__":
    main()
