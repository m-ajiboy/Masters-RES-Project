"""Rebuilds the inflexible-base demand component for a given target year using the ORIGINAL
V2 recipe (real 2023 ENTSO-E load data, weekday-aligned - Phase 11's method) instead of the
2016-base source (Phase 17) - to isolate whether the demand-SOURCE-YEAR choice itself is
what's driving (or not driving) the out-of-sample correlation loss seen in Phase 24, separate
from the import-ceiling question tested in the sweep. Heat pumps (real 2009 temperature),
electrolysis and e-mobility (separate flex agents), the 30,000 MW import ceiling, and the
11-country blended import price are all reused UNCHANGED from the existing Germany202X
builds - only the inflexible-base demand source year changes.

2023 is a non-leap year (365 days, 8760 hours) - matching both FAME's representation of 2028
(8760h, Jan1-Dec30) and real 2029 (8760h) exactly, so no leap-year handling is needed at all
here, simpler than the 2016-source builds.
"""
import sys
from pathlib import Path
import numpy as np
import pandas as pd
from demandlib import bdew

from brainpool_multiyear_data import ROOT, get_demand_components

HOURS = 8760
SRC_2023_LOAD = ROOT / "examples" / "backtest" / "Germany2023" / "timeseries" / "load.csv"
RAW_2009_DIR = ROOT / "weather2009_raw"
REGIONS = ["north", "east", "middle", "southwest"]

# 2023-01-01 is a Sunday. Shift (in days) needed so weekdays match each target year's Jan 1.
WEEKDAY_SHIFT_DAYS = {2028: 6, 2029: 1}  # 2028-01-01=Sat, 2029-01-01=Mon


def build_inflexible_base_2023src(year, target_twh):
    df = pd.read_csv(SRC_2023_LOAD, sep=";", header=None, names=["ts", "mw"])
    raw = df["mw"].values[:HOURS]
    assert len(raw) == HOURS

    shift_hours = WEEKDAY_SHIFT_DAYS[year] * 24
    shifted = np.roll(raw, -shift_hours)
    shares = shifted / shifted.sum()
    target_mwh = target_twh * 1_000_000
    hourly_mwh = shares * target_mwh
    print(f"  Inflexible base (real 2023 ENTSO-E data, shifted {WEEKDAY_SHIFT_DAYS[year]} "
          f"day(s) so weekdays match {year}): rescaled to {target_twh:.2f} TWh "
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
        annual_heat_demand=target_twh * 1_000_000_000, ww_incl=True, name=f"heat_pumps_{year}",
    )
    hourly_mwh = house.get_bdew_profile().values / 1000.0
    print(f"  Heat pumps (real 2009 temperature): scaled to {target_twh:.2f} TWh "
          f"(peak {hourly_mwh.max():.0f} MW)")
    return hourly_mwh


def main(year):
    comp = get_demand_components(year)
    print(f"Brainpool {year} demand components (TWh): {comp}\n")

    base = build_inflexible_base_2023src(year, comp["inflexible"])
    heat = build_heat_pumps(year, comp["heat_pumps"])
    combined_mwh = base + heat
    combined_total_twh = combined_mwh.sum() / 1_000_000
    remaining_target = comp["inflexible"] + comp["heat_pumps"]
    print(f"\nCombined total: {combined_total_twh:.4f} TWh (target: {remaining_target:.4f} TWh)")

    OUT = ROOT / "examples" / "backtest" / f"Germany{year}_V2_2023Demand" / "timeseries"
    OUT.mkdir(parents=True, exist_ok=True)
    idx = pd.date_range(f"{year}-01-01", periods=HOURS, freq="h")
    lines = [f"{ts.strftime('%Y-%m-%d_%H:%M:%S')};{val:.4f}" for ts, val in zip(idx, combined_mwh)]
    out_path = OUT / f"load_{year}_v2_2023demand.csv"
    out_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"Saved {out_path}")


if __name__ == "__main__":
    main(int(sys.argv[1]))
