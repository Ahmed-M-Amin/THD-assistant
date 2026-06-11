"""
Settings Page - User preferences and configuration
"""

import streamlit as st
from pathlib import Path
import sys

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Page config
st.set_page_config(page_title="Settings - THD Assistant", page_icon="⚙️", layout="wide")

language = st.session_state.get("language", "EN")

# Page title
if language == "EN":
    st.title("⚙️ Settings")
    st.markdown("Configure your preferences")
else:
    st.title("⚙️ Einstellungen")
    st.markdown("Konfigurieren Sie Ihre Einstellungen")

st.markdown("---")

# Settings sections
col1, col2 = st.columns(2)

with col1:
    # Language settings
    if language == "EN":
        st.markdown("### 🌐 Language Settings")

        current_language = st.session_state.language

        new_language = st.selectbox(
            "Interface Language",
            options=["EN", "DE"],
            index=0 if current_language == "EN" else 1,
            help="Select your preferred language for the entire application",
        )

        if new_language != current_language:
            st.session_state.language = new_language
            st.success(f"✅ Language changed to {new_language}")
            st.info("🔄 Please refresh or navigate to see changes throughout the app")
    else:
        st.markdown("### 🌐 Spracheinstellungen")

        current_language = st.session_state.language

        new_language = st.selectbox(
            "Oberflächensprache",
            options=["EN", "DE"],
            format_func=lambda x: "English" if x == "EN" else "Deutsch",
            index=0 if current_language == "EN" else 1,
            help="Wählen Sie Ihre bevorzugte Sprache für die gesamte Anwendung",
        )

        if new_language != current_language:
            st.session_state.language = new_language
            st.success(
                f"✅ Sprache geändert zu {'English' if new_language == 'EN' else 'Deutsch'}"
            )
            st.info(
                "🔄 Bitte aktualisieren Sie oder navigieren Sie, um Änderungen in der App zu sehen"
            )

with col2:
    # Student category
    if language == "EN":
        st.markdown("### 👥 Student Category")

        current_category = st.session_state.student_category

        new_category = st.selectbox(
            "Your Student Category",
            options=["German", "EU/EEA", "International"],
            index=["German", "EU/EEA", "International"].index(current_category)
            if current_category in ["German", "EU/EEA", "International"]
            else 1,
            help="This affects the fee information shown to you",
        )

        if new_category != current_category:
            st.session_state.student_category = new_category
            st.success(f"✅ Student category changed to {new_category}")

        # Category information
        with st.expander("ℹ️ About Student Categories"):
            st.markdown("""
            ### Student Categories Explained
            
            **German Students**
            - German citizens or permanent residents
            - No tuition fees
            - Application fee: €60 (one-time)
            - Semester contribution: €82 (student union fee)
            
            **EU/EEA Students**
            - Citizens of EU or EEA countries
            - Same benefits as German students
            - Application fee: €60 (one-time)
            - Semester contribution: €82 (student union fee)
            
            **International Students**
            - Students from outside EU/EEA
            - No tuition fees
            - Application fee: €60 (one-time)
            - Service fee: €500/semester
            - Student union fee: €82/semester
            - Total per semester: €582
            - Additional requirements (visa, language certificates)
            """)
    else:
        st.markdown("### 👥 Studentenkategorie")

        current_category = st.session_state.student_category

        category_map = {
            "German": "Deutsch",
            "EU/EEA": "EU/EWR",
            "International": "International",
        }
        reverse_category_map = {v: k for k, v in category_map.items()}

        new_category_de = st.selectbox(
            "Ihre Studentenkategorie",
            options=["Deutsch", "EU/EWR", "International"],
            index=["Deutsch", "EU/EWR", "International"].index(
                category_map.get(current_category, "EU/EWR")
            ),
            help="Dies beeinflusst die Ihnen angezeigten Gebühreninformationen",
        )

        new_category = reverse_category_map[new_category_de]

        if new_category != current_category:
            st.session_state.student_category = new_category
            st.success(f"✅ Studentenkategorie geändert zu {new_category_de}")

        # Category information
        with st.expander("ℹ️ Über Studentenkategorien"):
            st.markdown("""
            ### Studentenkategorien erklärt
            
            **Deutsche Studenten**
            - Deutsche Staatsbürger oder Daueraufenthaltsberechtigte
            - Keine Studiengebühren
            - Bewerbungsgebühr: €60 (einmalig)
            - Semesterbeitrag: €82 (Studentenwerk)
            
            **EU/EWR-Studenten**
            - Bürger von EU- oder EWR-Ländern
            - Gleiche Vorteile wie deutsche Studenten
            - Bewerbungsgebühr: €60 (einmalig)
            - Semesterbeitrag: €82 (Studentenwerk)
            
            **Internationale Studenten**
            - Studenten von außerhalb der EU/EWR
            - Keine Studiengebühren
            - Bewerbungsgebühr: €60 (einmalig)
            - Servicegebühr: €500/Semester
            - Studentenwerksbeitrag: €82/Semester
            - Gesamt pro Semester: €582
            - Zusätzliche Anforderungen (Visum, Sprachzertifikate)
            """)

st.markdown("---")

# Application info
if language == "EN":
    st.markdown("### ℹ️ Application Information")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown(
            """
        **Current Settings:**
        - Language: `{}`
        - Student Category: `{}`
        """.format(st.session_state.language, st.session_state.student_category)
        )

    with col2:
        st.markdown(
            """
        **System Information:**
        - Programs Loaded: `{}`
        - Session Active: `{}`
        """.format(
                st.session_state.data_store.get_program_count()
                if "data_store" in st.session_state and st.session_state.data_store
                else "N/A",
                "Yes" if "data_store" in st.session_state else "No",
            )
        )
else:
    st.markdown("### ℹ️ Anwendungsinformationen")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown(
            """
        **Aktuelle Einstellungen:**
        - Sprache: `{}`
        - Studentenkategorie: `{}`
        """.format(st.session_state.language, st.session_state.student_category)
        )

    with col2:
        st.markdown(
            """
        **Systeminformationen:**
        - Geladene Programme: `{}`
        - Sitzung aktiv: `{}`
        """.format(
                st.session_state.data_store.get_program_count()
                if "data_store" in st.session_state and st.session_state.data_store
                else "N/A",
                "Ja" if "data_store" in st.session_state else "Nein",
            )
        )

# Reset settings
st.markdown("---")

col1, col2, col3 = st.columns([2, 1, 1])

with col2:
    if language == "EN":
        if st.button("🔄 Reset to Defaults", use_container_width=True):
            st.session_state.language = "EN"
            st.session_state.student_category = "EU/EEA"
            st.success("✅ Settings reset to defaults")
            st.rerun()
    else:
        if st.button("🔄 Auf Standard zurücksetzen", use_container_width=True):
            st.session_state.language = "EN"
            st.session_state.student_category = "EU/EEA"
            st.success("✅ Einstellungen auf Standard zurückgesetzt")
            st.rerun()

with col3:
    if language == "EN":
        if st.button("🏠 Back to Home", use_container_width=True, type="primary"):
            st.switch_page("Home.py")
    else:
        if st.button("🏠 Zur Startseite", use_container_width=True, type="primary"):
            st.switch_page("Home.py")

# Footer
st.markdown("---")
if language == "EN":
    st.markdown(
        """
    <div style="text-align: center; color: #666; padding: 20px;">
        <p>
            THD University Assistant v2.0<br>
            Powered by Google Gemini AI & RAG Technology
        </p>
    </div>
    """,
        unsafe_allow_html=True,
    )
else:
    st.markdown(
        """
    <div style="text-align: center; color: #666; padding: 20px;">
        <p>
            THD Universitätsassistent v2.0<br>
            Unterstützt durch Google Gemini KI & RAG-Technologie
        </p>
    </div>
    """,
        unsafe_allow_html=True,
    )
