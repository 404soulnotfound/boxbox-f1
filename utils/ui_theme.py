"""
utils/ui_theme.py
-----------------
Option A: Pit Wall Command Center theme for Box Box F1.
Features:
  - F1 Carbon fiber dark background
  - Official F1 Racing Red (#e10600), Pirelli yellow (#ffd600), and white accents
  - Semicircular radial confidence gauges (SVG)
  - Steering wheel rotary dial components (SVG)
  - Circular compound selection badges
  - Live Pit Wall Telemetry Feed panel
  - Broadcast ticker banner
"""

import streamlit as st
import math


def inject_f1_theme():
    st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Titillium+Web:ital,wght@0,300;0,400;0,600;0,700;0,900;1,700&family=JetBrains+Mono:wght@400;600;700;800&family=Orbitron:wght@700;900&display=swap');

        /* ── Global Typography & Reset ── */
        html, body, [class*="css"] {
            font-family: 'Titillium Web', -apple-system, sans-serif;
            color: #e2e8f0;
        }

        /* ── Carbon Fiber App Background ── */
        .stApp {
            background-color: #0a0c10 !important;
            background-image: 
                radial-gradient(circle at 50% 0%, rgba(225, 6, 0, 0.12) 0%, transparent 60%),
                linear-gradient(rgba(255, 255, 255, 0.02) 1px, transparent 1px),
                linear-gradient(90deg, rgba(255, 255, 255, 0.02) 1px, transparent 1px),
                linear-gradient(135deg, #090b0e 0%, #0d1017 50%, #07090c 100%) !important;
            background-size: 100% 100%, 24px 24px, 24px 24px, 100% 100% !important;
        }

        /* ── Sidebar: F1 Carbon Console ── */
        section[data-testid="stSidebar"] {
            background-color: #0d1017 !important;
            border-right: 2px solid #1e2532 !important;
            box-shadow: 4px 0 20px rgba(0, 0, 0, 0.6) !important;
        }
        section[data-testid="stSidebar"] hr {
            border-color: rgba(225, 6, 0, 0.25) !important;
        }
        section[data-testid="stSidebar"] label,
        section[data-testid="stSidebar"] .stSelectbox label,
        section[data-testid="stSidebar"] .stSlider label,
        section[data-testid="stSidebar"] .stNumberInput label {
            color: #cbd5e1 !important;
            font-weight: 700 !important;
            font-size: 0.8rem !important;
            text-transform: uppercase !important;
            letter-spacing: 1px !important;
        }

        /* ── Headings ── */
        h1, h2, h3, h4 {
            font-family: 'Titillium Web', sans-serif !important;
            font-weight: 900 !important;
            color: #ffffff !important;
            text-transform: uppercase !important;
            letter-spacing: 0.5px !important;
        }

        /* ── Broadcast Top Ticker Bar ── */
        .broadcast-ticker {
            background: #000000;
            border-top: 3px solid #e10600;
            border-bottom: 2px solid #1a202c;
            padding: 8px 16px;
            margin: -1rem -1rem 1.5rem -1rem;
            display: flex;
            align-items: center;
            justify-content: space-between;
            font-family: 'JetBrains Mono', monospace;
            font-size: 0.82rem;
            box-shadow: 0 4px 15px rgba(0,0,0,0.5);
            flex-wrap: wrap;
            gap: 10px;
        }
        .broadcast-ticker .ticker-item {
            display: flex;
            align-items: center;
            gap: 8px;
            color: #ffffff;
            font-weight: 700;
        }
        .broadcast-ticker .ticker-badge {
            background: #e10600;
            color: #fff;
            padding: 2px 8px;
            font-weight: 900;
            font-size: 0.72rem;
            letter-spacing: 1.5px;
            border-radius: 2px;
        }
        .broadcast-ticker .ticker-caution {
            color: #ffd600;
            background: rgba(255, 214, 0, 0.15);
            border: 1px solid #ffd600;
            padding: 2px 8px;
            border-radius: 2px;
            animation: pulse-caution 1.8s infinite;
        }
        @keyframes pulse-caution {
            0%, 100% { opacity: 1; }
            50% { opacity: 0.6; }
        }

        /* ── Pit Wall Card Containers ── */
        .pitwall-card {
            background: linear-gradient(145deg, #121620 0%, #0d1017 100%);
            border: 1px solid #1e2638;
            border-top: 3px solid #e10600;
            border-radius: 8px;
            padding: 1.25rem;
            box-shadow: 0 8px 24px rgba(0, 0, 0, 0.4);
            margin-bottom: 1.25rem;
            position: relative;
        }
        .pitwall-card-header {
            font-family: 'Titillium Web', sans-serif;
            font-size: 0.85rem;
            font-weight: 800;
            color: #ffffff;
            text-transform: uppercase;
            letter-spacing: 1.5px;
            margin-bottom: 0.75rem;
            display: flex;
            align-items: center;
            justify-content: space-between;
            border-bottom: 1px solid rgba(255,255,255,0.06);
            padding-bottom: 6px;
        }

        /* ── Strategy Recommendation Rows (Option A style) ── */
        .strategy-row-card {
            background: #141923;
            border: 1px solid #1e293b;
            border-radius: 8px;
            padding: 12px 18px;
            margin-bottom: 12px;
            display: flex;
            align-items: center;
            justify-content: space-between;
            transition: all 0.2s ease;
        }
        .strategy-row-card.recommended {
            border: 1px solid #e10600;
            background: linear-gradient(90deg, rgba(225, 6, 0, 0.15) 0%, #141923 80%);
            box-shadow: 0 0 20px rgba(225, 6, 0, 0.25);
        }
        .strategy-bar-container {
            flex-grow: 1;
            margin: 0 20px;
        }
        .strategy-progress-bg {
            background: #090c10;
            border-radius: 4px;
            height: 14px;
            overflow: hidden;
            border: 1px solid #1e2638;
        }
        .strategy-progress-fill {
            height: 100%;
            background: linear-gradient(90deg, #b30500 0%, #e10600 100%);
            border-radius: 4px;
        }

        /* ── Telemetry Feed Panel (Right-side Option A) ── */
        .telemetry-feed-card {
            background: #080a0e;
            border: 1px solid #1e2638;
            border-top: 3px solid #e10600;
            border-radius: 8px;
            padding: 1rem;
            font-family: 'JetBrains Mono', monospace;
            font-size: 0.78rem;
            height: 100%;
            box-shadow: 0 8px 24px rgba(0, 0, 0, 0.5);
        }
        .telemetry-log-item {
            padding: 5px 0;
            border-bottom: 1px solid rgba(255, 255, 255, 0.04);
            display: flex;
            justify-content: space-between;
            color: #94a3b8;
        }
        .telemetry-log-item .log-time {
            color: #64748b;
        }
        .telemetry-log-item .log-val {
            color: #f1f5f9;
            font-weight: 700;
        }
        .telemetry-log-item.alert-red .log-val {
            color: #ff4d4d;
        }
        .telemetry-log-item.alert-green .log-val {
            color: #00e676;
        }
        .telemetry-log-item.alert-yellow .log-val {
            color: #ffd600;
        }

        /* ── Circular Compound Badges ── */
        .compound-pill {
            display: inline-flex;
            align-items: center;
            justify-content: center;
            width: 48px;
            height: 48px;
            border-radius: 50%;
            font-weight: 900;
            font-size: 0.75rem;
            font-family: 'Titillium Web', sans-serif;
            text-transform: uppercase;
            box-shadow: 0 0 15px rgba(0,0,0,0.6);
            transition: transform 0.15s ease;
        }
        .compound-pill:hover {
            transform: scale(1.08);
        }
        .compound-pill.soft {
            background: #140404;
            color: #ff4d4d;
            border: 3px solid #e10600;
            box-shadow: 0 0 16px rgba(225, 6, 0, 0.5);
        }
        .compound-pill.medium {
            background: #141204;
            color: #ffd600;
            border: 3px solid #ffd600;
            box-shadow: 0 0 16px rgba(255, 214, 0, 0.5);
        }
        .compound-pill.hard {
            background: #14161a;
            color: #ffffff;
            border: 3px solid #ffffff;
            box-shadow: 0 0 16px rgba(255, 255, 255, 0.4);
        }

        /* ── Rotary Dial SVG Container ── */
        .rotary-dial-container {
            display: flex;
            flex-direction: column;
            align-items: center;
            text-align: center;
            background: #10141e;
            border: 1px solid #1e2638;
            border-radius: 8px;
            padding: 10px 8px;
        }
        .rotary-dial-label {
            font-size: 0.68rem;
            color: #94a3b8;
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: 1px;
            margin-top: 4px;
        }
        .rotary-dial-val {
            font-family: 'JetBrains Mono', monospace;
            font-size: 0.95rem;
            color: #f1f5f9;
            font-weight: 800;
            margin-top: 2px;
        }

        /* ── Metric Card Overrides ── */
        div[data-testid="stMetric"] {
            background: #10141e !important;
            border: 1px solid #1e2638 !important;
            border-top: 2px solid #e10600 !important;
            border-radius: 6px !important;
            padding: 0.8rem 1rem !important;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3) !important;
        }
        div[data-testid="stMetricLabel"] {
            font-size: 0.72rem !important;
            color: #94a3b8 !important;
            text-transform: uppercase !important;
            letter-spacing: 1px !important;
            font-weight: 700 !important;
        }
        div[data-testid="stMetricValue"] {
            color: #ffffff !important;
            font-family: 'JetBrains Mono', monospace !important;
            font-weight: 800 !important;
            font-size: 1.4rem !important;
        }
        div[data-testid="stMetricDelta"] {
            font-size: 0.75rem !important;
            color: #64748b !important;
        }

        /* ── Buttons ── */
        .stButton>button[kind="primary"] {
            background: linear-gradient(135deg, #e10600 0%, #a80500 100%) !important;
            border: 1px solid #ff4d4d !important;
            color: #ffffff !important;
            font-family: 'Titillium Web', sans-serif !important;
            font-weight: 900 !important;
            letter-spacing: 1.5px !important;
            text-transform: uppercase !important;
            border-radius: 4px !important;
            box-shadow: 0 4px 16px rgba(225, 6, 0, 0.45) !important;
            transition: all 0.2s ease !important;
        }
        .stButton>button[kind="primary"]:hover {
            box-shadow: 0 6px 24px rgba(225, 6, 0, 0.7) !important;
            transform: translateY(-1px) !important;
        }

        /* ── Form Inputs ── */
        .stSelectbox>div>div,
        .stTextInput>div>div>input,
        .stNumberInput>div>div>input {
            background: #10141e !important;
            border: 1px solid #1e2638 !important;
            color: #ffffff !important;
            border-radius: 4px !important;
        }
        .stSlider [data-baseweb="slider"] [role="slider"] {
            background-color: #e10600 !important;
            border-color: #ff4d4d !important;
            box-shadow: 0 0 10px rgba(225, 6, 0, 0.6) !important;
        }
        .stSlider [data-baseweb="slider"] div[class*="Track"] {
            background-color: #1e2532 !important;
        }

        /* ── Scrollbars ── */
        ::-webkit-scrollbar { width: 6px; }
        ::-webkit-scrollbar-track { background: #0a0c10; }
        ::-webkit-scrollbar-thumb { background: #e10600; border-radius: 3px; }
    </style>
    """, unsafe_allow_html=True)


def render_pit_wall_banner(
    circuit: str = "Bahrain",
    session_type: str = "RACE",
    lap_str: str = "LAP 34 / 57",
    leader_delta: str = "VER +0.4s",
    sc_status: str = "SC DEPLOYED - CAUTION",
    weather_str: str = "DRY (28°C)"
):
    """Renders the top broadcast ticker identical to Option A."""
    is_caution = "SC" in sc_status.upper() or "CAUTION" in sc_status.upper()
    status_class = "ticker-caution" if is_caution else "ticker-badge"

    st.markdown(f"""
    <div class="broadcast-ticker">
        <div class="ticker-item">
            <span class="ticker-badge">F1 LIVE</span>
            <span style="letter-spacing: 1px;">{lap_str}</span>
        </div>
        <div class="ticker-item">
            <span style="color: #94a3b8;">LEADER:</span>
            <span style="color: #00e676;">{leader_delta}</span>
        </div>
        <div class="ticker-item">
            <span class="{status_class}">● {sc_status}</span>
        </div>
        <div class="ticker-item">
            <span style="color: #94a3b8;">CIRCUIT:</span>
            <span style="color: #ffffff;">{circuit.upper()} GP</span>
        </div>
        <div class="ticker-item">
            <span style="color: #94a3b8;">WEATHER:</span>
            <span style="color: #38bdf8;">{weather_str}</span>
        </div>
    </div>
    """, unsafe_allow_html=True)


def render_semicircular_gauge(percent: float, size: int = 85, color: str = "#e10600") -> str:
    """
    Renders a radial semicircular gauge matching Option A.
    Shows an arc fill based on percentage with the % number centered.
    """
    pct = max(0.0, min(100.0, float(percent)))
    # Radius = 34, center = (45, 45). Arc goes from (11, 45) to (79, 45)
    # Arc circumference = pi * r = 34 * 3.14159 ~= 106.8
    arc_len = 106.8
    offset = arc_len * (1.0 - (pct / 100.0))

    return f"""
    <svg width="{size}" height="{int(size * 0.75)}" viewBox="0 0 90 60" style="display: block; margin: 0 auto; filter: drop-shadow(0 0 6px {color}60);">
        <!-- Background Track -->
        <path d="M 11 48 A 34 34 0 0 1 79 48" fill="none" stroke="#1a202c" stroke-width="8" stroke-linecap="round" />
        <!-- Filled Arc -->
        <path d="M 11 48 A 34 34 0 0 1 79 48" fill="none" stroke="{color}" stroke-width="8"
              stroke-dasharray="{arc_len:.1f}" stroke-dashoffset="{offset:.1f}" stroke-linecap="round" />
        <!-- Percentage Text -->
        <text x="45" y="44" text-anchor="middle" font-family="'JetBrains Mono', monospace"
              font-size="16" font-weight="900" fill="#ffffff">{int(pct)}%</text>
    </svg>
    """


def render_rotary_dial(label: str, value: str, rotation_deg: int = 45, color: str = "#e10600") -> str:
    """
    Renders an F1 steering-wheel rotary switch dial matching Option A bottom-left.
    """
    return f"""
    <div class="rotary-dial-container">
        <svg width="58" height="58" viewBox="0 0 60 60" style="filter: drop-shadow(0 0 6px rgba(0,0,0,0.6));">
            <!-- Outer Ring with Ticks -->
            <circle cx="30" cy="30" r="26" fill="#0d1017" stroke="#1e2638" stroke-width="2" />
            <circle cx="30" cy="30" r="21" fill="#151922" stroke="{color}" stroke-width="1.5" stroke-dasharray="2 4" />
            <!-- Inner Knob -->
            <circle cx="30" cy="30" r="14" fill="#090b0e" stroke="#2a3344" stroke-width="2" />
            <!-- Indicator Notch -->
            <g transform="rotate({rotation_deg} 30 30)">
                <line x1="30" y1="16" x2="30" y2="24" stroke="{color}" stroke-width="3" stroke-linecap="round" />
            </g>
        </svg>
        <div class="rotary-dial-label">{label}</div>
        <div class="rotary-dial-val">{value}</div>
    </div>
    """


def render_compound_badges_selector(active_compound: str = "MEDIUM"):
    """Renders the 3 circular compound badges matching Option A."""
    compounds = [("SOFT", "soft", "#e10600"), ("MEDIUM", "medium", "#ffd600"), ("HARD", "hard", "#ffffff")]
    html = '<div style="display: flex; gap: 14px; justify-content: center; margin: 10px 0;">'
    for name, cls, col in compounds:
        is_active = (name.upper() == active_compound.upper())
        active_style = f"transform: scale(1.1); box-shadow: 0 0 20px {col}90;" if is_active else "opacity: 0.75;"
        html += f"""
        <div class="compound-pill {cls}" style="{active_style}">
            {name[:4]}
        </div>
        """
    html += '</div>'
    st.markdown(html, unsafe_allow_html=True)


def render_telemetry_feed_panel(
    driver: str = "VER",
    lap: int = 34,
    speed: int = 318,
    fuel_kg: float = 42.5,
    tire_temp_fl: int = 98,
    sector_delta: str = "-0.14s",
    pit_lane_status: str = "CLEAR",
    radio_msg: str = "BOX THIS LAP"
):
    """Renders the dedicated Telemetry Feed panel on the right matching Option A."""
    delta_class = "alert-green" if sector_delta.startswith("-") else "alert-red"
    st.markdown(f"""
    <div class="telemetry-feed-card">
        <div style="color: #ffffff; font-size: 0.85rem; font-weight: 800; border-bottom: 2px solid #e10600; padding-bottom: 6px; margin-bottom: 10px; display: flex; justify-content: space-between;">
            <span>TELEMETRY FEED</span>
            <span style="color: #00e676; font-size: 0.7rem;">● LIVE STREAM</span>
        </div>
        <div class="telemetry-log-item">
            <span class="log-time">14:32:05</span>
            <span>T2 TRAP SPEED</span>
            <span class="log-val">{speed} km/h</span>
        </div>
        <div class="telemetry-log-item">
            <span class="log-time">14:32:10</span>
            <span>PIT LANE ENTRY</span>
            <span class="log-val alert-green">{pit_lane_status}</span>
        </div>
        <div class="telemetry-log-item">
            <span class="log-time">14:32:18</span>
            <span>EST. FUEL LOAD</span>
            <span class="log-val">{fuel_kg:.1f} kg</span>
        </div>
        <div class="telemetry-log-item">
            <span class="log-time">14:32:25</span>
            <span>TYRE FL / FR</span>
            <span class="log-val alert-yellow">{tire_temp_fl}°C / {tire_temp_fl+2}°C</span>
        </div>
        <div class="telemetry-log-item {delta_class}">
            <span class="log-time">14:32:32</span>
            <span>SECTOR 1 DELTA</span>
            <span class="log-val">{sector_delta}</span>
        </div>
        <div class="telemetry-log-item alert-red" style="margin-top: 8px; border-top: 1px dashed rgba(225,6,0,0.4); padding-top: 8px;">
            <span class="log-time">14:32:40</span>
            <span>RADIO CH 1</span>
            <span class="log-val">"{radio_msg}"</span>
        </div>
    </div>
    """, unsafe_allow_html=True)
