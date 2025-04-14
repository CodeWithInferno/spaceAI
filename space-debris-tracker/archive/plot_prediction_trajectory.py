import plotly.graph_objects as go
import numpy as np
import pandas as pd
import os
import torch
import joblib
from train_lstm import LSTMModel, SEQUENCE_LENGTH

# === Load satellite prediction ===
CSV_DIR = "satellite_data"
MODEL_PATH = "lstm_model.pth"
SCALER_PATH = "scaler.save"
PREDICT_STEPS = 1

csv_files = [f for f in os.listdir(CSV_DIR) if f.endswith(".csv")]
csv_path = os.path.join(CSV_DIR, csv_files[0])
df = pd.read_csv(csv_path)

# === Load model + scaler ===
model = LSTMModel()
model.load_state_dict(torch.load(MODEL_PATH, map_location=torch.device("cpu")))
model.eval()
scaler = joblib.load(SCALER_PATH)

coords = df[["x_km", "y_km", "z_km"]].values
coords_scaled = scaler.transform(coords)
input_seq = coords_scaled[-SEQUENCE_LENGTH:]

# === Predict one step forward ===
input_tensor = torch.tensor(input_seq, dtype=torch.float32).unsqueeze(0)
with torch.no_grad():
    pred_scaled = model(input_tensor).numpy()
pred_position = scaler.inverse_transform(pred_scaled)[0]

# === Create Earth sphere ===
theta = np.linspace(0, 2 * np.pi, 100)
phi = np.linspace(0, np.pi, 100)
theta, phi = np.meshgrid(theta, phi)
r = 6371
x = r * np.sin(phi) * np.cos(theta)
y = r * np.sin(phi) * np.sin(theta)
z = r * np.cos(phi)

# === Plot globe with satellite dot ===
fig = go.Figure()

# Earth surface
fig.add_trace(go.Surface(
    x=x, y=y, z=z,
    surfacecolor=np.ones_like(z),
    colorscale=[[0, "black"], [1, "blue"]],
    showscale=False,
    opacity=0.4
))

# Satellite position
fig.add_trace(go.Scatter3d(
    x=[pred_position[0]],
    y=[pred_position[1]],
    z=[pred_position[2]],
    mode="markers",
    marker=dict(size=6, color="red"),
    name="Predicted Satellite"
))

# Layout
fig.update_layout(
    title=f"🌍 Earth + Satellite: {csv_files[0]}",
    scene=dict(
        xaxis=dict(visible=False),
        yaxis=dict(visible=False),
        zaxis=dict(visible=False),
        aspectmode="data",
        bgcolor="black",
        camera=dict(eye=dict(x=1.6, y=1.6, z=1.1))
    ),
    margin=dict(l=0, r=0, t=50, b=0),
    paper_bgcolor='black',
    font=dict(color='white')
)

fig.show()
