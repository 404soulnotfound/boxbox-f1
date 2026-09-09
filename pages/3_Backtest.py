"""
pages/3_Backtest.py
--------------------
Backtest the AI strategy engine against historical races.
Loads a full race, replays it lap-by-lap, generates AI recommendations
at each pit decision point, and compares with what actually happened.
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import sys, os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from data.loader import load_race_laps
from models.simulator import MonteCarloSimulator, RaceState, safety_car_probability
from models.tyre_model import TyreDegModel
from utils.ui_theme import inject_f1_theme, render_pit_wall_banner

st.set_page_config(page_title="Strategy Backtest // BOX BOX", page_icon="📊", layout="wide")
inject_f1_theme()

COMPOUND_COLORS = {0: "#e10600", 1: "#ffd600", 2: "#ffffff", 3: "#39b54a", 4: "#0072bb"}
COMPOUND_NAMES  = {0: "SOFT", 1: "MEDIUM", 2: "HARD", 3: "INTER", 4: "WET"}

render_pit_wall_banner(
    circuit="HISTORICAL REPLAY",
    session_type="STRATEGY ENGINE BACKTEST",
    lap_str="FULL GRAND PRIX",
    track_temp="HISTORICAL",
    air_temp="HISTORICAL",
    sc_status="SESSION LOGGED"
)

st.markdown("""
<div class="hero-container" style="padding: 1.5rem 2rem; margin-bottom: 1.5rem;">
    <div class="hero-tag">HISTORICAL RACE VALIDATION</div>
    <div class="hero-title" style="font-size: 2.2rem;">📊 STRATEGY BACKTEST & REPLAY ENGINE</div>
    <div class="hero-sub" style="font-size: 0.95rem;">
        Replay any real Formula 1 Grand Prix lap-by-lap. Inspect what the AI strategy model
        would have commanded at critical pit windows vs the actual calls made by real pit walls.
    </div>
</div>
""", unsafe_allow_html=True)

# Select race
col1, col2, col3, col4 = st.columns(4)
with col1:
    bt_year = st.selectbox("Season", [2023, 2022, 2021], index=0, key="bt_year")
with col2:
    bt_circuit = st.selectbox("Circuit", ["Bahrain", "Britain", "Monza", "Spain", "Japan", "Austria"], key="bt_circ")
with col3:
    bt_driver = st.text_input("Driver Code (3 Letters)", value="VER", max_chars=3).upper()
with col4:
    st.markdown("<br>", unsafe_allow_html=True)
    bt_btn = st.button("▶ EXECUTE BACKTEST", type="primary", use_container_width=True)

if bt_btn:
    with st.spinner(f"Retrieving telemetry for {bt_year} {bt_circuit} GP..."):
        try:
            df = load_race_laps(bt_year, bt_circuit)
        except Exception as e:
            st.error(f"Could not load data: {e}")
            st.stop()

    drv_df = df[df["Driver"] == bt_driver].sort_values("LapNumber").reset_index(drop=True)
    if len(drv_df) == 0:
        available = sorted(df["Driver"].unique())
        st.error(f"Driver '{bt_driver}' not found. Available: {', '.join(available)}")
        st.stop()

    # Load model
    if TyreDegModel.is_saved(bt_circuit):
        model = TyreDegModel.load(bt_circuit)
    elif TyreDegModel.is_saved("global"):
        model = TyreDegModel.load("global")
    else:
        model = None

    simulator = MonteCarloSimulator(tyre_model=model, n_simulations=5_000)

    total_laps = int(drv_df["LapNumber"].max())
    pit_laps   = drv_df[drv_df["TyreAge"] == 1]["LapNumber"].tolist()[1:]

    st.success(f"✓ Replaying {bt_year} {bt_circuit} GP for **{bt_driver}** | Completed Laps: {len(drv_df)} | Pit In Laps: {pit_laps}")

    # Plot actual race lap times
    st.markdown("### ⏱️ Grand Prix Telemetry Trace & Pit Windows")

    fig_main = go.Figure()
    for code in drv_df["CompoundCode"].unique():
        sub = drv_df[drv_df["CompoundCode"] == code]
        name = COMPOUND_NAMES.get(code, "?")
        fig_main.add_trace(go.Scatter(
            x=sub["LapNumber"], y=sub["LapTimeSeconds"],
            mode="markers+lines", name=name,
            line=dict(color=COMPOUND_COLORS.get(code, "#fff"), width=2),
            marker=dict(color=COMPOUND_COLORS.get(code, "#fff"), size=6),
        ))

    for pl in pit_laps:
        fig_main.add_vline(
            x=pl, line_dash="dash", line_color="#e10600", line_width=2,
            annotation_text=f"PIT (Lap {pl})", annotation_font_color="#e10600",
            annotation_position="top right"
        )

    fig_main.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(18, 22, 32, 0.7)",
        font=dict(color="#cbd5e1", family="Titillium Web"),
        height=340,
        margin=dict(l=20, r=20, t=15, b=20),
        legend=dict(bgcolor="rgba(10, 14, 22, 0.8)", bordercolor="rgba(255,255,255,0.1)"),
        xaxis=dict(title="Lap Number", showgrid=True, gridcolor="rgba(255,255,255,0.06)", color="#94a3b8"),
        yaxis=dict(title="Lap Time (Seconds)", showgrid=True, gridcolor="rgba(255,255,255,0.06)", color="#94a3b8"),
    )
    st.plotly_chart(fig_main, use_container_width=True)

    # Decision windows
    st.markdown("### 📻 AI Strategy Calls at Pit Windows")
    check_laps = [l for l in [15, 20, 25, 30, 35] if l < total_laps - 5]

    for check_lap in check_laps:
        row = drv_df[drv_df["LapNumber"] == check_lap]
        if len(row) == 0:
            continue
        row = row.iloc[0]

        state = RaceState(
            current_lap   = int(row["LapNumber"]),
            total_laps    = total_laps,
            tyre_age      = int(row["TyreAge"]),
            compound_code = int(row["CompoundCode"]),
            gap_ahead     = 3.5,
            gap_behind    = 2.2,
            pit_loss_time = 22.0,
            track_temp    = float(row.get("TrackTemp", 38)),
            air_temp      = float(row.get("AirTemp", 28)),
        )

        decisions = simulator.compute_best_strategy(state, new_compound=1)
        best = decisions[0]

        next_actual_pit = next((pl for pl in pit_laps if pl > check_lap), None)
        ai_pit_lap = check_lap + best.pit_lap_offset if best.pit_lap_offset < 999 else None
        
        diff_str = ""
        badge_bg = "#1e293b"
        if next_actual_pit and ai_pit_lap:
            diff = abs(next_actual_pit - ai_pit_lap)
            if diff <= 3:
                diff_str = f"✅ ALIGNED WITH PIT WALL (±{diff} Laps)"
                badge_bg = "rgba(0, 230, 118, 0.2)"
            else:
                diff_str = f"⚠️ DIVERGED BY {diff} LAPS"
                badge_bg = "rgba(225, 6, 0, 0.2)"

        compound_name = COMPOUND_NAMES.get(int(row["CompoundCode"]), "?")
        
        with st.expander(f"📍 Lap {check_lap} // Compound: {compound_name} (Age {int(row['TyreAge'])} laps) — AI: {best.action} | {diff_str}"):
            rc1, rc2, rc3 = st.columns(3)
            rc1.metric("Optimal Call", best.action)
            rc2.metric("Confidence", f"{best.confidence*100:.0f}%")
            rc3.metric("Actual Team Pit", f"Lap {next_actual_pit}" if next_actual_pit else "Extended")

            st.write(f"**Race Engineer Analysis:** {best.reasoning}")

            # Strategy table
            rows = []
            for d in decisions:
                rows.append({
                    "Strategy":      d.action.replace('_', ' '),
                    "Compound":      d.recommended_compound,
                    "Median Time":   f"{d.p50_time:.1f}s",
                    "P10 (Best)":    f"{d.p10_time:.1f}s",
                    "P90 (Worst)":   f"{d.p90_time:.1f}s",
                    "Delta vs Best": f"+{d.expected_time_loss:.1f}s",
                    "Confidence":    f"{d.confidence*100:.0f}%",
                    "Recommended":   "★ OPTIMAL" if d.is_recommended else "",
                })
            st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)

    # Stint summary
    st.markdown("---")
    st.markdown("### 📋 Grand Prix Stint Breakdown")

    stint_data = []
    current_stint = 1
    stint_start   = int(drv_df.iloc[0]["LapNumber"])
    prev_age      = 0

    for _, row in drv_df.iterrows():
        if row["TyreAge"] < prev_age:
            stint_end = int(row["LapNumber"]) - 1
            stint_len = stint_end - stint_start + 1
            compound  = COMPOUND_NAMES.get(int(drv_df[drv_df["LapNumber"] == stint_start]["CompoundCode"].values[0]), "?")
            stint_data.append({
                "Stint":     f"Stint {current_stint}",
                "Compound":  compound,
                "Start Lap": stint_start,
                "End Lap":   stint_end,
                "Laps Run":  stint_len,
            })
            current_stint += 1
            stint_start    = int(row["LapNumber"])
        prev_age = int(row["TyreAge"])

    stint_data.append({
        "Stint":     f"Stint {current_stint}",
        "Compound":  COMPOUND_NAMES.get(int(drv_df.iloc[-1]["CompoundCode"]), "?"),
        "Start Lap": stint_start,
        "End Lap":   int(drv_df.iloc[-1]["LapNumber"]),
        "Laps Run":  int(drv_df.iloc[-1]["LapNumber"]) - stint_start + 1,
    })

    st.dataframe(pd.DataFrame(stint_data), use_container_width=True, hide_index=True)
else:
    st.info("👆 Configure season, circuit, and driver code above, then click **Execute Backtest**.")
