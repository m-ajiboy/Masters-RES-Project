"""Builds the 24 new real bilateral transmission-capacity timeseries files (12 ROE-ROE
country pairs, both directions) for the mesh-topology rebuild of Germany2027_MarketCoupling_
AllZones. Source: ENTSO-E's real ERAA 2024 PEMMDB NTC data (TY2026), 98th percentile of real
hourly values per border (_explore_bilateral_ntc.py) - the same real-data-grounded technique
already used throughout this project (Phase 35/36/44/46), now extended to the ROE-ROE borders
Phase 42/43's star topology never had. Phase 43's original DE-X transmission values are left
completely untouched, isolating "star vs. mesh topology" as the one new variable.
"""
import json
import pandas as pd

OUT_DIR = r"C:\Users\MuideenOA\Desktop\PyTut\Amiris\examples\backtest\Germany2027_MarketCoupling_AllZones_Mesh\timeseries"

with open(r"C:\Users\MuideenOA\maven-tools\eraa_data\bilateral_ntc_matrix.json") as f:
    matrix = json.load(f)

# The 12 real ROE-ROE pairs found (excluding DE, already covered by Phase 43's own real
# flow-derived DE-X values, left untouched)
PAIRS = [
    ("AT", "CH"), ("AT", "CZ"), ("BE", "FR"), ("BE", "NL"), ("CH", "FR"), ("CZ", "PL"),
    ("DK", "NL"), ("DK", "NO"), ("DK", "SE"), ("NL", "NO"), ("NO", "SE"), ("PL", "SE"),
]

idx = pd.date_range("2027-01-01", periods=8760, freq="h")

for a, b in PAIRS:
    for frm, to in [(a, b), (b, a)]:
        key = f"{frm}-{to}"
        if key not in matrix:
            print(f"WARNING: {key} not found in matrix, skipping")
            continue
        value = matrix[key]
        fname = f"transfer_{frm}to{to}_realNTC.csv"
        lines = [f"{ts.strftime('%Y-%m-%d_%H:%M:%S')};{value:.1f}" for ts in idx]
        with open(rf"{OUT_DIR}\{fname}", "w", encoding="utf-8") as f:
            f.write("\n".join(lines) + "\n")
        print(f"Saved {fname} (flat {value:,.0f} MW, real ERAA NTC, 98th percentile)")

print(f"\nDone - {2*len(PAIRS)} real bilateral transmission timeseries files saved.")
