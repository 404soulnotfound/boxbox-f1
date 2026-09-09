# 🏎️ BOX BOX // F1 AI Race Strategist

> A high-performance Formula 1 pit wall race strategy suite using real telemetry data.
> Models tyre degradation, runs Monte Carlo race simulations, and recommends
> optimal pit windows — engineered by **Soumili Pal**.

![Python](https://img.shields.io/badge/Python-3.10+-blue)
![Streamlit](https://img.shields.io/badge/Streamlit-1.35+-red)
![FastF1](https://img.shields.io/badge/FastF1-3.3+-orange)
![LightGBM](https://img.shields.io/badge/LightGBM-4.3+-green)

---

## What it does

| Feature | Description |
|---|---|
| 🧠 Tyre degradation model | LightGBM trained on real FastF1 data, predicts lap time per compound/age |
| 🎲 Monte Carlo simulator | 10,000 simulations of remaining race laps per strategy in <200ms |
| 🎯 Pit window optimiser | Ranks all strategies by expected finishing performance |
| ⚔️ Undercut detector | Calculates whether pitting now gains position vs the car ahead |
| 🚨 Safety car probability | Poisson-based SC probability for remaining laps |
| 📊 Strategy backtest | Replay any historical race, compare AI calls to reality |

---

## Project structure

```
boxbox-f1/
├── app.py                      # Streamlit homepage & pit wall telemetry
├── train.py                    # Offline model training script
├── requirements.txt
├── .streamlit/
│   └── config.toml             # F1 dark racing theme configuration
├── data/
│   └── loader.py               # FastF1 data loader + fuel correction
├── models/
│   ├── tyre_model.py           # LightGBM tyre degradation model
│   └── simulator.py            # Monte Carlo race simulator
├── pages/
│   ├── 1_Strategy_Simulator.py # Main strategy dashboard
│   ├── 2_Tyre_Analysis.py      # Data exploration + model training UI
│   ├── 3_Backtest.py           # Historical race backtesting
│   ├── 4_About.py              # Architecture & technical methodology
│   └── 5_Circuit_Compare.py    # Cross-circuit tyre wear comparison
├── utils/
│   ├── demo_data.py            # Built-in calibrated profiles
│   └── ui_theme.py             # Pit wall theme components & telemetry bar
├── saved_models/               # Trained .joblib files (auto-created)
└── cache/                      # FastF1 data cache (auto-created)
```

---

## Quick start

### 1. Clone and install
```bash
git clone https://github.com/404soulnotfound/boxbox-f1.git
cd boxbox-f1
pip install -r requirements.txt
```

### 2. Train models (two options)

**Option A — via terminal (trains all circuits at once, ~5 mins):**
```bash
python train.py
```

**Option B — via the app UI:**
```bash
streamlit run app.py
# Then go to: Tyre Analysis → load a race → click Train Model
```

### 3. Launch the app
```bash
streamlit run app.py
```

---

## Key concepts implemented

### Fuel load correction
Raw lap times improve naturally as fuel burns off (~0.035s per kg per lap).
Without correction, the model mistakes fuel saving for tyre health.

```python
FuelCorrectedTime = LapTimeSeconds - (FuelLoad_kg × 0.035)
```

### Monte Carlo simulation
All 10,000 simulations run simultaneously using NumPy array broadcasting —
no Python for-loops over simulations. This keeps 10k runs under 200ms.

```python
times_2d = np.tile(times_1d, (n_sims, 1))   # shape: (10000, n_laps)
noise    = np.random.normal(0, 0.15, (n_sims, n_laps))
result   = times_2d + noise
```

### Undercut viability
```
Undercut viable if: laps_to_recover_gap < laps_remaining
where: laps_to_recover = pit_loss_time / deg_rate_delta_per_lap
```

### Safety car probability (Poisson model)
```python
P(SC in remaining laps) = 1 - exp(-circuit_rate × remaining_fraction)
```

---

## Data sources

- **FastF1** — Official F1 timing and telemetry data (2018–present)
- **OpenF1 API** — Real-time timing during live sessions
- All data is publicly available under the FastF1 license

---

## Deploy to Streamlit Cloud (free)

1. Push to GitHub
2. Go to [share.streamlit.io](https://share.streamlit.io)
3. Connect your repo → select `app.py` → deploy
4. Share the URL on your portfolio / LinkedIn

**Note:** The training step requires FastF1 which downloads data.
Pre-train models locally, commit the `saved_models/` folder to your repo,
and Streamlit Cloud will use those cached models directly.

---

## Portfolio talking points

- **Real data, real problem** — Uses official F1 telemetry from FastF1, not synthetic data
- **Monte Carlo simulation** — Probabilistic reasoning, not just deterministic optimization
- **Fuel correction** — Domain knowledge applied correctly, not just ML on raw numbers
- **Per-circuit models** — Understands that Monza ≠ Monaco for tyre behaviour
- **Uncertainty quantification** — P10/P50/P90 intervals, not just point predictions
- **Backtest validation** — AI decisions compared against real-world outcomes

---

## Author & Contact

**Soumili Pal**  
- 🐙 GitHub: [@404soulnotfound](https://github.com/404soulnotfound)
- 💼 LinkedIn: [soumilipal](https://www.linkedin.com/in/soumilipal)
- 📧 Email: [tidha427@gmail.com](mailto:tidha427@gmail.com)

---

## Disclaimer

This is an independent open-source telemetry and machine learning system. Not affiliated with Formula 1, FOM, or the FIA. Uses publicly available timing and telemetry data under FastF1 terms.
