# -*- coding: utf-8 -*-
"""
Builds Germany2023's hard_coal_price.csv, natural_gas_price.csv, and
oil_price.csv from free public FRED series (which mirror the IMF/World Bank
"Global Price of Commodities" dataset for gas/coal, and daily Brent spot for
oil), converted into the EUR/MWh_th unit AMIRIS's existing scenarios use.

CO2 (EU ETS allowance) price is handled separately - no free bulk-download
source was found for it, so co2_price.csv is not produced by this script.

Disclosed unit-conversion assumptions (these are genuine methodological
choices, not exact universal constants - flagged here rather than hidden):
  - Natural gas: 1 MMBtu = 0.293071 MWh (this one IS an exact energy-unit
    conversion, not an approximation)
  - Hard coal: 1 tonne benchmark thermal coal ~= 6.978 MWh_th
    (assumes ~6,000 kcal/kg net calorific value, the typical benchmark
    thermal coal quality - e.g. Newcastle/API2-style benchmarks)
  - Oil: 1 barrel of Brent crude ~= 1.7 MWh_th (a commonly used approximate
    conversion figure for average crude oil energy content)
  - USD -> EUR conversion uses FRED's daily EUR/USD spot rate (DEXUSEU),
    monthly-averaged where matching a monthly gas/coal price point
"""
import os
import pandas as pd
import requests

OUT_DIR = r"C:\Users\MuideenOA\Desktop\PyTut\Amiris\examples\backtest\Germany2023\timeseries"
os.makedirs(OUT_DIR, exist_ok=True)

YEAR = 2023
START = f"{YEAR}-01-01"
END = f"{YEAR}-12-31"

MWH_PER_MMBTU = 0.293071
MWH_PER_TONNE_COAL = 6.978
MWH_PER_BARREL_OIL = 1.7


def fetch_fred(series_id: str) -> pd.Series:
    url = f"https://fred.stlouisfed.org/graph/fredgraph.csv?id={series_id}&cosd={START}&coed={END}"
    r = requests.get(url, timeout=30)
    r.raise_for_status()
    from io import StringIO
    df = pd.read_csv(StringIO(r.text))
    df.columns = ["date", "value"]
    df["date"] = pd.to_datetime(df["date"])
    df["value"] = pd.to_numeric(df["value"], errors="coerce")
    return df.set_index("date")["value"]


def save_amiris_price_csv(series: pd.Series, path: str):
    s = series.dropna().sort_index()
    lines = [f"{ts.strftime('%Y-%m-%d')}_00:00:00;{val:.4f}" for ts, val in s.items()]
    last_year = s.index[-1].year
    last_val = s.iloc[-1]
    lines.append(f"{last_year + 1}-01-01_00:00:00;{last_val:.4f}")
    lines.append(f"{last_year + 2}-01-01_00:00:00;{last_val:.4f}")
    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")
    print(f"Saved {path} ({len(s)} real rows + 2 padding rows)")


print("Fetching EUR/USD exchange rate...")
eurusd_daily = fetch_fred("DEXUSEU").ffill()
eurusd_monthly = eurusd_daily.resample("MS").mean()  # month-start-aligned average

# ---- Oil: Brent, USD/barrel, daily -> EUR/MWh_th ----
print("Fetching Brent oil price...")
oil_usd_per_bbl = fetch_fred("DCOILBRENTEU").ffill()
eurusd_matched = eurusd_daily.reindex(oil_usd_per_bbl.index).ffill()
oil_eur_per_mwh = (oil_usd_per_bbl / eurusd_matched) / MWH_PER_BARREL_OIL
save_amiris_price_csv(oil_eur_per_mwh, os.path.join(OUT_DIR, "oil_price.csv"))

# ---- Natural gas: IMF EU gas benchmark, USD/MMBtu, monthly -> EUR/MWh_th ----
print("Fetching natural gas price...")
gas_usd_per_mmbtu = fetch_fred("PNGASEUUSDM").dropna()
eurusd_matched = eurusd_monthly.reindex(gas_usd_per_mmbtu.index).ffill()
gas_eur_per_mwh = (gas_usd_per_mmbtu / eurusd_matched) / MWH_PER_MMBTU
save_amiris_price_csv(gas_eur_per_mwh, os.path.join(OUT_DIR, "natural_gas_price.csv"))

# ---- Hard coal: IMF Australia coal benchmark, USD/tonne, monthly -> EUR/MWh_th ----
print("Fetching coal price...")
coal_usd_per_tonne = fetch_fred("PCOALAUUSDM").dropna()
eurusd_matched = eurusd_monthly.reindex(coal_usd_per_tonne.index).ffill()
coal_eur_per_mwh = (coal_usd_per_tonne / eurusd_matched) / MWH_PER_TONNE_COAL
save_amiris_price_csv(coal_eur_per_mwh, os.path.join(OUT_DIR, "hard_coal_price.csv"))

print("\nSummary (EUR/MWh_th):")
print(f"  Oil:        min={oil_eur_per_mwh.min():.2f}  max={oil_eur_per_mwh.max():.2f}  mean={oil_eur_per_mwh.mean():.2f}")
print(f"  Gas:        min={gas_eur_per_mwh.min():.2f}  max={gas_eur_per_mwh.max():.2f}  mean={gas_eur_per_mwh.mean():.2f}")
print(f"  Hard coal:  min={coal_eur_per_mwh.min():.2f}  max={coal_eur_per_mwh.max():.2f}  mean={coal_eur_per_mwh.mean():.2f}")
print("\nDone. co2_price.csv NOT produced - handle separately (see conversation).")
