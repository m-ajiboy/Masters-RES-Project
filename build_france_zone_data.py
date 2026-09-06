"""Phase 42 (pilot): disaggregates France out of the aggregate 'Rest of Europe' zone into its
own real, separately-modelled zone - testing whether a real named neighbour improves on the
single-aggregate approach (Phase 32's decision: escalate only if the aggregate doesn't do
enough; the aggregate result was already excellent, so this is a genuine "does disaggregating
help further" pilot, not a fix for a failure).

Chose France as the pilot country: largest single economy in the ROE aggregate (407,334 GWh
demand, 146,461 MW capacity - both real Eurostat 2023), and the one country for which this
project already has independently real, separately-fetched raw data for every input (Eurostat
demand/capacity, renewables.ninja per-country 2009 weather, ENTSO-E DE<->FR flow) - no new
fetching needed.

Every number below is real, computed directly from the already-fetched raw data in
RestOfEurope2023/, with ONE new real figure sourced specifically for this pilot: France's own
pumped-hydro capacity (RTE, ~5.8 GW as of 2015, the most recent published figure found - a
genuine country-specific upgrade over the general 30% EU-wide IHA ratio used for the rest of
the aggregate).

Writes: France's own demand/renewable/storage timeseries, the REDUCED 'ROE minus France'
demand/renewable/storage timeseries (so France's capacity is not double-counted), and the real
flow-derived DE<->FR transmission capacity (Phase 36's exact 98th-percentile methodology,
applied to this one border alone)."""
import json
import pandas as pd

ROE_ROOT = r"C:\Users\MuideenOA\Desktop\PyTut\Amiris\examples\backtest\RestOfEurope2023"
OUT_ROOT = r"C:\Users\MuideenOA\Desktop\PyTut\Amiris\examples\backtest\Germany2027_MarketCoupling_FranceZone\timeseries"
ENTSOE_DIR = rf"{ROE_ROOT}\raw_entsoe"
NINJA_DIR = rf"{ROE_ROOT}\raw_renewables_ninja"

with open(rf"{ROE_ROOT}\restofeurope_aggregate_summary.json") as f:
    summary = json.load(f)
cap = summary["per_country_capacity_MW"]
demand = summary["per_country_demand_GWh"]

FR_CAP = cap["FR"]
ROE9_COUNTRIES = ["AT", "BE", "CZ", "DK", "NO", "NL", "PL", "SE", "CH"]

print("=" * 70)
print("1. DEMAND: France vs. reduced ROE (9 countries)")
print("=" * 70)
fr_demand_gwh = demand["FR"]
roe9_demand_gwh = summary["total_demand_GWh"] - fr_demand_gwh
print(f"France (real, Eurostat 2023): {fr_demand_gwh:,.1f} GWh")
print(f"ROE minus France (9 countries): {roe9_demand_gwh:,.1f} GWh "
      f"(was {summary['total_demand_GWh']:,.1f} GWh for all 10)")

# Both reuse the SAME real 2027 German demand SHAPE (Phase 33's established methodology),
# just rescaled to a different real annual total.
de_shape = pd.read_csv(
    r"C:\Users\MuideenOA\Desktop\PyTut\Amiris\examples\backtest\Germany2027_MarketCoupling_ROEFlex\timeseries\load_2027_feb29fix.csv",
    sep=";", header=None, names=["ts", "val"])
de_shape_norm = de_shape["val"] / de_shape["val"].sum()

for total_mwh, name in [(fr_demand_gwh * 1000, "load_france_2027_shapeFromDE.csv"),
                         (roe9_demand_gwh * 1000, "load_restofeurope9_2027_shapeFromDE.csv")]:
    series = de_shape_norm * total_mwh
    out = pd.DataFrame({"ts": de_shape["ts"], "val": series})
    out.to_csv(rf"{OUT_ROOT}\{name}", sep=";", header=False, index=False, float_format="%.4f")
    print(f"  Saved {name} (sum={series.sum():,.0f} MWh)")

print("\n" + "=" * 70)
print("2. RENEWABLE CAPACITY: France's own vs. reduced ROE (9-country re-blend)")
print("=" * 70)
for tech in ["Wind_onshore", "Wind_offshore", "Solar_PV"]:
    fr_val = FR_CAP.get(tech, 0.0)
    roe9_val = sum(cap[c].get(tech, 0.0) for c in ROE9_COUNTRIES)
    print(f"{tech}: France={fr_val:,.1f} MW | ROE-9={roe9_val:,.1f} MW "
          f"(orig ROE-10={fr_val + roe9_val:,.1f} MW)")

# France's own profile: its own real 2009 weather, no blending needed (single country).
idx_2027 = pd.date_range("2027-01-01", periods=8760, freq="h")


def save_profile(series, name):
    out = pd.DataFrame({"ts": idx_2027.strftime("%Y-%m-%d_%H:%M:%S"), "val": series.values})
    out.to_csv(rf"{OUT_ROOT}\{name}", sep=";", header=False, index=False, float_format="%.6f")
    print(f"  Saved {name}")


def load_raw(prefix, country):
    return pd.read_csv(rf"{NINJA_DIR}\{prefix}_{country}_2009.csv", index_col=0)["electricity"].reset_index(drop=True)


fr_onshore = load_raw("wind_onshore", "FR")
fr_offshore = load_raw("wind_offshore", "FR")
fr_solar = load_raw("solar", "FR")
save_profile(fr_onshore, "wind_onshore_profile_france_2027.csv")
save_profile(fr_offshore, "wind_offshore_profile_france_2027.csv")
save_profile(fr_solar, "solar_profile_france_2027.csv")

# Reduced ROE (9 countries): re-blend, capacity-weighted, excluding France.
ONSHORE_9 = ["AT", "BE", "CZ", "DK", "NO", "NL", "PL", "SE"]
OFFSHORE_9 = ["BE", "DK", "NL", "SE"]
SOLAR_9 = ONSHORE_9


def blend(prefix, countries, weight_key):
    weights = {c: cap[c][weight_key] for c in countries}
    total_weight = sum(weights.values())
    series_list = [load_raw(prefix, c) * weights[c] for c in countries]
    return sum(series_list) / total_weight


roe9_onshore = blend("wind_onshore", ONSHORE_9, "Wind_onshore")
roe9_offshore = blend("wind_offshore", OFFSHORE_9, "Wind_offshore")
roe9_solar = blend("solar", SOLAR_9, "Solar_PV")
save_profile(roe9_onshore, "wind_onshore_profile_restofeurope9_2027.csv")
save_profile(roe9_offshore, "wind_offshore_profile_restofeurope9_2027.csv")
save_profile(roe9_solar, "solar_profile_restofeurope9_2027.csv")

print("\n" + "=" * 70)
print("3. HYDRO SPLIT: France (real RTE pumped figure) vs. reduced ROE (EU-wide 30% method)")
print("=" * 70)
FR_PUMPED_MW = 5800.0  # RTE, real published figure (~5.82 GW operational storage, 2015,
                        # essentially all pumped - most recent public figure found;
                        # France's PSH fleet has seen minimal build-out since per government
                        # 2030-2035 expansion plans, so this remains the best available real
                        # base figure for 2023).
RESERVOIR_SHARE = 0.902  # Switzerland's real ENTSO-E ratio, reused (Phase 37 precedent)
RUN_OF_RIVER_SHARE = 0.098

fr_hydro_total = FR_CAP["Hydro_total"]
fr_conventional = fr_hydro_total - FR_PUMPED_MW
fr_reservoir = fr_conventional * RESERVOIR_SHARE
fr_ror = fr_conventional * RUN_OF_RIVER_SHARE
print(f"France hydro total (real Eurostat): {fr_hydro_total:,.1f} MW")
print(f"  Pumped (real RTE figure): {FR_PUMPED_MW:,.1f} MW")
print(f"  Reservoir (Swiss ratio applied to remainder): {fr_reservoir:,.1f} MW")
print(f"  Run-of-river (Swiss ratio applied to remainder): {fr_ror:,.1f} MW")

roe9_hydro_total = sum(cap[c]["Hydro_total"] for c in ROE9_COUNTRIES)
roe9_pumped = roe9_hydro_total * 0.30  # same EU-wide IHA 2023 ratio as the original aggregate
roe9_conventional = roe9_hydro_total * 0.70
roe9_reservoir = roe9_conventional * RESERVOIR_SHARE
roe9_ror = roe9_conventional * RUN_OF_RIVER_SHARE
print(f"\nReduced ROE (9 countries) hydro total: {roe9_hydro_total:,.1f} MW "
      f"(was {summary['capacity_MW_by_tech']['Hydro_total']:,.1f} MW for all 10)")
print(f"  Pumped (30% EU-wide method, unchanged methodology): {roe9_pumped:,.1f} MW")
print(f"  Reservoir: {roe9_reservoir:,.1f} MW")
print(f"  Run-of-river: {roe9_ror:,.1f} MW")

print("\n" + "=" * 70)
print("4. CONVENTIONAL CAPACITY: France's own vs. reduced ROE (9-country sum)")
print("=" * 70)
for tech in ["Coal_and_manufactured_gases", "Natural_gas", "Oil", "Nuclear"]:
    fr_val = FR_CAP.get(tech, 0.0)
    roe9_val = sum(cap[c].get(tech, 0.0) for c in ROE9_COUNTRIES)
    print(f"{tech}: France={fr_val:,.1f} MW | ROE-9={roe9_val:,.1f} MW")

print("\n" + "=" * 70)
print("5. TRANSMISSION: DE<->FR real flow-derived capacity (Phase 36 methodology, this border only)")
print("=" * 70)
PERCENTILE = 0.98
out_flow = pd.read_csv(rf"{ENTSOE_DIR}\flow_DEtoFR_2023.csv", index_col=0).iloc[:, 0]
in_flow = pd.read_csv(rf"{ENTSOE_DIR}\flow_FRtoDE_2023.csv", index_col=0).iloc[:, 0]
de_to_fr_cap = out_flow.quantile(PERCENTILE)
fr_to_de_cap = in_flow.quantile(PERCENTILE)
print(f"DE->FR: P98={de_to_fr_cap:,.0f} MW (max={out_flow.max():,.0f})")
print(f"FR->DE: P98={fr_to_de_cap:,.0f} MW (max={in_flow.max():,.0f})")

# Original ROE-10 aggregate transmission (Phase 36) - subtract FR's share for the reduced zone.
ZONES_10 = ["AT", "BE", "CH", "CZ", "DK_1", "DK_2", "FR", "NL", "NO_2", "PL"]
orig_de_to_roe = sum(
    pd.read_csv(rf"{ENTSOE_DIR}\flow_DEto{z}_2023.csv", index_col=0).iloc[:, 0].quantile(PERCENTILE)
    for z in ZONES_10)
orig_roe_to_de = sum(
    pd.read_csv(rf"{ENTSOE_DIR}\flow_{z}toDE_2023.csv", index_col=0).iloc[:, 0].quantile(PERCENTILE)
    for z in ZONES_10)
de_to_roe9_cap = orig_de_to_roe - de_to_fr_cap
roe9_to_de_cap = orig_roe_to_de - fr_to_de_cap
print(f"\nOriginal DE<->ROE-10 total: DE->{orig_de_to_roe:,.0f} MW, ->DE {orig_roe_to_de:,.0f} MW")
print(f"Reduced DE<->ROE-9 (minus FR's share): DE->{de_to_roe9_cap:,.0f} MW, ->DE {roe9_to_de_cap:,.0f} MW")

for value, fname in [(de_to_fr_cap, "transfer_DEtoFR_realflow.csv"),
                      (fr_to_de_cap, "transfer_FRtoDE_realflow.csv"),
                      (de_to_roe9_cap, "transfer_DEtoROE9_realflow.csv"),
                      (roe9_to_de_cap, "transfer_ROE9toDE_realflow.csv")]:
    lines = [f"{ts.strftime('%Y-%m-%d_%H:%M:%S')};{value:.1f}" for ts in idx_2027]
    path = rf"{OUT_ROOT}\{fname}"
    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")
    print(f"  Saved {fname} (flat {value:,.0f} MW)")

print("\nDone. All real-derived France-zone and reduced-ROE-zone timeseries written.")
print(f"\nSUMMARY OF KEY NUMBERS FOR AGENT YAML FILES:")
print(f"France: demand={fr_demand_gwh*1000:,.0f} MWh/yr, coal={FR_CAP['Coal_and_manufactured_gases']:.3f} MW, "
      f"gas={FR_CAP['Natural_gas']:.3f} MW, oil={FR_CAP['Oil']:.3f} MW, nuclear={FR_CAP['Nuclear']:.1f} MW, "
      f"windon={FR_CAP['Wind_onshore']:.2f} MW, windoff={FR_CAP['Wind_offshore']:.1f} MW, solar={FR_CAP['Solar_PV']:.3f} MW, "
      f"pumped={FR_PUMPED_MW:.1f} MW, reservoir={fr_reservoir:.2f} MW, ror={fr_ror:.2f} MW")
roe9_coal = sum(cap[c]["Coal_and_manufactured_gases"] for c in ROE9_COUNTRIES)
roe9_gas = sum(cap[c]["Natural_gas"] for c in ROE9_COUNTRIES)
roe9_oil = sum(cap[c]["Oil"] for c in ROE9_COUNTRIES)
roe9_nuclear = sum(cap[c]["Nuclear"] for c in ROE9_COUNTRIES)
roe9_windon = sum(cap[c]["Wind_onshore"] for c in ROE9_COUNTRIES)
roe9_windoff = sum(cap[c]["Wind_offshore"] for c in ROE9_COUNTRIES)
roe9_solar = sum(cap[c]["Solar_PV"] for c in ROE9_COUNTRIES)
print(f"ROE-9: demand={roe9_demand_gwh*1000:,.0f} MWh/yr, coal={roe9_coal:.3f} MW, gas={roe9_gas:.3f} MW, "
      f"oil={roe9_oil:.3f} MW, nuclear={roe9_nuclear:.1f} MW, windon={roe9_windon:.3f} MW, "
      f"windoff={roe9_windoff:.1f} MW, solar={roe9_solar:.3f} MW, "
      f"pumped={roe9_pumped:.2f} MW, reservoir={roe9_reservoir:.2f} MW, ror={roe9_ror:.2f} MW")
print(f"Transmission: DE<->FR = {de_to_fr_cap:,.1f} / {fr_to_de_cap:,.1f} MW, "
      f"DE<->ROE9 = {de_to_roe9_cap:,.1f} / {roe9_to_de_cap:,.1f} MW")
