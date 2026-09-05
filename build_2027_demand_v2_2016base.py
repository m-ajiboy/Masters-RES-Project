"""Rebuilds V2's inflexible-base demand component using REAL 2016 German load data instead
of 2023 - real 2016 weather was found to be the closest match to 2009 (Brainpool's real
weather-year basis) of any year we have real demand data for, and 2023 (used until now) was
found to be the WORST match of the six candidates checked (see
compare_candidate_years_to_2009.py). 2016 is also a "normal" pre-COVID, pre-energy-crisis
year structurally, unlike 2023.

A genuine bonus: 2016-01-01 and 2027-01-01 are BOTH Fridays, so - unlike the 2023 source,
which needed a 5-day shift to align weekdays - no weekday shift is needed at all here. 2016
is a leap year (366 days); Feb 29 is dropped to give a clean 365-day source series.

Heat pumps (real 2009 temperature), electrolysis, and e-mobility are reused unchanged from
the existing best build.
"""
from pathlib import Path
import numpy as np
import pandas as pd

from build_2027_demand_v2_split import ROOT, HOURS, YEAR, get_brainpool_demand_components
from build_2027_heatpump_2009temp import build_heat_pumps_real_2009
from build_2027_demand_v2_split import build_electrolysis, build_e_mobility

SRC_2016_LOAD = ROOT / "examples" / "backtest" / "Germany2016" / "timeseries" / "load.csv"
OUT = ROOT / "examples" / "backtest" / "Germany2027_Demand2016Base" / "timeseries"
OUT.mkdir(parents=True, exist_ok=True)


def build_inflexible_base_2016(target_twh):
    df = pd.read_csv(SRC_2016_LOAD, sep=";", header=None, names=["ts", "mw"])
    df["ts"] = pd.to_datetime(df["ts"], format="%Y-%m-%d_%H:%M:%S")
    df = df[(df["ts"] >= "2016-01-01") & (df["ts"] < "2017-01-01")]
    df = df[~((df["ts"].dt.month == 2) & (df["ts"].dt.day == 29))]  # drop leap day

    # AMIRIS's own Germany2016 example file has a pre-existing gap: Dec 31 2016 is
    # entirely missing (confirmed by inspecting the file directly - not introduced here).
    # Filled with a copy of Dec 30 2016 (nearest-neighbour day) - one day out of 365,
    # a minor, documented simplification.
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
    assert len(raw) == HOURS, f"expected {HOURS} hours after cleanup, got {len(raw)}"

    # No weekday shift needed - both 2016-01-01 and 2027-01-01 are Fridays.
    shares = raw / raw.sum()
    target_mwh = target_twh * 1_000_000
    hourly_mwh = shares * target_mwh
    print(f"  Inflexible base (real 2016 data, no shift needed - both years start on a "
          f"Friday): rescaled to {target_twh:.2f} TWh (new peak {hourly_mwh.max():.0f} MW)")
    return hourly_mwh


def main():
    comp = get_brainpool_demand_components()
    total_target = sum(comp.values())

    print("Building demand with real 2016 inflexible-base data (closest weather match to 2009):")
    base = build_inflexible_base_2016(comp["inflexible"])
    heat = build_heat_pumps_real_2009(comp["heat_pumps"])
    elec = build_electrolysis(comp["electrolysis"])
    ev = build_e_mobility(comp["e_mobility"])

    combined_mwh = base + heat + elec + ev
    combined_total_twh = combined_mwh.sum() / 1_000_000
    print(f"\nCombined total: {combined_total_twh:.4f} TWh (target: {total_target:.4f} TWh)")
    print(f"Combined peak: {combined_mwh.max():.1f} MW")

    idx = pd.date_range(f"{YEAR}-01-01", periods=HOURS, freq="h")
    lines = [f"{ts.strftime('%Y-%m-%d_%H:%M:%S')};{val:.4f}" for ts, val in zip(idx, combined_mwh)]
    out_path = OUT / "load_v2_2016base.csv"
    out_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"\nSaved {out_path}")


if __name__ == "__main__":
    main()
