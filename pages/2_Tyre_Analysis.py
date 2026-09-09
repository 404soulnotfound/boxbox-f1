"""
pages/2_Tyre_Analysis.py
-------------------------
Explore historical tyre degradation data from FastF1.
Train the LightGBM model directly from the UI with real telemetry.
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
import sys, os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from data.loader import load_race_laps, COMPOUND_MAP, COMPOUND_LABELS
from models.tyre_model import TyreDegModel
from utils.ui_theme import inject_f1_theme, render_pit_wall_banner

st.set_page_config(page_title="Tyre Analysis // BOX BOX", page_icon="🔴", layout="wide")
inject_f1_theme()

COMPOUND_COLORS = {0: "#e10600", 1: "#ffd600", 2: "#ffffff", 3: "#39b54a", 4: "#0072bb"}
COMPOUND_NAMES  = {0: "SOFT", 1: "MEDIUM", 2: "HARD", 3: "INTER", 4: "WET"}

render_pit_wall_banner(
    circuit="TELEMETRY LAB",
    session_type="TYRE DEGRADATION & ML TRAINING",
    lap_str="HISTORICAL TELEMETRY",
    track_temp="VARIABLE",
    air_temp="VARIABLE",
    sc_status="SESSION READY"
)

st.markdown("""
<div class="hero-container" style="padding: 1.5rem 2rem; margin-bottom: 1.5rem;">
    <div class="hero-tag">DATA TELEMETRY & ML TRAINING LAB</div>
    <div class="hero-title" style="font-size: 2.2rem;">🔴 PIRELLI TYRE DEGRADATION ANALYSIS</div>
    <div class="hero-sub" style="font-size: 0.95rem;">
        Extract raw timing traces from FastF1, filter out fuel load burns (~0.035s per kg per lap),
        and fit high-precision quantile estimators to predict tyre life cliffs.
    </div>
</div>
""", unsafe_allow_html=True)

# --- Step 1: Load Data ---
st.markdown("### 1. Ingest Grand Prix Telemetry")

col_a, col_b, col_c = st.columns(3)
with col_a:
    sel_year = st.selectbox("Championship Season", [2024, 2023, 2022, 2021], index=1)
with col_b:
    sel_circuit = st.selectbox("Grand Prix Host", [
        "Bahrain", "Saudi Arabia", "Australia", "Azerbaijan",
        "Miami", "Monaco", "Spain", "Canada", "Austria",
        "Britain", "Hungary", "Belgium", "Netherlands",
        "Italy", "Singapore", "Japan", "Qatar",
        "United States", "Mexico City", "Abu Dhabi",
    ], index=0)
with col_c:
    st.markdown("<br>", unsafe_allow_html=True)
    load_btn = st.button("📥 INGEST FASTF1 TELEMETRY", type="primary", use_container_width=True)

if "lap_data" not in st.session_state:
    st.session_state.lap_data = None
if "loaded_label" not in st.session_state:
    st.session_state.loaded_label = ""

if load_btn:
    with st.spinner(f"Ingesting telemetry for {sel_year} {sel_circuit} GP via FastF1 API..."):
        try:
            df = load_race_laps(sel_year, sel_circuit)
            st.session_state.lap_data = df
            st.session_state.loaded_label = f"{sel_year} {sel_circuit}"
            st.success(f"✓ Ingested {len(df):,} valid racing laps from {sel_year} {sel_circuit} GP")
        except Exception as e:
            st.error(f"Failed to load data: {e}")
            st.info("Tip: If live download fails, FastF1 caching will attempt fallback.")

df = st.session_state.lap_data

if df is not None:
    st.markdown("---")

    # Metrics
    st.markdown(f"### 2. Telemetry Overview // {st.session_state.loaded_label}")
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Total Recorded Laps", f"{len(df):,}")
    m2.metric("Telemetry Drivers", df["Driver"].nunique())
    m3.metric("Pirelli Compounds", df["CompoundCode"].nunique())
    m4.metric("Mean Lap Time", f"{df['LapTimeSeconds'].mean():.2f}s")

    # Fuel vs Raw Lap times
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("#### ⚡ Fuel Load Compensation vs Raw Lap Time")
    st.caption("Removing ~0.035s/lap fuel burn reveals genuine rubber tyre degradation.")

    fig_raw = go.Figure()
    fig_raw.add_trace(go.Scatter(
        x=df["LapNumber"], y=df["LapTimeSeconds"],
        mode="markers", name="Raw Lap Time",
        marker=dict(color="#38bdf8", size=3.5, opacity=0.4),
    ))
    fig_raw.add_trace(go.Scatter(
        x=df["LapNumber"], y=df["FuelCorrectedTime"],
        mode="markers", name="Fuel-Corrected Pace",
        marker=dict(color="#e10600", size=4, opacity=0.6),
    ))
    fig_raw.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(18, 22, 32, 0.7)",
        font=dict(color="#cbd5e1", family="Titillium Web"),
        height=320,
        margin=dict(l=20, r=20, t=15, b=20),
        legend=dict(bgcolor="rgba(10, 14, 22, 0.8)", bordercolor="rgba(255,255,255,0.1)"),
        xaxis=dict(title="Lap Number", showgrid=True, gridcolor="rgba(255,255,255,0.06)", color="#94a3b8"),
        yaxis=dict(title="Lap Time (Seconds)", showgrid=True, gridcolor="rgba(255,255,255,0.06)", color="#94a3b8"),
    )
    st.plotly_chart(fig_raw, use_container_width=True)

    # Tyre Deg by Compound
    st.markdown("#### 🔄 Stint Wear Rates by Compound")
    st.caption("Dots represent individual driver laps. Solid traces show median degradation slopes.")

    fig_deg = go.Figure()
    for code, name in COMPOUND_NAMES.items():
        sub = df[df["CompoundCode"] == code]
        if len(sub) < 5:
            continue
        fig_deg.add_trace(go.Scatter(
            x=sub["TyreAge"], y=sub["FuelCorrectedTime"],
            mode="markers", name=f"{name} (Raw)",
            marker=dict(color=COMPOUND_COLORS[code], size=4, opacity=0.25),
            showlegend=True,
        ))
        trend = sub.groupby("TyreAge")["FuelCorrectedTime"].median().reset_index()
        if len(trend) > 3:
            fig_deg.add_trace(go.Scatter(
                x=trend["TyreAge"], y=trend["FuelCorrectedTime"],
                mode="lines", name=f"{name} Trend",
                line=dict(color=COMPOUND_COLORS[code], width=3),
                showlegend=True,
            ))

    fig_deg.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(18, 22, 32, 0.7)",
        font=dict(color="#cbd5e1", family="Titillium Web"),
        height=350,
        margin=dict(l=20, r=20, t=15, b=20),
        legend=dict(bgcolor="rgba(10, 14, 22, 0.8)", bordercolor="rgba(255,255,255,0.1)"),
        xaxis=dict(title="Tyre Age (Laps on Set)", showgrid=True, gridcolor="rgba(255,255,255,0.06)", color="#94a3b8"),
        yaxis=dict(title="Fuel-Corrected Pace (Seconds)", showgrid=True, gridcolor="rgba(255,255,255,0.06)", color="#94a3b8"),
    )
    st.plotly_chart(fig_deg, use_container_width=True)

    # Driver comparison
    st.markdown("#### 🏎️ Per-Driver Pace Distribution")
    driver_filter = st.multiselect(
        "Compare Driver Telemetry", sorted(df["Driver"].unique()),
        default=sorted(df["Driver"].unique())[:5]
    )
    sub_drv = df[df["Driver"].isin(driver_filter)] if driver_filter else df

    fig_box = px.box(
        sub_drv, x="Driver", y="FuelCorrectedTime",
        color="Driver", points=False,
    )
    fig_box.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(18, 22, 32, 0.7)",
        font=dict(color="#cbd5e1", family="Titillium Web"),
        height=300,
        showlegend=False,
        margin=dict(l=20, r=20, t=15, b=20),
        xaxis=dict(showgrid=False, color="#94a3b8"),
        yaxis=dict(showgrid=True, gridcolor="rgba(255,255,255,0.06)", color="#94a3b8", title="Corrected Lap Time (s)"),
    )
    st.plotly_chart(fig_box, use_container_width=True)

    # Train Model Section
    st.markdown("---")
    st.markdown("### 3. LightGBM Quantile Model Calibration")
    st.caption("Fit quantile regressors (P10, P50, P90) to provide uncertainty bounds for this specific circuit.")

    train_col1, train_col2 = st.columns([3, 1])
    with train_col1:
        st.info(
            f"Training dataset contains **{len(df):,} laps** from {st.session_state.loaded_label}. "
            f"Model weights will be persisted to `saved_models/tyre_model_{sel_circuit}.joblib`."
        )
    with train_col2:
        train_btn = st.button("🧠 TRAIN LIGHTGBM MODEL", type="primary", use_container_width=True)

    if train_btn:
        progress = st.progress(0, "Initiating telemetry pipeline...")
        try:
            progress.progress(20, "Extracting features...")
            model = TyreDegModel(circuit=sel_circuit)
            progress.progress(50, "Fitting Quantile Regressors (P10, P50, P90)...")
            result = model.train(df)
            progress.progress(90, "Saving weights to disk...")
            model.save()
            progress.progress(100, "Calibration Complete!")
            st.success(f"✅ Model trained! Validation MAE: **{result['mae']:.3f}s** across {result['n_laps']:,} laps")

            # Preview predictions
            st.markdown("#### Model Calibration Preview (Confidence Bands)")
            ages = list(range(1, 35))
            preview_data = []
            for code, name in [(0, "SOFT"), (1, "MEDIUM"), (2, "HARD")]:
                for age in ages:
                    pred = model.predict_lap_time(code, age)
                    preview_data.append({
                        "TyreAge": age, "Compound": name,
                        "P10": pred["p10"], "P50": pred["p50"], "P90": pred["p90"]
                    })
            prev_df = pd.DataFrame(preview_data)

            fig_prev = go.Figure()
            for name, color in [("SOFT", "#e10600"), ("MEDIUM", "#ffd600"), ("HARD", "#ffffff")]:
                sub = prev_df[prev_df["Compound"] == name]
                fig_prev.add_trace(go.Scatter(x=sub["TyreAge"], y=sub["P50"], name=name,
                                              line=dict(color=color, width=2.5), mode="lines"))
                fig_prev.add_trace(go.Scatter(
                    x=list(sub["TyreAge"]) + list(sub["TyreAge"])[::-1],
                    y=list(sub["P90"]) + list(sub["P10"])[::-1],
                    fill="toself", fillcolor=color, opacity=0.12,
                    line=dict(color="rgba(0,0,0,0)"), showlegend=False, name=f"{name} Uncertainty"
                ))
            fig_prev.update_layout(
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(18, 22, 32, 0.7)",
                font=dict(color="#cbd5e1", family="Titillium Web"),
                height=320,
                margin=dict(l=20, r=20, t=15, b=20),
                legend=dict(bgcolor="rgba(10, 14, 22, 0.8)", bordercolor="rgba(255,255,255,0.1)"),
                xaxis=dict(title="Tyre Age (Laps)", showgrid=True, gridcolor="rgba(255,255,255,0.06)", color="#94a3b8"),
                yaxis=dict(title="Predicted Lap Time (s)", showgrid=True, gridcolor="rgba(255,255,255,0.06)", color="#94a3b8"),
            )
            st.plotly_chart(fig_prev, use_container_width=True)

        except Exception as e:
            progress.empty()
            st.error(f"Training failed: {e}")
else:
    st.info("👆 Select a championship season and grand prix circuit above, then click **Ingest FastF1 Telemetry**.")
