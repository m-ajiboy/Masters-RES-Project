"""2024-base variant of build_real_transmission_capacity.py. Same 98th-percentile-of-real-
flow methodology, now on real 2024 ENTSO-E cross-border flow data. Checks all 11 real
neighbouring zones (not just the 10 used in the 2023 build) - SE_4 failed in the 2023 fetch
as a documented, confirmed-genuine gap; ENTSO-E is now confirmed working normally
(2026-09-17), so if SE_4 succeeded this time, this build closes that one remaining gap rather
than carrying it forward unnecessarily."""
import os
import pandas as pd

ENTSOE_DIR = r"C:\Users\MuideenOA\Desktop\PyTut\Amiris\examples\backtest\RestOfEurope2024\raw_entsoe"
ALL_ZONES = ["AT", "BE", "CH", "CZ", "DK_1", "DK_2", "FR", "NL", "NO_2", "PL", "SE_4"]
PERCENTILE = 0.98

de_to_roe_estimates = {}
roe_to_de_estimates = {}
zones_used = []
zones_missing = []

for zone in ALL_ZONES:
    out_path = rf"{ENTSOE_DIR}\flow_DEto{zone}_2024.csv"
    in_path = rf"{ENTSOE_DIR}\flow_{zone}toDE_2024.csv"
    if not (os.path.exists(out_path) and os.path.exists(in_path)):
        print(f"{zone}: MISSING (not fetched or fetch failed)")
        zones_missing.append(zone)
        continue
    out_flow = pd.read_csv(out_path, index_col=0).iloc[:, 0]
    in_flow = pd.read_csv(in_path, index_col=0).iloc[:, 0]
    de_to_roe_estimates[zone] = out_flow.quantile(PERCENTILE)
    roe_to_de_estimates[zone] = in_flow.quantile(PERCENTILE)
    zones_used.append(zone)
    print(f"{zone}: DE->  P{int(PERCENTILE*100)}={de_to_roe_estimates[zone]:,.0f} MW "
          f"(max={out_flow.max():,.0f}) | ->DE P{int(PERCENTILE*100)}={roe_to_de_estimates[zone]:,.0f} MW "
          f"(max={in_flow.max():,.0f})")

total_de_to_roe = sum(de_to_roe_estimates.values())
total_roe_to_de = sum(roe_to_de_estimates.values())
print(f"\nZones used ({len(zones_used)}): {zones_used}")
print(f"Zones missing ({len(zones_missing)}): {zones_missing}")
print(f"\nTotal DE->ROE capacity estimate: {total_de_to_roe:,.0f} MW")
print(f"Total ROE->DE capacity estimate: {total_roe_to_de:,.0f} MW")
print(f"\nFor comparison, the 2023-base build (10 zones, SE_4 missing) was "
      f"21,593 MW (DE->ROE) / 22,012 MW (ROE->DE).")

OUT_DIR = r"C:\Users\MuideenOA\Desktop\PyTut\Amiris\examples\backtest\Germany2027_MarketCoupling_ROEFlex_2024base\timeseries"
os.makedirs(OUT_DIR, exist_ok=True)

idx = pd.date_range("2027-01-01", periods=8760, freq="h")
for value, fname in [(total_de_to_roe, "transfer_DEtoROE_realflow_2024base.csv"),
                      (total_roe_to_de, "transfer_ROEtoDE_realflow_2024base.csv")]:
    lines = [f"{ts.strftime('%Y-%m-%d_%H:%M:%S')};{value:.1f}" for ts in idx]
    path = rf"{OUT_DIR}\{fname}"
    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")
    print(f"Saved {path} (flat {value:,.0f} MW, real-2024-flow-derived)")
