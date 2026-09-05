"""Rebuilds V2's heat-pump demand component using REAL 2009 hourly temperature data from
DWD (fetch_2009_dwd_temperature.py), averaged across the same 4 representative regions
used for the wind/solar 2009 pull, instead of the generic "Test Reference Year" (TRY)
typical-year climate data the original build used.

Everything else (inflexible base, electrolysis, e-mobility) is reused unchanged from the
weekday-aligned V2 build (build_2027_demand_v2_weekday.py) - this build layers the real-
2009-temperature heat pump on top of the current best demand baseline.
"""
from pathlib import Path
import numpy as np
import pandas as pd
from demandlib import bdew

from build_2027_demand_v2_split import ROOT, HOURS, YEAR, get_brainpool_demand_components
from build_2027_demand_v2_weekday import build_inflexible_base_weekday_aligned
from build_2027_demand_v2_split import build_electrolysis, build_e_mobility

RAW_DIR = ROOT / "weather2009_raw"
OUT = ROOT / "examples" / "backtest" / "Germany2027_HeatPump2009" / "timeseries"
OUT.mkdir(parents=True, exist_ok=True)

REGIONS = ["north", "east", "middle", "southwest"]


def load_station_temp(region):
    df = pd.read_csv(RAW_DIR / f"temperature_{region}_2009.csv", index_col=0, parse_dates=True)
    full_idx = pd.date_range("2009-01-01", periods=HOURS, freq="h")
    s = df["temp_c"].reindex(full_idx).interpolate().ffill().bfill()
    return s.values


def build_heat_pumps_real_2009(target_twh):
    temps = [load_station_temp(r) for r in REGIONS]
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
        name="heat_pumps_2009",
    )
    profile_kwh = house.get_bdew_profile()
    hourly_mwh = profile_kwh.values / 1000.0
    print(f"  Heat pumps (REAL 2009 temperature): mean {national_temp.mean():.1f} C, "
          f"min {national_temp.min():.1f} C, max {national_temp.max():.1f} C, "
          f"scaled to {target_twh:.2f} TWh (peak {hourly_mwh.max():.0f} MW)")
    return hourly_mwh


def main():
    comp = get_brainpool_demand_components()
    total_target = sum(comp.values())

    print("Building demand with real-2009-temperature heat pumps (all other components unchanged):")
    base = build_inflexible_base_weekday_aligned(comp["inflexible"])
    heat = build_heat_pumps_real_2009(comp["heat_pumps"])
    elec = build_electrolysis(comp["electrolysis"])
    ev = build_e_mobility(comp["e_mobility"])

    combined_mwh = base + heat + elec + ev
    combined_total_twh = combined_mwh.sum() / 1_000_000
    print(f"\nCombined total: {combined_total_twh:.4f} TWh (target: {total_target:.4f} TWh)")
    print(f"Combined peak: {combined_mwh.max():.1f} MW")

    idx = pd.date_range(f"{YEAR}-01-01", periods=HOURS, freq="h")
    lines = [f"{ts.strftime('%Y-%m-%d_%H:%M:%S')};{val:.4f}" for ts, val in zip(idx, combined_mwh)]
    out_path = OUT / "load_v2_heatpump2009.csv"
    out_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"\nSaved {out_path}")


if __name__ == "__main__":
    main()
