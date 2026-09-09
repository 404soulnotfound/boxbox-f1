"""
app.py
------
Homepage / landing page for Box Box — F1 AI Race Strategist.
Run with: streamlit run app.py
"""

import streamlit as st
import sys, os
sys.path.insert(0, os.path.dirname(__file__))

from models.tyre_model import TyreDegModel
from utils.ui_theme import inject_f1_theme, render_pit_wall_banner

st.set_page_config(
    page_title="BOX BOX — F1 AI Race Strategist",
    page_icon="🏎️",
    layout="wide",
    initial_sidebar_state="expanded",
)

inject_f1_theme()

# ─── Live telemetry banner ───────────────────────────────────────────────────
render_pit_wall_banner(
    circuit="Bahrain International Circuit",
    session_type="RACE CONTROL READY",
    lap_str="READY FOR TELEMETRY",
    track_temp="38.2°C",
    air_temp="28.4°C",
    sc_status="TRACK CLEAR"
)

# ─── Hero Section ────────────────────────────────────────────────────────────
st.markdown("""
<div class="hero-container">
    <div class="hero-tag">FORMULA 1 TELEMETRY & STRATEGY ENGINE</div>
    <div class="hero-title">BOX BOX // AI RACE STRATEGIST</div>
    <div class="hero-sub">
        High-performance pit stop optimization and tyre degradation modeling powered by 
        <strong>FastF1 telemetry</strong>, <strong>LightGBM Quantile Regression</strong>, and 
        <strong>10,000-run Monte Carlo simulations</strong> in sub-200ms.
    </div>
    <div style="margin-top: 1.5rem; display: flex; gap: 10px; flex-wrap: wrap;">
        <span style="background: rgba(225,6,0,0.15); border: 1px solid #e10600; color: #ff6b6b; padding: 4px 12px; border-radius: 20px; font-size: 0.8rem; font-weight: 700;">FASTF1 TELEMETRY</span>
        <span style="background: rgba(56,189,248,0.15); border: 1px solid #38bdf8; color: #38bdf8; padding: 4px 12px; border-radius: 20px; font-size: 0.8rem; font-weight: 700;">LIGHTGBM UNCERTAINTY</span>
        <span style="background: rgba(0,230,118,0.15); border: 1px solid #00e676; color: #00e676; padding: 4px 12px; border-radius: 20px; font-size: 0.8rem; font-weight: 700;">VECTORIZED MONTE CARLO</span>
        <span style="background: rgba(255,214,0,0.15); border: 1px solid #ffd600; color: #ffd600; padding: 4px 12px; border-radius: 20px; font-size: 0.8rem; font-weight: 700;">LIVE UNDERCUT CALCS</span>
    </div>
</div>
""", unsafe_allow_html=True)

# ─── System Model Status ─────────────────────────────────────────────────────
st.markdown("### 📡 ML Model Telemetry & Circuit Weights")

circuits_to_check = ["Bahrain", "Britain", "Monza", "Spain", "Monaco", "global"]
any_model = False
status_cols = st.columns(len(circuits_to_check))

for col, circuit in zip(status_cols, circuits_to_check):
    saved = TyreDegModel.is_saved(circuit)
    if saved:
        any_model = True
    status_indicator = (
        '<span style="color: #00e676; font-weight: 700; font-family: monospace;">● READY</span>'
        if saved else
        '<span style="color: #ffd600; font-weight: 700; font-family: monospace;">○ DEMO CALIBRATED</span>'
    )
    col.markdown(f"""
    <div style="background: #10141e; border: 1px solid {'#1e3a5f' if saved else '#1e2638'};
                border-radius: 8px; padding: 0.9rem; text-align: center; box-shadow: 0 4px 12px rgba(0,0,0,0.3);">
        <div style="font-size: 0.75rem; color: #94a3b8; text-transform: uppercase; letter-spacing: 1px; margin-bottom: 6px;">
            {circuit}
        </div>
        <div style="font-size: 0.85rem;">{status_indicator}</div>
    </div>""", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

if not any_model:
    st.info(
        "💡 **Notice:** Built-in calibrated profiles for all circuits are active right now! "
        "You can explore the **Strategy Simulator** or **Circuit Compare** instantly without waiting. "
        "To train custom LightGBM models on raw FastF1 sessions, head over to **Tyre Analysis**."
    )
else:
    st.success("✅ **Active AI Weights Found:** Ready for high-precision race telemetry analysis.")

st.markdown("---")

# ─── Features Grid ───────────────────────────────────────────────────────────
st.markdown("### 🏎️ Race Engineer Core Modules")

fc1, fc2, fc3 = st.columns(3)
features = [
    ("🧠", "LightGBM Tyre Degradation",
     "Quantile regression predicting fuel-corrected lap times with P10/P50/P90 confidence envelopes per compound.",
     "pages/1_Strategy_Simulator.py"),
    ("🎲", "Vectorized Monte Carlo",
     "Simulates 10,000 race runs simultaneously via NumPy array broadcasting in under 200ms with variable pit windows.",
     "pages/1_Strategy_Simulator.py"),
    ("🎯", "Optimal Pit Window Callout",
     "Calculates immediate delta vs stay-out strategies, evaluating tyre cliff timing and traffic re-entry pockets.",
     "pages/1_Strategy_Simulator.py"),
    ("⚔️", "Dynamic Undercut / Overcut",
     "Computes real-time laps required to overturn delta to car ahead based on pit loss and fresh rubber pace.",
     "pages/1_Strategy_Simulator.py"),
    ("🚨", "Stochastic Safety Car Matrix",
     "Poisson probability distribution modeling SC and VSC deployment odds based on historic circuit crash rates.",
     "pages/5_Circuit_Compare.py"),
    ("📊", "Historical Race Replay",
     "Backtest AI strategy calls lap-by-lap against real GP historical decisions (e.g. Verstappen, Hamilton, Leclerc).",
     "pages/3_Backtest.py"),
]

for i, (icon, title, desc, path) in enumerate(features):
    col = [fc1, fc2, fc3][i % 3]
    col.markdown(f"""
    <div class="f1-card" style="min-height: 180px; margin-bottom: 1.25rem;">
        <div style="font-size: 2rem; margin-bottom: 0.6rem;">{icon}</div>
        <div style="font-weight: 800; color: #ffffff; font-size: 1.05rem; margin-bottom: 0.4rem; letter-spacing: 0.5px;">
            {title}
        </div>
        <div style="color: #94a3b8; font-size: 0.88rem; line-height: 1.55;">
            {desc}
        </div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("---")

# ─── Workflow Section ────────────────────────────────────────────────────────
st.markdown("### 🚦 Race Weekend Workflow")

w1, w2, w3, w4 = st.columns(4)
workflow_steps = [
    ("1", "TELEMETRY INGESTION", "Fetch historical FP & GP timing via FastF1 API with automatic fuel burn corrections."),
    ("2", "MODEL CALIBRATION", "Train LightGBM quantile estimators on tyre degradation curves across compounds."),
    ("3", "RACE SIMULATION", "Evaluate 10,000 stochastic futures: pit now vs offset stints vs overcut."),
    ("4", "EXECUTE STRATEGY", "Receive definitive 'BOX BOX' or 'STAY OUT' radio recommendations with delta bounds."),
]

for col, (num, step_title, step_desc) in zip([w1, w2, w3, w4], workflow_steps):
    col.markdown(f"""
    <div style="background: #111622; border: 1px solid #1e2638; border-top: 3px solid #e10600; border-radius: 8px; padding: 1.2rem; height: 100%;">
        <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 0.5rem;">
            <span style="font-size: 1.25rem; font-weight: 900; color: #e10600; font-family: monospace;">0{num}</span>
            <span style="color: #475569; font-size: 0.75rem;">// STEP</span>
        </div>
        <div style="font-weight: 700; color: #fff; font-size: 0.95rem; margin-bottom: 0.4rem;">{step_title}</div>
        <div style="color: #94a3b8; font-size: 0.82rem; line-height: 1.5;">{step_desc}</div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("<br><br>", unsafe_allow_html=True)
st.markdown("---")

# ─── Footer ──────────────────────────────────────────────────────────────────
st.markdown("""
<div style="text-align: center; color: #94a3b8; font-size: 0.85rem; padding: 1.5rem 0; border-top: 1px solid rgba(255,255,255,0.06);">
    🏎️ <strong>BOX BOX // F1 AI Race Strategist</strong> — Engineered by <strong style="color: #ffffff;">Soumili Pal</strong><br>
    <div style="margin-top: 0.5rem; display: flex; justify-content: center; gap: 15px; font-size: 0.8rem;">
        <a href="https://github.com/404soulnotfound" target="_blank" style="color: #38bdf8; text-decoration: none;">GitHub</a> • 
        <a href="https://www.linkedin.com/in/soumilipal" target="_blank" style="color: #38bdf8; text-decoration: none;">LinkedIn</a> • 
        <a href="mailto:tidha427@gmail.com" style="color: #38bdf8; text-decoration: none;">tidha427@gmail.com</a>
    </div>
    <div style="margin-top: 0.5rem; font-size: 0.72rem; color: #475569;">
        Built with FastF1, LightGBM, Streamlit & Plotly · Not affiliated with Formula One Management or the FIA.
    </div>
</div>
""", unsafe_allow_html=True)
