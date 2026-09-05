# Germany 2017 Example
Historical simulation of German day-ahead market in 2017

## Time Series
| File                            | Description                                                                                         | Unit       |
|---------------------------------|-----------------------------------------------------------------------------------------------------|------------|
| `backup_storage_dispatch.csv`   | Hourly profile of backup storage dispatch (relevant for "Kalte Dunkelflaute" event in January 2017) | MWh/h      |
| `biomass_profile.csv`           | Normalized profile of biomass generation                                                            | 1          |
| `co2_price.csv`                 | Price of CO2 emission allowances                                                                    | EUR/t_CO2  |
| `hard_coal_availability.csv`    | Normalized availability of hard coal power plants                                                   | 1          |
| `hard_coal_price.csv`           | Delivery price to power plant per thermal MWH of hard coal                                          | EUR/MWh_th |
| `lignite_availability.csv`      | Normalized availability of lignite power plants                                                     | 1          |
| `load.csv`                      | Hourly net electricity production of market zone (load minus imports plus exports)                  | MWh/h      |
| `natural_gas_price.csv`         | Delivery price to power plant per thermal MWH of natural gas                                        | EUR/MWh_th |
| `nuclear_availability.csv`      | Normalized availability of nuclear power plants                                                     | 1          |
| `oil_price.csv`                 | Delivery price to power plant per thermal MWH of oil                                                | EUR/MWh_th |
| `other_res_profile.csv`         | Normalized profile of generation for power plants declared as "other renewables"                    | 1          |
| `run_of_river_profile.csv`      | Normalized profile of generation for run-of-river power plants                                      | 1          |
| `solar_profile.csv`             | Normalized profile of generation for PV power plants                                                | 1          |
| `wind_offshore_profile.csv`     | Normalized profile of generation for off-shore wind power plants                                    | 1          |
| `wind_onshore_profile.csv`      | Normalized profile of generation for on-shore wind power plants                                     | 1          |
