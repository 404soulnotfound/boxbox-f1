"""
utils/ui_theme.py
-----------------
Timing Screen Terminal theme for Box Box F1.
Inspired by the real F1 World Feed timing tower:
  - Pure black background
  - Green (#00ff87) monospace text for all data
  - Ferrari red (#e10600) for critical alerts and headers
  - White for neutral labels
"""

import streamlit as st


def inject_f1_theme():
    st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Share+Tech+Mono&family=Rajdhani:wght@400;600;700&family=Orbitron:wght@700;900&display=swap');

        /* ── Global Reset ── */
        html, body, [class*="css"] {
            font-family: 'Rajdhani', 'Share Tech Mono', monospace;
            color: #c8f0c8;
            background-color: #000000 !important;
        }

        /* ── App Background ── */
        .stApp {
            background-color: #000000 !important;
            background-image:
                linear-gradient(rgba(0, 255, 135, 0.025) 1px, transparent 1px),
                linear-gradient(90deg, rgba(0, 255, 135, 0.025) 1px, transparent 1px);
            background-size: 40px 40px;
        }

        /* ── Sidebar ── */
        section[data-testid="stSidebar"] {
            background-color: #050505 !important;
            border-right: 1px solid #00ff87 !important;
        }
        section[data-testid="stSidebar"] * {
            color: #00ff87 !important;
        }
        section[data-testid="stSidebar"] .stSelectbox label,
        section[data-testid="stSidebar"] .stSlider label,
        section[data-testid="stSidebar"] .stNumberInput label,
        section[data-testid="stSidebar"] p {
            color: #00ff87 !important;
            font-family: 'Share Tech Mono', monospace !important;
            font-size: 0.82rem !important;
            text-transform: uppercase;
            letter-spacing: 1px;
        }

        /* ── Headings ── */
        h1, h2, h3, h4 {
            font-family: 'Orbitron', monospace !important;
            color: #e10600 !important;
            text-transform: uppercase;
            letter-spacing: 2px;
        }

        /* ── Timing Row ── */
        .timing-header {
            background: #000;
            border-bottom: 2px solid #e10600;
            padding: 10px 16px;
            display: flex;
            align-items: center;
            justify-content: space-between;
            font-family: 'Share Tech Mono', monospace;
            margin-bottom: 1.5rem;
        }
        .timing-logo {
            font-family: 'Orbitron', monospace;
            font-size: 1.4rem;
            font-weight: 900;
            color: #e10600;
            letter-spacing: 4px;
        }
        .timing-status {
            display: flex;
            gap: 24px;
            font-size: 0.78rem;
            color: #00ff87;
            letter-spacing: 1.5px;
        }
        .timing-status span {
            display: flex;
            align-items: center;
            gap: 6px;
        }
        .status-dot {
            width: 8px;
            height: 8px;
            border-radius: 50%;
            background: #00ff87;
            box-shadow: 0 0 6px #00ff87;
            animation: blink 1.5s infinite;
            display: inline-block;
        }
        @keyframes blink {
            0%, 100% { opacity: 1; }
            50% { opacity: 0.2; }
        }

        /* ── Timing Table Row ── */
        .timing-row {
            display: grid;
            grid-template-columns: 36px 60px 1fr 110px 110px 110px 160px;
            align-items: center;
            padding: 6px 12px;
            border-bottom: 1px solid rgba(0, 255, 135, 0.1);
            font-family: 'Share Tech Mono', monospace;
            font-size: 0.85rem;
            transition: background 0.15s;
        }
        .timing-row:hover {
            background: rgba(0, 255, 135, 0.05);
        }
        .timing-row.header {
            color: #e10600;
            font-size: 0.72rem;
            letter-spacing: 2px;
            border-bottom: 1px solid #e10600;
            padding-bottom: 8px;
            margin-bottom: 4px;
        }
        .timing-pos { color: #e10600; font-weight: 700; }
        .timing-driver { color: #ffffff; font-weight: 700; letter-spacing: 1px; }
        .timing-gap { color: #00ff87; }
        .timing-compound { font-weight: 700; }
        .timing-rec-pit { color: #e10600; font-weight: 700; }
        .timing-rec-stay { color: #00ff87; }

        /* ── Compound badges ── */
        .compound-S { color: #e10600; }
        .compound-M { color: #ffd600; }
        .compound-H { color: #ffffff; }
        .compound-I { color: #39b54a; }
        .compound-W { color: #0072bb; }

        /* ── Terminal Panel ── */
        .terminal-panel {
            background: #000;
            border: 1px solid #00ff87;
            border-radius: 4px;
            padding: 1rem;
            font-family: 'Share Tech Mono', monospace;
            font-size: 0.8rem;
            color: #00ff87;
            line-height: 1.7;
            box-shadow: 0 0 16px rgba(0, 255, 135, 0.08), inset 0 0 20px rgba(0,0,0,0.5);
        }
        .terminal-panel .t-red { color: #e10600; }
        .terminal-panel .t-white { color: #ffffff; }
        .terminal-panel .t-dim { color: #2a6640; }
        .terminal-panel .t-yellow { color: #ffd600; }

        /* ── Metric override ── */
        div[data-testid="stMetric"] {
            background: #050505 !important;
            border: 1px solid #00ff87 !important;
            border-radius: 3px !important;
            padding: 0.75rem 1rem !important;
        }
        div[data-testid="stMetricLabel"] {
            font-size: 0.7rem !important;
            color: #2a9960 !important;
            text-transform: uppercase !important;
            letter-spacing: 1.5px !important;
            font-family: 'Share Tech Mono', monospace !important;
        }
        div[data-testid="stMetricValue"] {
            color: #00ff87 !important;
            font-family: 'Share Tech Mono', monospace !important;
            font-weight: 700 !important;
            font-size: 1.3rem !important;
        }
        div[data-testid="stMetricDelta"] {
            color: #2a9960 !important;
            font-family: 'Share Tech Mono', monospace !important;
            font-size: 0.75rem !important;
        }

        /* ── Buttons ── */
        .stButton>button[kind="primary"] {
            background: transparent !important;
            border: 1px solid #e10600 !important;
            color: #e10600 !important;
            font-family: 'Share Tech Mono', monospace !important;
            font-weight: 700 !important;
            letter-spacing: 2px !important;
            text-transform: uppercase !important;
            border-radius: 2px !important;
            box-shadow: 0 0 12px rgba(225, 6, 0, 0.3) !important;
            transition: all 0.2s !important;
        }
        .stButton>button[kind="primary"]:hover {
            background: rgba(225, 6, 0, 0.1) !important;
            box-shadow: 0 0 24px rgba(225, 6, 0, 0.5) !important;
        }
        .stButton>button:not([kind="primary"]) {
            background: transparent !important;
            border: 1px solid #00ff87 !important;
            color: #00ff87 !important;
            font-family: 'Share Tech Mono', monospace !important;
            letter-spacing: 2px !important;
            border-radius: 2px !important;
        }

        /* ── Selectbox / Input ── */
        .stSelectbox>div>div,
        .stTextInput>div>div>input,
        .stNumberInput>div>div>input {
            background: #050505 !important;
            border: 1px solid #00ff87 !important;
            color: #00ff87 !important;
            font-family: 'Share Tech Mono', monospace !important;
            border-radius: 2px !important;
        }

        /* ── Slider ── */
        .stSlider [data-baseweb="slider"] [role="slider"] {
            background-color: #00ff87 !important;
            border-color: #00ff87 !important;
        }
        .stSlider [data-baseweb="slider"] div[class*="Track"] {
            background-color: #0a2a18 !important;
        }

        /* ── Info / Warning / Error boxes ── */
        .stAlert {
            background: #050505 !important;
            border: 1px solid #00ff87 !important;
            color: #00ff87 !important;
            font-family: 'Share Tech Mono', monospace !important;
            border-radius: 2px !important;
        }

        /* ── Code blocks ── */
        .stCodeBlock code {
            background: #050505 !important;
            color: #00ff87 !important;
            font-family: 'Share Tech Mono', monospace !important;
            border: 1px solid rgba(0, 255, 135, 0.2) !important;
        }

        /* ── Divider ── */
        hr {
            border-color: rgba(0, 255, 135, 0.15) !important;
        }

        /* ── Scrollbar ── */
        ::-webkit-scrollbar { width: 5px; }
        ::-webkit-scrollbar-track { background: #000; }
        ::-webkit-scrollbar-thumb { background: #00ff87; border-radius: 2px; }

        /* ── Hero container (terminal variant) ── */
        .hero-container {
            background: #000;
            border: 1px solid #e10600;
            border-radius: 2px;
            padding: 1.5rem 2rem;
            margin-bottom: 1.5rem;
            box-shadow: 0 0 30px rgba(225, 6, 0, 0.15);
            position: relative;
            overflow: hidden;
        }
        .hero-container::before {
            content: "BOX BOX";
            position: absolute;
            right: -10px;
            bottom: -30px;
            font-family: 'Orbitron', monospace;
            font-size: 7rem;
            font-weight: 900;
            color: rgba(225, 6, 0, 0.04);
            pointer-events: none;
            letter-spacing: -2px;
        }
        .hero-tag {
            color: #00ff87;
            font-family: 'Share Tech Mono', monospace;
            font-size: 0.75rem;
            letter-spacing: 3px;
            text-transform: uppercase;
            margin-bottom: 0.4rem;
        }
        .hero-title {
            font-family: 'Orbitron', monospace;
            font-size: 2.2rem;
            font-weight: 900;
            color: #e10600;
            letter-spacing: 2px;
            line-height: 1.1;
            margin-bottom: 0.75rem;
            text-shadow: 0 0 20px rgba(225, 6, 0, 0.4);
        }
        .hero-sub {
            color: #2a9960;
            font-family: 'Share Tech Mono', monospace;
            font-size: 0.88rem;
            line-height: 1.7;
            max-width: 760px;
        }

        /* ── Call-to-pit box ── */
        .call-to-pit-box {
            background: #000;
            border: 1px solid #e10600;
            border-left: 4px solid #e10600;
            border-radius: 2px;
            padding: 1.25rem 1.5rem;
            margin-bottom: 1.5rem;
            box-shadow: 0 0 30px rgba(225, 6, 0, 0.2), inset 0 0 30px rgba(225, 6, 0, 0.03);
        }

        /* ── Strategy card ── */
        .strat-card {
            background: #000;
            border: 1px solid #1a4a30;
            border-radius: 2px;
            padding: 1rem;
            height: 100%;
            font-family: 'Share Tech Mono', monospace;
            transition: border-color 0.2s, box-shadow 0.2s;
        }
        .strat-card.recommended {
            border-color: #e10600;
            box-shadow: 0 0 20px rgba(225, 6, 0, 0.2);
        }

        /* ── Pit wall badge ── */
        .pit-wall-badge {
            background: #e10600;
            color: #ffffff;
            font-family: 'Share Tech Mono', monospace;
            font-weight: 700;
            font-size: 0.7rem;
            letter-spacing: 2px;
            padding: 2px 8px;
            border-radius: 1px;
            text-transform: uppercase;
        }

        /* ── Section titles ── */
        p.section-title {
            font-family: 'Orbitron', monospace !important;
            color: #e10600 !important;
            font-size: 0.85rem !important;
            letter-spacing: 3px !important;
            text-transform: uppercase !important;
            border-left: 3px solid #e10600;
            padding-left: 10px;
            margin: 1.5rem 0 1rem 0;
        }

        /* ── Decision rows ── */
        .decision-row {
            background: #000;
            border: 1px solid #1a4a30;
            border-left: 3px solid #00ff87;
            padding: 0.9rem 1rem;
            margin-bottom: 0.6rem;
            border-radius: 2px;
            font-family: 'Share Tech Mono', monospace;
        }
        .decision-row .q {
            color: #e10600;
            font-size: 0.85rem;
            font-weight: 700;
            margin-bottom: 4px;
            letter-spacing: 0.5px;
        }
        .decision-row .a {
            color: #2a9960;
            font-size: 0.82rem;
            line-height: 1.6;
        }

        /* ── Insight box ── */
        .insight-box {
            background: #000;
            border: 1px solid #1a4a30;
            border-radius: 2px;
            padding: 1rem;
            margin-bottom: 0.75rem;
            font-family: 'Share Tech Mono', monospace;
        }
        .insight-box .label {
            color: #00ff87;
            font-weight: 700;
            font-size: 0.85rem;
            margin-bottom: 6px;
            letter-spacing: 1px;
        }
        .insight-box p {
            color: #2a9960;
            font-size: 0.82rem;
            line-height: 1.6;
            margin: 0;
        }

        /* ── Skill badge ── */
        .skill-badge {
            display: inline-block;
            font-family: 'Share Tech Mono', monospace;
            font-size: 0.78rem;
            color: #00ff87;
            background: rgba(0, 255, 135, 0.05);
            border: 1px solid rgba(0, 255, 135, 0.2);
            padding: 3px 8px;
            border-radius: 1px;
            margin: 3px 3px 3px 0;
        }

        /* ── Metric highlight ── */
        .metric-highlight {
            background: #000;
            border: 1px solid #1a4a30;
            border-top: 2px solid #e10600;
            padding: 1rem;
            text-align: center;
            border-radius: 2px;
            font-family: 'Share Tech Mono', monospace;
        }
        .metric-highlight .val {
            font-family: 'Orbitron', monospace;
            font-size: 1.5rem;
            color: #e10600;
            font-weight: 900;
        }
        .metric-highlight .lbl {
            font-size: 0.7rem;
            color: #2a9960;
            text-transform: uppercase;
            letter-spacing: 1.5px;
            margin-top: 4px;
        }

        /* ── Tyre badges ── */
        .tyre-badge {
            display: inline-flex;
            align-items: center;
            justify-content: center;
            width: 28px; height: 28px;
            border-radius: 50%;
            font-weight: 900;
            font-size: 0.8rem;
            margin-right: 6px;
            font-family: 'Share Tech Mono', monospace;
        }
        .tyre-soft  { background: #e10600; color: #fff; box-shadow: 0 0 10px rgba(225,6,0,0.5); }
        .tyre-medium{ background: #ffd600; color: #000; box-shadow: 0 0 10px rgba(255,214,0,0.5); }
        .tyre-hard  { background: #ffffff; color: #000; box-shadow: 0 0 10px rgba(255,255,255,0.4); }
        .tyre-inter { background: #39b54a; color: #fff; box-shadow: 0 0 10px rgba(57,181,74,0.5); }
        .tyre-wet   { background: #0072bb; color: #fff; box-shadow: 0 0 10px rgba(0,114,187,0.5); }

    </style>
    """, unsafe_allow_html=True)


def render_pit_wall_banner(circuit="Bahrain", session_type="RACE", lap_str="LAP 24 / 57",
                           track_temp="36.5°C", air_temp="26.0°C", sc_status="GREEN FLAG"):
    sc_color = "#e10600" if "SC" in sc_status.upper() or "SAFETY" in sc_status.upper() else "#00ff87"
    st.markdown(f"""
    <div class="timing-header">
        <div class="timing-logo">BOX BOX // F1</div>
        <div class="timing-status">
            <span><span class="status-dot"></span> {circuit.upper()} GP</span>
            <span style="color:#888;">|</span>
            <span>{session_type}</span>
            <span style="color:#888;">|</span>
            <span>{lap_str}</span>
            <span style="color:#888;">|</span>
            <span>TRACK <strong style="color:#ffd600;">{track_temp}</strong></span>
            <span>AIR <strong style="color:#38bdf8;">{air_temp}</strong></span>
            <span style="color:{sc_color};">● {sc_status}</span>
        </div>
    </div>
    """, unsafe_allow_html=True)
