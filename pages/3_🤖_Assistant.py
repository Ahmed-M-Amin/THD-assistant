import streamlit as st
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

# Sync chat_history with current_session messages (Double Binding)
st.session_state.chat_history = st.session_state.current_session["messages"]

# Chat mode selection
mode = st.radio(
    "Chat Mode:" if language == "EN" else "Chat-Modus:",
    ["💬 Text Chat", "🎤 Live Chat"],
    horizontal=True,
)

# Display chat history from Session
for msg in st.session_state.current_session["messages"]:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])


# Function to save after every message
def save_chat_update():
    sess_mgr.save_session(st.session_state.current_session)


# ========== TEXT CHAT MODE ==========
if mode == "💬 Text Chat":
    if prompt := st.chat_input(
        "Type your question..." if language == "EN" else "Geben Sie Ihre Frage ein..."
    ):
        # Display user message
        st.session_state.current_session["messages"].append(
            {"role": "user", "content": prompt}
        )
        with st.chat_message("user"):
            st.write(prompt)

        # Save immediately (User msg)
        save_chat_update()

        # Get response
        with st.chat_message("assistant"):
            with st.spinner("Thinking..." if language == "EN" else "Denke nach..."):
                try:
                    response, _ = manager.process_text_query(prompt, language.lower())
                    st.write(response)
                    st.session_state.current_session["messages"].append(
                        {"role": "assistant", "content": response}
                    )
                    # Save immediately (Assistant msg)
                    save_chat_update()

                except Exception as e:
                    st.error(f"Error: {e}")

# ========== LIVE CHAT MODE ==========
else:  # Live Chat
    st.info(
        "🎤 **Live Chat Mode**\\n\\n"
        "Click 'Start' → Speak when ready → Bot responds → Automatically listens again"
        if language == "EN"
        else "🎤 **Live-Chat-Modus**\\n\\n"
        "Klicken Sie auf 'Start' → Sprechen Sie, wenn bereit → Bot antwortet → Hört automatisch wieder zu"
    )

    col1, col2 = st.columns(2)
    with col1:
        if not st.session_state.get("live_chat_active"):
            if st.button("▶️ Start Live Chat", type="primary", use_container_width=True):
                st.session_state.live_chat_active = True
                st.rerun()
        else:
            if st.button("⏹️ Stop Live Chat", use_container_width=True):
                st.session_state.live_chat_active = False
                st.rerun()

    if st.session_state.get("live_chat_active"):
        # Initialize voice handler
        if "voice_handler" not in st.session_state:
            st.session_state.voice_handler = LocalVoiceHandler()

        status = st.empty()
        try:
            status.markdown("### 🔴 Listening... Speak now!")

            # Listen
            text, audio_data = st.session_state.voice_handler.listen_once(
                listen_timeout=30.0, language=language.lower()
            )

            if text is None:
                status.warning("No voice detected. Try speaking again.")
                time.sleep(2)
                st.rerun()
            elif text == "":
                status.error("Could not understand audio. Try speaking louder/clearer.")
                time.sleep(2)
                st.rerun()
            else:
                # Goodbye check
                goodbye_phrases = [
                    "goodbye",
                    "bye",
                    "exit",
                    "quit",
                    "stop",
                    "tschüss",
                    "auf wiedersehen",
                ]
                if any(p in text.lower() for p in goodbye_phrases):
                    goodbye_msg = "Goodbye!"
                    st.session_state.current_session["messages"].append(
                        {"role": "user", "content": text}
                    )
                    st.session_state.current_session["messages"].append(
                        {"role": "assistant", "content": goodbye_msg}
                    )
                    save_chat_update()  # Save goodbye
                    st.session_state.live_chat_active = False
                    st.rerun()

                # User Msg
                st.session_state.current_session["messages"].append(
                    {"role": "user", "content": text}
                )
                with st.chat_message("user"):
                    st.write(text)
                save_chat_update()

                # Processor
                status.markdown("### 🧠 Thinking...")
                response, audio_response = manager.process_text_query(
                    text, language.lower()
                )

                # Assistant Msg
                st.session_state.current_session["messages"].append(
                    {"role": "assistant", "content": response}
                )
                with st.chat_message("assistant"):
                    st.write(response)
                save_chat_update()

                # Speak
                status.markdown("### 🗣️ Speaking...")
                if audio_response:
                    st.session_state.voice_handler.play_audio(audio_response)

                st.rerun()

        except AudioDeviceError as e:
            status.error(f"Microphone error: {e}")
            st.session_state.live_chat_active = False
        except Exception as e:
            status.error(f"Error: {e}")
            logging.error(f"Live chat error: {e}", exc_info=True)
