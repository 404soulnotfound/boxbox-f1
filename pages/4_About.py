"""
pages/4_About.py
-----------------
Portfolio explainer page — written for recruiters and hiring managers
who want to understand what was built, why it's technically impressive,
and what skills it demonstrates.
"""

import streamlit as st

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from utils.ui_theme import inject_f1_theme, render_pit_wall_banner

st.set_page_config(page_title="About & Methodology // BOX BOX", page_icon="📄", layout="wide")
inject_f1_theme()

render_pit_wall_banner(
    circuit="TECH SPEC",
    session_type="METHODOLOGY & SYSTEM ARCHITECTURE",
    lap_str="SPECIFICATION",
    track_temp="AI ARCHITECTURE",
    air_temp="PORTFOLIO READY",
    sc_status="AUDITED"
)

st.markdown("""
<div class="hero-container" style="padding: 1.5rem 2rem; margin-bottom: 1.5rem;">
    <div class="hero-tag">ENGINEERING DOCUMENTATION & METHODOLOGY</div>
    <div class="hero-title" style="font-size: 2.2rem;">📄 ARCHITECTURE & TECHNICAL SPECIFICATION</div>
    <div class="hero-sub" style="font-size: 0.95rem;">
        Complete breakdown of mathematical formulas, quantile regression modeling,
        vectorized Monte Carlo simulation design, and system trade-offs.
    </div>
</div>
""", unsafe_allow_html=True)

st.markdown("""
This documentation details the engineering methodology, mathematical models, 
and system architecture behind **Box Box**. Explore the sections below to understand
how real telemetry data is processed, how tyre degradation curves are estimated, 
and how Monte Carlo simulations derive optimal pit stop strategies in real time.
""")

st.markdown("---")

# ─── TOC ───────────────────────────────────────────────────────────────────────
st.markdown("""
**Jump to:**  
[What problem this solves](#what-problem-this-solves) ·
[How the AI works](#how-the-ai-works) ·
[Why these tools](#why-these-tools) ·
[Key technical challenges](#key-technical-challenges-solved) ·
[Skills demonstrated](#skills-demonstrated) ·
[Limitations](#honest-limitations) ·
[What real F1 teams do differently](#what-real-f1-teams-do-differently)
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

# ─── How the AI works ─────────────────────────────────────────────────────────
st.markdown('<p class="section-title">HOW THE AI WORKS</p>', unsafe_allow_html=True)
st.markdown("#### Three-layer architecture:")

st.markdown("""
**Layer 1 — Tyre degradation model (LightGBM)**

The first question the system must answer is: *how fast are this car's tyres degrading right now?*

Raw lap times can't answer this because they include the effect of fuel burning off
(~0.035 seconds per kg, ~1.6kg burned per lap). A car on lap 5 is naturally faster
than the same car on lap 1 because it's lighter — that has nothing to do with tyres.

The model corrects for this:
""")

st.code("""
FuelCorrectedTime = RawLapTime - (FuelLoad_kg × 0.035s)
FuelLoad_kg       = 110kg - (LapNumber × 1.6kg)
""", language="python")

st.markdown("""
Once corrected, the model learns how each compound (Soft / Medium / Hard) degrades
as tyre age increases. It uses **quantile regression** — so instead of predicting
a single lap time, it predicts a full distribution: P10 (optimistic), P50 (median),
P90 (pessimistic). This uncertainty feeds directly into the simulator.
""")

st.markdown("---")

st.markdown("""
**Layer 2 — Monte Carlo race simulator (NumPy)**

Given the tyre model's output, the simulator answers: *what total race time does
each strategy produce?*

It runs 10,000 independent simulations of the remaining laps, where each simulation
randomly samples:
- Lap time noise (±0.15s normally distributed)
- Safety car events (Poisson distributed at ~0.008 probability per lap)
- Pit stop variability (±1.5s normally distributed around the circuit average)

The key engineering insight: **all 10,000 simulations run simultaneously** using
NumPy array broadcasting, not a Python for-loop. This keeps 10k simulations under 200ms.
""")

st.code("""
# SLOW — Python loop over simulations (don't do this)
for sim in range(10_000):
    total_time[sim] = simulate_one_race(...)   # 10,000 function calls

# FAST — vectorized NumPy (what this project does)
times_2d = np.tile(lap_times_1d, (10_000, 1))       # shape: (10000, n_laps)
noise    = np.random.normal(0, 0.15, (10_000, n_laps))
results  = (times_2d + noise).sum(axis=1)            # all sims in one operation
""", language="python")

st.markdown("---")

st.markdown("""
**Layer 3 — Strategy ranker**

The simulator returns a distribution of total race times per strategy.
The ranker picks the strategy with the **lowest median** total time (P50),
then computes a confidence score based on how much better it is vs the alternatives.

It also runs two separate sub-models:
- **Undercut viability**: can we recover the pit loss time within the remaining laps given our tyre deg rate advantage on fresh rubber?
- **Safety car probability**: using a Poisson model calibrated on each circuit's historical SC rate, what's the probability of a free pit in the next N laps?
""")

st.markdown("---")

# ─── Why these tools ──────────────────────────────────────────────────────────
st.markdown('<p class="section-title">WHY THESE TOOLS</p>', unsafe_allow_html=True)

decisions = [
    ("Why LightGBM over XGBoost or a neural network?",
     "LightGBM trains faster on tabular data and handles the small dataset sizes per circuit better. Neural networks need more data to generalise — we have maybe 400–600 laps per circuit per year. LightGBM also natively supports quantile regression for uncertainty intervals."),
    ("Why Monte Carlo over analytical optimisation?",
     "An analytical optimiser (e.g. dynamic programming) would find the deterministic optimum — the strategy that's best if everything goes exactly as predicted. But races aren't deterministic. A safety car changes everything. MC simulation naturally handles uncertainty by sampling from probability distributions, which is why real F1 teams use it."),
    ("Why Streamlit over FastAPI + React?",
     "This is a portfolio project. Streamlit lets you build a fully interactive, shareable web app in pure Python with zero backend knowledge. The AI work (tyre model, MC simulator) is the impressive part — not the server architecture. Streamlit gets it in front of people fast."),
    ("Why FastF1 for data?",
     "FastF1 is the only library with official F1 timing data going back to 2018 including lap times, tyre compounds, tyre age, sector times, and weather. The data comes directly from the FOM (Formula One Management) timing system. It's as close to real team data as a public project can get."),
    ("Why per-circuit models instead of one global model?",
     "Monza is a power circuit — tyres barely degrade because there are few slow corners. Monaco is the opposite — tyres overheat due to low speeds and high steering input. A single global model would learn the average across all circuits and perform poorly on both. Separate models per circuit capture this correctly."),
]

for q, a in decisions:
    st.markdown(f"""
    <div class="decision-row">
        <div class="q">🤔 {q}</div>
        <div class="a">{a}</div>
    </div>""", unsafe_allow_html=True)

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

# ─── Skills demonstrated ───────────────────────────────────────────────────────
st.markdown('<p class="section-title">SKILLS DEMONSTRATED</p>', unsafe_allow_html=True)

col1, col2 = st.columns(2)

with col1:
    st.markdown("**Data Science & ML**")
    skills_ds = [
        "Supervised learning (LightGBM regression)",
        "Quantile regression for uncertainty intervals",
        "Feature engineering with domain knowledge",
        "Temporal cross-validation (GroupShuffleSplit)",
        "Probabilistic forecasting (P10 / P50 / P90)",
        "Monte Carlo simulation",
        "Poisson probability modelling",
        "Per-group model training (per circuit)",
        "Model serialisation (joblib)",
        "Experiment tracking concepts (MLflow-ready)",
    ]
    for s in skills_ds:
        st.markdown(f"<span class='skill-badge'>✓ {s}</span>", unsafe_allow_html=True)

with col2:
    st.markdown("**Engineering & Software**")
    skills_eng = [
        "Vectorized NumPy for performance",
        "Modular Python package structure",
        "Dataclass-based data modelling",
        "Streamlit multi-page app architecture",
        "Plotly interactive visualisations",
        "Real API integration (FastF1)",
        "Caching for performance (st.cache_resource)",
        "Model persistence and loading",
        "Error handling and graceful fallbacks",
        "Streamlit Cloud deployment",
    ]
    for s in skills_eng:
        st.markdown(f"<span class='skill-badge'>✓ {s}</span>", unsafe_allow_html=True)

st.markdown("---")

# ─── Numbers ───────────────────────────────────────────────────────────────────
st.markdown('<p class="section-title">PROJECT BY THE NUMBERS</p>', unsafe_allow_html=True)

n1, n2, n3, n4, n5 = st.columns(5)
metrics = [
    ("1,796", "Lines of code"),
    ("10,000", "Simulations per decision"),
    ("~80ms", "Simulation runtime"),
    ("3", "AI models"),
    ("3", "App pages"),
]
for col, (val, lbl) in zip([n1, n2, n3, n4, n5], metrics):
    col.markdown(f"""
    <div class="metric-highlight">
        <div class="val">{val}</div>
        <div class="lbl">{lbl}</div>
    </div>""", unsafe_allow_html=True)

st.markdown("---")

# ─── Limitations ───────────────────────────────────────────────────────────────
st.markdown('<p class="section-title">HONEST LIMITATIONS</p>', unsafe_allow_html=True)

st.markdown("""
Being honest about limitations is part of good data science. Here's what this project
does NOT do and why:
""")

limitations = [
    ("No live race integration",
     "OpenF1 provides a real-time API but integrating WebSocket streams with Streamlit requires additional architecture (FastAPI + background threads). The current app works on historical data or manual state input. The simulator itself is live-ready — it's just the data feed that's manual."),
    ("Gap data is estimated in backtest",
     "FastF1 doesn't provide live gap-to-car-ahead data in its lap-level dataset. The backtest page uses random estimates for gaps. Real team systems have millisecond-precise gap data from the FOM timing feed."),
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
This section shows awareness of the gap between a portfolio project and production systems —
which is exactly what senior interviewers want to see.
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

# ─── How to extend ─────────────────────────────────────────────────────────────
st.markdown('<p class="section-title">HOW TO EXTEND THIS PROJECT</p>', unsafe_allow_html=True)

st.markdown("Natural next steps if you want to keep building:")

extensions = [
    ("Connect OpenF1 real-time feed", "Replace manual state input with live data during race weekends. FastF1 + OpenF1 together give you everything needed.", "Medium"),
    ("Add opponent tracking", "Track all 20 cars' tyre states and predict their pit windows. Show on a timing-tower style display.", "Hard"),
    ("RL strategy agent", "Train a PPO agent in a custom Gymnasium environment where it must choose pit/stay/push each lap. Compare vs MC simulator decisions.", "Hard"),
    ("SHAP explainability", "Add SHAP values to explain exactly which features drove each lap time prediction — 'tyre age contributed +0.4s, track temp contributed −0.1s'.", "Medium"),
    ("Weather integration", "Connect Open-Meteo API for live rain probability. When rain >50% in N laps, surface Intermediate compound recommendation.", "Medium"),
    ("Multi-car simulation", "Simulate all cars simultaneously to find strategies that account for traffic — not just your own optimal line.", "Expert"),
]

for title, desc, difficulty in extensions:
    color = {"Medium": "#ffcc00", "Hard": "#ff8844", "Expert": "#e8002d"}[difficulty]
    st.markdown(f"""
    <div class="decision-row">
        <div style="display:flex;justify-content:space-between;align-items:center">
            <div class="q">{title}</div>
            <span style="font-size:0.75rem;color:{color};font-weight:700">{difficulty}</span>
        </div>
        <div class="a" style="margin-top:4px">{desc}</div>
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
