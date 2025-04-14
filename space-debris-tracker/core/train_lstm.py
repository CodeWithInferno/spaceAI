from sgp4.api import Satrec, jday
from datetime import datetime, timedelta
import os
import pandas as pd
import numpy as np
import torch
from torch import nn
from torch.utils.data import DataLoader, Dataset
from sklearn.preprocessing import MinMaxScaler
from sklearn.model_selection import train_test_split
import joblib
import re
from collections import defaultdict

# === CONFIG ===
DATA_DIR = "satellite_data"
SEQUENCE_LENGTH = 10
PREDICT_HORIZON = 1
BATCH_SIZE = 64
EPOCHS = 50
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

    sequences = []
    targets = []

    for i in range(len(coords) - SEQUENCE_LENGTH - PREDICT_HORIZON):
        seq = coords[i:i+SEQUENCE_LENGTH]
        target = coords[i+SEQUENCE_LENGTH]
        sequences.append(seq)
        targets.append(target)

    return sequences, targets

# === Collect data from many satellites ===
all_sequences, all_targets = [], []
max_files = 500  # You can increase this if needed

csv_files = [f for f in os.listdir(DATA_DIR) if f.endswith(".csv")][:max_files]
for file in csv_files:
    try:
        file_path = os.path.join(DATA_DIR, file)
        sequences, targets = load_sequence_data(file_path)
        all_sequences.extend(sequences)
        all_targets.extend(targets)
    except:
        print(f"Skipping {file} due to error")

# === Train/test split ===
X_train, X_val, y_train, y_val = train_test_split(all_sequences, all_targets, test_size=0.1, random_state=42)

# === Scale globally ===
scaler = MinMaxScaler()
X_combined = np.concatenate(X_train, axis=0)
y_combined = np.array(y_train).reshape(-1, 3)
scaler.fit(np.vstack((X_combined, y_combined)))

X_train = [scaler.transform(seq) for seq in X_train]
y_train = [scaler.transform([target])[0] for target in y_train]
X_val = [scaler.transform(seq) for seq in X_val]
y_val = [scaler.transform([target])[0] for target in y_val]

# === Dataloaders ===
train_loader = DataLoader(SatelliteDataset(X_train, y_train), batch_size=BATCH_SIZE, shuffle=True)
val_loader = DataLoader(SatelliteDataset(X_val, y_val), batch_size=BATCH_SIZE)

# === Model ===
model = LSTMModel()
optimizer = torch.optim.Adam(model.parameters(), lr=LEARNING_RATE)
loss_fn = nn.MSELoss()

# === Training loop ===
for epoch in range(EPOCHS):
    model.train()
    train_loss = 0
    for batch_x, batch_y in train_loader:
        optimizer.zero_grad()
        output = model(batch_x)
        loss = loss_fn(output, batch_y)
        loss.backward()
        optimizer.step()
        train_loss += loss.item()

    model.eval()
    val_loss = 0
    with torch.no_grad():
        for val_x, val_y in val_loader:
            val_pred = model(val_x)
            val_loss += loss_fn(val_pred, val_y).item()

    print(f"Epoch {epoch+1}/{EPOCHS} | Train Loss: {train_loss:.6f} | Val Loss: {val_loss:.6f}")

# === Save model and scaler ===
torch.save(model.state_dict(), "lstm_model.pth")
joblib.dump(scaler, "scaler.save")
print("✅ Training complete. Model and scaler saved.")