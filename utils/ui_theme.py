"""
utils/ui_theme.py
-----------------
Direction 1: True F1 Cockpit Command Dashboard theme for Box Box F1.
Exact match to the visual mockup:
  - Widescreen 3-column cockpit layout (Zero intrusive sidebar)
  - Dark carbon weave background
  - F1 Racing Red (#e10600), Pirelli yellow (#ffd600), and white accents
  - Semicircular radial speedo gauges with illuminated tick marks
  - Physical steering wheel rotary knobs with indicator lines
  - Glowing circular Pirelli compound badges
  - Live Telemetry Feed stream
  - Full-width F1 broadcast ticker bar
"""

import streamlit as st
import math


def inject_f1_theme():
    st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Titillium+Web:ital,wght@0,300;0,400;0,600;0,700;0,900;1,700&family=JetBrains+Mono:wght@400;600;700;800&family=Orbitron:wght@700;900&display=swap');

        /* ── Full Widescreen Clean Canvas ── */
        .block-container {
            padding-top: 0.6rem !important;
            padding-bottom: 2rem !important;
            padding-left: 1.5rem !important;
            padding-right: 1.5rem !important;
            max-width: 100% !important;
        }

        html, body, [class*="css"] {
            font-family: 'Titillium Web', -apple-system, sans-serif;
            color: #e2e8f0;
        }

        /* ── Real Carbon Weave Background ── */
        .stApp {
            background-color: #0b0c10 !important;
            background-image: 
                radial-gradient(circle at 50% 0%, rgba(225, 6, 0, 0.15) 0%, transparent 50%),
                linear-gradient(45deg, #0f1218 25%, transparent 25%), 
                linear-gradient(-45deg, #0f1218 25%, transparent 25%), 
                linear-gradient(45deg, transparent 75%, #0f1218 75%), 
                linear-gradient(-45deg, transparent 75%, #0f1218 75%) !important;
            background-size: 100% 100%, 8px 8px, 8px 8px, 8px 8px, 8px 8px !important;
            background-position: 0 0, 0 0, 0 4px, 4px -4px, -4px 0px !important;
        }

        /* ── Headings ── */
        h1, h2, h3, h4 {
            font-family: 'Titillium Web', sans-serif !important;
            font-weight: 900 !important;
            color: #ffffff !important;
            text-transform: uppercase !important;
            letter-spacing: 0.5px !important;
        }

        /* ── Top Broadcast Caution Bar ── */
        .f1-cockpit-bar {
            background: #000000;
            border-top: 3px solid #e10600;
            border-bottom: 2px solid #1a202c;
            border-radius: 4px;
            padding: 8px 20px;
            margin-bottom: 1.25rem;
            display: flex;
            align-items: center;
            justify-content: space-between;
            font-family: 'JetBrains Mono', monospace;
            font-size: 0.88rem;
            font-weight: 800;
            box-shadow: 0 4px 20px rgba(0, 0, 0, 0.7);
            flex-wrap: wrap;
            gap: 12px;
        }
        .f1-cockpit-bar .f1-badge {
            background: #e10600;
            color: #ffffff;
            font-family: 'Orbitron', sans-serif;
            font-weight: 900;
            font-size: 0.85rem;
            padding: 3px 10px;
            border-radius: 3px;
            letter-spacing: 2px;
        }
        .f1-cockpit-bar .caution-pill {
            color: #ffd600;
            background: rgba(255, 214, 0, 0.15);
            border: 1px solid #ffd600;
            padding: 3px 12px;
            border-radius: 3px;
            letter-spacing: 1px;
            animation: pulse-caution 1.8s infinite;
        }
        @keyframes pulse-caution {
            0%, 100% { opacity: 1; }
            50% { opacity: 0.5; }
        }

        /* ── Main Cockpit Panels (Exact to Mockup 1) ── */
        .cockpit-panel {
            background: #11141c;
            border: 1px solid rgba(225, 6, 0, 0.5);
            border-radius: 8px;
            padding: 1.25rem;
            box-shadow: 0 8px 24px rgba(0, 0, 0, 0.5);
            height: 100%;
        }
        .cockpit-panel-title {
            font-family: 'Titillium Web', sans-serif;
            font-size: 0.9rem;
            font-weight: 900;
            color: #ffffff;
            text-transform: uppercase;
            letter-spacing: 1.5px;
            margin-bottom: 1rem;
            display: flex;
            align-items: center;
            justify-content: space-between;
            border-bottom: 1px solid rgba(255, 255, 255, 0.08);
            padding-bottom: 8px;
        }

        /* ── Strategy Recommendation Rows (Center Panel) ── */
        .cockpit-strategy-row {
            background: #151922;
            border: 1px solid #222938;
            border-radius: 8px;
            padding: 14px 16px;
            margin-bottom: 12px;
            display: flex;
            align-items: center;
            justify-content: space-between;
            box-shadow: 0 4px 14px rgba(0, 0, 0, 0.3);
            transition: all 0.2s ease;
        }
        .cockpit-strategy-row.active {
            border: 1px solid #e10600;
            background: linear-gradient(90deg, rgba(225, 6, 0, 0.18) 0%, #151922 85%);
            box-shadow: 0 0 20px rgba(225, 6, 0, 0.3);
        }
        .cockpit-strategy-info {
            min-width: 170px;
        }
        .cockpit-strategy-num {
            font-family: 'Orbitron', monospace;
            font-size: 1.3rem;
            font-weight: 900;
            color: #ffffff;
            margin-right: 8px;
        }
        .cockpit-strategy-title {
            font-size: 0.98rem;
            font-weight: 900;
            color: #ffffff;
            letter-spacing: 0.5px;
        }
        .cockpit-strategy-sub {
            font-size: 0.76rem;
            color: #94a3b8;
            margin-top: 3px;
        }
        .cockpit-strategy-bar {
            flex-grow: 1;
            margin: 0 16px;
        }
        .cockpit-bar-track {
            background: #090c10;
            border-radius: 4px;
            height: 12px;
            overflow: hidden;
            border: 1px solid #1e2638;
        }
        .cockpit-bar-fill {
            height: 100%;
            border-radius: 4px;
        }

        /* ── Live Telemetry Feed (Right Panel) ── */
        .cockpit-feed-item {
            display: flex;
            justify-content: space-between;
            padding: 6px 0;
            border-bottom: 1px solid rgba(255, 255, 255, 0.04);
            font-family: 'JetBrains Mono', monospace;
            font-size: 0.8rem;
            color: #cbd5e1;
        }
        .cockpit-feed-item .feed-key {
            color: #94a3b8;
        }
        .cockpit-feed-item .feed-val {
            font-weight: 700;
            color: #ffffff;
        }

        /* ── Circular Glowing Pirelli Compound Badges ── */
        .pirelli-badge-row {
            display: flex;
            gap: 16px;
            justify-content: center;
            margin: 14px 0 18px 0;
        }
        .pirelli-circle {
            width: 56px;
            height: 56px;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            font-weight: 900;
            font-size: 0.75rem;
            font-family: 'Titillium Web', sans-serif;
            text-transform: uppercase;
            background: #0d0f14;
            transition: all 0.2s ease;
            cursor: pointer;
        }
        .pirelli-circle.soft {
            border: 3px solid #e10600;
            color: #ff4d4d;
            box-shadow: 0 0 16px rgba(225, 6, 0, 0.6);
        }
        .pirelli-circle.medium {
            border: 3px solid #ffd600;
            color: #ffd600;
            box-shadow: 0 0 16px rgba(255, 214, 0, 0.6);
        }
        .pirelli-circle.hard {
            border: 3px solid #ffffff;
            color: #ffffff;
            box-shadow: 0 0 16px rgba(255, 255, 255, 0.5);
        }
        .pirelli-circle.active {
            transform: scale(1.12);
            filter: brightness(1.2);
        }

        /* ── Rotary Knobs Container ── */
        .rotary-knobs-grid {
            display: grid;
            grid-template-columns: 1fr 1fr 1fr;
            gap: 8px;
            margin-top: 10px;
        }
        .rotary-knob-box {
            background: #090b0e;
            border: 1px solid #1e2638;
            border-radius: 6px;
            padding: 8px 4px;
            text-align: center;
            display: flex;
            flex-direction: column;
            align-items: center;
        }
        .rotary-knob-label {
            font-size: 0.68rem;
            color: #94a3b8;
            font-weight: 800;
            text-transform: uppercase;
            letter-spacing: 1px;
            margin-top: 4px;
        }
        .rotary-knob-val {
            font-family: 'JetBrains Mono', monospace;
            font-size: 0.82rem;
            font-weight: 800;
            color: #ffffff;
        }

        /* ── Bottom Telemetry Chart Box ── */
        .cockpit-chart-card {
            background: #11141c;
            border: 1px solid rgba(225, 6, 0, 0.4);
            border-radius: 8px;
            padding: 12px;
            box-shadow: 0 8px 24px rgba(0, 0, 0, 0.5);
            margin-top: 1.25rem;
        }
        .cockpit-chart-header {
            font-size: 0.78rem;
            font-weight: 900;
            color: #ffffff;
            text-transform: uppercase;
            letter-spacing: 1px;
            margin-bottom: 6px;
            text-align: center;
            border-bottom: 1px solid rgba(255, 255, 255, 0.06);
            padding-bottom: 4px;
        }

        /* ── Input Styling ── */
        .stSelectbox>div>div {
            background: #090b0e !important;
            border: 1px solid #1e2638 !important;
            color: #ffffff !important;
            border-radius: 4px !important;
            font-weight: 700 !important;
        }
        .stSlider [data-baseweb="slider"] [role="slider"] {
            background-color: #e10600 !important;
            border-color: #ff4d4d !important;
            box-shadow: 0 0 10px rgba(225, 6, 0, 0.6) !important;
        }
        .stSlider [data-baseweb="slider"] div[class*="Track"] {
            background-color: #1e2532 !important;
        }

        /* ── Primary Button ── */
        .stButton>button[kind="primary"] {
            background: linear-gradient(135deg, #e10600 0%, #990500 100%) !important;
            border: 1px solid #ff4d4d !important;
            color: #ffffff !important;
            font-family: 'Titillium Web', sans-serif !important;
            font-weight: 900 !important;
            letter-spacing: 1.5px !important;
            text-transform: uppercase !important;
            border-radius: 4px !important;
            box-shadow: 0 4px 16px rgba(225, 6, 0, 0.45) !important;
            padding: 0.5rem 1rem !important;
        }
    </style>
    """, unsafe_allow_html=True)


def render_cockpit_top_bar(
    lap_str: str = "LAP 34/57",
    leader_delta: str = "VER +0.4s",
    sc_status: str = "SC DEPLOYED - CAUTION",
    weather_str: str = "WEATHER: DRY 28°C"
):
    """Renders the top F1 broadcast caution ticker matching Mockup 1."""
    st.markdown(f"""
    <div class="f1-cockpit-bar">
        <div style="display: flex; align-items: center; gap: 12px;">
            <span class="f1-badge">F1</span>
            <span style="color: #ffffff; letter-spacing: 1px;">{lap_str}</span>
            <span style="color: #4b5563;">|</span>
            <span style="color: #ffffff;">{leader_delta}</span>
        </div>
        <div>
            <span class="caution-pill">● {sc_status}</span>
        </div>
        <div>
            <span style="color: #38bdf8;">{weather_str}</span>
        </div>
    </div>
    """, unsafe_allow_html=True)


def render_cockpit_speedo_gauge(percentage: float, size: int = 96, color: str = "#e10600") -> str:
    """
    Renders the exact semicircular speedo gauge seen on the right of each strategy card in Mockup 1.
    Features illuminated tick marks, glowing red arc, and large bold percentage.
    """
    pct = max(0.0, min(100.0, float(percentage)))
    # Semicircle arc: Center (50, 48), radius 36. Arc from (14, 48) to (86, 48)
    # Length = pi * 36 ~= 113.1
    arc_len = 113.1
    offset = arc_len * (1.0 - (pct / 100.0))

    return f"""
    <svg width="{size}" height="{int(size * 0.7)}" viewBox="0 0 100 68" style="display: block; margin: 0 auto; filter: drop-shadow(0 0 8px {color}70);">
        <!-- Background Track -->
        <path d="M 14 50 A 36 36 0 0 1 86 50" fill="none" stroke="#1a202c" stroke-width="7" stroke-linecap="round" />
        <!-- Tick Marks Pattern -->
        <path d="M 14 50 A 36 36 0 0 1 86 50" fill="none" stroke="#2d3748" stroke-width="8" stroke-dasharray="2 6" stroke-linecap="butt" />
        <!-- Filled Glowing Arc -->
        <path d="M 14 50 A 36 36 0 0 1 86 50" fill="none" stroke="{color}" stroke-width="7"
              stroke-dasharray="{arc_len:.1f}" stroke-dashoffset="{offset:.1f}" stroke-linecap="round" />
        <!-- Inner Gauge Value -->
        <text x="50" y="46" text-anchor="middle" font-family="'JetBrains Mono', monospace"
              font-size="16" font-weight="900" fill="#ffffff">{int(pct)}%</text>
    </svg>
    """


def render_cockpit_rotary_knob(label: str, value: str, angle_deg: int = 0, color: str = "#e10600") -> str:
    """
    Renders the physical steering-wheel rotary dial knob seen in the bottom-left of Mockup 1.
    """
    return f"""
    <div class="rotary-knob-box">
        <svg width="52" height="52" viewBox="0 0 60 60">
            <!-- Outer Bezel -->
            <circle cx="30" cy="30" r="26" fill="#090b0e" stroke="#1e2638" stroke-width="2" />
            <!-- Ticks -->
            <circle cx="30" cy="30" r="22" fill="#141822" stroke="#252f44" stroke-width="1.5" stroke-dasharray="2 5" />
            <!-- Inner Raised Knob -->
            <circle cx="30" cy="30" r="15" fill="#0b0d12" stroke="#2d3748" stroke-width="2" />
            <!-- Rotating Indicator Line -->
            <g transform="rotate({angle_deg} 30 30)">
                <line x1="30" y1="17" x2="30" y2="25" stroke="{color}" stroke-width="3" stroke-linecap="round" />
            </g>
        </svg>
        <div class="rotary-knob-label">{label}</div>
        <div class="rotary-knob-val">{value}</div>
    </div>
    """


def render_cockpit_compound_buttons(active_compound: str = "MEDIUM"):
    """Renders the 3 circular glowing compound buttons matching Mockup 1."""
    compounds = [("SOFT", "soft", "#e10600"), ("MEDIUM", "medium", "#ffd600"), ("HARD", "hard", "#ffffff")]
    html = '<div class="pirelli-badge-row">'
    for name, cls, col in compounds:
        is_active = (name.upper() == active_compound.upper())
        active_cls = "active" if is_active else ""
        html += f"""
        <div class="pirelli-circle {cls} {active_cls}">
            {name}
        </div>
        """
    html += '</div>'
    st.markdown(html, unsafe_allow_html=True)
