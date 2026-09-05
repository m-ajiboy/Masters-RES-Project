"""Builds all timeseries CSVs for the Germany2027 AMIRIS scenario.

Sources:
  - Amiris_Inputdata_EN.xlsx (Brainpool 2027 data): Variable_cost, feedinprofile sheets
  - examples/backtest/Germany2019/timeseries/*.csv (AMIRIS's own validated data): outages,
    must-run, offshore wind profile, run-of-river profile, biomass profile

Decisions applied (per user's 2026-08-10 direction):
  1. Outage/must-run: reuse AMIRIS's own 2019 files, re-dated 2019->2027 (month/day/time and
     values unchanged - only the calendar year label shifts).
  2. Wind offshore: reuse AMIRIS's own profile as-is. Validated: implies 37.1% annual capacity
     factor, which sits inside the real German offshore fleet's 37-45% range (EnergyNumbers.info,
     Fraunhofer) - no adjustment needed.
  3/4/5 (subsidy, storage duration, cross-border): handled in the agents-build script, not here.

Unit conversions:
  - Hard coal: USD/tonne -> EUR/MWh(thermal), using 8.141 MWh/tonne (standard calorific
    equivalent, ~29.3 GJ/t) and the file's own USD/EUR monthly exchange rate.
  - Oil (Brent): USD/barrel -> EUR/MWh(thermal), using 1.70 MWh/barrel (~5.8 MMBtu/barrel).
  - Natural gas: 'Natural Gas Germany [EUR/MWh]' column used directly, already in the right unit.
  - EUA (CO2): used directly, already EUR/tCO2, AMIRIS's expected unit.
  - Nuclear/Lignite fuel cost: not present in Brainpool data; AMIRIS's own flat estimates
    (2.00 / 5.00 EUR/MWh) are carried over, consistent with AMIRIS's own scenario convention
    of treating these as internal estimates rather than market-quoted series. Nuclear is moot
    (0 GW capacity in 2027) and is omitted from the built scenario entirely.
"""
import shutil
from pathlib import Path
import openpyxl

ROOT = Path(__file__).parent
SRC_2019 = ROOT / "examples" / "backtest" / "Germany2019" / "timeseries"
OUT = ROOT / "examples" / "backtest" / "Germany2027" / "timeseries"
XLSX = ROOT / "Amiris_Inputdata_EN.xlsx"

COAL_MWH_PER_TONNE = 8.141
OIL_MWH_PER_BARREL = 1.70


def ensure_out():
    OUT.mkdir(parents=True, exist_ok=True)


def redate_timeseries(src_name, dst_name, year_map):
    """Copies a semicolon-delimited AMIRIS timeseries CSV, replacing the leading 4-digit
    year in each timestamp per year_map (e.g. {'2019':'2027','2020':'2028','2021':'2029'}),
    leaving month/day/time and the value column untouched."""
    src = SRC_2019 / src_name
    lines = src.read_text(encoding="utf-8").splitlines()
    out_lines = []
    for line in lines:
        if not line.strip():
            continue
        ts, val = line.split(";", 1)
        yr = ts[:4]
        new_yr = year_map.get(yr, yr)
        out_lines.append(f"{new_yr}{ts[4:]};{val}")
    (OUT / dst_name).write_text("\n".join(out_lines) + "\n", encoding="utf-8")
    print(f"  redated {src_name} -> {dst_name} ({len(out_lines)} rows)")


def copy_unchanged(src_name, dst_name=None):
    dst_name = dst_name or src_name
    shutil.copy(SRC_2019 / src_name, OUT / dst_name)
    print(f"  copied {src_name} -> {dst_name} (unchanged)")


def load_variable_cost():
    wb = openpyxl.load_workbook(XLSX, data_only=True)
    ws = wb["Variable_cost"]
    headers = [c.value for c in ws[1]]
    headers[0] = "Date"  # row 1's own label for column A is a units artifact, not "Date"
    rows = []
    for r in ws.iter_rows(min_row=3, values_only=True):
        if r[0] is None:
            continue
        rows.append(dict(zip(headers, r)))
    return rows


def build_fuel_and_co2_prices():
    rows = load_variable_cost()
    hard_coal_lines, oil_lines, gas_lines, eua_lines = [], [], [], []

    for row in rows:
        dt = row["Date"]
        ts = dt.strftime("%Y-%m-%d_00:00:00")
        usd_per_eur = row["USD Exchange Rate [USD/EUR]"]

        coal_usd_t = row["Hard Coal [USD/tonne]"]
        coal_eur_mwh = (coal_usd_t / usd_per_eur) / COAL_MWH_PER_TONNE
        hard_coal_lines.append(f"{ts};{coal_eur_mwh:.4f}")

        oil_usd_bbl = row["Crude Oil Brent [USD/barrel]"]
        oil_eur_mwh = (oil_usd_bbl / usd_per_eur) / OIL_MWH_PER_BARREL
        oil_lines.append(f"{ts};{oil_eur_mwh:.4f}")

        gas_eur_mwh = row["Natural Gas Germany [EUR/MWh]"]
        gas_lines.append(f"{ts};{gas_eur_mwh:.4f}")

        eua_eur_t = row["EUA - EU Emission Allowance [EUR/tCO2]"]
        eua_lines.append(f"{ts};{eua_eur_t:.4f}")

    # Trailing sentinel rows for fameio's end-of-year interpolation, matching AMIRIS's own
    # convention seen in the 2019 files (a zero-ish continuation row at the following Jan 1).
    last_year = rows[-1]["Date"].year
    for series, last_val in [
        (hard_coal_lines, hard_coal_lines[-1].split(";")[1]),
        (oil_lines, oil_lines[-1].split(";")[1]),
        (gas_lines, gas_lines[-1].split(";")[1]),
        (eua_lines, eua_lines[-1].split(";")[1]),
    ]:
        series.append(f"{last_year + 1}-01-01_00:00:00;{last_val}")

    (OUT / "hard_coal_price.csv").write_text("\n".join(hard_coal_lines) + "\n", encoding="utf-8")
    (OUT / "oil_price.csv").write_text("\n".join(oil_lines) + "\n", encoding="utf-8")
    (OUT / "natural_gas_price.csv").write_text("\n".join(gas_lines) + "\n", encoding="utf-8")
    (OUT / "co2_price.csv").write_text("\n".join(eua_lines) + "\n", encoding="utf-8")
    print(f"  built hard_coal_price.csv, oil_price.csv, natural_gas_price.csv, co2_price.csv "
          f"({len(rows)} monthly rows each + 1 sentinel)")


def load_feedinprofile():
    wb = openpyxl.load_workbook(XLSX, data_only=True)
    ws = wb["feedinprofile"]
    headers = [c.value for c in ws[1]]
    rows = []
    for r in ws.iter_rows(min_row=2, values_only=True):
        rows.append(dict(zip(headers, r)))
    return rows


def build_solar_profiles():
    """Builds TWO separate solar profiles (openfield/Grid-Feed-in and rooftop/Prosuming),
    since the two use different AMIRIS SupportInstrument mechanisms (MPVAR vs FIT) and
    therefore must stay as separate operator agents, each with its own real capacity and
    profile shape, rather than one blended agent."""
    rows = load_feedinprofile()
    import datetime
    dt = datetime.datetime(2027, 1, 1, 0, 0, 0)
    openfield_lines, rooftop_lines = [], []
    for row in rows:
        openfield_avg = (row["PV_openfield_north"] + row["PV_openfield_east"]
                          + row["PV_openfield_middle"] + row["PV_openfield_swest"]) / 4.0
        rooftop_avg = (row["PV_rooftop_north"] + row["PV_rooftop_east"]
                       + row["PV_rooftop_middle"] + row["PV_rooftop_swest"]) / 4.0
        ts = dt.strftime("%Y-%m-%d_%H:%M:%S")
        openfield_lines.append(f"{ts};{openfield_avg:.6f}")
        rooftop_lines.append(f"{ts};{rooftop_avg:.6f}")
        dt += datetime.timedelta(hours=1)

    (OUT / "solar_openfield_profile.csv").write_text("\n".join(openfield_lines) + "\n", encoding="utf-8")
    (OUT / "solar_rooftop_profile.csv").write_text("\n".join(rooftop_lines) + "\n", encoding="utf-8")
    print(f"  built solar_openfield_profile.csv and solar_rooftop_profile.csv "
          f"({len(openfield_lines)} hourly rows each, regional averages)")


def build_wind_onshore_profile():
    rows = load_feedinprofile()
    import datetime
    dt = datetime.datetime(2027, 1, 1, 0, 0, 0)
    lines = []
    for row in rows:
        avg = (row["Wind_north"] + row["Wind_east"] + row["Wind_middle"] + row["Wind_swest"]) / 4.0
        ts = dt.strftime("%Y-%m-%d_%H:%M:%S")
        lines.append(f"{ts};{avg:.6f}")
        dt += datetime.timedelta(hours=1)
    (OUT / "wind_onshore_profile.csv").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"  built wind_onshore_profile.csv ({len(lines)} hourly rows, regional average)")


def main():
    ensure_out()
    print("Outage / must-run (redated 2019 -> 2027):")
    year_map = {"2019": "2027", "2020": "2028", "2021": "2029"}
    redate_timeseries("lignite_outage.csv", "lignite_outage.csv", year_map)
    redate_timeseries("lignite_must_run.csv", "lignite_must_run.csv", year_map)
    redate_timeseries("hard_coal_outage.csv", "hard_coal_outage.csv", year_map)
    redate_timeseries("hard_coal_must_run.csv", "hard_coal_must_run.csv", year_map)
    redate_timeseries("natural_gas_outage.csv", "natural_gas_outage.csv", year_map)
    redate_timeseries("natural_gas_must_run.csv", "natural_gas_must_run.csv", year_map)

    print("Fuel and CO2 prices (from Brainpool Variable_cost sheet):")
    build_fuel_and_co2_prices()

    print("Renewable profiles:")
    build_solar_profiles()
    build_wind_onshore_profile()
    redate_timeseries("wind_offshore_profile.csv", "wind_offshore_profile.csv", year_map)
    redate_timeseries("run_of_river_profile.csv", "run_of_river_profile.csv", year_map)
    redate_timeseries("other_res_profile.csv", "other_res_profile.csv", year_map)
    redate_timeseries("biomass_profile.csv", "biomass_profile.csv", year_map)

    print("\nDone. Files written to:", OUT)


if __name__ == "__main__":
    main()
