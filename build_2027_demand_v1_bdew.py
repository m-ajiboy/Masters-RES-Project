"""Builds load.csv V1 for the Germany2027 scenario: a single BDEW H0 standard load profile
scaled to the FULL combined Brainpool demand total (all four components summed), per the
user's direction to use "the BDEW way for all the demands" as the first, simpler version.

Combined annual total = Inflexible base + Electrolysis + E-mobility + Heat pumps
                       (Net Exports and Pumped Storage Losses are excluded: the former is a
                       cross-border trade balance handled separately per the no-import decision
                       for this build; the latter is already implicit in AMIRIS's storage agents'
                       own charging/discharging efficiency and would double-count if added here.)

Method: demandlib's BDEW ElecSlp.get_scaled_power_profiles(), which implements the real BDEW
Standardlastprofil methodology (12 representative daily curves by season x day-type, with H0's
day-of-year dynamization applied automatically) at 15-minute resolution, then resampled to
AMIRIS's expected hourly resolution.
"""
from pathlib import Path
import openpyxl
from demandlib import bdew

ROOT = Path(__file__).parent
OUT = ROOT / "examples" / "backtest" / "Germany2027" / "timeseries"
XLSX = ROOT / "Amiris_Inputdata_EN.xlsx"


def get_combined_demand_mwh():
    wb = openpyxl.load_workbook(XLSX, data_only=True)
    ws = wb["Capacity"]
    row = [c.value for c in ws[3]]
    # Section C (Demand, TWh) starts at column index 31 in the row (0-based), per the
    # translated header layout established when this file was first inspected.
    headers = [c.value for c in ws[2]]
    demand_start = headers.index("Inflexible Gross Electricity Demand")
    inflexible = row[demand_start]
    electrolysis = row[demand_start + 1]
    e_mobility = row[demand_start + 2]
    heat_pumps = row[demand_start + 3]
    total_twh = inflexible + electrolysis + e_mobility + heat_pumps
    print(f"  Inflexible base:  {inflexible:>10.2f} TWh")
    print(f"  Electrolysis:     {electrolysis:>10.2f} TWh")
    print(f"  E-mobility:       {e_mobility:>10.2f} TWh")
    print(f"  Heat pumps:       {heat_pumps:>10.2f} TWh")
    print(f"  Combined total:   {total_twh:>10.2f} TWh")
    return total_twh * 1_000_000  # TWh -> MWh


def build():
    total_mwh = get_combined_demand_mwh()

    slp = bdew.ElecSlp(2027)
    # get_scaled_power_profiles expects annual demand in kWh; conversion_factor=4 matches
    # its 15-minute (quarter-hour) internal resolution.
    profile_kw = slp.get_scaled_power_profiles({"h0": total_mwh * 1000})["h0"]

    # Resample 15-min average power (kW) to hourly average power (kW) = hourly energy (kWh),
    # then convert kW -> MW to match AMIRIS's expected unit.
    hourly_mw = profile_kw.resample("1h").mean() / 1000.0

    lines = []
    for ts, val in hourly_mw.items():
        ts_str = ts.strftime("%Y-%m-%d_%H:%M:%S")
        lines.append(f"{ts_str};{val:.4f}")

    out_path = OUT / "load_v1_bdew.csv"
    out_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"  built load_v1_bdew.csv ({len(lines)} hourly rows)")
    print(f"  check: sum of hourly MW values / 1e6 = {hourly_mw.sum()/1_000_000:.4f} TWh "
          f"(should match combined total above)")


if __name__ == "__main__":
    build()
