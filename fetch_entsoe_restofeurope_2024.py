"""2024-base variant of fetch_entsoe_restofeurope.py. Covers DE/LU against each of Germany's
11 real neighbouring bidding zones (both directions), plus Switzerland's (CH) annual load and
installed generation capacity, for real calendar-year 2024 instead of 2023 - live-confirmed
available through December 2024 (2026-09-17 check). Same monthly-chunked fetch pattern
(ENTSO-E rejects full-year requests). Saved under
examples/backtest/RestOfEurope2024/raw_entsoe/, fully separate from the 2023 vintage.
"""
import os
import time
import json
import pandas as pd
from entsoe import EntsoePandasClient

TOKEN_FILE = r"C:\Users\MuideenOA\Desktop\PyTut\Amiris\Token.txt"
OUT_DIR = r"C:\Users\MuideenOA\Desktop\PyTut\Amiris\examples\backtest\RestOfEurope2024\raw_entsoe"
os.makedirs(OUT_DIR, exist_ok=True)

with open(TOKEN_FILE, encoding="utf-8") as f:
    lines = [l.strip() for l in f if l.strip()]
token = lines[lines.index("Entso Token") + 1]

client = EntsoePandasClient(api_key=token)

ZONES = ["AT", "BE", "CH", "CZ", "DK_1", "DK_2", "FR", "NO_2", "NL", "PL", "SE_4"]
DE = "DE_LU"

MONTH_STARTS = pd.date_range("2024-01-01", "2025-01-01", freq="MS", tz="UTC")
MONTHS = list(zip(MONTH_STARTS[:-1], MONTH_STARTS[1:]))


def fetch_monthly_flow(source, sink):
    parts = []
    for start, end in MONTHS:
        try:
            chunk = client.query_crossborder_flows(source, sink, start=start, end=end)
            parts.append(chunk)
            time.sleep(0.8)
        except Exception as e:
            print(f"    chunk {start.date()} FAILED: {e}")
            return None
    if not parts:
        return None
    full = pd.concat(parts).sort_index()
    full.index = full.index.tz_localize(None)
    hourly = full.resample("h").mean()
    return hourly


def save(series, path):
    series.to_csv(path, header=["MW"])
    print(f"    saved {path} ({len(series)} hourly rows)")


print("=" * 70)
print("CROSS-BORDER PHYSICAL FLOWS (monthly-chunked): DE/LU <-> 11 neighbouring zones - 2024")
print("=" * 70)
flow_results = {}
for zone in ZONES:
    print(f"\n{zone}:")
    de_to_zone = fetch_monthly_flow(DE, zone)
    if de_to_zone is not None:
        save(de_to_zone, os.path.join(OUT_DIR, f"flow_DEto{zone}_2024.csv"))
        flow_results[f"DE_to_{zone}"] = float(de_to_zone.sum())
    else:
        flow_results[f"DE_to_{zone}"] = None

    zone_to_de = fetch_monthly_flow(zone, DE)
    if zone_to_de is not None:
        save(zone_to_de, os.path.join(OUT_DIR, f"flow_{zone}toDE_2024.csv"))
        flow_results[f"{zone}_to_DE"] = float(zone_to_de.sum())
    else:
        flow_results[f"{zone}_to_DE"] = None

print("\n" + "=" * 70)
print("SWITZERLAND (CH) BACKFILL: annual load and installed capacity (monthly-chunked) - 2024")
print("=" * 70)
ch_load_parts = []
for start, end in MONTHS:
    try:
        chunk = client.query_load("CH", start=start, end=end)
        ch_load_parts.append(chunk)
        time.sleep(0.8)
    except Exception as e:
        print(f"  CH load chunk {start.date()} FAILED: {e}")

ch_annual_gwh = None
if ch_load_parts:
    ch_load = pd.concat(ch_load_parts).sort_index()
    ch_load.index = ch_load.index.tz_localize(None)
    ch_load.to_csv(os.path.join(OUT_DIR, "ch_load_2024.csv"))
    hours_covered = (ch_load.index[-1] - ch_load.index[0]).total_seconds() / 3600
    mean_mw = float(ch_load.mean().iloc[0] if hasattr(ch_load, "columns") else ch_load.mean())
    ch_annual_gwh = mean_mw * 8760 / 1000
    print(f"  CH load saved: {len(ch_load)} rows, mean {mean_mw:.0f} MW -> ~{ch_annual_gwh:,.0f} GWh/year")
else:
    print("  CH load: all chunks failed")

try:
    ch_cap_agg = client.query_installed_generation_capacity("CH", start=pd.Timestamp("2024-01-01", tz="UTC"), end=pd.Timestamp("2025-01-01", tz="UTC"))
    ch_cap_agg.to_csv(os.path.join(OUT_DIR, "ch_capacity_by_type_2024.csv"))
    print("  CH capacity by production type saved:")
    print(ch_cap_agg)
    ch_capacity = ch_cap_agg.to_dict()
except Exception as e:
    print(f"  CH capacity by type FAILED: {e}")
    ch_capacity = None

with open(os.path.join(OUT_DIR, "..", "entsoe_backfill_summary.json"), "w") as f:
    json.dump({
        "flows_MWh": flow_results,
        "ch_annual_demand_GWh": ch_annual_gwh,
        "ch_capacity_MW": ch_capacity,
    }, f, indent=2, default=str)
print(f"\nSaved summary to entsoe_backfill_summary.json")
print("\nDone.")
