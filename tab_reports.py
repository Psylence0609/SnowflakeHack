"""
Tab 3 — Feature Engineering Reports
Every engineered feature gets a chart or annotated table.
Point features (IS_WAVE_PERIOD, IS_LOCAL_PEAK) are highlighted in red/dark.
"""
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from data import load_death_features, load_vaccine_features

# ── Helpers ────────────────────────────────────────────────────────────────
TEAL   = "#01696f"
RED    = "#c0392b"
AMBER  = "#e67e22"
NAVY   = "#005f94"
MUTED  = "rgba(0,0,0,0.05)"

def _section(title: str, subtitle: str = ""):
    sub_html = f"<p style='font-size:13px;color:#4a4a4a;margin:4px 0 0;'>{subtitle}</p>" if subtitle else ""
    st.markdown(f"""
    <div style="margin:32px 0 16px;">
        <h3 style="font-size:16px;font-weight:700;font-family:'Cabinet Grotesk',sans-serif;
            color:#01696f;margin:0;">{title}</h3>
        {sub_html}
    </div>
    """, unsafe_allow_html=True)

def _base_layout(title="", height=300):
    return dict(
        title=dict(text=title, font=dict(size=13, family="Satoshi", color="#01696f"), x=0),
        height=height, margin=dict(l=0, r=0, t=40 if title else 8, b=0),
        plot_bgcolor="#ffffff", paper_bgcolor="#ffffff",
        legend=dict(orientation="h", y=1.14, x=0,
                    font=dict(size=11, family="Satoshi"), bgcolor="rgba(0,0,0,0)"),
        xaxis=dict(showgrid=False,
                   tickfont=dict(size=11, family="Satoshi", color="#4a4a4a")),
        yaxis=dict(showgrid=True, gridcolor=MUTED,
                   tickfont=dict(size=11, family="Satoshi", color="#4a4a4a"),
                   tickformat=","),
    )

# ── Individual feature charts ──────────────────────────────────────────────

def chart_cfr(df):
    _section("Case Fatality Rate (CFR %)",
             "Deaths as a percentage of confirmed cases over time.")
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=df["DATE"], y=df["CFR_PCT"], mode="lines",
        line=dict(color=TEAL, width=2), fill="tozeroy",
        fillcolor="rgba(1,105,111,0.08)", name="CFR %"
    ))
    layout = _base_layout(height=260)
    layout["yaxis"]["ticksuffix"] = "%"   # <-- patch into the dict, not a second kwarg
    fig.update_layout(**layout)
    st.plotly_chart(fig, use_container_width=True)


def chart_wow(df):
    _section("Week-over-Week Case Growth (%)",
             "Positive values indicate accelerating spread; values below zero indicate decline.")

    colors = [RED if v > 0 else TEAL for v in df["WOW_GROWTH_PCT"].fillna(0)]
    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=df["DATE"], y=df["WOW_GROWTH_PCT"],
        marker_color=colors, name="WoW Growth"
    ))
    fig.add_hline(y=0, line_width=1, line_color="rgba(0,0,0,0.2)")
    layout = _base_layout(height=260)
    layout["yaxis"]["ticksuffix"] = "%"
    fig.update_layout(**layout)
    st.plotly_chart(fig, use_container_width=True)


def chart_doubling_time(df):
    _section("Doubling Time (Days)",
             "Higher values mean slower spread. Values below 14 days signal rapid escalation.")
    sub = df[df["DOUBLING_TIME_DAYS"].notna()]
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=sub["DATE"], y=sub["DOUBLING_TIME_DAYS"],
        mode="lines", line=dict(color=NAVY, width=2),
        fill="tozeroy", fillcolor="rgba(0,95,148,0.07)", name="Doubling Time"
    ))
    fig.add_hline(y=14, line_width=1, line_dash="dot", line_color=RED,
                  annotation_text="14-day threshold",
                  annotation_font_size=11, annotation_font_color=RED)
    layout = _base_layout(height=260)
    layout["yaxis"]["ticksuffix"] = " d"
    fig.update_layout(**layout)
    st.plotly_chart(fig, use_container_width=True)


def chart_per_100k(df):
    _section("Cases and Deaths per 100,000 Population",
             "Normalised incidence rates for cross-country comparability.")
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=df["DATE"], y=df["CASES_PER_100K"],
        mode="lines", line=dict(color=TEAL, width=2), name="Cases / 100K"
    ))
    fig.add_trace(go.Scatter(
        x=df["DATE"], y=df["DEATHS_PER_100K"],
        mode="lines", line=dict(color=RED, width=2), name="Deaths / 100K",
        yaxis="y2"
    ))
    layout = _base_layout(height=280)
    layout["yaxis"].update(
        title="Cases / 100K",
        title_font=dict(size=11, family="Satoshi", color=TEAL),
        tickfont=dict(size=11, family="Satoshi", color=TEAL)
    )
    layout["yaxis2"] = dict(
        overlaying="y", side="right", showgrid=False,
        tickformat=",",
        title="Deaths / 100K",
        title_font=dict(size=11, family="Satoshi", color=RED),
        tickfont=dict(size=11, family="Satoshi", color=RED)
    )
    fig.update_layout(**layout)


def chart_risk_score(df):
    _section("Composite Risk Score Over Time",
             "Aggregated severity index. Values above 60 are considered high risk.")
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=df["DATE"], y=df["RISK_SCORE"],
        mode="lines", line=dict(color=AMBER, width=2),
        fill="tozeroy", fillcolor="rgba(230,126,34,0.08)", name="Risk Score"
    ))
    fig.add_hline(y=60, line_width=1, line_dash="dot", line_color=RED,
                  annotation_text="High risk threshold",
                  annotation_font_size=11, annotation_font_color=RED)
    layout = _base_layout(height=260)
    fig.update_layout(**layout)
    st.plotly_chart(fig, use_container_width=True)


def chart_wave_and_peaks(df):
    _section("Wave Periods and Local Peaks",
             "Red bands mark detected wave periods. Red markers indicate local case peaks.")
    fig = go.Figure()

    # Base: 7-day rolling avg
    fig.add_trace(go.Scatter(
        x=df["DATE"], y=df["ROLLING_7DAY_CASES"],
        mode="lines", line=dict(color="#aaaaaa", width=1.5), name="7-Day Avg"
    ))

    # Wave periods — shaded background spans
    wave_rows = df[df["IS_WAVE_PERIOD"] == 1]
    if len(wave_rows) > 0:
        # Find contiguous wave groups
        wave_rows = wave_rows.copy()
        wave_rows["group"] = (wave_rows.index.to_series().diff() > 1).cumsum()
        for _, grp in wave_rows.groupby("group"):
            fig.add_vrect(
                x0=grp["DATE"].iloc[0].strftime("%Y-%m-%d"), x1=grp["DATE"].iloc[-1].strftime("%Y-%m-%d"),
                fillcolor="rgba(192,57,43,0.08)", line_width=0,
                annotation_text="Wave" if len(grp) > 7 else "",
                annotation_font_size=10, annotation_font_color=RED
            )

    # Local peaks
    peaks = df[df["IS_LOCAL_PEAK"] == 1]
    if len(peaks) > 0:
        fig.add_trace(go.Scatter(
            x=peaks["DATE"], y=peaks["ROLLING_7DAY_CASES"],
            mode="markers",
            marker=dict(color=RED, size=9, symbol="circle",
                        line=dict(color="#ffffff", width=1.5)),
            name="Local Peak"
        ))

    fig.update_layout(**_base_layout(height=320))
    st.plotly_chart(fig, use_container_width=True)


def chart_cases_14d_ago(df):
    _section("Cases 14 Days Ago vs. Today",
             "Lagged comparison used as a feature in ML forecasting.")
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=df["DATE"], y=df["NEW_CASES"],
        mode="lines", line=dict(color=TEAL, width=1.5), name="New Cases Today"
    ))
    fig.add_trace(go.Scatter(
        x=df["DATE"], y=df["CASES_14D_AGO"],
        mode="lines", line=dict(color="#4a4a4a", width=1.5, dash="dot"), name="Cases 14d Ago"
    ))
    fig.update_layout(**_base_layout(height=280))
    st.plotly_chart(fig, use_container_width=True)


def chart_temporal_features(df, vdf):
    _section("Temporal Feature Distributions",
             "Month, day-of-week, and week-of-year distributions used as ML calendar features.")
    col1, col2 = st.columns(2)

    # Cases by day of week (point aggregates → bar)
    dow_map = {0:"Mon",1:"Tue",2:"Wed",3:"Thu",4:"Fri",5:"Sat",6:"Sun"}
    dow_avg = df.groupby("DAY_OF_WEEK")["NEW_CASES"].mean().reset_index()
    dow_avg["DAY_NAME"] = dow_avg["DAY_OF_WEEK"].map(dow_map)
    with col1:
        fig_dow = go.Figure(go.Bar(
            x=dow_avg["DAY_NAME"], y=dow_avg["NEW_CASES"],
            marker_color=TEAL, name="Avg New Cases"
        ))
        fig_dow.update_layout(**_base_layout("Avg Cases by Day of Week", 240))
        st.plotly_chart(fig_dow, use_container_width=True)

    # Cases by month (point aggregates → bar)
    mon_map = {1:"Jan",2:"Feb",3:"Mar",4:"Apr",5:"May",6:"Jun",
               7:"Jul",8:"Aug",9:"Sep",10:"Oct",11:"Nov",12:"Dec"}
    mon_avg = df.groupby("MONTH_NUM")["NEW_CASES"].mean().reset_index()
    mon_avg["MON_NAME"] = mon_avg["MONTH_NUM"].map(mon_map)
    with col2:
        fig_mon = go.Figure(go.Bar(
            x=mon_avg["MON_NAME"], y=mon_avg["NEW_CASES"],
            marker_color=NAVY, name="Avg New Cases"
        ))
        fig_mon.update_layout(**_base_layout("Avg Cases by Month", 240))
        st.plotly_chart(fig_mon, use_container_width=True)


def chart_vax_features(vdf):
    _section("Vaccination Feature Breakdown",
             "Total vaccinated, fully vaccinated, and 14-day lagged coverage.")
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=vdf["DATE"], y=vdf["TOTAL_VACCINATED"],
        mode="lines", line=dict(color=NAVY, width=2),
        fill="tozeroy", fillcolor="rgba(0,95,148,0.07)", name="Total Vaccinated"
    ))
    fig.add_trace(go.Scatter(
        x=vdf["DATE"], y=vdf["TOTAL_FULLY_VACCINATED"],
        mode="lines", line=dict(color=TEAL, width=2), name="Fully Vaccinated"
    ))
    if "VAX_COVERAGE_14D_LAG" in vdf.columns:
        fig.add_trace(go.Scatter(
            x=vdf["DATE"], y=vdf["VAX_COVERAGE_14D_LAG"],
            mode="lines", line=dict(color="#4a4a4a", width=1.5, dash="dot"),
            name="Coverage (14d lag)"
        ))
    fig.update_layout(**_base_layout(height=300))
    st.plotly_chart(fig, use_container_width=True)


# ── Main render ────────────────────────────────────────────────────────────
def render(country: str):
    df  = load_death_features(country)
    vdf = load_vaccine_features(country)

    # 1. CFR
    chart_cfr(df)
    st.divider()

    # 2. Week-over-week growth
    chart_wow(df)
    st.divider()

    # 3. Doubling time
    chart_doubling_time(df)
    st.divider()

    # 4. Per-100K normalised
    # chart_per_100k(df)
    # st.divider()

    # 5. Composite risk score
    chart_risk_score(df)
    st.divider()

    # 6. Wave periods + local peaks (point features annotated in red)
    chart_wave_and_peaks(df)
    st.divider()

    # 7. 14-day lag feature
    chart_cases_14d_ago(df)
    st.divider()

    # 8. Temporal features (calendar aggregates)
    chart_temporal_features(df, vdf)
    st.divider()

    # 9. Vaccination features
    chart_vax_features(vdf)
