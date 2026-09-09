"""
utils/demo_data.py
------------------
Generates realistic synthetic F1 data so the app is fully functional
even before the user trains a model on real FastF1 data.

Used when:
- No FastF1 data has been downloaded yet
- Running on Streamlit Cloud with no cached models
- User wants to demo the app immediately

All values are calibrated from real 2023 F1 season data.
"""

import numpy as np
import pandas as pd

# Real-world calibrated tyre deg rates (seconds per lap)
# Source: FastF1 2023 season analysis
CIRCUIT_PROFILES = {
    "Bahrain": {
        "base_time": 94.0,
        "deg_rates":  {0: 0.085, 1: 0.048, 2: 0.025},  # Soft / Medium / Hard
        "pit_loss":   22.5,
        "sc_rate":    0.30,
        "total_laps": 57,
    },
    "Britain": {
        "base_time": 89.0,
        "deg_rates":  {0: 0.075, 1: 0.042, 2: 0.020},
        "pit_loss":   21.0,
        "sc_rate":    0.45,
        "total_laps": 52,
    },
    "Monza": {
        "base_time": 82.0,
        "deg_rates":  {0: 0.030, 1: 0.018, 2: 0.010},  # Low deg — fast circuit
        "pit_loss":   23.0,
        "sc_rate":    0.50,
        "total_laps": 53,
    },
    "Spain": {
        "base_time": 78.0,
        "deg_rates":  {0: 0.090, 1: 0.052, 2: 0.028},  # High deg — abrasive
        "pit_loss":   22.0,
        "sc_rate":    0.25,
        "total_laps": 66,
    },
    "Monaco": {
        "base_time": 74.0,
        "deg_rates":  {0: 0.040, 1: 0.022, 2: 0.012},  # Low deg — low speed
        "pit_loss":   28.0,  # Long pit lane
        "sc_rate":    0.55,
        "total_laps": 78,
    },
    "Japan": {
        "base_time": 92.0,
        "deg_rates":  {0: 0.070, 1: 0.038, 2: 0.019},
        "pit_loss":   22.0,
        "sc_rate":    0.35,
        "total_laps": 53,
    },
}

DEFAULT_PROFILE = {
    "base_time": 90.0,
    "deg_rates":  {0: 0.080, 1: 0.045, 2: 0.022},
    "pit_loss":   22.0,
    "sc_rate":    0.35,
    "total_laps": 57,
}

COMPOUND_NAMES = {0: "SOFT", 1: "MEDIUM", 2: "HARD"}
DRIVER_CODES   = ["VER", "PER", "HAM", "RUS", "LEC", "SAI", "NOR", "PIA", "ALO", "STR"]


def get_circuit_profile(circuit: str) -> dict:
    return CIRCUIT_PROFILES.get(circuit, DEFAULT_PROFILE)


def generate_race_laps(
    circuit:     str = "Bahrain",
    n_drivers:   int = 10,
    random_seed: int = 42,
) -> pd.DataFrame:
    """
    Generate a synthetic but realistic race lap dataset.
    Mimics what FastF1 returns after load_race_laps().

    Each driver gets:
    - 1 or 2 stints with realistic tyre age progression
    - Lap times following the circuit's degradation profile
    - Realistic noise on each lap

    Returns
    -------
    pd.DataFrame with columns matching loader.py output:
        Driver, LapNumber, CompoundCode, TyreAge,
        LapTimeSeconds, FuelCorrectedTime, AirTemp, TrackTemp
    """
    np.random.seed(random_seed)
    profile    = get_circuit_profile(circuit)
    total_laps = profile["total_laps"]
    base_time  = profile["base_time"]
    deg_rates  = profile["deg_rates"]

    records = []

    for drv_idx in range(min(n_drivers, len(DRIVER_CODES))):
        driver = DRIVER_CODES[drv_idx]

        # Driver performance offset (some drivers are faster)
        drv_offset = np.random.normal(0, 0.3)

        # Strategy: 1 or 2 stints
        n_stints = np.random.choice([1, 2], p=[0.2, 0.8])

        if n_stints == 1:
            stints = [(1, total_laps, np.random.choice([1, 2]))]  # Medium or Hard
        else:
            pit_lap = int(np.random.uniform(total_laps * 0.35, total_laps * 0.55))
            c1      = np.random.choice([0, 1])   # Soft or Medium first
            c2      = 1 if c1 == 0 else 2        # Medium or Hard second
            stints  = [
                (1,           pit_lap,    c1),
                (pit_lap + 1, total_laps, c2),
            ]

        for stint_start, stint_end, compound_code in stints:
            tyre_age_start = 1
            for lap_num in range(stint_start, stint_end + 1):
                tyre_age = tyre_age_start + (lap_num - stint_start)

                # Fuel load (decreasing through race)
                fuel_load  = max(0.0, 110.0 - lap_num * 1.6)
                fuel_delta = fuel_load * 0.035  # time saved by being lighter

                # Tyre degradation: base + deg_rate × tyre_age
                deg_rate   = deg_rates.get(compound_code, 0.04)
                deg_time   = deg_rate * tyre_age

                # Fuel-corrected lap time (what the tyre model sees)
                fc_time = base_time + deg_time + drv_offset + np.random.normal(0, 0.12)

                # Raw lap time = fuel-corrected + fuel benefit
                raw_time = fc_time + fuel_delta

                # Track conditions (slowly warming through race)
                track_temp = 38.0 + lap_num * 0.05 + np.random.normal(0, 0.5)
                air_temp   = track_temp - 8.0

                records.append({
                    "Driver":            driver,
                    "LapNumber":         lap_num,
                    "CompoundCode":      compound_code,
                    "TyreAge":           tyre_age,
                    "LapTimeSeconds":    round(raw_time, 3),
                    "FuelCorrectedTime": round(fc_time,  3),
                    "AirTemp":           round(air_temp, 1),
                    "TrackTemp":         round(track_temp, 1),
                })

    df = pd.DataFrame(records)
    return df.sort_values(["Driver", "LapNumber"]).reset_index(drop=True)


def generate_stint_curve(
    compound_code: int,
    n_laps:        int  = 35,
    circuit:       str  = "Bahrain",
    noise:         bool = False,
) -> pd.DataFrame:
    """
    Generate a smooth tyre degradation curve for a single compound.
    Used for plotting when no trained model is available.
    """
    profile   = get_circuit_profile(circuit)
    base_time = profile["base_time"]
    deg_rate  = profile["deg_rates"].get(compound_code, 0.04)

    ages  = np.arange(1, n_laps + 1)
    times = base_time + deg_rate * ages

    if noise:
        times += np.random.normal(0, 0.08, len(ages))

    return pd.DataFrame({
        "TyreAge": ages,
        "p10":     times - 0.20,
        "p50":     times,
        "p90":     times + 0.25,
        "DegVsFresh": deg_rate * ages,
    })


def get_demo_race_state(circuit: str = "Bahrain") -> dict:
    """
    Return a realistic pre-filled race state for the given circuit.
    Used to pre-populate the Strategy Simulator sidebar.
    """
    profile = get_circuit_profile(circuit)
    return {
        "total_laps":   profile["total_laps"],
        "current_lap":  int(profile["total_laps"] * 0.48),
        "compound":     "MEDIUM",
        "tyre_age":     16,
        "gap_ahead":    4.2,
        "gap_behind":   1.9,
        "pit_loss":     profile["pit_loss"],
        "track_temp":   38,
        "sc_rate_pct":  int(profile["sc_rate"] * 100),
    }
