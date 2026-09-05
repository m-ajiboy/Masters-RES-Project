[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.7789049.svg)](https://doi.org/10.5281/zenodo.7789049)

# Examples

Example configurations built for [AMIRIS 4.0.0](https://gitlab.com/dlr-ve/esy/amiris/amiris/-/releases/v4.0.0).
Requires `amirispy>=3.3.0` or `fameio>=3.5.1`. 
See the individual licence information in the respective scenarios.

## How-to

Please use the latest version of [AMIRIS-Py](https://gitlab.com/dlr-ve/esy/amiris/amiris-py) to run AMIRIS-Examples.
Follow these very few instructions in its [README](https://gitlab.com/dlr-ve/esy/amiris/amiris-py/-/blob/main/README.md) to have AMIRIS running in no time.

## Scenarios

The example scenarios are spread across subfolders grouped by use case. 

### Demo

This folder covers small scenarios that demonstrate how to parametrise AMIRIS:

* Simple: running for one day using dummy data
* SimpleCoupled: coupling two markets running for one day using dummy data

### Backtest

This folder contains historical simulations for different market zones and years:

* Austria2019: Austrian day-ahead market in 2019
* Germany2015: German day-ahead market in 2015
* Germany2016: German day-ahead market in 2016
* Germany2017: German day-ahead market in 2017
* Germany2018: German day-ahead market in 2018
* Germany2019: German day-ahead market in 2019 with 18 competing storage units

The folder `scripts` contains additional scripts to extract and reformat data from public data sources.

### Future

This folder will contain scenarios to analyse possible energy market futures.
Currently, no future scenario is available.

## Citing AMIRIS Examples

If you use AMIRIS Examples in your scientific work please cite:

Kristina Nienhaus, Christoph Schimeczek, Ulrich Frey, Evelyn Sperber, Seyedfarzad Sarfarazi, Felix Nitsch, Johannes Kochems & A. Achraf El Ghazi (2023). AMIRIS Examples. Zenodo. [doi: 10.5281/zenodo.7789049](https://doi.org/10.5281/zenodo.7789049)

## Acknowledgments

We thank those who contributed to enhancing the AMIRIS examples:
* [v1.1](https://gitlab.com/dlr-ve/esy/amiris/examples/-/releases/v1.1) Dr. Tom Bauermann, for pointing out errors in historical fuel prices
