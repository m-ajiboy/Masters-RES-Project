import re

files = {
    "GasMarkupTest": ("Germany2027_MarketCoupling_ROEFlex_GasMarkupTest",
                       "Natural gas ConventionalTrader minMarkup/maxMarkup widened from -10/10 to -25/25"),
    "CoalMarkupTest": ("Germany2027_MarketCoupling_ROEFlex_CoalMarkupTest",
                        "Hard coal ConventionalTrader minMarkup/maxMarkup widened from -15/5 to -30/10"),
    "OilMarkupTest": ("Germany2027_MarketCoupling_ROEFlex_OilMarkupTest",
                       "Oil ConventionalTrader minMarkup/maxMarkup given a real non-zero band, from 0/0 to -10/15"),
}
root = r"C:\Users\MuideenOA\Desktop\PyTut\Amiris\examples\backtest"
for key, (folder, change) in files.items():
    path = rf"{root}\{folder}\scenario.yaml"
    with open(path, encoding="utf-8") as f:
        content = f.read()
    new_meta = (
        f'  runId: "{folder}"\n'
        f'  description: "AMIRIS scenario for German day-ahead electricity market in 2027 - an EXPLORATORY SENSITIVITY TEST on top of the standing-best Germany2027_MarketCoupling_ROEFlex (Phase 37), changing exactly ONE thing: {change}. Same real per-fuel markup-band sweep methodology as Phase 31 (which tested lignite, found a genuine working mechanism but no meaningful excl-shortage correlation improvement, not adopted). Explicitly exploratory - not adopted. Germany2027_MarketCoupling_ROEFlex (Phase 37, original markup band) is kept fully unmodified as the comparison baseline."'
    )
    content = re.sub(r"  runId:.*\n  description:.*", new_meta, content, count=1)
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"Updated {folder}")
