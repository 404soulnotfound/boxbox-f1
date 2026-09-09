"""
models/simulator.py
-------------------
Vectorized Monte Carlo race simulator.

Runs 10,000 simulations of the remaining race laps for each
candidate strategy and returns the expected finishing position
distribution.

Key design: all simulations run simultaneously using NumPy arrays.
No Python loops over simulations — this keeps 10k runs under 200ms.
"""

import numpy as np
import pandas as pd
from dataclasses import dataclass, field
from typing import Optional


@dataclass
class RaceState:
    """
    Complete snapshot of the race situation at the current lap.
    This is the single source of truth fed to all AI models.
    """
    current_lap:       int
    total_laps:        int
    tyre_age:          int          # laps on current set
    compound_code:     int          # 0=Soft, 1=Medium, 2=Hard
    gap_ahead:         float        # seconds to car in front
    gap_behind:        float        # seconds to car behind
    pit_loss_time:     float = 22.0 # average pit stop time loss for this circuit
    track_temp:        float = 35.0
    air_temp:          float = 25.0
    safety_car_active: bool  = False

    @property
    def laps_remaining(self) -> int:
        return max(0, self.total_laps - self.current_lap)


@dataclass
class StrategyDecision:
    """Output from the strategy engine for one candidate strategy."""
    action:               str         # "PIT_NOW", "PIT_IN_3", "PIT_IN_5", "STAY_OUT"
    pit_lap_offset:       int         # 0 = this lap, 3 = in 3 laps, etc.
    recommended_compound: str         # "SOFT", "MEDIUM", "HARD"
    expected_time_loss:   float       # vs best strategy (seconds)
    confidence:           float       # 0–1 probability this is optimal
    p10_time:             float       # optimistic total race time
    p50_time:             float       # median total race time
    p90_time:             float       # pessimistic total race time
    reasoning:            str         # human-readable explanation
    is_recommended:       bool = False


class MonteCarloSimulator:
    """
    Vectorized Monte Carlo race simulator.

    For each candidate strategy (pit now, pit in 3, pit in 5, stay out),
    runs N simulations of the remaining laps and computes the
    distribution of total lap time (proxy for finishing position).
    """

    # Compound base degradation rates (seconds lost per lap vs fresh)
    # Soft tyres degrade fastest, Hard slowest
    DEG_RATES = {
        0: 0.080,   # Soft
        1: 0.045,   # Medium
        2: 0.022,   # Hard
        3: 0.010,   # Intermediate
        4: 0.005,   # Wet
    }

    COMPOUND_NAMES = {0: "SOFT", 1: "MEDIUM", 2: "HARD", 3: "INTER", 4: "WET"}
    COMPOUND_CODES = {"SOFT": 0, "MEDIUM": 1, "HARD": 2}

    # Safety car probability per lap (historical F1 average ~8% per race)
    SC_PROB_PER_LAP = 0.008

    def __init__(self, tyre_model=None, n_simulations: int = 10_000):
        self.tyre_model    = tyre_model
        self.n_sims        = n_simulations

    def _lap_time_array(
        self,
        compound_code: int,
        tyre_ages: np.ndarray,   # shape (n_laps,)
        base_time: float,
        noise_std: float = 0.15,
        n: int = None,
    ) -> np.ndarray:
        """
        Compute simulated lap times for all sims × all laps at once.
        Shape: (n_sims, n_laps)

        Uses the tyre_model if available, else falls back to a
        simple linear degradation formula.
        """
        n = n or self.n_sims
        n_laps = len(tyre_ages)

        if self.tyre_model and self.tyre_model.is_trained:
            # Vectorized inference: predict p50 for each age
            times_1d = np.array([
                self.tyre_model.predict_lap_time(compound_code, int(age))["p50"]
                for age in tyre_ages
            ])
        else:
            # Fallback: linear degradation model
            deg_rate = self.DEG_RATES.get(compound_code, 0.04)
            times_1d = base_time + deg_rate * tyre_ages

        # Broadcast to (n_sims, n_laps) and add lap-to-lap noise
        times_2d = np.tile(times_1d, (n, 1))                     # (n, n_laps)
        noise    = np.random.normal(0, noise_std, (n, n_laps))
        return times_2d + noise

    def _apply_safety_car(
        self,
        times: np.ndarray,         # (n_sims, n_laps)
        pit_lap_in_stint: int,     # which lap in the remaining stint is the pit
    ) -> np.ndarray:
        """
        Randomly inject safety car events that bunch the field.
        Under SC, gaps are neutralised and a free pit becomes possible.
        """
        n, n_laps = times.shape
        sc_mask = np.random.binomial(1, self.SC_PROB_PER_LAP, (n, n_laps)).astype(bool)

        # SC slows everyone — adds ~20s neutralisation delay spread over 2 laps
        times[sc_mask] += np.random.uniform(8, 12, sc_mask.sum())

        # If SC coincides with pit lap, reduce pit loss time (free pit under SC)
        if pit_lap_in_stint < n_laps:
            sc_on_pit = sc_mask[:, pit_lap_in_stint]
            times[sc_on_pit, pit_lap_in_stint] -= 15.0  # pit ~free under SC

        return times

    def simulate_strategy(
        self,
        state:         RaceState,
        pit_offset:    int,         # 0=now, 3=in 3 laps, 999=stay out
        new_compound:  int,         # compound code after pit
    ) -> dict:
        """
        Run N simulations for a single strategy.

        Returns
        -------
        dict with p10, p50, p90 total race time across simulations
        """
        L  = state.laps_remaining
        N  = self.n_sims

        if L <= 0:
            return {"p10": 0, "p50": 0, "p90": 0, "mean": 0}

        # Base reference lap time (we use a neutral ~90s if no model)
        base_time = (
            self.tyre_model.baseline_lt
            if self.tyre_model and self.tyre_model.is_trained and self.tyre_model.baseline_lt
            else 90.0
        )

        total_times = np.zeros(N)

        if pit_offset >= L or pit_offset == 999:
            # STAY OUT — run the entire stint on current tyres
            tyre_ages = np.arange(state.tyre_age, state.tyre_age + L)
            times = self._lap_time_array(state.compound_code, tyre_ages, base_time)
            times = self._apply_safety_car(times, pit_lap_in_stint=L + 1)
            total_times = times.sum(axis=1)
        else:
            # PIT on lap `pit_offset` from now

            # --- Pre-pit stint ---
            pre_laps = pit_offset
            if pre_laps > 0:
                ages_pre = np.arange(state.tyre_age, state.tyre_age + pre_laps)
                t_pre    = self._lap_time_array(state.compound_code, ages_pre, base_time)
                t_pre    = self._apply_safety_car(t_pre, pit_lap_in_stint=pit_offset)
                total_times += t_pre.sum(axis=1)

            # --- Pit stop time loss ---
            pit_noise  = np.random.normal(state.pit_loss_time, 1.5, N)  # ±1.5s variability
            total_times += pit_noise

            # --- Post-pit stint ---
            post_laps = L - pre_laps
            if post_laps > 0:
                ages_post = np.arange(1, post_laps + 1)
                t_post    = self._lap_time_array(new_compound, ages_post, base_time)
                t_post    = self._apply_safety_car(t_post, pit_lap_in_stint=L + 1)
                total_times += t_post.sum(axis=1)

        return {
            "p10":  float(np.percentile(total_times, 10)),
            "p50":  float(np.percentile(total_times, 50)),
            "p90":  float(np.percentile(total_times, 90)),
            "mean": float(np.mean(total_times)),
        }

    def compute_best_strategy(
        self,
        state:          RaceState,
        candidate_pits: list = None,
        new_compound:   int  = 1,    # default: Medium
    ) -> list:
        """
        Evaluate all candidate strategies and rank by median total time.

        Parameters
        ----------
        state          : Current race state
        candidate_pits : List of pit offsets to evaluate. Auto-generated if None.
        new_compound   : Compound code to put on after pit

        Returns
        -------
        List of StrategyDecision objects sorted by expected performance
        """
        if candidate_pits is None:
            L = state.laps_remaining
            candidate_pits = [
                offset for offset in [0, 2, 4, 6, 999]
                if offset == 999 or offset < L - 3
            ]

        action_labels = {
            0:   "PIT NOW",
            2:   "PIT IN 2",
            4:   "PIT IN 4",
            6:   "PIT IN 6",
            999: "STAY OUT",
        }

        results = []
        for offset in candidate_pits:
            sim = self.simulate_strategy(state, offset, new_compound)
            results.append({
                "offset": offset,
                "label":  action_labels.get(offset, f"PIT IN {offset}"),
                **sim,
            })

        # Sort by median time (lower = better)
        results.sort(key=lambda r: r["p50"])
        best_p50 = results[0]["p50"]

        decisions = []
        total_confidence = 0.0

        for i, r in enumerate(results):
            # Confidence: based on how much worse this strategy is vs best
            time_gap   = r["p50"] - best_p50
            confidence = max(0.0, 1.0 - (time_gap / max(1.0, best_p50)) * 50)
            total_confidence += confidence

            compound_name = self.COMPOUND_NAMES.get(new_compound, "MEDIUM")

            # Human-readable reasoning
            if r["offset"] == 999:
                reasoning = (
                    f"Stay out on current {self.COMPOUND_NAMES.get(state.compound_code,'?')} "
                    f"(age {state.tyre_age} laps). "
                    f"Expected {state.laps_remaining} laps to end. "
                    f"Median total time: {r['p50']:.1f}s."
                )
            else:
                offset_val = r['offset']
                timing_str = 'now' if offset_val == 0 else f'in {offset_val} laps'
                reasoning = (
                    f"Pit {timing_str} for {compound_name}. "
                    f"Pit loss ~{state.pit_loss_time:.0f}s. "
                    f"Gap ahead: {state.gap_ahead:.1f}s | Gap behind: {state.gap_behind:.1f}s. "
                    f"Median total time: {r['p50']:.1f}s."
                )

            decisions.append(StrategyDecision(
                action               = r["label"],
                pit_lap_offset       = r["offset"],
                recommended_compound = compound_name if r["offset"] != 999 else self.COMPOUND_NAMES.get(state.compound_code, "?"),
                expected_time_loss   = round(r["p50"] - best_p50, 2),
                confidence           = round(confidence, 3),
                p10_time             = round(r["p10"], 2),
                p50_time             = round(r["p50"], 2),
                p90_time             = round(r["p90"], 2),
                reasoning            = reasoning,
                is_recommended       = (i == 0),
            ))

        # Normalise confidence to sum to 1
        if total_confidence > 0:
            for d in decisions:
                d.confidence = round(d.confidence / total_confidence, 3)

        return decisions


def estimate_undercut(
    state:         RaceState,
    tyre_deg_delta: float = 0.06,  # seconds per lap we gain vs opponent on fresh tyres
) -> dict:
    """
    Estimate whether an undercut (pit now) gains position vs the car ahead.

    Undercut works when:
        pit_loss_time < (laps_to_recover × tyre_deg_delta_per_lap)

    Returns
    -------
    dict with: viable (bool), laps_to_recover (float), recommendation (str)
    """
    if state.gap_ahead <= 0:
        return {"viable": False, "laps_to_recover": None, "recommendation": "No car ahead to undercut."}

    # How many laps on fresh rubber to recover the pit stop time loss?
    laps_to_recover = state.pit_loss_time / max(tyre_deg_delta, 0.001)

    # Undercut is viable if we can recover within remaining laps
    viable = laps_to_recover < state.laps_remaining and state.gap_ahead < state.pit_loss_time * 1.5

    recommendation = (
        f"UNDERCUT VIABLE — recover gap in ~{laps_to_recover:.1f} laps "
        f"(gap ahead: {state.gap_ahead:.1f}s, pit loss: {state.pit_loss_time:.0f}s)"
        if viable else
        f"Undercut unlikely — need {laps_to_recover:.1f} laps to recover "
        f"but only {state.laps_remaining} remain."
    )

    return {
        "viable":           viable,
        "laps_to_recover":  round(laps_to_recover, 1),
        "recommendation":   recommendation,
    }


def safety_car_probability(
    circuit_base_rate: float = 0.40,   # historical SC rate for this circuit (0–1 per race)
    laps_remaining:    int   = 20,
    total_laps:        int   = 57,
) -> float:
    """
    Estimate probability that a safety car occurs in the remaining laps.
    Simple Poisson model — assume SC events are ~Poisson distributed.

    Returns float in [0, 1]
    """
    # Expected number of SC events in remaining proportion of race
    remaining_fraction = laps_remaining / max(total_laps, 1)
    expected_events    = circuit_base_rate * remaining_fraction

    # P(at least one event) = 1 - P(zero events) under Poisson
    prob = 1.0 - np.exp(-expected_events)
    return round(float(np.clip(prob, 0.0, 1.0)), 3)
