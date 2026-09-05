"""Computes the ROE hydro storage/subsidy split, grounded in real sourced figures:
- Pumped-storage share of total EU hydro: 30% (46 GW PSH / 153 GW total EU hydro, IHA 2023
  "EU report details importance of hydropower and pumped storage").
- Within the remaining conventional (non-pumped) share, reservoir vs. run-of-river split
  uses Switzerland's real ENTSO-E capacity-by-type data (Phase 35) as the only real
  per-technology reference point available for this aggregate: Hydro Water Reservoir 5,588.0
  MW vs. Hydro Run-of-river 604.5 MW.
- Storage duration (hours) and charge/discharge efficiency for both new ROE storage agents
  reuse Germany's own real, already-calibrated pumped-hydro (6.3989h) and reservoir-hydro
  (111.22h) figures as TECHNOLOGY characteristics (duration/efficiency are engineering
  properties of the technology, reasonably similar across countries - unlike demand or
  capacity, which are genuinely national) - the same category of reuse already applied to
  internationally-traded fuel prices.
"""
TOTAL_HYDRO_MW = 110769.344  # real Eurostat (9 countries) + ENTSO-E Switzerland backfill (Phase 35)

PUMPED_SHARE = 46 / 153  # IHA 2023, real EU-wide figure
CONVENTIONAL_SHARE = 1 - PUMPED_SHARE

CH_RESERVOIR_MW = 5588.0
CH_RUN_OF_RIVER_MW = 604.5
RESERVOIR_FRACTION_OF_CONVENTIONAL = CH_RESERVOIR_MW / (CH_RESERVOIR_MW + CH_RUN_OF_RIVER_MW)
ROR_FRACTION_OF_CONVENTIONAL = CH_RUN_OF_RIVER_MW / (CH_RESERVOIR_MW + CH_RUN_OF_RIVER_MW)

pumped_mw = TOTAL_HYDRO_MW * PUMPED_SHARE
conventional_mw = TOTAL_HYDRO_MW * CONVENTIONAL_SHARE
reservoir_mw = conventional_mw * RESERVOIR_FRACTION_OF_CONVENTIONAL
run_of_river_mw = conventional_mw * ROR_FRACTION_OF_CONVENTIONAL

print(f"Total ROE hydro capacity: {TOTAL_HYDRO_MW:,.1f} MW")
print(f"  Pumped storage (30%, IHA 2023 EU-wide): {pumped_mw:,.1f} MW")
print(f"  Conventional (70%): {conventional_mw:,.1f} MW")
print(f"    Reservoir (CH ratio {RESERVOIR_FRACTION_OF_CONVENTIONAL:.4f}): {reservoir_mw:,.1f} MW")
print(f"    Run-of-river (CH ratio {ROR_FRACTION_OF_CONVENTIONAL:.4f}): {run_of_river_mw:,.1f} MW")
print(f"  Check: {pumped_mw + reservoir_mw + run_of_river_mw:,.1f} MW (should equal total)")

# --- Storage energy content, reusing DE's own real duration ratios ---
DE_PUMPED_DURATION_H = 53607.55 / 8377.60  # 6.3989h
DE_RESERVOIR_DURATION_H = 171282.22 / 1540.00  # 111.22h

pumped_energy_mwh = pumped_mw * DE_PUMPED_DURATION_H
reservoir_energy_mwh = reservoir_mw * DE_RESERVOIR_DURATION_H

print(f"\nPumped storage: {pumped_mw:,.2f} MW x {DE_PUMPED_DURATION_H:.4f}h = {pumped_energy_mwh:,.2f} MWh energy")
print(f"Reservoir hydro: {reservoir_mw:,.2f} MW x {DE_RESERVOIR_DURATION_H:.4f}h = {reservoir_energy_mwh:,.2f} MWh energy")

# --- Charge/discharge power ratios, reusing DE's own real ratios ---
DE_PUMPED_CHARGE_MW = 8377.60
DE_PUMPED_DISCHARGE_MW = 7958.72
DE_RESERVOIR_CHARGE_MW = 1540.00
DE_RESERVOIR_DISCHARGE_MW = 1801.80

pumped_gross_charge = pumped_mw
pumped_net_discharge = pumped_mw * (DE_PUMPED_DISCHARGE_MW / DE_PUMPED_CHARGE_MW)
reservoir_gross_charge = reservoir_mw
reservoir_net_discharge = reservoir_mw * (DE_RESERVOIR_DISCHARGE_MW / DE_RESERVOIR_CHARGE_MW)

print(f"\nPumped storage: GrossChargingPowerInMW={pumped_gross_charge:,.2f}, NetDischargingPowerInMW={pumped_net_discharge:,.2f}")
print(f"Reservoir hydro: GrossChargingPowerInMW={reservoir_gross_charge:,.2f}, NetDischargingPowerInMW={reservoir_net_discharge:,.2f}")

energy_res_pumped = pumped_energy_mwh / 34  # ~34 discretisation steps, matching DE's own resolution scale
energy_res_reservoir = reservoir_energy_mwh / 1222  # matching DE's own resolution scale (171282/140.05=1223)
print(f"\nSuggested EnergyResolutionInMWH: pumped={energy_res_pumped:,.2f}, reservoir={energy_res_reservoir:,.2f}")
