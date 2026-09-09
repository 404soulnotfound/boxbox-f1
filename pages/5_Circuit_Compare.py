"""
pages/5_Circuit_Compare.py
---------------------------
Compare tyre degradation profiles and strategy patterns
across multiple F1 circuits side by side.
Uses demo data so it works without training any models.
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import sys, os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from utils.demo_data import CIRCUIT_PROFILES, generate_stint_curve, get_circuit_profile
from utils.ui_theme import inject_f1_theme, render_pit_wall_banner

st.set_page_config(page_title="Circuit Compare // BOX BOX", page_icon="🗺️", layout="wide")
inject_f1_theme()

COMPOUND_COLORS = {0: "#e10600", 1: "#ffd600", 2: "#ffffff"}
COMPOUND_NAMES  = {0: "SOFT", 1: "MEDIUM", 2: "HARD"}

render_pit_wall_banner(
    circuit="CALENDAR BENCHMARK",
    session_type="CIRCUIT COMPARISON & WEAR PROFILES",
    lap_str="CROSS-CIRCUIT",
    track_temp="MULTI-TRACK",
    air_temp="MULTI-TRACK",
    sc_status="CIRCUIT PROFILES"
)

st.markdown("""
<div class="hero-container" style="padding: 1.5rem 2rem; margin-bottom: 1.5rem;">
    <div class="hero-tag">TRACK METRICS & TYRE WEAR PROFILES</div>
    <div class="hero-title" style="font-size: 2.2rem;">🗺️ GRAND PRIX CIRCUIT COMPARISON</div>
    <div class="hero-sub" style="font-size: 0.95rem;">
        Examine how circuit surface asphalt, lateral cornering loads, pit lane transit times,
        and historical safety car rates dictate completely contrasting pit window tactics.
    </div>
</div>
""", unsafe_allow_html=True)

# Circuit selector
circuits = list(CIRCUIT_PROFILES.keys())
selected = st.multiselect(
    "Select Grand Prix Circuits for Cross-Comparison",
    circuits,
    default=["Bahrain", "Monza", "Spain", "Monaco"],
    max_selections=6,
)

if len(selected) < 2:
    st.warning("Please select at least 2 circuits to compare.")
    st.stop()

st.markdown("---")

# Stat cards
st.markdown("### 🏁 Circuit Profiles & Characteristics")
cols = st.columns(len(selected))
for col, circuit in zip(cols, selected):
    prof = get_circuit_profile(circuit)
    soft_deg = prof["deg_rates"][0] * 1000  # ms/lap
    sc_pct   = prof["sc_rate"] * 100

    deg_badge = (
        '<span style="color:#e10600; font-weight:800;">HIGH DEG</span>'
        if soft_deg > 75 else
        ('<span style="color:#ffd600; font-weight:800;">MEDIUM DEG</span>'
         if soft_deg > 45 else
         '<span style="color:#00e676; font-weight:800;">LOW DEG</span>')
    )

    col.markdown(f"""
    <div class="f1-card">
        <div style="font-weight: 800; font-size: 1.1rem; color: #ffffff; margin-bottom: 0.3rem;">
            {circuit.upper()}
        </div>
        <div style="font-size: 0.75rem; margin-bottom: 0.75rem;">
            TYPE: {deg_badge}
        </div>
        <div style="border-top: 1px solid rgba(255,255,255,0.06); padding-top: 0.5rem; font-size: 0.8rem;" class="telemetry-font">
            <div style="margin-bottom: 3px;">BASE: <strong style="color: #fff;">{prof['base_time']}s</strong></div>
            <div style="margin-bottom: 3px;">PIT LOSS: <strong style="color: #38bdf8;">{prof['pit_loss']}s</strong></div>
            <div style="margin-bottom: 3px;">SC RATE: <strong style="color: #ff9800;">{sc_pct:.0f}%</strong></div>
            <div>SOFT WEAR: <strong style="color: #e10600;">+{soft_deg:.0f}ms/lap</strong></div>
        </div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# Charts
ch_col1, ch_col2 = st.columns(2)

with ch_col1:
    st.markdown("#### 📉 Soft Tyre Degradation Slopes")
    fig_deg = go.Figure()
    circuit_colors = ["#e10600", "#38bdf8", "#ffd600", "#00e676", "#c084fc", "#fb923c"]
    
    for i, circuit in enumerate(selected):
        prof = get_circuit_profile(circuit)
        laps = list(range(1, 31))
        deg  = prof["deg_rates"][0]
        # Normalized time relative to fresh tyre
        delta = [deg * l for l in laps]
        color = circuit_colors[i % len(circuit_colors)]

        fig_deg.add_trace(go.Scatter(
            x=laps, y=delta, name=circuit,
            line=dict(color=color, width=2.5),
            mode="lines",
        ))

    fig_deg.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(18, 22, 32, 0.7)",
        font=dict(color="#cbd5e1", family="Titillium Web"),
        height=320,
        margin=dict(l=20, r=20, t=15, b=20),
        legend=dict(bgcolor="rgba(10, 14, 22, 0.8)", bordercolor="rgba(255,255,255,0.1)"),
        xaxis=dict(title="Tyre Age (Laps on Set)", showgrid=True, gridcolor="rgba(255,255,255,0.06)", color="#94a3b8"),
        yaxis=dict(title="Pace Degradation Delta (Seconds)", showgrid=True, gridcolor="rgba(255,255,255,0.06)", color="#94a3b8"),
    )
    st.plotly_chart(fig_deg, use_container_width=True)

with ch_col2:
    st.markdown("#### ⏱️ Pit Lane Delta Loss Comparison")
    pit_losses = [get_circuit_profile(c)["pit_loss"] for c in selected]
    
    fig_pit = go.Figure(go.Bar(
        x=selected,
        y=pit_losses,
        marker=dict(
            color=pit_losses,
            colorscale="Reds",
            line=dict(color="#ff3b30", width=1)
        ),
        text=[f"{v}s" for v in pit_losses],
        textposition="auto",
    ))
    fig_pit.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(18, 22, 32, 0.7)",
        font=dict(color="#cbd5e1", family="Titillium Web"),
        height=320,
        margin=dict(l=20, r=20, t=15, b=20),
        xaxis=dict(showgrid=False, color="#94a3b8"),
        yaxis=dict(title="Pit Loss Delta (Seconds)", showgrid=True, gridcolor="rgba(255,255,255,0.06)", color="#94a3b8"),
    )
    st.plotly_chart(fig_pit, use_container_width=True)

st.markdown("---")
st.caption("🏎️ BOX BOX // Circuit profiles calibrated from official 2023 FIA & FastF1 telemetry benchmarks.")
