"""Evidence script: the import-ceiling calibration sweep for the Germany2027_WithImport
'fix'. Compares Brainpool's real 2027 price forecast against four candidate flat
AvailableEnergyForImport ceilings (20,000 / 25,000 / 30,000 / 37,650 MW - the last being
the first-pass fix, sized off the real observed 2023 peak gross import hour), each run as
a full AMIRIS simulation (see build_2027_import_moderate.py for how each candidate's
timeseries was built).

Why this sweep exists: the first-pass fix (flat 37,650 MW every hour) eliminated all
shortage hours, but overshot Brainpool's average price (bias -12.59 EUR/MWh) - a smaller,
flat ceiling still available in every hour, but less generous, was expected to reduce how
much import clears in ordinary (non-shortage) hours while still covering most genuine
shortage instances.

Finding: bias improves monotonically as the ceiling shrinks, but MAE and correlation get
WORSE - a smaller ceiling produces a deceptively good average (positive and negative
hourly errors cancelling out) while actually tracking Brainpool less reliably hour to
hour, and reintroduces some shortage hours. 30,000 MW was chosen as the final calibrated
value: MAE and correlation are essentially as good as the full 37,650 MW ceiling, shortage
hours are almost eliminated (3 remaining, 0.03%), and bias is meaningfully improved
(-10.70 vs -12.59).
"""
import openpyxl
import pandas as pd

ROOT = r"C:\Users\MuideenOA\Desktop\PyTut\Amiris"

CANDIDATES = {
    "20,000 MW": rf"{ROOT}\examples\backtest\Germany2027_WithImport_Fix\result_WithImport_Fix20k",
    "25,000 MW": rf"{ROOT}\examples\backtest\Germany2027_WithImport_Fix\result_WithImport_Fix25k",
    "30,000 MW (FINAL)": rf"{ROOT}\examples\backtest\Germany2027_WithImport_Fix\result_WithImport_Fix30k",
    "37,650 MW (first fix)": rf"{ROOT}\examples\backtest\Germany2027_WithImport_Fix\result_WithImport_Fix",
}


def load_brainpool():
    wb = openpyxl.load_workbook(rf"{ROOT}\Brainpool 2027 output.xlsx", data_only=True)
    ws = wb["Brainpool_output"]
    rows = [(r[0], r[2]) for r in ws.iter_rows(min_row=4, values_only=True) if r[0] is not None]
    df = pd.DataFrame(rows, columns=["ts", "bp"]).set_index("ts")
    df.index = pd.to_datetime(df.index)
    return df


def main():
    bp = load_brainpool()
    print(f"{'Ceiling':24s} {'shortage':>14s} {'mean':>8s} {'bias':>8s} {'MAE':>7s} {'r':>6s} {'import cleared':>16s}")
    for label, path in CANDIDATES.items():
        dam = pd.read_csv(rf"{path}\DayAheadMarketSingleZone.csv", sep=";")
        dam["ts"] = pd.to_datetime(dam["TimeStep"])
        dam = dam.set_index("ts")
        joined = bp.join(dam["ElectricityPriceInEURperMWH"])
        p = joined["ElectricityPriceInEURperMWH"]
        shortage = (p >= 2999.9).sum()
        bias = (p - joined["bp"]).mean()
        mae = (p - joined["bp"]).abs().mean()
        r = p.corr(joined["bp"])
        imp = pd.read_csv(rf"{path}\ImportTrader.csv", sep=";")
        awarded = imp["AwardedEnergyInMWH"].sum() / 1e6
        print(f"{label:24s} {shortage:6d} ({shortage/len(p)*100:5.2f}%) {p.mean():8.2f} "
              f"{bias:+8.2f} {mae:7.2f} {r:6.3f} {awarded:13.2f} TWh")


if __name__ == "__main__":
    main()
