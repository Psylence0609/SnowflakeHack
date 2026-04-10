"""Tab 1 — Country KPIs"""
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from data import load_death_features, load_vaccine_features, load_risk_tiers

TIER_COLOR = {"HIGH": "#c0392b", "MODERATE": "#e67e22", "LOW": "#27ae60"}
TIER_BG    = {"HIGH": "#fdf0ef", "MODERATE": "#fef6ee", "LOW": "#edfaf1"}

def render(country: str):
    df   = load_death_features(country)
    vax  = load_vaccine_features(country)
    risk = load_risk_tiers()

    latest   = df.iloc[-1]
    prev_week = df.iloc[-8] if len(df) > 8 else df.iloc[0]
    r_row    = risk[risk["COUNTRY_REGION"] == country]
    tier     = r_row["RISK_TIER"].values[0] if len(r_row) else "N/A"
    trend    = r_row["FORECAST_TREND"].values[0] if len(r_row) else "N/A"
    risk_score = r_row["AVG_RISK_SCORE"].values[0] if len(r_row) else "N/A"

    # ── Risk Banner ────────────────────────────────────────────────────────
    tc = TIER_COLOR.get(tier, "#6b6b6b")
    tb = TIER_BG.get(tier, "#f5f5f5")
    st.markdown(f"""
    <div style="
        background:{tb};border:1px solid {tc}22;border-radius:10px;
        padding:16px 24px;margin-bottom:28px;
        display:flex;align-items:center;gap:16px;">
        <div style="width:10px;height:10px;border-radius:50%;background:{tc};flex-shrink:0;"></div>
        <div>
            <span style="font-size:12px;font-weight:700;text-transform:uppercase;
                letter-spacing:0.1em;color:{tc};">{tier} RISK</span>
            <span style="font-size:13px;color:#6b6b6b;margin-left:16px;">
                30-day forecast: <strong style="color:#1a1a1a;">{trend}</strong>
            </span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ── KPI Row 1 ──────────────────────────────────────────────────────────
    c1, c2, c3, c4 = st.columns(4)

    total_cases = int(latest["TOTAL_CASES"])
    total_deaths = int(latest["TOTAL_DEATHS"])
    cfr = round(float(latest["CFR_PCT"]), 2)
    wow = round(float(latest["WOW_GROWTH_PCT"]) if pd.notna(latest["WOW_GROWTH_PCT"]) else 0, 1)

    c1.metric("Total Confirmed Cases",
              f"{total_cases:,}",
              delta=f"+{int(latest['NEW_CASES']):,} today")
    c2.metric("Total Deaths",
              f"{total_deaths:,}",
              delta=f"+{int(latest['NEW_DEATHS']):,} today",
              delta_color="inverse")
    c3.metric("Case Fatality Rate",
              f"{cfr}%",
              delta=f"{round(cfr - float(prev_week['CFR_PCT']),3):+.3f}% vs last week",
              delta_color="inverse")
    c4.metric("Week-over-Week Growth",
              f"{wow:+.1f}%",
              delta="Rising" if wow > 5 else ("Stable" if wow > -5 else "Declining"),
              delta_color="inverse" if wow > 5 else ("off" if -5 <= wow <= 5 else "normal"))

    st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)

    # ── KPI Row 2 ──────────────────────────────────────────────────────────
    c5, c6, c7, c8 = st.columns(4)

    cases_100k  = round(float(latest["CASES_PER_100K"]), 1)
    deaths_100k = round(float(latest["DEATHS_PER_100K"]), 2)
    r7_cases    = int(latest["ROLLING_7DAY_CASES"]) if pd.notna(latest["ROLLING_7DAY_CASES"]) else 0
    dt          = round(float(latest["DOUBLING_TIME_DAYS"]),1) if pd.notna(latest["DOUBLING_TIME_DAYS"]) else None

    latest_vax  = vax.iloc[-1] if len(vax) else None
    vax_val     = f"{int(latest_vax['TOTAL_VACCINATED']):,}" if latest_vax is not None and pd.notna(latest_vax['TOTAL_VACCINATED']) else "N/A"

    c5.metric("Cases per 100K", f"{cases_100k:,}")
    c6.metric("Deaths per 100K", f"{deaths_100k:,}")
    c7.metric("7-Day Avg New Cases", f"{r7_cases:,}")
    c8.metric("Doubling Time", f"{dt} days" if dt else "N/A")

    st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)

    # ── KPI Row 3 — Vaccination ────────────────────────────────────────────
    c9, c10, c11, c12 = st.columns(4)

    if latest_vax is not None:
        tv   = int(latest_vax["TOTAL_VACCINATED"])   if pd.notna(latest_vax["TOTAL_VACCINATED"])   else 0
        tfv  = int(latest_vax["TOTAL_FULLY_VACCINATED"]) if pd.notna(latest_vax["TOTAL_FULLY_VACCINATED"]) else 0
        nv   = int(latest_vax["NEW_VACCINATIONS"])   if pd.notna(latest_vax["NEW_VACCINATIONS"])   else 0
        lag  = int(latest_vax["VAX_COVERAGE_14D_LAG"]) if pd.notna(latest_vax["VAX_COVERAGE_14D_LAG"]) else 0
        c9.metric("Total Vaccinated",       f"{tv:,}")
        c10.metric("Fully Vaccinated",      f"{tfv:,}")
        c11.metric("Daily Vaccinations",    f"{nv:,}")
        c12.metric("Vax Coverage (14d lag)",f"{lag:,}")
    else:
        c9.metric("Vaccination Data", "Not available")

    st.markdown("<div style='height:24px'></div>", unsafe_allow_html=True)

    # ── Mini sparkline: 30-day new cases ──────────────────────────────────
    last30 = df.tail(30)
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=last30["DATE"], y=last30["ROLLING_7DAY_CASES"],
        mode="lines", line=dict(color="#01696f", width=2),
        fill="tozeroy", fillcolor="rgba(1,105,111,0.07)",
        name="7-day avg"
    ))
    fig.update_layout(
        title=dict(text="7-Day Rolling Average — Last 30 Days",
                   font=dict(size=13, family="Satoshi", color="#1a1a1a")),
        height=180, margin=dict(l=0, r=0, t=36, b=0),
        plot_bgcolor="#ffffff", paper_bgcolor="#ffffff",
        showlegend=False,
        xaxis=dict(showgrid=False, showticklabels=True,
                   tickfont=dict(size=11, family="Satoshi", color="#9a9a9a")),
        yaxis=dict(showgrid=True, gridcolor="rgba(0,0,0,0.05)",
                   tickfont=dict(size=11, family="Satoshi", color="#9a9a9a"),
                   tickformat=",")
    )
    st.plotly_chart(fig, use_container_width=True)

    # ── Risk Score gauge sparkline ─────────────────────────────────────────
    # risk_score = round(float(latest["RISK_SCORE"]) if pd.notna(latest["RISK_SCORE"]) else 0, 1)
    st.markdown(f"""
    <div style="background:#f9f9f9;border:1px solid rgba(0,0,0,0.07);
        border-radius:10px;padding:20px 24px;margin-top:8px;">
        <div style="font-size:11px;font-weight:700;text-transform:uppercase;
            letter-spacing:0.1em;color:#9a9a9a;margin-bottom:10px;">
            Composite Risk Score
        </div>
        <div style="display:flex;align-items:center;gap:16px;">
            <div style="font-size:36px;font-weight:800;font-family:'Cabinet Grotesk',sans-serif;
                color:{tc};font-variant-numeric:tabular-nums;">{risk_score}</div>
            <div style="flex:1;background:#ebebeb;border-radius:4px;height:8px;">
                <div style="width:{min(risk_score,100)}%;background:{tc};
                    border-radius:4px;height:8px;transition:width 0.6s ease;"></div>
            </div>
            <div style="font-size:12px;font-weight:600;color:{tc};">{tier}</div>
        </div>
    </div>
    """, unsafe_allow_html=True)
