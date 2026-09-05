"""ENTSO-E is back up but appears to enforce a stricter request-size limit while stabilizing
post-outage - confirmed directly: a full-year Cross-Border Physical Flows request fails with
400 Bad Request, while a 2-day window for the same pair succeeds. Fetches in MONTHLY chunks
instead (a known-working window size) and concatenates. Covers DE/LU against each of
Germany's 11 real neighbouring bidding zones (both directions), plus Switzerland's (CH)
annual load and installed generation capacity - backfilling the one gap in the
Eurostat-sourced Rest-of-Europe dataset (Phase 33). Saved under
examples/backtest/RestOfEurope2023/raw_entsoe/, following the existing raw_eurostat/
convention. Source data is 15-minute resolution - resampled to hourly (mean) to match this
project's convention throughout.
"""
import os
import time
import json
import pandas as pd
from entsoe import EntsoePandasClient

TOKEN_FILE = r"C:\Users\MuideenOA\Desktop\PyTut\Amiris\Token.txt"
OUT_DIR = r"C:\Users\MuideenOA\Desktop\PyTut\Amiris\examples\backtest\RestOfEurope2023\raw_entsoe"
os.makedirs(OUT_DIR, exist_ok=True)

with open(TOKEN_FILE, encoding="utf-8") as f:
    lines = [l.strip() for l in f if l.strip()]
token = lines[lines.index("Entso Token") + 1]

client = EntsoePandasClient(api_key=token)

ZONES = ["AT", "BE", "CH", "CZ", "DK_1", "DK_2", "FR", "NO_2", "NL", "PL", "SE_4"]
DE = "DE_LU"

MONTH_STARTS = pd.date_range("2023-01-01", "2024-01-01", freq="MS", tz="UTC")
MONTHS = list(zip(MONTH_STARTS[:-1], MONTH_STARTS[1:]))


def fetch_monthly_flow(source, sink):
    """Fetch a full year of crossborder flow in monthly chunks, resampled to hourly."""
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
print("CROSS-BORDER PHYSICAL FLOWS (monthly-chunked): DE/LU <-> 11 neighbouring zones")
print("=" * 70)
flow_results = {}
for zone in ZONES:
    print(f"\n{zone}:")
    de_to_zone = fetch_monthly_flow(DE, zone)
    if de_to_zone is not None:
        save(de_to_zone, os.path.join(OUT_DIR, f"flow_DEto{zone}_2023.csv"))
        flow_results[f"DE_to_{zone}"] = float(de_to_zone.sum())
    else:
        flow_results[f"DE_to_{zone}"] = None

    zone_to_de = fetch_monthly_flow(zone, DE)
    if zone_to_de is not None:
        save(zone_to_de, os.path.join(OUT_DIR, f"flow_{zone}toDE_2023.csv"))
        flow_results[f"{zone}_to_DE"] = float(zone_to_de.sum())
    else:
        flow_results[f"{zone}_to_DE"] = None

print("\n" + "=" * 70)
print("SWITZERLAND (CH) BACKFILL: annual load and installed capacity (monthly-chunked)")
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
    ch_load.to_csv(os.path.join(OUT_DIR, "ch_load_2023.csv"))
    ch_annual_gwh = float(ch_load.iloc[:, 0].sum() if hasattr(ch_load, "columns") else ch_load.sum())
    # ENTSO-E load is instantaneous MW readings at 15-min/hourly resolution; approximate
    # annual GWh via mean MW * hours in year (more robust than a raw sum of mixed-resolution data)
    hours_covered = (ch_load.index[-1] - ch_load.index[0]).total_seconds() / 3600
    mean_mw = float(ch_load.mean().iloc[0] if hasattr(ch_load, "columns") else ch_load.mean())
    ch_annual_gwh = mean_mw * 8760 / 1000
    print(f"  CH load saved: {len(ch_load)} rows, mean {mean_mw:.0f} MW -> ~{ch_annual_gwh:,.0f} GWh/year")
else:
    print("  CH load: all chunks failed")

try:
    ch_cap_agg = client.query_installed_generation_capacity("CH", start=pd.Timestamp("2023-01-01", tz="UTC"), end=pd.Timestamp("2024-01-01", tz="UTC"))
    ch_cap_agg.to_csv(os.path.join(OUT_DIR, "ch_capacity_by_type_2023.csv"))
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
