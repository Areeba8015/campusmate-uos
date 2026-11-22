import datetime
import html
import re
import streamlit as st
from eliza_engine import ElizaEngine

st.set_page_config(page_title="CampusMate UoS", page_icon="🎓", layout="centered")


# --- UI HELPER FUNCTIONS ---
def format_markdown_to_html(text: str) -> str:
    """Converts basic markdown bold/italic/code/newlines into safe HTML for chat bubbles."""
    escaped = html.escape(text)
    escaped = re.sub(r"\*\*(.*?)\*\*", r"<strong>\1</strong>", escaped)
    escaped = re.sub(r"\*(.*?)\*", r"<em>\1</em>", escaped)
    escaped = re.sub(
        r"`(.*?)`",
        r"<code style='background:#f1f5f9;padding:1px 5px;border-radius:4px;color:#1e40af;'>\1</code>",
        escaped,
    )
    return escaped.replace("\n", "<br>")
def current_time_str() -> str:
    return datetime.datetime.now().strftime("%I:%M %p").lstrip("0")


# --- CUSTOM CSS ---
st.markdown(
    """
    <style>
    .stApp {
        background-color: #f8fafc;
        font-family: 'Segoe UI', -apple-system, BlinkMacSystemFont, sans-serif;
    }
    header[data-testid="stHeader"] {
        background: transparent;
    }
    .block-container {
        padding-top: 1.5rem;
        padding-bottom: 5rem;
        max-width: 780px;
    }
    .hero-banner {
        background: linear-gradient(135deg, #dce6ff 0%, #e8efff 55%, #d6e2ff 100%);
        border-radius: 18px;
        padding: 26px 32px;
        margin-bottom: 18px;
        display: flex;
        justify-content: space-between;
        align-items: flex-start;
        box-shadow: 0 4px 14px rgba(30, 64, 175, 0.06);
        border: 1px solid #cbd8ff;
    }
    .hero-left h1 {
        margin: 0 0 6px 0;
        font-size: 2rem;
        font-weight: 800;
        color: #1e293b;
        letter-spacing: -0.5px;
    }
    .hero-left p {
        margin: 0;
        font-size: 0.98rem;
        color: #475569;
        line-height: 1.45;
    }
    .hero-tagline {
        font-family: 'Georgia', serif;
        font-style: italic;
        color: #2563eb;
        font-size: 0.95rem;
        font-weight: 600;
        white-space: nowrap;
        padding-top: 4px;
    }
    .chat-row {
        display: flex;
        align-items: flex-start;
        margin-bottom: 16px;
        gap: 12px;
    }
    .chat-row.user {
        justify-content: flex-end;
    }
    .chat-row.assistant {
        justify-content: flex-start;
    }
    .avatar {
        width: 38px;
        height: 38px;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        flex-shrink: 0;
        font-size: 18px;
        box-shadow: 0 2px 6px rgba(0,0,0,0.08);
    }
    .avatar.bot {
        background: linear-gradient(135deg, #e0e7ff, #c7d2fe);
        color: #1d4ed8;
        border: 1px solid #bfdbfe;
    }
    .avatar.user {
        background: #2b4c8c;
        color: #ffffff;
    }
    .bubble {
        max-width: 76%;
        padding: 13px 18px;
        border-radius: 16px;
        font-size: 0.95rem;
        line-height: 1.5;
        position: relative;
    }
    .bubble.user {
        background-color: #d8e2ff;
        color: #1e293b;
        border-top-right-radius: 4px;
    }
    .bubble.assistant {
        background-color: #ffffff;
        color: #1e293b;
        border: 1px solid #e2e8f0;
        border-top-left-radius: 4px;
        box-shadow: 0 2px 6px rgba(15, 23, 42, 0.03);
    }
    .timestamp {
        font-size: 0.72rem;
        color: #64748b;
        margin-top: 6px;
        display: block;
    }
    .bubble.user .timestamp {
        text-align: right;
        color: #4f6491;
    }
    .debug-pill {
        margin-top: 8px;
        padding-top: 6px;
        border-top: 1px dashed #e2e8f0;
        font-size: 0.74rem;
        color: #64748b;
        font-family: monospace;
    }
    div[data-testid="stHorizontalBlock"] button {
        border-radius: 22px !important;
        border: 1px solid #cbd5e1 !important;
        background-color: #ffffff !important;
        color: #1e3a8a !important;
        font-size: 0.84rem !important;
        font-weight: 500 !important;
        padding: 0.35rem 0.85rem !important;
        box-shadow: 0 1px 3px rgba(0,0,0,0.03) !important;
        transition: all 0.15s ease !important;
    }
    div[data-testid="stHorizontalBlock"] button:hover {
        border-color: #2563eb !important;
        background-color: #eff6ff !important;
        color: #1d4ed8 !important;
    }
    div[data-testid="stChatInput"] {
        background-color: #ffffff;
        border: 1px solid #cbd5e1;
        border-radius: 16px;
        padding: 4px 6px;
        box-shadow: 0 4px 12px rgba(15, 23, 42, 0.05);
    }
    div[data-testid="stChatInput"] button {
        background-color: #1d63ed !important;
        color: white !important;
        border-radius: 12px !important;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# --- INITIALIZE ENGINE & SESSION STATE ---
if "engine" not in st.session_state:
    st.session_state.engine = ElizaEngine("rules.json")

if "messages" not in st.session_state:
    st.session_state.messages = [
        {
            "role": "assistant",
            "content": "Assalam-o-Alaikum! I'm **CampusMate UoS** (BS Data Science Sem-3). Ask about your daily timetable, course instructors, Wazir Agha Library, or Prime Cafe!",
            "time": current_time_str(),
            "debug": None,
        }
    ]

# --- SIDEBAR CONTROLS ---
with st.sidebar:
    st.header("⚙️ AI Engine Controls")
    show_debug = st.toggle("Show ELIZA Rule Trace", value=False)

    st.subheader("🧠 ELIZA Memory Stack")
    if st.session_state.engine.memory_stack:
        for i, item in enumerate(st.session_state.engine.memory_stack, 1):
            st.info(f"**Slot {i}:** {item}")
    else:
        st.caption("Empty (populates when you share study stress or feelings).")

    st.divider()
    if st.button("🗑️ Clear Conversation", use_container_width=True):
        st.session_state.engine.clear_memory()
        st.session_state.messages = [
            {
                "role": "assistant",
                "content": "Chat cleared! How can I help you with your University of Sargodha schedule or studies?",
                "time": current_time_str(),
                "debug": None,
            }
        ]
        st.rerun()

# --- TOP HERO BANNER ---
st.markdown(
    """
    <div class="hero-banner">
        <div class="hero-left">
            <h1>Hello! 👋</h1>
            <p>Ask me anything about our university, academics,<br>or study resources.</p>
        </div>
        <div class="hero-tagline">Learn • Get Help • Succeed</div>
    </div>
    """,
    unsafe_allow_html=True,
)

# --- RENDER CHAT HISTORY ---
for msg in st.session_state.messages:
    role = msg["role"]
    content_html = format_markdown_to_html(msg["content"])
    timestamp = msg.get("time", "")

    if role == "user":
        st.markdown(
            f"""
            <div class="chat-row user">
                <div class="bubble user">
                    {content_html}
                    <span class="timestamp">{timestamp} ✓✓</span>
                </div>
                <div class="avatar user">👤</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    else:
        debug_html = ""
        if show_debug and msg.get("debug"):
            d = msg["debug"]
            debug_html = (
                f"<div class='debug-pill'>🔍 Intent: <b>{d['intent']}</b> | "
                f"Priority: {d['priority']} | {d['latency_ms']} ms</div>"
            )

        st.markdown(
            f"""
            <div class="chat-row assistant">
                <div class="avatar bot">🎓</div>
                <div class="bubble assistant">
                    {content_html}
                    <span class="timestamp">{timestamp}</span>
                    {debug_html}
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

# --- QUICK-ACTION SUGGESTION CHIPS ---
st.write("")
chip_cols = st.columns(4)
chips = [
    ("📅 Monday Classes", "What is my Monday schedule?"),
    ("🤖 AI Course", "When is Artificial Intelligence class?"),
    ("📖 UoS Library", "Wazir Agha Library timings?"),
    ("😰 Exam Stress", "I am stressed about Data Structures"),
]

for col, (label, prompt_text) in zip(chip_cols, chips):
    with col:
        if st.button(label, use_container_width=True):
            st.session_state["chip_prompt"] = prompt_text

# --- INPUT BAR ---
user_query = st.chat_input("Type your message...")
if "chip_prompt" in st.session_state:
    user_query = st.session_state.pop("chip_prompt")

if user_query:
    st.session_state.messages.append(
        {
            "role": "user",
            "content": user_query,
            "time": current_time_str(),
            "debug": None,
        }
    )
    reply, debug_data = st.session_state.engine.get_response(user_query)
    st.session_state.messages.append(
        {
            "role": "assistant",
            "content": reply,
            "time": current_time_str(),
            "debug": debug_data,
        }
    )
    st.rerun()
