import re
import glob
from collections import defaultdict

files = glob.glob(r"C:\Users\MuideenOA\Desktop\PyTut\Amiris\examples\backtest\Germany2027_MarketCoupling_AllZones\agents\*.yaml")
id_locations = defaultdict(list)
for path in files:
    with open(path, encoding="utf-8") as f:
        for i, line in enumerate(f, 1):
            m = re.match(r"\s*Id:\s*(\d+)\s*$", line)
            if m:
                id_locations[int(m.group(1))].append((path.split("\\")[-1], i))

dupes = {k: v for k, v in id_locations.items() if len(v) > 1}
if dupes:
    print(f"FOUND {len(dupes)} DUPLICATE IDs:")
    for id_, locs in sorted(dupes.items()):
        print(f"  Id {id_}: {locs}")
else:
    print(f"No collisions - {len(id_locations)} unique agent IDs across {len(files)} files.")
