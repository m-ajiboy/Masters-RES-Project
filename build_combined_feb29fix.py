"""Builds the combined (inflexible-base + heat-pump) demand series for the Feb29-drop bug
fix, for both 2027 and 2029. Electrolysis and e-mobility are unaffected (separate flex
agents, never used the buggy Feb-29-drop base) so are not rebuilt here."""
import sys
from pathlib import Path
import pandas as pd

from build_demand_feb29fix import build_inflexible_base_fixed, build_heat_pumps

ROOT = Path(r"C:\Users\MuideenOA\Desktop\PyTut\Amiris")
HOURS = 8760

TARGETS = {
    2027: dict(inflexible=604.8502088984375, heat_pumps=18.69330319775391),
    2029: dict(inflexible=652.7285793007812, heat_pumps=23.50352479321289),
}


def main(year):
    t = TARGETS[year]
    base = build_inflexible_base_fixed(year, t["inflexible"])
    heat = build_heat_pumps(year, t["heat_pumps"])
    combined = base + heat
    print(f"Combined total: {combined.sum()/1e6:.4f} TWh (target: {t['inflexible']+t['heat_pumps']:.4f} TWh)")

    OUT = ROOT / "examples" / "backtest" / f"Germany{year}_Feb29DropFix" / "timeseries"
    OUT.mkdir(parents=True, exist_ok=True)
    idx = pd.date_range(f"{year}-01-01", periods=HOURS, freq="h")
    lines = [f"{ts.strftime('%Y-%m-%d_%H:%M:%S')};{val:.4f}" for ts, val in zip(idx, combined)]
    out_path = OUT / f"load_{year}_feb29fix.csv"
    out_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"Saved {out_path}")


if __name__ == "__main__":
    main(int(sys.argv[1]))
