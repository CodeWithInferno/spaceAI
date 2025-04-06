from sgp4.api import Satrec, jday
from datetime import datetime, timedelta
import os
import pandas as pd
import numpy as np
import torch
from torch import nn
from torch.utils.data import DataLoader, Dataset
from sklearn.preprocessing import MinMaxScaler
import joblib
import re
from collections import defaultdict

# === CONFIG ===
DATA_DIR = "satellite_data"
SEQUENCE_LENGTH = 10
PREDICT_HORIZON = 1
BATCH_SIZE = 64
EPOCHS = 10
LEARNING_RATE = 0.001

# === Dataset ===
class SatelliteDataset(Dataset):
    def __init__(self, sequences, targets):
        self.sequences = sequences
        self.targets = targets

    def __len__(self):
        return len(self.sequences)

    def __getitem__(self, idx):
        return torch.tensor(self.sequences[idx], dtype=torch.float32), torch.tensor(self.targets[idx], dtype=torch.float32)

# === Model ===
class LSTMModel(nn.Module):
    def __init__(self, input_size=3, hidden_size=64, num_layers=2, output_size=3):
        super().__init__()
        self.lstm = nn.LSTM(input_size, hidden_size, num_layers, batch_first=True)
        self.linear = nn.Linear(hidden_size, output_size)

    def forward(self, x):
        out, _ = self.lstm(x)
        out = self.linear(out[:, -1, :])
        return out

# === Load Data ===
def load_sequence_data(file_path):
    df = pd.read_csv(file_path)
    coords = df[["x_km", "y_km", "z_km"]].values

    scaler = MinMaxScaler()
    coords_scaled = scaler.fit_transform(coords)

    sequences = []
    targets = []

    for i in range(len(coords_scaled) - SEQUENCE_LENGTH - PREDICT_HORIZON):
        seq = coords_scaled[i:i+SEQUENCE_LENGTH]
        target = coords_scaled[i+SEQUENCE_LENGTH]
        sequences.append(seq)
        targets.append(target)

    return sequences, targets, scaler

# === Training ===
csv_files = [f for f in os.listdir(DATA_DIR) if f.endswith(".csv")]
file_path = os.path.join(DATA_DIR, csv_files[0])  # train on one satellite for now

sequences, targets, scaler = load_sequence_data(file_path)
dataset = SatelliteDataset(sequences, targets)
dataloader = DataLoader(dataset, batch_size=BATCH_SIZE, shuffle=True)

model = LSTMModel()
optimizer = torch.optim.Adam(model.parameters(), lr=LEARNING_RATE)
loss_fn = nn.MSELoss()

for epoch in range(EPOCHS):
    total_loss = 0
    for batch_x, batch_y in dataloader:
        optimizer.zero_grad()
        output = model(batch_x)
        loss = loss_fn(output, batch_y)
        loss.backward()
        optimizer.step()
        total_loss += loss.item()
    print(f"Epoch {epoch+1}/{EPOCHS} - Loss: {total_loss:.6f}")

# === Save Model ===
torch.save(model.state_dict(), "lstm_model.pth")
joblib.dump(scaler, "scaler.save")
print("✅ Training complete. Model and scaler saved.")
