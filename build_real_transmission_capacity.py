"""Derives a real, flow-data-grounded DE<->ROE transmission capacity estimate from Phase 35's
real 2023 ENTSO-E cross-border physical flow data - replacing Phase 34's flat 30,000 MW
placeholder (which just reused the unrelated import ceiling).

Documented methodology: physical flow is not the same as NTC (net transfer capacity) - flow
reflects what actually moved given prices/weather/availability, capacity is the physical
limit. But a flow-based estimate is still a real, grounded improvement over an arbitrary
reused number. Uses the 98th percentile of each border's real hourly flow (in each direction
separately) as a robust proxy for that border's effective capacity - a genuine limit should
occasionally be approached/reached in the data, and a high percentile is far less sensitive
to a single outlier hour than the plain maximum. Sums the 10 real available borders (AT, BE,
CH, CZ, DK_1, DK_2, FR, NL, NO_2, PL) into one aggregate DE<->ROE figure per direction, since
ROE is modelled as a single combined zone. SE_4 is excluded (Phase 35's one documented flow
gap) - the estimate is a genuine, if incomplete, undercount by that one border's real share,
flagged explicitly rather than silently patched with a guess.
"""
import pandas as pd

ENTSOE_DIR = r"C:\Users\MuideenOA\Desktop\PyTut\Amiris\examples\backtest\RestOfEurope2023\raw_entsoe"
ZONES = ["AT", "BE", "CH", "CZ", "DK_1", "DK_2", "FR", "NL", "NO_2", "PL"]
PERCENTILE = 0.98

de_to_roe_estimates = {}
roe_to_de_estimates = {}

for zone in ZONES:
    out_flow = pd.read_csv(rf"{ENTSOE_DIR}\flow_DEto{zone}_2023.csv", index_col=0).iloc[:, 0]
    in_flow = pd.read_csv(rf"{ENTSOE_DIR}\flow_{zone}toDE_2023.csv", index_col=0).iloc[:, 0]
    de_to_roe_estimates[zone] = out_flow.quantile(PERCENTILE)
    roe_to_de_estimates[zone] = in_flow.quantile(PERCENTILE)
    print(f"{zone}: DE->  P{int(PERCENTILE*100)}={de_to_roe_estimates[zone]:,.0f} MW "
          f"(max={out_flow.max():,.0f}) | ->DE P{int(PERCENTILE*100)}={roe_to_de_estimates[zone]:,.0f} MW "
          f"(max={in_flow.max():,.0f})")

total_de_to_roe = sum(de_to_roe_estimates.values())
total_roe_to_de = sum(roe_to_de_estimates.values())
print(f"\nTotal DE->ROE capacity estimate (sum of {len(ZONES)} borders, missing SE_4): "
      f"{total_de_to_roe:,.0f} MW")
print(f"Total ROE->DE capacity estimate (sum of {len(ZONES)} borders, missing SE_4): "
      f"{total_roe_to_de:,.0f} MW")
print(f"\nFor comparison, Phase 34's placeholder was a flat 30,000 MW in both directions.")

OUT_DIR = r"C:\Users\MuideenOA\Desktop\PyTut\Amiris\examples\backtest\Germany2027_MarketCoupling_RealFlow\timeseries"

idx = pd.date_range("2027-01-01", periods=8760, freq="h")
for value, fname in [(total_de_to_roe, "transfer_DEtoROE_realflow.csv"),
                      (total_roe_to_de, "transfer_ROEtoDE_realflow.csv")]:
    lines = [f"{ts.strftime('%Y-%m-%d_%H:%M:%S')};{value:.1f}" for ts in idx]
    path = rf"{OUT_DIR}\{fname}"
    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")
    print(f"Saved {path} (flat {value:,.0f} MW, real-flow-derived)")
