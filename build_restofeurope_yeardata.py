"""Extends the Rest-of-Europe (ROE) zone to 2028 and 2029, for the out-of-sample
market-coupling extension (Phase 38). Methodological choice, stated up front and applied
consistently: ROE's economic SIZE (total demand, total capacity by technology, transmission
capacity) is held FROZEN at its real 2023 Eurostat/ENTSO-E snapshot (Phase 33/35/36) for both
years - no future-year Rest-of-Europe demand/capacity data exists to source, since 2028/2029
have not happened yet. This directly mirrors this project's own established out-of-sample
methodology (Phase 24): every calibrated mechanism is reused completely unchanged across
years, not re-tuned, so the out-of-sample test is genuine. Only the hourly SHAPE of each
series is redated to match each target year's real calendar, using the exact same
proven-correct techniques already used for Germany's own DE-side out-of-sample builds:
elapsed-hours-since-Jan-1 repositioning for 2028 (FAME's leap-year 365-day, Jan1-Dec30
representation), and a direct year-swap for 2029 (a plain, non-leap 365-day year, same as
2027 and the real 2009 weather source).

Demand SHAPE is re-derived from each year's own real DE demand file (not by redating 2027's
already-derived ROE file directly) specifically to avoid re-introducing a Phase-28-style
weekday-misalignment bug - each year's DE demand file is already correctly weekday-aligned,
so basing ROE's shape on it directly is safer than trying to redate an already-derived series.
"""
import datetime
import json
import pandas as pd

ROOT = r"C:\Users\MuideenOA\Desktop\PyTut\Amiris"
ROE_DIR = rf"{ROOT}\examples\backtest\RestOfEurope2023"
RAW_NINJA = rf"{ROE_DIR}\raw_renewables_ninja"

with open(rf"{ROE_DIR}\restofeurope_aggregate_summary.json") as f:
    agg = json.load(f)
ROE_TOTAL_DEMAND_MWH = agg["total_demand_GWh"] * 1000  # GWh -> MWh
CAP = agg["capacity_MW_by_tech"]

ONSHORE_COUNTRIES = ["AT", "BE", "CZ", "DK", "FR", "NO", "NL", "PL", "SE"]
OFFSHORE_COUNTRIES = ["BE", "DK", "FR", "NL", "SE"]
CAP_PER_COUNTRY = agg["per_country_capacity_MW"]

TRANSMISSION_DE_TO_ROE = 21593.0
TRANSMISSION_ROE_TO_DE = 22012.0


def build_for_year(year, de_scenario_folder, de_demand_file, out_scenario_folder, is_leap_fame=False):
    print(f"\n{'='*70}\nBuilding ROE data for {year} (source DE scenario: {de_scenario_folder})\n{'='*70}")
    out_dir = rf"{ROOT}\examples\backtest\{out_scenario_folder}\timeseries"
    import os
    os.makedirs(out_dir, exist_ok=True)

    # --- 1. Demand: rescale that year's own real DE demand shape to ROE's frozen total ---
    de_demand_path = rf"{ROOT}\examples\backtest\{de_scenario_folder}\timeseries\{de_demand_file}"
    de = pd.read_csv(de_demand_path, sep=";", header=None, names=["ts", "mwh"])
    print(f"DE {year} demand shape: {len(de)} hours, total={de['mwh'].sum():,.0f} MWh")
    shape = de["mwh"] / de["mwh"].sum()
    rescaled = shape * ROE_TOTAL_DEMAND_MWH
    out = pd.DataFrame({"ts": de["ts"], "mwh": rescaled})
    fname = f"load_restofeurope_{year}_shapeFromDE.csv"
    out.to_csv(rf"{out_dir}\{fname}", sep=";", header=False, index=False, float_format="%.4f")
    print(f"  saved {fname}, new total={rescaled.sum():,.0f} MWh (target {ROE_TOTAL_DEMAND_MWH:,.0f})")

    # --- 2. Renewable profiles: redate the real 2009 raw data onto the target calendar ---
    def redate_series(series_2009, year, is_leap_fame):
        """series_2009: pandas Series indexed by real 2009 hourly timestamps (0-8759)."""
        if is_leap_fame:
            # elapsed-hours-since-Jan-1 repositioning (2028's FAME-leap 365-day calendar)
            new_index = []
            for ts in series_2009.index:
                elapsed_hours = (ts - datetime.datetime(2009, 1, 1)).total_seconds() / 3600
                new_index.append(datetime.datetime(year, 1, 1) + datetime.timedelta(hours=elapsed_hours))
            return pd.Series(series_2009.values, index=new_index)
        else:
            # plain year-swap (2029: both 2009 and 2029 are real, non-leap 365-day years)
            new_index = [ts.replace(year=year) for ts in series_2009.index]
            return pd.Series(series_2009.values, index=new_index)

    def blend_and_redate(tech_prefix, countries, weight_key, out_name):
        weights = {c: CAP_PER_COUNTRY[c][weight_key] for c in countries}
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
        print(f"  saved {out_name} ({len(lines)} rows), mean CF={redated.mean():.4f}")

    blend_and_redate("wind_onshore", ONSHORE_COUNTRIES, "Wind_onshore",
                      f"wind_onshore_profile_restofeurope_{year}.csv")
    blend_and_redate("wind_offshore", OFFSHORE_COUNTRIES, "Wind_offshore",
                      f"wind_offshore_profile_restofeurope_{year}.csv")
    blend_and_redate("solar", ONSHORE_COUNTRIES, "Solar_PV",
                      f"solar_profile_restofeurope_{year}.csv")

    # --- 3. Flat series: hydro run-of-river CF, nuclear price, transmission capacity ---
    n_hours = len(de)  # matches DE's own hour count for this year (8760 either way)
    idx = pd.to_datetime(de["ts"], format="%Y-%m-%d_%H:%M:%S")

    def write_flat(value, fname, fmt="%.4f"):
        lines = [f"{ts.strftime('%Y-%m-%d_%H:%M:%S')};{fmt % value}" for ts in idx]
        with open(rf"{out_dir}\{fname}", "w", encoding="utf-8") as f:
            f.write("\n".join(lines) + "\n")
        print(f"  saved {fname} (flat {value})")

    write_flat(0.40, "hydro_profile_restofeurope_FLAT.csv")
    write_flat(TRANSMISSION_DE_TO_ROE, f"transfer_DEtoROE_realflow_{year}.csv", "%.1f")
    write_flat(TRANSMISSION_ROE_TO_DE, f"transfer_ROEtoDE_realflow_{year}.csv", "%.1f")

    # --- 4. Fuel prices: copy each year's own real DE fuel price series directly ---
    import shutil
    for fname in ["hard_coal_price.csv", "natural_gas_price.csv", "oil_price.csv"]:
        src = rf"{ROOT}\examples\backtest\{de_scenario_folder}\timeseries\{fname}"
        dst_name = fname.replace(".csv", f"_restofeurope_{year}.csv")
        shutil.copy(src, rf"{out_dir}\{dst_name}")
        print(f"  copied {fname} -> {dst_name} (real DE {year} fuel price, reused for ROE)")

    print(f"\n{year} ROE timeseries build complete -> {out_dir}")


build_for_year(2028, "Germany2028", "load_2028_base.csv", "Germany2028_MarketCoupling_ROEFlex", is_leap_fame=True)
build_for_year(2029, "Germany2029_Feb29DropFix", "load_2029_feb29fix.csv", "Germany2029_MarketCoupling_ROEFlex", is_leap_fame=False)
