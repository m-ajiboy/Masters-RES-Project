"""One-off diagnostic: is real 2024 annual data actually published yet for the sources this
project uses for the Rest-of-Europe market-coupling zone (Eurostat demand/capacity, ENTSO-E
cross-border flows)? Checked live before committing to any 2024 rebuild - do not assume."""
import requests
import pandas as pd
from entsoe import EntsoePandasClient

print("=" * 70)
print("EUROSTAT nrg_cb_e (demand) - testing 2024 for DE and FR")
print("=" * 70)
for country in ["DE", "FR"]:
    url = "https://ec.europa.eu/eurostat/api/dissemination/statistics/1.0/data/nrg_cb_e"
    params = {"format": "JSON", "lang": "EN", "freq": "A", "geo": country, "unit": "GWH",
              "nrg_bal": "FC", "time": "2024"}
    r = requests.get(url, params=params, timeout=30)
    print(f"{country}: status={r.status_code}", end=" ")
    if r.status_code == 200:
        d = r.json()
        vals = list(d.get("value", {}).values())
        print(f"-> {vals[0] if vals else 'NO VALUE (empty)'}")
    else:
        print()

print()
print("=" * 70)
print("EUROSTAT nrg_inf_epc (capacity) - testing 2024 for DE wind onshore")
print("=" * 70)
url = "https://ec.europa.eu/eurostat/api/dissemination/statistics/1.0/data/nrg_inf_epc"
params = {"format": "JSON", "lang": "EN", "freq": "A", "geo": "DE", "unit": "MW",
          "plant_tec": "CAP_NET_ELC", "operator": "TOTAL", "siec": "RA310", "time": "2024"}
r = requests.get(url, params=params, timeout=30)
print(f"status={r.status_code}", end=" ")
if r.status_code == 200:
    d = r.json()
    vals = list(d.get("value", {}).values())
    print(f"-> {vals[0] if vals else 'NO VALUE (empty)'}")

print()
print("=" * 70)
print("ENTSO-E - testing 2024 crossborder flow DE->AT (1-month window)")
print("=" * 70)
TOKEN_FILE = r"C:\Users\MuideenOA\Desktop\PyTut\Amiris\Token.txt"
with open(TOKEN_FILE, encoding="utf-8") as f:
    lines = [l.strip() for l in f if l.strip()]
token = lines[lines.index("Entso Token") + 1]
client = EntsoePandasClient(api_key=token)
start = pd.Timestamp("2024-06-01", tz="UTC")
end = pd.Timestamp("2024-07-01", tz="UTC")
try:
    result = client.query_crossborder_flows("DE_LU", "AT", start=start, end=end)
    print(f"  OK - {len(result)} rows, {result.index.min()} to {result.index.max()}")
except Exception as e:
    print(f"  FAILED: {e}")

print()
print("Testing full 2024 year availability (Dec 2024 specifically, to confirm year-end published)...")
start = pd.Timestamp("2024-12-01", tz="UTC")
end = pd.Timestamp("2025-01-01", tz="UTC")
try:
    result = client.query_crossborder_flows("DE_LU", "AT", start=start, end=end)
    print(f"  OK - {len(result)} rows, {result.index.min()} to {result.index.max()}")
except Exception as e:
    print(f"  FAILED: {e}")
