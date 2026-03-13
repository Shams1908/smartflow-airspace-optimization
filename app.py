import streamlit as st
import time
import pandas as pd
import plotly.express as px
from datetime import datetime

from src.layout import create_layout
from src.simulation_engine import SimulationEngine
from src.state_manager import StateManager
from src.renderer import Renderer
from src.metrics_engine import MetricsEngine
from src.feature_extractor import FeatureExtractor
from src.prediction_engine import PredictionEngine
from src.heatmap import HeatmapEngine

# --- Configuration & Styling ---
st.set_page_config(
    page_title="Autonomous Multi-Agent Traffic Coordination Dashboard",
    page_icon="✈️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Styling for "Aerospace" Look
st.markdown("""
<style>
    .metric-box {
        background-color: #1E1E1E;
        padding: 15px;
        border-radius: 5px;
        border-left: 4px solid #00C853;
        margin-bottom: 10px;
    }
    .status-active { color: #00C853; font-weight: bold; }
    .status-inactive { color: #FF3D00; font-weight: bold; }
    .legend-panel {
        font-size: 0.9em;
        background-color: #000221;
        padding: 10px;
        border-radius: 5px;
        border: 1px solid #dee2e6;
    }
</style>
""", unsafe_allow_html=True)

# --- Initialization Phase ---
if "initialized" not in st.session_state:
    st.session_state.layout = create_layout()
    # Core Engines
    st.session_state.sim_engine = SimulationEngine(st.session_state.layout, spawn_rate=0.3)
    st.session_state.state_manager = StateManager()
    st.session_state.renderer = Renderer(st.session_state.layout)
    st.session_state.metrics_engine = MetricsEngine()
    st.session_state.heatmap_engine = HeatmapEngine(st.session_state.layout)
    
    # AI Layers
    feature_extractor = FeatureExtractor(st.session_state.layout)
    st.session_state.prediction_engine = PredictionEngine(feature_extractor)
    
    # State flags & Logs
    st.session_state.sim_speed = 5
    st.session_state.event_log = ["System Initialized."]
    st.session_state.last_sim_time = time.time()
    st.session_state.last_analytics_time = time.time()
    
    # Get initial snapshot
    init_snap = st.session_state.state_manager.capture_state(st.session_state.sim_engine.simulation_ref)
    st.session_state.metrics_engine.calculate_metrics(init_snap)
    st.session_state.heatmap_engine.update_density(init_snap)
    
    st.session_state.initialized = True

def log_event(msg):
    timestamp = datetime.now().strftime("%H:%M:%S")
    st.session_state.event_log.insert(0, f"[{timestamp}] {msg}")
    if len(st.session_state.event_log) > 50:
        st.session_state.event_log = st.session_state.event_log[:50]

# --- Sidebar Controls ---
with st.sidebar:
    st.header("⚙️ Core Systems Control")
    
    # Run controls
    col1, col2 = st.columns(2)
    with col1:
        if st.button("▶️ ENGAGE SIMULATION", use_container_width=True):
            st.session_state.sim_engine.play()
            log_event("Simulation Engine Engaged.")
    with col2:
        if st.button("⏸️ HALT", use_container_width=True):
            st.session_state.sim_engine.pause()
            log_event("Simulation Halted.")
            
    if st.button("🔄 RESTART SCENARIO", use_container_width=True):
        st.session_state.sim_engine.reset(st.session_state.layout, spawn_rate=0.4)
        st.session_state.state_manager = StateManager()
        st.session_state.metrics_engine = MetricsEngine()
        st.session_state.heatmap_engine = HeatmapEngine(st.session_state.layout)
        log_event("Scenario Reset to Base Configuration.")
            
    st.markdown("---")
    
    # Tick Rate Control
    st.session_state.sim_speed = st.slider("Simulation Tick Rate (Hz)", min_value=1, max_value=20, value=5)
    
    st.markdown("---")
    st.subheader("📡 System Status Panel")
    is_running = st.session_state.sim_engine.is_running
    status_cls = "status-active" if is_running else "status-inactive"
    status_txt = "ACTIVE" if is_running else "STANDBY"
    
    st.markdown(f"**Simulation Status:** <span class='{status_cls}'>{status_txt}</span>", unsafe_allow_html=True)
    st.markdown("**Navigation AI:** <span class='status-active'>ACTIVE</span>", unsafe_allow_html=True)
    st.markdown("**Conflict Detection:** <span class='status-active'>ACTIVE</span>", unsafe_allow_html=True)
    st.markdown("**Prediction Engine:** <span class='status-active'>ONLINE</span>", unsafe_allow_html=True)
    st.markdown("**Dynamic Routing:** <span class='status-active'>ACTIVE</span>", unsafe_allow_html=True)
    
    st.markdown("---")
    st.subheader("🚨 Emergency Interventions")
    
    ecol1, ecol2 = st.columns(2)
    with ecol1:
        if st.button("🚨 Evacuation", use_container_width=True):
            st.session_state.sim_engine.trigger_emergency_evacuation()
            log_event("WARNING: Emergency Evacuation Triggered. All agents rerouting to exits.")
            
        if st.button("🚧 Block Path", use_container_width=True):
            cell = st.session_state.sim_engine.block_walkway()
            if cell:
               log_event(f"ALERT: Walkway blocked at {cell}. AI Recomputing Routes.")
            
    with ecol2:
        if st.button("🍽 Table Fail", use_container_width=True):
            st.session_state.sim_engine.trigger_table_failure()
            log_event("ALERT: Seating Capacity Reduced by 2. Agents holding in queue.")
            
        if st.button("✅ All Clear", use_container_width=True):
            st.session_state.sim_engine.clear_emergencies()
            log_event("SYSTEM NORMAL: Emergency cleared. Flow recovering.")
    
    st.markdown("---")
    st.subheader("📖 Visual Legend")
    st.markdown("""
    <div class="legend-panel">
    🟢 <b>Green Circle:</b> Active Agent<br>
    🔴 <b>Red Circle:</b> Rerouted / Waiting Agent<br>
    🔵 <b>Blue Lines:</b> Navigation Corridor<br>
    ⚪ <b>White Lines:</b> Predicted Trajectory<br>
    <br>
    🟩🟨🟥 <b>Heatmap:</b> Traffic Density (Low to High)<br>
    ⭕ <b>Red Pulsing Ring:</b> Predicted Traffic Conflict<br>
    </div>
    """, unsafe_allow_html=True)

# --- Main Dashboard Layout ---
st.title("Autonomous Multi-Agent Traffic Coordination System")

# We create static containers so that we never have to `st.rerun()` the whole page.
top_col1, top_col2 = st.columns([2, 1])

with top_col1:
    st.subheader("Primary Radar / Main Simulation")
    sim_view_container = st.empty()
    
    st.subheader("Traffic Density Matrix")
    heatmap_container = st.empty()

with top_col2:
    st.subheader("Real-Time Analytics")
    metrics_container = st.empty()
    
    st.subheader("AI Traffic Conflict Forecast")
    graph_container = st.empty()
    
    st.subheader("System Event Log")
    log_container = st.empty()


# --- Render Loop (Smooth Visuals without Full Page Refresh) ---
# How this works: Streamlit executes this script top-to-bottom.
# To prevent UI flickering, we trap execution in a while loop and update st.empty()
# containers. If the user interacts with a widget, Streamlit interrupts the loop and reruns.

target_fps = 30
frame_time = 1.0 / target_fps
interpolation_factor = 0.0

loop_counter = 0

while True:
    loop_counter += 1
    loop_start = time.time()
    
    # 1. Update Simulation Engine (Decoupled Frequency based on sim_speed)
    sim_tick_duration = 1.0 / st.session_state.sim_speed
    
    if st.session_state.sim_engine.is_running:
        time_since_sim = loop_start - st.session_state.last_sim_time
        if time_since_sim >= sim_tick_duration:
            # Step the mathematical simulation
            st.session_state.sim_engine.step()
            
            # Capture state snapshot
            snapshot = st.session_state.state_manager.capture_state(st.session_state.sim_engine.simulation_ref)
            
            # Reset interpolation for visualizer
            interpolation_factor = 0.0
            st.session_state.last_sim_time = loop_start
            
            # Check for events
            if snapshot.active_count > 30 and ("High Traffic Density Alert." not in st.session_state.event_log[0:3]):
                log_event("Alert: High Traffic Density. Dynamic Routing compensating.")
        else:
            # Interpolate between ticks for smooth 30fps rendering
            interpolation_factor = min(1.0, time_since_sim / sim_tick_duration)
            
    # 2. Update Analytics & AI Predictions (Decoupled Frequency: ~2Hz)
    if loop_start - st.session_state.last_analytics_time > 0.5:
        current_snap = st.session_state.state_manager.get_current_state()
        if current_snap:
            # Compute Analytics
            st.session_state.metrics_engine.calculate_metrics(current_snap)
            
            # Run AI Predictions
            predictions = st.session_state.prediction_engine.run_prediction(current_snap)
            if predictions:
                high_risk = [p for p in predictions if p["prob"] > 0.8]
                if high_risk:
                   log_event(f"Prediction Engine: Conflict forecasted at {high_risk[0]['pos']} within {high_risk[0]['time_horizon']}s.")
            
            # Update Heatmap Image Buffer
            st.session_state.heatmap_engine.update_density(current_snap)
            
        st.session_state.last_analytics_time = loop_start

    # 3. Render Views (UI Updates)
    snapshot = st.session_state.state_manager.get_current_state()
    predictions = st.session_state.prediction_engine.get_current_predictions()
    
    # Draw Main Simulation
    frame = st.session_state.renderer.render_frame(snapshot, predictions, interpolation_factor)
    sim_view_container.image(frame, use_container_width=True, clamp=True)
    
    # Draw Heatmap
    # To save overhead, we only rerender heatmap image if it's an analytics tick phase
    if loop_start - st.session_state.last_analytics_time < frame_time * 2: # just updated
         hm_img = st.session_state.heatmap_engine.render()
         heatmap_container.image(hm_img, use_container_width=True)
    elif "hm_img" not in st.session_state: # Initial draw fallback
         st.session_state.hm_img = st.session_state.heatmap_engine.render()
         heatmap_container.image(st.session_state.hm_img, use_container_width=True)

    # Render Metrics Panel
    metrics = st.session_state.metrics_engine.get_latest_metrics()
    with metrics_container.container():
        mcol1, mcol2 = st.columns(2)
        mcol1.metric("Active Agents", metrics["active_agents"])
        mcol2.metric("Traffic Conflict Score", round(metrics["congestion_score"], 1))
        mcol1.metric("Avg Nav Wait (s)", round(metrics["avg_wait_time"], 1))
        mcol2.metric("System Throughput", metrics["throughput"])

    # Render Prediction Chart
    # Only update the graph if new telemetry data has arrived (reduces flashing)
    current_metrics_len = len(st.session_state.metrics_engine.metrics_history)
    if "last_metrics_len" not in st.session_state or st.session_state.last_metrics_len != current_metrics_len:
        st.session_state.last_metrics_len = current_metrics_len
        df_metrics = pd.DataFrame(st.session_state.metrics_engine.metrics_history)
        
        if not df_metrics.empty:
            fig = px.area(
                df_metrics.tail(60), # Last 60 ticks
                x="tick", y=["active_agents", "congestion_score"], 
                title="System Load vs Conflict Score",
                color_discrete_sequence=["#00B8D4", "#FF3D00"]
            )
            fig.update_layout(margin=dict(l=0, r=0, t=30, b=0), height=250, xaxis_title="Time (Ticks)", yaxis_title="Score / Count")
            graph_container.plotly_chart(fig, use_container_width=True, key=f"metrics_chart_{current_metrics_len}")
        else:
            graph_container.info("Awaiting telemetry data...")

    # Render Event Log
    log_text = "\n".join(st.session_state.event_log)
    log_container.code(log_text, language="text")

    # Frame Pacing
    elapsed = time.time() - loop_start
    sleep_time = max(0, frame_time - elapsed)
    time.sleep(sleep_time)
