import pandas as pd
import numpy as np
from datetime import datetime, timedelta

# === CONFIG ===
DURATION_MINUTES = 10           # simulate 10 mins
TIME_STEP_SECONDS = 60          # every 1 minute
OUTPUT_FILE = "rocket_path.csv"

# === Rocket Starting Position (example low Earth orbit entry vector) ===
pos = np.array([6371 + 150, 0, 0])     # 150 km above Earth's surface
vel = np.array([0, 6.9, 1.2])          # sample orbital insertion velocity in km/s

positions = []
timestamps = []

now = datetime.utcnow()
for t in range(0, DURATION_MINUTES * 60, TIME_STEP_SECONDS):
    time = now + timedelta(seconds=t)
    new_pos = pos + vel * (t)
    positions.append(new_pos)
    timestamps.append(time.isoformat())

df = pd.DataFrame(positions, columns=["x_km", "y_km", "z_km"])
df.insert(0, "timestamp", timestamps)
df.to_csv(OUTPUT_FILE, index=False)

print(f"✅ Rocket trajectory saved to {OUTPUT_FILE}")
