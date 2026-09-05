"""Builds a MODERATE flat import ceiling, replacing the (too-generous, 37,649.98 MW)
first fix. Diagnosis of the original with-import run's own unmet-demand data showed:
median shortfall at shortage hours was only 5,028.6 MW, 90th percentile 15,324.7 MW,
worst-case 33,653.6 MW. The first fix's flat ceiling was set at the worst-case+headroom
level (37,650 MW), which also let import compete freely in nearly every ordinary hour,
overshooting Brainpool's price level (bias flipped from strongly positive to -12.59
EUR/MWh for V2). This builds a smaller, still-flat ceiling intended to cover the large
majority of real shortage instances without flooding every normal hour with cheap import.
"""
from pathlib import Path
import sys
import pandas as pd

ROOT = Path(__file__).parent
SRC = ROOT / "examples" / "backtest" / "Germany2023" / "timeseries"

YEAR = 2027
HOURS = 8760


def write_series(values, out_dir, out_name, label):
    idx = pd.date_range(f"{YEAR}-01-01", periods=HOURS, freq="h")
    lines = [f"{ts.strftime('%Y-%m-%d_%H:%M:%S')};{v:.4f}" for ts, v in zip(idx, values)]
    (out_dir / out_name).write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"  {label}: saved {out_dir / out_name} ({len(lines)} rows)")


def build_for(out_dir: Path, ceiling_mw: float):
    out_dir.mkdir(parents=True, exist_ok=True)
    flat = [ceiling_mw] * HOURS
    print(f"  Available import energy (MODERATE): flat {ceiling_mw:.1f} MW every hour "
          f"= {ceiling_mw * HOURS / 1_000_000:.2f} TWh ceiling if fully used every hour.")
    write_series(flat, out_dir, "AvailableEnergyForImport.csv", "AvailableEnergyForImport")

    fr_price = pd.read_csv(SRC / "raw_fr_price_2023.csv", index_col=0)["value"].values[:HOURS]
    write_series(fr_price, out_dir, "ImportCostInEURperMWH.csv", "ImportCostInEURperMWH")


def main():
    ceiling_mw = float(sys.argv[1]) if len(sys.argv) > 1 else 20000.0
    for scenario_name in ["Germany2027_WithImport_Fix", "Germany2027_V1WithImport_Fix"]:
        out_dir = ROOT / "examples" / "backtest" / scenario_name / "timeseries"
        print(f"\nBuilding moderate ({ceiling_mw:.0f} MW) import ceiling for {scenario_name}:")
        build_for(out_dir, ceiling_mw)


if __name__ == "__main__":
    main()
