"""Quick, approximate diagnostic: what would correlation look like if AMIRIS's reported price
were floored at various levels, instead of the engine's real hard-coded -500 EUR/MWh floor
(Constants.MINIMAL_PRICE_IN_EUR_PER_MWH, verified by decompiling amiris-core_4.1.2)?

IMPORTANT CAVEAT, stated up front and in every output: this is a POST-HOC CLIP of the already
-simulated price series, not a real re-simulation. The underlying MWh dispatched, storage
charging timing, and every other agent's behavior are UNCHANGED - only the reported price
column is clipped at each candidate floor. A genuine floor change would alter bidding behavior
(agents would stop pushing price as low, storage/flex agents would see a different price signal
and might charge differently), so this only tells us whether the NEGATIVE-PRICE-DEPTH mismatch
alone is a meaningful lever - not a trustworthy final answer. Used here purely to decide whether
the much bigger investment (patching and rebuilding AMIRIS's own engine) is worth pursuing.
"""
import numpy as np
import pandas as pd

from brainpool_multiyear_data import load_brainpool_price

ROOT = r"C:\Users\MuideenOA\Desktop\PyTut\Amiris\examples\backtest"
RESULTS = {
    2027: rf"{ROOT}\Germany2027_Feb29DropFix\result_Germany2027_Feb29DropFix\DayAheadMarketSingleZone.csv",
    2028: rf"{ROOT}\Germany2028\result_Germany2028\DayAheadMarketSingleZone.csv",
    2029: rf"{ROOT}\Germany2029_Feb29DropFix\result_Germany2029_Feb29DropFix\DayAheadMarketSingleZone.csv",
}

FLOORS = [None, -25, -50, -75, -100, -150, -200, -300, -400, -500,
          0, 5, 10, 15, 20, 25, 30, 40, 50, 75, 100]


def load_amiris(path):
    dam = pd.read_csv(path, sep=";")
    dam["ts"] = pd.to_datetime(dam["TimeStep"])
    return dam.set_index("ts")["ElectricityPriceInEURperMWH"]


print("=" * 90)
print("STEP 1: How negative does Brainpool's OWN real price actually go, per year?")
print("=" * 90)
for year in (2027, 2028, 2029):
    bp = load_brainpool_price(year)
    neg = bp[bp < 0]
    print(f"{year}: {len(neg)} negative hours ({100*len(neg)/len(bp):.1f}%), "
          f"min={bp.min():.2f}, mean of negative hours={neg.mean() if len(neg) else float('nan'):.2f}")

print()
print("=" * 90)
print("STEP 2: Floor sweep - clip AMIRIS's reported price at each candidate floor, recompute")
print("        correlation and bias against Brainpool's real price. None=no clip (current -500")
print("        engine floor as observed in the actual results).")
print("=" * 90)

summary_rows = []
for year, path in RESULTS.items():
    print(f"\n----- {year} -----")
    amiris = load_amiris(path)
    bp_full = load_brainpool_price(year)
    bp = bp_full[bp_full.index < f"{year}-12-31"] if year == 2028 else bp_full
    joined = pd.DataFrame({"AMIRIS": amiris, "Brainpool": bp}).dropna()

    shortage_mask = joined["AMIRIS"] >= 2999.9
    print(f"{'Floor':>10} | {'All-hours r':>12} | {'Excl-shortage r':>16} | {'All-hours bias':>15} | {'Clipped hours':>14}")
    for floor in FLOORS:
        if floor is None:
            clipped = joined["AMIRIS"]
            floor_label = "none(-500)"
            n_clipped = 0
        else:
            clipped = joined["AMIRIS"].clip(lower=floor)
            floor_label = str(floor)
            n_clipped = int((joined["AMIRIS"] < floor).sum())
        r_all = clipped.corr(joined["Brainpool"])
        r_excl = clipped[~shortage_mask].corr(joined["Brainpool"][~shortage_mask])
        bias = (clipped - joined["Brainpool"]).mean()
        print(f"{floor_label:>10} | {r_all:>12.4f} | {r_excl:>16.4f} | {bias:>+15.2f} | {n_clipped:>14}")
        summary_rows.append(dict(year=year, floor=floor_label, r_all=r_all, r_excl=r_excl, bias=bias, n_clipped=n_clipped))

print()
print("=" * 90)
print("STEP 3: Best floor per year, by all-hours correlation")
print("=" * 90)
df = pd.DataFrame(summary_rows)
for year in (2027, 2028, 2029):
    sub = df[df["year"] == year]
    best = sub.loc[sub["r_all"].idxmax()]
    baseline = sub[sub["floor"] == "none(-500)"].iloc[0]
    print(f"{year}: best floor = {best['floor']} (r_all={best['r_all']:.4f}, was {baseline['r_all']:.4f} unclipped) "
          f"-- delta = {best['r_all']-baseline['r_all']:+.4f}")

df.to_csv(r"C:\Users\MuideenOA\Desktop\PyTut\Amiris\_floor_sweep_results.csv", index=False)
print("\nSaved full sweep table to _floor_sweep_results.csv")
