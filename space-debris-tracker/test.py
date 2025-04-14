import os
import pandas as pd
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

# Load up to 10 satellite trajectory files
DATA_DIR = "/Users/pratham/Programming/spaceAI/space-debris-tracker/satellite_data"
csv_files = [f for f in os.listdir(DATA_DIR) if f.endswith(".csv")][:10]

# Create a 3D plot
fig = plt.figure(figsize=(12, 10))
ax = fig.add_subplot(111, projection='3d')

# Distinct colors for each satellite
colors = plt.cm.get_cmap('tab10', len(csv_files))

for idx, file in enumerate(csv_files):
    path = os.path.join(DATA_DIR, file)
    df = pd.read_csv(path)
    ax.plot(df["x_km"], df["y_km"], df["z_km"], label=file.replace(".csv", ""), color=colors(idx))

ax.set_title("Orbits of 10 Satellites")
ax.set_xlabel("X (km)")
ax.set_ylabel("Y (km)")
ax.set_zlabel("Z (km)")
ax.legend()

# Save the figure
output_path = "/Users/pratham/Programming/spaceAI/space-debris-trackersatellite_orbits_10.png"
plt.savefig(output_path)
plt.close()

output_path
