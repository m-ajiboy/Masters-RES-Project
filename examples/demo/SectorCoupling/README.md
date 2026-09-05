# Sector Coupling Demo

Demonstration of modelling flexibilities from different demand sectors in AMIRIS, i.e., 
* pumped-hydro power plants, 
* heat pumps with flexible temperature limits, 
* electric vehicles with flexible unidirectional and bidirectional charging, and
* industrial load shifting.

## Time Series
| File                                   | Description                                                                         | Unit       |
|----------------------------------------|-------------------------------------------------------------------------------------|------------|
| `biomass_profile.csv`                  | Normalized profile of biomass generation                                            | 1          |
| `co2_price.csv`                        | Price of CO2 emission allowances                                                    | EUR/t_CO2  |
| `ev_connection_power`                  | Total power of electric vehicles with flexible charging tariffs connected the grid  | MW         |
| `ev_inflow_driving.csv`                | Energy outflow (i.e. negative inflow) of electric vehicles due to driving           | MWh/h      |
| `ev_max_battery_content.csv`           | Maximum achievable energy content of electric vehicles batteries                    | MWh        |
| `ev_min_battery_content.csv`           | Minimum allowed energy content of electric vehicles batteries                       | MWh        |
| `hard_coal_availability.csv`           | Normalized availability of hard coal power plants                                   | 1          |
| `hard_coal_price.csv`                  | Delivery price to power plant per thermal MWH of hard coal                          | EUR/MWh_th |
| `heat_pump_efficiency_scaled.csv`      | Coefficient of performance divided by number of households modelled                 | 1          |
| `heat_pump_thermal_inflow.csv`         | Temperature loss of buildings due (i.e. negative inflow)                            | K/h        |          
| `lignite_availability.csv`             | Normalized availability of lignite power plants                                     | 1          |
| `load.csv`                             | Hourly net electricity production of market zone (load minus imports plus exports)  | MWh/h      |
| `load_shifting_lower_energy_limit.csv` | Maximum cumulated load reduction                                                    | MWh        |
| `load_shifting_power.csv`              | Maximum reduction or increase of load                                               | MWh/h      |
| `load_shifting_upper_energy_limit.csv` | Maximum cumulated load increase                                                     | MWh        |
| `natural_gas_price.csv`                | Delivery price to power plant per thermal MWH of natural gas                        | EUR/MWh_th |
| `nuclear_availability.csv`             | Normalized availability of nuclear power plants                                     | 1          |
| `oil_price.csv`                        | Delivery price to power plant per thermal MWH of oil                                | EUR/MWh_th |
| `other_res_profile.csv`                | Normalized profile of generation for power plants declared as "other renewables"    | 1          |
| `run_of_river_profile.csv`             | Normalized profile of generation for run-of-river power plants                      | 1          |
| `solar_profile.csv`                    | Normalized profile of generation for PV power plants                                | 1          |
| `wind_offshore_profile.csv`            | Normalized profile of generation for off-shore wind power plants                    | 1          |
| `wind_onshore_profile.csv`             | Normalized profile of generation for on-shore wind power plants                     | 1          |
