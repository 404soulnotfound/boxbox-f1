"""
app.py
------
Homepage for Box Box — F1 AI Race Strategist.
Option A: Pit Wall Command Center theme.
"""

import streamlit as st
import sys, os
sys.path.insert(0, os.path.dirname(__file__))

from models.tyre_model import TyreDegModel
from utils.ui_theme import inject_f1_theme, render_pit_wall_banner, render_compound_badges_selector

st.set_page_config(
    page_title="BOX BOX // F1 Pit Wall Command Center",
    page_icon="🏎️",
    layout="wide",
    initial_sidebar_state="expanded",
)

inject_f1_theme()

# ─── Top Broadcast Ticker Bar (Option A) ──────────────────────────────────────
render_pit_wall_banner(
    circuit="Bahrain International",
    session_type="PIT WALL COMMAND ONLINE",
    lap_str="READY FOR TELEMETRY",
    leader_delta="TELEMETRY SYNCED",
    sc_status="TRACK CLEAR - GREEN",
    weather_str="DRY (28°C)"
)

# ─── Hero Section ─────────────────────────────────────────────────────────────
st.markdown("""
<div style="background: linear-gradient(135deg, rgba(20,24,34,0.95) 0%, rgba(10,12,16,0.98) 100%);
            border: 1px solid #1e2638; border-top: 3px solid #e10600; border-radius: 8px;
            padding: 2rem 2.2rem; margin-bottom: 1.5rem; box-shadow: 0 12px 30px rgba(0,0,0,0.5);">
    <div style="font-size: 0.8rem; font-weight: 800; color: #e10600; letter-spacing: 2px; text-transform: uppercase;">
        FORMULA 1 AI STRATEGY INTELLIGENCE
    </div>
    <div style="font-size: 2.6rem; font-weight: 900; color: #ffffff; letter-spacing: 1px; margin: 6px 0;">
        BOX BOX // PIT WALL COMMAND CENTER
    </div>
    <div style="font-size: 1rem; color: #94a3b8; max-width: 800px; line-height: 1.6;">
        Real-time Grand Prix pit stop optimization powered by <strong>FastF1 telemetry</strong>, 
        <strong>LightGBM Quantile Regression</strong>, and <strong>10,000-iteration vectorized Monte Carlo simulations</strong> in &lt;200ms.
    </div>
    <div style="margin-top: 1.25rem; display: flex; gap: 12px; flex-wrap: wrap;">
        <span style="background: rgba(225,6,0,0.15); border: 1px solid #e10600; color: #ff6b6b; padding: 4px 12px; border-radius: 4px; font-size: 0.78rem; font-weight: 800;">ALL 22 CALENDAR CIRCUITS</span>
        <span style="background: rgba(255,214,0,0.15); border: 1px solid #ffd600; color: #ffd600; padding: 4px 12px; border-radius: 4px; font-size: 0.78rem; font-weight: 800;">RADIAL CONFIDENCE GAUGES</span>
        <span style="background: rgba(0,230,118,0.15); border: 1px solid #00e676; color: #00e676; padding: 4px 12px; border-radius: 4px; font-size: 0.78rem; font-weight: 800;">LIVE TELEMETRY STREAM</span>
        <span style="background: rgba(56,189,248,0.15); border: 1px solid #38bdf8; color: #38bdf8; padding: 4px 12px; border-radius: 4px; font-size: 0.78rem; font-weight: 800;">FUEL BURN PHYSICS</span>
    </div>
</div>
""", unsafe_allow_html=True)

# ─── System Model Telemetry Status ───────────────────────────────────────────
st.markdown("""
<div class="pitwall-card-header">
    <span>CIRCUIT ML MODEL STATUS</span>
    <span style="color: #94a3b8; font-size: 0.75rem;">TELEMETRY CACHE</span>
</div>
""", unsafe_allow_html=True)

circuits_to_check = ["Bahrain", "Britain", "Monza", "Spain", "Monaco", "global"]
any_model = False
status_cols = st.columns(len(circuits_to_check))

for col, circuit in zip(status_cols, circuits_to_check):
    saved = TyreDegModel.is_saved(circuit)
    if saved:
        any_model = True
    status_txt   = "● ACTIVE" if saved else "○ CALIBRATED"
    status_color = "#00e676" if saved else "#ffd600"
    col.markdown(f"""
    <div style="background: #10141e; border: 1px solid {'#00e676' if saved else '#1e2638'};
                border-top: 2px solid {'#00e676' if saved else '#e10600'};
                border-radius: 6px; padding: 0.8rem 0.6rem; text-align: center; box-shadow: 0 4px 12px rgba(0,0,0,0.3);">
        <div style="font-size: 0.7rem; color: #94a3b8; text-transform: uppercase; font-weight: 700; letter-spacing: 1px; margin-bottom: 4px;">
            {circuit}
        </div>
        <div style="font-size: 0.82rem; color: {status_color}; font-weight: 800; font-family: 'JetBrains Mono', monospace;">
            {status_txt}
        </div>
    </div>""", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ─── Core Modules ─────────────────────────────────────────────────────────────
st.markdown("""
<div class="pitwall-card-header">
    <span>RACE ENGINEER CORE MODULES</span>
    <span style="color: #e10600; font-size: 0.75rem;">COMMAND PLATFORM</span>
</div>
""", unsafe_allow_html=True)

fc1, fc2, fc3 = st.columns(3)
features = [
    ("01", "🏎️ STRATEGY SIMULATOR",
     "Input car telemetry, stint laps, and gaps. Simulator computes 10,000 Monte Carlo runs to evaluate Pit Now vs Stay Out with radial confidence gauges.",
     "#e10600"),
    ("02", "📊 TYRE DEGRADATION LAB",
     "Ingest real FastF1 timing telemetry. Train LightGBM quantile regression models on fuel-corrected lap times per Pirelli compound.",
     "#ffd600"),
    ("03", "⏱️ STRATEGY BACKTEST",
     "Replay historical Grand Prix lap-by-lap. Compare AI calls vs real-world team pit calls with seconds gained/lost analysis.",
     "#00e676"),
    ("04", "🗺️ CIRCUIT INTELLIGENCE",
     "Examine calibrated wear rates, pit lane loss deltas, and historical Safety Car risk across all 22 calendar circuits.",
     "#38bdf8"),
    ("05", "⚔️ UNDERCUT / OVERCUT VIABILITY",
     "Real-time evaluation of whether fresh tyre delta can overturn competitor gap before the chequered flag.",
     "#e10600"),
    ("06", "📡 LIVE TELEMETRY LOGS",
     "Multi-source pipeline combining official FastF1 timing feed with resilient synthetic fallback for zero-downtime cloud hosting.",
     "#ffffff"),
]

for i, (num, title, desc, color) in enumerate(features):
    col = [fc1, fc2, fc3][i % 3]
    col.markdown(f"""
    <div style="background: #111520; border: 1px solid #1e2638; border-top: 3px solid {color};
                border-radius: 6px; padding: 1.1rem; margin-bottom: 1rem; min-height: 160px; box-shadow: 0 4px 15px rgba(0,0,0,0.3);">
        <div style="display: flex; justify-content: space-between; margin-bottom: 6px;">
            <span style="color: {color}; font-size: 0.72rem; font-weight: 800; letter-spacing: 1.5px;">MODULE {num}</span>
        </div>
        <div style="color: #ffffff; font-weight: 800; font-size: 0.95rem; margin-bottom: 6px;">
            {title}
        </div>
        <div style="color: #94a3b8; font-size: 0.82rem; line-height: 1.55;">
            {desc}
        </div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ─── Workflow Steps ───────────────────────────────────────────────────────────
st.markdown("""
<div class="pitwall-card-header">
    <span>RACE WEEKEND EXECUTION PIPELINE</span>
    <span style="color: #94a3b8; font-size: 0.75rem;">WORKFLOW</span>
</div>
""", unsafe_allow_html=True)

w1, w2, w3, w4 = st.columns(4)
steps = [
    ("01", "INGEST TELEMETRY", "FastF1 data fetch with fuel-burn physics removal (~1.6kg/lap)."),
    ("02", "FIT QUANTILE MODEL", "LightGBM models trained on tyre compound age curves (P10/P50/P90)."),
    ("03", "MONTE CARLO SWEEP", "10,000 vector runs testing pit windows, safety car, and traffic."),
    ("04", "RADIO PIT CALL", "Definitive BOX BOX or EXTEND STINT directive with radial gauge score."),
]

for col, (num, title, desc) in zip([w1, w2, w3, w4], steps):
    col.markdown(f"""
    <div style="background: #10141e; border: 1px solid #1e2638; border-left: 3px solid #e10600;
                border-radius: 6px; padding: 1rem; height: 100%;">
        <div style="font-size: 1.2rem; font-weight: 900; color: #e10600; font-family: 'JetBrains Mono', monospace;">{num}</div>
        <div style="color: #ffffff; font-weight: 800; font-size: 0.85rem; margin: 4px 0;">{title}</div>
        <div style="color: #94a3b8; font-size: 0.78rem; line-height: 1.5;">{desc}</div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("<br><br><hr style='border-color: rgba(255,255,255,0.06);'>", unsafe_allow_html=True)

# ─── Attribution Footer ───────────────────────────────────────────────────────
st.markdown("""
<div style="text-align: center; color: #94a3b8; font-size: 0.85rem; padding: 1rem 0;">
    🏎️ <strong>BOX BOX // F1 AI Race Strategist</strong> — Pit Wall Command Center<br>
    Engineered by <strong style="color: #ffffff;">Soumili Pal</strong><br>
    <div style="margin-top: 0.5rem; display: flex; justify-content: center; gap: 18px; font-size: 0.8rem;">
        <a href="https://github.com/404soulnotfound" target="_blank" style="color: #38bdf8; text-decoration: none;">GitHub</a> • 
        <a href="https://www.linkedin.com/in/soumilipal" target="_blank" style="color: #38bdf8; text-decoration: none;">LinkedIn</a> • 
        <a href="mailto:tidha427@gmail.com" style="color: #38bdf8; text-decoration: none;">tidha427@gmail.com</a>
    </div>
    <div style="margin-top: 0.4rem; font-size: 0.72rem; color: #475569;">
        Built with FastF1, LightGBM, Streamlit & Plotly · Not affiliated with Formula One Management or the FIA.
    </div>
</div>
""", unsafe_allow_html=True)
