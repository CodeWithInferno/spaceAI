import pandas as pd
import numpy as np

# === CONFIG ===
SATELLITE_PREDICTIONS = "predicted_positions.csv"
ROCKET_PATH = "rocket_path.csv"
COLLISION_RADIUS_KM = 10  # threshold for "too close"

# === Load data ===
sats = pd.read_csv(SATELLITE_PREDICTIONS)
rocket = pd.read_csv(ROCKET_PATH)

# === Use rocket position at t+1 (first entry)
rocket_xyz = rocket.iloc[1][["x_km", "y_km", "z_km"]].values.astype(float)

collisions = []

for _, row in sats.iterrows():
    sat_xyz = row[["x_km", "y_km", "z_km"]].values.astype(float)
    distance = np.linalg.norm(sat_xyz - rocket_xyz)

    if distance <= COLLISION_RADIUS_KM:
        collisions.append({
            "satellite": row["satellite"],
            "distance_km": distance
        })

# === Results ===
if not collisions:
    print("✅ No collisions detected. Safe launch window!")
else:
    print("⚠️ Potential Collisions Detected:")
    for c in collisions:
        print(f" - {c['satellite']}: {c['distance_km']:.2f} km")
