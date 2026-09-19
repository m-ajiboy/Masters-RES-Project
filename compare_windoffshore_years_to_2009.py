"""Ranks each real candidate wind-offshore year (2010-2025) by how closely its real
capacity-factor pattern matches real 2009's, the same monthly-RMSE method already used
for the demand-shape-year search. National offshore profile = mean of the two real
representative points (North Sea German Bight, Baltic Sea near Ruegen), matching the
regional-averaging convention already used throughout this project."""
import pandas as pd

RAW_DIR = r"C:\Users\MuideenOA\Desktop\PyTut\Amiris\weather2009_raw"
REGIONS = ["north_sea", "baltic_sea"]
YEARS = [2010, 2011, 2012, 2013, 2014, 2015, 2016, 2017, 2018, 2019,
         2020, 2021, 2022, 2023, 2024, 2025]


def national_offshore_cf(year):
    series = []
    for region in REGIONS:
        df = pd.read_csv(rf"{RAW_DIR}\wind_offshore_{region}_{year}.csv", index_col=0, parse_dates=True)
        s = df.iloc[:, 0].astype(float)
        s = s[~((s.index.month == 2) & (s.index.day == 29))]
        s = s[~s.index.duplicated(keep="first")]
        full_idx = pd.date_range(f"{year}-01-01", periods=8760, freq="h")
        s = s.reindex(full_idx).interpolate().ffill().bfill()
        series.append(s.values)
    return sum(series) / len(series)


cf_2009 = national_offshore_cf(2009)
monthly_2009 = pd.Series(cf_2009, index=pd.date_range("2009-01-01", periods=8760, freq="h")).resample("ME").mean()
print(f"2009 (reference): annual mean CF = {cf_2009.mean():.4f}")
print()

results = []
for year in YEARS:
    cf_y = national_offshore_cf(year)
    monthly_y = pd.Series(cf_y, index=pd.date_range("2009-01-01", periods=8760, freq="h")).resample("ME").mean()
    monthly_rmse = ((monthly_y.values - monthly_2009.values) ** 2).mean() ** 0.5
    hourly_corr = pd.Series(cf_y).corr(pd.Series(cf_2009))
    results.append((year, cf_y.mean(), monthly_rmse, hourly_corr))
    print(f"{year}: annual mean CF={cf_y.mean():.4f} (diff {cf_y.mean()-cf_2009.mean():+.4f}), "
          f"monthly-pattern RMSE vs 2009={monthly_rmse:.4f}, hour-to-hour corr={hourly_corr:.3f}")

print("\nRanked by monthly-pattern similarity to 2009 (lower RMSE = closer match):")
for rank, (year, mean_cf, rmse, corr) in enumerate(sorted(results, key=lambda x: x[2]), 1):
    print(f"  {rank}. {year}: monthly RMSE={rmse:.4f}, annual mean CF={mean_cf:.4f}")
