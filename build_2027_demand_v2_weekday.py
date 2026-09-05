"""Rebuilds V2's inflexible-base demand component with WEEKDAY-ALIGNED redating, instead
of the original positional mapping (hour 1 of 2023 -> hour 1 of 2027 regardless of actual
weekday). Everything else (heat pumps, electrolysis, e-mobility) is reused unchanged from
build_2027_demand_v2_split.py.

Motivation: the correlation breakdown (plot_correlation_breakdown.py) found weekday hours
have bias -22.78 EUR/MWh and weekend hours +16.18 EUR/MWh vs. Brainpool - a ~39 EUR/MWh
systematic gap - while correlation WITHIN each group is strong (0.64+), well above the
pooled 0.42-0.56. That pattern is consistent with the inflexible base's demand shape
landing on the wrong weekday of the 2027 calendar, since the original build never aligned
weekdays between the 2023 source year and the 2027 target year.

Method: 2023-01-01 was a Sunday; 2027-01-01 is a Friday. Shifting the 2023 source data by
5 days (120 hours) means 2023-01-06 (also a Friday) becomes the new starting point, so
every subsequent day's weekday matches the corresponding 2027 day exactly. The last ~5
days of the year wrap around to the start of the 2023 data (both years have 365 days, non-
leap) - this wraparound is off by one weekday for those ~5 days only (365 mod 7 = 1), a
tiny, documented residual imperfection affecting under 0.1% of the year.
"""
from pathlib import Path
import numpy as np
import pandas as pd

from build_2027_demand_v2_split import (
    ROOT, SRC_2023_LOAD, HOURS, YEAR,
    get_brainpool_demand_components, build_heat_pumps, build_electrolysis, build_e_mobility,
)

OUT = ROOT / "examples" / "backtest" / "Germany2027_DemandV2Weekday" / "timeseries"
OUT.mkdir(parents=True, exist_ok=True)

WEEKDAY_SHIFT_HOURS = 5 * 24  # 2023-01-01 (Sun) -> 2023-01-06 (Fri) matches 2027-01-01 (Fri)


def build_inflexible_base_weekday_aligned(target_twh):
    df = pd.read_csv(SRC_2023_LOAD, sep=";", header=None, names=["ts", "mw"])
    df = df.iloc[:HOURS].copy()
    raw = df["mw"].values
    shifted = np.roll(raw, -WEEKDAY_SHIFT_HOURS)  # circular shift so weekdays line up
    shares = shifted / shifted.sum()
    target_mwh = target_twh * 1_000_000
    hourly_mwh = shares * target_mwh
    print(f"  Inflexible base (weekday-aligned): rescaled real 2023 ENTSO-E shape, "
          f"shifted {WEEKDAY_SHIFT_HOURS} hours (5 days) so weekdays match the 2027 "
          f"calendar, to {target_twh:.2f} TWh (new peak {hourly_mwh.max():.0f} MW)")
    return hourly_mwh


def main():
    print("Brainpool demand components (TWh):")
    comp = get_brainpool_demand_components()
    total_target = sum(comp.values())
    print(f"  combined target: {total_target:.2f} TWh\n")

    print("Building each component:")
    base = build_inflexible_base_weekday_aligned(comp["inflexible"])
    heat = build_heat_pumps(comp["heat_pumps"])
    elec = build_electrolysis(comp["electrolysis"])
    ev = build_e_mobility(comp["e_mobility"])

    combined_mwh = base + heat + elec + ev
    combined_total_twh = combined_mwh.sum() / 1_000_000
    print(f"\nCombined total: {combined_total_twh:.4f} TWh (target: {total_target:.4f} TWh)")
    print(f"Combined peak: {combined_mwh.max():.1f} MW")

    idx = pd.date_range(f"{YEAR}-01-01", periods=HOURS, freq="h")
    lines = [f"{ts.strftime('%Y-%m-%d_%H:%M:%S')};{val:.4f}" for ts, val in zip(idx, combined_mwh)]
    out_path = OUT / "load_v2_weekday.csv"
    out_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"\nSaved {out_path}")


if __name__ == "__main__":
    main()
