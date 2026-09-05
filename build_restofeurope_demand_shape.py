"""Builds an hourly demand shape for the Rest-of-Europe aggregate zone, while ENTSO-E (the
real source for actual hourly load by country) remains down. Eurostat gave a real ANNUAL
total (1,139,270.364 GWh, 9 countries, Phase 33) but no hourly resolution at all.

Documented simplification: borrows Germany's own real, already-verified 2027 hourly demand
SHAPE (load_2027_feb29fix.csv, this project's current best build - already correctly dated
to 2027, no weekday-realignment needed since the target year matches) and rescales it to
match the real Eurostat-sourced Rest-of-Europe annual TOTAL. This is the same
borrow-a-real-shape-rescale-to-a-real-total technique already used and documented throughout
this project (e.g. Phase 17's demand rebuild). Flagged for replacement with real per-country
hourly load data once ENTSO-E recovers (Phase 33's cron retry) - not treated as a final input.
"""
import pandas as pd

GERMANY_SHAPE = r"C:\Users\MuideenOA\Desktop\PyTut\Amiris\examples\backtest\Germany2027_Feb29DropFix\timeseries\load_2027_feb29fix.csv"
OUT_DIR = r"C:\Users\MuideenOA\Desktop\PyTut\Amiris\examples\backtest\RestOfEurope2023"
OUT_FILE = rf"{OUT_DIR}\load_restofeurope_2027_shapeFromDE.csv"

REST_OF_EUROPE_TOTAL_MWH = 1_139_270.364 * 1000  # GWh -> MWh, real Eurostat 2023 total (Phase 33)

df = pd.read_csv(GERMANY_SHAPE, sep=";", header=None, names=["ts", "mwh"])
print(f"Germany 2027 shape: {len(df)} hours, annual total = {df['mwh'].sum():,.0f} MWh")

shape = df["mwh"] / df["mwh"].sum()  # normalize to a per-unit shape summing to 1.0
rescaled = shape * REST_OF_EUROPE_TOTAL_MWH

out = pd.DataFrame({"ts": df["ts"], "mwh": rescaled})
out.to_csv(OUT_FILE, sep=";", header=False, index=False, float_format="%.4f")

print(f"\nRest-of-Europe rescaled shape saved: {OUT_FILE}")
print(f"  Hours: {len(out)}")
print(f"  New annual total: {out['mwh'].sum():,.0f} MWh (target was {REST_OF_EUROPE_TOTAL_MWH:,.0f} MWh)")
print(f"  Min hour: {out['mwh'].min():,.0f} MWh, Max hour: {out['mwh'].max():,.0f} MWh, Mean: {out['mwh'].mean():,.0f} MWh")

# Sanity check: weekday vs weekend pattern should carry over unchanged from the source shape
out["dt"] = pd.to_datetime(out["ts"], format="%Y-%m-%d_%H:%M:%S")
out["weekday"] = out["dt"].dt.dayofweek
wd_mean = out[out["weekday"] < 5]["mwh"].mean()
we_mean = out[out["weekday"] >= 5]["mwh"].mean()
print(f"\n  Weekday avg: {wd_mean:,.0f} MWh, Weekend avg: {we_mean:,.0f} MWh "
      f"(weekday should be higher, matching real demand patterns)")

# For scale context: compare to Germany's own real 2027 demand
germany_total = df["mwh"].sum()
print(f"\n  For scale: Germany's own 2027 demand = {germany_total:,.0f} MWh "
      f"({germany_total/1e6:.1f} TWh) vs. this Rest-of-Europe total "
      f"({REST_OF_EUROPE_TOTAL_MWH/1e6:.1f} TWh) - "
      f"a ratio of {REST_OF_EUROPE_TOTAL_MWH/germany_total:.2f}x, for 9 countries combined.")
