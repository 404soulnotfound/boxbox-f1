"""
models/tyre_model.py
--------------------
Trains and serves a LightGBM tyre degradation model.

What it predicts:
    Fuel-corrected lap time given compound, tyre age, and temperature.

Why LightGBM:
    Fast, handles tabular data well, supports quantile regression
    so we get uncertainty intervals (p10/p50/p90) for free.
"""

import numpy as np
import pandas as pd
import lightgbm as lgb
import joblib
import os
from sklearn.model_selection import GroupShuffleSplit
from sklearn.metrics import mean_absolute_error

MODEL_DIR = os.path.join(os.path.dirname(__file__), "..", "saved_models")
os.makedirs(MODEL_DIR, exist_ok=True)

FEATURES = ["CompoundCode", "TyreAge", "AirTemp", "TrackTemp"]
TARGET   = "FuelCorrectedTime"


class TyreDegModel:
    """
    Wraps three LightGBM models (p10, p50, p90) for probabilistic
    lap time prediction as a function of tyre state.
    """

    def __init__(self, circuit: str = "global"):
        self.circuit     = circuit
        self.model_p10   = None
        self.model_p50   = None
        self.model_p90   = None
        self.baseline_lt = None  # median lap time on fresh tyre (reference)
        self.mae         = None
        self.is_trained  = False

    # ------------------------------------------------------------------
    # Training
    # ------------------------------------------------------------------

    def train(self, df: pd.DataFrame) -> dict:
        """
        Train three quantile regression models on lap data.

        Parameters
        ----------
        df : DataFrame with at least FEATURES + TARGET columns

        Returns
        -------
        dict with validation MAE and sample count
        """
        df = df.dropna(subset=FEATURES + [TARGET]).copy()

        if len(df) < 50:
            raise ValueError(f"Not enough data to train ({len(df)} laps). Need at least 50.")

        X = df[FEATURES].values
        y = df[TARGET].values

        # Store baseline: median lap time when tyre is 1–3 laps old (fresh)
        fresh_mask = df["TyreAge"] <= 3
        self.baseline_lt = float(df.loc[fresh_mask, TARGET].median()) if fresh_mask.sum() > 0 else float(y.min())

        # Train/val split by driver (group) so the same driver's laps
        # don't appear in both train and val
        groups = df["Driver"].values if "Driver" in df.columns else np.arange(len(df))
        splitter = GroupShuffleSplit(n_splits=1, test_size=0.2, random_state=42)
        train_idx, val_idx = next(splitter.split(X, y, groups))

        X_train, X_val = X[train_idx], X[val_idx]
        y_train, y_val = y[train_idx], y[val_idx]

        lgb_params = dict(
            objective      = "quantile",
            n_estimators   = 400,
            learning_rate  = 0.05,
            num_leaves     = 31,
            min_child_samples = 10,
            verbose        = -1,
        )

        self.model_p10 = lgb.LGBMRegressor(**lgb_params, alpha=0.1)
        self.model_p50 = lgb.LGBMRegressor(**lgb_params, alpha=0.5)
        self.model_p90 = lgb.LGBMRegressor(**lgb_params, alpha=0.9)

        for model in [self.model_p10, self.model_p50, self.model_p90]:
            model.fit(X_train, y_train,
                      eval_set=[(X_val, y_val)],
                      callbacks=[lgb.early_stopping(50, verbose=False),
                                 lgb.log_evaluation(period=-1)])

        val_pred  = self.model_p50.predict(X_val)
        self.mae  = float(mean_absolute_error(y_val, val_pred))
        self.is_trained = True

        print(f"[TyreModel] Trained on {len(X_train)} laps | Val MAE: {self.mae:.3f}s")
        return {"mae": self.mae, "n_laps": len(df), "circuit": self.circuit}

    # ------------------------------------------------------------------
    # Inference
    # ------------------------------------------------------------------

    def predict_lap_time(
        self,
        compound_code: int,
        tyre_age: int,
        air_temp:   float = 25.0,
        track_temp: float = 35.0,
    ) -> dict:
        """
        Predict lap time (seconds) for a given tyre state.

        Returns
        -------
        dict with keys: p10, p50, p90, degradation_vs_fresh
        """
        if not self.is_trained:
            raise RuntimeError("Model not trained. Call .train() first.")

        X = np.array([[compound_code, tyre_age, air_temp, track_temp]])

        p10 = float(self.model_p10.predict(X)[0])
        p50 = float(self.model_p50.predict(X)[0])
        p90 = float(self.model_p90.predict(X)[0])

        deg = p50 - self.baseline_lt if self.baseline_lt else 0.0

        return {"p10": p10, "p50": p50, "p90": p90, "degradation_vs_fresh": deg}

    def predict_stint(
        self,
        compound_code: int,
        start_age:    int,
        n_laps:       int,
        air_temp:     float = 25.0,
        track_temp:   float = 35.0,
    ) -> pd.DataFrame:
        """
        Predict lap times for an entire stint (start_age → start_age + n_laps).

        Returns
        -------
        DataFrame with columns: TyreAge, p10, p50, p90, DegVsFresh
        """
        rows = []
        for age in range(start_age, start_age + n_laps):
            pred = self.predict_lap_time(compound_code, age, air_temp, track_temp)
            rows.append({"TyreAge": age, **pred, "DegVsFresh": pred["degradation_vs_fresh"]})
        return pd.DataFrame(rows)

    # ------------------------------------------------------------------
    # Persistence
    # ------------------------------------------------------------------

    def save(self):
        path = os.path.join(MODEL_DIR, f"tyre_model_{self.circuit}.joblib")
        joblib.dump(self, path)
        print(f"[TyreModel] Saved to {path}")

    @classmethod
    def load(cls, circuit: str = "global") -> "TyreDegModel":
        path = os.path.join(MODEL_DIR, f"tyre_model_{circuit}.joblib")
        if not os.path.exists(path):
            raise FileNotFoundError(f"No saved model for circuit '{circuit}'. Train first.")
        model = joblib.load(path)
        print(f"[TyreModel] Loaded from {path}")
        return model

    @classmethod
    def is_saved(cls, circuit: str) -> bool:
        path = os.path.join(MODEL_DIR, f"tyre_model_{circuit}.joblib")
        return os.path.exists(path)
