"""Builds the real-growth-projected ROE timeseries (demand shape, renewable yield profiles,
transmission capacity) for the 2028 and 2029 Growth scenarios. Same real 2009 weather and the
same redating techniques already proven in build_restofeurope_yeardata.py (Phase 38) - only
the underlying capacity/demand/transmission TOTALS change, now using the real ERAA-growth-
rate-projected 2028/2029 figures (_compute_roe_growth_projection.py, _compute_ntc_growth.py)
instead of Phase 38's frozen 2024 snapshot repeated for both years.
"""
import datetime
import json
import pandas as pd

ROOT = r"C:\Users\MuideenOA\Desktop\PyTut\Amiris"
RAW_NINJA = rf"{ROOT}\examples\backtest\RestOfEurope2023\raw_renewables_ninja"

with open(r"C:\Users\MuideenOA\maven-tools\eraa_data\roe_growth_projection.json") as f:
    growth = json.load(f)
with open(r"C:\Users\MuideenOA\maven-tools\eraa_data\ntc_growth_projection.json") as f:
    ntc_growth = json.load(f)
with open(rf"{ROOT}\examples\backtest\RestOfEurope2024\restofeurope_aggregate_summary.json") as f:
    agg2024 = json.load(f)

ONSHORE_COUNTRIES = ["AT", "BE", "CZ", "DK", "FR", "NO", "NL", "PL", "SE"]
OFFSHORE_COUNTRIES = ["BE", "DK", "FR", "NL", "SE"]

# Real 2024 per-country capacity (Phase 44) - used as the WEIGHTING basis, scaled uniformly
# to match each year's real ERAA-projected category TOTAL (documented simplification: ERAA's
# growth rate is a country-level aggregate, not sourced per-country - so each country's real
# 2024 share of the category is preserved, and the whole category is scaled to the real
# projected total).
cap2024 = agg2024["per_country_capacity_MW"]


def scaled_country_weights(category, target_total, countries):
    country_2024 = {c: cap2024[c][category] for c in countries}
    total_2024 = sum(country_2024.values())
    scale = target_total / total_2024
    return {c: v * scale for c, v in country_2024.items()}


def build_for_year(year, de_scenario_folder, de_demand_file, out_scenario_folder, is_leap_fame=False):
    print(f"\n{'='*70}\nBuilding GROWTH ROE data for {year} (source DE scenario: {de_scenario_folder})\n{'='*70}")
    out_dir = rf"{ROOT}\examples\backtest\{out_scenario_folder}\timeseries"
    import os
    os.makedirs(out_dir, exist_ok=True)

    cap_key = f"capacity_MW_{year}"
    demand_key = f"demand_TWH_{year}"
    roe_total_demand_mwh = growth[demand_key] * 1_000_000

    # --- 1. Demand: rescale that year's own real DE demand shape to the GROWN ROE total ---
    de_demand_path = rf"{ROOT}\examples\backtest\{de_scenario_folder}\timeseries\{de_demand_file}"
    de = pd.read_csv(de_demand_path, sep=";", header=None, names=["ts", "mwh"])
    print(f"DE {year} demand shape: {len(de)} hours, total={de['mwh'].sum():,.0f} MWh")
    shape = de["mwh"] / de["mwh"].sum()
    rescaled = shape * roe_total_demand_mwh
    out = pd.DataFrame({"ts": de["ts"], "mwh": rescaled})
    # Same filename as the frozen build (matches DemandRestOfEurope.yaml's existing reference
    # exactly, since this folder was copied from it) - only the CONTENT changes.
    fname = f"load_restofeurope_{year}_shapeFromDE.csv"
    out.to_csv(rf"{out_dir}\{fname}", sep=";", header=False, index=False, float_format="%.4f")
    print(f"  saved {fname}, new total={rescaled.sum():,.0f} MWh (real ERAA-growth-projected target "
          f"{roe_total_demand_mwh:,.0f} MWh, vs. frozen-2024 baseline {agg2024['total_demand_GWh']*1000:,.0f} MWh)")

    # --- 2. Renewable profiles: real 2009 weather, redated, weighted by GROWN per-country capacity ---
    def redate_series(series_2009, year, is_leap_fame):
        if is_leap_fame:
            new_index = []
            for ts in series_2009.index:
                elapsed_hours = (ts - datetime.datetime(2009, 1, 1)).total_seconds() / 3600
                new_index.append(datetime.datetime(year, 1, 1) + datetime.timedelta(hours=elapsed_hours))
            return pd.Series(series_2009.values, index=new_index)
        else:
            new_index = [ts.replace(year=year) for ts in series_2009.index]
            return pd.Series(series_2009.values, index=new_index)

    def blend_and_redate(tech_prefix, countries, category, out_name):
        weights = scaled_country_weights(category, growth[cap_key][category], countries)
        total_weight = sum(weights.values())
        series_list = []
        for c in countries:
            raw = pd.read_csv(rf"{RAW_NINJA}\{tech_prefix}_{c}_2009.csv", index_col=0)
            raw.index = pd.to_datetime(raw.index)
            series_list.append(raw["electricity"] * weights[c])
        blended_2009 = sum(series_list) / total_weight
        redated = redate_series(blended_2009, year, is_leap_fame)
        idx_str = [ts.strftime("%Y-%m-%d_%H:%M:%S") for ts in redated.index]
        lines = [f"{t};{v:.6f}" for t, v in zip(idx_str, redated.values)]
        with open(rf"{out_dir}\{out_name}", "w", encoding="utf-8") as f:
            f.write("\n".join(lines) + "\n")
        print(f"  saved {out_name} ({len(lines)} rows), mean CF={redated.mean():.4f}, "
              f"total capacity weight={total_weight:,.0f} MW (real ERAA-growth-projected)")

    # Same filenames as the frozen build (matches RenewablesRestOfEurope.yaml's existing
    # references exactly) - only the CONTENT (real growth-projected capacity weights) changes.
    blend_and_redate("wind_onshore", ONSHORE_COUNTRIES, "Wind_onshore",
                      f"wind_onshore_profile_restofeurope_{year}.csv")
    blend_and_redate("wind_offshore", OFFSHORE_COUNTRIES, "Wind_offshore",
                      f"wind_offshore_profile_restofeurope_{year}.csv")
    blend_and_redate("solar", ONSHORE_COUNTRIES, "Solar_PV",
                      f"solar_profile_restofeurope_{year}.csv")

    # --- 3. Flat series: hydro run-of-river CF (unchanged technology assumption), transmission ---
    n_hours = len(de)
    idx = pd.to_datetime(de["ts"], format="%Y-%m-%d_%H:%M:%S")

    def write_flat(value, fname, fmt="%.4f"):
        lines = [f"{ts.strftime('%Y-%m-%d_%H:%M:%S')};{fmt % value}" for ts in idx]
        with open(rf"{out_dir}\{fname}", "w", encoding="utf-8") as f:
            f.write("\n".join(lines) + "\n")
        print(f"  saved {fname} (flat {value})")

    write_flat(0.40, "hydro_profile_restofeurope_FLAT.csv")
    ntc = ntc_growth[f"projected_{year}"]
    write_flat(ntc["DE_to_ROE"], "transfer_DEtoROE_realflow.csv", "%.1f")
    write_flat(ntc["ROE_to_DE"], "transfer_ROEtoDE_realflow.csv", "%.1f")

    # --- 4. Fuel prices: copy each year's own real DE fuel price series directly (unchanged) ---
    import shutil
    for fname in ["hard_coal_price.csv", "natural_gas_price.csv", "oil_price.csv"]:
        src = rf"{ROOT}\examples\backtest\{de_scenario_folder}\timeseries\{fname}"
        dst_name = fname.replace(".csv", f"_restofeurope_{year}.csv")
        shutil.copy(src, rf"{out_dir}\{dst_name}")

    print(f"\n{year} GROWTH ROE timeseries build complete -> {out_dir}")


build_for_year(2028, "Germany2028", "load_2028_base.csv", "Germany2028_MarketCoupling_ROEFlex_Growth", is_leap_fame=True)
build_for_year(2029, "Germany2029_Feb29DropFix", "load_2029_feb29fix.csv", "Germany2029_MarketCoupling_ROEFlex_Growth", is_leap_fame=False)
