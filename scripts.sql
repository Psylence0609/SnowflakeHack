Create  DATABASE IF not exists HACKATHON;
CREATE SCHEMA IF not exists hackathon.sg01;

CREATE OR REPLACE VIEW hackathon.sg01.top_countries AS
WITH jhu_coverage AS (
    SELECT
        COUNTRY_REGION,
        ISO3166_1,
        COUNT(DISTINCT CASE WHEN CASE_TYPE = 'Confirmed' THEN DATE END) AS confirmed_days,
        COUNT(DISTINCT CASE WHEN CASE_TYPE = 'Deaths'    THEN DATE END) AS deaths_days,
        MIN(DATE)                                                        AS jhu_start,
        MAX(DATE)                                                        AS jhu_end,
        DATEDIFF('day', MIN(DATE), MAX(DATE))                           AS jhu_span_days,
        SUM(CASE WHEN CASE_TYPE = 'Confirmed'
                  AND DIFFERENCE < 0 THEN 1 ELSE 0 END)                AS negative_corrections
    FROM COVID19_EPIDEMIOLOGICAL_DATA.PUBLIC.JHU_COVID_19
    WHERE PROVINCE_STATE IS NULL
      AND DATE BETWEEN '2020-01-22' AND '2022-12-31'
    GROUP BY COUNTRY_REGION, ISO3166_1
    HAVING confirmed_days >= 730
       AND deaths_days    >= 730
       AND jhu_span_days  >= 730
),

vax_coverage AS (
    SELECT
        COUNTRY_REGION,
        ISO3166_1,
        COUNT(DISTINCT DATE)                                             AS vax_days,
        SUM(CASE WHEN PEOPLE_VACCINATED IS NOT NULL THEN 1 ELSE 0 END)  AS days_with_people_vax,
        SUM(CASE WHEN DAILY_VACCINATIONS IS NOT NULL THEN 1 ELSE 0 END) AS days_with_daily_vax,
        MIN(DATE)                                                        AS vax_start,
        MAX(DATE)                                                        AS vax_end,
        MAX(PEOPLE_VACCINATED_PER_HUNDRED)                               AS max_vax_pct
    FROM COVID19_EPIDEMIOLOGICAL_DATA.PUBLIC.OWID_VACCINATIONS
    WHERE DATE BETWEEN '2020-12-01' AND '2022-12-31'
    GROUP BY COUNTRY_REGION, ISO3166_1
    HAVING vax_days             >= 300
       AND days_with_daily_vax  >= 200
),

-- Countries that qualify in BOTH tables, ranked by coverage
qualified_countries AS (
    SELECT
        j.COUNTRY_REGION,
        (j.confirmed_days + j.deaths_days + v.vax_days) AS total_coverage_score,
        RANK() OVER (ORDER BY (j.confirmed_days + j.deaths_days + v.vax_days) DESC) AS quality_rank
    FROM jhu_coverage j
    INNER JOIN vax_coverage v ON j.COUNTRY_REGION = v.COUNTRY_REGION
)

-- Lock in your top 25 (or swap for the explicit list below)

SELECT COUNTRY_REGION, total_coverage_score
FROM qualified_countries
ORDER BY total_coverage_score DESC
LIMIT 25;






CREATE OR REPLACE TABLE HACKATHON.sg01.covid_deaths AS
-- Confirmed cases — cumulative, country-level only
WITH confirmed AS (
    SELECT
        DATE,
        COUNTRY_REGION,
        SUM(CASES) AS total_cases
    FROM COVID19_EPIDEMIOLOGICAL_DATA.PUBLIC.JHU_COVID_19
    WHERE CASE_TYPE = 'Confirmed'
      AND PROVINCE_STATE IS NULL
      AND COUNTRY_REGION IN (SELECT COUNTRY_REGION FROM HACKATHON.sg01.top_countries ORDER BY TOTAL_COVERAGE_SCORE DESC LIMIT 20)
    GROUP BY COUNTRY_REGION, DATE
    ORDER BY COUNTRY_REGION, DATE
),

-- Deaths — cumulative, country-level only
deaths AS (
    SELECT
        DATE,
        COUNTRY_REGION,
        SUM(CASES) AS total_deaths
    FROM COVID19_EPIDEMIOLOGICAL_DATA.PUBLIC.JHU_COVID_19
    WHERE CASE_TYPE = 'Deaths'
      AND PROVINCE_STATE IS NULL
      AND COUNTRY_REGION IN (SELECT COUNTRY_REGION FROM HACKATHON.sg01.top_countries ORDER BY TOTAL_COVERAGE_SCORE DESC LIMIT 20)
    GROUP BY COUNTRY_REGION, DATE
    ORDER BY COUNTRY_REGION, DATE
)

-- Join all three sources and compute daily deltas
SELECT * FROM(
    SELECT
        c.DATE,
        c.COUNTRY_REGION,
        c.total_cases,
        d.total_deaths,
        
        -- Daily new cases from cumulative (LAG delta)
        c.total_cases  - LAG(c.total_cases)  OVER (
            PARTITION BY c.COUNTRY_REGION ORDER BY c.DATE
        ) AS new_cases,
        -- Daily new deaths from cumulative (LAG delta)
        d.total_deaths - LAG(d.total_deaths) OVER (
            PARTITION BY c.COUNTRY_REGION ORDER BY c.DATE
        ) AS new_deaths
    FROM confirmed c
    LEFT JOIN deaths   d ON c.DATE = d.DATE AND c.COUNTRY_REGION = d.COUNTRY_REGION
    
    WHERE c.DATE >= '2020-01-22'
)
WHERE new_cases  >= 0
  AND new_deaths >= 0
ORDER BY COUNTRY_REGION, DATE;


-- Vaccinations — 
CREATE OR REPLACE TABLE hackathon.sg01.covid_vaccines AS (
    SELECT
        DATE,
        COUNTRY_REGION,
        PEOPLE_VACCINATED,
        PEOPLE_FULLY_VACCINATED,
        DAILY_VACCINATIONS
    FROM COVID19_EPIDEMIOLOGICAL_DATA.PUBLIC.OWID_VACCINATIONS
    WHERE COUNTRY_REGION IN (SELECT COUNTRY_REGION FROM hackathon.sg01.top_countries ORDER BY total_coverage_score DESC LIMIT 20)
    ORDER BY COUNTRY_REGION, DATE
);

CREATE TABLE HACKATHON.sg01.POPULATION (COUNTRY VARCHAR, POPULATION_YEAR INT, POPULATION_TOTAL INT);

INSERT INTO hackathon.sg01.POPULATION (COUNTRY, POPULATION_YEAR, POPULATION_TOTAL) VALUES
  ('Singapore', 2024, 6036860),
  ('Switzerland', 2024, 9005582),
  ('Finland', 2024, 5619911),
  ('Israel', 2024, 9731300),
  ('Philippines', 2024, 115843670),
  ('Greece', 2024, 10424706),
  ('Ireland', 2024, 5395790),
  ('Argentina', 2024, 45696159),
  ('Luxembourg', 2024, 681532),
  ('Poland', 2024, 37957295),
  ('Bahrain', 2024, 1509789),
  ('Croatia', 2024, 3867925),
  ('Romania', 2024, 18940334),
  ('Lithuania', 2024, 2823087),
  ('Austria', 2024, 9109123),
  ('Egypt', 2024, 112716598),
  ('Bulgaria', 2024, 6261473),
  ('Costa Rica', 2024, 5234198),
  ('Estonia', 2024, 1331475),
  ('Qatar', 2024, 2850501),
  ('Czechia', 2024, 10639950),
  ('Hungary', 2024, 9597085),
  ('Portugal', 2024, 10351274),
  ('Indonesia', 2024, 281603220),
  ('Belarus', 2024, 9259751);

  CREATE OR REPLACE TABLE hackathon.sg01.covid_death_features AS
SELECT
  DATE,
  COUNTRY_REGION,
  TOTAL_CASES,
  TOTAL_DEATHS,
  
  NEW_CASES,
  NEW_DEATHS,

  -- 1. 7-day rolling average of new cases HACKATHON.SG01.COVID_FEATURES(smooths weekend dips)
  ROUND(AVG(NEW_CASES) OVER (
    PARTITION BY COUNTRY_REGION
    ORDER BY DATE
    ROWS BETWEEN 6 PRECEDING AND CURRENT ROW
  ), 0) AS ROLLING_7DAY_CASES,

  -- 2. 7-day rolling average of new deaths
  ROUND(AVG(NEW_DEATHS) OVER (
    PARTITION BY COUNTRY_REGION
    ORDER BY DATE
    ROWS BETWEEN 6 PRECEDING AND CURRENT ROW
  ), 0) AS ROLLING_7DAY_DEATHS,

  -- 3. Case Fatality Rate %
  ROUND(DIV0(TOTAL_DEATHS, TOTAL_CASES) * 100, 3) AS CFR_PCT,

  -- 4. Week-over-week growth rate %
  ROUND(
    DIV0(
      NEW_CASES - LAG(NEW_CASES, 7) OVER (PARTITION BY COUNTRY_REGION ORDER BY DATE),
      LAG(NEW_CASES, 7) OVER (PARTITION BY COUNTRY_REGION ORDER BY DATE)
    ) * 100
  , 1) AS WOW_GROWTH_PCT,

  -- 5. Doubling time in days (Rule of 70)
  CASE
    WHEN DIV0(
           NEW_CASES - LAG(NEW_CASES, 7) OVER (PARTITION BY COUNTRY_REGION ORDER BY DATE),
           LAG(NEW_CASES, 7) OVER (PARTITION BY COUNTRY_REGION ORDER BY DATE)
         ) * 100 > 0
    THEN ROUND(
           70 / (DIV0(
                   NEW_CASES - LAG(NEW_CASES, 7) OVER (PARTITION BY COUNTRY_REGION ORDER BY DATE),
                   LAG(NEW_CASES, 7) OVER (PARTITION BY COUNTRY_REGION ORDER BY DATE)
                 ) * 100)
         , 1)
    ELSE NULL
  END AS DOUBLING_TIME_DAYS,

  -- 6. OUTBREAK WAVE DETECTOR
-- Marks the start of a new wave: rolling avg crosses above its 28-day avg
    CASE
      WHEN AVG(NEW_CASES) OVER (PARTITION BY COUNTRY_REGION ORDER BY DATE ROWS BETWEEN 6 PRECEDING AND CURRENT ROW)
         > AVG(NEW_CASES) OVER (PARTITION BY COUNTRY_REGION ORDER BY DATE ROWS BETWEEN 89 PRECEDING AND CURRENT ROW)
      THEN 1 ELSE 0
    END AS IS_WAVE_PERIOD,

    -- 7. DEATH LAG CORRELATION FEATURE
-- Deaths typically lag cases by ~14 days — this captures that signal
LAG(NEW_CASES, 14) OVER (PARTITION BY COUNTRY_REGION ORDER BY DATE) AS CASES_14D_AGO,

-- 8. PEAK FLAG — was today a local maximum? (great for annotations on charts)
CASE
  WHEN NEW_CASES >= MAX(NEW_CASES) OVER (
    PARTITION BY COUNTRY_REGION
    ORDER BY DATE
    ROWS BETWEEN 30 PRECEDING AND 30 FOLLOWING
  ) THEN 1 ELSE 0
END AS IS_LOCAL_PEAK,

--9
ROUND(DIV0(TOTAL_DEATHS, population_total) * 100000, 2) AS DEATHS_PER_100K,

--10
ROUND(DIV0(TOTAL_CASES, population_total) * 100000, 2) AS CASES_PER_100K,

--11
ROUND(
  (COALESCE(WOW_GROWTH_PCT, 0) * 0.5) +
  (CFR_PCT * 10) +
  (IS_WAVE_PERIOD * 20)
, 1) AS RISK_SCORE,

  -- 12. Calendar features for ML seasonality
  MONTH(DATE)      AS MONTH_NUM,
  DAYOFWEEK(DATE)  AS DAY_OF_WEEK,
  WEEKOFYEAR(DATE) AS WEEK_OF_YEAR

  

FROM hackathon.sg01.covid_deaths
LEFT JOIN (select * from hackathon.sg01.population where
country in (SELECT COUNTRY_REGION FROM hackathon.sg01.top_countries order by total_coverage_score DESC LIMIT 20)
) ON COUNTRY_REGION = country
ORDER BY COUNTRY_REGION, DATE;


CREATE OR REPLACE TABLE hackathon.sg01.covid_vaccines_features AS
SELECT 
    DATE,
    COUNTRY_REGION,
    PEOPLE_VACCINATED AS TOTAL_VACCINATED,
    PEOPLE_FULLY_VACCINATED AS TOTAL_FULLY_VACCINATED,
    DAILY_VACCINATIONS AS NEW_VACCINATIONS,

    -- 6. Vaccination lag (immune response takes ~14 days)
    LAG(TOTAL_VACCINATED, 14) OVER (
    PARTITION BY COUNTRY_REGION ORDER BY DATE
    ) AS VAX_COVERAGE_14D_LAG,

    MONTH(DATE)      AS MONTH_NUM,
    DAYOFWEEK(DATE)  AS DAY_OF_WEEK,
    WEEKOFYEAR(DATE) AS WEEK_OF_YEAR

FROM hackathon.sg01.covid_vaccines
ORDER BY COUNTRY_REGION, DATE;
