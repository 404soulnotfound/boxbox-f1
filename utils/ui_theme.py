"""
utils/ui_theme.py
-----------------
Shared styling, CSS components, and telemetry header for Box Box F1.
"""

import streamlit as st

def inject_f1_theme():
    st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Titillium+Web:ital,wght@0,300;0,400;0,600;0,700;0,900;1,700&family=JetBrains+Mono:wght@400;600;700&display=swap');

        html, body, [class*="css"] {
            font-family: 'Titillium Web', -apple-system, BlinkMacSystemFont, sans-serif;
            color: #e6e8ec;
        }

        /* App Background */
        .stApp {
            background-color: #07090e;
            background-image: 
                radial-gradient(at 0% 0%, rgba(225, 6, 0, 0.08) 0px, transparent 50%),
                radial-gradient(at 100% 100%, rgba(30, 41, 59, 0.25) 0px, transparent 50%),
                linear-gradient(rgba(255, 255, 255, 0.015) 1px, transparent 1px),
                linear-gradient(90deg, rgba(255, 255, 255, 0.015) 1px, transparent 1px);
            background-size: 100% 100%, 100% 100%, 36px 36px, 36px 36px;
        }

        /* Headers */
        h1, h2, h3, h4 {
            font-family: 'Titillium Web', sans-serif !important;
            font-weight: 800 !important;
            letter-spacing: 0.5px;
            text-transform: uppercase;
        }

        /* Monospace / Telemetry values */
        .telemetry-font {
            font-family: 'JetBrains Mono', monospace !important;
        }

        /* Top Pit Wall Ticker */
        .pit-wall-banner {
            background: linear-gradient(90deg, #111622 0%, #171e2e 50%, #111622 100%);
            border: 1px solid rgba(225, 6, 0, 0.3);
            border-left: 4px solid #e10600;
            border-radius: 8px;
            padding: 0.75rem 1.25rem;
            margin-bottom: 1.5rem;
            display: flex;
            align-items: center;
            justify-content: space-between;
            box-shadow: 0 8px 24px rgba(0,0,0,0.4);
        }

        .pit-wall-badge {
            background: #e10600;
            color: #ffffff;
            font-weight: 900;
            font-size: 0.75rem;
            letter-spacing: 2px;
            padding: 3px 8px;
            border-radius: 3px;
            text-transform: uppercase;
            display: inline-block;
        }

        /* Hero banner */
        .hero-container {
            background: linear-gradient(135deg, rgba(21, 25, 34, 0.9) 0%, rgba(13, 17, 23, 0.95) 100%);
            border: 1px solid rgba(255, 255, 255, 0.08);
            border-top: 2px solid #e10600;
            border-radius: 12px;
            padding: 2rem 2.5rem;
            margin-bottom: 2rem;
            box-shadow: 0 16px 32px rgba(0, 0, 0, 0.5);
            backdrop-filter: blur(10px);
            position: relative;
            overflow: hidden;
        }
        .hero-container::before {
            content: "BOX BOX";
            position: absolute;
            right: -20px;
            bottom: -35px;
            font-size: 8rem;
            font-weight: 900;
            font-style: italic;
            color: rgba(255, 255, 255, 0.025);
            pointer-events: none;
            letter-spacing: -2px;
        }

        .hero-tag {
            color: #e10600;
            font-weight: 700;
            font-size: 0.85rem;
            letter-spacing: 2.5px;
            text-transform: uppercase;
            margin-bottom: 0.4rem;
        }

        .hero-title {
            font-size: 2.8rem;
            font-weight: 900;
            color: #ffffff;
            letter-spacing: 1px;
            line-height: 1.1;
            margin-bottom: 0.75rem;
        }

        .hero-sub {
            color: #94a3b8;
            font-size: 1.1rem;
            line-height: 1.6;
            max-width: 750px;
            margin-bottom: 0.5rem;
        }

        /* Cards */
        .f1-card {
            background: #121620;
            border: 1px solid #1e2638;
            border-radius: 10px;
            padding: 1.25rem;
            box-shadow: 0 4px 16px rgba(0, 0, 0, 0.3);
            transition: transform 0.15s ease, border-color 0.15s ease;
        }
        .f1-card:hover {
            border-color: #e10600;
            transform: translateY(-2px);
        }

        /* Streamlit metric card overrides */
        div[data-testid="stMetric"] {
            background: #121620 !important;
            border: 1px solid #1e2638 !important;
            border-radius: 10px !important;
            padding: 1rem 1.25rem !important;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.25) !important;
        }
        div[data-testid="stMetricLabel"] {
            font-size: 0.75rem !important;
            color: #94a3b8 !important;
            text-transform: uppercase !important;
            letter-spacing: 1px !important;
            font-weight: 600 !important;
        }
        div[data-testid="stMetricValue"] {
            color: #f8fafc !important;
            font-family: 'JetBrains Mono', monospace !important;
            font-weight: 700 !important;
        }

        /* Tyre Badges */
        .tyre-badge {
            display: inline-flex;
            align-items: center;
            justify-content: center;
            width: 32px;
            height: 32px;
            border-radius: 50%;
            font-weight: 900;
            font-size: 0.9rem;
            margin-right: 8px;
            box-shadow: 0 0 10px rgba(0,0,0,0.5);
        }
        .tyre-soft {
            background: #e10600;
            color: #ffffff;
            box-shadow: 0 0 12px rgba(225, 6, 0, 0.6);
        }
        .tyre-medium {
            background: #ffd600;
            color: #0b0e14;
            box-shadow: 0 0 12px rgba(255, 214, 0, 0.6);
        }
        .tyre-hard {
            background: #ffffff;
            color: #0b0e14;
            box-shadow: 0 0 12px rgba(255, 255, 255, 0.6);
        }
        .tyre-inter {
            background: #39b54a;
            color: #ffffff;
            box-shadow: 0 0 12px rgba(57, 181, 74, 0.6);
        }
        .tyre-wet {
            background: #0072bb;
            color: #ffffff;
            box-shadow: 0 0 12px rgba(0, 114, 187, 0.6);
        }

        /* Buttons */
        .stButton>button[kind="primary"] {
            background: linear-gradient(135deg, #e10600 0%, #b30500 100%) !important;
            border: 1px solid #ff3b30 !important;
            color: #ffffff !important;
            font-weight: 700 !important;
            letter-spacing: 1px !important;
            text-transform: uppercase !important;
            border-radius: 6px !important;
            box-shadow: 0 4px 14px rgba(225, 6, 0, 0.4) !important;
            transition: all 0.2s ease !important;
        }
        .stButton>button[kind="primary"]:hover {
            box-shadow: 0 6px 20px rgba(225, 6, 0, 0.6) !important;
            transform: translateY(-1px) !important;
        }

        /* Call to pit recommendation hero */
        .call-to-pit-box {
            background: linear-gradient(135deg, rgba(225, 6, 0, 0.15) 0%, rgba(20, 24, 34, 0.95) 100%);
            border: 2px solid #e10600;
            border-radius: 12px;
            padding: 1.5rem;
            margin-bottom: 1.5rem;
            box-shadow: 0 8px 30px rgba(225, 6, 0, 0.25);
        }

        .sidebar .sidebar-content {
            background-color: #0d111a !important;
        }
    </style>
    """, unsafe_allow_html=True)


def render_pit_wall_banner(circuit="Bahrain", session_type="RACE", lap_str="LAP 24 / 57", track_temp="36.5°C", air_temp="26.0°C", sc_status="GREEN FLAG"):
    st.markdown(f"""
    <div class="pit-wall-banner">
        <div style="display: flex; align-items: center; gap: 12px;">
            <span class="pit-wall-badge">PIT WALL LIVE</span>
            <span style="font-weight: 700; color: #fff; font-size: 1.05rem;">{circuit.upper()} GP</span>
            <span style="color: #64748b;">|</span>
            <span class="telemetry-font" style="color: #cbd5e1; font-weight: 600;">{session_type}</span>
        </div>
        <div style="display: flex; align-items: center; gap: 20px;" class="telemetry-font">
            <span style="color: #94a3b8; font-size: 0.85rem;">STATUS: <strong style="color: #00e676;">{sc_status}</strong></span>
            <span style="color: #94a3b8; font-size: 0.85rem;">TRACK: <strong style="color: #ff9800;">{track_temp}</strong></span>
            <span style="color: #94a3b8; font-size: 0.85rem;">AIR: <strong style="color: #38bdf8;">{air_temp}</strong></span>
            <span style="background: #1e293b; padding: 4px 10px; border-radius: 4px; color: #f8fafc; font-weight: 700; font-size: 0.85rem;">{lap_str}</span>
        </div>
    </div>
    """, unsafe_allow_html=True)
