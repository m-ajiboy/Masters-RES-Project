"""Aligns Brainpool's real 2027 day-ahead price forecast against all four built AMIRIS
Germany2027 scenario versions on the same UTC hourly grid, and computes comparison stats."""
import openpyxl
import pandas as pd

ROOT = r"C:\Users\MuideenOA\Desktop\PyTut\Amiris"

AMIRIS_RESULTS = {
    "V1 no-import": rf"{ROOT}\result_Germany2027_test\DayAheadMarketSingleZone.csv",
    "V1 with-import": rf"{ROOT}\examples\backtest\Germany2027_V1WithImport\result_V1WithImport\DayAheadMarketSingleZone.csv",
    "V2 no-import": rf"{ROOT}\examples\backtest\Germany2027_DemandV2\result_DemandV2\DayAheadMarketSingleZone.csv",
    "V2 with-import": rf"{ROOT}\examples\backtest\Germany2027_WithImport\result_WithImport\DayAheadMarketSingleZone.csv",
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
    print(f"Brainpool: {len(bp)} rows, {bp.index.min()} to {bp.index.max()}")

    combined = bp.copy()
    for label, path in AMIRIS_RESULTS.items():
        s = load_amiris(path)
        combined[label] = s.reindex(combined.index)
        print(f"{label}: {s.index.min()} to {s.index.max()}, {combined[label].isna().sum()} unmatched rows")

    print("\n=== Summary statistics (EUR/MWh) ===")
    stats = pd.DataFrame({
        "mean": combined.mean(),
        "median": combined.median(),
        "std": combined.std(),
        "min": combined.min(),
        "max": combined.max(),
        "negative_hrs": (combined < 0).sum(),
        "shortage_hrs_3000": (combined >= 2999.9).sum(),
    })
    print(stats.to_string())

    print("\n=== Correlation with Brainpool (Pearson r) ===")
    for label in AMIRIS_RESULTS:
        r = combined["brainpool_price"].corr(combined[label])
        mae = (combined[label] - combined["brainpool_price"]).abs().mean()
        rmse = ((combined[label] - combined["brainpool_price"]) ** 2).mean() ** 0.5
        bias = (combined[label] - combined["brainpool_price"]).mean()
        print(f"{label}: r={r:.3f}  MAE={mae:.2f}  RMSE={rmse:.2f}  bias={bias:+.2f}")

    print("\n=== Same stats EXCLUDING AMIRIS shortage hours (>=3000) ===")
    for label in AMIRIS_RESULTS:
        mask = combined[label] < 2999.9
        sub_amiris = combined.loc[mask, label]
        sub_bp = combined.loc[mask, "brainpool_price"]
        r = sub_bp.corr(sub_amiris)
        mae = (sub_amiris - sub_bp).abs().mean()
        bias = (sub_amiris - sub_bp).mean()
        print(f"{label}: n={mask.sum()} ({mask.sum()/len(combined)*100:.1f}% of hours)  "
              f"mean={sub_amiris.mean():.2f}  r={r:.3f}  MAE={mae:.2f}  bias={bias:+.2f}")

    combined.to_csv(rf"{ROOT}\comparison_2027_aligned.csv")
    print(f"\nSaved aligned hourly comparison to comparison_2027_aligned.csv")


if __name__ == "__main__":
    main()
