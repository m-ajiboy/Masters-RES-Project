"""Full lignite-markup sweep: -60 (baseline), -40, -20, -10 EUR/MWh, each against Brainpool's
real 2027 price. Reports correlation, bias, MAE, and negative-price frequency/depth for every
point, to find whether any value in this range is a genuine improvement over the baseline."""
import pandas as pd

from brainpool_multiyear_data import load_brainpool_price

ROOT = r"C:\Users\MuideenOA\Desktop\PyTut\Amiris\examples\backtest"
POINTS = {
    -60: rf"{ROOT}\Germany2027_Feb29DropFix\result_Germany2027_Feb29DropFix\DayAheadMarketSingleZone.csv",
    -40: rf"{ROOT}\Germany2027_LigniteMarkupTest_m40\result_Germany2027_LigniteMarkupTest_m40\DayAheadMarketSingleZone.csv",
    -20: rf"{ROOT}\Germany2027_LigniteMarkupTest\result_Germany2027_LigniteMarkupTest\DayAheadMarketSingleZone.csv",
    -10: rf"{ROOT}\Germany2027_LigniteMarkupTest_m10\result_Germany2027_LigniteMarkupTest_m10\DayAheadMarketSingleZone.csv",
}


def load(path):
    dam = pd.read_csv(path, sep=";")
    dam["ts"] = pd.to_datetime(dam["TimeStep"])
    return dam.set_index("ts")["ElectricityPriceInEURperMWH"]


bp = load_brainpool_price(2027)

print(f"{'minMarkup':>10} | {'all-hours r':>12} | {'excl-shortage r':>16} | {'bias':>8} | {'MAE':>7} | {'neg hrs':>8} | {'neg %':>7} | {'min price':>10} | {'shortage hrs':>13}")
rows = []
for markup, path in POINTS.items():
    series = load(path)
    joined = pd.DataFrame({"AMIRIS": series, "Brainpool": bp}).dropna()
    shortage = joined["AMIRIS"] >= 2999.9
    r_all = joined["AMIRIS"].corr(joined["Brainpool"])
    r_excl = joined.loc[~shortage, "AMIRIS"].corr(joined.loc[~shortage, "Brainpool"])
    bias = (joined["AMIRIS"] - joined["Brainpool"]).mean()
    mae = (joined["AMIRIS"] - joined["Brainpool"]).abs().mean()
    neg = joined["AMIRIS"][joined["AMIRIS"] < 0]
    print(f"{markup:>10} | {r_all:>12.4f} | {r_excl:>16.4f} | {bias:>+8.2f} | {mae:>7.2f} | "
          f"{len(neg):>8} | {100*len(neg)/len(joined):>6.1f}% | {joined['AMIRIS'].min():>10.2f} | {shortage.sum():>13}")
    rows.append(dict(markup=markup, r_all=r_all, r_excl=r_excl, bias=bias, mae=mae,
                      neg_hours=len(neg), neg_pct=100*len(neg)/len(joined),
                      min_price=joined["AMIRIS"].min(), shortage_hours=int(shortage.sum())))

df = pd.DataFrame(rows)
best_r = df.loc[df["r_all"].idxmax()]
print(f"\nBest all-hours correlation: minMarkup={best_r['markup']:.0f} (r={best_r['r_all']:.4f})")
print(f"Baseline (-60) all-hours correlation: r={df[df['markup']==-60]['r_all'].values[0]:.4f}")

df.to_csv(r"C:\Users\MuideenOA\Desktop\PyTut\Amiris\_lignite_markup_sweep_results.csv", index=False)
print("\nSaved full sweep table to _lignite_markup_sweep_results.csv")
