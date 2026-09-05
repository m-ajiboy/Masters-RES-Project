"""Second resume pass: only DE<->SE_4 remain (confirmed working in isolation - the earlier
failure was transient ENTSO-E flakiness, not a real code problem). Fetches those two, then
rebuilds the final summary from all already-saved CSVs (fixing the prior run's JSON
serialization bug - Timestamp keys from CH capacity's to_dict() are converted to strings).
"""
import os
import time
import json
import pandas as pd
from entsoe import EntsoePandasClient

TOKEN_FILE = r"C:\Users\MuideenOA\Desktop\PyTut\Amiris\Token.txt"
OUT_DIR = r"C:\Users\MuideenOA\Desktop\PyTut\Amiris\examples\backtest\RestOfEurope2023\raw_entsoe"

with open(TOKEN_FILE, encoding="utf-8") as f:
    lines = [l.strip() for l in f if l.strip()]
token = lines[lines.index("Entso Token") + 1]

client = EntsoePandasClient(api_key=token)
DE = "DE_LU"

MONTH_STARTS = pd.date_range("2023-01-01", "2024-01-01", freq="MS", tz="UTC")
MONTHS = list(zip(MONTH_STARTS[:-1], MONTH_STARTS[1:]))


def log(msg):
    print(msg, flush=True)


def fetch_monthly_flow(source, sink, label):
    parts = []
    for i, (start, end) in enumerate(MONTHS, start=1):
        try:
            chunk = client.query_crossborder_flows(source, sink, start=start, end=end)
            parts.append(chunk)
            log(f"    [{label}] month {i}/12 ({start.strftime('%Y-%m')}) OK, {len(chunk)} rows")
            time.sleep(1.0)
        except Exception as e:
            log(f"    [{label}] month {i}/12 ({start.strftime('%Y-%m')}) FAILED: {e} - retrying once")
            time.sleep(3.0)
            try:
                chunk = client.query_crossborder_flows(source, sink, start=start, end=end)
                parts.append(chunk)
                log(f"    [{label}] month {i}/12 retry OK, {len(chunk)} rows")
                time.sleep(1.0)
            except Exception as e2:
                log(f"    [{label}] month {i}/12 retry FAILED too: {e2}")
                return None
    if not parts:
        return None
    full = pd.concat(parts).sort_index()
    full.index = full.index.tz_localize(None)
    hourly = full.resample("h").mean()
    return hourly


def save(series, path):
    series.to_csv(path, header=["MW"])
    log(f"    saved {path} ({len(series)} hourly rows)")


REMAINING = [("DE", "SE_4"), ("SE_4", "DE")]

log("=" * 70)
log("FETCHING THE 2 REMAINING PAIRS: DE<->SE_4")
log("=" * 70)
for source, sink in REMAINING:
    fname = f"flow_{source}to{sink}_2023.csv"
    out_path = os.path.join(OUT_DIR, fname)
    if os.path.exists(out_path):
        log(f"\n{source}->{sink}: already saved, skipping")
        continue
    log(f"\n{source}->{sink}:")
    result = fetch_monthly_flow(source, sink, f"{source}->{sink}")
    if result is not None:
        save(result, out_path)
    else:
        log(f"    {source}->{sink} FAILED entirely")

# --- Rebuild final summary from ALL saved files ---
log("\n" + "=" * 70)
log("BUILDING FINAL SUMMARY (from all saved files)")
log("=" * 70)
ZONES = ["AT", "BE", "CH", "CZ", "DK_1", "DK_2", "FR", "NO_2", "NL", "PL", "SE_4"]
flow_totals = {}
for zone in ZONES:
    for direction, fname in [(f"DE_to_{zone}", f"flow_DEto{zone}_2023.csv"),
                              (f"{zone}_to_DE", f"flow_{zone}toDE_2023.csv")]:
        path = os.path.join(OUT_DIR, fname)
        if os.path.exists(path):
            s = pd.read_csv(path, index_col=0)
            flow_totals[direction] = float(s.iloc[:, 0].sum())
        else:
            flow_totals[direction] = None

ch_load_path = os.path.join(OUT_DIR, "ch_load_2023.csv")
ch_annual_gwh = None
if os.path.exists(ch_load_path):
    existing = pd.read_csv(ch_load_path, index_col=0)
    mean_mw = float(existing.iloc[:, 0].mean())
    ch_annual_gwh = mean_mw * 8760 / 1000

ch_cap_path = os.path.join(OUT_DIR, "ch_capacity_by_type_2023.csv")
ch_capacity = None
if os.path.exists(ch_cap_path):
    cap_df = pd.read_csv(ch_cap_path, index_col=0)
    ch_capacity = {col: float(cap_df[col].iloc[0]) for col in cap_df.columns}

with open(os.path.join(OUT_DIR, "..", "entsoe_backfill_summary.json"), "w") as f:
    json.dump({
        "flows_MWh_annual_total": flow_totals,
        "ch_annual_demand_GWh": ch_annual_gwh,
        "ch_capacity_MW": ch_capacity,
    }, f, indent=2)
log("Saved entsoe_backfill_summary.json")

missing = [k for k, v in flow_totals.items() if v is None]
log(f"\nFlow pairs complete: {22 - len(missing)}/22")
if missing:
    log(f"Still missing: {missing}")
log(f"CH annual demand: {ch_annual_gwh:,.0f} GWh" if ch_annual_gwh else "CH annual demand: MISSING")
log(f"CH capacity: {ch_capacity}")
log("\nDone.")
