# -*- coding: utf-8 -*-
"""Exports DE's real hourly price series from the already-completed Phase 37 headline
run (Germany2027_MarketCoupling_ROEFlex) as an AMIRIS-formatted timeseries CSV, for use
as a file-based "oracle" cross-zone price signal in the CrossZonePrice investigative
experiment. This is DE's REAL, ALREADY-REALISED price from the headline run, not a
genuine forward-looking forecast - an explicit, disclosed upper-bound/oracle test of
whether ROE's storage dispatch closes the shortage-hour gap if it could see DE's actual
price, not a claim that this is a deployable real-time forecasting mechanism."""
import pandas as pd

SRC = r"C:\Users\MuideenOA\Desktop\PyTut\Amiris\examples\backtest\Germany2027_MarketCoupling_ROEFlex\result_Germany2027_MarketCoupling_ROEFlex\DayAheadMarketMultiZone.csv"
OUT = r"C:\Users\MuideenOA\Desktop\PyTut\Amiris\examples\backtest\Germany2027_MarketCoupling_ROEFlex_CrossZonePrice\timeseries\de_actual_price_oracle.csv"

df = pd.read_csv(SRC, sep=";")
df["ts"] = pd.to_datetime(df["TimeStep"])
de = df[df["AgentId"] == 1].set_index("ts")["ElectricityPriceInEURperMWH"].sort_index()

lines = [f"{ts.strftime('%Y-%m-%d_%H:%M:%S')};{val:.4f}" for ts, val in de.items()]
with open(OUT, "w", encoding="utf-8") as f:
    f.write("\n".join(lines) + "\n")

print(f"Saved {OUT}: {len(de)} rows, mean {de.mean():.2f}, max {de.max():.2f}")
