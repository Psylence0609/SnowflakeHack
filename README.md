# COVID-19 Public Health Intelligence Platform

This project builds an end-to-end COVID analytics stack on Snowflake and serves it through a Streamlit dashboard with a Cortex Analyst assistant.

## Demo

- Demo link: [Add your demo URL here](#)

## Tech Stack

- Data platform: Snowflake
- Data source: Starschema COVID-19 Epidemiological Data share
- SQL pipeline: Snowflake SQL in `scripts.sql`
- ML: `SNOWFLAKE.ML.FORECAST` in `ML.ipynb`
- App framework: Streamlit
- Visualization: Plotly + Streamlit native components
- Conversational analytics: Snowflake Cortex Analyst via semantic view `HACKATHON.SG01.FIRST`

## Architecture Diagram

![Architecture](Architecture.png)

## UI Preview Carousel

<marquee behavior="scroll" direction="left" scrollamount="8">
  <img src="Images/img4.png" alt="Dashboard Preview 4" width="520" />
  &nbsp;&nbsp;&nbsp;&nbsp;
  <img src="Images/img1.png" alt="Dashboard Preview 1" width="520" />
  &nbsp;&nbsp;&nbsp;&nbsp;
  <img src="Images/img2.png" alt="Dashboard Preview 2" width="520" />
  &nbsp;&nbsp;&nbsp;&nbsp;
  <img src="Images/img3.png" alt="Dashboard Preview 3" width="520" />
  &nbsp;&nbsp;&nbsp;&nbsp;
  <img src="Images/img4.png" alt="Dashboard Preview 4" width="520" />
  &nbsp;&nbsp;&nbsp;&nbsp;
  <img src="Images/img1.png" alt="Dashboard Preview 1" width="520" />
  &nbsp;&nbsp;&nbsp;&nbsp;
  <img src="Images/img2.png" alt="Dashboard Preview 2" width="520" />
  &nbsp;&nbsp;&nbsp;&nbsp;
  <img src="Images/img3.png" alt="Dashboard Preview 3" width="520" />
</marquee>


## 1) Data Procurement and Curation

Data is sourced from the Snowflake shared dataset:

- Source database: `COVID19_EPIDEMIOLOGICAL_DATA`
- Source schema: `PUBLIC`
- Source tables:
  - `JHU_COVID_19` (cases and deaths)
  - `OWID_VACCINATIONS` (vaccination metrics)

Using the SQL in `scripts.sql`, the pipeline:

- Filters to country-level records (`PROVINCE_STATE IS NULL`)
- Computes coverage quality and keeps countries with sufficiently abundant history
- Builds curated base tables for deaths/cases and vaccinations
- Applies feature engineering to create model-ready time-series features

Countries are retained only when they have enough date coverage and non-null signal across cases, deaths, and vaccinations.

## 2) Core Feature Engineering

Important engineered features include:

- `ROLLING_7DAY_CASES`, `ROLLING_7DAY_DEATHS`
- `CFR_PCT` (case fatality rate)
- `WOW_GROWTH_PCT` (week-over-week growth)
- `DOUBLING_TIME_DAYS`
- `IS_WAVE_PERIOD`, `CASES_14D_AGO`, `IS_LOCAL_PEAK`
- `CASES_PER_100K`, `DEATHS_PER_100K`, `RISK_SCORE`
- Vaccination features: `NEW_VACCINATIONS`, `VAX_COVERAGE_14D_LAG`
- Calendar signals: `MONTH_NUM`, `DAY_OF_WEEK`, `WEEK_OF_YEAR`

## 3) ML Notebook (`ML.ipynb`)

`ML.ipynb` trains Snowflake time-series models per country for 3 targets:

- `ROLLING_7DAY_CASES`
- `ROLLING_7DAY_DEATHS`
- `NEW_VACCINATIONS`

The notebook uses `SNOWFLAKE.ML.FORECAST`, with one series per `COUNTRY_REGION`, then evaluates model quality through Snowflake evaluation metrics.

We track SMAPE for forecast quality because unlike MAPE, SMAPE is robust when true values are near zero, avoiding divide-by-zero instability.

## 4) Final Analytical and Forecast Tables

The pipeline produces and serves these key outputs:

1. `COVID_DEATH_FEATURES` (death/case feature table)
2. `COVID_VACCINES_FEATURES`
3. `COUNTRY_RISK_TIERS` (risk tier classification)
4. `FORECAST_ROLLING_7DAY_CASES` (7-day cases forecast)
5. `FORECAST_ROLLING_7DAY_DEATHS` (7-day deaths forecast)
6. `COVID_VACCINATIONS_FORECAST_RESULTS` (30-day new vaccinations forecast with lower/upper bounds)

## 5) Cortex Analyst + Dashboard

A semantic view is attached for Cortex Analyst (`HACKATHON.SG01.FIRST`), and the Streamlit app serves:

- Interactive country-level dashboards (overview, forecasts, reports)
- A Cortex Analyst chatbot that acts as a support agent for analytical Q&A

## Run the App

```bash
streamlit run streamlit_app.py
```
