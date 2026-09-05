"""Shared readers for the new "Amiris_Inputdata 2027 -2029.xlsx" file, which stacks 2027,
2028, and 2029 data in the same sheets the original single-year Amiris_Inputdata_EN.xlsx
used - Capacity (one row per year), Variable_cost (12 monthly rows per year), Brainpool_output
(8760/8784 hourly rows per year), feedinprofile (a SINGLE reused year of hourly capacity-
factor shapes, since Brainpool holds the weather-year basis - 2009 - constant across all
target years and only varies installed capacity)."""
from pathlib import Path
import openpyxl
import pandas as pd

ROOT = Path(__file__).parent
XLSX = ROOT / "Amiris_Inputdata 2027 -2029.xlsx"


def load_capacity_row(year):
    """Returns a dict of every Capacity-sheet column for the given year (2027/2028/2029)."""
    wb = openpyxl.load_workbook(XLSX, data_only=True)
    ws = wb["Capacity"]
    headers = [ws.cell(row=2, column=c).value for c in range(1, ws.max_column + 1)]
    for r in range(3, ws.max_row + 1):
        row = [ws.cell(row=r, column=c).value for c in range(1, ws.max_column + 1)]
        if row[0] == year:
            # headers has duplicate names (Kernkraft appears twice etc.) - keep first
            # occurrence only for the ones we actually use, via a name->index map built
            # fresh per call so duplicate later columns don't silently overwrite.
            result = {}
            for h, v in zip(headers, row):
                if h is not None and h not in result:
                    result[h] = v
            # explicit second-occurrence installed-capacity block (after the blank column)
            # holds the SAME per-technology capacities restated in GW for the demand-side
            # section - not needed, first occurrence (columns B-K) is what agents use.
            return result
    raise ValueError(f"Year {year} not found in Capacity sheet")


def get_demand_components(year):
    row = load_capacity_row(year)
    return {
        "inflexible": row["Inflexible Bruttostromnachfrage"],
        "electrolysis": row["Elektrolyse"],
        "e_mobility": row["Elektromobilität"],
        "heat_pumps": row["Wärmepumpen"],
    }


def load_variable_cost_rows(year):
    wb = openpyxl.load_workbook(XLSX, data_only=True)
    ws = wb["Variable_cost"]
    headers = [c.value for c in ws[1]]
    headers[0] = "Date"
    rows = []
    for r in ws.iter_rows(min_row=3, values_only=True):
        if r[0] is None:
            continue
        d = dict(zip(headers, r))
        if d["Date"].year == year:
            rows.append(d)
    return rows


def load_feedinprofile_rows():
    """Single reused weather-year shape (365 days), same for every target year."""
    wb = openpyxl.load_workbook(XLSX, data_only=True)
    ws = wb["feedinprofile"]
    headers = [c.value for c in ws[1]]
    rows = []
    for r in ws.iter_rows(min_row=2, values_only=True):
        rows.append(dict(zip(headers, r)))
    return rows


def load_brainpool_price(year):
    wb = openpyxl.load_workbook(XLSX, data_only=True)
    ws = wb["Brainpool_output"]
    rows = []
    for r in ws.iter_rows(min_row=4, values_only=True):
        if r[0] is None:
            continue
        if r[0].year == year:
            rows.append((r[0], r[2]))
    df = pd.DataFrame(rows, columns=["ts", "brainpool_price"]).set_index("ts")
    return df["brainpool_price"]


if __name__ == "__main__":
    for y in (2027, 2028, 2029):
        comp = get_demand_components(y)
        bp = load_brainpool_price(y)
        vc = load_variable_cost_rows(y)
        print(f"{y}: demand={comp}, brainpool hours={len(bp)}, variable_cost months={len(vc)}")
