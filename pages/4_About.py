"""
pages/4_About.py
-----------------
About & Engineering Methodology page for Box Box F1.
Presents the technical architecture, domain problem, and system specifications.
"""

import streamlit as st
import sys, os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from utils.ui_theme import inject_f1_theme, render_pit_wall_banner

st.set_page_config(page_title="About & Methodology // BOX BOX", page_icon="📄", layout="wide")
inject_f1_theme()

render_pit_wall_banner(
    circuit="SYSTEM SPEC",
    session_type="METHODOLOGY & ARCHITECTURE",
    lap_str="FULL SPEC",
    leader_delta="ML ARCHITECTURE",
    sc_status="CODE AUDITED",
    weather_str="PRODUCTION DEPLOYED"
)

st.markdown("""
<div class="pitwall-card" style="padding: 1.5rem 1.8rem; margin-bottom: 1.5rem;">
    <div style="font-size: 0.78rem; font-weight: 800; color: #e10600; letter-spacing: 2px; text-transform: uppercase;">
        ENGINEERING DOCUMENTATION & SYSTEM METHODOLOGY
    </div>
    <div style="font-size: 2.2rem; font-weight: 900; color: #ffffff; letter-spacing: 1px; margin: 4px 0;">
        📄 ARCHITECTURE & TECHNICAL SPECIFICATION
    </div>
    <div style="font-size: 0.95rem; color: #94a3b8; line-height: 1.6;">
        System architecture, mathematical models, and domain engineering challenges behind <strong>Box Box</strong>.
        Engineered by <strong>Soumili Pal</strong>.
    </div>
</div>
""", unsafe_allow_html=True)

st.markdown("""
This documentation details the engineering methodology, mathematical models, 
and system architecture behind **Box Box**. Explore the sections below to understand
how real telemetry data is processed, how uncertainty intervals are quantified, 
and how Monte Carlo simulations derive optimal pit stop strategies in real time.
""")

st.markdown("---")

# ─── TOC ───────────────────────────────────────────────────────────────────────
st.markdown("""
**Jump to:**  
[What problem this solves](#what-problem-this-solves) ·
[Key technical challenges](#key-technical-challenges-solved) ·
[System benchmarks](#project-by-the-numbers) ·
[System scope & limitations](#system-scope-limitations) ·
[Real F1 trackside comparison](#what-real-f1-teams-do-differently) ·
[Engineered by](#engineered-by)
""")

st.markdown("---")

# ─── What problem ──────────────────────────────────────────────────────────────
st.markdown('<p class="section-title">WHAT PROBLEM THIS SOLVES</p>', unsafe_allow_html=True)

st.markdown("""
In Formula 1, a race strategy decision — specifically **when to pit and which tyre compound
to use** — can be worth 5 to 15 seconds of race time. This is often the difference between
winning and finishing 3rd.

The core problem: **a team engineer cannot manually compute the optimal pit window** because:
""")

problems = [
    ("Too many variables", "Tyre deg rate, fuel load, weather, safety car probability, opponent strategies, pit lane traffic — all change every lap."),
    ("Uncertainty is irreducible", "You don't know exactly when your tyres will fall off a cliff. You don't know when the safety car will come out. You need to reason over distributions, not single values."),
    ("Decisions must be fast", "A pit window might be open for 2–3 laps. Computing the optimal call manually while also managing a race car is impossible."),
    ("Opponent interaction", "If you pit, the car behind might also pit and emerge ahead of you. If you stay out, the car behind might undercut you. You need to model opponent intent."),
]

for title, desc in problems:
    st.markdown(f"""
    <div class="decision-row">
        <div class="q">❌ Problem: {title}</div>
        <div class="a">{desc}</div>
    </div>""", unsafe_allow_html=True)

st.markdown("""
**This tool solves this** by running 10,000 simulations of every possible strategy
simultaneously and returning the one with the best *expected* outcome — not just the
deterministic optimum, but the strategy that performs best across the full distribution
of possible race outcomes.
""")

st.markdown("---")

# ─── Key challenges ────────────────────────────────────────────────────────────
st.markdown('<p class="section-title">KEY TECHNICAL CHALLENGES SOLVED</p>', unsafe_allow_html=True)

challenges = [
    ("🔴", "Fuel load correction",
     "Most public F1 ML projects skip this and end up with models that think tyres degrade faster in the first half of the race. Fuel correction is a domain knowledge requirement — you can't learn it from the data alone."),
    ("🟡", "Temporal train/val split",
     "Splitting laps randomly between train and test would leak information — the model would see lap 30 in training and lap 29 in validation, which is almost the same state. Grouping by driver ensures the split is meaningful."),
    ("🟢", "Vectorized simulation performance",
     "10,000 simulations in pure Python loops take ~30 seconds. The same computation in NumPy takes ~80ms. This makes the difference between a tool that feels live and one that feels broken."),
    ("🔵", "Safety car completely invalidates strategy",
     "A safety car converts a 22-second pit loss into a near-free pit. The system uses a Poisson probability model per circuit (some circuits have 3x the SC rate of others) and factors this into every simulation."),
    ("🟣", "Uncertainty quantification",
     "Point predictions (single lap time values) are not useful for strategy. What matters is the distribution — especially the tail. A strategy with median 1800s but P90 of 1840s is riskier than one with median 1803s and P90 of 1810s."),
]

for icon, title, desc in challenges:
    st.markdown(f"""
    <div class="insight-box">
        <div class="label">{icon} {title}</div>
        <p>{desc}</p>
    </div>""", unsafe_allow_html=True)

st.markdown("---")

# ─── Numbers ───────────────────────────────────────────────────────────────────
st.markdown('<p class="section-title">PROJECT BY THE NUMBERS</p>', unsafe_allow_html=True)

n1, n2, n3, n4, n5 = st.columns(5)
metrics = [
    ("1,796", "Lines of code"),
    ("10,000", "Simulations per decision"),
    ("~80ms", "Simulation runtime"),
    ("22", "Circuits supported"),
    ("5", "App modules"),
]
for col, (val, lbl) in zip([n1, n2, n3, n4, n5], metrics):
    col.markdown(f"""
    <div class="metric-highlight">
        <div class="val">{val}</div>
        <div class="lbl">{lbl}</div>
    </div>""", unsafe_allow_html=True)

st.markdown("---")

# ─── Limitations ───────────────────────────────────────────────────────────────
st.markdown('<p class="section-title">SYSTEM SCOPE & LIMITATIONS</p>', unsafe_allow_html=True)

st.markdown("""
Key technical boundaries and telemetry assumptions applied in the current release:
""")

limitations = [
    ("No live race integration",
     "OpenF1 provides a real-time API but integrating WebSocket streams with Streamlit requires additional architecture (FastAPI + background threads). The current app works on historical data or manual state input. The simulator itself is live-ready — it's just the data feed that's manual."),
    ("Gap data is estimated in backtest",
     "FastF1 doesn't provide live gap-to-car-ahead data in its lap-level dataset. The backtest page uses calibrated estimates for gaps. Real team systems have millisecond-precise gap data from the FOM timing feed."),
    ("No opponent modelling",
     "The simulator models your car's strategy in isolation. A complete system would model each opponent's tyre state and predict their pit windows, then simulate the interaction. This requires tracking all 20 cars simultaneously."),
    ("Training data volume",
     "Per-circuit models are trained on 400–900 laps (1–2 seasons). Real team models are trained on thousands of laps across many more conditions and include sensor-level tyre temperature and wear data unavailable publicly."),
    ("Safety car model is approximate",
     "The Poisson SC model uses historical circuit-level rates. A better model would use real-time gap distributions between cars (tighter gaps = higher crash probability) and driver incident history."),
]

for title, desc in limitations:
    st.markdown(f"""
    <div class="decision-row">
        <div class="q">⚠️ {title}</div>
        <div class="a">{desc}</div>
    </div>""", unsafe_allow_html=True)

st.markdown("---")

# ─── What real teams do ────────────────────────────────────────────────────────
st.markdown('<p class="section-title">WHAT REAL F1 TEAMS DO DIFFERENTLY</p>', unsafe_allow_html=True)

st.markdown("""
A comparison between public telemetry modeling and team-grade proprietary trackside infrastructure:
""")

gaps = [
    ("Data volume & quality",
     "Real teams have sensor-level data: tyre surface temperature across the contact patch, brake disc temps, suspension loads, tyre compound batch ID. This lets their deg models achieve sub-0.05s MAE vs this project's ~0.15–0.3s."),
    ("Opponent modelling",
     "Teams track all 20 cars simultaneously. Their system predicts when each opponent is likely to pit (based on their deg rates), then simulates the traffic consequences of each possible pit window."),
    ("Weather integration",
     "Real-time radar data feeds into the strategy system. If rain is 70% likely in 8 laps, the entire strategy tree changes. This project has a weather API hook but doesn't model wet-dry transitions."),
    ("Driver-in-the-loop",
     "Drivers radio engineers with tyre feel data ('the rears are going'). This subjective input is combined with objective telemetry. Some teams use NLP to process radio transcripts in real time."),
    ("Simulation scale",
     "Real teams run millions of simulations, not 10,000, using GPU-accelerated computation. They also pre-compute strategy trees before the race using all known starting conditions."),
]

for title, desc in gaps:
    st.markdown(f"""
    <div class="insight-box">
        <div class="label">📌 {title}</div>
        <p>{desc}</p>
    </div>""", unsafe_allow_html=True)

st.markdown("---")

# ─── Contact ───────────────────────────────────────────────────────────────────
st.markdown('<p class="section-title">ENGINEERED BY</p>', unsafe_allow_html=True)

st.markdown("""<div style="background: #111622; border: 1px solid #1e2638; border-top: 3px solid #e10600; border-radius: 10px; padding: 1.5rem;">
    <div style="font-size: 1.3rem; font-weight: 800; color: #ffffff; margin-bottom: 0.4rem; letter-spacing: 0.5px;">
        Soumili Pal
    </div>
    <div style="color: #94a3b8; font-size: 0.95rem; line-height: 2;">
        📧 <a href="mailto:tidha427@gmail.com" style="color: #38bdf8; text-decoration: none;">tidha427@gmail.com</a><br>
        🐙 <a href="https://github.com/404soulnotfound" target="_blank" style="color: #38bdf8; text-decoration: none;">github.com/404soulnotfound</a><br>
        💼 <a href="https://www.linkedin.com/in/soumilipal" target="_blank" style="color: #38bdf8; text-decoration: none;">linkedin.com/in/soumilipal</a>
    </div>
    <div style="margin-top: 1.25rem; border-top: 1px solid rgba(255,255,255,0.08); padding-top: 0.75rem; color: #64748b; font-size: 0.8rem;">
        Built with FastF1 · LightGBM · NumPy · Streamlit · Plotly<br>
        Data: Formula One Management timing feed via FastF1 · Not affiliated with Formula 1, FOM, or FIA.
    </div>
</div>""", unsafe_allow_html=True)
