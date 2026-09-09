"""
data/loader.py
--------------
Loads and cleans Formula 1 race data using the FastF1 library.
Handles fuel correction, tyre encoding, and feature extraction.
"""

import fastf1
import pandas as pd
import numpy as np
import os
import warnings
warnings.filterwarnings("ignore")

# Enable FastF1 cache so data isn't re-downloaded every run
CACHE_DIR = os.path.join(os.path.dirname(__file__), "..", "cache")
os.makedirs(CACHE_DIR, exist_ok=True)
fastf1.Cache.enable_cache(CACHE_DIR)

# Constants
FUEL_START_KG      = 110.0   # Max fuel load at race start (FIA rules)
FUEL_BURN_PER_LAP  = 1.6     # Average kg burned per lap
FUEL_TIME_PER_KG   = 0.035   # Each kg of fuel costs ~0.035s per lap

COMPOUND_MAP = {
    "SOFT":         0,
    "MEDIUM":       1,
    "HARD":         2,
    "INTERMEDIATE": 3,
    "WET":          4,
}

COMPOUND_LABELS = {v: k for k, v in COMPOUND_MAP.items()}


def load_race_laps(year: int, circuit: str) -> pd.DataFrame:
    """
    Load all lap data for a race session.
    Returns a cleaned DataFrame with fuel-corrected lap times.

    Parameters
    ----------
    year    : Season year (e.g. 2023)
    circuit : Circuit name as FastF1 understands it (e.g. 'Bahrain', 'Monza')

    Returns
    -------
    pd.DataFrame with columns:
        Driver, LapNumber, CompoundCode, TyreAge,
        LapTimeSeconds, FuelCorrectedTime, AirTemp, TrackTemp, IsValid
    """
    print(f"[Loader] Fetching {year} {circuit} Race...")
    session = fastf1.get_session(year, circuit, "R")
    session.load(telemetry=False, weather=True, messages=False)

    laps = session.laps.copy()

    # Drop laps with no recorded time or compound info
    laps = laps.dropna(subset=["LapTime", "Compound"])

    # Convert LapTime (timedelta) to float seconds
    laps["LapTimeSeconds"] = laps["LapTime"].dt.total_seconds()

    # Remove obvious outliers — pit laps, in/out laps, safety car laps
    laps = laps[laps["LapTimeSeconds"] < laps["LapTimeSeconds"].quantile(0.97)]
    laps = laps[laps["IsPersonalBest"].notna() | laps["LapNumber"] > 1]

    # Fuel load correction
    # As the race progresses, the car gets lighter so laps get faster
    # We subtract this natural improvement to isolate tyre degradation
    laps["FuelLoad"] = FUEL_START_KG - (laps["LapNumber"] * FUEL_BURN_PER_LAP)
    laps["FuelLoad"] = laps["FuelLoad"].clip(lower=0)
    laps["FuelCorrectedTime"] = (
        laps["LapTimeSeconds"] - laps["FuelLoad"] * FUEL_TIME_PER_KG
    )

    # Tyre age (how many laps on the current set)
    laps["TyreAge"] = laps["TyreLife"].fillna(laps.groupby("Driver")["LapNumber"].transform(lambda x: x - x.min()))

    # Compound encoding
    laps["CompoundCode"] = laps["Compound"].map(COMPOUND_MAP).fillna(-1).astype(int)
    laps = laps[laps["CompoundCode"] >= 0]  # drop unknown compounds

    # Weather
    if "AirTemp" not in laps.columns:
        laps["AirTemp"]   = 25.0
        laps["TrackTemp"] = 35.0
    else:
        laps["AirTemp"]   = laps["AirTemp"].fillna(laps["AirTemp"].median())
        laps["TrackTemp"] = laps["TrackTemp"].fillna(laps["TrackTemp"].median())

    result = laps[[
        "Driver", "LapNumber", "CompoundCode", "TyreAge",
        "LapTimeSeconds", "FuelCorrectedTime", "AirTemp", "TrackTemp"
    ]].copy()

    result = result.dropna()
    print(f"[Loader] Loaded {len(result)} valid laps for {len(result['Driver'].unique())} drivers.")
    return result.reset_index(drop=True)


def load_multi_race(year: int, circuits: list) -> pd.DataFrame:
    """
    Load and combine data from multiple races.
    Adds a CircuitID column (0-indexed) for circuit-aware models.
    """
    all_dfs = []
    for i, circuit in enumerate(circuits):
        try:
            df = load_race_laps(year, circuit)
            df["Circuit"]   = circuit
            df["CircuitID"] = i
            all_dfs.append(df)
        except Exception as e:
            print(f"[Loader] Could not load {circuit}: {e}")

    if not all_dfs:
        raise ValueError("No data could be loaded for any circuit.")

    combined = pd.concat(all_dfs, ignore_index=True)
    print(f"[Loader] Combined dataset: {len(combined)} laps across {len(all_dfs)} circuits.")
    return combined


def get_available_circuits(year: int = 2023) -> list:
    """Return a hard-coded list of common F1 circuits for the given year."""
    circuits_2023 = [
        "Bahrain", "Saudi Arabia", "Australia", "Azerbaijan",
        "Miami", "Monaco", "Spain", "Canada", "Austria",
        "Britain", "Hungary", "Belgium", "Netherlands",
        "Italy", "Singapore", "Japan", "Qatar",
        "United States", "Mexico City", "São Paulo", "Las Vegas", "Abu Dhabi"
    ]
    return circuits_2023
