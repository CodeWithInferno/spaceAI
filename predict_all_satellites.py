import os
import pandas as pd
import torch
import joblib
import time
from train_lstm import LSTMModel, SEQUENCE_LENGTH

# === CONFIG ===
DATA_DIR = "satellite_data"
MODEL_PATH = "lstm_model.pth"
SCALER_PATH = "scaler.save"
OUTPUT_FILE = "predicted_positions.csv"
MAX_FILES = None  # e.g. 100 for testing, or None for all

# === Load model and scaler
model = LSTMModel()
model.load_state_dict(torch.load(MODEL_PATH))
model.eval()

scaler = joblib.load(SCALER_PATH)

# === Collect predictions
predictions = []
start_time = time.time()

all_files = [f for f in os.listdir(DATA_DIR) if f.endswith(".csv")]
if MAX_FILES:
    all_files = all_files[:MAX_FILES]

for i, fname in enumerate(all_files):
    path = os.path.join(DATA_DIR, fname)

    try:
        df = pd.read_csv(path)
        if len(df) < SEQUENCE_LENGTH:
            print(f"⚠️ Skipping {fname} (too short)")
            continue

        coords = df[["x_km", "y_km", "z_km"]].values
        coords_scaled = scaler.transform(coords)
        input_seq = coords_scaled[-SEQUENCE_LENGTH:]
        input_tensor = torch.tensor(input_seq, dtype=torch.float32).unsqueeze(0)

        with torch.no_grad():
            pred_scaled = model(input_tensor).numpy()

        pred_position = scaler.inverse_transform(pred_scaled)[0]

        predictions.append({
            "satellite": fname.replace(".csv", ""),
            "x_km": pred_position[0],
            "y_km": pred_position[1],
            "z_km": pred_position[2]
        })

        if i % 10 == 0:
            print(f"✅ Processed {i}/{len(all_files)} satellites")

    except Exception as e:
        print(f"❌ Error processing {fname}: {e}")
        continue

# === Save output
out_df = pd.DataFrame(predictions)
out_df.to_csv(OUTPUT_FILE, index=False)
print(f"✅ Done. Saved {len(predictions)} predictions to {OUTPUT_FILE}")
print(f"⏱️ Total time: {time.time() - start_time:.2f} seconds")
