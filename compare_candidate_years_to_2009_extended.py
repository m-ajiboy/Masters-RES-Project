"""Extends Phase 17's real-temperature comparison (compare_candidate_years_to_2009.py,
which covered 2015-2019 and 2023) to the full candidate pool now available:
2010-2014, 2015-2019, 2020-2022, 2023, 2024-2025 (2026 excluded, year not yet complete).

Data gap, disclosed rather than hidden: the East DWD station's historical archive has no
real 2024 data at all (confirmed directly - the file claims coverage through 2025 but the
2024 slice is empty). 2024's national average is therefore computed from the other 3
stations (north, middle, southwest) only, not all 4 like every other year - flagged
explicitly in the output rather than silently averaged in or dropped."""
import pandas as pd

ROOT = r"C:\Users\MuideenOA\Desktop\PyTut\Amiris"
RAW_DIR = rf"{ROOT}\weather2009_raw"
ALL_REGIONS = ["north", "east", "middle", "southwest"]
CANDIDATE_YEARS = [2010, 2011, 2012, 2013, 2014, 2015, 2016, 2017, 2018, 2019,
                   2020, 2021, 2022, 2023, 2024, 2025]
MISSING_REGION_BY_YEAR = {2024: ["east"]}  # confirmed real gap, not assumed


def national_avg_temp(year):
    regions = [r for r in ALL_REGIONS if r not in MISSING_REGION_BY_YEAR.get(year, [])]
    series = []
    for region in regions:
        df = pd.read_csv(rf"{RAW_DIR}\temperature_{region}_{year}.csv", index_col=0, parse_dates=True)
        s = df["temp_c"]
        s = s[~((s.index.month == 2) & (s.index.day == 29))]
        full_idx = pd.date_range(f"{year}-01-01", periods=8760, freq="h")
        s = s[~s.index.duplicated(keep="first")]
        s = s.reindex(full_idx).astype(float).interpolate().ffill().bfill()
        series.append(s.values)
    return sum(series) / len(series), regions


def heating_degree_days(hourly_temp, base=15.0):
    daily_mean = pd.Series(hourly_temp).groupby(pd.Series(hourly_temp).index // 24).mean()
    return sum(max(0, base - t) for t in daily_mean)


temp_2009, _ = national_avg_temp(2009)
hdd_2009 = heating_degree_days(temp_2009)
monthly_2009 = pd.Series(temp_2009, index=pd.date_range("2009-01-01", periods=8760, freq="h")).resample("ME").mean()

print(f"2009 (reference): annual mean={temp_2009.mean():.2f} C, heating degree days={hdd_2009:.0f}")
print()

results = []
for year in CANDIDATE_YEARS:
    temp_y, regions_used = national_avg_temp(year)
    flag = "" if len(regions_used) == 4 else f"  [WARNING: only {len(regions_used)}/4 stations - {regions_used}]"
    hdd_y = heating_degree_days(temp_y)
    monthly_y = pd.Series(temp_y, index=pd.date_range("2009-01-01", periods=8760, freq="h")).resample("ME").mean()
    monthly_rmse = ((monthly_y.values - monthly_2009.values) ** 2).mean() ** 0.5
    hourly_corr = pd.Series(temp_y).corr(pd.Series(temp_2009))
    results.append((year, temp_y.mean(), hdd_y, monthly_rmse, hourly_corr, len(regions_used)))
    print(f"{year}: annual mean={temp_y.mean():.2f} C (diff {temp_y.mean()-temp_2009.mean():+.2f}), "
          f"HDD={hdd_y:.0f} (diff {hdd_y-hdd_2009:+.0f}), "
          f"monthly-pattern RMSE vs 2009={monthly_rmse:.2f} C, "
          f"hour-to-hour correlation with 2009={hourly_corr:.3f}{flag}")

print("\nFull ranking by monthly-pattern similarity to 2009 (lower RMSE = closer match),")
print("including the original Phase 17 candidates (2015-2019, 2023) for direct comparison:")
for rank, (year, mean_t, hdd, rmse, corr, nstations) in enumerate(sorted(results, key=lambda x: x[3]), 1):
    tested_before = " (Phase 17)" if year in (2015, 2016, 2017, 2018, 2019, 2023) else " (NEW)"
    print(f"  {rank}. {year}: monthly RMSE={rmse:.2f} C, HDD diff={hdd-hdd_2009:+.0f}{tested_before}")

print(f"\nPrevious Phase 17 winner: 2016 (monthly RMSE 2.31 C, HDD deficit -40)")
best = min(results, key=lambda x: x[3])
print(f"New overall best match: {best[0]} (monthly RMSE {best[3]:.2f} C, HDD diff {best[2]-hdd_2009:+.0f})")
