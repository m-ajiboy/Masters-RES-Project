"""Extracts real DE<->ROE9 transmission capacity (NTC) from ENTSO-E's real ERAA 2024 PEMMDB
NTC files (TY2026/2028/2030, National Trends scenario, both HVAC and HVDC sheets), applying
the same 98th-percentile-of-real-hourly-values methodology already established in this
project (Phase 35/44, on real ENTSO-E flow data) - here on real NTC (actual grid capacity)
data instead, which is arguably a more direct measure than observed flow. Computes a real
growth RATE (2026->2028->2030) to apply to Phase 44's real 2024 flow-derived transmission
capacity baseline, consistent with the capacity/demand growth-rate technique already used.
"""
import pandas as pd
import json

NTC_DIR = r"C:\Users\MuideenOA\maven-tools\eraa_data\NTCs\NTCs"
YEARS = [2026, 2028, 2030]
ROE_PREFIXES = ["AT", "BE", "CH", "CZ", "DK", "FR", "NL", "NO", "PL", "SE"]
DE_PREFIX = "DE"


def find_de_roe_columns(header_row, from_row, to_row):
    """Returns list of (col_idx, direction) where direction is 'DE_to_ROE' or 'ROE_to_DE'."""
    matches = []
    for col in range(2, len(from_row)):
        frm = str(from_row[col])
        to = str(to_row[col])
        if frm.startswith(DE_PREFIX) and any(to.startswith(p) for p in ROE_PREFIXES):
            matches.append((col, "DE_to_ROE"))
        elif to.startswith(DE_PREFIX) and any(frm.startswith(p) for p in ROE_PREFIXES):
            matches.append((col, "ROE_to_DE"))
    return matches


results = {}
for year in YEARS:
    path = rf"{NTC_DIR}\PEMMDB_NationalTrends_NTCs Consolidated TY{year}.xlsx"
    de_to_roe_p98_sum = 0.0
    roe_to_de_p98_sum = 0.0
    borders_found = []
    for sheet in ["HVAC", "HVDC"]:
        raw = pd.read_excel(path, sheet_name=sheet, header=None)
        from_row = raw.iloc[8].tolist()
        to_row = raw.iloc[9].tolist()
        matches = find_de_roe_columns(raw.iloc[7].tolist(), from_row, to_row)
        if not matches:
            continue
        data = raw.iloc[16:].reset_index(drop=True)
        for col, direction in matches:
            series = pd.to_numeric(data[col], errors="coerce").dropna()
            if series.empty:
                continue
            p98 = series.quantile(0.98)
            borders_found.append((sheet, from_row[col], to_row[col], direction, p98))
            if direction == "DE_to_ROE":
                de_to_roe_p98_sum += p98
            else:
                roe_to_de_p98_sum += p98
    results[year] = {"DE_to_ROE": de_to_roe_p98_sum, "ROE_to_DE": roe_to_de_p98_sum, "borders": borders_found}
    print(f"\n{'='*70}\nTY{year}: {len(borders_found)} real DE<->ROE9 borders found\n{'='*70}")
    for sheet, frm, to, direction, p98 in borders_found:
        print(f"  [{sheet}] {frm}->{to} ({direction}): P98={p98:,.0f} MW")
    print(f"  TOTAL DE->ROE P98 sum: {de_to_roe_p98_sum:,.0f} MW")
    print(f"  TOTAL ROE->DE P98 sum: {roe_to_de_p98_sum:,.0f} MW")

print("\n" + "=" * 70)
print("GROWTH RATES (real ERAA NTC, 2026->2028->2030)")
print("=" * 70)
g_de_to_roe_2628 = results[2028]["DE_to_ROE"] / results[2026]["DE_to_ROE"]
g_de_to_roe_2830 = results[2030]["DE_to_ROE"] / results[2028]["DE_to_ROE"]
g_roe_to_de_2628 = results[2028]["ROE_to_DE"] / results[2026]["ROE_to_DE"]
g_roe_to_de_2830 = results[2030]["ROE_to_DE"] / results[2028]["ROE_to_DE"]
print(f"DE->ROE: 2026->2028 x{g_de_to_roe_2628:.4f}, 2028->2030 x{g_de_to_roe_2830:.4f}")
print(f"ROE->DE: 2026->2028 x{g_roe_to_de_2628:.4f}, 2028->2030 x{g_roe_to_de_2830:.4f}")

# Apply to Phase 44's real 2024 flow-derived baseline
BASELINE_DE_TO_ROE = 20495.0
BASELINE_ROE_TO_DE = 22954.0
proj_2028_de_to_roe = BASELINE_DE_TO_ROE * g_de_to_roe_2628
proj_2028_roe_to_de = BASELINE_ROE_TO_DE * g_roe_to_de_2628
g_de_to_roe_2629 = g_de_to_roe_2628 * (g_de_to_roe_2830 ** 0.5)
g_roe_to_de_2629 = g_roe_to_de_2628 * (g_roe_to_de_2830 ** 0.5)
proj_2029_de_to_roe = BASELINE_DE_TO_ROE * g_de_to_roe_2629
proj_2029_roe_to_de = BASELINE_ROE_TO_DE * g_roe_to_de_2629

print(f"\nProjected (applied to real 2024 baseline {BASELINE_DE_TO_ROE:,.0f}/{BASELINE_ROE_TO_DE:,.0f} MW):")
print(f"  2028: DE->ROE {proj_2028_de_to_roe:,.0f} MW, ROE->DE {proj_2028_roe_to_de:,.0f} MW")
print(f"  2029: DE->ROE {proj_2029_de_to_roe:,.0f} MW, ROE->DE {proj_2029_roe_to_de:,.0f} MW")

out = {
    "methodology": "ERAA 2024 PEMMDB NTC (National Trends), 98th percentile of real hourly values per border, "
                    "growth rate 2026->2028->2030 applied to Phase 44's real 2024 flow-derived baseline.",
    "baseline_2024": {"DE_to_ROE": BASELINE_DE_TO_ROE, "ROE_to_DE": BASELINE_ROE_TO_DE},
    "projected_2028": {"DE_to_ROE": proj_2028_de_to_roe, "ROE_to_DE": proj_2028_roe_to_de},
    "projected_2029": {"DE_to_ROE": proj_2029_de_to_roe, "ROE_to_DE": proj_2029_roe_to_de},
}
with open(r"C:\Users\MuideenOA\maven-tools\eraa_data\ntc_growth_projection.json", "w") as f:
    json.dump(out, f, indent=2)
print("\nSaved to maven-tools/eraa_data/ntc_growth_projection.json")
