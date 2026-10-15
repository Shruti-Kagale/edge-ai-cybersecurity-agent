import pandas as pd
import joblib

# =========================
# LOAD MODEL + COLUMNS
# =========================
model = joblib.load("models/model.pkl")
columns = joblib.load("models/columns.pkl")

print("Model Loaded Successfully!")

# =========================
# SAMPLE NETWORK TRAFFIC
# =========================
sample_data = {
    "Destination Port": 80,
    "Flow Duration": 50000,
    "Total Fwd Packets": 10,
    "Total Backward Packets": 5,
}

# =========================
# CONVERT TO DATAFRAME
# =========================
df = pd.DataFrame([sample_data])

# MATCH TRAINING COLUMNS
df = df.reindex(columns=columns, fill_value=0)

# =========================
# PREDICT
# =========================
prediction = model.predict(df)[0]

# =========================
# RESULT
# =========================
if prediction == 1:
    print("⚠ ALERT: DDoS Attack Detected!")
else:
    print("✅ Normal Traffic")