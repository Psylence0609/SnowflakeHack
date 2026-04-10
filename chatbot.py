import json
import streamlit as st

from data import (
    get_session,
    load_cases_forecast,
    load_death_features,
    load_deaths_forecast,
    load_risk_tiers,
    load_vax_forecast,
    load_vaccine_features,
)

SEARCH_SERVICE_NAME = "HACKATHON.SG01.COVID_SEARCH_SVC"
SEMANTIC_MODEL_PATH = "@HACKATHON.SG01.SEMANTIC_STAGE/semantic.yaml"
MAX_HISTORY = 24


def render(country: str, active_tab: str) -> None:
    st.markdown(
        """
        <style>
        .chat-greeting {
            margin: 48px auto 18px auto;
            text-align: center;
            padding: 18px 12px;
            max-width: 280px;
            color: #1f2d2d;
        }

        .chat-greeting .emoji {
            font-size: 34px;
            line-height: 1;
            margin-bottom: 8px;
        }

        .chat-greeting .title {
            font-size: 17px;
            font-weight: 800;
            color: #1a1a1a;
            margin-bottom: 6px;
        }

        .chat-greeting .sub {
            font-size: 12px;
            color: #6f7b7b;
            line-height: 1.45;
        }

        .chat-header-title {
            font-size: 16px;
            font-weight: 800;
            color: #1a1a1a;
            line-height: 1.2;
            margin: 0;
        }

        .chat-header-sub {
            font-size: 11px;
            color: #7a7a7a;
            text-transform: uppercase;
            letter-spacing: 0.08em;
            margin-top: 4px;
        }

        .chat-inline-close {
            display: flex;
            justify-content: flex-end;
        }

        .chat-inline-close button {
            background: #f5fbfb !important;
            color: #01696f !important;
            border: 1px solid #bfe3e4 !important;
            border-radius: 8px !important;
            font-weight: 700 !important;
            min-height: 34px !important;
            min-width: 34px !important;
            width: 34px !important;
            padding: 0 !important;
            font-size: 18px !important;
        }

        .chat-inline-close button:hover {
            background: #01696f !important;
            color: #ffffff !important;
        }

        .chat-input-block {
            background: #ffffff;
            padding-top: 10px;
            margin-top: 10px;
            border-top: 1px solid rgba(0,0,0,0.06);
        }

        div[data-testid="stChatInput"] {
            background: #ffffff !important;
        }

        div[data-testid="stChatInput"] > div {
            background: #ffffff !important;
            border: 1px solid #d6e2e2 !important;
        }

        div[data-testid="stChatInput"] input,
        div[data-testid="stChatInput"] textarea {
            background: #ffffff !important;
            color: #4a4a4a !important;
        }

        div[data-testid="stChatInput"] input::placeholder,
        div[data-testid="stChatInput"] textarea::placeholder {
            color: #7a7a7a !important;
        }

        div[data-testid="stChatInput"] button {
            background: #ffffff !important;
            color: #4a4a4a !important;
            border: 1px solid #d6e2e2 !important;
        }

        [data-testid="stChatMessageContent"] p,
        [data-testid="stChatMessageContent"] li,
        [data-testid="stChatMessageContent"] span {
            color: #4a4a4a !important;
        }

        div[data-testid="stForm"] {
            background: #ffffff;
            padding-top: 10px;
            margin-top: 10px;
            border-top: 1px solid rgba(0,0,0,0.06);
        }

        div[data-testid="stForm"] button {
            border-radius: 999px !important;
            min-height: 38px !important;
            font-size: 18px !important;
            padding: 0 14px !important;
        }

        div[data-testid="stTextInput"] input {
            border-radius: 999px !important;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

    header_left, header_right = st.columns([3.6, 1.2], vertical_alignment="top")
    with header_left:
        st.markdown('<p class="chat-header-title">Cortex Chatbot</p>', unsafe_allow_html=True)
        st.markdown(
            f'<div class="chat-header-sub">{country} • {active_tab}</div>',
            unsafe_allow_html=True,
        )

    with header_right:
        st.markdown('<div class="chat-inline-close">', unsafe_allow_html=True)
        if st.button("✕", key="close_chat_panel_inline"):
            st.session_state.chat_panel_open = False
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

    if st.button("Clear chat", key="clear_chat_history"):
        st.session_state.chat_messages = []
        st.session_state.chatbot_memory = {}
        st.rerun()

    msg_pane = st.container(height=650, border=False)

    with msg_pane:
        messages = st.session_state.get("chat_messages", [])
        if not messages:
            st.markdown(
                """
                <div class="chat-greeting">
                  <div class="emoji">👋</div>
                  <div class="title">Hello, I am your Cortex Analyst</div>
                  <div class="sub">Ask me about this country, the current tab, trends, risk, forecasts, and feature insights.</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

        for message in messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

    question = st.chat_input("Ask about trends, risks, or forecasts...", key="chat_text_input")

    if question and question.strip():
        question = question.strip()

        _append_message("user", question)
        with msg_pane:
            with st.chat_message("user"):
                st.markdown(question)

            with st.chat_message("assistant"):
                with st.spinner("Thinking with Cortex..."):
                    answer = _generate_answer(question=question, country=country, active_tab=active_tab)
                st.markdown(answer)

        _append_message("assistant", answer)
        _update_memory(question=question, answer=answer, country=country, active_tab=active_tab)
        st.rerun()


def _append_message(role: str, content: str) -> None:
    if "chat_messages" not in st.session_state:
        st.session_state.chat_messages = []

    st.session_state.chat_messages.append({"role": role, "content": content})
    if len(st.session_state.chat_messages) > MAX_HISTORY:
        st.session_state.chat_messages = st.session_state.chat_messages[-MAX_HISTORY:]


def _generate_answer(question: str, country: str, active_tab: str) -> str:
    metrics_context = _build_metrics_context(country)
    tab_context = _build_tab_context(country, active_tab)
    tab_guide = _tab_guide()
    memory_context = _memory_context(country, active_tab)
    search_context = _search_context(question)

    analyst_answer = _ask_cortex_analyst(
        question=question,
        country=country,
        active_tab=active_tab,
        tab_guide=tab_guide,
        tab_context=tab_context,
        search_context=search_context,
        memory_context=memory_context,
    )
    if analyst_answer:
        return analyst_answer

    direct_answer = _direct_risk_comparison_answer(question)
    if direct_answer:
        return direct_answer

    prompt = f"""
You are a COVID-19 analytics assistant for a Snowflake Streamlit dashboard.

Use this semantic model as the source of business meaning: {SEMANTIC_MODEL_PATH}
Current country: {country}
Current active dashboard tab: {active_tab}

What each dashboard tab shows:
{tab_guide}

Country metrics context:
{metrics_context}

Tab-specific context for the currently viewed tab ({active_tab}):
{tab_context}

Conversation memory context:
{memory_context}

Retrieved context from cortex search service {SEARCH_SERVICE_NAME}:
{search_context}

Instructions:
- Answer with concise, actionable insights.
- Prefer exact values from context when available.
- Tie insights to what the user is currently viewing in the active tab.
- Mention if the answer is from memory/context versus fresh evidence.
- If evidence is weak or missing, say so clearly.
- Keep response under 8 bullet points.

User question:
{question}
"""

    return _complete_with_cortex(prompt)


def _ask_cortex_analyst(
    question: str,
    country: str,
    active_tab: str,
    tab_guide: str,
    tab_context: str,
    search_context: str,
    memory_context: str,
) -> str | None:
    session = get_session()

    grounded_question = (
        f"{question}\n\n"
        f"Dashboard context: country={country}, active_tab={active_tab}.\n"
        f"Tab guide: {tab_guide}\n"
        f"Active tab context: {tab_context}\n"
        f"Search service context ({SEARCH_SERVICE_NAME}): {search_context}\n"
        f"Conversation memory: {memory_context}\n"
        "If the user asks for cross-country comparison, use all countries and include both values and country names."
    )

    req = {
        "messages": [
            {
                "role": "user",
                "content": [{"type": "text", "text": grounded_question}],
            }
        ],
        "semantic_model_file": SEMANTIC_MODEL_PATH,
    }

    req_json = _sql_escape(json.dumps(req))

    variants = [
        f"""
        SELECT SNOWFLAKE.CORTEX.ANALYST(
            PARSE_JSON('{req_json}')
        ) AS RESPONSE
        """,
        f"""
        SELECT SNOWFLAKE.CORTEX.ANALYST(
            '{SEMANTIC_MODEL_PATH}',
            '{_sql_escape(grounded_question)}'
        ) AS RESPONSE
        """,
    ]

    for sql in variants:
        try:
            df = session.sql(sql).to_pandas()
            if df.empty:
                continue

            parsed = _extract_analyst_text(df.iloc[0]["RESPONSE"])
            if parsed:
                return parsed
        except Exception:
            continue

    return None


def _extract_analyst_text(raw_response) -> str | None:
    if raw_response is None:
        return None

    if isinstance(raw_response, str):
        try:
            parsed = json.loads(raw_response)
        except Exception:
            return raw_response.strip() or None
    else:
        parsed = raw_response

    if isinstance(parsed, dict):
        # Common Analyst response shape.
        message = parsed.get("message")
        if isinstance(message, dict):
            content = message.get("content")
            if isinstance(content, list):
                text_blocks = []
                sql_blocks = []
                for block in content:
                    if not isinstance(block, dict):
                        continue
                    btype = str(block.get("type", "")).lower()
                    if btype == "text" and block.get("text"):
                        text_blocks.append(str(block["text"]))
                    if btype in ("sql", "statement"):
                        stmt = block.get("statement") or block.get("sql")
                        if stmt:
                            sql_blocks.append(str(stmt))
                if text_blocks and sql_blocks:
                    return "\n\n".join(text_blocks) + "\n\nSQL used:\n```sql\n" + "\n\n".join(sql_blocks) + "\n```"
                if text_blocks:
                    return "\n\n".join(text_blocks)

        # Alternate shape fallbacks.
        for key in ("answer", "text", "content", "response"):
            if key in parsed and parsed[key]:
                value = parsed[key]
                if isinstance(value, list):
                    return "\n".join(str(v) for v in value)
                return str(value)

    return str(parsed)


def _direct_risk_comparison_answer(question: str) -> str | None:
    text = (question or "").lower()
    comparison_markers = [
        "most risk",
        "least risk",
        "highest risk",
        "lowest risk",
        "compare",
        "riskiest",
        "safest",
    ]

    if not any(marker in text for marker in comparison_markers):
        return None

    try:
        risk_df = load_risk_tiers()
        if risk_df.empty:
            return None

        sorted_df = risk_df.sort_values("AVG_RISK_SCORE", ascending=False).reset_index(drop=True)
        high = sorted_df.iloc[0]
        low = sorted_df.iloc[-1]
        gap = _safe_float(high.get("AVG_RISK_SCORE"), 2) - _safe_float(low.get("AVG_RISK_SCORE"), 2)

        return (
            "Based on `HACKATHON.SG01.COUNTRY_RISK_TIERS`:\n"
            f"- Highest risk country: **{high['COUNTRY_REGION']}** (avg risk score: {_safe_float(high.get('AVG_RISK_SCORE'), 2)}, "
            f"tier: {high.get('RISK_TIER', 'N/A')}, trend: {high.get('FORECAST_TREND', 'N/A')})\n"
            f"- Lowest risk country: **{low['COUNTRY_REGION']}** (avg risk score: {_safe_float(low.get('AVG_RISK_SCORE'), 2)}, "
            f"tier: {low.get('RISK_TIER', 'N/A')}, trend: {low.get('FORECAST_TREND', 'N/A')})\n"
            f"- Risk score gap: **{gap:.2f}**"
        )
    except Exception:
        return None


def _build_metrics_context(country: str) -> str:
    try:
        death_df = load_death_features(country)
        vax_df = load_vaccine_features(country)
        risk_df = load_risk_tiers()

        if death_df.empty:
            return "No death/case rows found for this country."

        latest = death_df.iloc[-1]
        pieces = [
            f"Date: {latest['DATE'].date()}",
            f"Total cases: {_safe_int(latest.get('TOTAL_CASES'))}",
            f"Total deaths: {_safe_int(latest.get('TOTAL_DEATHS'))}",
            f"New cases: {_safe_int(latest.get('NEW_CASES'))}",
            f"New deaths: {_safe_int(latest.get('NEW_DEATHS'))}",
            f"CFR %: {_safe_float(latest.get('CFR_PCT'))}",
            f"WoW growth %: {_safe_float(latest.get('WOW_GROWTH_PCT'))}",
            f"Risk score: {_safe_float(latest.get('RISK_SCORE'))}",
        ]

        if not vax_df.empty:
            v_latest = vax_df.iloc[-1]
            pieces.extend(
                [
                    f"Total vaccinated: {_safe_int(v_latest.get('TOTAL_VACCINATED'))}",
                    f"Fully vaccinated: {_safe_int(v_latest.get('TOTAL_FULLY_VACCINATED'))}",
                    f"New vaccinations: {_safe_int(v_latest.get('NEW_VACCINATIONS'))}",
                ]
            )

        risk_row = risk_df[risk_df["COUNTRY_REGION"] == country]
        if not risk_row.empty:
            rr = risk_row.iloc[0]
            pieces.extend(
                [
                    f"Risk tier: {rr['RISK_TIER']}",
                    f"Forecast trend: {rr['FORECAST_TREND']}",
                    f"Avg risk score: {_safe_float(rr.get('AVG_RISK_SCORE'))}",
                ]
            )

        return "\n".join(pieces)
    except Exception as exc:
        return f"Unable to build metric context: {exc}"


def _build_tab_context(country: str, active_tab: str) -> str:
    try:
        tab_name = (active_tab or "").strip().lower()

        if tab_name == "overview":
            death_df = load_death_features(country)
            vax_df = load_vaccine_features(country)
            risk_df = load_risk_tiers()

            if death_df.empty:
                return "Overview tab: no data available for selected country."

            latest = death_df.iloc[-1]
            spark = death_df.tail(30)
            spark_start = spark.iloc[0] if not spark.empty else latest
            spark_delta = _safe_float(latest.get("ROLLING_7DAY_CASES"), 2) - _safe_float(
                spark_start.get("ROLLING_7DAY_CASES"), 2
            )

            risk_row = risk_df[risk_df["COUNTRY_REGION"] == country]
            tier = risk_row["RISK_TIER"].values[0] if not risk_row.empty else "N/A"
            trend = risk_row["FORECAST_TREND"].values[0] if not risk_row.empty else "N/A"

            vax_line = "Vaccination metrics unavailable."
            if not vax_df.empty:
                v_latest = vax_df.iloc[-1]
                vax_line = (
                    f"Total vaccinated {_safe_int(v_latest.get('TOTAL_VACCINATED'))}, "
                    f"fully vaccinated {_safe_int(v_latest.get('TOTAL_FULLY_VACCINATED'))}, "
                    f"daily vaccinations {_safe_int(v_latest.get('NEW_VACCINATIONS'))}."
                )

            return (
                "Overview tab shows KPI cards, risk banner, a 30-day rolling-cases sparkline, and a "
                "composite risk score bar.\n"
                f"Latest KPI snapshot: total cases {_safe_int(latest.get('TOTAL_CASES'))}, total deaths {_safe_int(latest.get('TOTAL_DEATHS'))}, "
                f"CFR {_safe_float(latest.get('CFR_PCT'))}%, WoW growth {_safe_float(latest.get('WOW_GROWTH_PCT'))}%.\n"
                f"Risk banner: tier {tier}, forecast trend {trend}.\n"
                f"30-day rolling average delta: {spark_delta:.2f}.\n"
                f"{vax_line}"
            )

        if tab_name == "forecasts":
            cases_fc = load_cases_forecast(country)
            deaths_fc = load_deaths_forecast(country)
            vax_fc = load_vax_forecast(country)

            lines = [
                "Forecasts tab shows 3 time-series charts with historical lines + forecast lines + 90% confidence intervals.",
                "It includes date-range filtering and a forecast-start divider annotation.",
            ]

            if not cases_fc.empty:
                c0 = cases_fc.iloc[0]
                c1 = cases_fc.iloc[-1]
                lines.append(
                    f"Cases forecast from {c0['DATE'].date()} to {c1['DATE'].date()}: {_safe_float(c0.get('FORECAST'))} -> {_safe_float(c1.get('FORECAST'))}."
                )
            if not deaths_fc.empty:
                d0 = deaths_fc.iloc[0]
                d1 = deaths_fc.iloc[-1]
                lines.append(
                    f"Deaths forecast from {d0['DATE'].date()} to {d1['DATE'].date()}: {_safe_float(d0.get('FORECAST'))} -> {_safe_float(d1.get('FORECAST'))}."
                )
            if not vax_fc.empty:
                v0 = vax_fc.iloc[0]
                v1 = vax_fc.iloc[-1]
                lines.append(
                    f"Vaccination forecast from {v0['DATE'].date()} to {v1['DATE'].date()}: {_safe_float(v0.get('FORECAST'))} -> {_safe_float(v1.get('FORECAST'))}."
                )

            return "\n".join(lines)

        if tab_name == "feature reports":
            death_df = load_death_features(country)
            vax_df = load_vaccine_features(country)

            if death_df.empty:
                return "Feature Reports tab: no data available for selected country."

            latest = death_df.iloc[-1]
            wave_count = int((death_df.get("IS_WAVE_PERIOD", 0) == 1).sum()) if "IS_WAVE_PERIOD" in death_df.columns else 0
            peak_count = int((death_df.get("IS_LOCAL_PEAK", 0) == 1).sum()) if "IS_LOCAL_PEAK" in death_df.columns else 0

            return (
                "Feature Reports tab shows engineered features: CFR trend, WoW growth bars, doubling time, "
                "composite risk score trend, wave and local-peak annotations, 14-day lag comparisons, temporal "
                "distribution charts, and vaccination feature breakdown.\n"
                f"Latest feature snapshot: CFR {_safe_float(latest.get('CFR_PCT'))}%, WoW {_safe_float(latest.get('WOW_GROWTH_PCT'))}%, "
                f"doubling time {_safe_float(latest.get('DOUBLING_TIME_DAYS'))} days, risk score {_safe_float(latest.get('RISK_SCORE'))}.\n"
                f"Detected wave points: {wave_count}, local peaks: {peak_count}.\n"
                f"Vaccination feature rows available: {len(vax_df)}."
            )

        return "Unknown tab; provide a general explanation tied to available metrics and search evidence."
    except Exception as exc:
        return f"Unable to build tab context: {exc}"


def _tab_guide() -> str:
    return (
        "Overview: high-level KPI cards (total/new cases/deaths, CFR, WoW growth), risk tier banner and trend, "
        "per-100k stats, vaccination KPI cards, 30-day rolling average sparkline, and composite risk score bar.\n"
        "Forecasts: three forecast charts (cases, deaths, vaccinations) with historical series, forecast series, "
        "confidence intervals, and date-range filtering.\n"
        "Feature Reports: engineered-feature deep dive including CFR trend, WoW bars, doubling time threshold, "
        "risk score trend, wave/peak annotations, lag features, calendar distributions, and vaccination breakdown."
    )


def _memory_context(country: str, active_tab: str) -> str:
    messages = st.session_state.get("chat_messages", [])
    mem = st.session_state.get("chatbot_memory", {})
    recent = messages[-8:]

    recent_lines = []
    for msg in recent:
        role = msg.get("role", "unknown")
        content = str(msg.get("content", "")).strip().replace("\n", " ")
        if len(content) > 220:
            content = content[:220] + "..."
        recent_lines.append(f"{role}: {content}")

    countries_seen = ", ".join(mem.get("countries_seen", [])) or country
    tabs_seen = ", ".join(mem.get("tabs_seen", [])) or active_tab
    topics = ", ".join(mem.get("topics", [])) or "No stable topics yet"
    summary = mem.get("summary", "No prior summary stored yet")

    return (
        f"Memory summary: {summary}\n"
        f"Countries discussed in this session: {countries_seen}\n"
        f"Tabs discussed in this session: {tabs_seen}\n"
        f"Recurring topics: {topics}\n"
        "Recent dialogue snippets:\n"
        + ("\n".join(recent_lines) if recent_lines else "No prior dialogue")
    )


def _update_memory(question: str, answer: str, country: str, active_tab: str) -> None:
    mem = st.session_state.get("chatbot_memory", {})

    countries_seen = set(mem.get("countries_seen", []))
    tabs_seen = set(mem.get("tabs_seen", []))
    topics = set(mem.get("topics", []))

    countries_seen.add(country)
    tabs_seen.add(active_tab)

    text = f"{question} {answer}".lower()
    topic_keywords = {
        "risk": ["risk", "tier", "severity"],
        "forecast": ["forecast", "predict", "projection", "confidence interval"],
        "vaccination": ["vaccine", "vaccination", "dose", "fully vaccinated"],
        "mortality": ["death", "fatality", "cfr"],
        "trend": ["trend", "growth", "decline", "wave", "peak"],
    }

    for topic, words in topic_keywords.items():
        if any(word in text for word in words):
            topics.add(topic)

    short_q = question.strip().replace("\n", " ")
    if len(short_q) > 120:
        short_q = short_q[:120] + "..."

    short_a = answer.strip().replace("\n", " ")
    if len(short_a) > 180:
        short_a = short_a[:180] + "..."

    summary = (
        f"User usually asks about {', '.join(sorted(topics)) if topics else 'general COVID metrics'}; "
        f"latest question: '{short_q}'; latest answer summary: '{short_a}'"
    )

    st.session_state.chatbot_memory = {
        "countries_seen": sorted(countries_seen),
        "tabs_seen": sorted(tabs_seen),
        "topics": sorted(topics),
        "summary": summary,
    }


def _search_context(question: str) -> str:
    session = get_session()
    payload = {
        "query": question,
        "columns": [],
        "limit": 4,
    }

    try:
        payload_str = _sql_escape(json.dumps(payload))
        sql = f"""
        SELECT SNOWFLAKE.CORTEX.SEARCH_PREVIEW(
            '{SEARCH_SERVICE_NAME}',
            PARSE_JSON('{payload_str}')
        ) AS RESULT
        """
        df = session.sql(sql).to_pandas()
        if df.empty:
            return "No search results returned."

        result_obj = df.iloc[0]["RESULT"]
        return _flatten_search_result(result_obj)
    except Exception as exc:
        return f"Search service unavailable or query failed: {exc}"


def _flatten_search_result(result_obj) -> str:
    if result_obj is None:
        return "No search results available."

    if isinstance(result_obj, str):
        try:
            parsed = json.loads(result_obj)
        except Exception:
            return result_obj
    else:
        parsed = result_obj

    candidates = []

    if isinstance(parsed, dict):
        for key in ("results", "chunks", "data"):
            if key in parsed and isinstance(parsed[key], list):
                for item in parsed[key]:
                    if isinstance(item, dict):
                        for text_key in ("text", "chunk", "content", "document_text"):
                            if text_key in item and item[text_key]:
                                candidates.append(str(item[text_key]))
                                break
                    elif item:
                        candidates.append(str(item))

    if not candidates:
        return json.dumps(parsed)[:2000]

    return "\n\n".join(candidates[:4])


def _complete_with_cortex(prompt: str) -> str:
    session = get_session()
    models = ["mistral-large2", "snowflake-arctic", "llama3.1-70b"]

    escaped_prompt = _sql_escape(prompt)

    for model in models:
        try:
            sql = f"""
            SELECT SNOWFLAKE.CORTEX.COMPLETE(
                '{model}',
                '{escaped_prompt}'
            ) AS RESPONSE
            """
            df = session.sql(sql).to_pandas()
            if df.empty:
                continue
            return _extract_response_text(df.iloc[0]["RESPONSE"])
        except Exception:
            continue

    return (
        "I could not get a Cortex response right now. Please verify model privileges and "
        "service availability in schema HACKATHON.SG01."
    )


def _extract_response_text(raw_response) -> str:
    if raw_response is None:
        return "No response returned from Cortex."

    if isinstance(raw_response, str):
        try:
            parsed = json.loads(raw_response)
        except Exception:
            return raw_response
    else:
        parsed = raw_response

    if isinstance(parsed, dict):
        choices = parsed.get("choices")
        if isinstance(choices, list) and choices:
            choice = choices[0]
            if isinstance(choice, dict):
                for key in ("messages", "message", "text", "content"):
                    if key in choice and choice[key]:
                        value = choice[key]
                        if isinstance(value, list):
                            return "\n".join(str(v) for v in value)
                        return str(value)

    return str(parsed)


def _sql_escape(value: str) -> str:
    return value.replace("'", "''")


def _safe_float(value, digits: int = 2) -> float:
    try:
        return round(float(value), digits)
    except Exception:
        return 0.0


def _safe_int(value) -> int:
    try:
        return int(float(value))
    except Exception:
        return 0
