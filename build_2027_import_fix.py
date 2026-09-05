"""Builds the FINAL, per-version-calibrated ImportTrader timeseries for the Germany2027
with-import variants, replacing the original (real-2023-net-flow-shaped)
AvailableEnergyForImport.csv.

Diagnosis that motivated this fix (see conversation record / build docs): in the original
with-import builds, AvailableEnergyForImport was shaped from real 2023 net cross-border
flow timing, clipped to net-import hours only, then rescaled to Brainpool's 43.90 TWh
annual target. Checking the V2-with-import result directly: of 469 shortage hours,
301 (64%) had ZERO import available that hour - purely because 2023's own historical
timing happened to show a net export (or zero) at that specific hour-of-year, which has
no relationship to when THIS build's synthetic 2027 demand/renewable shapes actually run
short.

The fix: decouple import availability from any historical TIMING pattern entirely - a
flat, constant ceiling every hour, letting the market (real 2023 French day-ahead price,
unchanged) decide hour by hour how much of it actually gets used.

A calibration sweep (build_2027_import_moderate.py, compare_2027_import_ceiling_sweep.py)
against Brainpool's real 2027 price forecast tested 20,000 / 25,000 / 30,000 / 37,650 MW
flat ceilings. Finding: the best ceiling is NOT the same for both demand versions -

  - V2 (component-split demand, the more refined build): 30,000 MW gives the best overall
    fit - shortage hours nearly eliminated (3 remaining, 0.03%), MAE/correlation
    essentially matching the more generous ceiling, and a meaningfully smaller bias than
    the original 37,650 MW pass.
  - V1 (BDEW-for-everything demand, peak 138 GW - well above Brainpool's own 119 GW
    stated peak): 30,000 MW is NOT enough - shortage hours actually rise (73 -> 164) and
    bias gets much worse (+7.42 -> +39.46), because V1's much larger structural demand
    peak genuinely needs more import headroom to stay covered. V1 keeps the original
    37,649.98 MW ceiling (the real observed peak single-hour gross import into DE_LU in
    2023) as its final value.

This is itself a finding: how much import headroom is needed to close the AMIRIS-
Brainpool gap depends on how realistic the underlying demand shape already is - a cruder
demand model needs a bigger import buffer to compensate, a more refined one doesn't.
"""
from pathlib import Path
import pandas as pd

ROOT = Path(__file__).parent
SRC = ROOT / "examples" / "backtest" / "Germany2023" / "timeseries"

YEAR = 2027
HOURS = 8760

FINAL_CEILINGS_MW = {
    "Germany2027_WithImport_Fix": 30_000.0,       # V2 - calibrated
    "Germany2027_V1WithImport_Fix": 37_649.98,    # V1 - real observed 2023 peak gross import hour
}


def write_series(values, out_dir, out_name, label):
    idx = pd.date_range(f"{YEAR}-01-01", periods=HOURS, freq="h")
    lines = [f"{ts.strftime('%Y-%m-%d_%H:%M:%S')};{v:.4f}" for ts, v in zip(idx, values)]
    (out_dir / out_name).write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"  {label}: saved {out_dir / out_name} ({len(lines)} rows)")


def build_for(out_dir: Path, ceiling_mw: float):
    out_dir.mkdir(parents=True, exist_ok=True)

    flat = [ceiling_mw] * HOURS
    print(f"  Available import energy (FINAL): flat {ceiling_mw:.2f} MW every hour "
          f"= {ceiling_mw * HOURS / 1_000_000:.2f} TWh ceiling if fully used every hour "
          f"(no annual target imposed - market decides actual clearing).")
    write_series(flat, out_dir, "AvailableEnergyForImport.csv", "AvailableEnergyForImport")

    fr_price = pd.read_csv(SRC / "raw_fr_price_2023.csv", index_col=0)["value"].values[:HOURS]
    print(f"  Import cost (unchanged): real 2023 French day-ahead price (mean {fr_price.mean():.2f} "
          f"EUR/MWh, min {fr_price.min():.2f}, max {fr_price.max():.2f})")
    write_series(fr_price, out_dir, "ImportCostInEURperMWH.csv", "ImportCostInEURperMWH")


def main():
    for scenario_name, ceiling_mw in FINAL_CEILINGS_MW.items():
        out_dir = ROOT / "examples" / "backtest" / scenario_name / "timeseries"
        print(f"\nBuilding final import timeseries for {scenario_name} ({ceiling_mw:.2f} MW):")
        build_for(out_dir, ceiling_mw)


if __name__ == "__main__":
    main()
