"""Rebuilds the 2016-base V2 demand series (see build_2027_demand_v2_2016base.py) but
WITHOUT the electrolysis component - electrolysis is pulled out and modeled instead as a
separate, price-responsive GenericFlexibilityTrader agent (see agents/Electrolysis.yaml in
the Germany2027_FlexElectrolysis scenario), so it can shift WHEN it draws its 14.97 TWh of
electricity toward cheap/negative-price hours instead of drawing it flat every hour. Every
other component (inflexible base on real 2016 data, heat pumps on real 2009 temperature,
e-mobility) is identical to the 2016-base build."""
from pathlib import Path
import pandas as pd

from build_2027_demand_v2_split import ROOT, HOURS, YEAR, get_brainpool_demand_components
from build_2027_demand_v2_split import build_e_mobility
from build_2027_demand_v2_2016base import build_inflexible_base_2016
from build_2027_heatpump_2009temp import build_heat_pumps_real_2009

OUT = ROOT / "examples" / "backtest" / "Germany2027_FlexElectrolysis" / "timeseries"
OUT.mkdir(parents=True, exist_ok=True)


def main():
    comp = get_brainpool_demand_components()

    print("Building demand WITHOUT electrolysis (2016-base, real 2009 heat-pump temperature):")
    base = build_inflexible_base_2016(comp["inflexible"])
    heat = build_heat_pumps_real_2009(comp["heat_pumps"])
    ev = build_e_mobility(comp["e_mobility"])

    combined_mwh = base + heat + ev
    combined_total_twh = combined_mwh.sum() / 1_000_000
    print(f"\nCombined total (excl. electrolysis): {combined_total_twh:.4f} TWh "
          f"(inflexible+heat+ev target: {comp['inflexible']+comp['heat_pumps']+comp['e_mobility']:.4f} TWh)")
    print(f"Electrolysis ({comp['electrolysis']:.4f} TWh) is handled separately by its own agent.")

    idx = pd.date_range(f"{YEAR}-01-01", periods=HOURS, freq="h")
    lines = [f"{ts.strftime('%Y-%m-%d_%H:%M:%S')};{val:.4f}" for ts, val in zip(idx, combined_mwh)]
    out_path = OUT / "load_v2_2016base_noelectrolysis.csv"
    out_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"\nSaved {out_path}")


if __name__ == "__main__":
    main()
