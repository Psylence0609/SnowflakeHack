import streamlit as st
from data import load_countries
import tab_overview, tab_forecasts, tab_reports
import chatbot

def render():
    if "chat_panel_open" not in st.session_state:
        st.session_state.chat_panel_open = False

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
    .top-bar-logo  { display: flex; align-items: center; gap: 12px; }
    .top-bar-name  {
        font-family: 'Cabinet Grotesk', 'Satoshi', sans-serif;
        font-size: 15px; font-weight: 800; color: #1a1a1a; letter-spacing: -0.01em;
    }
    .top-bar-sub {
        font-size: 11px; font-weight: 600; color: #9a9a9a;
        text-transform: uppercase; letter-spacing: 0.08em;
    }

    /* Back button — white bg, teal border */
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

    /* Divider between main and chat panel */
    .chat-divider {
        border-left: 1px solid rgba(0,0,0,0.08);
        padding-left: 1.25rem;
    }

    /* Right pane shell */
    div[data-testid="stVerticalBlock"] div[data-testid="stContainer"][data-stale="false"] {
        scroll-margin-top: 80px;
    }

    .chat-pane-marker + div[data-testid="stContainer"] {
        min-height: 82vh;
    }

    /* Floating chat button (always visible) */
    div[data-testid="stButton"] > button[kind="primary"] {
        position: fixed !important;
        right: 18px !important;
        bottom: 86px !important;
        z-index: 1200 !important;
        width: 64px !important;
        height: 64px !important;
        border-radius: 999px !important;
        background: #159a67 !important;
        color: #ffffff !important;
        border: none !important;
        box-shadow: 0 12px 28px rgba(21, 154, 103, 0.35) !important;
        padding: 0 !important;
        font-size: 30px !important;
        line-height: 1 !important;
        min-height: 64px !important;
    }

    div[data-testid="stButton"] > button[kind="primary"]:hover {
        background: #118559 !important;
        color: #ffffff !important;
        transform: translateY(-2px) scale(1.03);
    }

    .chat-close-btn button {
        background: #f5fbfb !important;
        color: #01696f !important;
        border: 1px solid #bfe3e4 !important;
        border-radius: 8px !important;
        font-weight: 700 !important;
        padding: 3px 10px !important;
        min-height: 32px !important;
    }

    .chat-close-btn button:hover {
        background: #01696f !important;
        color: #ffffff !important;
    }

    @media (max-width: 900px) {
        .chat-pane-marker + div[data-testid="stContainer"] {
            min-height: 68vh;
        }

        div[data-testid="stButton"] > button[kind="primary"] {
            right: 18px !important;
            bottom: 72px !important;
            width: 58px !important;
            height: 58px !important;
            min-height: 58px !important;
        }
    }
    </style>
    """, unsafe_allow_html=True)

    # ── Top bar ──────────────────────────────────────────────────────────────
    st.markdown("""
    <div class="top-bar">
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
    </div>
    """, unsafe_allow_html=True)

    # ── Country selector row ─────────────────────────────────────────────────
    col_sel, col_back, col_spacer = st.columns([2, 1, 5])

    with col_sel:
        country = st.selectbox(
            "Country",
            load_countries(),
            index=0,
            label_visibility="collapsed",
            key="country_select"
        )

    with col_back:
        if st.button("Back to Home", key="back_home"):
            st.session_state.page = "hero"
            st.rerun()

    # Country heading
    st.markdown(f'<div class="country-heading">{country}</div>', unsafe_allow_html=True)

    # ── Main layout + optional right chat pane ─────────────────────────────
    if "active_tab" not in st.session_state:
        st.session_state.active_tab = "Overview"

    def render_tabs() -> None:
        tab1, tab2, tab3 = st.tabs(["Overview", "Forecasts", "Feature Reports"])

        with tab1:
            st.session_state.active_tab = "Overview"
            tab_overview.render(country)

        with tab2:
            st.session_state.active_tab = "Forecasts"
            tab_forecasts.render(country)

        with tab3:
            st.session_state.active_tab = "Feature Reports"
            tab_reports.render(country)

    if st.session_state.get("chat_panel_open", False):
        main_col, chat_col = st.columns([3.2, 1.25], gap="medium")
        with main_col:
            render_tabs()

        with chat_col:
            st.markdown('<div class="chat-pane-marker"></div>', unsafe_allow_html=True)
            pane = st.container(border=True)
            with pane:
                chatbot.render(
                    country=country,
                    active_tab=st.session_state.get("active_tab", "Overview")
                )
    else:
        render_tabs()

        if st.button("🤖", key="open_chat_fab", type="primary"):
            st.session_state.chat_panel_open = True
            st.rerun()