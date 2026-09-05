"""Builds all timeseries CSVs for the Germany2028 AMIRIS scenario - an out-of-sample
validation build: every calibrated mechanism from the Germany2027 line of work is reused
COMPLETELY UNCHANGED, only rescaled to 2028's own Brainpool targets - no re-tuning.

IMPORTANT CORRECTION: 2028 is a real calendar leap year (366 days), but AMIRIS's underlying
FAME simulation framework does NOT support a true 366-day year at all - confirmed directly by
FAME's own error message when a 2028-12-31 timestamp was attempted: "Cannot convert time
stamp string - last day of leap year is Dec 30th!". FAME always represents a year as exactly
365 days; for leap years it omits Dec 31, not Feb 29. Every 2028 timeseries here therefore
spans exactly 8760 hours (the same as every other build in this project).

Redating the Germany2019 source files (non-leap, real Jan1-Dec31) onto FAME's 2028 calendar
(365 days too, but shaped Jan1-Dec30 with Feb29 present) is done by ELAPSED-HOURS-SINCE-JAN-1
position, not by literal month/day string matching, since the two calendars have a different
day-per-month shape despite both totalling 365 days: a source point at hour offset H past its
own Jan 1 becomes 2028's Jan 1 + H hours, regardless of what calendar date that source point
was originally labelled with. Documented consequence: this introduces a harmless ~1-day
seasonal drift for these already-reused/borrowed series (real Dec 2019 outage data ends up
placed against nominal "Dec 2028" one day earlier in the month) - a negligible simplification
on data that already carries far larger documented caveats (borrowed from an unrelated year).
"""
import datetime
from pathlib import Path

from brainpool_multiyear_data import load_variable_cost_rows, load_feedinprofile_rows

ROOT = Path(__file__).parent
SRC_2019 = ROOT / "examples" / "backtest" / "Germany2019" / "timeseries"
OUT = ROOT / "examples" / "backtest" / "Germany2028" / "timeseries"

COAL_MWH_PER_TONNE = 8.141
OIL_MWH_PER_BARREL = 1.70
YEAR = 2028
HOURS = 8760  # FAME's own convention: every year is 365 days, even 2028 (Dec 31 omitted)
NEW_JAN1 = datetime.datetime(YEAR, 1, 1, 0, 0, 0)


def ensure_out():
    OUT.mkdir(parents=True, exist_ok=True)


def redate_by_elapsed_hours(src_name, dst_name):
    """Repositions every row of a Germany2019 source file onto FAME's 2028 calendar by
    elapsed hours since the row's own Jan-1 00:00 (see module docstring). Handles both dense
    (one row per hour) and sparse (change-point) series uniformly. Trailing sentinel rows
    (dated the following year(s) in the source) are repositioned the same way, one/two years
    past 2028's own Jan 1."""
    src = SRC_2019 / src_name
    lines = [l for l in src.read_text(encoding="utf-8").splitlines() if l.strip()]
    out_lines = []
    for line in lines:
        ts, val = line.split(";", 1)
        src_dt = datetime.datetime.strptime(ts, "%Y-%m-%d_%H:%M:%S")
        # elapsed hours since Jan-1 of THIS row's own year (2019 for real data rows, or
        # 2020/2021 for the trailing sentinel rows)
        year_start = datetime.datetime(src_dt.year, 1, 1)
        elapsed_hours = (src_dt - year_start).total_seconds() / 3600
        year_offset = src_dt.year - 2019
        # Built directly from (target year + offset)'s own Jan-1, NOT via real-calendar-day
        # arithmetic on NEW_JAN1 - adding "365 days" to a real leap-year Jan-1 lands on
        # Dec-31 (invalid in FAME), not the following Jan-1.
        new_dt = datetime.datetime(YEAR + year_offset, 1, 1) + datetime.timedelta(hours=elapsed_hours)
        out_lines.append(f"{new_dt.strftime('%Y-%m-%d_%H:%M:%S')};{val}")
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
    dt = NEW_JAN1
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
    dt = NEW_JAN1
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
    print("Outage / must-run (redated 2019 -> 2028 by elapsed-hours position):")
    redate_by_elapsed_hours("lignite_outage.csv", "lignite_outage.csv")
    redate_by_elapsed_hours("lignite_must_run.csv", "lignite_must_run.csv")
    redate_by_elapsed_hours("hard_coal_outage.csv", "hard_coal_outage.csv")
    redate_by_elapsed_hours("hard_coal_must_run.csv", "hard_coal_must_run.csv")
    redate_by_elapsed_hours("natural_gas_outage.csv", "natural_gas_outage.csv")
    redate_by_elapsed_hours("natural_gas_must_run.csv", "natural_gas_must_run.csv")

    print("Fuel and CO2 prices (from Brainpool Variable_cost sheet, 2028 rows):")
    build_fuel_and_co2_prices()

    print("Renewable profiles:")
    build_solar_profiles()
    build_wind_onshore_profile()
    redate_by_elapsed_hours("wind_offshore_profile.csv", "wind_offshore_profile.csv")
    redate_by_elapsed_hours("run_of_river_profile.csv", "run_of_river_profile.csv")
    redate_by_elapsed_hours("other_res_profile.csv", "other_res_profile.csv")
    redate_by_elapsed_hours("biomass_profile.csv", "biomass_profile.csv")

    print("\nDone. Files written to:", OUT)


if __name__ == "__main__":
    main()
