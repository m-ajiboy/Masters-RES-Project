"""Compares each candidate demand-source year's real national-average temperature against
real 2009's, to check which of our AVAILABLE real-demand years (2015-2019, 2023) has
weather most similar to 2009 - rather than assuming 2023 (used until now) or guessing at
2019 (a user-suggested candidate) without checking."""
import pandas as pd

ROOT = r"C:\Users\MuideenOA\Desktop\PyTut\Amiris"
RAW_DIR = rf"{ROOT}\weather2009_raw"
REGIONS = ["north", "east", "middle", "southwest"]
CANDIDATE_YEARS = [2015, 2016, 2017, 2018, 2019, 2023]


def national_avg_temp(year):
    series = []
    for region in REGIONS:
        df = pd.read_csv(rf"{RAW_DIR}\temperature_{region}_{year}.csv", index_col=0, parse_dates=True)
        s = df["temp_c"]
        # drop Feb 29 if present, so all years compare on the same 365-day calendar
        s = s[~((s.index.month == 2) & (s.index.day == 29))]
        # reindex to a clean full-year hourly grid and fill any gaps (some stations have
        # a handful of missing hours in the raw record)
        full_idx = pd.date_range(f"{year}-01-01", periods=8760, freq="h")
        s = s[~s.index.duplicated(keep="first")]
        s = s.reindex(full_idx).astype(float).interpolate().ffill().bfill()
        series.append(s.values)
    return sum(series) / len(series)


def heating_degree_days(hourly_temp, base=15.0):
    daily_mean = pd.Series(hourly_temp).groupby(pd.Series(hourly_temp).index // 24).mean()
    return sum(max(0, base - t) for t in daily_mean)


temp_2009 = national_avg_temp(2009)
hdd_2009 = heating_degree_days(temp_2009)
monthly_2009 = pd.Series(temp_2009, index=pd.date_range("2009-01-01", periods=8760, freq="h")).resample("ME").mean()

print(f"2009 (reference): annual mean={temp_2009.mean():.2f} C, heating degree days={hdd_2009:.0f}")
print()

results = []
for year in CANDIDATE_YEARS:
    temp_y = national_avg_temp(year)
    hdd_y = heating_degree_days(temp_y)
    monthly_y = pd.Series(temp_y, index=pd.date_range("2009-01-01", periods=8760, freq="h")).resample("ME").mean()
    monthly_rmse = ((monthly_y.values - monthly_2009.values) ** 2).mean() ** 0.5
    hourly_corr = pd.Series(temp_y).corr(pd.Series(temp_2009))
    results.append((year, temp_y.mean(), hdd_y, monthly_rmse, hourly_corr))
    print(f"{year}: annual mean={temp_y.mean():.2f} C (diff {temp_y.mean()-temp_2009.mean():+.2f}), "
          f"HDD={hdd_y:.0f} (diff {hdd_y-hdd_2009:+.0f}), "
          f"monthly-pattern RMSE vs 2009={monthly_rmse:.2f} C, "
          f"hour-to-hour correlation with 2009={hourly_corr:.3f}")

print("\nRanked by monthly-pattern similarity to 2009 (lower RMSE = closer match):")
for year, mean_t, hdd, rmse, corr in sorted(results, key=lambda x: x[3]):
    print(f"  {year}: monthly RMSE={rmse:.2f} C")
