"""2024-base variant of build_restofeurope_demand_shape.py. Same borrow-Germany's-own-shape-
rescale-to-real-total technique, now targeting the real 2024 Eurostat annual total
(1,158,143.0 GWh, 9 countries) instead of 2023's 1,139,270.364 GWh."""
import pandas as pd

GERMANY_SHAPE = r"C:\Users\MuideenOA\Desktop\PyTut\Amiris\examples\backtest\Germany2027_Feb29DropFix\timeseries\load_2027_feb29fix.csv"
OUT_DIR = r"C:\Users\MuideenOA\Desktop\PyTut\Amiris\examples\backtest\RestOfEurope2024"
OUT_FILE = rf"{OUT_DIR}\load_restofeurope_2027_shapeFromDE.csv"

REST_OF_EUROPE_TOTAL_MWH = 1_158_143.0 * 1000  # GWh -> MWh, real Eurostat 2024 total

df = pd.read_csv(GERMANY_SHAPE, sep=";", header=None, names=["ts", "mwh"])
print(f"Germany 2027 shape: {len(df)} hours, annual total = {df['mwh'].sum():,.0f} MWh")

shape = df["mwh"] / df["mwh"].sum()
rescaled = shape * REST_OF_EUROPE_TOTAL_MWH

out = pd.DataFrame({"ts": df["ts"], "mwh": rescaled})
out.to_csv(OUT_FILE, sep=";", header=False, index=False, float_format="%.4f")

print(f"\nRest-of-Europe rescaled shape saved: {OUT_FILE}")
print(f"  New annual total: {out['mwh'].sum():,.0f} MWh (target was {REST_OF_EUROPE_TOTAL_MWH:,.0f} MWh)")
