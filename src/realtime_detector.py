import pandas as pd
import joblib
import time
from collections import deque
import threading

# =========================
# LOAD MODEL
# =========================
model = joblib.load("models/model.pkl")
columns = joblib.load("models/columns.pkl")

print("🚀 AI IDS STARTED (STABLE VERSION)\n")

packet_buffer = deque(maxlen=100)
WINDOW_TIME = 3
last_time = time.time()

# =========================
# SAFE LOGGING (NO UNICODE ERROR)
# =========================
def log_event(msg):
    try:
        with open("logs.txt", "a", encoding="utf-8") as f:
            f.write(msg + "\n")
    except:
        pass  # never crash IDS

# =========================
# FEATURE ENGINEERING
# =========================
def build_features(buffer):

    features = {col: 0 for col in columns}

    syn_count = 0
    attack_signal = 0
    ports = []

    for pkt in buffer:
        ports.append(pkt["port"])

        if pkt["flags"] == "S":
            syn_count += 1

        if pkt.get("burst", 0) == 1:
            attack_signal += 1

    features["Total Fwd Packets"] = len(buffer)
    features["Total Backward Packets"] = len(buffer) // 2
    features["Flow Duration"] = WINDOW_TIME * 1000
    features["SYN_Flag_Count"] = syn_count

    if ports:
        features["Destination Port"] = max(set(ports), key=ports.count)

    return pd.DataFrame([features])[columns]

# =========================
# ANALYZE
# =========================
def analyze():

    if len(packet_buffer) < 5:
        return

    df = build_features(packet_buffer)
    pred = model.predict(df)[0]

    syn_ratio = sum(1 for p in packet_buffer if p["flags"] == "S") / len(packet_buffer)

    attack_signal = sum(p.get("burst", 0) for p in packet_buffer)

    # =========================
    # DETECTION LOGIC
    # =========================
    if pred == 1 or syn_ratio > 0.5 or attack_signal > 5:

        if syn_ratio > 0.7:
            severity = "HIGH"
        elif syn_ratio > 0.4:
            severity = "MEDIUM"
        else:
            severity = "LOW"

        msg = f"ATTACK DETECTED | Severity: {severity}"
        print("🚨", msg)
        log_event(msg)

    else:
        msg = "NORMAL TRAFFIC"
        print("✅", msg)
        log_event(msg)

    packet_buffer.clear()

# =========================
# PROCESS PACKET
# =========================
def process(packet):
    packet_buffer.append(packet)

# =========================
# MONITOR THREAD
# =========================
def monitor():
    global last_time

    while True:
        time.sleep(1)

        try:
            if time.time() - last_time >= WINDOW_TIME:
                analyze()
                last_time = time.time()
        except:
            pass  # prevent crash

# start thread safely
threading.Thread(target=monitor, daemon=True).start()

# =========================
# IMPORT SIMULATOR
# =========================
from attack_simulator import start_simulation

if __name__ == "__main__":
    start_simulation(process)