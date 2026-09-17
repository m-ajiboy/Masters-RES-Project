"""Extracts the REAL bilateral (country-to-country, not just DE-to-X) transmission capacity
matrix among the 10 real ROE neighbours from ENTSO-E's real ERAA 2024 PEMMDB NTC data
(already downloaded and verified in Phase 46) - the data needed for a genuine mesh topology,
as opposed to Phase 42/43's star topology (each zone linked only to Germany), which Phase 45
diagnosed as the real cause of France's stranded-surplus problem.
"""
import pandas as pd

NTC_DIR = r"C:\Users\MuideenOA\maven-tools\eraa_data\NTCs\NTCs"
YEAR = 2026  # nearest-term real ERAA year to now
COUNTRIES = ["AT", "BE", "CH", "CZ", "DK", "FR", "NL", "NO", "PL", "SE", "DE"]


def find_country_columns(from_row, to_row):
    """Returns {(from_country, to_country): col_idx} for every column whose zone codes
    both start with one of our 11 real country prefixes (any pair, not just DE-involving)."""
    matches = {}
    for col in range(2, len(from_row)):
        frm_zone = str(from_row[col])
        to_zone = str(to_row[col])
        frm_country = next((c for c in COUNTRIES if frm_zone.startswith(c)), None)
        to_country = next((c for c in COUNTRIES if to_zone.startswith(c)), None)
        if frm_country and to_country and frm_country != to_country:
            matches[(frm_country, to_country)] = matches.get((frm_country, to_country), []) + [col]
    return matches


path = rf"{NTC_DIR}\PEMMDB_NationalTrends_NTCs Consolidated TY{YEAR}.xlsx"
pair_p98 = {}
pair_borders_used = {}
for sheet in ["HVAC", "HVDC"]:
    raw = pd.read_excel(path, sheet_name=sheet, header=None)
    from_row = raw.iloc[8].tolist()
    to_row = raw.iloc[9].tolist()
    matches = find_country_columns(from_row, to_row)
    data = raw.iloc[16:].reset_index(drop=True)
    for (frm, to), cols in matches.items():
        total_p98 = 0.0
        borders = []
        for col in cols:
            series = pd.to_numeric(data[col], errors="coerce").dropna()
            if series.empty:
                continue
            p98 = series.quantile(0.98)
            total_p98 += p98
            borders.append((sheet, from_row[col], to_row[col], p98))
        if borders:
            pair_p98[(frm, to)] = pair_p98.get((frm, to), 0.0) + total_p98
            pair_borders_used.setdefault((frm, to), []).extend(borders)

print(f"Real bilateral NTC pairs found among the 11 countries (TY{YEAR}, 98th percentile, MW):")
print("=" * 70)
seen = set()
for (frm, to), total in sorted(pair_p98.items()):
    if (to, frm) in seen:
        continue
    seen.add((frm, to))
    reverse = pair_p98.get((to, frm), None)
    print(f"{frm} <-> {to}: {frm}->{to} = {total:,.0f} MW"
          + (f", {to}->{frm} = {reverse:,.0f} MW" if reverse else " (no reverse pair found)"))

print()
print("=" * 70)
print("Bilateral pairs among the 10 ROE countries specifically (excluding DE, already covered by Phase 44/46):")
print("=" * 70)
roe_only = [(f, t) for (f, t) in pair_p98 if f != "DE" and t != "DE"]
seen2 = set()
for (frm, to) in sorted(roe_only):
    if (to, frm) in seen2:
        continue
    seen2.add((frm, to))
    print(f"  {frm} <-> {to}: {pair_p98[(frm, to)]:,.0f} / {pair_p98.get((to, frm), 0):,.0f} MW")

print(f"\nTotal distinct ROE-ROE bilateral pairs found: {len(seen2)}")

import json
out = {f"{f}-{t}": v for (f, t), v in pair_p98.items()}
with open(r"C:\Users\MuideenOA\maven-tools\eraa_data\bilateral_ntc_matrix.json", "w") as f:
    json.dump(out, f, indent=2)
print(f"\nSaved full matrix to maven-tools/eraa_data/bilateral_ntc_matrix.json")
