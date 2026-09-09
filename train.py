"""
train.py
--------
Train the tyre degradation model on historical FastF1 data.

Run this ONCE before launching the Streamlit app:
    python train.py

It downloads race data, trains a LightGBM model per circuit,
and saves them to saved_models/ for use in the dashboard.

Typical training time: 3–8 minutes depending on circuits selected.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

import pandas as pd
import warnings
warnings.filterwarnings("ignore")

from data.loader import load_race_laps, load_multi_race
from models.tyre_model import TyreDegModel

# ─── Configuration ────────────────────────────────────────────────────────────
# Circuits to train on — start with 3–4 to keep training fast,
# then add more for better generalisation
TRAIN_CIRCUITS = [
    "Bahrain",
    "Britain",
    "Monza",
    "Spain",
]

# Train on multiple years for more data
TRAIN_YEARS = [2022, 2023]

# Circuit to use for the "global" fallback model (trained on all circuits)
TRAIN_GLOBAL = True
# ──────────────────────────────────────────────────────────────────────────────


def train_circuit_model(circuit: str, years: list) -> dict:
    """Train a model for a single circuit using multiple years of data."""
    all_dfs = []
    for year in years:
        try:
            df = load_race_laps(year, circuit)
            df["Year"] = year
            all_dfs.append(df)
            print(f"  ✓ {year} {circuit}: {len(df)} laps loaded")
        except Exception as e:
            print(f"  ✗ {year} {circuit}: {e}")

    if not all_dfs:
        print(f"  No data for {circuit} — skipping.")
        return {"circuit": circuit, "status": "skipped"}

    combined = pd.concat(all_dfs, ignore_index=True)
    print(f"  Training on {len(combined)} laps...")

    model = TyreDegModel(circuit=circuit)
    try:
        result = model.train(combined)
        model.save()
        print(f"  ✓ MAE: {result['mae']:.3f}s  →  saved_models/tyre_model_{circuit}.joblib")
        return {"circuit": circuit, "status": "ok", **result}
    except Exception as e:
        print(f"  ✗ Training failed: {e}")
        return {"circuit": circuit, "status": "error", "error": str(e)}


def train_global_model(circuits: list, years: list) -> dict:
    """Train a global model on all circuits combined."""
    all_dfs = []
    for year in years:
        for circuit in circuits:
            try:
                df = load_race_laps(year, circuit)
                df["Year"]    = year
                df["Circuit"] = circuit
                all_dfs.append(df)
            except Exception:
                pass

    if not all_dfs:
        print("  No data for global model — skipping.")
        return {"status": "skipped"}

    combined = pd.concat(all_dfs, ignore_index=True)
    print(f"  Training global model on {len(combined)} laps from {len(all_dfs)} race-years...")

    model = TyreDegModel(circuit="global")
    try:
        result = model.train(combined)
        model.save()
        print(f"  ✓ Global MAE: {result['mae']:.3f}s  →  saved_models/tyre_model_global.joblib")
        return {"status": "ok", **result}
    except Exception as e:
        print(f"  ✗ Global training failed: {e}")
        return {"status": "error", "error": str(e)}


def main():
    print("=" * 60)
    print("  F1 AI Race Strategist — Tyre Model Training")
    print("=" * 60)
    print()

    results = []

    # Per-circuit models
    print("── Per-circuit models ───────────────────────────────────")
    for circuit in TRAIN_CIRCUITS:
        print(f"\n[{circuit}]")
        result = train_circuit_model(circuit, TRAIN_YEARS)
        results.append(result)

    # Global fallback model
    if TRAIN_GLOBAL:
        print(f"\n── Global model (all circuits combined) ─────────────────")
        result = train_global_model(TRAIN_CIRCUITS, TRAIN_YEARS)
        results.append({"circuit": "global", **result})

    # Summary
    print("\n" + "=" * 60)
    print("  Training Summary")
    print("=" * 60)
    for r in results:
        status = r.get("status", "?")
        circuit = r.get("circuit", "?")
        mae    = f"MAE={r['mae']:.3f}s" if "mae" in r else ""
        icon   = "✓" if status == "ok" else ("−" if status == "skipped" else "✗")
        print(f"  {icon}  {circuit:<20} {status:<10} {mae}")

    print()
    print("  Training complete. Launch the app with:")
    print("  streamlit run app.py")
    print()


if __name__ == "__main__":
    main()
