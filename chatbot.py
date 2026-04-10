import json
import streamlit as st
import pandas as pd
from snowflake.snowpark.context import get_active_session

try:
    import _snowflake  # type: ignore
except Exception:
    _snowflake = None

API_ENDPOINT = "/api/v2/cortex/analyst/message"
SEMANTIC_VIEW = "HACKATHON.SG01.FIRST"
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
                  <div class="sub">Ask me about this country and active dashboard tab.</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

        for message in messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])
                if "df" in message:
                    st.dataframe(pd.DataFrame(message["df"]), use_container_width=True)
                    

    question = st.chat_input("Ask a question...", key="chat_text_input")

    if question and question.strip():
        question = question.strip()

        _append_message("user", question)
        with msg_pane:
            with st.chat_message("user"):
                st.markdown(question)

            with st.chat_message("assistant"):
                with st.spinner("Thinking with Cortex Analyst..."):
                    answer, df_result = _generate_answer(
                        question=question, country=country, active_tab=active_tab
                    )
                st.markdown(answer)
                if df_result is not None and not df_result.empty:   # ← this must be present
                    st.dataframe(df_result, use_container_width=True)

        _append_message("assistant", answer)
        if df_result is not None and not df_result.empty:
            st.session_state.chat_messages[-1]["df"] = df_result.to_dict()
        _update_memory(question=question, answer=answer, country=country, active_tab=active_tab)
        st.rerun()


def _append_message(role: str, content: str) -> None:
    if "chat_messages" not in st.session_state:
        st.session_state.chat_messages = []

    st.session_state.chat_messages.append({"role": role, "content": content})
    if len(st.session_state.chat_messages) > MAX_HISTORY:
        st.session_state.chat_messages = st.session_state.chat_messages[-MAX_HISTORY:]


def _generate_answer(question: str, country: str, active_tab: str) -> str:
    messages = _build_analyst_messages(question=question, country=country, active_tab=active_tab)
    parsed, err = _get_analyst_response(messages)
    if err:
        return err, None

    if parsed is None:
        return "Cortex Analyst returned no content.", None

    # Walk the content blocks directly
    message = parsed.get("message", {})
    content = message.get("content", []) if isinstance(message, dict) else []

    output_text = []
    sql_to_run = None
    df = None
    stmt = None

    for block in content:
        if not isinstance(block, dict):
            continue
        btype = str(block.get("type", "")).lower()
    
        if btype == "text":
            txt = block.get("text", "").strip()
            if txt:
                output_text.append(txt)
    
        elif btype == "sql":
            stmt = block.get("statement", "").strip()
            if stmt:                                        # ← INSIDE elif, not outside
                output_text.append(f"**SQL used:**\n```sql\n{stmt}\n```")
                try:
                    from snowflake.snowpark.context import get_active_session
                    session = get_active_session()
                    df = session.sql(stmt).to_pandas()
                    # output_text.append(str(df.shape))
                except Exception as e:
                    output_text.append(f"⚠️ Could not execute query: {e}")
                    df = None
    
        elif btype == "suggestions":
            suggestions = block.get("suggestions", [])
            if suggestions:
                output_text.append("Did you mean:\n- " + "\n- ".join(suggestions))
    
    # ← outside the loop entirely
    result = "\n\n".join(output_text)
    return result, df


def _build_analyst_messages(question: str, country: str, active_tab: str) -> list[dict]:
    recent = st.session_state.get("chat_messages", [])[-12:]

    normalized: list[dict] = []
    for msg in recent:
        role = msg.get("role", "user")
        if role not in ("user", "assistant"):
            role = "user"

        text = str(msg.get("content", "")).strip()
        if not text:
            continue

        # Analyst API requires strict role alternation; merge consecutive same-role turns.
        if normalized and normalized[-1]["role"] == role:
            prev_text = normalized[-1]["content"][0]["text"]
            normalized[-1]["content"][0]["text"] = f"{prev_text}\n\n{text}"
        else:
            normalized.append(
                {
                    "role": role,
                    "content": [{"type": "text", "text": text}],
                }
            )

    if not normalized:
        normalized = [{"role": "user", "content": [{"type": "text", "text": question}]}]

    if normalized[0]["role"] == "assistant":
        normalized = normalized[1:]

    if not normalized:
        normalized = [{"role": "user", "content": [{"type": "text", "text": question}]}]

    # Add lightweight dashboard context to the latest user turn.
    context_prefix = (
        f"[Context] selected_country={country}; active_tab={active_tab}. "
        "Use this only if relevant.\n\n"
    )
    if normalized[-1]["role"] == "user":
        normalized[-1]["content"][0]["text"] = context_prefix + normalized[-1]["content"][0]["text"]
    else:
        normalized.append(
            {
                "role": "user",
                "content": [{"type": "text", "text": context_prefix + question}],
            }
        )

    return normalized


def _get_analyst_response(messages: list[dict]) -> tuple[dict | None, str | None]:
    if _snowflake is None:
        return None, "Snowflake runtime client '_snowflake' is unavailable in this environment."

    request_body = {
        "messages": messages,
        "semantic_view": SEMANTIC_VIEW,
    }

    try:
        resp = _snowflake.send_snow_api_request(
            "POST",
            API_ENDPOINT,
            {},
            {},
            request_body,
            None,
            50000,
        )
    except Exception as exc:
        return None, f"Cortex Analyst API call failed: {exc}"

    raw_content = resp.get("content")
    if raw_content is None:
        raw_content = ""
    elif not isinstance(raw_content, str):
        raw_content = str(raw_content)

    try:
        parsed = json.loads(raw_content or "{}")
    except Exception:
        parsed = {"message": raw_content}

    if int(resp.get("status", 500)) < 400:
        return parsed, None

    message = parsed.get("message", "Unknown Analyst API error")
    return parsed, f"Error {resp.get('status')}: {message}"


def _extract_analyst_text(raw_response) -> str | None:
    if raw_response is None:
        return None

    parsed = raw_response
    if isinstance(raw_response, str):
        try:
            parsed = json.loads(raw_response)
        except Exception:
            return raw_response.strip() or None

    if isinstance(parsed, dict):
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

        for key in ("answer", "text", "content", "response"):
            if key in parsed and parsed[key]:
                value = parsed[key]
                if isinstance(value, list):
                    return "\n".join(str(v) for v in value)
                return str(value)

    return str(parsed)


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