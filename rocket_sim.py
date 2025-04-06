import numpy as np
from sgp4.api import Satrec, jday
from datetime import datetime, timedelta
import pandas as pd

# === CONFIG ===
TLE_FILE = "3le"  # Replace with your TLE file path if needed
COLLISION_DISTANCE_KM = 10  # Threshold distance for collision
ROCKET_LAUNCH_TIME = datetime.utcnow()  # Launch time

# === STEP 1: Load TLEs ===
satellites = []
with open(TLE_FILE, "r") as f:
    lines = f.readlines()

for i in range(0, len(lines), 3):
    name = lines[i].strip().replace("0 ", "")
    line1 = lines[i + 1].strip()
    line2 = lines[i + 2].strip()
    satellites.append({"name": name, "line1": line1, "line2": line2})

# === STEP 2: Define Rocket Path (simple upward arc for 10 minutes) ===
rocket_path = []
for t in range(0, 601, 30):  # every 30 seconds, for 10 minutes
    x = t * 0.5
    y = t * 0.3
    z = 6371 + t * 2  # Earth radius is ~6371 km
    rocket_path.append({"t": t, "pos": (x, y, z)})

# === STEP 3: Collision Detection ===
collisions = []

for rocket_point in rocket_path:
    time_offset = timedelta(seconds=rocket_point["t"])
    current_time = ROCKET_LAUNCH_TIME + time_offset
    jd, fr = jday(current_time.year, current_time.month, current_time.day,
                  current_time.hour, current_time.minute, current_time.second)

    for sat in satellites:
        s = Satrec.twoline2rv(sat["line1"], sat["line2"])
        e, r, v = s.sgp4(jd, fr)
        if e == 0:
            rocket_pos = np.array(rocket_point["pos"])
            sat_pos = np.array(r)
            distance = np.linalg.norm(rocket_pos - sat_pos)
            if distance < COLLISION_DISTANCE_KM:
                collisions.append({
                    "Time (UTC)": current_time,
                    "Satellite": sat["name"],
                    "Distance (km)": round(distance, 3),
                    "Rocket Pos": rocket_point["pos"],
                    "Satellite Pos": tuple(round(coord, 2) for coord in r)
                })

# === STEP 4: Output ===
if collisions:
    df = pd.DataFrame(collisions)
    print("🚨 Potential Collisions Detected:")
    print(df)
    df.to_csv("potential_collisions.csv", index=False)
else:
    print("✅ No collisions detected. Safe launch window!")
