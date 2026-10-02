"""
pages/1_Strategy_Simulator.py
------------------------------
Option A: Pit Wall Command Center — Interactive Strategy Simulator.
Features:
  - Semicircular radial confidence gauges
  - Steering wheel rotary dials
  - Circular compound pills
  - Dedicated Live Telemetry Feed panel
  - Broadcast ticker banner
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
    render_pit_wall_banner,
    render_semicircular_gauge,
    render_rotary_dial,
    render_compound_badges_selector,
    render_telemetry_feed_panel
)

st.set_page_config(page_title="Pit Wall Strategy Simulator // BOX BOX", page_icon="🏎️", layout="wide")
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

# ─── Sidebar: F1 Console with Rotary Dials ─────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div style="font-weight: 900; color: #ffffff; font-size: 1.1rem; letter-spacing: 1px; border-bottom: 2px solid #e10600; padding-bottom: 6px; margin-bottom: 12px; display: flex; align-items: center; justify-content: space-between;">
        <span>CIRCUIT SELECTOR</span>
        <span style="font-size: 0.7rem; color: #e10600; font-family: 'JetBrains Mono', monospace;">PIT WALL</span>
    </div>
    """, unsafe_allow_html=True)

    circuit = st.selectbox("Select Grand Prix", ALL_CIRCUITS, index=0, label_visibility="collapsed")

    st.markdown("""
    <div style="font-weight: 800; color: #ffffff; font-size: 0.85rem; letter-spacing: 1px; text-transform: uppercase; margin: 16px 0 6px 0;">
        COMPOUND SELECTION
    </div>
    """, unsafe_allow_html=True)
    
    compound = st.selectbox("Fitted Tyre Compound", ["SOFT", "MEDIUM", "HARD"], index=1)
    render_compound_badges_selector(compound)

    st.markdown("<hr style='margin: 12px 0; border-color: rgba(225,6,0,0.2);'>", unsafe_allow_html=True)

    st.markdown("**Stint Telemetry**")
    total_laps  = st.slider("Total Race Laps", min_value=30, max_value=78, value=57)
    current_lap = st.slider("Current Lap", min_value=1, max_value=total_laps - 3, value=34)
    tyre_age     = st.slider("Tyre Age (Laps Completed)", min_value=1, max_value=40, value=16)
    new_compound = st.selectbox("Compound at Next Stop", ["HARD", "MEDIUM", "SOFT"], index=0)

    st.markdown("<hr style='margin: 12px 0; border-color: rgba(225,6,0,0.2);'>", unsafe_allow_html=True)
    st.markdown("**Interval Gaps**")
    gap_ahead  = st.number_input("Gap Ahead (s)", min_value=0.0, max_value=60.0, value=0.4, step=0.1)
    gap_behind = st.number_input("Gap Behind (s)", min_value=0.0, max_value=60.0, value=2.8, step=0.1)

    st.markdown("<hr style='margin: 12px 0; border-color: rgba(225,6,0,0.2);'>", unsafe_allow_html=True)
    st.markdown("**Steering Wheel Rotary Controls**")
    pit_loss   = st.slider("Pit Lane Loss Delta (s)", min_value=17.0, max_value=32.0, value=22.5, step=0.5)
    track_temp = st.slider("Track Temp (°C)", min_value=15, max_value=58, value=38)
    sc_base    = st.slider("Historical SC Risk (%)", min_value=5, max_value=75, value=40)

    # Option A bottom-left rotary dials
    dial_col1, dial_col2, dial_col3 = st.columns(3)
    with dial_col1:
        st.markdown(render_rotary_dial("PIT LOSS", f"{pit_loss:.1f}s", rotation_deg=int((pit_loss - 17) * 12), color="#e10600"), unsafe_allow_html=True)
    with dial_col2:
        st.markdown(render_rotary_dial("TRACK", f"{track_temp}°C", rotation_deg=int((track_temp - 15) * 5), color="#ffd600"), unsafe_allow_html=True)
    with dial_col3:
        st.markdown(render_rotary_dial("SC RISK", f"{sc_base}%", rotation_deg=int(sc_base * 3.6), color="#00e676"), unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    n_sims  = st.select_slider("Monte Carlo Iterations", options=[1_000, 5_000, 10_000, 20_000], value=10_000)
    run_btn = st.button("⚡ EXECUTE STRATEGY SIMULATION", type="primary", use_container_width=True)

# ─── Top Broadcast Ticker (Option A) ──────────────────────────────────────────
laps_remaining = max(0, total_laps - current_lap)
sc_prob = safety_car_probability(sc_base / 100, laps_remaining, total_laps)
sc_status_text = "SC DEPLOYED - CAUTION" if sc_prob > 0.4 else "TRACK CLEAR - GREEN"

render_pit_wall_banner(
    circuit=circuit,
    session_type="RACE STRATEGY COMPUTED",
    lap_str=f"LAP {current_lap} / {total_laps}",
    leader_delta=f"VER +{gap_ahead:.1f}s",
    sc_status=sc_status_text,
    weather_str=f"DRY ({track_temp - 10}°C)"
)

# ─── Build Race State ──────────────────────────────────────────────────────────
state = RaceState(
    current_lap   = current_lap,
    total_laps    = total_laps,
    tyre_age      = tyre_age,
    compound_code = COMPOUND_CODES[compound],
    gap_ahead     = gap_ahead,
    gap_behind    = gap_behind,
    pit_loss_time = pit_loss,
    track_temp    = float(track_temp),
    air_temp      = float(track_temp) - 10,
)

# Run Simulation
model     = load_model(circuit)
simulator = MonteCarloSimulator(tyre_model=model, n_simulations=n_sims)
decisions = simulator.compute_best_strategy(state, new_compound=COMPOUND_CODES[new_compound])
undercut  = estimate_undercut(state)
best      = decisions[0] if decisions else None

# ─── Option A Main Grid: Strategy Recommendations + Telemetry Feed ─────────────
main_col, telemetry_col = st.columns([65, 35])

with main_col:
    st.markdown("""
    <div class="pitwall-card-header">
        <span>STRATEGY RECOMMENDATIONS</span>
        <span style="color: #e10600; font-family: 'JetBrains Mono', monospace; font-size: 0.75rem;">10,000 MONTE CARLO ITERATIONS</span>
    </div>
    """, unsafe_allow_html=True)

    for i, d in enumerate(decisions):
        is_rec = d.is_recommended
        card_class = "strategy-row-card recommended" if is_rec else "strategy-row-card"
        gauge_color = "#e10600" if is_rec else ("#ffd600" if i == 1 else "#38bdf8")
        badge_label = "★ OPTIMAL CALL" if is_rec else f"+{d.expected_time_loss:.1f}s DELTA"
        badge_color = "#00e676" if is_rec else "#94a3b8"
        confidence_pct = d.confidence * 100

        st.markdown(f"""
        <div class="{card_class}">
            <div style="min-width: 170px;">
                <div style="font-size: 0.75rem; color: {badge_color}; font-weight: 800; letter-spacing: 1px;">
                    {badge_label}
                </div>
                <div style="font-weight: 900; font-size: 1.15rem; color: #ffffff; letter-spacing: 0.5px; margin-top: 2px;">
                    {d.action.replace('_', ' ')}
                </div>
                <div style="font-size: 0.8rem; color: #94a3b8; margin-top: 4px;">
                    FITTING: <strong style="color: {COMPOUND_COLORS.get(d.recommended_compound, '#fff')};">● {d.recommended_compound}</strong>
                </div>
            </div>
            
            <div class="strategy-bar-container">
                <div style="display: flex; justify-content: space-between; font-size: 0.72rem; color: #94a3b8; font-family: 'JetBrains Mono', monospace; margin-bottom: 4px;">
                    <span>CONFIDENCE INDEX</span>
                    <span style="color: #ffffff; font-weight: 700;">{confidence_pct:.1f}%</span>
                </div>
                <div class="strategy-progress-bg">
                    <div class="strategy-progress-fill" style="width: {confidence_pct}%; background: linear-gradient(90deg, #7a0300 0%, {gauge_color} 100%);"></div>
                </div>
                <div style="font-size: 0.75rem; color: #64748b; margin-top: 4px; font-family: 'JetBrains Mono', monospace;">
                    P50 EXP: <strong style="color: #ffffff;">{d.p50_time:.1f}s</strong> (P10: {d.p10_time:.1f}s / P90: {d.p90_time:.1f}s)
                </div>
            </div>

            <div style="min-width: 90px; text-align: center;">
                {render_semicircular_gauge(confidence_pct, size=88, color=gauge_color)}
            </div>
        </div>
        """, unsafe_allow_html=True)

    # Radio Engineer Callout
    if best:
        is_box_now = "PIT_NOW" in best.action
        radio_color = "#e10600" if is_box_now else "#00e676"
        radio_call  = "BOX BOX, BOX BOX! IN THIS LAP!" if is_box_now else f"STAY OUT // EXTEND STINT ({best.action})"
        st.markdown(f"""
        <div style="background: rgba(225, 6, 0, 0.1); border: 1px solid #e10600; border-left: 4px solid #e10600; border-radius: 6px; padding: 12px 16px; margin-top: 8px;">
            <div style="font-size: 0.75rem; font-weight: 800; color: #94a3b8; text-transform: uppercase; letter-spacing: 1.5px;">
                📻 PIT WALL RADIO DIRECTIVE
            </div>
            <div style="font-size: 1.35rem; font-weight: 900; color: {radio_color}; letter-spacing: 1px; margin-top: 2px;">
                {radio_call}
            </div>
            <div style="color: #cbd5e1; font-size: 0.85rem; margin-top: 6px; line-height: 1.5;">
                <strong>Engineer Rationale:</strong> {best.reasoning}
            </div>
        </div>
        """, unsafe_allow_html=True)

with telemetry_col:
    render_telemetry_feed_panel(
        driver="VER",
        lap=current_lap,
        speed=314,
        fuel_kg=max(0, 110.0 - current_lap * 1.6),
        tire_temp_fl=96 + int(tyre_age * 0.4),
        sector_delta="-0.18s",
        pit_lane_status="CLEAR (22.5s LOSS)",
        radio_msg="BOX THIS LAP" if (best and "PIT_NOW" in best.action) else "MONITOR PACE"
    )

st.markdown("<br>", unsafe_allow_html=True)

# ─── Option A Bottom Row: Charts ──────────────────────────────────────────────
st.markdown("""
<div class="pitwall-card-header">
    <span>TELEMETRY & STRATEGY VISUALIZATION</span>
    <span style="color: #94a3b8; font-size: 0.75rem;">LIVE CHARTS</span>
</div>
""", unsafe_allow_html=True)

ch1, ch2, ch3 = st.columns(3)

CHART_THEME = dict(
    paper_bgcolor="#0d1017",
    plot_bgcolor="#090b0e",
    font=dict(color="#cbd5e1", family="Titillium Web"),
    height=280,
    margin=dict(l=15, r=15, t=30, b=20),
    xaxis=dict(showgrid=True, gridcolor="rgba(255,255,255,0.05)", color="#94a3b8"),
    yaxis=dict(showgrid=True, gridcolor="rgba(255,255,255,0.05)", color="#94a3b8"),
)

with ch1:
    st.markdown("<span style='font-size:0.8rem; font-weight:800; color:#e10600;'>STRATEGY DELTA UNCERTAINTY (P10 / P50 / P90)</span>", unsafe_allow_html=True)
    fig_time = go.Figure()
    for d in decisions:
        fig_time.add_trace(go.Bar(
            name=d.action,
            x=[d.action.replace("_", " ")],
            y=[d.p50_time],
            error_y=dict(
                type="data",
                array=[d.p90_time - d.p50_time],
                arrayminus=[d.p50_time - d.p10_time],
                visible=True, color="#94a3b8", thickness=2,
            ),
            marker=dict(
                color="#e10600" if d.is_recommended else "#1e293b",
                line=dict(color="#ff4d4d" if d.is_recommended else "#334155", width=1.5)
            ),
            showlegend=False,
        ))
    layout_time = {**CHART_THEME}
    layout_time["yaxis"] = dict(**layout_time["yaxis"], title="Total Race Seconds")
    fig_time.update_layout(**layout_time)
    st.plotly_chart(fig_time, use_container_width=True)

with ch2:
    st.markdown("<span style='font-size:0.8rem; font-weight:800; color:#ffd600;'>PIRELLI TYRE DEGRADATION (S / M / H)</span>", unsafe_allow_html=True)
    ages = list(range(1, 41))
    traces = []
    if model and model.is_trained:
        for comp_name, comp_code in [("SOFT", 0), ("MEDIUM", 1), ("HARD", 2)]:
            times = [model.predict_lap_time(comp_code, a, float(track_temp)-10, float(track_temp))["p50"] for a in ages]
            traces.append((comp_name, ages, times))
    else:
        deg = {0: 0.082, 1: 0.046, 2: 0.024}
        base = 90.0
        traces = [
            ("SOFT",   ages, [base + deg[0]*a for a in ages]),
            ("MEDIUM", ages, [base + deg[1]*a for a in ages]),
            ("HARD",   ages, [base + deg[2]*a for a in ages]),
        ]

    fig_deg = go.Figure()
    for comp_name, x, y in traces:
        fig_deg.add_trace(go.Scatter(
            x=x, y=y, name=comp_name,
            line=dict(color=COMPOUND_COLORS[comp_name], width=2.5),
            mode="lines"
        ))
    fig_deg.add_vline(x=tyre_age, line_dash="dash", line_color="#e10600", line_width=2,
                      annotation_text=f"LAP {tyre_age}", annotation_font_color="#e10600")
    layout_deg = {**CHART_THEME}
    layout_deg["xaxis"] = dict(**layout_deg["xaxis"], title="Tyre Age (Laps)")
    layout_deg["yaxis"] = dict(**layout_deg["yaxis"], title="Lap Time (s)")
    layout_deg["legend"] = dict(bgcolor="rgba(10,12,16,0.8)", bordercolor="#1e2638")
    fig_deg.update_layout(**layout_deg)
    st.plotly_chart(fig_deg, use_container_width=True)

with ch3:
    st.markdown("<span style='font-size:0.8rem; font-weight:800; color:#38bdf8;'>MONTE CARLO PROBABILITY DENSITY</span>", unsafe_allow_html=True)
    if len(decisions) >= 2:
        best_d   = decisions[0]
        second_d = decisions[1]
        n_plot   = 2_000
        sim_best   = np.random.normal(best_d.p50_time, (best_d.p90_time - best_d.p10_time) / 2.56, n_plot)
        sim_second = np.random.normal(second_d.p50_time, (second_d.p90_time - second_d.p10_time) / 2.56, n_plot)

        fig_dist = go.Figure()
        fig_dist.add_trace(go.Histogram(
            x=sim_best, name=f"#1 {best_d.action.replace('_',' ')}", nbinsx=40,
            marker_color="#e10600", opacity=0.75,
        ))
        fig_dist.add_trace(go.Histogram(
            x=sim_second, name=f"#2 {second_d.action.replace('_',' ')}", nbinsx=40,
            marker_color="#38bdf8", opacity=0.55,
        ))
        layout_dist = {**CHART_THEME}
        layout_dist["barmode"] = "overlay"
        layout_dist["xaxis"] = dict(**layout_dist["xaxis"], title="Race Seconds")
        layout_dist["yaxis"] = dict(**layout_dist["yaxis"], title="Sims")
        layout_dist["legend"] = dict(bgcolor="rgba(10,12,16,0.8)", bordercolor="#1e2638")
        fig_dist.update_layout(**layout_dist)
        st.plotly_chart(fig_dist, use_container_width=True)

# ─── Tactical Undercut Bar ─────────────────────────────────────────────────────
st.markdown("<hr style='margin: 1.5rem 0; border-color: rgba(255,255,255,0.06);'>", unsafe_allow_html=True)
uc1, uc2, uc3 = st.columns(3)
with uc1:
    viable = undercut["viable"]
    color = "#00e676" if viable else "#e10600"
    st.markdown(f"""
    <div style="background:#10141e; border: 1px solid {color}; border-radius: 6px; padding: 12px;">
        <div style="font-size: 0.72rem; color: #94a3b8; text-transform: uppercase;">UNDERCUT VIABILITY</div>
        <div style="font-size: 1.4rem; font-weight: 900; color: {color}; margin-top: 2px;">
            {"✓ FEASIBLE" if viable else "✗ HIGH RISK"}
        </div>
        <div style="font-size: 0.8rem; color: #cbd5e1; margin-top: 4px;">{undercut['recommendation']}</div>
    </div>
    """, unsafe_allow_html=True)

with uc2:
    ltr = undercut.get("laps_to_recover")
    st.markdown(f"""
    <div style="background:#10141e; border: 1px solid #1e2638; border-radius: 6px; padding: 12px;">
        <div style="font-size: 0.72rem; color: #94a3b8; text-transform: uppercase;">LAPS TO OVERTURN GAP</div>
        <div style="font-size: 1.4rem; font-weight: 900; color: #ffffff; margin-top: 2px; font-family: 'JetBrains Mono', monospace;">
            {f"{ltr:.1f} LAPS" if ltr else "OVERCUT / DEFEND"}
        </div>
        <div style="font-size: 0.8rem; color: #94a3b8; margin-top: 4px;">Based on {pit_loss:.1f}s pit stop time loss.</div>
    </div>
    """, unsafe_allow_html=True)

with uc3:
    st.markdown(f"""
    <div style="background:#10141e; border: 1px solid #1e2638; border-radius: 6px; padding: 12px;">
        <div style="font-size: 0.72rem; color: #94a3b8; text-transform: uppercase;">SAFETY CAR RISK WINDOW</div>
        <div style="font-size: 1.4rem; font-weight: 900; color: {'#ffd600' if sc_prob>0.3 else '#00e676'}; margin-top: 2px; font-family: 'JetBrains Mono', monospace;">
            {sc_prob*100:.1f}% PROBABILITY
        </div>
        <div style="font-size: 0.8rem; color: #94a3b8; margin-top: 4px;">Poisson expectation over {laps_remaining} remaining laps.</div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)
st.caption("🏎️ BOX BOX // Pit Wall Command Center. Built with FastF1 & LightGBM.")
