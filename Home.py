"""
THD University Assistant - Home Page (Main Entry Point)
"""

import streamlit as st
import sys
from pathlib import Path
import base64

# Add src directory to path for imports
project_root = Path(__file__).parent
src_path = project_root / "src"
sys.path.insert(0, str(src_path))

from src.config import settings
from src.data_store import ProgramDataStore

# Page configuration (MUST be first Streamlit command)
st.set_page_config(
    page_title="THD University Assistant",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Initialize session state
if "language" not in st.session_state:
    st.session_state.language = "EN"

if "student_category" not in st.session_state:
    st.session_state.student_category = "EU/EEA"

# Initialize page tracker
if "last_page" not in st.session_state:
    st.session_state.last_page = "Home"

# Initialize session manager
from src.session_manager import SessionManager

if "session_manager" not in st.session_state:
    st.session_state.session_manager = SessionManager()

# Initialize data store (NO CACHE - to ensure latest code is used)
if "data_store" not in st.session_state:
    try:
        with st.spinner("Loading program database..."):
            data_store = ProgramDataStore()
            st.session_state.data_store = data_store
            if not data_store or len(data_store.programs) == 0:
                st.error("❌ No programs loaded - check data files")
                st.session_state.data_store = None
    except Exception as e:
        st.error(f"❌ Failed to load program database: {str(e)}")
        st.session_state.data_store = None


# Function to load background image
def get_background_image():
    """Load background image and convert to base64."""
    background_path = project_root / "assets" / "background.jpg"
    if background_path.exists():
        with open(background_path, "rb") as f:
            data = base64.b64encode(f.read()).decode()
        return data
    return None


# Apply global background
background_data = get_background_image()
if background_data:
    st.markdown(
        f"""
    <style>
    .stApp {{
        background-image: url("data:image/jpeg;base64,{background_data}");
        background-size: cover;
        background-position: center;
        background-repeat: no-repeat;
        background-attachment: fixed;
    }}
    .main {{
        background-color: rgba(255, 255, 255, 0.9);
        border-radius: 15px;
        padding: 20px;
    }}
    /* Sidebar transparency */
    [data-testid="stSidebar"] {{
        background-color: rgba(255, 255, 255, 0.16);
    }}
    </style>
    """,
        unsafe_allow_html=True,
    )

# Language selector at top right
col1, col2 = st.columns([4, 1])

with col2:
    language = st.selectbox(
        "🌐",
        options=["EN", "DE"],
        index=0 if st.session_state.language == "EN" else 1,
        key="language_selector",
        label_visibility="collapsed",
    )

    if language != st.session_state.language:
        st.session_state.language = language
        st.rerun()

# Content based on language
if st.session_state.language == "EN":
    # English content
    # logo_path = project_root / "assets" / "logo.png"

    # # Logo and title together (centered)
    # col1, col2, col3 = st.columns([1, 2, 1])
    # with col2:
    #     if logo_path.exists():
    #         st.image(str(logo_path), width=200)

    # Title section (moved up, no logo)
    st.markdown(
        """
    <div style="text-align: center; margin-top: 20px;">
        <h1 style="font-size: 48px; color: #667eea; margin-bottom: 10px;">
            🎓 THD University Assistant
        </h1>
        <p style="font-size: 20px; color: #0a0a0a; margin-bottom: 30px;">
            Your AI-powered guide to Technische Hochschule Deggendorf
        </p>
    </div>
    """,
        unsafe_allow_html=True,
    )

    st.markdown("---")

    # Features overview
    st.markdown("## 🌟 What Can I Help You With?")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown(
            """
        <div style="background: white; padding: 30px; border-radius: 15px; box-shadow: 0 4px 12px rgba(0,0,0,0.1); text-align: center; height: 280px;">
            <div style="font-size: 48px; margin-bottom: 15px;">🔍</div>
            <h3 style="color: #667eea; margin-bottom: 15px;">Search Programs</h3>
            <p style="color: #666; line-height: 1.6;">
                Explore 93 study programs. 
                Find your perfect program by degree level or keywords.
            </p>
        </div>
        """,
            unsafe_allow_html=True,
        )

        if st.button("🔍 Start Searching", key="search_nav", use_container_width=True):
            st.switch_page("pages/1_🔍_Program_Search.py")

    with col2:
        st.markdown(
            """
        <div style="background: white; padding: 30px; border-radius: 15px; box-shadow: 0 4px 12px rgba(0,0,0,0.1); text-align: center; height: 280px;">
            <div style="font-size: 48px; margin-bottom: 15px;">🎤</div>
            <h3 style="color: #667eea; margin-bottom: 15px;">Speech Chat</h3>
            <p style="color: #666; line-height: 1.6;">
                Ask questions using text or voice. 
                Get instant, accurate AI-powered answers.
            </p>
        </div>
        """,
            unsafe_allow_html=True,
        )

        if st.button("🤖 Start Chat", key="chat_nav", use_container_width=True):
            st.switch_page("pages/3_🤖_Assistant.py")

    with col3:
        st.markdown(
            """
        <div style="background: white; padding: 30px; border-radius: 15px; box-shadow: 0 4px 12px rgba(0,0,0,0.1); text-align: center; height: 280px;">
            <div style="font-size: 48px; margin-bottom: 15px;">⚙️</div>
            <h3 style="color: #667eea; margin-bottom: 15px;">Settings</h3>
            <p style="color: #666; line-height: 1.6;">
                Customize your language and student category preferences.
            </p>
        </div>
        """,
            unsafe_allow_html=True,
        )

        if st.button("⚙️ Settings", key="settings_nav", use_container_width=True):
            st.switch_page("pages/4_⚙️_Settings.py")

    st.markdown("---")

    # Statistics
    st.markdown("## 📊 By The Numbers")

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.markdown(
            """
        <div style="background: white; padding: 20px; border-radius: 10px; text-align: center; box-shadow: 0 2px 8px rgba(0,0,0,0.1);">
            <div style="font-size: 36px; font-weight: bold; color: #667eea;">93</div>
            <div style="font-size: 14px; color: #666;">Study Programs</div>
        </div>
        """,
            unsafe_allow_html=True,
        )

    with col2:
        st.markdown(
            """
        <div style="background: white; padding: 20px; border-radius: 10px; text-align: center; box-shadow: 0 2px 8px rgba(0,0,0,0.1);">
            <div style="font-size: 36px; font-weight: bold; color: #667eea;">2</div>
            <div style="font-size: 14px; color: #666;">Languages</div>
        </div>
        """,
            unsafe_allow_html=True,
        )

    with col3:
        st.markdown(
            """
        <div style="background: white; padding: 20px; border-radius: 10px; text-align: center; box-shadow: 0 2px 8px rgba(0,0,0,0.1);">
            <div style="font-size: 36px; font-weight: bold; color: #667eea;">24/7</div>
            <div style="font-size: 14px; color: #666;">AI Support</div>
        </div>
        """,
            unsafe_allow_html=True,
        )

    with col4:
        st.markdown(
            """
        <div style="background: white; padding: 20px; border-radius: 10px; text-align: center; box-shadow: 0 2px 8px rgba(0,0,0,0.1);">
            <div style="font-size: 36px; font-weight: bold; color: #667eea;">∞</div>
            <div style="font-size: 14px; color: #666;">Questions</div>
        </div>
        """,
            unsafe_allow_html=True,
        )

    st.markdown("---")

    # About section
    st.markdown("## ℹ️ About This Assistant")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown(
            """
        <div style="background-color: rgba(255, 255, 255, 0.95); padding: 20px; border-radius: 10px; color: #000000; border: 1px solid #eee;">
            <h3 style="color: #000000; margin-top: 0;">🤖 Powered by AI</h3>
            <p style="color: #000000; margin-bottom: 0;">
                This assistant uses:<br>
                • <strong>Google Gemini AI</strong> for natural language understanding<br>
                • <strong>RAG Technology</strong> for accurate information<br>
                • <strong>Semantic Search</strong> to find relevant programs<br>
                • <strong>Voice Recognition</strong> for hands-free interaction
            </p>
        </div>
        """,
            unsafe_allow_html=True,
        )

    with col2:
        st.markdown(
            """
        <div style="background-color: rgba(255, 255, 255, 0.95); padding: 20px; border-radius: 10px; color: #000000; border: 1px solid #eee;">
            <h3 style="color: #000000; margin-top: 0;">🎯 Our Mission</h3>
            <p style="color: #000000; margin-bottom: 0;">
                To make university admissions easier by providing:<br>
                • <strong>Instant answers</strong> to your questions<br>
                • <strong>Accurate information</strong> from official sources<br>
                • <strong>Bilingual support</strong> in English and German<br>
                • <strong>24/7 availability</strong> whenever you need help
            </p>
        </div>
        """,
            unsafe_allow_html=True,
        )

else:  # German content
    # logo_path = project_root / "assets" / "logo.png"

    # # Logo and title together (centered)
    # col1, col2, col3 = st.columns([1, 2, 1])
    # with col2:
    #     if logo_path.exists():
    #         st.image(str(logo_path), width=200)

    # Title section (moved up, no logo)
    st.markdown(
        """
    <div style="text-align: center; margin-top: 20px;">
        <h1 style="font-size: 48px; color: #667eea; margin-bottom: 10px;">
            🎓 THD Universitätsassistent
        </h1>
        <p style="font-size: 20px; color: #0a0a0a; margin-bottom: 30px;">
            Ihr KI-gestützter Leitfaden für die Technische Hochschule Deggendorf
        </p>
    </div>
    """,
        unsafe_allow_html=True,
    )

    st.markdown("---")

    # Funktionsübersicht
    st.markdown("## 🌟 Wie kann ich Ihnen helfen?")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown(
            """
        <div style="background: white; padding: 30px; border-radius: 15px; box-shadow: 0 4px 12px rgba(0,0,0,0.1); text-align: center; height: 280px;">
            <div style="font-size: 48px; margin-bottom: 15px;">🔍</div>
            <h3 style="color: #667eea; margin-bottom: 15px;">Programme suchen</h3>
            <p style="color: #666; line-height: 1.6;">
                Durchsuchen Sie 93 Studienprogramme. 
                Finden Sie Ihr perfektes Programm.
            </p>
        </div>
        """,
            unsafe_allow_html=True,
        )

        if st.button("🔍 Suche starten", key="search_nav_de", use_container_width=True):
            st.switch_page("pages/1_🔍_Program_Search.py")

    with col2:
        st.markdown(
            """
        <div style="background: white; padding: 30px; border-radius: 15px; box-shadow: 0 4px 12px rgba(0,0,0,0.1); text-align: center; height: 280px;">
            <div style="font-size: 48px; margin-bottom: 15px;">🎤</div>
            <h3 style="color: #667eea; margin-bottom: 15px;">Sprach-Chat</h3>
            <p style="color: #666; line-height: 1.6;">
                Stellen Sie Fragen per Text oder Sprache.
                Erhalten Sie sofortige KI-Antworten.
            </p>
        </div>
        """,
            unsafe_allow_html=True,
        )

        if st.button("🤖 Chat starten", key="chat_nav_de", use_container_width=True):
            st.switch_page("pages/3_🤖_Assistant.py")

    with col3:
        st.markdown(
            """
        <div style="background: white; padding: 30px; border-radius: 15px; box-shadow: 0 4px 12px rgba(0,0,0,0.1); text-align: center; height: 280px;">
            <div style="font-size: 48px; margin-bottom: 15px;">⚙️</div>
            <h3 style="color: #667eea; margin-bottom: 15px;">Einstellungen</h3>
            <p style="color: #666; line-height: 1.6;">
                Passen Sie Ihre Sprach- und Kategorieeinstellungen an.
            </p>
        </div>
        """,
            unsafe_allow_html=True,
        )

        if st.button(
            "⚙️ Einstellungen", key="settings_nav_de", use_container_width=True
        ):
            st.switch_page("pages/4_⚙️_Settings.py")

    st.markdown("---")

    # Statistiken
    st.markdown("## 📊 Zahlen und Fakten")

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.markdown(
            """
        <div style="background: white; padding: 20px; border-radius: 10px; text-align: center; box-shadow: 0 2px 8px rgba(0,0,0,0.1);">
            <div style="font-size: 36px; font-weight: bold; color: #667eea;">93</div>
            <div style="font-size: 14px; color: #666;">Studienprogramme</div>
        </div>
        """,
            unsafe_allow_html=True,
        )

    with col2:
        st.markdown(
            """
        <div style="background: white; padding: 20px; border-radius: 10px; text-align: center; box-shadow: 0 2px 8px rgba(0,0,0,0.1);">
            <div style="font-size: 36px; font-weight: bold; color: #667eea;">2</div>
            <div style="font-size: 14px; color: #666;">Sprachen</div>
        </div>
        """,
            unsafe_allow_html=True,
        )

    with col3:
        st.markdown(
            """
        <div style="background: white; padding: 20px; border-radius: 10px; text-align: center; box-shadow: 0 2px 8px rgba(0,0,0,0.1);">
            <div style="font-size: 36px; font-weight: bold; color: #667eea;">24/7</div>
            <div style="font-size: 14px; color: #666;">KI-Unterstützung</div>
        </div>
        """,
            unsafe_allow_html=True,
        )

    with col4:
        st.markdown(
            """
        <div style="background: white; padding: 20px; border-radius: 10px; text-align: center; box-shadow: 0 2px 8px rgba(0,0,0,0.1);">
            <div style="font-size: 36px; font-weight: bold; color: #667eea;">∞</div>
            <div style="font-size: 14px; color: #666;">Fragen</div>
        </div>
        """,
            unsafe_allow_html=True,
        )

    st.markdown("---")

    # Über uns
    st.markdown("## ℹ️ Über diesen Assistenten")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown(
            """
        <div style="background-color: rgba(255, 255, 255, 0.95); padding: 20px; border-radius: 10px; color: #000000; border: 1px solid #eee;">
            <h3 style="color: #000000; margin-top: 0;">🤖 Unterstützt durch KI</h3>
            <p style="color: #000000; margin-bottom: 0;">
                Dieser Assistent verwendet:<br>
                • <strong>Google Gemini KI</strong> für natürliches Sprachverständnis<br>
                • <strong>RAG-Technologie</strong> für präzise Informationen<br>
                • <strong>Semantische Suche</strong> zum Finden relevanter Programme<br>
                • <strong>Spracherkennung</strong> für freihändige Interaktion
            </p>
        </div>
        """,
            unsafe_allow_html=True,
        )

    with col2:
        st.markdown(
            """
        <div style="background-color: rgba(255, 255, 255, 0.95); padding: 20px; border-radius: 10px; color: #000000; border: 1px solid #eee;">
            <h3 style="color: #000000; margin-top: 0;">🎯 Unsere Mission</h3>
            <p style="color: #000000; margin-bottom: 0;">
                Hochschulzulassungen erleichtern durch:<br>
                • <strong>Sofortige Antworten</strong> auf Ihre Fragen<br>
                • <strong>Genaue Informationen</strong> aus offiziellen Quellen<br>
                • <strong>Zweisprachiger Support</strong> auf Deutsch und Englisch<br>
                • <strong>24/7 Verfügbarkeit</strong> wann immer Sie Hilfe benötigen
            </p>
        </div>
        """,
            unsafe_allow_html=True,
        )

# Footer
st.markdown("---")
st.markdown(
    """
<div style="text-align: center; color: #666; padding: 20px;">
    <p>
        Made with ❤️ for THD University Students<br>
        Technische Hochschule Deggendorf<br>
        <a href="https://www.th-deg.de" target="_blank">www.th-deg.de</a>
    </p>
</div>
""",
    unsafe_allow_html=True,
)
