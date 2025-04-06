import torch
import joblib
import pandas as pd
from train_lstm import LSTMModel, SEQUENCE_LENGTH  # reuse the model definition

# === CONFIG ===
MODEL_PATH = "lstm_model.pth"
SCALER_PATH = "scaler.save"
CSV_FILE = "satellite_data/FENGYUN_1C_DEB_837.csv"  # <- replace with the file you trained on

# Load CSV
df = pd.read_csv(CSV_FILE)
coords = df[["x_km", "y_km", "z_km"]].values

# Load scaler and scale data
scaler = joblib.load(SCALER_PATH)
coords_scaled = scaler.transform(coords)

# Prepare input sequence
input_seq = coords_scaled[-SEQUENCE_LENGTH:]
input_tensor = torch.tensor(input_seq, dtype=torch.float32).unsqueeze(0)

# Load model
model = LSTMModel()
model.load_state_dict(torch.load(MODEL_PATH))
model.eval()

# Predict
with torch.no_grad():
    prediction_scaled = model(input_tensor).numpy()

predicted_coords = scaler.inverse_transform(prediction_scaled)[0]

# Output
print("📍 Predicted Next Satellite Position:")
print(f"x = {predicted_coords[0]:.2f} km")
print(f"y = {predicted_coords[1]:.2f} km")
print(f"z = {predicted_coords[2]:.2f} km")
