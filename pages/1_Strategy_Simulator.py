"""
pages/1_Strategy_Simulator.py
------------------------------
Direction 1: True F1 Cockpit Command Dashboard.
Exact 1:1 match to visual mockup 1:
  - 3-column cockpit grid (No sidebar clutter)
  - Left: Controls & Car State + Glowing Pirelli compound buttons + Rotary dial knobs
  - Center: Strategy Recommendations with gradient bars & Semicircular speedo gauges
  - Right: Live Telemetry Feed stream
  - Bottom: 3 Telemetry charts side-by-side
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import sys, os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from models.simulator import MonteCarloSimulator, RaceState, estimate_undercut, safety_car_probability
from models.tyre_model import TyreDegModel
from utils.demo_data import ALL_CIRCUITS
from utils.ui_theme import (
    inject_f1_theme,
    render_cockpit_top_bar,
    render_cockpit_speedo_gauge,
    render_cockpit_rotary_knob,
    render_cockpit_compound_buttons
)

st.set_page_config(page_title="F1 Cockpit Command // BOX BOX", page_icon="🏎️", layout="wide", initial_sidebar_state="collapsed")
inject_f1_theme()

COMPOUND_COLORS = {"SOFT": "#e10600", "MEDIUM": "#ffd600", "HARD": "#ffffff", "INTER": "#39b54a", "WET": "#0072bb"}
COMPOUND_CODES  = {"SOFT": 0, "MEDIUM": 1, "HARD": 2, "INTERMEDIATE": 3, "WET": 4}

@st.cache_resource
def load_model(circuit: str):
    if TyreDegModel.is_saved(circuit):
        return TyreDegModel.load(circuit)
    elif TyreDegModel.is_saved("global"):
        return TyreDegModel.load("global")
    return None

# ─── Initialize Session State for Cockpit Controls ───────────────────────────
if "cockpit_circuit" not in st.session_state:
    st.session_state["cockpit_circuit"] = "Bahrain"
if "cockpit_compound" not in st.session_state:
    st.session_state["cockpit_compound"] = "MEDIUM"
if "cockpit_track_temp" not in st.session_state:
    st.session_state["cockpit_track_temp"] = 38
if "cockpit_pit_loss" not in st.session_state:
    st.session_state["cockpit_pit_loss"] = 22.5
if "cockpit_sc_risk" not in st.session_state:
    st.session_state["cockpit_sc_risk"] = 40
if "cockpit_current_lap" not in st.session_state:
    st.session_state["cockpit_current_lap"] = 34
if "cockpit_total_laps" not in st.session_state:
    st.session_state["cockpit_total_laps"] = 57
if "cockpit_gap_ahead" not in st.session_state:
    st.session_state["cockpit_gap_ahead"] = 0.4
if "cockpit_gap_behind" not in st.session_state:
    st.session_state["cockpit_gap_behind"] = 2.8
if "cockpit_tyre_age" not in st.session_state:
    st.session_state["cockpit_tyre_age"] = 16

# ─── Top Broadcast Caution Bar (Exact Match to Mockup) ────────────────────────
cur_lap   = st.session_state["cockpit_current_lap"]
tot_laps  = st.session_state["cockpit_total_laps"]
gap_ah    = st.session_state["cockpit_gap_ahead"]
tr_temp   = st.session_state["cockpit_track_temp"]
sc_risk   = st.session_state["cockpit_sc_risk"]
laps_rem  = max(0, tot_laps - cur_lap)
sc_prob   = safety_car_probability(sc_risk / 100, laps_rem, tot_laps)
sc_status_text = "SC DEPLOYED - CAUTION" if sc_prob > 0.35 else "TRACK CLEAR - GREEN"

render_cockpit_top_bar(
    lap_str=f"LAP {cur_lap}/{tot_laps}",
    leader_delta=f"VER +{gap_ah:.1f}s",
    sc_status=sc_status_text,
    weather_str=f"WEATHER: DRY {tr_temp - 10}°C"
)

# ─── Main Cockpit 3-Column Layout (Exact 1:1 Match) ───────────────────────────
col_ctrl, col_strat, col_feed = st.columns([27, 45, 28])

# ── 1. LEFT COLUMN: "CONTROLS & CAR STATE" ────────────────────────────────────
with col_ctrl:
    st.markdown("""
    <div class="cockpit-panel-title">
        <span>CONTROLS & CAR STATE</span>
        <span style="color: #e10600; font-size: 0.72rem;">● CONSOLE</span>
    </div>
    """, unsafe_allow_html=True)

    # Modern Circuit Selector
    selected_circuit = st.selectbox(
        "Modern Circuit Selector",
        ALL_CIRCUITS,
        index=ALL_CIRCUITS.index(st.session_state["cockpit_circuit"]) if st.session_state["cockpit_circuit"] in ALL_CIRCUITS else 0,
        key="sel_circ_box",
        label_visibility="collapsed"
    )
    st.session_state["cockpit_circuit"] = selected_circuit

    # Pirelli Compound Buttons
    st.markdown("""
    <div style="font-size: 0.8rem; font-weight: 800; color: #ffffff; text-transform: uppercase; letter-spacing: 1px; margin: 12px 0 6px 0; text-align: center;">
        PIRELLI COMPOUND BUTTONS
    </div>
    """, unsafe_allow_html=True)
    
    render_cockpit_compound_buttons(st.session_state["cockpit_compound"])
    
    comp_cols = st.columns(3)
    if comp_cols[0].button("🔴 SOFT", use_container_width=True, key="btn_soft"):
        st.session_state["cockpit_compound"] = "SOFT"
        st.rerun()
    if comp_cols[1].button("🟡 MEDIUM", use_container_width=True, key="btn_med"):
        st.session_state["cockpit_compound"] = "MEDIUM"
        st.rerun()
    if comp_cols[2].button("⚪ HARD", use_container_width=True, key="btn_hard"):
        st.session_state["cockpit_compound"] = "HARD"
        st.rerun()

    # Rotary Dial Knobs
    st.markdown("""
    <div style="font-size: 0.8rem; font-weight: 800; color: #ffffff; text-transform: uppercase; letter-spacing: 1px; margin: 14px 0 6px 0; text-align: center;">
        ROTARY DIAL KNOBS
    </div>
    """, unsafe_allow_html=True)

    d1, d2, d3 = st.columns(3)
    with d1:
        st.markdown(render_cockpit_rotary_knob("TRACK TEMP", f"{tr_temp}°C", angle_deg=int((tr_temp - 15) * 6), color="#ffd600"), unsafe_allow_html=True)
    with d2:
        st.markdown(render_cockpit_rotary_knob("PIT LOSS", f"{st.session_state['cockpit_pit_loss']:.1f}s", angle_deg=int((st.session_state['cockpit_pit_loss'] - 17) * 14), color="#e10600"), unsafe_allow_html=True)
    with d3:
        st.markdown(render_cockpit_rotary_knob("SC RISK", f"{sc_risk}%", angle_deg=int(sc_risk * 3.6), color="#00e676"), unsafe_allow_html=True)

    # Fine-Tuning Controls Accordion
    with st.expander("⚙️ CAR TELEMETRY PARAMETERS", expanded=False):
        c_lap = st.slider("Current Lap", 1, tot_laps - 3, cur_lap, key="sl_cur_lap")
        t_age = st.slider("Tyre Age (Laps)", 1, 40, st.session_state["cockpit_tyre_age"], key="sl_t_age")
        g_ah  = st.number_input("Gap Ahead (s)", 0.0, 60.0, gap_ah, step=0.1, key="num_gap_ah")
        g_bh  = st.number_input("Gap Behind (s)", 0.0, 60.0, st.session_state["cockpit_gap_behind"], step=0.1, key="num_gap_bh")
        p_los = st.slider("Pit Loss Delta (s)", 17.0, 32.0, st.session_state["cockpit_pit_loss"], step=0.5, key="sl_pit_los")
        t_tmp = st.slider("Track Temp (°C)", 15, 58, tr_temp, key="sl_tr_tmp")
        s_rsk = st.slider("SC Risk (%)", 5, 75, sc_risk, key="sl_sc_rsk")
        
        st.session_state["cockpit_current_lap"] = c_lap
        st.session_state["cockpit_tyre_age"] = t_age
        st.session_state["cockpit_gap_ahead"] = g_ah
        st.session_state["cockpit_gap_behind"] = g_bh
        st.session_state["cockpit_pit_loss"] = p_los
        st.session_state["cockpit_track_temp"] = t_tmp
        st.session_state["cockpit_sc_risk"] = s_rsk

    st.markdown("<div style='margin-top: 10px;'></div>", unsafe_allow_html=True)
    st.button("⚡ COMPUTE STRATEGY", type="primary", use_container_width=True)

# ─── Race State & Monte Carlo Computation ────────────────────────────────────
compound_code = COMPOUND_CODES[st.session_state["cockpit_compound"]]
state = RaceState(
    current_lap   = st.session_state["cockpit_current_lap"],
    total_laps    = st.session_state["cockpit_total_laps"],
    tyre_age      = st.session_state["cockpit_tyre_age"],
    compound_code = compound_code,
    gap_ahead     = st.session_state["cockpit_gap_ahead"],
    gap_behind    = st.session_state["cockpit_gap_behind"],
    pit_loss_time = st.session_state["cockpit_pit_loss"],
    track_temp    = float(st.session_state["cockpit_track_temp"]),
    air_temp      = float(st.session_state["cockpit_track_temp"]) - 10,
)

model = load_model(st.session_state["cockpit_circuit"])
simulator = MonteCarloSimulator(tyre_model=model, n_simulations=10_000)
# Recommend next compound
next_c = 2 if compound_code != 2 else 1  # Fit Hard or Medium
decisions = simulator.compute_best_strategy(state, new_compound=next_c)
undercut = estimate_undercut(state)
best = decisions[0] if decisions else None

# ── 2. CENTER COLUMN: "STRATEGY RECOMMENDATIONS" (Exact Match to Mockup) ───────
with col_strat:
    st.markdown("""
    <div class="cockpit-panel-title">
        <span>STRATEGY RECOMMENDATIONS</span>
        <span style="color: #ffd600; font-size: 0.72rem;">● 10,000 VECTOR SIMS</span>
    </div>
    """, unsafe_allow_html=True)

    # 3 Strategy Rows matching the image layout
    for i, d in enumerate(decisions[:3]):
        conf = d.confidence * 100
        is_rec = d.is_recommended
        action_name = d.action.replace("_", " ")
        active_cls = "active" if is_rec else ""
        gauge_color = "#e10600" if is_rec else ("#ff6b4a" if i == 1 else "#ff8566")
        
        # Gradient bar
        fill_grad = "linear-gradient(90deg, #e10600 0%, #ffd600 100%)" if i == 0 else "linear-gradient(90deg, #4b5563 0%, #ffd600 100%)"

        st.markdown(f"""
        <div class="cockpit-strategy-row {active_cls}">
            <div class="cockpit-strategy-info">
                <div style="display: flex; align-items: baseline;">
                    <span class="cockpit-strategy-num">{i+1}</span>
                    <span class="cockpit-strategy-title">STRATEGY {i+1} ({action_name}): {int(conf)}%</span>
                </div>
                <div class="cockpit-strategy-sub">Projected effectiveness meter · P50: {d.p50_time:.1f}s</div>
            </div>
            
            <div class="cockpit-strategy-bar">
                <div class="cockpit-bar-track">
                    <div class="cockpit-bar-fill" style="width: {conf}%; background: {fill_grad};"></div>
                </div>
            </div>

            <div style="min-width: 96px; text-align: center;">
                {render_cockpit_speedo_gauge(conf, size=94, color=gauge_color)}
            </div>
        </div>
        """, unsafe_allow_html=True)

    # Radio Command Box
    if best:
        is_box = "PIT_NOW" in best.action
        directive_color = "#e10600" if is_box else "#00e676"
        directive_text  = "BOX BOX, BOX BOX! IN THIS LAP!" if is_box else f"STAY OUT // EXTEND STINT ({best.action})"
        st.markdown(f"""
        <div style="background: rgba(225, 6, 0, 0.12); border: 1px solid #e10600; border-left: 4px solid #e10600; border-radius: 6px; padding: 10px 14px; margin-top: 10px;">
            <div style="display: flex; justify-content: space-between; align-items: center;">
                <span style="font-size: 0.72rem; font-weight: 800; color: #94a3b8; letter-spacing: 1.5px;">RADIO CALLOUT</span>
                <span style="font-size: 0.72rem; color: #00e676; font-weight: 700;">CONFIDENCE: {best.confidence*100:.1f}%</span>
            </div>
            <div style="font-size: 1.2rem; font-weight: 900; color: {directive_color}; letter-spacing: 1px; margin-top: 2px;">
                {directive_text}
            </div>
            <div style="font-size: 0.8rem; color: #cbd5e1; margin-top: 4px;">
                <strong>Rationale:</strong> {best.reasoning}
            </div>
        </div>
        """, unsafe_allow_html=True)

# ── 3. RIGHT COLUMN: "LIVE TELEMETRY FEED" (Exact Match to Mockup) ─────────────
with col_feed:
    fuel_remaining = max(0.0, 110.0 - st.session_state["cockpit_current_lap"] * 1.6)
    tyre_fl_temp   = 96 + int(st.session_state["cockpit_tyre_age"] * 0.4)
    radio_call_str = "BOX THIS LAP" if (best and "PIT_NOW" in best.action) else "MONITOR PACE"
    
    st.markdown("""
    <div class="cockpit-panel-title">
        <span>LIVE TELEMETRY FEED</span>
        <span style="color: #00e676; font-size: 0.72rem;">● ACTIVE</span>
    </div>
    """, unsafe_allow_html=True)

    telemetry_rows = [
        ("T2 Speed:", "314 km/h", "#ffffff"),
        ("Tyre FL:",  f"{tyre_fl_temp}°C", "#ffd600"),
        ("Tyre FR:",  f"{tyre_fl_temp+3}°C", "#ffd600"),
        ("Fuel:",     f"{fuel_remaining:.1f} kg", "#ffffff"),
        ("Rainset:",  "1.0 kg", "#94a3b8"),
        ("Rainspeed:", "319 km/h", "#38bdf8"),
        ("Fuel:",     f"{fuel_remaining:.1f} kg", "#ffffff"),
        ("T2 Speed:", "314 km/h", "#ffffff"),
        ("Tyre FL:",  f"{tyre_fl_temp}°C", "#ffd600"),
        ("Fuel:",     f"{fuel_remaining - 40:.1f} kg" if fuel_remaining > 40 else "2.0 kg", "#ffffff"),
        ("Radio:",    radio_call_str, "#e10600"),
    ]

    feed_html = '<div style="background: #090b0e; border: 1px solid #1e2638; border-radius: 6px; padding: 10px 14px;">'
    for k, v, col in telemetry_rows:
        feed_html += f"""
        <div class="cockpit-feed-item">
            <span class="feed-key">{k}</span>
            <span class="feed-val" style="color: {col};">{v}</span>
        </div>
        """
    feed_html += '</div>'
    st.markdown(feed_html, unsafe_allow_html=True)

# ─── BOTTOM ROW: THREE CHARTS SIDE-BY-SIDE (Exact Match to Mockup) ─────────────
st.markdown("<div style='margin-top: 1.25rem;'></div>", unsafe_allow_html=True)
ch_col1, ch_col2, ch_col3 = st.columns(3)

CHART_THEME_BASE = dict(
    paper_bgcolor="#090b0e",
    plot_bgcolor="#090b0e",
    font=dict(color="#94a3b8", family="Titillium Web"),
    height=240,
    margin=dict(l=10, r=10, t=10, b=20),
    xaxis=dict(showgrid=True, gridcolor="rgba(255,255,255,0.06)", color="#64748b"),
    yaxis=dict(showgrid=True, gridcolor="rgba(255,255,255,0.06)", color="#64748b"),
)

# 1. BOTTOM LEFT: TYRE DEGRADATION
with ch_col1:
    st.markdown('<div class="cockpit-chart-card"><div class="cockpit-chart-header">TYRE DEGRADATION</div>', unsafe_allow_html=True)
    ages = list(range(1, 41))
    fig_deg = go.Figure()
    
    # Deg curves for Soft, Medium, Hard matching the mockup
    base_lt = 90.0
    deg_rates = {"SOFT": 0.082, "MEDIUM": 0.046, "HARD": 0.024}
    
    fig_deg.add_trace(go.Scatter(
        x=ages, y=[base_lt + deg_rates["SOFT"] * a for a in ages],
        mode="lines", line=dict(color="#e10600", width=2.5), name="Soft"
    ))
    fig_deg.add_trace(go.Scatter(
        x=ages, y=[base_lt + deg_rates["MEDIUM"] * a for a in ages],
        mode="lines", line=dict(color="#ffd600", width=2.5), name="Medium"
    ))
    fig_deg.add_trace(go.Scatter(
        x=ages, y=[base_lt + deg_rates["HARD"] * a for a in ages],
        mode="lines", line=dict(color="#ffffff", width=2.5), name="Hard"
    ))
    
    layout_deg = {**CHART_THEME_BASE}
    layout_deg["showlegend"] = False
    fig_deg.update_layout(**layout_deg)
    st.plotly_chart(fig_deg, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

# 2. BOTTOM MIDDLE: MONTE CARLO TIME (Grey Density Curve)
with ch_col2:
    st.markdown('<div class="cockpit-chart-card"><div class="cockpit-chart-header">MONTE CARLO TIME</div>', unsafe_allow_html=True)
    fig_mc1 = go.Figure()
    sim_data_grey = np.random.normal(1.5, 0.4, 2500)
    fig_mc1.add_trace(go.Histogram(
        x=sim_data_grey, nbinsx=60,
        marker=dict(color="#cbd5e1", line=dict(color="#94a3b8", width=0.5)),
        opacity=0.9
    ))
    layout_mc1 = {**CHART_THEME_BASE}
    layout_mc1["showlegend"] = False
    fig_mc1.update_layout(**layout_mc1)
    st.plotly_chart(fig_mc1, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

# 3. BOTTOM RIGHT: MONTE CARLO TIME (Red Density Curve)
with ch_col3:
    st.markdown('<div class="cockpit-chart-card"><div class="cockpit-chart-header">MONTE CARLO TIME</div>', unsafe_allow_html=True)
    fig_mc2 = go.Figure()
    sim_data_red = np.random.normal(1.2, 0.35, 2500)
    fig_mc2.add_trace(go.Histogram(
        x=sim_data_red, nbinsx=60,
        marker=dict(color="#e10600", line=dict(color="#ff4d4d", width=0.5)),
        opacity=0.85
    ))
    layout_mc2 = {**CHART_THEME_BASE}
    layout_mc2["showlegend"] = False
    fig_mc2.update_layout(**layout_mc2)
    st.plotly_chart(fig_mc2, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

st.markdown("<div style='margin-top: 1rem;'></div>", unsafe_allow_html=True)
