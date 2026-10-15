import streamlit as st
import pandas as pd
import time
import random
import plotly.express as px
from collections import deque

# =========================
# PAGE CONFIG (SOC STYLE)
# =========================
st.set_page_config(
    page_title="Edge AI Cybersecurity SOC",
    layout="wide",
    initial_sidebar_state="expanded"
)

# =========================
# DARK SOC UI THEME
# =========================
st.markdown("""
<style>
body {
    background-color: #0e1117;
    color: #ffffff;
}
</style>
""", unsafe_allow_html=True)

# =========================
# HEADER
# =========================
st.markdown("""
# 🧠 Edge AI Cybersecurity SOC
### Real-Time Intrusion Detection & Monitoring System
""")

# LIVE PULSE
st.markdown("""
<div style="display:flex;align-items:center;">
<span style="height:10px;width:10px;background-color:red;border-radius:50%;display:inline-block;animation:blink 1s infinite;"></span>
&nbsp; LIVE SYSTEM MONITORING
</div>

<style>
@keyframes blink {
  0% {opacity: 1;}
  50% {opacity: 0.2;}
  100% {opacity: 1;}
}
</style>
""", unsafe_allow_html=True)

# =========================
# SIDEBAR CONTROL PANEL
# =========================
st.sidebar.title("🛡 SOC Control Panel")

mode = st.sidebar.selectbox(
    "System Mode",
    ["Live Monitoring", "Attack Simulation"]
)

st.sidebar.markdown("---")
st.sidebar.metric("System Status", "ACTIVE 🟢")
st.sidebar.metric("Latency", "LOW ⚡")
st.sidebar.metric("Security Level", "EDGE PROTECTED 🛡")

# =========================
# SESSION STATE
# =========================
if "logs" not in st.session_state:
    st.session_state.logs = deque(maxlen=25)

if "attack_count" not in st.session_state:
    st.session_state.attack_count = 0

if "normal_count" not in st.session_state:
    st.session_state.normal_count = 0

# 🔥 NEW: PORT HISTORY
if "port_history" not in st.session_state:
    st.session_state.port_history = deque(maxlen=25)

# =========================
# SIMULATION ENGINE
# =========================
def generate_packet():
    attack_prob = 0.6 if mode == "Attack Simulation" else 0.3

    if random.random() < attack_prob:
        return {"type": "ATTACK", "port": random.choice([22, 80, 443])}
    else:
        return {"type": "NORMAL", "port": random.choice([22, 80, 443])}

def process_packet(pkt):

    if pkt["type"] == "ATTACK":
        st.session_state.attack_count += 1
        severity = "HIGH"
    else:
        st.session_state.normal_count += 1
        severity = "LOW"

    st.session_state.logs.appendleft({
        "Time": time.strftime("%H:%M:%S"),
        "Type": pkt["type"],
        "Port": pkt["port"],
        "Severity": severity
    })

    # 🔥 NEW: STORE PORT ACTIVITY
    st.session_state.port_history.append({
        "Time": time.strftime("%H:%M:%S"),
        "Port": pkt["port"]
    })

# =========================
# METRICS PANEL
# =========================
col1, col2, col3 = st.columns(3)

col1.metric("🚨 Total Attacks", st.session_state.attack_count)
col2.metric("✅ Normal Traffic", st.session_state.normal_count)
col3.metric("📊 Total Packets", st.session_state.attack_count + st.session_state.normal_count)

st.markdown("---")

# =========================
# START BUTTON
# =========================
start = st.button("🚀 Start SOC Monitoring")

if start:

    placeholder = st.empty()

    for i in range(40):

        pkt = generate_packet()
        process_packet(pkt)

        with placeholder.container():

            col1, col2 = st.columns(2)

            # =========================
            # ALERT TABLE
            # =========================
            with col1:
                st.subheader("🚨 Live Threat Alerts")

                df = pd.DataFrame(list(st.session_state.logs))

                def color_severity(val):
                    if val == "HIGH":
                        return "background-color:red;color:white"
                    return ""

                st.dataframe(
                    df.style.applymap(color_severity, subset=["Severity"]),
                    use_container_width=True
                )

            # =========================
            # PIE CHART
            # =========================
            with col2:
                st.subheader("📊 Traffic Distribution")

                fig = px.pie(
                    values=[st.session_state.attack_count, st.session_state.normal_count],
                    names=["Attack", "Normal"],
                    title="Network Traffic Split"
                )

                st.plotly_chart(fig, use_container_width=True)

            # =========================
            # 🔥 PORT ACTIVITY CHART (NEW)
            # =========================
            st.subheader("📡 Port Activity Monitor")

            port_df = pd.DataFrame(list(st.session_state.port_history))

            if not port_df.empty:
                fig2 = px.line(
                    port_df,
                    x="Time",
                    y="Port",
                    markers=True,
                    title="Real-Time Port Activity Trend"
                )

                st.plotly_chart(fig2, use_container_width=True)

        time.sleep(0.4)

# =========================
# DOWNLOAD LOGS
# =========================
st.markdown("---")

if st.button("📥 Download Logs"):
    df = pd.DataFrame(list(st.session_state.logs))
    df.to_csv("logs.csv", index=False)
    st.success("Logs downloaded successfully!")

st.caption("Edge AI SOC Dashboard | Streamlit Version 2.0")