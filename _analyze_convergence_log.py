import re

LOG_PATH = r"C:\Users\MuideenOA\.claude\projects\C--Users-MuideenOA-Desktop-PyTut-Amiris\18e58e4e-3937-44df-8c83-f2d3181925ef\tool-results\toolu_01Whiu4hJHhpFrLAMPrJRp6X.txt"

SHORTAGE_HOURS_RAW = """2029-01-01 17:00:00
2029-01-01 18:00:00
2029-01-01 19:00:00
2029-01-01 20:00:00
2029-01-01 21:00:00
2029-01-02 08:00:00
2029-01-02 14:00:00
2029-01-02 19:00:00
2029-01-02 20:00:00
2029-01-02 21:00:00
2029-01-09 17:00:00
2029-01-09 18:00:00
2029-01-09 19:00:00
2029-01-15 16:00:00
2029-01-15 17:00:00
2029-01-15 18:00:00
2029-01-15 19:00:00
2029-01-24 16:00:00
2029-01-24 17:00:00
2029-01-24 18:00:00
2029-01-24 19:00:00
2029-01-25 06:00:00
2029-01-25 07:00:00
2029-02-06 20:00:00
2029-02-06 21:00:00
2029-02-06 22:00:00
2029-02-06 23:00:00
2029-02-07 08:00:00
2029-02-07 09:00:00
2029-02-07 10:00:00
2029-02-07 11:00:00
2029-02-07 12:00:00
2029-02-07 13:00:00
2029-02-07 14:00:00
2029-02-07 15:00:00
2029-02-07 18:00:00
2029-02-18 20:00:00
2029-02-28 15:00:00
2029-02-28 16:00:00
2029-02-28 18:00:00
2029-10-23 07:00:00
2029-10-23 14:00:00
2029-10-23 15:00:00
2029-10-23 16:00:00
2029-10-23 17:00:00
2029-10-23 18:00:00
2029-11-09 16:00:00
2029-11-09 17:00:00
2029-11-09 18:00:00
2029-11-09 19:00:00
2029-11-30 14:00:00
2029-11-30 15:00:00
2029-11-30 16:00:00
2029-11-30 17:00:00
2029-11-30 18:00:00
2029-12-17 06:00:00
2029-12-17 07:00:00
2029-12-17 08:00:00
2029-12-17 15:00:00
2029-12-17 16:00:00
2029-12-17 17:00:00
2029-12-17 18:00:00
2029-12-17 19:00:00
2029-12-17 20:00:00
2029-12-18 16:00:00
2029-12-18 17:00:00
2029-12-18 19:00:00
2029-12-18 20:00:00
2029-12-19 14:00:00
2029-12-19 15:00:00
2029-12-19 16:00:00
2029-12-19 17:00:00
2029-12-19 18:00:00
2029-12-19 19:00:00
2029-12-19 20:00:00
2029-12-19 21:00:00""".splitlines()

# Build a lookup from "MM/DD)_HH:00:00" fragment (the log's date format) to the shortage set
targets = set()
for line in SHORTAGE_HOURS_RAW:
    date_part, time_part = line.split(" ")
    _, mm, dd = date_part.split("-")
    targets.add(f"({mm}/{dd})_{time_part}")

print(f"Looking for {len(targets)} real shortage-hour timestamps in the log...")

# Parse the log: group lines by hour fragment, keep the LAST line for each hour
by_hour_last_line = {}
pattern = re.compile(r"t=2029-\d+(\(\d\d/\d\d\)_\d\d:00:00) (STOPREASON=\S+|SHIFT_APPLIED)(.*)")
with open(LOG_PATH, encoding="utf-8", errors="replace") as f:
    for line in f:
        m = pattern.search(line)
        if not m:
            continue
        frag, kind, rest = m.groups()
        if frag in targets:
            by_hour_last_line[frag] = (kind, rest.strip())

print(f"\nFound log entries for {len(by_hour_last_line)} of {len(targets)} shortage hours\n")
print(f"{'Hour':<20} {'Final action':<28} Detail")
print("-" * 100)
reason_counts = {}
for frag in sorted(targets):
    if frag in by_hour_last_line:
        kind, rest = by_hour_last_line[frag]
        print(f"{frag:<20} {kind:<28} {rest[:75]}")
        reason_counts[kind] = reason_counts.get(kind, 0) + 1
    else:
        print(f"{frag:<20} {'NO exp=1/cheap=9001 activity':<28}")
        reason_counts["NO_ACTIVITY"] = reason_counts.get("NO_ACTIVITY", 0) + 1

print("\n" + "=" * 60)
print("SUMMARY: final reason DE stopped importing more from ROE")
print("=" * 60)
for reason, count in sorted(reason_counts.items(), key=lambda x: -x[1]):
    print(f"  {reason}: {count} of {len(targets)} shortage hours")
