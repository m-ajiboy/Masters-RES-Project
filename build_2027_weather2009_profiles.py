"""Builds AMIRIS-formatted 2027 renewable profiles from the real 2009 weather-year data
pulled from renewables.ninja (fetch_2009_renewables_ninja.py), for the "Weather2009"
experiment: does aligning the renewable weather-year with Brainpool's own (reportedly
2009-based) weather assumption improve correlation with Brainpool's real 2027 price?

Averages the regional points into one national profile per technology (mirroring
Brainpool's own regional-averaging approach), then redates the 2009 calendar onto 2027
(both are non-leap years, 365 days, so this is a clean 1:1 hour-of-year mapping - no
Feb 29 edge case to handle).

Run-of-river is NOT rebuilt - renewables.ninja has no hydro data at all, confirmed by
checking their documentation. It stays as AMIRIS's own reused profile in this variant.

Solar uses the SAME averaged shape for both openfield and rooftop (the underlying weather-
driven irradiance pattern is identical; Brainpool's own split is a capacity/technology
distinction, not a different weather basis) - a documented simplification.
"""
from pathlib import Path
import pandas as pd

ROOT = Path(__file__).parent
RAW_DIR = ROOT / "weather2009_raw"
OUT_DIR = ROOT / "examples" / "backtest" / "Germany2027_Weather2009" / "timeseries"
OUT_DIR.mkdir(parents=True, exist_ok=True)

YEAR = 2027
HOURS = 8760

ONSHORE_REGIONS = ["north", "east", "middle", "southwest"]
OFFSHORE_REGIONS = ["north_sea", "baltic_sea"]
SOLAR_REGIONS = ["north", "east", "middle", "southwest"]


def load_raw(name):
    df = pd.read_csv(RAW_DIR / f"{name}_2009.csv", index_col=0)
    return df["electricity"].values[:HOURS]


def average(names, prefix):
    arrs = [load_raw(f"{prefix}_{n}") for n in names]
    return sum(arrs) / len(arrs)


def write_profile(values, out_name, label):
    idx = pd.date_range(f"{YEAR}-01-01", periods=HOURS, freq="h")
    lines = [f"{ts.strftime('%Y-%m-%d_%H:%M:%S')};{v:.6f}" for ts, v in zip(idx, values)]
    (OUT_DIR / out_name).write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"  {label}: saved {out_name} (mean capacity factor {values.mean():.3f})")


def main():
    print("Building Weather2009 renewable profiles (real 2009 weather, redated to 2027):")

    wind_onshore = average(ONSHORE_REGIONS, "wind_onshore")
    write_profile(wind_onshore, "wind_onshore_profile.csv", "Wind onshore")

    wind_offshore = average(OFFSHORE_REGIONS, "wind_offshore")
    write_profile(wind_offshore, "wind_offshore_profile.csv", "Wind offshore")

    solar = average(SOLAR_REGIONS, "solar")
    write_profile(solar, "solar_openfield_profile.csv", "Solar (openfield)")
    write_profile(solar, "solar_rooftop_profile.csv", "Solar (rooftop, same shape)")

    print("\nRun-of-river NOT rebuilt (renewables.ninja has no hydro data) - copy AMIRIS's "
          "own reused profile into this folder separately before running the scenario.")


if __name__ == "__main__":
    main()
