"""Builds the two ImportTrader timeseries for the Germany2027 "with-import" scenario
variant: AvailableEnergyForImport.csv and ImportCostInEURperMWH.csv.

Brainpool's Capacity sheet gives 'Net Exports' = -43.90 TWh for 2027, i.e. Germany is a
projected NET IMPORTER of 43.90 TWh (negative exports). This mirrors the real 2023
outturn, where Germany was a net importer for the first time in decades (24.4 TWh net,
per real ENTSO-E cross-border flow data pulled for this project).

AMIRIS's ImportTrader can only add supply (offer imported energy into the day-ahead
market) - there is no ExportTrader for a single, uncoupled market zone, so this variant
captures only the import side of cross-border trade, not Germany's real export flows.
That is a deliberate, documented simplification (a full treatment would need a multi-zone
MarketCoupling setup).

  - AvailableEnergyForImport: real 2023 net cross-border flow (imports - exports),
    clipped at zero (only the hours Germany was a real net importer are usable), then
    rescaled so the annual total matches Brainpool's 43.90 TWh 2027 target. This keeps
    the real historical TIMING of import need (e.g. Dunkelflaute periods, winter
    evenings) rather than inventing a shape.
  - ImportCostInEURperMWH: real 2023 French day-ahead price, used as a proxy for import
    cost. France is Germany's largest, most stable single interconnector partner
    (large steady nuclear baseload) - a documented simplification standing in for a
    flow-weighted mix of all 11 of DE_LU's neighbouring price zones.
"""
from pathlib import Path
import pandas as pd

ROOT = Path(__file__).parent
SRC = ROOT / "examples" / "backtest" / "Germany2023" / "timeseries"
OUT = ROOT / "examples" / "backtest" / "Germany2027_WithImport" / "timeseries"
OUT.mkdir(parents=True, exist_ok=True)

YEAR = 2027
HOURS = 8760
BRAINPOOL_NET_IMPORT_TWH = 43.89669867352295


def write_series(values, out_name, label):
    idx = pd.date_range(f"{YEAR}-01-01", periods=HOURS, freq="h")
    lines = [f"{ts.strftime('%Y-%m-%d_%H:%M:%S')};{v:.4f}" for ts, v in zip(idx, values)]
    (OUT / out_name).write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"  {label}: saved {out_name} ({len(lines)} rows)")


def build_available_energy_for_import():
    imports = pd.read_csv(SRC / "raw_imports_total_2023.csv", index_col=0)["value"].values[:HOURS]
    exports = pd.read_csv(SRC / "raw_exports_total_2023.csv", index_col=0)["value"].values[:HOURS]
    net = imports - exports
    net_import_hours = net.clip(min=0)
    real_total_twh = net_import_hours.sum() / 1_000_000
    target_mwh = BRAINPOOL_NET_IMPORT_TWH * 1_000_000
    scale = target_mwh / net_import_hours.sum()
    scaled = net_import_hours * scale
    print(f"  Available import energy: real 2023 net-import-hour shape ({(net>0).sum()} hours, "
          f"{real_total_twh:.2f} TWh) rescaled x{scale:.3f} to Brainpool's "
          f"{BRAINPOOL_NET_IMPORT_TWH:.2f} TWh target (new peak {scaled.max():.0f} MW)")
    write_series(scaled, "AvailableEnergyForImport.csv", "AvailableEnergyForImport")


def build_import_cost():
    fr_price = pd.read_csv(SRC / "raw_fr_price_2023.csv", index_col=0)["value"].values[:HOURS]
    print(f"  Import cost: real 2023 French day-ahead price (mean {fr_price.mean():.2f} "
          f"EUR/MWh, min {fr_price.min():.2f}, max {fr_price.max():.2f})")
    write_series(fr_price, "ImportCostInEURperMWH.csv", "ImportCostInEURperMWH")


def main():
    print("Building Germany2027_WithImport timeseries:")
    build_available_energy_for_import()
    build_import_cost()


if __name__ == "__main__":
    main()
