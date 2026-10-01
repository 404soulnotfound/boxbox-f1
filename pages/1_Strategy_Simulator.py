"""
pages/1_Strategy_Simulator.py
------------------------------
Strategy Simulator — Timing Screen Terminal theme.
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
from utils.ui_theme import inject_f1_theme, render_pit_wall_banner

st.set_page_config(page_title="Strategy Simulator // BOX BOX", page_icon="🏎️", layout="wide")
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

# ─── Sidebar ──────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div style="font-family:'Share Tech Mono',monospace; color:#e10600;
                font-size:0.75rem; letter-spacing:2px; border-bottom:1px solid #e10600;
                padding-bottom:8px; margin-bottom:12px;">
        // TELEMETRY INPUT PANEL
    </div>
    """, unsafe_allow_html=True)

    circuit = st.selectbox("CIRCUIT", ALL_CIRCUITS, index=0)

    st.markdown("<div style='border-top:1px solid #1a4a30; margin: 10px 0;'></div>", unsafe_allow_html=True)
    st.markdown("<span style='font-family:Share Tech Mono,monospace;font-size:0.7rem;color:#e10600;letter-spacing:2px;'>// STINT</span>", unsafe_allow_html=True)
    total_laps  = st.slider("TOTAL LAPS", min_value=30, max_value=78, value=57)
    current_lap = st.slider("CURRENT LAP", min_value=1, max_value=total_laps - 3, value=28)

    st.markdown("<div style='border-top:1px solid #1a4a30; margin: 10px 0;'></div>", unsafe_allow_html=True)
    st.markdown("<span style='font-family:Share Tech Mono,monospace;font-size:0.7rem;color:#e10600;letter-spacing:2px;'>// TYRE</span>", unsafe_allow_html=True)
    compound     = st.selectbox("COMPOUND ON CAR", ["SOFT", "MEDIUM", "HARD"], index=1)
    tyre_age     = st.slider("TYRE AGE (LAPS)", min_value=1, max_value=40, value=18)
    new_compound = st.selectbox("NEXT COMPOUND", ["HARD", "MEDIUM", "SOFT"], index=0)

    st.markdown("<div style='border-top:1px solid #1a4a30; margin: 10px 0;'></div>", unsafe_allow_html=True)
    st.markdown("<span style='font-family:Share Tech Mono,monospace;font-size:0.7rem;color:#e10600;letter-spacing:2px;'>// GAPS</span>", unsafe_allow_html=True)
    gap_ahead  = st.number_input("GAP AHEAD (s)", min_value=0.0, max_value=60.0, value=3.2, step=0.1)
    gap_behind = st.number_input("GAP BEHIND (s)", min_value=0.0, max_value=60.0, value=1.9, step=0.1)

    st.markdown("<div style='border-top:1px solid #1a4a30; margin: 10px 0;'></div>", unsafe_allow_html=True)
    st.markdown("<span style='font-family:Share Tech Mono,monospace;font-size:0.7rem;color:#e10600;letter-spacing:2px;'>// CONDITIONS</span>", unsafe_allow_html=True)
    pit_loss   = st.slider("PIT LANE LOSS (s)", min_value=17.0, max_value=32.0, value=22.5, step=0.5)
    track_temp = st.slider("TRACK TEMP (°C)", min_value=15, max_value=58, value=38)
    sc_base    = st.slider("SC RISK FACTOR (%)", min_value=5, max_value=75, value=35)
    n_sims     = st.select_slider("MC ITERATIONS", options=[1_000, 5_000, 10_000, 20_000], value=10_000)

    run_btn = st.button("⚡ EXECUTE SIMULATION", type="primary", use_container_width=True)

# ─── Header ───────────────────────────────────────────────────────────────────
render_pit_wall_banner(
    circuit=circuit,
    session_type="STRATEGY SIMULATION",
    lap_str=f"LAP {current_lap} / {total_laps}",
    track_temp=f"{track_temp}°C",
    air_temp=f"{track_temp - 8}°C",
    sc_status="RACE ACTIVE"
)

# ─── Hero ─────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="hero-container">
    <div class="hero-tag">// MODULE 01 · PIT STOP STRATEGY OPTIMIZER</div>
    <div class="hero-title">STRATEGY SIMULATOR</div>
    <div class="hero-sub">
        > INPUT RACE STATE → 10,000 MONTE CARLO SIMS → RANKED STRATEGY OUTPUT IN &lt;200ms<br>
        > COMPOUND: SOFT / MEDIUM / HARD · ALL 22 F1 CALENDAR CIRCUITS
    </div>
</div>
""", unsafe_allow_html=True)

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
    air_temp      = float(track_temp) - 8,
)

laps_remaining = state.laps_remaining
sc_prob = safety_car_probability(sc_base / 100, laps_remaining, total_laps)

# ─── Telemetry Row ────────────────────────────────────────────────────────────
m1, m2, m3, m4, m5, m6 = st.columns(6)
m1.metric("LAP",        f"L{current_lap}/{total_laps}",  delta=f"{laps_remaining} left", delta_color="off")
m2.metric("COMPOUND",   compound,                         delta=f"{tyre_age} laps",       delta_color="off")
m3.metric("GAP AHEAD",  f"+{gap_ahead:.1f}s",            delta="Car ahead",              delta_color="off")
m4.metric("GAP BEHIND", f"-{gap_behind:.1f}s",           delta="Car behind",             delta_color="off")
m5.metric("PIT LOSS",   f"{pit_loss:.1f}s",              delta="Delta",                  delta_color="off")
m6.metric("SC RISK",    f"{sc_prob*100:.0f}%",           delta="Historical",             delta_color="off")

st.markdown("<br>", unsafe_allow_html=True)

# ─── Run Simulation ───────────────────────────────────────────────────────────
model     = load_model(circuit)
simulator = MonteCarloSimulator(tyre_model=model, n_simulations=n_sims)
decisions = simulator.compute_best_strategy(state, new_compound=COMPOUND_CODES[new_compound])
undercut  = estimate_undercut(state)
best      = decisions[0] if decisions else None

# ─── Primary Call-to-Pit ─────────────────────────────────────────────────────
if best:
    is_box_now  = "PIT_NOW" in best.action
    call_color  = "#e10600" if is_box_now else "#00ff87"
    radio_call  = "BOX BOX, BOX BOX! IN THIS LAP!" if is_box_now else f"STAY OUT // {best.action.replace('_', ' ')}"

    st.markdown(f"""
    <div class="call-to-pit-box">
        <div style="display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:12px;">
            <div>
                <div style="font-family:'Share Tech Mono',monospace; font-size:0.7rem;
                            color:#2a9960; letter-spacing:3px; margin-bottom:6px;">
                    // PIT WALL RADIO CALLOUT
                </div>
                <div style="font-family:'Orbitron',monospace; font-size:1.8rem;
                            font-weight:900; color:{call_color}; letter-spacing:2px;
                            text-shadow: 0 0 20px {call_color}40;">
                    {radio_call}
                </div>
            </div>
            <div style="text-align:right;">
                <div style="font-family:'Share Tech Mono',monospace; font-size:0.7rem;
                            color:#2a9960; letter-spacing:2px;">AI CONFIDENCE</div>
                <div style="font-family:'Orbitron',monospace; font-size:2rem;
                            font-weight:900; color:#00ff87;
                            text-shadow: 0 0 16px rgba(0,255,135,0.5);">
                    {best.confidence * 100:.1f}%
                </div>
            </div>
        </div>
        <div style="margin-top:1rem; padding-top:0.9rem;
                    border-top:1px solid rgba(0,255,135,0.15);
                    font-family:'Share Tech Mono',monospace; font-size:0.8rem;
                    color:#2a9960; line-height:1.7;">
            > {best.reasoning}
        </div>
        <div style="display:flex; gap:12px; margin-top:0.9rem; flex-wrap:wrap;
                    font-family:'Share Tech Mono',monospace; font-size:0.78rem;">
            <span style="border:1px solid #1a4a30; padding:4px 10px;">
                P10 <strong style="color:#00ff87;">{best.p10_time:.1f}s</strong>
            </span>
            <span style="border:1px solid #1a4a30; padding:4px 10px;">
                P50 <strong style="color:#ffffff;">{best.p50_time:.1f}s</strong>
            </span>
            <span style="border:1px solid #1a4a30; padding:4px 10px;">
                P90 <strong style="color:#ffd600;">{best.p90_time:.1f}s</strong>
            </span>
            <span style="border:1px solid {COMPOUND_COLORS.get(best.recommended_compound,'#fff')}40;
                         padding:4px 10px; color:{COMPOUND_COLORS.get(best.recommended_compound,'#fff')};">
                ● {best.recommended_compound}
            </span>
        </div>
    </div>
    """, unsafe_allow_html=True)

# ─── Candidate Strategy Rows ──────────────────────────────────────────────────
st.markdown("""
<p class="section-title">// RANKED CANDIDATE STRATEGIES</p>
""", unsafe_allow_html=True)

# Render as a timing-screen style table
st.markdown("""
<div class="timing-row header">
    <div>RNK</div>
    <div>ACTION</div>
    <div>COMPOUND</div>
    <div>CONFIDENCE</div>
    <div>P10</div>
    <div>P50 (MEDIAN)</div>
    <div>P90</div>
</div>
""", unsafe_allow_html=True)

for i, d in enumerate(decisions):
    comp_col  = COMPOUND_COLORS.get(d.recommended_compound, "#fff")
    rank_col  = "#e10600" if i == 0 else "#00ff87" if i == 1 else "#2a9960"
    action_lbl = d.action.replace("_", " ")
    badge     = "★ OPTIMAL" if d.is_recommended else f"+{d.expected_time_loss:.1f}s"

    st.markdown(f"""
    <div class="timing-row" style="{'border-left: 3px solid #e10600;' if i==0 else ''}">
        <div class="timing-pos">#{i+1}</div>
        <div style="font-family:'Share Tech Mono',monospace; color:#fff; font-weight:700;">
            {action_lbl}
            <span style="font-size:0.7rem; color:{rank_col}; margin-left:8px;">{badge}</span>
        </div>
        <div style="color:{comp_col}; font-weight:700; font-family:'Share Tech Mono',monospace;">
            ● {d.recommended_compound}
        </div>
        <div style="color:#00ff87; font-family:'Share Tech Mono',monospace; font-weight:700;">
            {d.confidence*100:.0f}%
        </div>
        <div style="color:#00ff87; font-family:'Share Tech Mono',monospace;">{d.p10_time:.1f}s</div>
        <div style="color:#fff;   font-family:'Share Tech Mono',monospace; font-weight:700;">{d.p50_time:.1f}s</div>
        <div style="color:#ffd600;font-family:'Share Tech Mono',monospace;">{d.p90_time:.1f}s</div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ─── Charts ───────────────────────────────────────────────────────────────────
col_ch1, col_ch2 = st.columns(2)

CHART_LAYOUT = dict(
    paper_bgcolor="#000000",
    plot_bgcolor="#000000",
    font=dict(color="#00ff87", family="Share Tech Mono"),
    height=320,
    margin=dict(l=20, r=20, t=30, b=20),
    xaxis=dict(showgrid=True, gridcolor="rgba(0,255,135,0.07)", color="#2a9960", linecolor="#1a4a30"),
    yaxis=dict(showgrid=True, gridcolor="rgba(0,255,135,0.07)", color="#2a9960", linecolor="#1a4a30"),
)

with col_ch1:
    st.markdown("""<p class="section-title" style="font-size:0.72rem;">// STRATEGY RACE TIME · P10/P50/P90</p>""", unsafe_allow_html=True)
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
                visible=True, color="#2a9960", thickness=2,
            ),
            marker=dict(
                color="rgba(225,6,0,0.7)" if d.is_recommended else "rgba(0,255,135,0.15)",
                line=dict(color="#e10600" if d.is_recommended else "#1a4a30", width=1.5)
            ),
            showlegend=False,
        ))
    layout = {**CHART_LAYOUT}
    layout["yaxis"] = dict(**layout["yaxis"], title="Total Race Seconds")
    fig_time.update_layout(**layout)
    st.plotly_chart(fig_time, use_container_width=True)

with col_ch2:
    st.markdown("""<p class="section-title" style="font-size:0.72rem;">// TYRE DEGRADATION CURVES</p>""", unsafe_allow_html=True)
    ages = list(range(1, 41))
    traces = []
    if model and model.is_trained:
        for comp_name, comp_code in [("SOFT", 0), ("MEDIUM", 1), ("HARD", 2)]:
            times = [model.predict_lap_time(comp_code, a, float(track_temp)-8, float(track_temp))["p50"] for a in ages]
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
    layout2 = {**CHART_LAYOUT}
    layout2["xaxis"] = dict(**layout2["xaxis"], title="Tyre Age (Laps)")
    layout2["yaxis"] = dict(**layout2["yaxis"], title="Lap Time (s)")
    layout2["legend"] = dict(bgcolor="#000", bordercolor="#1a4a30")
    fig_deg.update_layout(**layout2)
    st.plotly_chart(fig_deg, use_container_width=True)

# ─── Tactical Panel ───────────────────────────────────────────────────────────
st.markdown("---")
st.markdown("""<p class="section-title">// TACTICAL ANALYSIS · UNDERCUT / SC WINDOW</p>""", unsafe_allow_html=True)

u1, u2, u3 = st.columns(3)
with u1:
    viable = undercut["viable"]
    color  = "#00ff87" if viable else "#e10600"
    st.markdown(f"""
    <div class="terminal-panel">
        <div class="t-dim">// UNDERCUT VIABILITY</div>
        <div style="font-family:'Orbitron',monospace; font-size:1.3rem;
                    color:{color}; font-weight:900; margin: 8px 0;
                    text-shadow: 0 0 12px {color}60;">
            {"✓ FEASIBLE" if viable else "✗ HIGH RISK"}
        </div>
        <div class="t-dim" style="font-size:0.78rem;">{undercut["recommendation"]}</div>
    </div>
    """, unsafe_allow_html=True)

with u2:
    ltr = undercut.get("laps_to_recover")
    st.markdown(f"""
    <div class="terminal-panel">
        <div class="t-dim">// LAPS TO OVERTURN GAP</div>
        <div style="font-family:'Orbitron',monospace; font-size:1.3rem;
                    color:#fff; font-weight:900; margin: 8px 0;">
            {f"{ltr:.1f} LAPS" if ltr else "OVERCUT / DEFEND"}
        </div>
        <div class="t-dim" style="font-size:0.78rem;">
            Based on {pit_loss:.1f}s pit loss vs deg pace delta.
        </div>
    </div>
    """, unsafe_allow_html=True)

with u3:
    sc_text_color = "#00ff87" if sc_prob < 0.25 else ("#ffd600" if sc_prob < 0.5 else "#e10600")
    st.markdown(f"""
    <div class="terminal-panel">
        <div class="t-dim">// SAFETY CAR RISK WINDOW</div>
        <div style="font-family:'Orbitron',monospace; font-size:1.3rem;
                    color:{sc_text_color}; font-weight:900; margin: 8px 0;
                    text-shadow: 0 0 12px {sc_text_color}60;">
            {sc_prob*100:.1f}% PROBABILITY
        </div>
        <div class="t-dim" style="font-size:0.78rem;">
            Poisson model · {laps_remaining} laps remaining.
        </div>
    </div>
    """, unsafe_allow_html=True)

# ─── MC Distribution ──────────────────────────────────────────────────────────
if len(decisions) >= 2:
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("""<p class="section-title">// MONTE CARLO OUTCOME DENSITY · BEST vs 2ND</p>""", unsafe_allow_html=True)
    best_d   = decisions[0]
    second_d = decisions[1]
    n_plot   = 2_500

    sim_best   = np.random.normal(best_d.p50_time,   (best_d.p90_time   - best_d.p10_time) / 2.56, n_plot)
    sim_second = np.random.normal(second_d.p50_time, (second_d.p90_time - second_d.p10_time) / 2.56, n_plot)

    fig_dist = go.Figure()
    fig_dist.add_trace(go.Histogram(
        x=sim_best,   name=f"#1 {best_d.action.replace('_',' ')}",   nbinsx=60,
        marker_color="rgba(225,6,0,0.7)", opacity=0.8,
    ))
    fig_dist.add_trace(go.Histogram(
        x=sim_second, name=f"#2 {second_d.action.replace('_',' ')}", nbinsx=60,
        marker_color="rgba(0,255,135,0.4)", opacity=0.7,
    ))
    layout3 = {**CHART_LAYOUT}
    layout3["barmode"] = "overlay"
    layout3["xaxis"] = dict(**layout3["xaxis"], title="Race Elapsed Time (s)")
    layout3["yaxis"] = dict(**layout3["yaxis"], title="Iteration Count")
    layout3["legend"] = dict(bgcolor="#000", bordercolor="#1a4a30")
    layout3["height"] = 260
    fig_dist.update_layout(**layout3)
    st.plotly_chart(fig_dist, use_container_width=True)

st.markdown("---")
st.markdown("""
<div style="font-family:'Share Tech Mono',monospace; font-size:0.72rem; color:#1a4a30;">
    BOX BOX F1 // BUILT WITH FASTF1 &amp; LIGHTGBM · NOT AFFILIATED WITH FORMULA ONE MANAGEMENT
</div>
""", unsafe_allow_html=True)
