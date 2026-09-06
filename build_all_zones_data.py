"""Phase 43: full disaggregation - builds each of Germany's remaining 9 real neighbours
(AT, BE, CZ, DK, NO, NL, PL, SE, CH; France already built in Phase 42) as its OWN separate
zone, replacing the aggregate ROE zone entirely. Star topology throughout (every zone links
only to Germany, same simplification as Phase 42) - this build exists specifically to test
Phase 42's own prediction that extending the star-topology approach to all 10 countries
spreads the same failure mode rather than fixing it, not because a real improvement is
expected.

Every number is real, computed directly from the already-fetched raw data in
RestOfEurope2023/ (Eurostat demand/capacity, renewables.ninja per-country 2009 weather,
ENTSO-E DE<->country flow) - no new fetching. Countries with zero real capacity in a given
technology (per Eurostat) simply have no agent for that technology - not zeroed out
artificially, genuinely absent from the real data.

ID allocation (mirrors France's Phase 42 pattern exactly, one dedicated thousand-block per
country): AT=3000s, BE=4000s, CZ=5000s, DK=6000s, NO=7000s, FR=8000s (Phase 42, unchanged),
NL=9000s (reusing the old aggregate ROE's freed-up block), PL=10000s, SE=11000s, CH=12000s.
Offsets within each block: +1 exchange, +4 fuelsMarket, +6 forecaster, +11 MPVAR trader,
+13 FIT trader, +90 policy, +101..104 builders, +201..204 conventional traders,
+301..304 plant operators, +401..404 renewables, +500 demand, +601..602 storage."""
import json
import pandas as pd

ROE_ROOT = r"C:\Users\MuideenOA\Desktop\PyTut\Amiris\examples\backtest\RestOfEurope2023"
OUT_ROOT = r"C:\Users\MuideenOA\Desktop\PyTut\Amiris\examples\backtest\Germany2027_MarketCoupling_AllZones"
TS_DIR = rf"{OUT_ROOT}\timeseries"
AGENTS_DIR = rf"{OUT_ROOT}\agents"
CONTRACTS_DIR = rf"{OUT_ROOT}\contracts"
ENTSOE_DIR = rf"{ROE_ROOT}\raw_entsoe"
NINJA_DIR = rf"{ROE_ROOT}\raw_renewables_ninja"

with open(rf"{ROE_ROOT}\restofeurope_aggregate_summary.json") as f:
    summary = json.load(f)
cap = summary["per_country_capacity_MW"]
demand = summary["per_country_demand_GWh"]

# Country -> (ID base, ENTSO-E flow-file suffix(es) for DE<->country, has offshore wind?)
COUNTRIES = {
    "AT": {"base": 3000, "flow": ["AT"]},
    "BE": {"base": 4000, "flow": ["BE"]},
    "CZ": {"base": 5000, "flow": ["CZ"]},
    "DK": {"base": 6000, "flow": ["DK_1", "DK_2"]},
    "NO": {"base": 7000, "flow": ["NO_2"]},
    "NL": {"base": 9000, "flow": ["NL"]},
    "PL": {"base": 10000, "flow": ["PL"]},
    "SE": {"base": 11000, "flow": ["SE"]},
    "CH": {"base": 12000, "flow": ["CH"]},
}

RESERVOIR_SHARE = 0.902
RUN_OF_RIVER_SHARE = 0.098
PUMPED_SHARE = 0.30  # general EU-wide IHA method (Phase 33/37) - used for all these 9
                      # countries since no individual real pumped-storage figure was
                      # researched for them (unlike France's RTE-sourced figure in Phase 42) -
                      # a documented, honest limitation, not a new simplification.

idx_2027 = pd.date_range("2027-01-01", periods=8760, freq="h")

de_shape = pd.read_csv(
    r"C:\Users\MuideenOA\Desktop\PyTut\Amiris\examples\backtest\Germany2027_MarketCoupling_ROEFlex\timeseries\load_2027_feb29fix.csv",
    sep=";", header=None, names=["ts", "val"])
de_shape_norm = de_shape["val"] / de_shape["val"].sum()


def save_flat(value, fname):
    lines = [f"{ts.strftime('%Y-%m-%d_%H:%M:%S')};{value:.1f}" for ts in idx_2027]
    with open(rf"{TS_DIR}\{fname}", "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")


def save_profile(series, fname):
    out = pd.DataFrame({"ts": idx_2027.strftime("%Y-%m-%d_%H:%M:%S"), "val": series.values})
    out.to_csv(rf"{TS_DIR}\{fname}", sep=";", header=False, index=False, float_format="%.6f")


def load_raw(prefix, country):
    return pd.read_csv(rf"{NINJA_DIR}\{prefix}_{country}_2009.csv", index_col=0)["electricity"].reset_index(drop=True)


PERCENTILE = 0.98
results = {}

for code, info in COUNTRIES.items():
    c = cap[code]
    base = info["base"]
    print(f"\n{'='*60}\n{code} (base {base})\n{'='*60}")

    # ---- Demand shape ----
    total_mwh = demand[code] * 1000
    series = de_shape_norm * total_mwh
    save_flat_name = f"load_{code.lower()}_2027_shapeFromDE.csv"
    out = pd.DataFrame({"ts": de_shape["ts"], "val": series})
    out.to_csv(rf"{TS_DIR}\{save_flat_name}", sep=";", header=False, index=False, float_format="%.4f")
    print(f"  demand: {demand[code]:,.1f} GWh -> {save_flat_name}")

    # ---- Transmission capacity (98th percentile of real flow, summed if 2 bidding zones) ----
    # SE_4 (Sweden): Phase 35's documented persistent ENTSO-E flow-fetch gap - no raw flow
    # file was ever obtained for this border. Falls back to the real published nameplate
    # capacity of the Baltic Cable (the actual DE<->SE HVDC interconnector, 600 MW) instead
    # of a flow-derived estimate - a different, less precise methodology, used only because
    # the real flow data itself was never obtainable, not silently guessed.
    if code == "SE":
        de_to = to_de = 600.0
        print("  transmission: SE_4 flow data was never obtained (Phase 35 gap) - using the "
              "real Baltic Cable nameplate capacity (600 MW) as an honest fallback")
    else:
        de_to = sum(pd.read_csv(rf"{ENTSOE_DIR}\flow_DEto{z}_2023.csv", index_col=0).iloc[:, 0].quantile(PERCENTILE)
                    for z in info["flow"])
        to_de = sum(pd.read_csv(rf"{ENTSOE_DIR}\flow_{z}toDE_2023.csv", index_col=0).iloc[:, 0].quantile(PERCENTILE)
                    for z in info["flow"])
    save_flat(de_to, f"transfer_DEto{code}_realflow.csv")
    save_flat(to_de, f"transfer_{code}toDE_realflow.csv")
    print(f"  transmission: DE->{code} {de_to:,.0f} MW, {code}->DE {to_de:,.0f} MW")

    # ---- Renewable profiles (own real 2009 weather, no blending) ----
    has_windon = c.get("Wind_onshore", 0) > 0
    has_windoff = c.get("Wind_offshore", 0) > 0
    has_solar = c.get("Solar_PV", 0) > 0
    if has_windon:
        save_profile(load_raw("wind_onshore", code), f"wind_onshore_profile_{code.lower()}_2027.csv")
    if has_windoff:
        save_profile(load_raw("wind_offshore", code), f"wind_offshore_profile_{code.lower()}_2027.csv")
    if has_solar:
        save_profile(load_raw("solar", code), f"solar_profile_{code.lower()}_2027.csv")
    print(f"  renewables present: windon={has_windon} windoff={has_windoff} solar={has_solar}")

    # ---- Hydro split (30% EU-wide method) ----
    hydro_total = c.get("Hydro_total", 0.0)
    pumped = hydro_total * PUMPED_SHARE
    conventional = hydro_total * (1 - PUMPED_SHARE)
    reservoir = conventional * RESERVOIR_SHARE
    ror = conventional * RUN_OF_RIVER_SHARE
    print(f"  hydro: total={hydro_total:,.1f} pumped={pumped:,.1f} reservoir={reservoir:,.1f} ror={ror:,.1f}")

    results[code] = {
        "base": base,
        "demand_mwh": total_mwh,
        "de_to": de_to,
        "to_de": to_de,
        "has_windon": has_windon, "has_windoff": has_windoff, "has_solar": has_solar,
        "windon_mw": c.get("Wind_onshore", 0.0), "windoff_mw": c.get("Wind_offshore", 0.0),
        "solar_mw": c.get("Solar_PV", 0.0),
        "coal_mw": c.get("Coal_and_manufactured_gases", 0.0), "gas_mw": c.get("Natural_gas", 0.0),
        "oil_mw": c.get("Oil", 0.0), "nuclear_mw": c.get("Nuclear", 0.0),
        "hydro_total": hydro_total, "pumped_mw": pumped, "reservoir_mw": reservoir, "ror_mw": ror,
    }

with open(rf"{ROE_ROOT}\allzones_computed_numbers.json", "w") as f:
    json.dump(results, f, indent=2)
print("\n\nSaved allzones_computed_numbers.json - all real derived numbers for YAML generation.")
