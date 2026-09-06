"""Phase 41: does ROE's own storage physically run dry during Germany's shortage hours?

Phase 40 found DE's import stays suspiciously flat during shortage hours regardless of the
transmission ceiling, and flagged AMIRIS's internal price-convergence stopping logic as the
likely cause - but confirming that needs patching and rebuilding AMIRIS from source, which
was blocked (no Maven toolchain set up).

This is a different, fully-checkable real hypothesis that needs no engine rebuild: ROE's
pumped storage (Id 9601) only holds ~6.4 hours of full-power discharge (213,104 MWH content /
33,303 MW power) - a real, physical limit. Germany's shortage hours cluster in multi-hour
Dunkelflaute blocks. If ROE's pumped storage is draining to empty WHILE DE's shortage block is
still running, that alone would explain a flat, capped import volume - a genuine physical
constraint, not an algorithm quirk. Reservoir hydro (Id 9602) holds 7.77 TWh, orders of
magnitude too large to deplete in a single event, so it is checked mainly as a comparison.

Uses only real result data already on disk from the existing Phase 38 runs - no new AMIRIS run
needed."""
import pandas as pd

ROOT = r"C:\Users\MuideenOA\Desktop\PyTut\Amiris\examples\backtest"

PUMPED_MAX_MWH = 213104.35
PUMPED_MAX_DISCHARGE_MW = 31638.04
RESERVOIR_MAX_MWH = 7774883.23
RESERVOIR_MAX_DISCHARGE_MW = 81787.73

YEARS = {
    2028: rf"{ROOT}\Germany2028_MarketCoupling_ROEFlex\result_Germany2028_MarketCoupling_ROEFlex",
    2029: rf"{ROOT}\Germany2029_MarketCoupling_ROEFlex\result_Germany2029_MarketCoupling_ROEFlex",
}

for year, result_dir in YEARS.items():
    print("\n" + "=" * 78)
    print(f"YEAR {year}")
    print("=" * 78)

    market = pd.read_csv(rf"{result_dir}\DayAheadMarketMultiZone.csv", sep=";")
    market["ts"] = pd.to_datetime(market["TimeStep"])
    de = market[market["AgentId"] == 1].set_index("ts")
    shortage_hours = de[de["ElectricityPriceInEURperMWH"] >= 2999.9].index

    print(f"Shortage hours: {len(shortage_hours)}")
    if len(shortage_hours) == 0:
        continue

    flex = pd.read_csv(rf"{result_dir}\GenericFlexibilityTrader.csv", sep=";")
    flex["ts"] = pd.to_datetime(flex["TimeStep"])
    pumped = flex[flex["AgentId"] == 9601].set_index("ts")
    reservoir = flex[flex["AgentId"] == 9602].set_index("ts")

    imp = de.loc[shortage_hours, "AwardedNetEnergyFromImportInMWH"]
    pumped_soc = pumped.loc[shortage_hours, "StoredEnergyInMWH"]
    pumped_disch = pumped.loc[shortage_hours, "AwardedDischargeEnergyInMWH"]
    reservoir_soc = reservoir.loc[shortage_hours, "StoredEnergyInMWH"]
    reservoir_disch = reservoir.loc[shortage_hours, "AwardedDischargeEnergyInMWH"]

    print(f"\nDE import during shortage hours: mean={imp.mean():,.0f} MWh, "
          f"min={imp.min():,.0f}, max={imp.max():,.0f}, std={imp.std():,.0f}")

    print(f"\nROE pumped storage (max content {PUMPED_MAX_MWH:,.0f} MWh, "
          f"max discharge {PUMPED_MAX_DISCHARGE_MW:,.0f} MW):")
    print(f"  State of charge during shortage hours: mean={pumped_soc.mean():,.0f} MWh "
          f"({pumped_soc.mean()/PUMPED_MAX_MWH:.1%} of max), min={pumped_soc.min():,.0f} MWh "
          f"({pumped_soc.min()/PUMPED_MAX_MWH:.1%} of max)")
    near_empty = (pumped_soc < 0.05 * PUMPED_MAX_MWH).sum()
    print(f"  Hours with SoC below 5% of max: {near_empty} / {len(shortage_hours)}")
    print(f"  Discharge utilization during shortage hours: mean={pumped_disch.mean()/PUMPED_MAX_DISCHARGE_MW:.1%} "
          f"of max power, hours at >=95% of max discharge power: "
          f"{(pumped_disch >= 0.95 * PUMPED_MAX_DISCHARGE_MW).sum()} / {len(shortage_hours)}")

    print(f"\nROE reservoir hydro (max content {RESERVOIR_MAX_MWH:,.0f} MWh, "
          f"max discharge {RESERVOIR_MAX_DISCHARGE_MW:,.0f} MW):")
    print(f"  State of charge during shortage hours: mean={reservoir_soc.mean():,.0f} MWh "
          f"({reservoir_soc.mean()/RESERVOIR_MAX_MWH:.2%} of max), min={reservoir_soc.min():,.0f} MWh "
          f"({reservoir_soc.min()/RESERVOIR_MAX_MWH:.2%} of max)")
    print(f"  Discharge utilization during shortage hours: mean={reservoir_disch.mean()/RESERVOIR_MAX_DISCHARGE_MW:.1%} "
          f"of max power, hours at >=95% of max discharge power: "
          f"{(reservoir_disch >= 0.95 * RESERVOIR_MAX_DISCHARGE_MW).sum()} / {len(shortage_hours)}")

    # Correlation check: does low pumped-storage SoC line up with low import that hour?
    corr = pumped_soc.corr(imp)
    print(f"\nCorrelation between pumped-storage SoC and DE import, across shortage hours: {corr:.3f}")

    # Show the 10 shortage hours with the LOWEST DE import, alongside storage state, to inspect directly
    print("\nThe 10 shortage hours with the SMALLEST DE import (most import-constrained):")
    detail = pd.DataFrame({
        "DE_import_MWh": imp,
        "Pumped_SoC_MWh": pumped_soc,
        "Pumped_SoC_pct": pumped_soc / PUMPED_MAX_MWH,
        "Pumped_discharge_MWh": pumped_disch,
        "Pumped_discharge_pct_of_max": pumped_disch / PUMPED_MAX_DISCHARGE_MW,
        "Reservoir_discharge_pct_of_max": reservoir_disch / RESERVOIR_MAX_DISCHARGE_MW,
    }).sort_values("DE_import_MWh").head(10)
    with pd.option_context("display.float_format", lambda x: f"{x:,.2f}"):
        print(detail)
