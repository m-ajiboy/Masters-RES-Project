"""Adds the new real bilateral Transmission entries to each zone's DayAheadMarketMultiZone
block in the mesh-topology MarketsAndForecast.yaml, inserted right after each zone's existing
(untouched) DE transmission entry. Each entry pair is added symmetrically to both zones."""
import re

PATH = r"C:\Users\MuideenOA\Desktop\PyTut\Amiris\examples\backtest\Germany2027_MarketCoupling_AllZones_Mesh\agents\MarketsAndForecast.yaml"

with open(PATH, encoding="utf-8") as f:
    content = f.read()

# zone -> list of (partner_zone, comment) new connections to add, in the order they should
# appear. MarketZone code as it should be written in YAML (Norway needs quoting).
def zone_code(z):
    return "'NO'" if z == "NO" else z

NEW_CONNECTIONS = {
    "AT": ["CH"],
    "CH": ["AT", "FR"],
    "BE": ["FR", "NL"],
    "FR": ["BE", "CH"],
    "CZ": ["PL"],
    "PL": ["CZ", "SE"],
    "DK": ["NL", "NO", "SE"],
    "NL": ["BE", "DK", "NO"],
    "NO": ["DK", "NL", "SE"],
    "SE": ["DK", "NO", "PL"],
}

# Anchor: each zone's existing DE-only Transmission block, e.g.:
#       Transmission:
#         - MarketZone: DE
#           CapacityInMW: "./timeseries/transfer_ATtoDE_realflow.csv"
for zone, partners in NEW_CONNECTIONS.items():
    de_line = f'CapacityInMW: "./timeseries/transfer_{zone}toDE_realflow.csv"'
    assert de_line in content, f"Could not find anchor line for zone {zone}: {de_line}"
    new_entries = ""
    for partner in partners:
        new_entries += (
            f"\n        - MarketZone: {zone_code(partner)}\n"
            f'          CapacityInMW: "./timeseries/transfer_{zone}to{partner}_realNTC.csv"'
        )
    content = content.replace(de_line, de_line + new_entries, 1)

with open(PATH, "w", encoding="utf-8") as f:
    f.write(content)

print("All mesh Transmission entries added.")
for zone, partners in NEW_CONNECTIONS.items():
    print(f"  {zone}: +{partners}")
