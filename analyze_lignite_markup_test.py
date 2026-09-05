"""Analyzes the lignite-markup sensitivity test (Germany2027_LigniteMarkupTest, minMarkup -60
to -20) against the unmodified baseline (Germany2027_Feb29DropFix) and Brainpool's real 2027
price. Checks whether narrowing lignite's negative-bidding allowance reduces AMIRIS's excess
negative-price frequency/depth, and how it affects correlation."""
import pandas as pd

from brainpool_multiyear_data import load_brainpool_price

ROOT = r"C:\Users\MuideenOA\Desktop\PyTut\Amiris\examples\backtest"
BASELINE = rf"{ROOT}\Germany2027_Feb29DropFix\result_Germany2027_Feb29DropFix\DayAheadMarketSingleZone.csv"
TEST = rf"{ROOT}\Germany2027_LigniteMarkupTest\result_Germany2027_LigniteMarkupTest\DayAheadMarketSingleZone.csv"


def load(path):
    dam = pd.read_csv(path, sep=";")
    dam["ts"] = pd.to_datetime(dam["TimeStep"])
    return dam.set_index("ts")["ElectricityPriceInEURperMWH"]


baseline = load(BASELINE)
test = load(TEST)
bp = load_brainpool_price(2027)

joined = pd.DataFrame({"Baseline": baseline, "MarkupTest": test, "Brainpool": bp}).dropna()
shortage_baseline = joined["Baseline"] >= 2999.9
shortage_test = joined["MarkupTest"] >= 2999.9

print("=" * 70)
print("STEP 1: Did the price series actually change?")
print("=" * 70)
diff = (joined["MarkupTest"] - joined["Baseline"]).abs()
print(f"Hours with ANY price difference: {(diff > 0.01).sum()} of {len(joined)}")
print(f"Mean absolute difference (all hours): {diff.mean():.4f} EUR/MWh")
print(f"Max absolute difference: {diff.max():.2f} EUR/MWh")
print(f"Mean absolute difference (only hours that changed): "
      f"{diff[diff > 0.01].mean() if (diff > 0.01).any() else float('nan'):.4f} EUR/MWh")

print()
print("=" * 70)
print("STEP 2: Negative-price behaviour - baseline vs. markup test vs. real Brainpool")
print("=" * 70)
for label, series in [("Baseline", joined["Baseline"]), ("MarkupTest", joined["MarkupTest"]), ("Brainpool (real)", joined["Brainpool"])]:
    neg = series[series < 0]
    print(f"{label:>18}: {len(neg)} negative hours ({100*len(neg)/len(joined):.1f}%), "
          f"min={series.min():.2f}, mean of negative hours={neg.mean() if len(neg) else float('nan'):.2f}")

print()
print("=" * 70)
print("STEP 3: Correlation and bias vs. Brainpool - baseline vs. markup test")
print("=" * 70)
for label, series, shortage_mask in [
    ("Baseline", joined["Baseline"], shortage_baseline),
    ("MarkupTest", joined["MarkupTest"], shortage_test),
]:
    r_all = series.corr(joined["Brainpool"])
    r_excl = series[~shortage_mask].corr(joined["Brainpool"][~shortage_mask])
    bias_all = (series - joined["Brainpool"]).mean()
    mae_all = (series - joined["Brainpool"]).abs().mean()
    print(f"{label:>18}: all-hours r={r_all:.4f}, excl-shortage r={r_excl:.4f}, "
          f"bias={bias_all:+.2f}, MAE={mae_all:.2f}, shortage hours={shortage_mask.sum()}")

print()
print("=" * 70)
print("STEP 4: Where did the price actually change? (largest differences)")
print("=" * 70)
top_diff = diff.sort_values(ascending=False).head(10)
for ts, d in top_diff.items():
    print(f"  {ts}: baseline={joined.loc[ts, 'Baseline']:.2f}, test={joined.loc[ts, 'MarkupTest']:.2f}, diff={d:.2f}")
