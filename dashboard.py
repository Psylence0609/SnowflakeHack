import streamlit as st
from data import load_countries
import tab_overview, tab_forecasts, tab_reports, tab_data_quality
import chatbot

def render():
    if "chat_messages" not in st.session_state:
        st.session_state.chat_messages = []

    # ── Global CSS ──────────────────────────────────────────────────────────
    st.markdown("""
    <style>
    /* App-wide horizontal padding */
    .block-container {
        padding-left:  2rem !important;
        padding-right: 2rem !important;
        padding-top:   1.5rem !important;
        max-width: 100% !important;
    }

    /* Top bar */
    .top-bar {
        display: flex;
        align-items: center;
        justify-content: space-between;
        padding: 14px 0;
        border-bottom: 1px solid rgba(0,0,0,0.07);
        background: #ffffff;
        position: sticky;
        top: 0;
        z-index: 100;
        margin-bottom: 24px;
    }
    .top-bar-with-back {
        padding-left: 74px;
        margin-left: 18px;
    }
    .top-bar-logo  { display: flex; align-items: center; gap: 12px; }
    .top-bar-name  {
        font-family: 'Cabinet Grotesk', 'Satoshi', sans-serif;
        font-size: 15px; font-weight: 800; color: #1a1a1a; letter-spacing: -0.01em;
    }
    .top-bar-sub {
        font-size: 11px; font-weight: 600; color: #9a9a9a;
        text-transform: uppercase; letter-spacing: 0.08em;
    }

    .top-bar-country {
        position: absolute;
        left: 50%;
        transform: translateX(-50%);
        font-family: 'Cabinet Grotesk', 'Satoshi', sans-serif;
        font-size: clamp(2rem, 3.8vw, 3rem);
        font-weight: 800;
        color: #01696f;
        letter-spacing: -0.01em;
        white-space: nowrap;
    }

    .st-key-back_home {
        margin-bottom: 12px !important;
        width: fit-content !important;
    }
    .st-key-back_home button {
        width: 44px !important;
        height: 44px !important;
        min-height: 44px !important;
        border-radius: 12px !important;
        border: none !important;
        background-color: #01696f !important;
        color: #ffffff !important;
        font-size: 20px !important;
        font-weight: 800 !important;
        padding: 0 !important;
        line-height: 1 !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
    }
    .st-key-back_home button p {
        color: #ffffff !important;
        font-size: 24px !important;
        margin: 0 !important;
    }
    .st-key-back_home button:hover {
        background-color: #01575c !important;
        color: #ffffff !important;
    }

    .top-bar-with-back {
        padding-left: 0px;
    }

    /* KPI Colors */
    [data-testid="stMetricLabel"] { color: #4a4a4a !important; }
    [data-testid="stMetricValue"] { color: #4a4a4a !important; }

    /* Back button fallback (if any other normal buttons are built) — white bg, teal border */
    div[data-testid="stButton"] > button {
        background-color: #ffffff !important;
        color: #01696f !important;
        border: 1.5px solid #01696f !important;
        border-radius: 6px !important;
        font-weight: 600 !important;
        font-size: 13px !important;
        padding: 6px 18px !important;
        transition: background 150ms, color 150ms;
    }
    div[data-testid="stButton"] > button:hover {
        background-color: #01696f !important;
        color: #ffffff !important;
    }

    /* Green dropdowns with white text (country + date selectors) */
    div[data-baseweb="select"] > div {
        background: #01696f !important;
        border: 1px solid #01696f !important;
    }
    div[data-baseweb="select"] * {
        color: #ffffff !important;
    }
    div[data-testid="stDateInput"] input {
        background: #01696f !important;
        color: #ffffff !important;
        border: 1px solid #01696f !important;
    }
    div[data-testid="stDateInput"] svg {
        fill: #ffffff !important;
        color: #ffffff !important;
    }

    /* Country heading — centred, large */
    .country-heading {
        text-align: center;
        font-family: 'Cabinet Grotesk', 'Satoshi', sans-serif;
        font-size: clamp(1.6rem, 2.5vw, 2.4rem);
        font-weight: 800;
        color: #1a1a1a;
        letter-spacing: -0.02em;
        margin: 8px 0 24px 0;
    }

    /* Hide selectbox label */
    label[data-testid="stWidgetLabel"] { display: none !important; }

    </style>
    """, unsafe_allow_html=True)

    # ── Top bar ──────────────────────────────────────────────────────────────
    st.markdown('<div class="top-bar-anchor"></div>', unsafe_allow_html=True)
    if st.button("←", key="back_home", help="Back to Home"):
        st.session_state.page = "hero"
        st.rerun()

    st.markdown(f"""
    <div class="top-bar top-bar-with-back">
      <div class="top-bar-logo">
        <svg width="32" height="32" viewBox="0 0 48 48" fill="none" aria-label="logo">
          <rect width="48" height="48" rx="10" fill="#01696f"/>
          <circle cx="24" cy="24" r="10" stroke="white" stroke-width="2" fill="none"/>
          <circle cx="24" cy="24" r="3" fill="white"/>
          <line x1="24" y1="10" x2="24" y2="14" stroke="white" stroke-width="2" stroke-linecap="round"/>
          <line x1="24" y1="34" x2="24" y2="38" stroke="white" stroke-width="2" stroke-linecap="round"/>
          <line x1="10" y1="24" x2="14" y2="24" stroke="white" stroke-width="2" stroke-linecap="round"/>
          <line x1="34" y1="24" x2="38" y2="24" stroke="white" stroke-width="2" stroke-linecap="round"/>
        </svg>
        <div>
          <div class="top-bar-name">COVID-19 Intelligence</div>
          <div class="top-bar-sub">Powered by Snowflake Cortex</div>
        </div>
      </div>
            <div class="top-bar-country">{st.session_state.get('country_select', 'Argentina')}</div>
    </div>
    """, unsafe_allow_html=True)

    # ── Country selector row ─────────────────────────────────────────────────
    col_sel, col_spacer = st.columns([2, 6])

    with col_sel:
        country = st.selectbox(
            "Country",
            load_countries(),
            index=0,
            label_visibility="collapsed",
            key="country_select"
        )

    # ── Tabs ───────────────────────────────────────────────────────────────
    if "active_tab" not in st.session_state:
        st.session_state.active_tab = "Overview"

    tab1, tab2, tab3, tab4, tab5 = st.tabs(["Overview", "Forecasts", "Feature Reports", "Data Quality", "🤖 Cortex Analyst"])

    with tab1:
        st.session_state.active_tab = "Overview"
        tab_overview.render(country)

    with tab2:
        st.session_state.active_tab = "Forecasts"
        tab_forecasts.render(country)

    with tab3:
        st.session_state.active_tab = "Feature Reports"
        tab_reports.render(country)

    with tab4:
        st.session_state.active_tab = "Data Quality"
        tab_data_quality.render()

    with tab5:
        st.session_state.active_tab = "Cortex Analyst"
        chatbot.render(country=country, active_tab=st.session_state.get("active_tab", "Overview"))