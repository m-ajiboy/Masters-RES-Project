import re
import datetime

LOG_PATH = r"C:\Users\MuideenOA\maven-tools\diag_run2\diag_2029_result\logs\app.log"

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

targets = set()
for line in SHORTAGE_HOURS_RAW:
    dt = datetime.datetime.strptime(line, "%Y-%m-%d %H:%M:%S")
    doy = dt.timetuple().tm_yday
    frag = f"2029-{doy:03d}" + "(" + f"_{dt.hour:02d}:00:00"
    # store as (doy_str, hh_str) pair instead, more robust than string frag matching
    targets.add((f"{doy:03d}", f"{dt.hour:02d}:00:00"))

print(f"Looking for {len(targets)} real shortage-hour timestamps (by day-of-year) in the log...")

by_hour_last_line = {}
pattern = re.compile(r"t=2029-(\d{3})\([^)]*\)_(\d\d:00:00) (STOPREASON=\S+|SHIFT_APPLIED)(.*exp=1 cheap=9001.*)")
with open(LOG_PATH, encoding="utf-8", errors="replace") as f:
    for line in f:
        m = pattern.search(line)
        if not m:
            continue
        doy, hh, kind, rest = m.groups()
        key = (doy, hh)
        if key in targets:
            by_hour_last_line[key] = (kind, rest.strip())

print(f"\nFound log entries for {len(by_hour_last_line)} of {len(targets)} shortage hours\n")
print(f"{'DOY':<6}{'Hour':<10} {'Final action':<30} Detail")
print("-" * 110)
reason_counts = {}
for doy, hh in sorted(targets):
    key = (doy, hh)
    if key in by_hour_last_line:
        kind, rest = by_hour_last_line[key]
        print(f"{doy:<6}{hh:<10} {kind:<30} {rest[:70]}")
        reason_counts[kind] = reason_counts.get(kind, 0) + 1
    else:
        print(f"{doy:<6}{hh:<10} {'NO exp=1/cheap=9001 activity':<30}")
        reason_counts["NO_ACTIVITY"] = reason_counts.get("NO_ACTIVITY", 0) + 1

print("\n" + "=" * 60)
print("SUMMARY: final reason DE stopped importing more from ROE")
print("=" * 60)
for reason, count in sorted(reason_counts.items(), key=lambda x: -x[1]):
    print(f"  {reason}: {count} of {len(targets)} shortage hours")
