"""Quick diagnostic: is ENTSO-E down generally right now, or is SE_4 specifically still
broken? Tests one already-proven-working border (DE<->AT, a single 2-day window) alongside
a fresh attempt at DE<->SE_4."""
import pandas as pd
from entsoe import EntsoePandasClient

TOKEN_FILE = r"C:\Users\MuideenOA\Desktop\PyTut\Amiris\Token.txt"
with open(TOKEN_FILE, encoding="utf-8") as f:
    lines = [l.strip() for l in f if l.strip()]
token = lines[lines.index("Entso Token") + 1]

client = EntsoePandasClient(api_key=token)
start = pd.Timestamp("2023-06-01", tz="UTC")
end = pd.Timestamp("2023-06-03", tz="UTC")

print("Testing DE->AT (known-good border, 2-day window)...")
try:
    result = client.query_crossborder_flows("DE_LU", "AT", start=start, end=end)
    print(f"  OK - {len(result)} rows")
except Exception as e:
    print(f"  FAILED: {e}")

print("\nTesting DE->SE_4 (2-day window)...")
try:
    result = client.query_crossborder_flows("DE_LU", "SE_4", start=start, end=end)
    print(f"  OK - {len(result)} rows")
except Exception as e:
    print(f"  FAILED: {e}")

print("\nTesting SE_4->DE (2-day window)...")
try:
    result = client.query_crossborder_flows("SE_4", "DE_LU", start=start, end=end)
    print(f"  OK - {len(result)} rows")
except Exception as e:
    print(f"  FAILED: {e}")
