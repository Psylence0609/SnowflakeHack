"""Tab 2 — Forecasts with date range filter and confidence cone"""
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from data import (load_death_features, load_vaccine_features,
                  load_cases_forecast, load_deaths_forecast, load_vax_forecast)

# Color palette — distinct, non-gradient, accessible
PALETTE = {
    "cases":   {"line": "#01696f", "fill": "rgba(1,105,111,0.10)", "ci": "rgba(1,105,111,0.15)"},
    "deaths":  {"line": "#a13544", "fill": "rgba(161,53,68,0.08)",  "ci": "rgba(161,53,68,0.13)"},
    "vax":     {"line": "#005f94", "fill": "rgba(0,95,148,0.08)",   "ci": "rgba(0,95,148,0.13)"},
}

def _chart(actual: pd.DataFrame, forecast: pd.DataFrame,
           date_col: str, act_col: str, fc_col: str,
           title: str, y_label: str, scheme: dict) -> go.Figure:

    fig = go.Figure()

    # Historical
    fig.add_trace(go.Scatter(
        x=actual[date_col], y=actual[act_col],
        mode="lines", name="Historical",
        line=dict(color=scheme["line"], width=2),
        fill="tozeroy", fillcolor=scheme["fill"]
    ))

    # Forecast — filled confidence cone first, then the forecast line on top
    if len(forecast) > 0 and "UPPER_BOUND" in forecast.columns:
        fig.add_trace(go.Scatter(
            x=pd.concat([forecast[date_col], forecast[date_col].iloc[::-1]]),
            y=pd.concat([forecast["UPPER_BOUND"], forecast["LOWER_BOUND"].iloc[::-1]]),
            fill="toself", fillcolor=scheme["ci"],
            line=dict(color="rgba(0,0,0,0)"),
            hoverinfo="skip", showlegend=True, name="90% CI"
        ))

    if len(forecast) > 0:
        fig.add_trace(go.Scatter(
            x=forecast[date_col], y=forecast[fc_col],
            mode="lines", name="Forecast",
            line=dict(color=scheme["line"], width=2, dash="dash")
        ))

    # Vertical divider at forecast start
    if len(forecast) > 0:
        split = forecast[date_col].iloc[0].strftime("%Y-%m-%d")
        fig.add_shape(
            type="line",
            x0=split, x1=split,
            y0=0, y1=1,
            xref="x", yref="paper",
            line=dict(color="rgba(0,0,0,0.2)", width=1, dash="dot")
        )
        fig.add_annotation(
            x=split, y=1, xref="x", yref="paper",
            text="Forecast begins",
            showarrow=False,
            xanchor="left",
            yanchor="bottom",
            font=dict(size=11, color="#9a9a9a", family="Satoshi"),
            bgcolor="rgba(255,255,255,0.8)",
            borderpad=3
        )

    fig.update_layout(
        title=dict(text=title, font=dict(size=20, family="Satoshi", color="#1a1a1a"), x=0),
        height=360, margin=dict(l=0, r=0, t=48, b=0),
        plot_bgcolor="#ffffff", paper_bgcolor="#ffffff",
        legend=dict(orientation="h", y=1.02,x=0,
                    font=dict(size=12, family="Satoshi"),
                    bgcolor="rgba(0,0,0,0)"),
        xaxis=dict(showgrid=False,
                   tickfont=dict(size=11, family="Satoshi", color="#9a9a9a"),
                   rangeslider=dict(visible=False)),
        yaxis=dict(showgrid=True, gridcolor="rgba(0,0,0,0.05)",
                   title=y_label,
                   tickfont=dict(size=11, family="Satoshi", color="#9a9a9a"),
                   title_font=dict(size=11, family="Satoshi", color="#9a9a9a"),
                   tickformat=",")
    )
    return fig


def render(country: str):
    df   = load_death_features(country)
    vax  = load_vaccine_features(country)
    fc_c = load_cases_forecast(country)
    fc_d = load_deaths_forecast(country)
    fc_v = load_vax_forecast(country)

    # ── Date range filter ──────────────────────────────────────────────────
    min_date = df["DATE"].min().date()
    max_date_all = max(
        df["DATE"].max().date(),
        fc_c["DATE"].max().date() if len(fc_c) else df["DATE"].min().date(),
        fc_d["DATE"].max().date() if len(fc_d) else df["DATE"].min().date(),
        fc_v["DATE"].max().date() if len(fc_v) else df["DATE"].min().date(),
    )

    st.markdown("""
    <div style="display:flex;align-items:center;gap:8px;margin-bottom:20px;">
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#6b6b6b" stroke-width="2">
            <rect x="3" y="4" width="18" height="18" rx="2"/><line x1="16" y1="2" x2="16" y2="6"/>
            <line x1="8" y1="2" x2="8" y2="6"/><line x1="3" y1="10" x2="21" y2="10"/>
        </svg>
        <span style="font-size:12px;font-weight:700;text-transform:uppercase;
            letter-spacing:0.1em;color:#6b6b6b;">Date Range</span>
    </div>
    """, unsafe_allow_html=True)

    col_d1, col_d2, col_spacer = st.columns([1, 1, 3])
    with col_d1:
        d_start = st.date_input("From", value=min_date, min_value=min_date,
                                max_value=max_date_all, key="fc_start")
    with col_d2:
        d_end = st.date_input("To", value=max_date_all, min_value=min_date,
                              max_value=max_date_all, key="fc_end")

    # Filter data
    df_f  = df[(df["DATE"].dt.date >= d_start) & (df["DATE"].dt.date <= d_end)]
    vax_f = vax[(vax["DATE"].dt.date >= d_start) & (vax["DATE"].dt.date <= d_end)]
    fc_c_f = fc_c[fc_c["DATE"].dt.date <= d_end]
    fc_d_f = fc_d[fc_d["DATE"].dt.date <= d_end]
    fc_v_f = fc_v[fc_v["DATE"].dt.date <= d_end]



    st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)

    # ── Chart 1: Rolling 7-day Cases ──────────────────────────────────────
    fig1 = _chart(
        actual=df_f, forecast=fc_c_f,
        date_col="DATE", act_col="ROLLING_7DAY_CASES", fc_col="FORECAST",
        title="7-Day Rolling Average — Confirmed Cases",
        y_label="Average Daily Cases",
        scheme=PALETTE["cases"]
    )
    st.plotly_chart(fig1, use_container_width=True)

    st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)

    # ── Chart 2: Rolling 7-day Deaths ─────────────────────────────────────
    fig2 = _chart(
        actual=df_f, forecast=fc_d_f,
        date_col="DATE", act_col="ROLLING_7DAY_DEATHS", fc_col="FORECAST",
        title="7-Day Rolling Average — Deaths",
        y_label="Average Daily Deaths",
        scheme=PALETTE["deaths"]
    )
    st.plotly_chart(fig2, use_container_width=True)

    st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)

    # ── Chart 3: Daily Vaccinations ───────────────────────────────────────
    fig3 = _chart(
        actual=vax_f, forecast=fc_v_f,
        date_col="DATE", act_col="NEW_VACCINATIONS", fc_col="FORECAST",
        title="Daily New Vaccinations",
        y_label="Doses Administered",
        scheme=PALETTE["vax"]
    )
    st.plotly_chart(fig3, use_container_width=True)
