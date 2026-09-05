"""Phase 39: tests whether scaling the DE<->ROE transmission capacity by DE's own real
demand growth (the exact mechanism verified in Phase 38 - transmission capacity as a share
of DE's peak demand shrinks every year the link is left frozen) recovers 2027-level
shortage-hour counts for 2028 and 2029. Scales ONLY the transmission link, by DE's own real
peak-demand growth ratio - the narrowest, most directly-motivated single-variable test of
the verified hypothesis, keeping ROE's own demand/capacity frozen (no real data exists to
justify scaling ROE's economy itself, only DE's growth is real/sourced from Brainpool).
"""
import pandas as pd

ROOT = r"C:\Users\MuideenOA\Desktop\PyTut\Amiris\examples\backtest"

DE_PEAK_2027 = 99261.0
DE_PEAK_2028 = 103789.0
DE_PEAK_2029 = 108596.0

BASE_DE_TO_ROE = 21593.0
BASE_ROE_TO_DE = 22012.0

for year, de_peak in [(2028, DE_PEAK_2028), (2029, DE_PEAK_2029)]:
    scale = de_peak / DE_PEAK_2027
    new_de_to_roe = BASE_DE_TO_ROE * scale
    new_roe_to_de = BASE_ROE_TO_DE * scale
    print(f"{year}: DE peak growth scale={scale:.5f}, "
          f"DE->ROE {BASE_DE_TO_ROE:,.0f} -> {new_de_to_roe:,.1f} MW, "
          f"ROE->DE {BASE_ROE_TO_DE:,.0f} -> {new_roe_to_de:,.1f} MW")

    out_dir = rf"{ROOT}\Germany{year}_MarketCoupling_ROEFlex_ScaledTransmission\timeseries"
    import os
    os.makedirs(out_dir, exist_ok=True)

    # load the year's own real hour index from the existing build's transmission file
    ref = pd.read_csv(rf"{ROOT}\Germany{year}_MarketCoupling_ROEFlex\timeseries\transfer_DEtoROE_realflow_{year}.csv",
                       sep=";", header=None, names=["ts", "val"])
    for value, fname in [(new_de_to_roe, f"transfer_DEtoROE_scaled_{year}.csv"),
                          (new_roe_to_de, f"transfer_ROEtoDE_scaled_{year}.csv")]:
        lines = [f"{ts};{value:.1f}" for ts in ref["ts"]]
        with open(rf"{out_dir}\{fname}", "w", encoding="utf-8") as f:
            f.write("\n".join(lines) + "\n")
        print(f"  saved {fname}")
