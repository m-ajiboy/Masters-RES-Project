"""Builds a PLACEHOLDER bidirectional transmission-capacity timeseries for the
Germany2027_MarketCoupling scenario, pending real NTC data from ENTSO-E (still down as of
this build - Phase 33's cron retry continues). Uses a flat 30,000 MW in both directions,
matching this project's own already-calibrated, real import ceiling (Phase 8) - a documented,
reasonable starting estimate, NOT real cross-border capacity data. To be replaced once
ENTSO-E recovers.
"""
import pandas as pd

OUT_DIR = r"C:\Users\MuideenOA\Desktop\PyTut\Amiris\examples\backtest\Germany2027_MarketCoupling\timeseries"
PLACEHOLDER_MW = 30000.0

idx = pd.date_range("2027-01-01", periods=8760, freq="h")
lines = [f"{ts.strftime('%Y-%m-%d_%H:%M:%S')};{PLACEHOLDER_MW:.1f}" for ts in idx]
content = "\n".join(lines) + "\n"

for fname in ["transfer_DEtoROE_PLACEHOLDER.csv", "transfer_ROEtoDE_PLACEHOLDER.csv"]:
    with open(rf"{OUT_DIR}\{fname}", "w", encoding="utf-8") as f:
        f.write(content)
    print(f"Saved {fname} (flat {PLACEHOLDER_MW:.0f} MW, PLACEHOLDER pending real NTC)")
