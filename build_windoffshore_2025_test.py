# -*- coding: utf-8 -*-
"""Builds a wind-offshore-only variant of the headline scenario, replacing AMIRIS's own
2019-example wind-offshore profile (never weather-year-matched to anything) with the real
2025 renewables.ninja profile - the best real match to Brainpool's own 2009 weather basis
found in the 16-year sweep (compare_windoffshore_years_to_2009.py, monthly RMSE 0.0493).
Isolates wind-offshore as the ONLY variable versus the Phase 37 headline: DE demand stays
on the real 2016 shape (already confirmed best), everything else unchanged."""
from pathlib import Path
import pandas as pd

ROOT = Path(r"C:\Users\MuideenOA\Desktop\PyTut\Amiris")
RAW_DIR = ROOT / "weather2009_raw"
REGIONS = ["north_sea", "baltic_sea"]
YEAR = 2025
HOURS = 8760


def national_offshore_cf(year):
    series = []
    for region in REGIONS:
        df = pd.read_csv(RAW_DIR / f"wind_offshore_{region}_{year}.csv", index_col=0, parse_dates=True)
        s = df.iloc[:, 0].astype(float)
        s = s[~s.index.duplicated(keep="first")]
        full_idx = pd.date_range(f"{year}-01-01", periods=HOURS, freq="h")
        s = s.reindex(full_idx).interpolate().ffill().bfill()
        series.append(s.values)
    return sum(series) / len(series)


def main():
    cf = national_offshore_cf(YEAR)
    # Redate the real 2025 calendar onto 2027 (both non-leap, 365 days - clean 1:1
    # hour-of-year mapping, same technique as the original Weather2009 profile build).
    idx = pd.date_range("2027-01-01", periods=HOURS, freq="h")
    lines = [f"{ts.strftime('%Y-%m-%d_%H:%M:%S')};{val:.6f}" for ts, val in zip(idx, cf)]

    OUT_DIR = ROOT / "examples" / "backtest" / "Germany2027_MarketCoupling_ROEFlex_WindOffshore2025" / "timeseries"
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    out_path = OUT_DIR / "wind_offshore_profile.csv"
    out_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"Saved {out_path}: mean CF {cf.mean():.4f} (was 0.3709 in the AMIRIS-2019-default baseline)")


if __name__ == "__main__":
    main()
