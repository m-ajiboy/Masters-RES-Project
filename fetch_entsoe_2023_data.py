# -*- coding: utf-8 -*-
"""
Pulls the raw ingredients needed to build the Germany2023 AMIRIS scenario
directly from the ENTSO-E Transparency Platform, using the entsoe-py library.

Data pulled (all for Germany/Luxembourg bidding zone, calendar year 2023):
  1. Installed generation capacity per technology (one snapshot value per
     technology - used both to set AMIRIS's InstalledPowerInMW attributes
     and to normalise renewable generation into 0-1 capacity-factor profiles)
  2. Hourly electricity demand (load)
  3. Hourly generation per renewable technology, converted into the
     normalised 0-1 "yield profile" format AMIRIS expects

Requires a free ENTSO-E account and an API security token (Account Settings
-> "Web Api Security Token" -> Generate Token, or request it be enabled via
transparency@entsoe.eu if that option isn't visible on your account).
"""
import os
import pandas as pd
from entsoe import EntsoePandasClient

TOKEN_FILE = r"C:\Users\MuideenOA\Desktop\PyTut\Amiris\Entso Token.txt"
OUT_DIR = r"C:\Users\MuideenOA\Desktop\PyTut\Amiris\examples\backtest\Germany2023\timeseries"
os.makedirs(OUT_DIR, exist_ok=True)

# The token file has a label on the first line and the token itself on the
# last non-empty line - this just pulls that last line out.
with open(TOKEN_FILE, encoding="utf-8") as f:
    token = [line.strip() for line in f if line.strip()][-1]

client = EntsoePandasClient(api_key=token)

# Fetch in UTC deliberately: AMIRIS's own example input files use a fixed,
# continuous 8,760-hour grid with no daylight-saving gaps or duplicates, so
# UTC is the timezone convention that matches them.
START = pd.Timestamp("2023-01-01", tz="UTC")
END = pd.Timestamp("2024-01-01", tz="UTC")

# ENTSO-E's production/source-type (PSR) codes for each renewable technology
# AMIRIS models, paired with the installed capacity (MW) used to normalise
# generation into a 0-1 profile. Capacities came from a separate call to
# query_installed_generation_capacity("DE_LU", ...).
RENEWABLE_PSR_TYPES = {
    "solar_profile": ("B16", 63366.03),          # Solar
    "wind_onshore_profile": ("B19", 57741.55),   # Wind Onshore
    "wind_offshore_profile": ("B18", 8128.82),   # Wind Offshore
    "run_of_river_profile": ("B11", 3737.25),    # Hydro Run-of-river
    "biomass_profile": ("B01", 8513.80),         # Biomass
    "other_res_profile": ("B15", 384.15),        # Other renewable
}


def save_as_amiris_timeseries(series: pd.Series, path: str, pad_value):
    """Writes a pandas Series out in the exact format AMIRIS's timeseries
    CSVs use: no header, semicolon-delimited, 'YYYY-MM-DD_HH:MM:SS;value',
    plus two trailing placeholder rows one and two years after the data ends
    (a convention already used by every shipped AMIRIS example file)."""
    s = series.copy()
    s.index = s.index.tz_localize(None)
    s = s[~s.index.duplicated(keep="first")].sort_index()

    # ENTSO-E publishes load/generation at 15-minute resolution for this
    # period; AMIRIS wants one value per hour, so average down to hourly.
    s = s.resample("h").mean()

    # European grid data reliably has a single missing hour at the spring
    # daylight-saving transition (e.g. 26 Mar 2023, clocks jump 2:00->3:00) -
    # a genuine gap in the underlying reported data. Fill it by linear
    # interpolation between the surrounding hours rather than leaving a gap.
    if s.isna().any():
        s = s.interpolate(method="linear")

    lines = [f"{ts.strftime('%Y-%m-%d_%H:%M:%S')};{val}" for ts, val in s.items()]
    last_year = s.index[-1].year
    lines.append(f"{last_year + 1}-01-01_00:00:00;{pad_value}")
    lines.append(f"{last_year + 2}-01-01_00:00:00;{pad_value}")
    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")
    print(f"Saved {path} ({len(s)} real hourly rows + 2 placeholder rows)")


# ---- 1. Installed capacity per technology (one value for the whole year) ----
capacity = client.query_installed_generation_capacity("DE_LU", start=START, end=END)
print("Installed generation capacity, Germany 2023 (MW):")
print(capacity.T)
print()

# ---- 2. Hourly demand ----
load = client.query_load("DE_LU", start=START, end=END)
load_series = load.iloc[:, 0] if hasattr(load, "iloc") and load.ndim > 1 else load
save_as_amiris_timeseries(load_series, os.path.join(OUT_DIR, "load.csv"), pad_value=load_series.iloc[-1])

# ---- 3. Hourly generation per renewable technology, normalised to 0-1 ----
for filename, (psr_type, installed_mw) in RENEWABLE_PSR_TYPES.items():
    generation = client.query_generation("DE_LU", start=START, end=END, psr_type=psr_type)
    generation_series = generation.iloc[:, 0] if isinstance(generation, pd.DataFrame) else generation
    profile = (generation_series / installed_mw).clip(lower=0, upper=1).round(6)
    save_as_amiris_timeseries(profile, os.path.join(OUT_DIR, f"{filename}.csv"), pad_value=0.0)

print("\nDone.")
