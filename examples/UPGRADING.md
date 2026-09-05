<!-- SPDX-FileCopyrightText: 2023-2026 German Aerospace Center <amiris@dlr.de>

SPDX-License-Identifier: Apache-2.0 -->
# Upgrading

## [7.0.0]

This version requires AMIRIS version >= 4.1.0.
We recommend to use [amirispy](https://pypi.org/project/amirispy) and download the latest AMIRIS artifact like so: `amiris download --force --mode model`.

Specifically, these new mandatory configuration parameters were added to `GenericFlexibilityTrader`:
* `VariableCostInEURperMWH`, 
* `MaximumShiftTimeInHours`, 
* `EnableProlonging`, 
* `PenaltyCostInEURperMWH`, 
* `OnOverflow`, 
* `OnUnderflow`.

## [6.0.0]

This version requires AMIRIS version >= 4.0.0.
We recommend to use [amirispy](https://pypi.org/project/amirispy) and download the latest AMIRIS artifact like so: `amiris download --force --mode model`.

Specifically, these breaking changes occurred:
* Rename `GenericFlexibilityTrader` assessment function types to `MIN_SYSTEM_COST` and `MAX_PROFIT`
* PlantBuilder: Replace `PlannedAvailability` and `UnplannedAvailabilityFactor` attributes with `OutageFactor`
* Use bid prices to estimate system cost in `GenericFlexibilityTrader`'s assessment function `MIN_SYSTEM_COST`

If you update both, the AMIRIS model and examples, no manual update steps are necessary.

## [5.0.0]

This version requires AMIRIS version >= 3.6.0 < 4.0.
We recommend to use [amirispy](https://pypi.org/project/amirispy) and download the latest AMIRIS artifact like so: `amiris download --force --mode model`.

## [4.0.0]

This version requires AMIRIS version >= 3.5.0 < 3.6.
We recommend to use [amirispy](https://pypi.org/project/amirispy) and download the latest AMIRIS artifact like so: `amiris download --force --mode model`.

## [3.0.0]

This version requires AMIRIS version >= 3.0.0 < 3.5.
We recommend to use [amirispy](https://pypi.org/project/amirispy) and download the latest AMIRIS artifact like so: `amiris install --force --mode model`.

## [2.0.0]

This version requires AMIRIS version >= 2.0.0 < 3.0.
We recommend to use [amirispy](https://pypi.org/project/amirispy) and download the latest AMIRIS artifact like so: `amiris install --force --mode model`.