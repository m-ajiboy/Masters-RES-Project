# Simple Example
Simple scenario with two market zones running for one day with dummy data. Additionally, B is a net importer (e.g. negative demand in hour 2 and 3).
"Negative" demand is handled as a timeseries to the `ImportTrader` offered as supply on the energy exchange.

## Time Series
| File                     | Description                                                         | Unit     |
|--------------------------|---------------------------------------------------------------------|----------|
| `load.csv`               | Hourly electric energy demand                                       | MWh/h    |
| `pv_yield_profile.csv`   | Normalized profile of generation for PV power plants                | 1        |
| `wind_yield_profile.csv` | Normalized profile of generation for wind power plants              | 1        |
| `transfer_AtoB.csv`      | Hourly net transfer capacity for shifting demand from market A to B | MWh/h    |
| `transfer_BtoA.csv`      | Hourly net transfer capacity for shifting demand from market B to A | MWh/h    |
| `imports_B.csv`          | Hourly imports to market B which are offered at energy exchange     | MWh/h    |
