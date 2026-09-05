"""Blends the per-country real 2009 renewables.ninja capacity-factor profiles into
capacity-weighted Rest-of-Europe yield profiles per technology (wind onshore, wind offshore,
solar PV), using the real Eurostat installed-capacity figures (Phase 33) as weights - so
France's much larger wind fleet counts proportionally more than Czechia's, not an
unweighted average across countries. Redates 2009 to 2027 (both real, standard 365-day
years, so a direct day-of-year mapping applies - no weekday-shift logic needed, matching
the same technique already used for Germany's own 2009-to-2027 redate).
"""
import json
import pandas as pd

RAW_DIR = r"C:\Users\MuideenOA\Desktop\PyTut\Amiris\examples\backtest\RestOfEurope2023\raw_renewables_ninja"
OUT_DIR = r"C:\Users\MuideenOA\Desktop\PyTut\Amiris\examples\backtest\RestOfEurope2023"

with open(rf"{OUT_DIR}\restofeurope_aggregate_summary.json") as f:
    summary = json.load(f)
cap = summary["per_country_capacity_MW"]

ONSHORE_COUNTRIES = ["AT", "BE", "CZ", "DK", "FR", "NO", "NL", "PL", "SE"]
OFFSHORE_COUNTRIES = ["BE", "DK", "FR", "NL", "SE"]
SOLAR_COUNTRIES = ONSHORE_COUNTRIES


def load_raw(tech_prefix, country):
    df = pd.read_csv(rf"{RAW_DIR}\{tech_prefix}_{country}_2009.csv", index_col=0)
    return df["electricity"].reset_index(drop=True)


def blend(tech_prefix, countries, weight_key):
    weights = {c: cap[c][weight_key] for c in countries}
    total_weight = sum(weights.values())
    print(f"\n{tech_prefix}: weights (MW) = {weights}, total = {total_weight:,.0f} MW")
    series_list = [load_raw(tech_prefix, c) * weights[c] for c in countries]
    blended = sum(series_list) / total_weight
    print(f"  blended profile: mean={blended.mean():.4f}, max={blended.max():.4f}, "
          f"min={blended.min():.4f} (capacity factor, 0-1)")
    return blended


onshore = blend("wind_onshore", ONSHORE_COUNTRIES, "Wind_onshore")
offshore = blend("wind_offshore", OFFSHORE_COUNTRIES, "Wind_offshore")
solar = blend("solar", SOLAR_COUNTRIES, "Solar_PV")

# Redate 2009 -> 2027 (both real non-leap years, direct day-of-year mapping)
idx_2027 = pd.date_range("2027-01-01", periods=8760, freq="h")


def save(series, name):
    out = pd.DataFrame({"ts": idx_2027.strftime("%Y-%m-%d_%H:%M:%S"), "val": series.values})
    path = rf"{OUT_DIR}\{name}_restofeurope_2027.csv"
    out.to_csv(path, sep=";", header=False, index=False, float_format="%.6f")
    print(f"Saved {path} ({len(out)} rows)")


save(onshore, "wind_onshore_profile")
save(offshore, "wind_offshore_profile")
save(solar, "solar_profile")

print("\nDone - 3 capacity-weighted Rest-of-Europe yield profiles saved, real 2009 weather, redated to 2027.")
