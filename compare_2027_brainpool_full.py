"""Evidence script: aligns Brainpool's real 2027 day-ahead price forecast against every
AMIRIS Germany2027 result produced so far - the original 4-version matrix AND the two
import-fixed with-import reruns - on the same UTC hourly grid, and computes the same
comparison statistics (mean, median, shortage/negative hours, correlation, MAE, RMSE,
bias) for all of them side by side. This is the "before vs after" evidence for the
import-availability fix (see build_2027_import_fix.py): does decoupling
AvailableEnergyForImport from the 2023 historical timing pattern actually shrink the
shortage-hour frequency and the mean-price gap versus Brainpool, as predicted?

Does not overwrite the original round's comparison_2027_aligned.csv (from
compare_2027_brainpool.py) - writes its own output file instead.
"""
import openpyxl
import pandas as pd

ROOT = r"C:\Users\MuideenOA\Desktop\PyTut\Amiris"

AMIRIS_RESULTS = {
    "V1 no-import (rerun)": rf"{ROOT}\examples\backtest\Germany2027\result_Germany2027_rerun\DayAheadMarketSingleZone.csv",
    "V1 with-import (original)": rf"{ROOT}\examples\backtest\Germany2027_V1WithImport\result_V1WithImport\DayAheadMarketSingleZone.csv",
    "V1 with-import (FIXED, 37.65k - FINAL)": rf"{ROOT}\examples\backtest\Germany2027_V1WithImport_Fix\result_V1WithImport_Fix\DayAheadMarketSingleZone.csv",
    "V1 with-import (FIXED, 30k - rejected)": rf"{ROOT}\examples\backtest\Germany2027_V1WithImport_Fix\result_V1WithImport_Fix30k\DayAheadMarketSingleZone.csv",
    "V2 no-import (rerun)": rf"{ROOT}\examples\backtest\Germany2027_DemandV2\result_DemandV2_rerun\DayAheadMarketSingleZone.csv",
    "V2 with-import (original)": rf"{ROOT}\examples\backtest\Germany2027_WithImport\result_WithImport\DayAheadMarketSingleZone.csv",
    "V2 with-import (37.65k - superseded)": rf"{ROOT}\examples\backtest\Germany2027_WithImport_Fix\result_WithImport_Fix\DayAheadMarketSingleZone.csv",
    "V2 with-import (FIXED, 30k - FINAL)": rf"{ROOT}\examples\backtest\Germany2027_WithImport_Fix\result_WithImport_Fix30k\DayAheadMarketSingleZone.csv",
}

IMPORT_RESULTS = {
    "V1 with-import (original)": rf"{ROOT}\examples\backtest\Germany2027_V1WithImport\result_V1WithImport\ImportTrader.csv",
    "V1 with-import (FIXED, 37.65k - FINAL)": rf"{ROOT}\examples\backtest\Germany2027_V1WithImport_Fix\result_V1WithImport_Fix\ImportTrader.csv",
    "V1 with-import (FIXED, 30k - rejected)": rf"{ROOT}\examples\backtest\Germany2027_V1WithImport_Fix\result_V1WithImport_Fix30k\ImportTrader.csv",
    "V2 with-import (original)": rf"{ROOT}\examples\backtest\Germany2027_WithImport\result_WithImport\ImportTrader.csv",
    "V2 with-import (37.65k - superseded)": rf"{ROOT}\examples\backtest\Germany2027_WithImport_Fix\result_WithImport_Fix\ImportTrader.csv",
    "V2 with-import (FIXED, 30k - FINAL)": rf"{ROOT}\examples\backtest\Germany2027_WithImport_Fix\result_WithImport_Fix30k\ImportTrader.csv",
}


def load_brainpool():
    wb = openpyxl.load_workbook(rf"{ROOT}\Brainpool 2027 output.xlsx", data_only=True)
    ws = wb["Brainpool_output"]
    rows = [(r[0], r[2]) for r in ws.iter_rows(min_row=4, values_only=True) if r[0] is not None]
    df = pd.DataFrame(rows, columns=["ts", "brainpool_price"])
    df["ts"] = pd.to_datetime(df["ts"])
    return df.set_index("ts")


def load_amiris(path):
    dam = pd.read_csv(path, sep=";")
    dam["ts"] = pd.to_datetime(dam["TimeStep"])
    return dam.set_index("ts")["ElectricityPriceInEURperMWH"]


def main():
    bp = load_brainpool()
    print(f"Brainpool: {len(bp)} rows, {bp.index.min()} to {bp.index.max()}\n")

    combined = bp.copy()
    for label, path in AMIRIS_RESULTS.items():
        s = load_amiris(path)
        combined[label] = s.reindex(combined.index)

    print("=== Summary statistics (EUR/MWh) ===")
    stats = pd.DataFrame({
        "mean": combined.mean(),
        "median": combined.median(),
        "min": combined.min(),
        "max": combined.max(),
        "negative_hrs": (combined < 0).sum(),
        "shortage_hrs_3000": (combined >= 2999.9).sum(),
        "shortage_pct": (combined >= 2999.9).mean() * 100,
    })
    print(stats.to_string(float_format=lambda x: f"{x:,.2f}"))

    print("\n=== Correlation / error vs Brainpool (ALL hours) ===")
    for label in AMIRIS_RESULTS:
        r = combined["brainpool_price"].corr(combined[label])
        mae = (combined[label] - combined["brainpool_price"]).abs().mean()
        rmse = ((combined[label] - combined["brainpool_price"]) ** 2).mean() ** 0.5
        bias = (combined[label] - combined["brainpool_price"]).mean()
        print(f"{label:32s}: r={r:.3f}  MAE={mae:8.2f}  RMSE={rmse:9.2f}  bias={bias:+9.2f}")

    print("\n=== Correlation / error vs Brainpool (EXCLUDING each build's own shortage hours) ===")
    for label in AMIRIS_RESULTS:
        mask = combined[label] < 2999.9
        sub_amiris = combined.loc[mask, label]
        sub_bp = combined.loc[mask, "brainpool_price"]
        r = sub_bp.corr(sub_amiris)
        mae = (sub_amiris - sub_bp).abs().mean()
        bias = (sub_amiris - sub_bp).mean()
        print(f"{label:32s}: n={mask.sum():5d} ({mask.mean()*100:5.1f}% of hours)  "
              f"mean={sub_amiris.mean():7.2f}  r={r:.3f}  MAE={mae:6.2f}  bias={bias:+7.2f}")

    print("\n=== Import trader: offered vs. awarded, original vs. fixed ===")
    for label, path in IMPORT_RESULTS.items():
        imp = pd.read_csv(path, sep=";")
        offered = imp["OfferedEnergyInMWH"].sum() / 1_000_000
        awarded = imp["AwardedEnergyInMWH"].sum() / 1_000_000
        zero_hours = (imp["OfferedEnergyInMWH"] == 0).sum()
        util = awarded / offered * 100 if offered > 0 else float("nan")
        print(f"{label:32s}: offered={offered:7.2f} TWh  awarded={awarded:7.2f} TWh  "
              f"utilization={util:5.1f}%  hours with 0 offered={zero_hours}")

    combined.to_csv(rf"{ROOT}\comparison_2027_full_aligned_calibrated.csv")
    print(f"\nSaved full aligned hourly comparison to comparison_2027_full_aligned_calibrated.csv "
          f"(previous round's comparison_2027_full_aligned.csv is left untouched)")


if __name__ == "__main__":
    main()
