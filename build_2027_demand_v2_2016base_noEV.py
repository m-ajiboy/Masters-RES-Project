"""Rebuilds the 2016-base V2 demand series (see build_2027_demand_v2_2016base_noelectrolysis.py)
but ALSO without e-mobility - e-mobility is pulled out and modeled instead as a separate,
price-responsive GenericFlexibilityTrader agent (see agents/EMobility.yaml in the
Germany2027_FlexEMobility scenario), following the same proven pattern used for electrolysis
(Phase 20): a one-way flexible consumer that must eventually draw its full annual total, but
can choose WHEN. Electrolysis remains excluded too (already handled by its own agent,
unchanged from Germany2027_FlexElectrolysis). Only the inflexible base (real 2016 data) and
heat pumps (real 2009 temperature) remain in the combined series."""
from pathlib import Path
import pandas as pd

from build_2027_demand_v2_split import ROOT, HOURS, YEAR, get_brainpool_demand_components
from build_2027_demand_v2_2016base import build_inflexible_base_2016
from build_2027_heatpump_2009temp import build_heat_pumps_real_2009

OUT = ROOT / "examples" / "backtest" / "Germany2027_FlexEMobility" / "timeseries"
OUT.mkdir(parents=True, exist_ok=True)


def main():
    comp = get_brainpool_demand_components()

    print("Building demand WITHOUT electrolysis AND WITHOUT e-mobility (2016-base, real 2009 heat-pump temperature):")
    base = build_inflexible_base_2016(comp["inflexible"])
    heat = build_heat_pumps_real_2009(comp["heat_pumps"])

    combined_mwh = base + heat
    combined_total_twh = combined_mwh.sum() / 1_000_000
    remaining_target = comp["inflexible"] + comp["heat_pumps"]
    print(f"\nCombined total (excl. electrolysis, excl. e-mobility): {combined_total_twh:.4f} TWh "
          f"(inflexible+heat target: {remaining_target:.4f} TWh)")
    print(f"Electrolysis ({comp['electrolysis']:.4f} TWh) and e-mobility ({comp['e_mobility']:.4f} TWh) "
          f"are each handled by their own separate agent.")

    idx = pd.date_range(f"{YEAR}-01-01", periods=HOURS, freq="h")
    lines = [f"{ts.strftime('%Y-%m-%d_%H:%M:%S')};{val:.4f}" for ts, val in zip(idx, combined_mwh)]
    out_path = OUT / "load_v2_2016base_noEV_noelectrolysis.csv"
    out_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"\nSaved {out_path}")


if __name__ == "__main__":
    main()
