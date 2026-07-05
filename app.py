"""
app.py
------
Streamlit frontend for the Agentic AI Study Assistant.

This file ONLY handles the UI/UX layer. All agent logic (LLM, tools,
prompt handling, etc.) lives in the existing backend (agent.py, main.py,
config.py, tools/*). This module simply imports `build_agent` and talks
to it.

Run with:
    python -m streamlit run app.py
"""

import traceback
from datetime import datetime

import streamlit as st

# ---------------------------------------------------------------------------
# Backend import
# ---------------------------------------------------------------------------
# We import the agent builder from the existing backend. If the backend
# (or its dependencies / .env) is broken, we don't want the whole app to
# crash with a traceback -- we want to show a friendly error instead.
try:
    from agent import build_agent
    BACKEND_IMPORT_ERROR = None
except Exception as import_error:  # noqa: BLE001
    build_agent = None
    BACKEND_IMPORT_ERROR = str(import_error)


# ---------------------------------------------------------------------------
# Page configuration (must be the first Streamlit call)
# ---------------------------------------------------------------------------
st.set_page_config(
    page_title="Agentic AI Study Assistant",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded",
)


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------
APP_TITLE = "🤖 Agentic AI Study Assistant"
APP_SUBTITLE = "Learn Smarter with AI-Powered Assistance"
DEVELOPER_NAME = "Your Name"
APP_VERSION = "1.0.0"
GITHUB_URL = "https://github.com/your-username/agentic-ai-study-assistant"
MODEL_NAME = "Groq Llama-3 (see config.py for exact model)"

EXAMPLE_PROMPTS = [
    "What is Machine Learning?",
    "Calculate 225*17",
    "Read notes.txt",
]


# ---------------------------------------------------------------------------
# Custom CSS for a cleaner, more modern look
# ---------------------------------------------------------------------------
CUSTOM_CSS = """
<style>
    /* Tighten default top padding */
    .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
    }

    /* Header styling */
    .app-header-title {
        font-size: 2.2rem;
        font-weight: 700;
        margin-bottom: 0.2rem;
    }
    .app-header-subtitle {
        font-size: 1.05rem;
        color: var(--text-color, #888);
        opacity: 0.8;
        margin-bottom: 1.2rem;
    }

    /* Sidebar section headers */
    .sidebar-section-title {
        font-size: 0.95rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.03em;
        opacity: 0.7;
        margin-top: 1.2rem;
        margin-bottom: 0.4rem;
    }

    /* Status pill */
    .status-pill {
        display: inline-block;
        padding: 0.15rem 0.6rem;
        border-radius: 999px;
        font-size: 0.85rem;
        font-weight: 600;
    }
    .status-online {
        background-color: rgba(46, 204, 113, 0.15);
        color: #2ecc71;
    }
    .status-offline {
        background-color: rgba(231, 76, 60, 0.15);
        color: #e74c3c;
    }

    /* Example prompt buttons */
    div[data-testid="stButton"] button {
        border-radius: 10px;
        width: 100%;
    }

    /* Footer */
    .app-footer {
        text-align: center;
        opacity: 0.65;
        font-size: 0.85rem;
        margin-top: 2rem;
    }

    /* Chat timestamp */
    .chat-timestamp {
        font-size: 0.72rem;
        opacity: 0.55;
        margin-top: -0.4rem;
    }
</style>
"""
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)


# ---------------------------------------------------------------------------
# Session state initialization
# ---------------------------------------------------------------------------
def init_session_state() -> None:
    """Initialize all session_state keys used across the app."""
    if "messages" not in st.session_state:
        # Each message: {"role": "user"/"assistant", "content": str, "time": str}
        st.session_state.messages = []

    if "agent" not in st.session_state:
        st.session_state.agent = None

    if "agent_error" not in st.session_state:
        st.session_state.agent_error = None

    if "pending_prompt" not in st.session_state:
        st.session_state.pending_prompt = None


# ---------------------------------------------------------------------------
# Agent loading (cached so it's built only once per session)
# ---------------------------------------------------------------------------
@st.cache_resource(show_spinner=False)
def load_agent():
    """
    Build the LangChain agent exactly once and cache it for reuse.
    Raises the original exception on failure so the caller can decide
    how to present it to the user.
    """
    return build_agent()


def get_agent():
    """
    Return a ready-to-use agent instance, or None if it could not be
    built. Any error is stored in session_state for display in the UI.
    """
    if BACKEND_IMPORT_ERROR is not None:
        st.session_state.agent_error = (
            "Could not import the backend agent module. "
            f"Details: {BACKEND_IMPORT_ERROR}"
        )
        return None

    if st.session_state.agent is not None:
        return st.session_state.agent

    try:
        agent = load_agent()
        st.session_state.agent = agent
        st.session_state.agent_error = None
        return agent
    except Exception as error:  # noqa: BLE001
        st.session_state.agent_error = (
            "Failed to initialize the AI agent. This usually means the "
            "Groq API key is missing/invalid, the .env file could not be "
            f"loaded, or a network issue occurred.\n\nDetails: {error}"
        )
        return None


# ---------------------------------------------------------------------------
# Agent invocation helper
# ---------------------------------------------------------------------------
def invoke_agent(agent, user_input: str) -> str:
    """
    Call the LangChain agent with the user's input and return only the
    final textual answer. Handles a few common LangChain response shapes
    defensively since the exact return type depends on the backend
    implementation.
    """
    # Different agent builders expect different input shapes. LangChain's
    # newer `create_agent()` (LangGraph-based) expects a "messages" list,
    # while the classic AgentExecutor expects an "input" string. We try
    # the shapes in order of likelihood and use whichever one the agent
    # actually accepts without erroring or silently ignoring our input.
    invocation_attempts = [
        {"messages": [{"role": "user", "content": user_input}]},
        {"messages": [("user", user_input)]},
        {"input": user_input},
        user_input,
    ]

    last_error = None
    result = None
    for payload in invocation_attempts:
        try:
            result = agent.invoke(payload)
            break
        except Exception as attempt_error:  # noqa: BLE001
            last_error = attempt_error
            continue

    if result is None:
        # None of the known input shapes worked -- re-raise the last
        # error so the outer error handler can show a friendly message.
        raise last_error

    # Normalize the response into a plain string.
    if isinstance(result, dict):
        # LangGraph-style agents (e.g. langchain's create_agent) return
        # {"messages": [HumanMessage(...), AIMessage(...), ToolMessage(...)]}
        # The final AI message holds the answer we want to show.
        if "messages" in result and result["messages"]:
            for message in reversed(result["messages"]):
                content = getattr(message, "content", None)
                role = getattr(message, "type", "") or message.__class__.__name__.lower()
                # Skip tool-call-only messages with empty content, and make
                # sure we're grabbing an AI message, not a human/tool one.
                if content and "ai" in role:
                    return str(content).strip()
            # Fallback: last message's content, whatever it is.
            last_content = getattr(result["messages"][-1], "content", "")
            if last_content:
                return str(last_content).strip()

        # Classic AgentExecutor-style agents return one of these keys.
        for key in ("output", "output_text", "result", "answer"):
            if key in result and result[key]:
                return str(result[key]).strip()

        # Fall back to stringifying the whole dict if nothing matched.
        return str(result).strip()

    # Some agents return the AIMessage (or similar) object directly.
    direct_content = getattr(result, "content", None)
    if direct_content:
        return str(direct_content).strip()

    return str(result).strip()


def get_assistant_response(user_input: str) -> str:
    """
    Full pipeline: fetch agent, invoke it, and translate any failure into
    a friendly, non-technical error message.
    """
    agent = get_agent()

    if agent is None:
        return (
            "⚠️ I'm unable to reach the AI engine right now.\n\n"
            f"{st.session_state.agent_error}\n\n"
            "Please check your `.env` configuration and network connection, "
            "then try again."
        )

    try:
        return invoke_agent(agent, user_input)
    except Exception as error:  # noqa: BLE001
        # Log full traceback to the console for developers, but keep the
        # UI message friendly and free of stack traces.
        print("Agent invocation error:\n", traceback.format_exc())
        error_text = str(error).lower()

        if "rate limit" in error_text or "429" in error_text:
            return (
                "⚠️ The AI service is currently rate-limited. "
                "Please wait a moment and try again."
            )
        if "api key" in error_text or "auth" in error_text or "401" in error_text:
            return (
                "⚠️ Authentication with the AI service failed. "
                "Please verify your Groq API key in the `.env` file."
            )
        if "connection" in error_text or "timeout" in error_text:
            return (
                "⚠️ A network error occurred while contacting the AI service. "
                "Please check your internet connection and try again."
            )
        if "file" in error_text and ("not found" in error_text or "reader" in error_text):
            return (
                "⚠️ The File Reader tool couldn't access the requested file. "
                "Please make sure it exists inside the `data/` folder."
            )

        return (
            "⚠️ Something went wrong while processing your request. "
            "Please try again, or rephrase your question.\n\n"
            f"(Technical detail: {error})"
        )


# ---------------------------------------------------------------------------
# Sidebar
# ---------------------------------------------------------------------------
def render_sidebar() -> None:
    """Render the sidebar: branding, model info, tools, status, and actions."""
    with st.sidebar:
        st.markdown("## 🤖 Study Assistant")
        st.caption("Your AI-powered learning companion")

        st.divider()

        # --- About ---
        st.markdown('<div class="sidebar-section-title">About</div>', unsafe_allow_html=True)
        st.markdown(
            "An agentic AI assistant that helps you **learn, calculate, "
            "and read study materials** using a LangChain agent powered "
            "by Groq."
        )

        # --- Model Info ---
        st.markdown('<div class="sidebar-section-title">Model Information</div>', unsafe_allow_html=True)
        st.markdown(f"**Current Model:** `{MODEL_NAME}`")

        # --- Tools ---
        st.markdown('<div class="sidebar-section-title">Tools Available</div>', unsafe_allow_html=True)
        st.markdown("✅ Calculator")
        st.markdown("✅ File Reader")

        # --- System Status ---
        st.markdown('<div class="sidebar-section-title">System Status</div>', unsafe_allow_html=True)
        if BACKEND_IMPORT_ERROR is None and st.session_state.agent_error is None:
            st.markdown(
                '<span class="status-pill status-online">🟢 Online</span>',
                unsafe_allow_html=True,
            )
        else:
            st.markdown(
                '<span class="status-pill status-offline">🔴 Issue Detected</span>',
                unsafe_allow_html=True,
            )

        st.divider()

        # --- Actions ---
        st.markdown('<div class="sidebar-section-title">Actions</div>', unsafe_allow_html=True)
        col1, col2 = st.columns(2)
        with col1:
            if st.button("🗑️ Clear Chat", use_container_width=True):
                st.session_state.messages = []
                st.rerun()
        with col2:
            chat_text = build_chat_transcript()
            st.download_button(
                "⬇️ Download",
                data=chat_text,
                file_name="study_assistant_chat.txt",
                mime="text/plain",
                use_container_width=True,
                disabled=len(st.session_state.messages) == 0,
            )

        st.divider()

        # --- Project Info ---
        st.markdown('<div class="sidebar-section-title">Project Information</div>', unsafe_allow_html=True)
        st.markdown(f"**Developer:** {DEVELOPER_NAME}")
        st.markdown(f"**Version:** {APP_VERSION}")
        st.markdown(f"**GitHub:** [Repository]({GITHUB_URL})")

        st.divider()

        # --- Footer ---
        st.markdown(
            """
            <div class="app-footer">
                Made with ❤️ using<br>
                Python • LangChain • Groq • Streamlit
            </div>
            """,
            unsafe_allow_html=True,
        )


def build_chat_transcript() -> str:
    """Build a plain-text transcript of the chat for the download button."""
    lines = []
    for msg in st.session_state.messages:
        role_label = "You" if msg["role"] == "user" else "Assistant"
        timestamp = msg.get("time", "")
        lines.append(f"[{timestamp}] {role_label}: {msg['content']}")
    return "\n\n".join(lines)


# ---------------------------------------------------------------------------
# Header
# ---------------------------------------------------------------------------
def render_header() -> None:
    """Render the top header with title and subtitle."""
    st.markdown(f'<div class="app-header-title">{APP_TITLE}</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="app-header-subtitle">{APP_SUBTITLE}</div>', unsafe_allow_html=True)


# ---------------------------------------------------------------------------
# Example prompts
# ---------------------------------------------------------------------------
def render_example_prompts() -> None:
    """Show quick-start example prompt buttons above the chat."""
    st.markdown("###### 💡 Try an example:")
    cols = st.columns(len(EXAMPLE_PROMPTS))
    for col, prompt in zip(cols, EXAMPLE_PROMPTS):
        with col:
            if st.button(prompt, key=f"example_{prompt}", use_container_width=True):
                st.session_state.pending_prompt = prompt
    st.divider()


# ---------------------------------------------------------------------------
# Chat history rendering
# ---------------------------------------------------------------------------
def render_chat_history() -> None:
    """Render all past messages using st.chat_message()."""
    for msg in st.session_state.messages:
        avatar = "🧑‍🎓" if msg["role"] == "user" else "🤖"
        with st.chat_message(msg["role"], avatar=avatar):
            st.markdown(msg["content"])
            if msg.get("time"):
                st.markdown(
                    f'<div class="chat-timestamp">{msg["time"]}</div>',
                    unsafe_allow_html=True,
                )


# ---------------------------------------------------------------------------
# Handling a new user message
# ---------------------------------------------------------------------------
def handle_user_message(prompt: str) -> None:
    """Append the user's message, get the agent's reply, and append it too."""
    timestamp = datetime.now().strftime("%H:%M:%S")

    # Store & show the user message immediately.
    st.session_state.messages.append(
        {"role": "user", "content": prompt, "time": timestamp}
    )
    with st.chat_message("user", avatar="🧑‍🎓"):
        st.markdown(prompt)
        st.markdown(f'<div class="chat-timestamp">{timestamp}</div>', unsafe_allow_html=True)

    # Generate & show the assistant's reply.
    with st.chat_message("assistant", avatar="🤖"):
        with st.spinner("🤔 Thinking..."):
            response = get_assistant_response(prompt)
        st.markdown(response)
        reply_time = datetime.now().strftime("%H:%M:%S")
        st.markdown(f'<div class="chat-timestamp">{reply_time}</div>', unsafe_allow_html=True)

    st.session_state.messages.append(
        {"role": "assistant", "content": response, "time": reply_time}
    )


# ---------------------------------------------------------------------------
# Main application
# ---------------------------------------------------------------------------
def main() -> None:
    init_session_state()
    render_sidebar()
    render_header()

    # Show a persistent warning banner if the backend failed to import.
    if BACKEND_IMPORT_ERROR is not None:
        st.error(
            "⚠️ The backend agent could not be loaded. The app will run, "
            "but chat requests will fail until this is fixed.\n\n"
            f"Details: {BACKEND_IMPORT_ERROR}"
        )

    # Only show example prompts when the conversation is empty, ChatGPT-style.
    if not st.session_state.messages:
        render_example_prompts()

    # Render chat history so far.
    chat_container = st.container()
    with chat_container:
        render_chat_history()

    # If an example prompt button was clicked, treat it like user input.
    if st.session_state.pending_prompt:
        prompt = st.session_state.pending_prompt
        st.session_state.pending_prompt = None
        handle_user_message(prompt)
        st.rerun()

    # Standard chat input box, pinned at the bottom by Streamlit.
    user_prompt = st.chat_input("Ask me anything about your studies...")
    if user_prompt:
        handle_user_message(user_prompt)
        st.rerun()


if __name__ == "__main__":
    main()