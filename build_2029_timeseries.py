"""Builds all timeseries CSVs for the Germany2029 AMIRIS scenario - a second out-of-sample
validation build, same rationale as Germany2028 (no re-tuning of any calibrated mechanism).

2029 is NOT a leap year (365 days), so this is simpler than Germany2028: the Germany2019
source data (also 365 days) redates directly via a plain year-swap, exactly like the original
Germany2027 build - no elapsed-hours repositioning needed."""
from pathlib import Path

from brainpool_multiyear_data import load_variable_cost_rows, load_feedinprofile_rows

ROOT = Path(__file__).parent
SRC_2019 = ROOT / "examples" / "backtest" / "Germany2019" / "timeseries"
OUT = ROOT / "examples" / "backtest" / "Germany2029" / "timeseries"

COAL_MWH_PER_TONNE = 8.141
OIL_MWH_PER_BARREL = 1.70
YEAR = 2029
HOURS = 8760

YEAR_MAP = {"2019": "2029", "2020": "2030", "2021": "2031"}


def ensure_out():
    OUT.mkdir(parents=True, exist_ok=True)


def redate_timeseries(src_name, dst_name):
    src = SRC_2019 / src_name
    lines = src.read_text(encoding="utf-8").splitlines()
    out_lines = []
    for line in lines:
        if not line.strip():
            continue
        ts, val = line.split(";", 1)
        yr = ts[:4]
        new_yr = YEAR_MAP.get(yr, yr)
        out_lines.append(f"{new_yr}{ts[4:]};{val}")
    (OUT / dst_name).write_text("\n".join(out_lines) + "\n", encoding="utf-8")
    print(f"  redated {src_name} -> {dst_name} ({len(out_lines)} rows)")


def build_fuel_and_co2_prices():
    rows = load_variable_cost_rows(YEAR)
    hard_coal_lines, oil_lines, gas_lines, eua_lines = [], [], [], []

    for row in rows:
        dt = row["Date"]
        ts = dt.strftime("%Y-%m-%d_00:00:00")
        usd_per_eur = row["USD Wechselkurs [USD/EUR]"]

        coal_usd_t = row["Steinkohle [USD/t]"]
        coal_eur_mwh = (coal_usd_t / usd_per_eur) / COAL_MWH_PER_TONNE
        hard_coal_lines.append(f"{ts};{coal_eur_mwh:.4f}")

        oil_usd_bbl = row["Rohöl Brent [USD/bbl]"]
        oil_eur_mwh = (oil_usd_bbl / usd_per_eur) / OIL_MWH_PER_BARREL
        oil_lines.append(f"{ts};{oil_eur_mwh:.4f}")

        gas_eur_mwh = row["Gas-DE [EUR/MWh]"]
        gas_lines.append(f"{ts};{gas_eur_mwh:.4f}")

        eua_eur_t = row["EUA [EUR/tCO2]"]
        eua_lines.append(f"{ts};{eua_eur_t:.4f}")

    for series in (hard_coal_lines, oil_lines, gas_lines, eua_lines):
        last_val = series[-1].split(";")[1]
        series.append(f"{YEAR + 1}-01-01_00:00:00;{last_val}")

    (OUT / "hard_coal_price.csv").write_text("\n".join(hard_coal_lines) + "\n", encoding="utf-8")
    (OUT / "oil_price.csv").write_text("\n".join(oil_lines) + "\n", encoding="utf-8")
    (OUT / "natural_gas_price.csv").write_text("\n".join(gas_lines) + "\n", encoding="utf-8")
    (OUT / "co2_price.csv").write_text("\n".join(eua_lines) + "\n", encoding="utf-8")
    print(f"  built hard_coal_price.csv, oil_price.csv, natural_gas_price.csv, co2_price.csv "
          f"({len(rows)} monthly rows each + 1 sentinel)")


def build_solar_profiles():
    rows = load_feedinprofile_rows()
    assert len(rows) == 8760
    import datetime
    dt = datetime.datetime(YEAR, 1, 1, 0, 0, 0)
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
    print(f"  built solar_openfield_profile.csv and solar_rooftop_profile.csv ({len(openfield_lines)} hourly rows)")


def build_wind_onshore_profile():
    rows = load_feedinprofile_rows()
    import datetime
    dt = datetime.datetime(YEAR, 1, 1, 0, 0, 0)
    lines = []
    for row in rows:
        avg = (row["Wind_north"] + row["Wind_east"] + row["Wind_middle"] + row["Wind_swest"]) / 4.0
        ts = dt.strftime("%Y-%m-%d_%H:%M:%S")
        lines.append(f"{ts};{avg:.6f}")
        dt += datetime.timedelta(hours=1)
    (OUT / "wind_onshore_profile.csv").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"  built wind_onshore_profile.csv ({len(lines)} hourly rows)")


def main():
    ensure_out()
    print("Outage / must-run (redated 2019 -> 2029):")
    redate_timeseries("lignite_outage.csv", "lignite_outage.csv")
    redate_timeseries("lignite_must_run.csv", "lignite_must_run.csv")
    redate_timeseries("hard_coal_outage.csv", "hard_coal_outage.csv")
    redate_timeseries("hard_coal_must_run.csv", "hard_coal_must_run.csv")
    redate_timeseries("natural_gas_outage.csv", "natural_gas_outage.csv")
    redate_timeseries("natural_gas_must_run.csv", "natural_gas_must_run.csv")

    print("Fuel and CO2 prices (from Brainpool Variable_cost sheet, 2029 rows):")
    build_fuel_and_co2_prices()

    print("Renewable profiles:")
    build_solar_profiles()
    build_wind_onshore_profile()
    redate_timeseries("wind_offshore_profile.csv", "wind_offshore_profile.csv")
    redate_timeseries("run_of_river_profile.csv", "run_of_river_profile.csv")
    redate_timeseries("other_res_profile.csv", "other_res_profile.csv")
    redate_timeseries("biomass_profile.csv", "biomass_profile.csv")

    print("\nDone. Files written to:", OUT)


if __name__ == "__main__":
    main()
