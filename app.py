import streamlit as st
import time
import pandas as pd
import plotly.express as px
from datetime import datetime

from src.layout import create_layout
from src.simulation import Simulation
from src.pygame_renderer import PygameRenderer
from src.heatmap import generate_heatmap

# Page Config
st.set_page_config(
    page_title="SmartFlow Crowd Monitoring",
    page_icon="🚶",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize Session State
if "sim" not in st.session_state:
    st.session_state.layout = create_layout()
    st.session_state.sim = Simulation(st.session_state.layout, spawn_rate=0.3)
    st.session_state.renderer = PygameRenderer(st.session_state.layout)
    st.session_state.is_running = False
    st.session_state.sim_speed = 1.0 # default tick delay inverse
    st.session_state.metrics_history = pd.DataFrame(columns=["Tick", "Active Agents", "Wait Timers", "Throughput", "Congestion Score"])
    st.session_state.event_log = []

# Header
st.title("SmartFlow Crowd Monitoring Dashboard")
st.markdown("Real-time monitoring and analytics for space optimization and agent movement.")

# --- SIDEBAR INTERACTIVE CONTROL PANEL ---
with st.sidebar:
    st.header("🎛️ Control Panel")
    
    # Run controls
    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("▶️ Start"):
            st.session_state.is_running = True
    with col2:
        if st.button("⏸️ Pause"):
            st.session_state.is_running = False
    with col3:
        if st.button("🔄 Reset"):
            st.session_state.sim = Simulation(st.session_state.layout, spawn_rate=0.3)
            st.session_state.metrics_history = pd.DataFrame(columns=["Tick", "Active Agents", "Wait Timers", "Throughput", "Congestion Score"])
            st.session_state.event_log = []
            st.session_state.is_running = False
            
    st.markdown("---")
    
    # Speed Slider
    st.session_state.sim_speed = st.slider("Simulation Speed", min_value=1, max_value=10, value=3)
    tick_delay = 0.5 / st.session_state.sim_speed
    
    # Manual Interventions
    if st.button("🚶 Spawn Agents Group"):
        for _ in range(5):
            st.session_state.sim.spawn_student()
        st.session_state.event_log.insert(0, f"[{datetime.now().strftime('%H:%M:%S')}] Manual 5 agent spawn triggered.")
        
    if st.button("🚨 Trigger Emergency Evacuation"):
        st.session_state.event_log.insert(0, f"[{datetime.now().strftime('%H:%M:%S')}] EMERGENCY: Evacuation sequence initiated.")
        # Override all current goals to EXITS and speed up
        from src.agents import StudentState
        import random
        for s in st.session_state.sim.active_students:
            s.state = StudentState.EXIT
            s.goal_position = random.choice(st.session_state.sim.exits)
    
    st.markdown("---")
    # Scenario Selector
    scenario = st.selectbox("Scenario Selector", ["Normal Lunch Hour", "Concert Venue Exit", "Stadium Evacuation", "Festival Crowd Surge"])
    if st.button("Apply Scenario"):
        # For this prototype, 'applying' just alters spawn rates or resets
        if scenario == "Normal Lunch Hour":
            rate = 0.3
        elif scenario == "Concert Venue Exit":
            rate = 0.8
        elif scenario == "Stadium Evacuation":
            rate = 1.0
        else:
            rate = 0.6
        st.session_state.sim = Simulation(st.session_state.layout, spawn_rate=rate)
        st.session_state.event_log.insert(0, f"[{datetime.now().strftime('%H:%M:%S')}] Map reset. Scenario applied: {scenario} (Spawn Rate: {rate})")
        st.session_state.is_running = False


# --- MAIN LAYOUT GRIDS ---
left_col, right_col = st.columns([2, 1])

# Placeholders for real-time updates
with left_col:
    st.subheader("Main Simulation View")
    sim_view_placeholder = st.empty()
    
    st.subheader("Mini-map / Crowd Density Heatmap")
    heatmap_placeholder = st.empty()

with right_col:
    st.subheader("Real-Time Analytics")
    metric_col1, metric_col2 = st.columns(2)
    metric_active = metric_col1.empty()
    metric_congestion = metric_col2.empty()
    metric_speed = metric_col1.empty()
    metric_decisions = metric_col2.empty()
    
    st.subheader("Live Congestion Graph")
    graph_placeholder = st.empty()
    
    st.subheader("AI Decision Event Log")
    log_placeholder = st.empty()


# --- SIMULATION LOOP ---
# Provide an empty element that we will iteratively update if running
st.markdown("---")
status_text = st.empty()

if st.session_state.is_running:
    status_text.info(f"Simulation Running - Ticks: {st.session_state.sim.tick_count}")
    
    # Perform 1 tick
    st.session_state.sim.update()
    
    # 1. Update Metrics DF
    tick = st.session_state.sim.tick_count
    active_count = len(st.session_state.sim.active_students)
    total_wait = sum([s.wait_timer for s in st.session_state.sim.active_students])
    throughput = len(st.session_state.sim.completed_students)
    congestion_score = active_count * 1.5 + total_wait * 0.1 # proxy metric
    
    new_data = pd.DataFrame([{
        "Tick": tick,
        "Active Agents": active_count,
        "Wait Timers": total_wait,
        "Throughput": throughput,
        "Congestion Score": congestion_score
    }])
    st.session_state.metrics_history = pd.concat([st.session_state.metrics_history, new_data], ignore_index=True)
    
    # Detect mock events for logging
    if active_count > 30 and ("High density threshold (30+) reached." not in st.session_state.event_log):
        st.session_state.event_log.insert(0, f"[{datetime.now().strftime('%H:%M:%S')}] Alert: High density threshold (30+) reached. Rerouting active.")
    if tick % 50 == 0:
        st.session_state.event_log.insert(0, f"[{datetime.now().strftime('%H:%M:%S')}] System Check: {active_count} active agents.")
        
    # Keep log history reasonable
    if len(st.session_state.event_log) > 20:
        st.session_state.event_log = st.session_state.event_log[:20]
        
    # 2. Render Main Display
    frame = st.session_state.renderer.render_frame(st.session_state.sim.active_students)
    sim_view_placeholder.image(frame, use_container_width=True, clamp=True)
    
    # 3. Render Heatmap Output
    # Generate every few ticks to save CPU
    if tick % 5 == 0 or tick == 1:
        hm_img = generate_heatmap(st.session_state.layout, st.session_state.sim.active_students)
        heatmap_placeholder.image(hm_img, use_container_width=True)
        
    # 4. Render Metrics Dash
    with metric_active.container():
        st.metric("Active Agents", active_count, delta=int(new_data["Active Agents"].iloc[0] - st.session_state.metrics_history["Active Agents"].shift(1).iloc[-1]) if len(st.session_state.metrics_history) > 1 else 0)
    with metric_congestion.container():
        st.metric("Congestion Score", round(congestion_score, 1))
    with metric_speed.container():
        st.metric("Avg Wait Time", round(total_wait / max(1, active_count), 1))
    with metric_decisions.container():
        st.metric("Total Throughput", throughput)
        
    # 5. Render Plotly Graph
    df = st.session_state.metrics_history.tail(100).copy() # last 100 ticks
    if not df.empty:
        df["Active Agents"] = df["Active Agents"].astype(float)
        df["Congestion Score"] = df["Congestion Score"].astype(float)
        fig = px.line(df, x="Tick", y=["Active Agents", "Congestion Score"], title="System Congestion Over Time", markers=False)
        fig.update_layout(margin=dict(l=0, r=0, t=30, b=0), height=300)
        graph_placeholder.plotly_chart(fig, use_container_width=True)
        
    # 6. Render Logs
    with log_placeholder.container():
        log_text = "\n".join(st.session_state.event_log)
        st.text_area("System Events", log_text, height=200, label_visibility="collapsed")
        
    # Sleep control for loop rate
    time.sleep(tick_delay)
    
    # Rerun cleanly to execute next tick
    st.rerun()

else:
    status_text.warning("Simulation Paused. Click 'Start' to begin execution.")
    
    # Render idle state
    frame = st.session_state.renderer.render_frame(st.session_state.sim.active_students)
    sim_view_placeholder.image(frame, use_container_width=True, clamp=True)
    
    if "hm_img" not in st.session_state:
        st.session_state.hm_img = generate_heatmap(st.session_state.layout, st.session_state.sim.active_students)
    heatmap_placeholder.image(st.session_state.hm_img, use_container_width=True)
    
    # Initial graph
    df = st.session_state.metrics_history.tail(100).copy()
    if not df.empty:
        df["Active Agents"] = df["Active Agents"].astype(float)
        df["Congestion Score"] = df["Congestion Score"].astype(float)
        fig = px.line(df, x="Tick", y=["Active Agents", "Congestion Score"], title="System Congestion Over Time")
        fig.update_layout(margin=dict(l=0, r=0, t=30, b=0), height=300)
        graph_placeholder.plotly_chart(fig, use_container_width=True)
    else:
        graph_placeholder.info("No data yet. Run simulation to generate graphs.")
        
    with log_placeholder.container():
        log_text = "\n".join(st.session_state.event_log) if st.session_state.event_log else "No recent events..."
        st.text_area("System Events", log_text, height=200, label_visibility="collapsed")
