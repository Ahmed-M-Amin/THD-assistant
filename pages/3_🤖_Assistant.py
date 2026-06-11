import streamlit as st
import streamlit.components.v1 as components
from pathlib import Path
import sys
import logging
import io
import soundfile as sf
import time

# Add project root
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.conversation_manager import ConversationManager
from src.llm_engine_gemini import GeminiLLMEngine
from src.stt_engine_speechrecognition import SpeechRecognitionSTTEngine
from src.tts_engine_edge import EdgeTTSEngine
from src.data_store import ProgramDataStore
from src.config import settings
from src.local_voice_handler import LocalVoiceHandler, AudioDeviceError
from src.live_chat_worker import LiveChatWorker
from src.session_manager import SessionManager

# Page config
st.set_page_config(page_title="THD Assistant", page_icon="🤖", layout="wide")
language = st.session_state.get("language", "EN")
logging.basicConfig(level=logging.INFO)

# --- 1. SESSION MANAGEMENT SETUP ---
if "session_manager" not in st.session_state:
    st.session_state.session_manager = SessionManager()

# Initialize Conversation Manager
if "conversation_manager" not in st.session_state:
    try:
        # Use existing data_store from Home.py if available
        if "data_store" in st.session_state and st.session_state.data_store:
            data_store = st.session_state.data_store
        else:
            data_store = ProgramDataStore()
            st.session_state.data_store = data_store

        stt = SpeechRecognitionSTTEngine()
        llm = GeminiLLMEngine(api_key=settings.GEMINI_API_KEY, data_store=data_store)
        tts = EdgeTTSEngine()
        st.session_state.conversation_manager = ConversationManager(stt, llm, tts)
    except Exception as e:
        st.error(f"Initialization error: {e}")
        st.stop()

manager = st.session_state.conversation_manager
sess_mgr = st.session_state.session_manager

# --- 2. AUTO-ARCHIVE / PAGE TRACKER LOGIC ---
# If user navigated from another page, start a FRESH session
current_page = "Assistant"
last_page = st.session_state.get("last_page", None)

if last_page != current_page:
    # Just arrived -> Create New Chat
    new_sess = sess_mgr.create_session()
    st.session_state.current_session = new_sess
    st.session_state.chat_history = new_sess["messages"]  # Sync legacy var
    st.session_state.last_page = current_page
    # Ensure LLM context is clear
    manager.reset_context()

# Ensure we have a current session object
if "current_session" not in st.session_state:
    # Create default if missing
    new_sess = sess_mgr.create_session()
    st.session_state.current_session = new_sess
    st.session_state.chat_history = new_sess["messages"]

current_sess = st.session_state.current_session

# --- 3. SIDEBAR: HISTORY & ACTIONS ---
with st.sidebar:
    st.title("🗄️ History" if language == "EN" else "🗄️ Verlauf")

    # New Chat Button
    if st.button(
        "➕ New Chat" if language == "EN" else "➕ Neuer Chat",
        use_container_width=True,
        type="primary",
    ):
        new_sess = sess_mgr.create_session()
        st.session_state.current_session = new_sess
        st.session_state.chat_history = new_sess["messages"]
        manager.reset_context()
        st.rerun()

    st.markdown("---")

    # List Past Sessions
    sessions = sess_mgr.list_sessions()
    for s in sessions:
        # Highlight active session? User requested NO blue ball/indicator.
        label = s["title"]
        # if s['id'] == st.session_state.current_session['id']:
        #    label = f"🔵 {label}"  <-- REMOVED PER USER REQUEST

        if st.button(label, key=s["id"], use_container_width=True):
            loaded = sess_mgr.load_session(s["id"])
            if loaded:
                st.session_state.current_session = loaded
                st.session_state.chat_history = loaded["messages"]
                # Attempt to restore LLM context
                manager.reset_context()
                for m in loaded["messages"]:
                    manager.update_context(m["role"], m["content"], language.lower())
                st.rerun()

    st.markdown("---")
    # Delete Current Chat
    if st.button(
        "🗑️ Delete This Chat" if language == "EN" else "🗑️ Chat löschen",
        use_container_width=True,
    ):
        sess_mgr.delete_session(st.session_state.current_session["id"])

        # Logic: Load the next available session, or create new if none left
        remaining_sessions = sess_mgr.list_sessions()
        if remaining_sessions:
            # Load the most recent one (first in list)
            next_session = sess_mgr.load_session(remaining_sessions[0]["id"])
            if next_session:
                st.session_state.current_session = next_session
                st.session_state.chat_history = next_session["messages"]
                manager.reset_context()
                for m in next_session["messages"]:
                    manager.update_context(m["role"], m["content"], language.lower())
        else:
            # None left, must create new
            new_sess = sess_mgr.create_session()
            st.session_state.current_session = new_sess
            st.session_state.chat_history = new_sess["messages"]
            manager.reset_context()

        st.success("Chat deleted")
        time.sleep(0.5)
        st.rerun()

# --- 4. MAIN UI START ---
st.title("🤖 THD Assistant" if language == "EN" else "🤖 THD Assistent")

# Initialize live chat state if missing
if "live_chat_active" not in st.session_state:
    st.session_state.live_chat_active = False

# Sync chat_history with current_session messages (Double Binding)
st.session_state.chat_history = st.session_state.current_session["messages"]

# Display chat history from Session
for msg in st.session_state.current_session["messages"]:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])


# Function to save after every message
def save_chat_update():
    sess_mgr.save_session(st.session_state.current_session)


def reset_live_chat_state():
    """Clear live-mode state, stop worker, and stop any audio playback."""
    worker = st.session_state.get("live_chat_worker")
    if worker is not None:
        worker.stop()
    st.session_state.pop("live_chat_worker", None)
    if "voice_handler" in st.session_state:
        st.session_state.voice_handler.stop_playback()


def get_live_chat_worker() -> LiveChatWorker:
    if "voice_handler" not in st.session_state:
        st.session_state.voice_handler = LocalVoiceHandler()

    session = st.session_state.current_session
    worker = st.session_state.get("live_chat_worker")
    if worker is None:
        worker = LiveChatWorker(
            voice_handler=st.session_state.voice_handler,
            manager=manager,
            language=language.lower(),
            session=session,
            save_session=lambda: sess_mgr.save_session(session),
        )
        worker.start()
        st.session_state.live_chat_worker = worker
    return worker



# ===== SHARED CSS: mic / stop button floated inside the chat input bar =====
is_live = st.session_state.live_chat_active

# In text mode the button label is "🎤"; in live mode it is "⏹ Stop"
# Streamlit sets aria-label = the button text, so we target it directly.
st.markdown("""
<style>
/* --- Mic button (text mode) ------------------------------------------ */
button[aria-label="🎤"] {
    position: fixed !important;
    bottom: 17px !important;
    right: 70px !important;
    z-index: 10000 !important;
    background: transparent !important;
    border: none !important;
    font-size: 1.35rem !important;
    padding: 0 !important;
    margin: 0 !important;
    cursor: pointer !important;
    color: #888 !important;
    border-radius: 50% !important;
    box-shadow: none !important;
    min-height: unset !important;
    height: 36px !important;
    width: 36px !important;
    line-height: 36px !important;
    transition: color 0.2s, background 0.2s !important;
    display: flex !important;
    align-items: center !important;
    justify-content: center !important;
}
button[aria-label="🎤"]:hover {
    color: #ff4b4b !important;
    background: rgba(255,75,75,0.12) !important;
}

/* --- Stop button (live mode) ------------------------------------------ */
button[aria-label="⏹ Stop"] {
    position: fixed !important;
    bottom: 17px !important;
    right: 70px !important;
    z-index: 10000 !important;
    background: #ff4b4b !important;
    border: none !important;
    color: #fff !important;
    font-size: 1.1rem !important;
    font-weight: 700 !important;
    border-radius: 50% !important;
    padding: 0 !important;
    margin: 0 !important;
    cursor: pointer !important;
    height: 36px !important;
    width: 36px !important;
    min-height: unset !important;
    box-shadow: 0 0 10px rgba(255,75,75,0.5) !important;
    animation: stop-pulse 1.4s ease-in-out infinite !important;
    display: flex !important;
    align-items: center !important;
    justify-content: center !important;
    line-height: 36px !important;
    transition: background 0.2s !important;
}
button[aria-label="⏹ Stop"]:hover {
    background: #cc2222 !important;
    animation: none !important;
}
@keyframes stop-pulse {
    0%, 100% { box-shadow: 0 0 6px  rgba(255,75,75,0.5); }
    50%       { box-shadow: 0 0 18px rgba(255,75,75,0.9); }
}

/* --- Breathing room for messages above the bar ----------------------- */
section[data-testid="stMain"] > div {
    padding-bottom: 80px !important;
}
</style>
""", unsafe_allow_html=True)


# ========== TEXT CHAT MODE (default) ==========
if not is_live:
    # Mic button — CSS above floats it inside the chat input bar
    if st.button("🎤", help="Start Live Voice Chat" if language == "EN" else "Live-Sprach-Chat starten"):
        reset_live_chat_state()
        st.session_state.live_chat_active = True
        st.rerun()

    if prompt := st.chat_input(
        "Type your question..." if language == "EN" else "Geben Sie Ihre Frage ein..."
    ):
        st.session_state.current_session["messages"].append(
            {"role": "user", "content": prompt}
        )
        with st.chat_message("user"):
            st.write(prompt)
        save_chat_update()

        with st.chat_message("assistant"):
            with st.spinner("Thinking..." if language == "EN" else "Denke nach..."):
                try:
                    response, _ = manager.process_text_query(prompt, language.lower())
                    st.write(response)
                    st.session_state.current_session["messages"].append(
                        {"role": "assistant", "content": response}
                    )
                    save_chat_update()
                except Exception as e:
                    st.error(f"Error: {e}")

# ========== LIVE CHAT MODE ==========
else:
    if st.button("⏹ Stop", help="Stop Live Chat and return to text mode" if language == "EN" else "Live-Chat beenden und zum Textmodus zurückkehren"):
        reset_live_chat_state()
        st.session_state.live_chat_active = False
        st.rerun()

    worker = get_live_chat_worker()

    status_labels = {
        "starting": ("### 🔴 Starting live chat...", "### 🔴 Live-Chat startet..."),
        "listening": ("### 🔴 Listening… Speak now!", "### 🔴 Hört zu… Sprechen Sie jetzt!"),
        "thinking": ("### 🧠 Thinking...", "### 🧠 Denke nach..."),
        "speaking": ("### 🗣️ Speaking...", "### 🗣️ Spricht..."),
        "no_voice": (
            "No voice detected. Try speaking again.",
            "Keine Stimme erkannt. Bitte erneut sprechen.",
        ),
        "unclear": (
            "Could not understand audio. Try speaking louder/clearer.",
            "Audio nicht verstanden. Bitte lauter/deutlicher sprechen.",
        ),
    }

    idx = 0 if language == "EN" else 1
    if worker.error:
        st.error(f"Error: {worker.error}")
        reset_live_chat_state()
        st.session_state.live_chat_active = False
    elif worker.status in ("stopped", "error"):
        reset_live_chat_state()
        st.session_state.live_chat_active = False
        st.rerun()
    else:
        label = status_labels.get(worker.status, status_labels["listening"])[idx]
        if worker.status in ("no_voice", "unclear"):
            st.warning(label)
        else:
            st.markdown(label)

        time.sleep(1.0)
        st.rerun()
