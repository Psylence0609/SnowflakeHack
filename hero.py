import streamlit as st

def render():
    st.markdown("""
    <style>
    .hero-wrap {
        min-height: 100vh;
        background: #ffffff;
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        padding: 80px 40px;
        position: relative;
        overflow: hidden;
    }
    .hero-grid {
        position: absolute;
        inset: 0;
        background-image:
            linear-gradient(rgba(0,0,0,0.04) 1px, transparent 1px),
            linear-gradient(90deg, rgba(0,0,0,0.04) 1px, transparent 1px);
        background-size: 48px 48px;
        pointer-events: none;
    }
    .hero-content {
        position: relative;
        z-index: 2;
        text-align: center;
        max-width: 760px;
    }
    .hero-eyebrow {
        display: inline-flex;
        align-items: center;
        gap: 8px;
        font-family: 'Satoshi', sans-serif;
        font-size: 11px;
        font-weight: 700;
        letter-spacing: 0.14em;
        text-transform: uppercase;
        color: #01696f;
        background: rgba(1,105,111,0.08);
        border: 1px solid rgba(1,105,111,0.18);
        border-radius: 100px;
        padding: 6px 16px;
        margin-bottom: 32px;
    }
    .hero-dot {
        width: 6px;
        height: 6px;
        border-radius: 50%;
        background: #01696f;
        animation: pulse 2s ease-in-out infinite;
    }
    @keyframes pulse {
        0%, 100% { opacity: 1; transform: scale(1); }
        50% { opacity: 0.4; transform: scale(0.8); }
    }
    .hero-title {
        font-family: 'Cabinet Grotesk', 'Satoshi', sans-serif;
        font-size: clamp(36px, 5vw, 64px);
        font-weight: 800;
        line-height: 1.05;
        letter-spacing: -0.03em;
        color: #1a1a1a;
        margin-bottom: 24px;
    }
    .hero-title .accent {
        color: #01696f;
    }
    .hero-desc {
        font-family: 'Satoshi', sans-serif;
        font-size: 17px;
        font-weight: 400;
        color: #6b6b6b;
        line-height: 1.7;
        max-width: 560px;
        margin: 0 auto 48px;
    }
    .hero-stats {
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 0;
        border-top: 1px solid rgba(0,0,0,0.08);
        padding-top: 40px;
        margin-top: 12px;
        flex-wrap: wrap;
    }
    .hero-stat {
        padding: 0 36px;
        text-align: left;
    }
    .hero-stat + .hero-stat {
        border-left: 1px solid rgba(0,0,0,0.08);
    }
    .hero-stat-val {
        font-family: 'Cabinet Grotesk', sans-serif;
        font-size: 26px;
        font-weight: 800;
        color: #1a1a1a;
        font-variant-numeric: tabular-nums;
        letter-spacing: -0.02em;
    }
    .hero-stat-val .hi { color: #01696f; }
    .hero-stat-label {
        font-size: 11px;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.1em;
        color: #9a9a9a;
        margin-top: 2px;
    }
    .hero-logo {
        margin-bottom: 40px;
        display: flex;
        justify-content: center;
    }

    /* Hero page: zero out block-container */
    .block-container {
        max-width: 100% !important;
        padding-left: 0 !important;
        padding-right: 0 !important;
        padding-top: 0 !important;
    }
    /* Center the button column itself */
    .st-key-open_dashboard_btn {
        display: flex !important;
        justify-content: center !important;
        width: 100% !important;
    }
    .st-key-open_dashboard_btn > div {
        display: flex !important;
        justify-content: center !important;
        width: 100% !important;
    }
    .st-key-open_dashboard_btn button {
        background: #01696f !important;
        color: #ffffff !important;
        border: none !important;
        width: 240px !important;
        max-width: 240px !important;
        margin: 0 auto !important;
        display: block !important;
    }
    .st-key-open_dashboard_btn button:hover {
        background: #01575c !important;
        color: #ffffff !important;
    }
    </style>

    <div class="hero-wrap">
        <div class="hero-grid"></div>
        <div class="hero-content">
            <div class="hero-logo">
                <svg width="48" height="48" viewBox="0 0 48 48" fill="none" aria-label="COVID Intelligence logo">
                    <rect width="48" height="48" rx="12" fill="#01696f"/>
                    <circle cx="24" cy="24" r="10" stroke="white" stroke-width="2" fill="none"/>
                    <circle cx="24" cy="24" r="3" fill="white"/>
                    <line x1="24" y1="10" x2="24" y2="14" stroke="white" stroke-width="2" stroke-linecap="round"/>
                    <line x1="24" y1="34" x2="24" y2="38" stroke="white" stroke-width="2" stroke-linecap="round"/>
                    <line x1="10" y1="24" x2="14" y2="24" stroke="white" stroke-width="2" stroke-linecap="round"/>
                    <line x1="34" y1="24" x2="38" y2="24" stroke="white" stroke-width="2" stroke-linecap="round"/>
                    <line x1="14.93" y1="14.93" x2="17.76" y2="17.76" stroke="white" stroke-width="1.5" stroke-linecap="round"/>
                    <line x1="30.24" y1="30.24" x2="33.07" y2="33.07" stroke="white" stroke-width="1.5" stroke-linecap="round"/>
                    <line x1="33.07" y1="14.93" x2="30.24" y2="17.76" stroke="white" stroke-width="1.5" stroke-linecap="round"/>
                    <line x1="17.76" y1="30.24" x2="14.93" y2="33.07" stroke="white" stroke-width="1.5" stroke-linecap="round"/>
                </svg>
            </div>
            <div class="hero-eyebrow">
                <span class="hero-dot"></span>
                Snowflake Cortex Intelligence
            </div>
            <h1 class="hero-title">
                COVID-19 Public Health<br>
                <span class="accent">Intelligence Platform</span>
            </h1>
            <p class="hero-desc">
                ML-powered forecasting and risk analysis across 19 countries.
                Built on Snowflake Cortex with real epidemiological data.
            </p>
        </div>
        <div class="hero-stats">
            <div class="hero-stat">
                <div class="hero-stat-val"><span class="hi">15+</span></div>
                <div class="hero-stat-label">Countries Tracked</div>
            </div>
            <div class="hero-stat">
                <div class="hero-stat-val">30<span style="font-size:16px;color:#9a9a9a">d</span></div>
                <div class="hero-stat-label">Forecast Horizon</div>
            </div>
            <div class="hero-stat">
                <div class="hero-stat-val"><span class="hi">3</span></div>
                <div class="hero-stat-label">ML Models</div>
            </div>
            <div class="hero-stat">
                <div class="hero-stat-val">3yr</div>
                <div class="hero-stat-label">Historical Data</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    if st.button("Open Dashboard", key="open_dashboard_btn"):
        st.session_state.page = "dashboard"
        st.rerun()