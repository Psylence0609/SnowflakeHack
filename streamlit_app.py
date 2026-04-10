import streamlit as st

st.set_page_config(
    page_title="COVID-19 Intelligence",
    page_icon=None,
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ── Global CSS ─────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://api.fontshare.com/v2/css?f[]=satoshi@400,500,600,700&f[]=cabinet-grotesk@700,800&display=swap');

*, *::before, *::after { box-sizing: border-box; }

html, body, [data-testid="stAppViewContainer"], [data-testid="stMain"],
[data-testid="stMainBlockContainer"], section.main {
    background: #ffffff !important;
    color: #1a1a1a !important;
    font-family: 'Satoshi', 'Inter', sans-serif !important;
}

[data-testid="stSidebar"] { display: none !important; }
[data-testid="stHeader"] { display: none !important; }
footer { display: none !important; }
#MainMenu { display: none !important; }

.block-container {
    padding: 0 !important;
    max-width: 100% !important;
}

h1, h2, h3 {
    font-family: 'Cabinet Grotesk', 'Satoshi', sans-serif !important;
    color: #1a1a1a !important;
}

.stButton > button {
    font-family: 'Satoshi', sans-serif !important;
    font-weight: 600 !important;
    font-size: 14px !important;
    border-radius: 6px !important;
    transition: all 180ms cubic-bezier(0.16, 1, 0.3, 1) !important;
}

[data-testid="metric-container"] {
    background: #ffffff !important;
    border: 1px solid oklch(0.1 0 0 / 0.08) !important;
    border-radius: 10px !important;
    padding: 20px 24px !important;
    box-shadow: 0 1px 3px rgba(0,0,0,0.06), 0 4px 12px rgba(0,0,0,0.04) !important;
}

[data-testid="stTabs"] [data-baseweb="tab-list"] {
    gap: 4px !important;
    background: #f5f5f3 !important;
    padding: 4px !important;
    border-radius: 8px !important;
    width: fit-content !important;
}

[data-testid="stTabs"] [data-baseweb="tab"] {
    font-family: 'Satoshi', sans-serif !important;
    font-weight: 600 !important;
    font-size: 13px !important;
    border-radius: 6px !important;
    padding: 8px 20px !important;
    color: #6b6b6b !important;
    background: transparent !important;
}

[data-testid="stTabs"] [aria-selected="true"] {
    background: #ffffff !important;
    color: #1a1a1a !important;
    box-shadow: 0 1px 3px rgba(0,0,0,0.1) !important;
}

[data-testid="stSelectbox"] label,
[data-testid="stDateInput"] label {
    font-size: 12px !important;
    font-weight: 600 !important;
    letter-spacing: 0.06em !important;
    text-transform: uppercase !important;
    color: #6b6b6b !important;
}

.stDataFrame {
    border: 1px solid rgba(0,0,0,0.08) !important;
    border-radius: 8px !important;
    overflow: hidden !important;
}

div[data-testid="stPlotlyChart"] {
    border: 1px solid rgba(0,0,0,0.06) !important;
    border-radius: 10px !important;
    overflow: hidden !important;
    background: #ffffff !important;
}
</style>
""", unsafe_allow_html=True)

# ── Session state router ───────────────────────────────────────────────────
if "page" not in st.session_state:
    st.session_state.page = "hero"

if st.session_state.page == "hero":
    import hero
    hero.render()
elif st.session_state.page == "dashboard":
    import dashboard
    dashboard.render()