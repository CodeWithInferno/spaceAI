from flask import Flask, jsonify
import pandas as pd
import threading
import time
from flask_cors import CORS

app = Flask(__name__)        # 🟢 define app first
CORS(app)                    # ✅ then apply CORS

CSV_FILE = "predicted_positions.csv"
UPDATE_INTERVAL = 2  # seconds

df = pd.read_csv(CSV_FILE)
index = {"step": 0}

def update_index():
    while True:
        index["step"] = (index["step"] + 1) % len(df)
        time.sleep(UPDATE_INTERVAL)

@app.route("/data")
def get_position():
    row = df.iloc[index["step"]]
    return jsonify({
        "x": row["x_km"],
        "y": row["y_km"],
        "z": row["z_km"],
        "step": index["step"]
    })

if __name__ == "__main__":
    threading.Thread(target=update_index, daemon=True).start()
    app.run(debug=True)
