from sgp4.api import Satrec, jday
from datetime import datetime, timedelta
import os
import pandas as pd
import re
from collections import defaultdict

# === CONFIG ===
TLE_FILE = "3le"  # Path to your TLE file
OUTPUT_FOLDER = "satellite_data"
SIMULATION_DURATION_HOURS = 24
TIME_STEP_SECONDS = 60

# === Ensure output folder exists ===
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

# === Helpers ===
def clean_filename(name):
    # Remove bad characters and replace spaces
    return re.sub(r'[<>:"/\\|?*]', '_', name.replace(" ", "_"))

# For counting duplicate filenames
name_counts = defaultdict(int)
tba_count = 1

# === Load TLEs ===
satellites = []
with open(TLE_FILE, "r") as f:
    lines = f.readlines()

for i in range(0, len(lines), 3):
    name = lines[i].strip().replace("0 ", "").strip().replace("/", "-")
    line1 = lines[i + 1].strip()
    line2 = lines[i + 2].strip()
    satellites.append({"name": name, "line1": line1, "line2": line2})

# === Simulation Time Window ===
start_time = datetime.utcnow()
end_time = start_time + timedelta(hours=SIMULATION_DURATION_HOURS)

# === Run Simulation ===
for idx, sat in enumerate(satellites):
    try:
        s = Satrec.twoline2rv(sat["line1"], sat["line2"])
    except Exception as e:
        print(f"❌ Skipping index {idx} due to bad TLE: {e}")
        continue

    times = []
    positions = []
    current_time = start_time

    while current_time <= end_time:
        jd, fr = jday(current_time.year, current_time.month, current_time.day,
                      current_time.hour, current_time.minute, current_time.second)
        e, r, v = s.sgp4(jd, fr)
        if e == 0:
            times.append(current_time.isoformat())
            positions.append(r)
        current_time += timedelta(seconds=TIME_STEP_SECONDS)

    if positions:
        df = pd.DataFrame(positions, columns=["x_km", "y_km", "z_km"])
        df.insert(0, "timestamp", times)

        # Generate filename
        name = sat["name"]
        if not name or "TBA" in name or "TO BE ASSIGNED" in name:
            base_name = f"TBA"
        else:
            base_name = clean_filename(name)

        name_counts[base_name] += 1
        file_name = f"{base_name}_{name_counts[base_name]:03d}.csv"

        file_path = os.path.join(OUTPUT_FOLDER, file_name)
        df.to_csv(file_path, index=False)
        print(f"✅ Saved: {file_path}")
