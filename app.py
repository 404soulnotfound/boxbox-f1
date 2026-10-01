"""
app.py
------
Homepage for Box Box — F1 AI Race Strategist.
Timing Screen Terminal theme.
"""

import streamlit as st
import sys, os
sys.path.insert(0, os.path.dirname(__file__))

from models.tyre_model import TyreDegModel
from utils.ui_theme import inject_f1_theme, render_pit_wall_banner

st.set_page_config(
    page_title="BOX BOX // F1 STRATEGY ENGINE",
    page_icon="🏎️",
    layout="wide",
    initial_sidebar_state="expanded",
)

inject_f1_theme()

# ─── Timing Header ───────────────────────────────────────────────────────────
render_pit_wall_banner(
    circuit="All Circuits",
    session_type="SYSTEM READY",
    lap_str="AWAITING INPUT",
    track_temp="--.-°C",
    air_temp="--.-°C",
    sc_status="TRACK CLEAR"
)

# ─── Hero ─────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="hero-container">
    <div class="hero-tag">// FORMULA 1 AI STRATEGY ENGINE — TIMING SCREEN TERMINAL</div>
    <div class="hero-title">BOX BOX F1</div>
    <div class="hero-sub">
        > REAL FastF1 TELEMETRY  ·  LightGBM QUANTILE REGRESSION  ·  10,000-RUN MONTE CARLO  ·  ALL 22 CIRCUITS<br>
        > ENTER RACE STATE → GET RANKED PIT STRATEGIES WITH CONFIDENCE SCORES IN &lt;200ms
    </div>
</div>
""", unsafe_allow_html=True)

# ─── ML Model Status ──────────────────────────────────────────────────────────
st.markdown("""
<p class="section-title">// SYSTEM STATUS · ML MODEL WEIGHTS</p>
""", unsafe_allow_html=True)

circuits_to_check = ["Bahrain", "Britain", "Monza", "Spain", "Monaco", "global"]
any_model = False
status_cols = st.columns(len(circuits_to_check))

for col, circuit in zip(status_cols, circuits_to_check):
    saved = TyreDegModel.is_saved(circuit)
    if saved:
        any_model = True
    status_txt  = "● ONLINE" if saved else "○ DEMO MODE"
    status_color = "#00ff87" if saved else "#ffd600"
    col.markdown(f"""
    <div style="background: #000; border: 1px solid {'#00ff87' if saved else '#1a4a30'};
                border-top: 2px solid {'#00ff87' if saved else '#e10600'};
                padding: 0.7rem 0.5rem; text-align: center; font-family: 'Share Tech Mono', monospace;">
        <div style="font-size: 0.65rem; color: #2a9960; text-transform: uppercase;
                    letter-spacing: 1.5px; margin-bottom: 4px;">{circuit.upper()}</div>
        <div style="font-size: 0.8rem; color: {status_color}; font-weight: 700;">{status_txt}</div>
    </div>""", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

if not any_model:
    st.info(
        "// DEMO MODE ACTIVE: Calibrated circuit profiles loaded for all 22 circuits. "
        "Head to Tyre Analysis to train live LightGBM models on real FastF1 data."
    )
else:
    st.success("// ACTIVE AI WEIGHTS DETECTED — HIGH-PRECISION MODE ENABLED")

st.markdown("---")

# ─── Module Grid ─────────────────────────────────────────────────────────────
st.markdown("""
<p class="section-title">// RACE ENGINEER CORE MODULES</p>
""", unsafe_allow_html=True)

fc1, fc2, fc3 = st.columns(3)
features = [
    ("01", "STRATEGY SIMULATOR",
     "Input live race state. AI runs 10,000 Monte Carlo sims across Pit Now / +3 / +5 / Stay Out strategies. Returns ranked decisions with P10/P50/P90 race time bounds.",
     "#e10600"),
    ("02", "TYRE ANALYSIS",
     "Load real FastF1 GP data. Train LightGBM quantile regression model on fuel-corrected lap times per compound. View degradation curves and driver stint maps.",
     "#00ff87"),
    ("03", "STRATEGY BACKTEST",
     "Select any historical GP. Replay lap-by-lap. Compare AI pit recommendations vs actual team decisions. Quantify seconds gained or lost.",
     "#ffd600"),
    ("04", "CIRCUIT COMPARE",
     "Side-by-side tyre degradation profiles for any two circuits from the full 22-circuit calendar. SC probability, pit loss delta, deg rate per compound.",
     "#38bdf8"),
    ("05", "UNDERCUT / OVERCUT",
     "Real-time viability check: can fresh rubber recover the 22s pit loss before the race ends? Poisson safety car probability window included.",
     "#00ff87"),
    ("06", "LIVE TELEMETRY",
     "FastF1 API integration with automatic fallback to calibrated demo data on cloud environments. Never crashes — always returns data.",
     "#e10600"),
]

for i, (num, title, desc, color) in enumerate(features):
    col = [fc1, fc2, fc3][i % 3]
    col.markdown(f"""
    <div style="background: #000; border: 1px solid #1a4a30;
                border-left: 3px solid {color};
                padding: 1.1rem; margin-bottom: 1rem; min-height: 160px;
                font-family: 'Share Tech Mono', monospace;">
        <div style="display: flex; justify-content: space-between; margin-bottom: 6px;">
            <span style="color: {color}; font-size: 0.7rem; letter-spacing: 2px;">// MODULE {num}</span>
        </div>
        <div style="font-family: 'Orbitron', monospace; color: #ffffff;
                    font-size: 0.85rem; font-weight: 700; margin-bottom: 8px;
                    letter-spacing: 1.5px;">{title}</div>
        <div style="color: #2a9960; font-size: 0.78rem; line-height: 1.6;">{desc}</div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("---")

# ─── Workflow ─────────────────────────────────────────────────────────────────
st.markdown("""
<p class="section-title">// RACE WEEKEND EXECUTION SEQUENCE</p>
""", unsafe_allow_html=True)

w1, w2, w3, w4 = st.columns(4)
steps = [
    ("01", "TELEMETRY INGESTION",  "Fetch historical race laps via FastF1 API with fuel burn correction applied."),
    ("02", "MODEL CALIBRATION",    "Train LightGBM quantile estimators on per-compound tyre degradation curves."),
    ("03", "MONTE CARLO SWEEP",    "Evaluate 10,000 stochastic race futures: pit now vs +3 vs +5 vs stay out."),
    ("04", "STRATEGY CALLOUT",     "Receive BOX BOX or STAY OUT with P10/P50/P90 time bounds and confidence score."),
]
for col, (num, title, desc) in zip([w1, w2, w3, w4], steps):
    col.markdown(f"""
    <div style="background: #000; border: 1px solid #1a4a30; border-top: 2px solid #e10600;
                padding: 1rem; height: 100%; font-family: 'Share Tech Mono', monospace;">
        <div style="font-family: 'Orbitron', monospace; font-size: 1.3rem;
                    color: #e10600; font-weight: 900; margin-bottom: 6px;">{num}</div>
        <div style="color: #ffffff; font-size: 0.8rem; font-weight: 700;
                    letter-spacing: 1px; margin-bottom: 6px;">{title}</div>
        <div style="color: #2a9960; font-size: 0.76rem; line-height: 1.55;">{desc}</div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("<br><br>---", unsafe_allow_html=True)

# ─── Footer ───────────────────────────────────────────────────────────────────
st.markdown("""
<div style="text-align: center; font-family: 'Share Tech Mono', monospace;
            color: #2a9960; font-size: 0.78rem; padding: 1rem 0;">
    BOX BOX // F1 AI RACE STRATEGY ENGINE &nbsp;·&nbsp; ENGINEERED BY
    <strong style="color: #00ff87;">SOUMILI PAL</strong><br>
    <span style="margin-top: 0.4rem; display: inline-block; font-size: 0.72rem;">
        <a href="https://github.com/404soulnotfound" target="_blank"
           style="color: #00ff87; text-decoration: none;">[ GITHUB ]</a>
        &nbsp;·&nbsp;
        <a href="https://www.linkedin.com/in/soumilipal" target="_blank"
           style="color: #00ff87; text-decoration: none;">[ LINKEDIN ]</a>
        &nbsp;·&nbsp;
        <a href="mailto:tidha427@gmail.com"
           style="color: #00ff87; text-decoration: none;">[ EMAIL ]</a>
    </span><br>
    <span style="font-size: 0.68rem; color: #1a4a30; margin-top: 4px; display: inline-block;">
        NOT AFFILIATED WITH FORMULA ONE MANAGEMENT OR THE FIA
    </span>
</div>
""", unsafe_allow_html=True)
