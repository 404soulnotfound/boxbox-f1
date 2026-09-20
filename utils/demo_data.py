"""
utils/demo_data.py
------------------
Generates realistic synthetic F1 data so the app is fully functional
even before the user trains a model on real FastF1 data.

Used when:
- No FastF1 data has been downloaded yet
- Running on Streamlit Cloud with no cached models
- User wants to demo the app immediately

All values are calibrated from real F1 season data across all standard calendar circuits.
"""

import numpy as np
import pandas as pd

# Real-world calibrated tyre deg rates (seconds per lap) and parameters
# Covering all standard circuits on the modern F1 calendar
CIRCUIT_PROFILES = {
    "Bahrain": {
        "base_time": 94.0,
        "deg_rates":  {0: 0.085, 1: 0.048, 2: 0.025},  # Soft / Medium / Hard
        "pit_loss":   22.5,
        "sc_rate":    0.30,
        "total_laps": 57,
    },
    "Saudi Arabia": {
        "base_time": 91.5,
        "deg_rates":  {0: 0.045, 1: 0.026, 2: 0.014},
        "pit_loss":   20.5,
        "sc_rate":    0.65,
        "total_laps": 50,
    },
    "Australia": {
        "base_time": 80.5,
        "deg_rates":  {0: 0.055, 1: 0.032, 2: 0.018},
        "pit_loss":   20.0,
        "sc_rate":    0.60,
        "total_laps": 58,
    },
    "Azerbaijan": {
        "base_time": 104.0,
        "deg_rates":  {0: 0.048, 1: 0.028, 2: 0.015},
        "pit_loss":   21.0,
        "sc_rate":    0.55,
        "total_laps": 51,
    },
    "Miami": {
        "base_time": 89.5,
        "deg_rates":  {0: 0.065, 1: 0.038, 2: 0.020},
        "pit_loss":   21.5,
        "sc_rate":    0.40,
        "total_laps": 57,
    },
    "Monaco": {
        "base_time": 74.0,
        "deg_rates":  {0: 0.040, 1: 0.022, 2: 0.012},
        "pit_loss":   28.0,
        "sc_rate":    0.60,
        "total_laps": 78,
    },
    "Spain": {
        "base_time": 78.0,
        "deg_rates":  {0: 0.090, 1: 0.052, 2: 0.028},
        "pit_loss":   22.0,
        "sc_rate":    0.25,
        "total_laps": 66,
    },
    "Canada": {
        "base_time": 75.0,
        "deg_rates":  {0: 0.050, 1: 0.030, 2: 0.016},
        "pit_loss":   19.5,
        "sc_rate":    0.55,
        "total_laps": 70,
    },
    "Austria": {
        "base_time": 68.0,
        "deg_rates":  {0: 0.060, 1: 0.035, 2: 0.019},
        "pit_loss":   20.5,
        "sc_rate":    0.35,
        "total_laps": 71,
    },
    "Britain": {
        "base_time": 89.0,
        "deg_rates":  {0: 0.075, 1: 0.042, 2: 0.020},
        "pit_loss":   21.0,
        "sc_rate":    0.45,
        "total_laps": 52,
    },
    "Hungary": {
        "base_time": 79.5,
        "deg_rates":  {0: 0.080, 1: 0.046, 2: 0.024},
        "pit_loss":   21.0,
        "sc_rate":    0.25,
        "total_laps": 70,
    },
    "Belgium": {
        "base_time": 106.0,
        "deg_rates":  {0: 0.070, 1: 0.040, 2: 0.022},
        "pit_loss":   23.5,
        "sc_rate":    0.45,
        "total_laps": 44,
    },
    "Netherlands": {
        "base_time": 73.0,
        "deg_rates":  {0: 0.082, 1: 0.047, 2: 0.025},
        "pit_loss":   21.5,
        "sc_rate":    0.50,
        "total_laps": 72,
    },
    "Monza": {
        "base_time": 82.0,
        "deg_rates":  {0: 0.030, 1: 0.018, 2: 0.010},
        "pit_loss":   23.0,
        "sc_rate":    0.40,
        "total_laps": 53,
    },
    "Singapore": {
        "base_time": 97.0,
        "deg_rates":  {0: 0.060, 1: 0.034, 2: 0.018},
        "pit_loss":   28.5,
        "sc_rate":    0.80,
        "total_laps": 62,
    },
    "Japan": {
        "base_time": 92.0,
        "deg_rates":  {0: 0.070, 1: 0.038, 2: 0.019},
        "pit_loss":   22.0,
        "sc_rate":    0.35,
        "total_laps": 53,
    },
    "Qatar": {
        "base_time": 85.0,
        "deg_rates":  {0: 0.095, 1: 0.055, 2: 0.030},
        "pit_loss":   24.0,
        "sc_rate":    0.45,
        "total_laps": 57,
    },
    "United States": {
        "base_time": 96.0,
        "deg_rates":  {0: 0.075, 1: 0.043, 2: 0.023},
        "pit_loss":   21.5,
        "sc_rate":    0.40,
        "total_laps": 56,
    },
    "Mexico City": {
        "base_time": 80.0,
        "deg_rates":  {0: 0.050, 1: 0.028, 2: 0.015},
        "pit_loss":   22.5,
        "sc_rate":    0.45,
        "total_laps": 71,
    },
    "São Paulo": {
        "base_time": 73.5,
        "deg_rates":  {0: 0.078, 1: 0.045, 2: 0.024},
        "pit_loss":   21.0,
        "sc_rate":    0.65,
        "total_laps": 71,
    },
    "Las Vegas": {
        "base_time": 94.5,
        "deg_rates":  {0: 0.035, 1: 0.020, 2: 0.011},
        "pit_loss":   21.0,
        "sc_rate":    0.50,
        "total_laps": 50,
    },
    "Abu Dhabi": {
        "base_time": 86.0,
        "deg_rates":  {0: 0.065, 1: 0.036, 2: 0.019},
        "pit_loss":   22.0,
        "sc_rate":    0.35,
        "total_laps": 58,
    },
}

ALL_CIRCUITS = list(CIRCUIT_PROFILES.keys())

DEFAULT_PROFILE = {
    "base_time": 90.0,
    "deg_rates":  {0: 0.080, 1: 0.045, 2: 0.022},
    "pit_loss":   22.0,
    "sc_rate":    0.35,
    "total_laps": 57,
}

COMPOUND_NAMES = {0: "SOFT", 1: "MEDIUM", 2: "HARD"}
DRIVER_CODES   = [
    "VER", "PER", "HAM", "RUS", "LEC", "SAI", "NOR", "PIA", "ALO", "STR",
    "GAS", "OCO", "TSU", "RIC", "ALB", "SAR", "BOT", "ZHO", "HUL", "MAG"
]


def get_circuit_profile(circuit: str) -> dict:
    return CIRCUIT_PROFILES.get(circuit, DEFAULT_PROFILE)


def generate_race_laps(
    circuit:     str = "Bahrain",
    n_drivers:   int = 20,
    random_seed: int = 42,
) -> pd.DataFrame:
    """
    Generate a synthetic but realistic race lap dataset.
    Mimics what FastF1 returns after load_race_laps().
    """
    np.random.seed(random_seed)
    profile    = get_circuit_profile(circuit)
    total_laps = profile["total_laps"]
    base_time  = profile["base_time"]
    deg_rates  = profile["deg_rates"]

    records = []
    driver_list = DRIVER_CODES[:min(n_drivers, len(DRIVER_CODES))]

    for drv_idx, driver in enumerate(driver_list):
        drv_offset = np.random.normal(0, 0.3)
        n_stints = np.random.choice([1, 2], p=[0.2, 0.8])

        if n_stints == 1:
            stints = [(1, total_laps, np.random.choice([1, 2]))]
        else:
            pit_lap = int(np.random.uniform(total_laps * 0.35, total_laps * 0.55))
            c1      = np.random.choice([0, 1])
            c2      = 1 if c1 == 0 else 2
            stints  = [
                (1,           pit_lap,    c1),
                (pit_lap + 1, total_laps, c2),
            ]

        for stint_start, stint_end, compound_code in stints:
            tyre_age_start = 1
            for lap_num in range(stint_start, stint_end + 1):
                tyre_age = tyre_age_start + (lap_num - stint_start)
                fuel_load  = max(0.0, 110.0 - lap_num * 1.6)
                fuel_delta = fuel_load * 0.035
                deg_rate   = deg_rates.get(compound_code, 0.04)
                deg_time   = deg_rate * tyre_age
                noise      = np.random.normal(0, 0.15)
                lap_time   = base_time + drv_offset + deg_time - fuel_delta + noise
                corrected  = lap_time + fuel_delta

                records.append({
                    "Driver":            driver,
                    "LapNumber":         float(lap_num),
                    "CompoundCode":      int(compound_code),
                    "TyreAge":           float(tyre_age),
                    "LapTimeSeconds":    round(lap_time, 3),
                    "FuelCorrectedTime": round(corrected, 3),
                    "AirTemp":           26.0,
                    "TrackTemp":         36.0,
                })

    df = pd.DataFrame(records)
    return df.sort_values(["Driver", "LapNumber"]).reset_index(drop=True)


def generate_stint_curve(
    compound_code: int,
    n_laps:        int  = 30,
    circuit:       str  = "Bahrain",
    noise:         bool = False,
) -> pd.DataFrame:
    """
    Generate a smooth tyre degradation curve for a single compound.
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
