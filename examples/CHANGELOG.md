<!-- SPDX-FileCopyrightText: 2023-2026 German Aerospace Center <amiris@dlr.de>

SPDX-License-Identifier: CC0-1.0 -->

# Changelog
## [7.1.0](https://gitlab.com/dlr-ve/esy/amiris/examples/-/releases/v7.1.0) - 2026-04-22
### Added
- Add `SectorCoupling` to `demo` #72 (@dlr-cjs, @dlr-jk)

## [7.0.0](https://gitlab.com/dlr-ve/esy/amiris/examples/-/releases/v7.0.0) - 2026-04-20
_If you are upgrading: please see `UPGRADING.md`_
### Changed
- **Breaking**: Update minimum requirement for AMIRIS to version 4.1.0 #65 (@dlr-cjs)
- Update metadata in scenario.yaml to match used version of AMIRIS #64 (@dlr-cjs)

### Added
- Add folder `scripts` in section `backtest` to hold data preparation scripts #67 (@dlr-cjs, @dlr_fn, @dlr-jk)

## [6.0.0](https://gitlab.com/dlr-ve/esy/amiris/examples/-/releases/v6.0.0) - 2025-09-09
_If you are upgrading: please see `UPGRADING.md`_
### Changed
- **Breaking**: Update minimum requirement for AMIRIS to version 4.0.0 #64 (@dlr-cjs)
- **Breaking**: Update scenarios to match schema of AMIRIS v4.0.0 #64 (@dlr-cjs)
- Update markups for conventional power plants due to changed storage dispatch behaviour #64 (@dlr-cjs)
- Update `Germany2019` backtesting example to showcase competition of storage units #64 (@dlr-cjs)
- Reorganised file content in `agents\Conventionals.yaml` to compact list with same agent types #64 (@dlr-cjs) 

## [5.1.0](https://gitlab.com/dlr-ve/esy/amiris/examples/-/releases/v5.1.0) - 2025-08-01
### Changed
- Move backtesting scenarios to new subfolder `backtest` #46 (@dlr-cjs)
- Move demo scenarios to new subfolder `demo` #46 (@dlr-cjs)
- Split `Agents` section in each scenario to individual files in new subfolder `agents` #56 (@dlr-cjs)
- Update all contracts to use the new keyword `Every` #53 (@dlr-cjs)
- Update minimum version to `amirispy>=3.3.0` #53 (@dlr-cjs)
- Update metadata in schema #58 (@dlr-cjs, @litotes18)
- Add license statement for REUSE compatibility for own files and data #8 (@dlr-cjs)
- Ensure `CHANGELOG.md` is updated using CI !8 (@dlr-cjs)

## [5.0.0](https://gitlab.com/dlr-ve/esy/amiris/examples/-/releases/v5.0.0) - 2025-07-21
_If you are upgrading: please see `UPGRADING.md`_
### Changed
- **Breaking**: Update minimum requirement for AMIRIS to version 3.6.0 #54 (@dlr-cjs)
- **Breaking**: Replace `MeritOrderForecaster` with `SensitivityForecaster` in all scenarios #54 (@dlr-cjs)
- Update schema.yaml to AMIRIS v3.6.0 #54 (@dlr-cjs)

## [4.0.0](https://gitlab.com/dlr-ve/esy/amiris/examples/-/releases/v4.0.0) - 2025-05-05
_If you are upgrading: please see `UPGRADING.md`_
### Changed
- **Breaking**: Update minimum requirement for AMIRIS is to version 3.5.0 #47 (@dlr-cjs)
- **Breaking**: Replace `StorageTrader` with `GenericFlexibilityTrader` in all scenarios #47 (@dlr-cjs)
- Update schema.yaml to AMIRIS v3.5.0 #47 (@dlr-cjs)

## [3.2.0](https://gitlab.com/dlr-ve/esy/amiris/examples/-/releases/v3.2.0) - 2025-02-21
### Changed
- Update schema.yaml to AMIRIS v3.4.0 #45 (@dlr_fn)

## [3.1.0](https://gitlab.com/dlr-ve/esy/amiris/examples/-/releases/v3.1.0) - 2025-01-29
### Changed
- Update schema.yaml to AMIRIS v3.3.0 #42 (@dlr_fn, @dlr-cjs)

## [3.0.0](https://gitlab.com/dlr-ve/esy/amiris/examples/-/releases/v3.0.0) - 2024-09-20
_If you are upgrading: please see `UPGRADING.md`_
### Changed
- **Breaking**: Update minimum requirement for AMIRIS is to version 3.0.0 #40 (@dlr_fn, @dlr-cjs)
- **Breaking**: Update schema to latest version from AMIRIS v3.0.0 #40 (@dlr_fn, @dlr-cjs)
- Rename Agent Attributes `Set` to `PolicySet` #40 (@dlr_fn, @dlr-cjs)
- Rename Agent Attributes `OwnMarketZone` and `ConnectedMarketZone` to `MarketZone` #40 (@dlr_fn, @dlr-cjs)
- Update GateClosureInfo contracts to time -30 #40 (@dlr_fn, @dlr-cjs)
- Update GateClosureInfoOffsetInSeconds to new contract time of 31 #40 (@dlr_fn, @dlr-cjs)

### Added
- StringSets for `FuelType`, `MarketZone`, and `PolicySet` #40 (@dlr_fn, @dlr-cjs)
- Add GateClosureInfo contracts to Forecasters #40 (@dlr_fn, @dlr-cjs)

### Removed
- Remove Agent Attributes `ElectricityForecastRequestOffsetInSeconds`, `HydrogenForecastRequestOffsetInSeconds`, and `ForecastRequestOffsetInSeconds` from `StorageTrader`, `ElectrolysisTrader`, `MeritOrderForecaster`, and `PriceForecaster` #40 (@dlr_fn, @dlr-cjs)
- Remove obsolete section `Output` in `GeneralProperties` #40 (@dlr_fn, @dlr-cjs)

### Fixed
- Breaking: Fixed typo in `Refinancing.InvestmentExpensesInEURperMW` #39 (@dlr_fn, @dlr-cjs)

## [2.1.0](https://gitlab.com/dlr-ve/esy/amiris/examples/-/releases/v2.1.0) - 2024-05-28
### Changed
- Modify timeseries to remove unwanted extrapolation #38 (@dlr-cjs, @dlr_fn)
- Update AMIRIS all schema according to v2.2.0 #38 (@dlr-cjs, @dlr_fn)

### Added
- Add simple market coupling example #16 (@dlr_fn)

## [2.0.1](https://gitlab.com/dlr-ve/esy/amiris/examples/-/releases/v2.0.1) - 2024-03-14
### Fixed
- Germany 2016: fixed wrong datapoints in RES timeseries #37 (@dlr_fn, @dlr-cjs)


## [2.0.0](https://gitlab.com/dlr-ve/esy/amiris/examples/-/releases/v2.0.0) - 2024-03-12
_If you are upgrading: please see `UPGRADING.md`_
### Changed
- **Breaking**: Update schema.yaml to conform with latest AMIRIS version #26, #28, #29, #31, #34 (@dlr-cjs, @dlr_jk)
- **Breaking**: Update scenarios to conform with latest AMIRIS version #26, #29, #31 (@dlr-cjs, @dlr_jk)
- **Breaking**: Harmonized timeseries names to snake_case #12 (@dlr_fn)
- Germany 2019: Update all timeseries and markups based on automated data workflow #24 (@dlr-cjs)

### Added 
- Added `Germany2015` example (#19 @dlr-cjs, @dlr_fn)
- Added `Germany2016` example (#20 @dlr-cjs, @dlr_fn)
- Added `Germany2017` example (#21 @dlr-cjs, @dlr_fn)
- Added `Germany2018` example (#22 @dlr-cjs, @dlr_fn)
- Germany 2019: Added power plant availability time series for `hard_coal`, `lignite`, and `nuclear` #12 (@dlr-cjs)
- Added missing policy contracts in scenarios `Austria2019` and `Simple` #32 (@dlr_jk, @litotes18, @dlr-cjs)

### Fixed
- Germany 2019: Remove drops from demand timeseries caused by missing data #24 (@dlr-cjs) 
- All scenarios: Fixed racing condition for Payout action in ConventionalPlantOperator contracts #33 (@dlr_jk, @litotes18, @dlr-cjs)

## [1.1](https://gitlab.com/dlr-ve/esy/amiris/examples/-/releases/v1.1) - 2023-10-19
### Changed
- Updated schema.yaml to conform with latest AMIRIS version #23 (@dlr-cjs)

### Added
- `README.md` to each scenario with units and description of timeseries

### Fixed
- Fuel price timeseries in `Germany2019` example are now calculated correctly #17 (@dlr_fn, @dlr-cjs)

## [1.0](https://gitlab.com/dlr-ve/esy/amiris/examples/-/releases/v1.0) - 2022-08-30
_Initial release_
