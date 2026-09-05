"""First real analysis of the Germany2027_MarketCoupling result: DE-zone price vs. the
pre-coupling baseline (Germany2027_Feb29DropFix) and vs. Brainpool's real 2027 price.
Also checks transmission utilization and the ROE zone's own price."""
import pandas as pd
from brainpool_multiyear_data import load_brainpool_price

ROOT = r"C:\Users\MuideenOA\Desktop\PyTut\Amiris\examples\backtest"
COUPLING = rf"{ROOT}\Germany2027_MarketCoupling\result_Germany2027_MarketCoupling\DayAheadMarketMultiZone.csv"
BASELINE = rf"{ROOT}\Germany2027_Feb29DropFix\result_Germany2027_Feb29DropFix\DayAheadMarketSingleZone.csv"

df = pd.read_csv(COUPLING, sep=";")
df["ts"] = pd.to_datetime(df["TimeStep"])

de = df[df["AgentId"] == 1].set_index("ts")
roe = df[df["AgentId"] == 9001].set_index("ts")

baseline = pd.read_csv(BASELINE, sep=";")
baseline["ts"] = pd.to_datetime(baseline["TimeStep"])
baseline = baseline.set_index("ts")["ElectricityPriceInEURperMWH"]

bp = load_brainpool_price(2027)

joined = pd.DataFrame({
    "DE_coupled": de["ElectricityPriceInEURperMWH"],
    "DE_baseline": baseline,
    "ROE": roe["ElectricityPriceInEURperMWH"],
    "Brainpool": bp,
}).dropna()

print("=" * 70)
print("STEP 1: Basic price stats")
print("=" * 70)
for label in ["DE_coupled", "DE_baseline", "ROE", "Brainpool"]:
    s = joined[label]
    print(f"{label:>12}: mean={s.mean():.2f}, min={s.min():.2f}, max={s.max():.2f}, "
          f"negative hours={len(s[s<0])} ({100*len(s[s<0])/len(s):.1f}%)")

print()
print("=" * 70)
print("STEP 2: Correlation with Brainpool - coupled vs. baseline")
print("=" * 70)
shortage_coupled = joined["DE_coupled"] >= 2999.9
shortage_baseline = joined["DE_baseline"] >= 2999.9
r_all_coupled = joined["DE_coupled"].corr(joined["Brainpool"])
r_excl_coupled = joined.loc[~shortage_coupled, "DE_coupled"].corr(joined.loc[~shortage_coupled, "Brainpool"])
r_all_baseline = joined["DE_baseline"].corr(joined["Brainpool"])
r_excl_baseline = joined.loc[~shortage_baseline, "DE_baseline"].corr(joined.loc[~shortage_baseline, "Brainpool"])
bias_coupled = (joined["DE_coupled"] - joined["Brainpool"]).mean()
bias_baseline = (joined["DE_baseline"] - joined["Brainpool"]).mean()
print(f"Baseline (pre-coupling): all-hours r={r_all_baseline:.4f}, excl-shortage r={r_excl_baseline:.4f}, "
      f"bias={bias_baseline:+.2f}, shortage hours={shortage_baseline.sum()}")
print(f"Coupled (MarketCoupling): all-hours r={r_all_coupled:.4f}, excl-shortage r={r_excl_coupled:.4f}, "
      f"bias={bias_coupled:+.2f}, shortage hours={shortage_coupled.sum()}")

print()
print("=" * 70)
print("STEP 3: Transmission utilization (DE side)")
print("=" * 70)
imports = de["AwardedNetEnergyFromImportInMWH"]
exports = de["AwardedNetEnergyToExportInMWH"]
print(f"DE importing from ROE: {len(imports[imports>0])} hours, total {imports.sum():,.0f} MWh, "
      f"max hour {imports.max():,.0f} MWh (ceiling 30,000 MW placeholder)")
print(f"DE exporting to ROE: {len(exports[exports>0])} hours, total {exports.sum():,.0f} MWh, "
      f"max hour {exports.max():,.0f} MWh")
print(f"Hours DE imports AT the placeholder ceiling (>=29,900 MWh): {len(imports[imports>=29900])}")
print(f"Hours DE exports AT the placeholder ceiling (>=29,900 MWh): {len(exports[exports>=29900])}")

print()
print("=" * 70)
print("STEP 4: Did coupling actually change DE's price vs. pre-coupling for that same hour?")
print("=" * 70)
diff = (de["ElectricityPriceInEURperMWH"] - de["PreCouplingElectricityPriceInEURperMWH"]).dropna()
print(f"Hours where coupling changed DE's price: {(diff.abs()>0.01).sum()} of {len(diff)}")
print(f"Mean change: {diff.mean():+.2f} EUR/MWh (negative = coupling lowered price on average)")
