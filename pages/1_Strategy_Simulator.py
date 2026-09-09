"""
pages/1_Strategy_Simulator.py
------------------------------
High-performance interactive strategy simulator page for Box Box F1.
User inputs current race state -> AI runs Monte Carlo simulations
-> Shows ranked strategy recommendations with confidence scores.
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
import sys, os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from models.simulator import MonteCarloSimulator, RaceState, estimate_undercut, safety_car_probability
from models.tyre_model import TyreDegModel
from utils.ui_theme import inject_f1_theme, render_pit_wall_banner

# --- Page config ---
st.set_page_config(page_title="Strategy Simulator // BOX BOX", page_icon="🏎️", layout="wide")
inject_f1_theme()

COMPOUND_COLORS = {"SOFT": "#e10600", "MEDIUM": "#ffd600", "HARD": "#ffffff", "INTER": "#39b54a", "WET": "#0072bb"}
COMPOUND_CODES  = {"SOFT": 0, "MEDIUM": 1, "HARD": 2, "INTERMEDIATE": 3, "WET": 4}
COMPOUND_EMOJI  = {"SOFT": "🔴", "MEDIUM": "🟡", "HARD": "⚪"}

# --- Load model ---
@st.cache_resource
def load_model(circuit: str):
    """Try circuit-specific model, fall back to global."""
    if TyreDegModel.is_saved(circuit):
        return TyreDegModel.load(circuit)
    elif TyreDegModel.is_saved("global"):
        return TyreDegModel.load("global")
    else:
        return None

# --- Sidebar Controls ---
with st.sidebar:
    st.markdown("""
    <div style="display: flex; align-items: center; gap: 8px; margin-bottom: 0.5rem;">
        <span class="pit-wall-badge">TELEMETRY INPUT</span>
    </div>
    """, unsafe_allow_html=True)
    st.caption("Live Pit Wall Telemetry & Car State Parameters")

    circuit = st.selectbox("Grand Prix Circuit", [
        "Bahrain", "Britain", "Monza", "Spain",
        "Monaco", "Japan", "Austria", "Canada"
    ])

    st.markdown("---")
    st.markdown("**Stint Progress**")
    total_laps  = st.slider("Total Race Laps", min_value=30, max_value=78, value=57)
    current_lap = st.slider("Current Lap", min_value=1, max_value=total_laps - 3, value=28)

    st.markdown("---")
    st.markdown("**Tyre Telemetry**")
    compound     = st.selectbox("Current Compound On Car", ["SOFT", "MEDIUM", "HARD"], index=1)
    tyre_age     = st.slider("Tyre Age (Laps Completed)", min_value=1, max_value=40, value=18)
    new_compound = st.selectbox("Fitted Compound at Next Stop", ["HARD", "MEDIUM", "SOFT"], index=0)

    st.markdown("---")
    st.markdown("**Track Gaps & Intervals**")
    gap_ahead  = st.number_input("Gap to Car Ahead (seconds)", min_value=0.0, max_value=60.0, value=3.2, step=0.1)
    gap_behind = st.number_input("Gap to Car Behind (seconds)", min_value=0.0, max_value=60.0, value=1.9, step=0.1)

    st.markdown("---")
    st.markdown("**Environmental & Pit Loss**")
    pit_loss   = st.slider("Pit Lane Loss Delta (s)", min_value=17.0, max_value=32.0, value=22.5, step=0.5)
    track_temp = st.slider("Track Temperature (°C)", min_value=15, max_value=58, value=38)
    sc_base    = st.slider("Circuit Historical SC Risk (%)", min_value=5, max_value=75, value=35)

    n_sims = st.select_slider("Monte Carlo Iterations", options=[1_000, 5_000, 10_000, 20_000], value=10_000)
    run_btn = st.button("⚡ EXECUTE STRATEGY SIMULATION", type="primary", use_container_width=True)

# --- Top Banner ---
lap_str = f"LAP {current_lap} / {total_laps}"
render_pit_wall_banner(
    circuit=circuit,
    session_type="RACE STRATEGY COMPUTED",
    lap_str=lap_str,
    track_temp=f"{track_temp}°C",
    air_temp=f"{track_temp - 8}°C",
    sc_status="RACE ACTIVE"
)

# Build race state
state = RaceState(
    current_lap       = current_lap,
    total_laps        = total_laps,
    tyre_age          = tyre_age,
    compound_code     = COMPOUND_CODES[compound],
    gap_ahead         = gap_ahead,
    gap_behind        = gap_behind,
    pit_loss_time     = pit_loss,
    track_temp        = float(track_temp),
    air_temp          = float(track_temp) - 8,
)

laps_remaining = state.laps_remaining
sc_prob = safety_car_probability(sc_base / 100, laps_remaining, total_laps)

# --- Live Telemetry Row ---
m1, m2, m3, m4, m5, m6 = st.columns(6)
m1.metric("Current Lap", f"L{current_lap} / {total_laps}", delta=f"{laps_remaining} remaining", delta_color="off")
m2.metric("Tyre Compound", f"{compound}", delta=f"{tyre_age} laps old", delta_color="off")
m3.metric("Gap Ahead", f"+{gap_ahead:.1f}s", delta="Car in Front", delta_color="off")
m4.metric("Gap Behind", f"-{gap_behind:.1f}s", delta="Chasing Car", delta_color="off")
m5.metric("Pit Lane Loss", f"{pit_loss:.1f}s", delta="In-out delta", delta_color="off")
m6.metric("SC Likelihood", f"{sc_prob*100:.0f}%", delta="Historical prob", delta_color="off")

st.markdown("<br>", unsafe_allow_html=True)

# Compute Strategy
model = load_model(circuit)
simulator = MonteCarloSimulator(tyre_model=model, n_simulations=n_sims)
decisions = simulator.compute_best_strategy(state, new_compound=COMPOUND_CODES[new_compound])
undercut  = estimate_undercut(state)

best_decision = decisions[0] if decisions else None

# --- HERO CALLOUT: PIT CALL ---
if best_decision:
    is_box_now = "PIT_NOW" in best_decision.action
    box_header_color = "#e10600" if is_box_now else "#38bdf8"
    radio_call = "BOX BOX, BOX BOX! IN THIS LAP!" if is_box_now else f"STAY OUT // EXTEND STINT ({best_decision.action})"
    
    st.markdown(f"""
    <div class="call-to-pit-box">
        <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 10px;">
            <div>
                <div style="font-size: 0.8rem; font-weight: 800; color: #94a3b8; letter-spacing: 2px; text-transform: uppercase;">
                    📻 PIT WALL RADIO CALLOUT
                </div>
                <div style="font-size: 2.2rem; font-weight: 900; color: {box_header_color}; letter-spacing: 1px; line-height: 1.2; margin-top: 4px;">
                    {radio_call}
                </div>
            </div>
            <div style="text-align: right;">
                <div style="font-size: 0.8rem; color: #94a3b8; text-transform: uppercase; letter-spacing: 1px;">AI CONFIDENCE</div>
                <div style="font-size: 2.2rem; font-weight: 900; color: #00e676; font-family: 'JetBrains Mono', monospace;">
                    {best_decision.confidence * 100:.1f}%
                </div>
            </div>
        </div>
        <div style="margin-top: 1rem; padding-top: 1rem; border-top: 1px solid rgba(255,255,255,0.1); color: #cbd5e1; font-size: 0.95rem; line-height: 1.6;">
            <strong>Race Engineer Insight:</strong> {best_decision.reasoning}
        </div>
        <div style="display: flex; gap: 1.5rem; margin-top: 1rem; flex-wrap: wrap;" class="telemetry-font">
            <span style="background: rgba(0,0,0,0.4); padding: 6px 12px; border-radius: 6px; font-size: 0.85rem; border: 1px solid #1e293b;">
                OPTIMISTIC (P10): <strong style="color: #00e676;">{best_decision.p10_time:.1f}s</strong>
            </span>
            <span style="background: rgba(0,0,0,0.4); padding: 6px 12px; border-radius: 6px; font-size: 0.85rem; border: 1px solid #1e293b;">
                EXPECTED (P50): <strong style="color: #ffffff;">{best_decision.p50_time:.1f}s</strong>
            </span>
            <span style="background: rgba(0,0,0,0.4); padding: 6px 12px; border-radius: 6px; font-size: 0.85rem; border: 1px solid #1e293b;">
                PESSIMISTIC (P90): <strong style="color: #ff9800;">{best_decision.p90_time:.1f}s</strong>
            </span>
            <span style="background: rgba(0,0,0,0.4); padding: 6px 12px; border-radius: 6px; font-size: 0.85rem; border: 1px solid #1e293b;">
                NEW COMPOUND: <strong style="color: {COMPOUND_COLORS.get(best_decision.recommended_compound, '#fff')};">● {best_decision.recommended_compound}</strong>
            </span>
        </div>
    </div>
    """, unsafe_allow_html=True)

# --- Ranked Strategy Candidates ---
st.markdown("### 📋 Ranked Candidate Strategies")

strat_cols = st.columns(len(decisions))
for i, (col, d) in enumerate(zip(strat_cols, decisions)):
    comp_col = COMPOUND_COLORS.get(d.recommended_compound, "#fff")
    is_rec = d.is_recommended
    border_col = "#e10600" if is_rec else "#1e293b"
    bg_col = "rgba(225, 6, 0, 0.08)" if is_rec else "#121620"
    badge_label = "RECOMMENDED" if is_rec else f"DELTA +{d.expected_time_loss:.1f}s"
    badge_color = "#00e676" if is_rec else "#94a3b8"

    col.markdown(f"""
    <div style="background: {bg_col}; border: 1px solid {border_col}; border-radius: 10px; padding: 1.2rem; height: 100%; box-shadow: 0 4px 12px rgba(0,0,0,0.3);">
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.5rem;">
            <span style="font-weight: 800; color: {'#e10600' if is_rec else '#cbd5e1'}; font-size: 1.05rem;">
                {d.action.replace('_', ' ')}
            </span>
            <span style="font-size: 0.75rem; font-weight: 800; color: {badge_color};">
                {badge_label}
            </span>
        </div>
        <div style="font-size: 0.85rem; color: #94a3b8; margin-bottom: 0.75rem;">
            FITTING: <strong style="color: {comp_col};">● {d.recommended_compound}</strong>
        </div>
        <div style="font-size: 0.82rem; color: #94a3b8; line-height: 1.4; margin-bottom: 0.8rem;">
            {d.reasoning}
        </div>
        <div style="border-top: 1px solid rgba(255,255,255,0.06); padding-top: 0.6rem; font-size: 0.8rem;" class="telemetry-font">
            <div>MEDIAN TIME: <strong style="color: #fff;">{d.p50_time:.1f}s</strong></div>
            <div>CONFIDENCE: <strong style="color: #38bdf8;">{d.confidence*100:.0f}%</strong></div>
        </div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("<br><br>", unsafe_allow_html=True)

# --- Charts Row ---
col_ch1, col_ch2 = st.columns(2)

with col_ch1:
    st.markdown("#### ⏱️ Strategy Race Time Uncertainty (P10 / P50 / P90)")
    fig_time = go.Figure()
    for d in decisions:
        fig_time.add_trace(go.Bar(
            name=d.action,
            x=[d.action.replace('_', ' ')],
            y=[d.p50_time],
            error_y=dict(
                type="data",
                array=[d.p90_time - d.p50_time],
                arrayminus=[d.p50_time - d.p10_time],
                visible=True,
                color="#94a3b8",
                thickness=2,
            ),
            marker=dict(
                color="#e10600" if d.is_recommended else "#1e293b",
                line=dict(color="#ff3b30" if d.is_recommended else "#334155", width=1.5)
            ),
            showlegend=False,
        ))
    fig_time.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(18, 22, 32, 0.7)",
        font=dict(color="#cbd5e1", family="Titillium Web"),
        height=320,
        margin=dict(l=20, r=20, t=15, b=20),
        xaxis=dict(showgrid=False, color="#94a3b8"),
        yaxis=dict(showgrid=True, gridcolor="rgba(255,255,255,0.06)", color="#94a3b8", title="Total Race Seconds"),
    )
    st.plotly_chart(fig_time, use_container_width=True)

with col_ch2:
    st.markdown("#### 📉 Pirelli Tyre Degradation Curves")
    ages = list(range(1, 41))
    traces = []
    
    if model and model.is_trained:
        for comp_name, comp_code in [("SOFT", 0), ("MEDIUM", 1), ("HARD", 2)]:
            times = []
            for age in ages:
                pred = model.predict_lap_time(comp_code, age, float(track_temp) - 8, float(track_temp))
                times.append(pred["p50"])
            traces.append((comp_name, ages, times))
    else:
        deg = {0: 0.082, 1: 0.046, 2: 0.024}
        base = 90.0
        traces = [
            ("SOFT",   ages, [base + deg[0] * a for a in ages]),
            ("MEDIUM", ages, [base + deg[1] * a for a in ages]),
            ("HARD",   ages, [base + deg[2] * a for a in ages]),
        ]

    fig_deg = go.Figure()
    for comp_name, x, y in traces:
        fig_deg.add_trace(go.Scatter(
            x=x, y=y, name=comp_name,
            line=dict(color=COMPOUND_COLORS[comp_name], width=3),
            mode="lines"
        ))
    
    fig_deg.add_vline(
        x=tyre_age, line_dash="dash", line_color="#e10600", line_width=2,
        annotation_text=f"Current: Lap {tyre_age}",
        annotation_position="top right",
        annotation_font_color="#e10600"
    )

    fig_deg.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(18, 22, 32, 0.7)",
        font=dict(color="#cbd5e1", family="Titillium Web"),
        height=320,
        margin=dict(l=20, r=20, t=15, b=20),
        xaxis=dict(showgrid=True, gridcolor="rgba(255,255,255,0.06)", color="#94a3b8", title="Tyre Age (Laps)"),
        yaxis=dict(showgrid=True, gridcolor="rgba(255,255,255,0.06)", color="#94a3b8", title="Lap Time (s)"),
        legend=dict(bgcolor="rgba(10, 14, 22, 0.8)", bordercolor="rgba(255,255,255,0.1)"),
    )
    st.plotly_chart(fig_deg, use_container_width=True)

# --- Tactical Undercut & Probability Breakdown ---
st.markdown("---")
st.markdown("### ⚔️ Tactical Undercut / Overcut & Race Control Analysis")

u1, u2, u3 = st.columns(3)
with u1:
    viable = undercut["viable"]
    color  = "#00e676" if viable else "#e10600"
    st.markdown(f"""
    <div style="background: #121620; border: 1px solid {color}; border-radius: 10px; padding: 1.25rem;">
        <div style="color: #94a3b8; font-size: 0.75rem; text-transform: uppercase; letter-spacing: 1px;">UNDERCUT VIABILITY</div>
        <div style="color: {color}; font-size: 1.8rem; font-weight: 900; margin-top: 4px;">
            {"✓ FEASIBLE" if viable else "✗ HIGH RISK / NOT VIABLE"}
        </div>
        <div style="color: #cbd5e1; font-size: 0.85rem; margin-top: 6px;">
            {undercut['recommendation']}
        </div>
    </div>
    """, unsafe_allow_html=True)

with u2:
    ltr = undercut.get("laps_to_recover")
    st.markdown(f"""
    <div style="background: #121620; border: 1px solid #1e293b; border-radius: 10px; padding: 1.25rem;">
        <div style="color: #94a3b8; font-size: 0.75rem; text-transform: uppercase; letter-spacing: 1px;">LAPS TO OVERTURN GAP</div>
        <div style="color: #ffffff; font-size: 1.8rem; font-weight: 900; margin-top: 4px;" class="telemetry-font">
            {f"{ltr:.1f} LAPS" if ltr else "OVERCUT / DEFEND"}
        </div>
        <div style="color: #94a3b8; font-size: 0.85rem; margin-top: 6px;">
            Based on {pit_loss:.1f}s pit loss vs delta degradation pace.
        </div>
    </div>
    """, unsafe_allow_html=True)

with u3:
    sc_text_color = "#00e676" if sc_prob < 0.25 else ("#ffd600" if sc_prob < 0.5 else "#e10600")
    st.markdown(f"""
    <div style="background: #121620; border: 1px solid #1e293b; border-radius: 10px; padding: 1.25rem;">
        <div style="color: #94a3b8; font-size: 0.75rem; text-transform: uppercase; letter-spacing: 1px;">SAFETY CAR RISK WINDOW</div>
        <div style="color: {sc_text_color}; font-size: 1.8rem; font-weight: 900; margin-top: 4px;" class="telemetry-font">
            {sc_prob*100:.1f}% PROBABILITY
        </div>
        <div style="color: #94a3b8; font-size: 0.85rem; margin-top: 6px;">
            Poisson expectation over remaining {laps_remaining} laps.
        </div>
    </div>
    """, unsafe_allow_html=True)

# Monte Carlo Overlap Distribution
if len(decisions) >= 2:
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("#### 📊 Monte Carlo Outcome Density: Best Call vs 2nd Option")
    best   = decisions[0]
    second = decisions[1]
    n_plot = 2_500

    sim_best   = np.random.normal(best.p50_time, (best.p90_time - best.p10_time) / 2.56, n_plot)
    sim_second = np.random.normal(second.p50_time, (second.p90_time - second.p10_time) / 2.56, n_plot)

    fig_dist = go.Figure()
    fig_dist.add_trace(go.Histogram(
        x=sim_best, name=f"1st: {best.action.replace('_', ' ')}", nbinsx=60,
        marker_color="#e10600", opacity=0.75,
    ))
    fig_dist.add_trace(go.Histogram(
        x=sim_second, name=f"2nd: {second.action.replace('_', ' ')}", nbinsx=60,
        marker_color="#38bdf8", opacity=0.55,
    ))
    fig_dist.update_layout(
        barmode="overlay",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(18, 22, 32, 0.7)",
        font=dict(color="#cbd5e1", family="Titillium Web"),
        height=260,
        margin=dict(l=20, r=20, t=15, b=20),
        xaxis=dict(title="Race Elapsed Time (Seconds)", color="#94a3b8", showgrid=True, gridcolor="rgba(255,255,255,0.06)"),
        yaxis=dict(title="Iteration Count", color="#94a3b8", showgrid=True, gridcolor="rgba(255,255,255,0.06)"),
        legend=dict(bgcolor="rgba(10, 14, 22, 0.8)", bordercolor="rgba(255,255,255,0.1)"),
    )
    st.plotly_chart(fig_dist, use_container_width=True)

st.markdown("---")
st.caption("🏎️ BOX BOX // Built with FastF1 & LightGBM. Not affiliated with Formula One Management.")
