from sgp4.api import Satrec, jday
from datetime import datetime
import plotly.graph_objects as go
import numpy as np

# === Load TLEs ===
tle_path = "3le"
satellites = []

with open(tle_path, "r") as f:
    lines = f.readlines()

for i in range(0, min(len(lines), 3000), 3):  # limit to ~1000 satellites
    name = lines[i].strip().replace("0 ", "")
    line1 = lines[i+1].strip()
    line2 = lines[i+2].strip()
    satellites.append((name, line1, line2))

# === Get current satellite positions ===
positions = []
now = datetime.utcnow()
jd, fr = jday(now.year, now.month, now.day, now.hour, now.minute, now.second)

for name, l1, l2 in satellites:
    s = Satrec.twoline2rv(l1, l2)
    e, r, v = s.sgp4(jd, fr)
    if e == 0:
        x, y, z = r
        distance = np.linalg.norm(r)
        positions.append({
            "name": name,
            "x": x,
            "y": y,
            "z": z,
            "distance": distance
        })

# === Prepare plot arrays ===
x = [p["x"] for p in positions]
y = [p["y"] for p in positions]
z = [p["z"] for p in positions]
color = [p["distance"] for p in positions]  # coloring by distance
hover = [f"{p['name']}<br>Distance: {p['distance']:.0f} km" for p in positions]

fig = go.Figure()

# Plot satellites as colored dots
fig.add_trace(go.Scatter3d(
    x=x, y=y, z=z,
    mode='markers',
    marker=dict(
        size=2.5,
        color=color,
        colorscale='Viridis',
        colorbar=dict(title='Distance (km)'),
        opacity=0.9
    ),
    hovertext=hover,
    hoverinfo="text",
    name='Satellites'
))

# Plot Earth
u, v = np.mgrid[0:2*np.pi:50j, 0:np.pi:25j]
earth_x = 6371 * np.cos(u) * np.sin(v)
earth_y = 6371 * np.sin(u) * np.sin(v)
earth_z = 6371 * np.cos(v)

fig.add_trace(go.Surface(
    x=earth_x, y=earth_y, z=earth_z,
    colorscale='Blues',
    opacity=0.6,
    showscale=False,
    name='Earth'
))

# Layout polish
fig.update_layout(
    title="🛰️ Satellite Orbit Visualization (Live Snapshot)",
    scene=dict(
        xaxis_title='X (km)',
        yaxis_title='Y (km)',
        zaxis_title='Z (km)',
        aspectmode='data'
    ),
    margin=dict(l=0, r=0, b=0, t=40),
    height=800
)

fig.show()
