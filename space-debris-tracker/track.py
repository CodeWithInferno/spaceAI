from sgp4.api import Satrec, jday
from datetime import datetime

tle_file = "3le"  # Path to your file

satellites = []

with open(tle_file, "r") as f:
    lines = f.readlines()

# Parse in chunks of 3 lines
for i in range(0, len(lines), 3):
    name = lines[i].strip().replace("0 ", "")  # Remove the '0 ' prefix
    line1 = lines[i + 1].strip()
    line2 = lines[i + 2].strip()

    satellites.append({"name": name, "line1": line1, "line2": line2})

# Get current time
now = datetime.utcnow()
jd, fr = jday(now.year, now.month, now.day, now.hour, now.minute, now.second)

# Track and print positions
for sat in satellites:
    s = Satrec.twoline2rv(sat["line1"], sat["line2"])
    e, r, v = s.sgp4(jd, fr)

    if e == 0:
        print(f"{sat['name']}: x={r[0]:.2f}, y={r[1]:.2f}, z={r[2]:.2f}")
    else:
        print(f"{sat['name']}: error code {e}")
