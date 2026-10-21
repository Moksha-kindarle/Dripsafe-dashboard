import streamlit as st
import random
from datetime import datetime, timedelta
import pandas as pd

st.set_page_config(
    page_title="DripSafe | Patient Monitor",
    page_icon="💧",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Dark, clinical dashboard styling inspired by the existing DripSafe HTML demo.
st.markdown("""
<style>
:root { color-scheme: dark; }
.stApp { background: #0b1220; color: #e8eef8; }
[data-testid="stSidebar"] { background: #101a2b; border-right: 1px solid #24334b; }
.block-container { padding-top: 1.5rem; padding-bottom: 2rem; max-width: 1500px; }
h1, h2, h3 { color: #f4f7fb; }
.small-muted { color: #9aaac1; font-size: 0.9rem; }
.metric-card {
    background: linear-gradient(145deg, #152238, #101a2b);
    border: 1px solid #263750; border-radius: 16px; padding: 18px 20px;
}
.metric-label { color: #9aacc5; font-size: 0.9rem; margin-bottom: 8px; }
.metric-value { color: #f5f8ff; font-size: 2rem; font-weight: 700; line-height: 1.1; }
.metric-foot { color: #9aacc5; font-size: 0.82rem; margin-top: 8px; }
.status-pill {
    display: inline-block; border-radius: 999px; padding: 6px 12px;
    font-size: 0.85rem; font-weight: 700;
}
</style>
""", unsafe_allow_html=True)

if "fluid" not in st.session_state:
    st.session_state.fluid = 76
if "drops" not in st.session_state:
    st.session_state.drops = 3
if "events" not in st.session_state:
    st.session_state.events = [
        {"time": (datetime.now() - timedelta(minutes=8)).strftime("%H:%M:%S"), "event": "Monitoring session started", "kind": "INFO"},
        {"time": (datetime.now() - timedelta(minutes=5)).strftime("%H:%M:%S"), "event": "IR sensor signal received", "kind": "DROP"},
        {"time": (datetime.now() - timedelta(minutes=2)).strftime("%H:%M:%S"), "event": "Fluid level checked", "kind": "INFO"},
    ]
if "history" not in st.session_state:
    st.session_state.history = [76, 75, 76, 74, 73, 75, 76]

def add_event(message, kind="INFO"):
    st.session_state.events.insert(
        0, {"time": datetime.now().strftime("%H:%M:%S"), "event": message, "kind": kind}
    )
    st.session_state.events = st.session_state.events[:12]

with st.sidebar:
    st.markdown("## 💧 DripSafe")
    st.caption("SMART INFUSION MONITOR")
    st.divider()
    st.markdown("### Simulation controls")
    st.caption("These controls simulate readings; they are not connected to the ESP32 yet.")
    new_fluid = st.slider("Fluid level (%)", 0, 100, int(st.session_state.fluid), 1)
    if new_fluid != st.session_state.fluid:
        st.session_state.fluid = new_fluid
        st.session_state.history.append(new_fluid)
        st.session_state.history = st.session_state.history[-20:]
        add_event(f"Fluid level adjusted to {new_fluid}%", "LEVEL")
    if st.button("＋ Simulate one IR drop", use_container_width=True):
        st.session_state.drops += 1
        add_event("IR sensor event simulated — drop count +1", "DROP")
        st.rerun()
    if st.button("↻ Reset demo values", use_container_width=True):
        st.session_state.fluid = 76
        st.session_state.drops = 3
        st.session_state.history = [76, 75, 76, 74, 73, 75, 76]
        st.session_state.events = [
            {"time": datetime.now().strftime("%H:%M:%S"), "event": "Demo values reset", "kind": "INFO"}
        ]
        st.rerun()
    st.divider()
    st.markdown("**Connection**")
    st.markdown('<span class="status-pill" style="background:#3b2c16;color:#ffcf70">● DEMO MODE</span>', unsafe_allow_html=True)
    st.caption("Live hardware connection: not configured")

fluid = int(st.session_state.fluid)
drops = int(st.session_state.drops)
low_fluid = fluid <= 20
status = "LOW FLUID ALERT" if low_fluid else "Normal"
status_color = "#ff6b6b" if low_fluid else "#54d6a0"

header_left, header_right = st.columns([3, 1])
with header_left:
    st.markdown("# DripSafe Monitor")
    st.markdown('<p class="small-muted">Infusion monitoring workspace · Patient safety overview</p>', unsafe_allow_html=True)
with header_right:
    st.markdown(f'<div style="text-align:right;padding-top:12px"><span class="status-pill" style="background:{"#3c2027" if low_fluid else "#17382f"};color:{status_color}">● {status}</span><div class="small-muted" style="margin-top:8px">Updated {datetime.now().strftime("%H:%M:%S")}</div></div>', unsafe_allow_html=True)

st.divider()

m1, m2, m3, m4 = st.columns(4)
with m1:
    st.markdown(f'<div class="metric-card"><div class="metric-label">Fluid remaining</div><div class="metric-value">{fluid}%</div><div class="metric-foot">Simulated sensor value</div></div>', unsafe_allow_html=True)
with m2:
    st.markdown(f'<div class="metric-card"><div class="metric-label">Drop count</div><div class="metric-value">{drops}</div><div class="metric-foot">IR event counter</div></div>', unsafe_allow_html=True)
with m3:
    st.markdown(f'<div class="metric-card"><div class="metric-label">System status</div><div class="metric-value" style="font-size:1.55rem;color:{status_color}">{("ALERT" if low_fluid else "NORMAL")}</div><div class="metric-foot">Threshold: 20% fluid</div></div>', unsafe_allow_html=True)
with m4:
    st.markdown('<div class="metric-card"><div class="metric-label">Device connection</div><div class="metric-value" style="font-size:1.55rem;color:#ffcf70">DEMO</div><div class="metric-foot">ESP32 not connected</div></div>', unsafe_allow_html=True)

st.write("")
left, right = st.columns([1.55, 1])
with left:
    st.markdown("### Fluid-level trend")
    st.caption("Illustrative recent values — generated from the demo controls")
    chart_df = pd.DataFrame({"Reading": st.session_state.history})
    st.line_chart(chart_df, height=260, y_min=0, y_max=100)
    st.progress(fluid / 100, text=f"Current fluid level · {fluid}%")
    if low_fluid:
        st.error("Fluid level is at or below 20%. Check the infusion bag.")
    else:
        st.success("Fluid level is above the configured alert threshold.")
with right:
    st.markdown("### System overview")
    st.markdown(f"""
    <div class="metric-card">
      <div class="metric-label">Monitoring mode</div><div style="font-size:1.15rem;font-weight:650">Interactive demo</div>
      <hr style="border-color:#263750">
      <div class="metric-label">Fluid alert threshold</div><div style="font-size:1.05rem;font-weight:650">20%</div>
      <div class="metric-label" style="margin-top:14px">Drop detection</div><div style="font-size:1.05rem;font-weight:650">Manual IR-event simulation</div>
      <div class="metric-label" style="margin-top:14px">Next integration step</div><div style="font-size:0.95rem">Connect ESP32 readings through a secure data bridge.</div>
    </div>
    """, unsafe_allow_html=True)

st.write("")
st.markdown("### Recent activity")
events_df = pd.DataFrame(st.session_state.events)
st.dataframe(events_df, use_container_width=True, hide_index=True, height=245)

st.caption("Prototype/demo only. This dashboard does not control medical equipment or provide clinical alarms. Values are simulated until a real sensor data connection is implemented.")
