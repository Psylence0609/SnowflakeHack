"""
data.py  —  All Snowflake queries centralised here.
Replace get_session() with your actual session if needed.
"""
from snowflake.snowpark.context import get_active_session
import streamlit as st
import pandas as pd

@st.cache_data(ttl=300)
def load_countries() -> list[str]:
    session = get_session()
    df = session.sql("""
        SELECT DISTINCT COUNTRY_REGION
        FROM HACKATHON.SG01.COVID_DEATH_FEATURES
        ORDER BY COUNTRY_REGION
    """).to_pandas()
    return df["COUNTRY_REGION"].tolist()

@st.cache_resource
def get_session():
    return get_active_session()

@st.cache_data(ttl=300)
def load_death_features(country: str) -> pd.DataFrame:
    session = get_session()
    df = session.sql(f"""
        SELECT DATE, COUNTRY_REGION,
               TOTAL_CASES, TOTAL_DEATHS,
               NEW_CASES, NEW_DEATHS,
               ROLLING_7DAY_CASES, ROLLING_7DAY_DEATHS,
               CFR_PCT, WOW_GROWTH_PCT, DOUBLING_TIME_DAYS,
               IS_WAVE_PERIOD, CASES_14D_AGO, IS_LOCAL_PEAK,
               DEATHS_PER_100K, CASES_PER_100K, RISK_SCORE,
               MONTH_NUM, DAY_OF_WEEK, WEEK_OF_YEAR
        FROM HACKATHON.SG01.COVID_DEATH_FEATURES
        WHERE COUNTRY_REGION = '{country}'
        ORDER BY DATE
    """).to_pandas()
    df["DATE"] = pd.to_datetime(df["DATE"])
    return df

@st.cache_data(ttl=300)
def load_vaccine_features(country: str) -> pd.DataFrame:
    session = get_session()
    df = session.sql(f"""
        SELECT DATE, COUNTRY_REGION,
               TOTAL_VACCINATED, TOTAL_FULLY_VACCINATED,
               NEW_VACCINATIONS, VAX_COVERAGE_14D_LAG,
               MONTH_NUM, DAY_OF_WEEK, WEEK_OF_YEAR
        FROM HACKATHON.SG01.COVID_VACCINES_FEATURES
        WHERE COUNTRY_REGION = '{country}'
        ORDER BY DATE
    """).to_pandas()
    df["DATE"] = pd.to_datetime(df["DATE"])
    return df

@st.cache_data(ttl=300)
def load_cases_forecast(country: str) -> pd.DataFrame:
    session = get_session()
    df = session.sql(f"""
        SELECT FORECAST_DATE AS DATE,
               PREDICTED_ROLLING_7DAY_CASES AS FORECAST,
               LOWER_BOUND, UPPER_BOUND
        FROM HACKATHON.SG01.FORECAST_ROLLING_7DAY_CASES
        WHERE COUNTRY_REGION = '{country}'
        ORDER BY FORECAST_DATE
    """).to_pandas()
    df["DATE"] = pd.to_datetime(df["DATE"])
    return df

@st.cache_data(ttl=300)
def load_deaths_forecast(country: str) -> pd.DataFrame:
    session = get_session()
    df = session.sql(f"""
        SELECT FORECAST_DATE AS DATE,
               PREDICTED_ROLLING_7DAY_DEATHS AS FORECAST,
               LOWER_BOUND, UPPER_BOUND
        FROM HACKATHON.SG01.FORECAST_ROLLING_7DAY_DEATHS
        WHERE COUNTRY_REGION = '{country}'
        ORDER BY FORECAST_DATE
    """).to_pandas()
    df["DATE"] = pd.to_datetime(df["DATE"])
    return df

@st.cache_data(ttl=300)
def load_vax_forecast(country: str) -> pd.DataFrame:
    session = get_session()
    df = session.sql(f"""
        SELECT TS AS DATE,
           FORECAST,
           LOWER_BOUND, UPPER_BOUND
        FROM HACKATHON.SG01.COVID_VACCINATIONS_FORECAST_RESULTS
        WHERE SERIES::VARCHAR = '{country}'
        ORDER BY TS
    """).to_pandas()
    df["DATE"] = pd.to_datetime(df["DATE"])
    return df

@st.cache_data(ttl=300)
def load_risk_tiers() -> pd.DataFrame:
    session = get_session()
    df = session.sql("""
        SELECT COUNTRY_REGION, RISK_TIER, FORECAST_TREND,
               AVG_RISK_SCORE, AVG_CFR_PCT, AVG_WOW_GROWTH_PCT,
               CASES_PER_100K, DEATHS_PER_100K, CURRENTLY_IN_WAVE
        FROM HACKATHON.SG01.COUNTRY_RISK_TIERS
        ORDER BY AVG_RISK_SCORE DESC
    """).to_pandas()
    return df

@st.cache_data(ttl=300)
def load_data_quality_report() -> pd.DataFrame:
    session = get_session()
    df = session.sql("""
        SELECT *
        FROM HACKATHON.SG01.DATA_QUALITY_REPORT
    """).to_pandas()
    return df

@st.cache_data(ttl=300)
def load_bias_flags() -> pd.DataFrame:
    session = get_session()
    df = session.sql("""
        SELECT *
        FROM HACKATHON.SG01.BIAS_FLAGS
    """).to_pandas()
    return df