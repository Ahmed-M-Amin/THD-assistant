"""
Program Details Page - Display detailed information for a selected program
Dynamically renders based on available data in YAML files
"""

import streamlit as st
from pathlib import Path
import sys

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Page config
st.set_page_config(
    page_title="Program Details - THD Assistant", page_icon="📋", layout="wide"
)


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================


def parse_fee_value(fee_str):
    """Extract numeric value from fee string like '€82' -> 82"""
    if not fee_str:
        return 0
    try:
        # Remove € symbol, spaces, and convert to int
        return int(fee_str.replace("€", "").replace(",", "").strip())
    except (ValueError, AttributeError):
        return 0


def should_show_field(value):
    """Check if a field should be displayed"""
    if value is None:
        return False

    # Allow integer 0
    if isinstance(value, (int, float)) and value == 0:
        return True

    if isinstance(value, str):
        stripped = value.strip().lower()
        # Explicitly allow "0", "€0", "0€"
        if stripped in ["0", "€0", "0€"]:
            return True
        # Hide empty or "none"
        if stripped == "" or stripped == "none":
            return False

    if isinstance(value, list) and len(value) == 0:
        return False

    return True


# ============================================================================
# MAIN PAGE LOGIC
# ============================================================================

# Check if data store is available
if "data_store" not in st.session_state or st.session_state.data_store is None:
    st.error(
        "❌ Program database not loaded. Please return to Home page."
        if st.session_state.get("language") == "EN"
        else "❌ Programmdatenbank nicht geladen. Bitte zur Startseite zurückkehren."
    )
    st.stop()

data_store = st.session_state.data_store
language = st.session_state.get("language", "EN")

# Page title
if language == "EN":
    st.title("📋 Program Details")
else:
    st.title("📋 Programmdetails")

# Get all programs for dropdown
all_programs = data_store.get_all_programs()

if not all_programs:
    st.error(
        "❌ No programs available"
        if language == "EN"
        else "❌ Keine Programme verfügbar"
    )
    st.stop()

# Create program options for dropdown
program_options = {
    f"{p.title} ({p.degree_level}, {p.language_of_instruction})": p.code
    for p in all_programs
}
program_titles = list(program_options.keys())

# Find selected program
selected_title = None
if st.session_state.get("selected_program_id"):
    # Find the program with matching code
    for title, code in program_options.items():
        if code == st.session_state.selected_program_id:
            selected_title = title
            break

# Program selector
if selected_title:
    default_index = program_titles.index(selected_title)
else:
    default_index = 0

if language == "EN":
    selected_program_title = st.selectbox(
        "Select a program to view details", options=program_titles, index=default_index
    )
else:
    selected_program_title = st.selectbox(
        "Wählen Sie ein Programm, um Details anzuzeigen",
        options=program_titles,
        index=default_index,
    )

selected_program_code = program_options[selected_program_title]

# Find the program object
selected_program = None
for program in all_programs:
    if program.code == selected_program_code:
        selected_program = program
        break

if not selected_program:
    st.error(
        "❌ Program not found" if language == "EN" else "❌ Programm nicht gefunden"
    )
    st.stop()


# ============================================================================
# MAIN LAYOUT - TWO COLUMNS
# ============================================================================

col1, col2 = st.columns([2, 1])

# ============================================================================
# COLUMN 1 - MAIN CONTENT
# ============================================================================

with col1:
    # ========================================================================
    # PROGRAM HEADER (Always show)
    # ========================================================================
    st.markdown(
        f"""
    <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                color: white; padding: 30px; border-radius: 15px; margin-bottom: 20px;">
        <h1 style="margin: 0; font-size: 36px;">{selected_program.title}</h1>
        <p style="margin: 10px 0 0 0; font-size: 18px; opacity: 0.9;">
            {selected_program.degree_level.upper()} {"Program" if language == "EN" else "Programm"} | {selected_program.language_of_instruction.upper()}
        </p>
    </div>
    """,
        unsafe_allow_html=True,
    )

    # ========================================================================
    # QUICK FACTS (Only if data exists)
    # ========================================================================
    if should_show_field(selected_program.quick_facts):
        if language == "EN":
            st.markdown("### ⚡ Quick Facts")
        else:
            st.markdown("### ⚡ Schnelle Fakten")

        # Filter out fee-related quick facts (fees are shown dynamically in sidebar)
        fee_keywords = ["€82", "semester contribution", "tuition fee", "No tuition"]
        for fact in selected_program.quick_facts:
            # Skip facts that contain fee-related keywords
            if not any(keyword in fact for keyword in fee_keywords):
                st.markdown(f"✓ {fact}")

        st.markdown("---")

    # ========================================================================
    # OVERVIEW (Always show)
    # ========================================================================
    if language == "EN":
        st.markdown("### 📖 Overview")
        if should_show_field(selected_program.field_of_study):
            st.markdown(
                f"**Field of Study:** {selected_program.field_of_study.replace('_', ' ').title()}"
            )
        st.markdown(f"**Faculty:** {selected_program.faculty}")
        st.markdown(f"**Duration:** {selected_program.duration_semesters} Semesters")
        st.markdown(f"**ECTS Credits:** {selected_program.ects_total}")

        if should_show_field(selected_program.tags):
            st.markdown(
                "**Tags:** " + ", ".join([f"#{tag}" for tag in selected_program.tags])
            )

        # Display intakes
        if selected_program.intakes:
            st.markdown("**Application Periods:**")
            for intake in selected_program.intakes:
                st.markdown(
                    f"- **{intake.term.capitalize()}:** {intake.application_window.start} to {intake.application_window.end}"
                )
    else:
        st.markdown("### 📖 Überblick")
        if should_show_field(selected_program.field_of_study):
            st.markdown(
                f"**Studienfeld:** {selected_program.field_of_study.replace('_', ' ').title()}"
            )
        st.markdown(f"**Fakultät:** {selected_program.faculty}")
        st.markdown(f"**Dauer:** {selected_program.duration_semesters} Semester")
        st.markdown(f"**ECTS-Punkte:** {selected_program.ects_total}")

        if should_show_field(selected_program.tags):
            st.markdown(
                "**Tags:** " + ", ".join([f"#{tag}" for tag in selected_program.tags])
            )

        # Display intakes
        if selected_program.intakes:
            st.markdown("**Bewerbungszeiträume:**")
            for intake in selected_program.intakes:
                st.markdown(
                    f"- **{intake.term.capitalize()}:** {intake.application_window.start} bis {intake.application_window.end}"
                )

    st.markdown("---")

    # ========================================================================
    # ACADEMIC BACKGROUND REQUIREMENTS (Based on degree level)
    # ========================================================================
    if (
        selected_program.eligibility
        and selected_program.eligibility.academic_background
    ):
        if language == "EN":
            st.markdown("### 🎓 Academic Background Requirements")
        else:
            st.markdown("### 🎓 Akademische Voraussetzungen")

        academic_bg = selected_program.eligibility.academic_background

        # Show requirements based on program's degree level
        if selected_program.degree_level == "bachelor" and academic_bg.bachelor:
            if academic_bg.bachelor.get("required"):
                st.markdown(
                    "**Required:**" if language == "EN" else "**Erforderlich:**"
                )
                for req in academic_bg.bachelor["required"]:
                    st.markdown(f"- {req}")

            if academic_bg.bachelor.get("preferred"):
                st.markdown("**Preferred:**" if language == "EN" else "**Bevorzugt:**")
                for pref in academic_bg.bachelor["preferred"]:
                    st.markdown(f"- {pref}")

        elif selected_program.degree_level == "master" and academic_bg.master:
            if academic_bg.master.get("required"):
                st.markdown(
                    "**Required:**" if language == "EN" else "**Erforderlich:**"
                )
                for req in academic_bg.master["required"]:
                    st.markdown(f"- {req}")

            if academic_bg.master.get("preferred"):
                st.markdown("**Preferred:**" if language == "EN" else "**Bevorzugt:**")
                for pref in academic_bg.master["preferred"]:
                    st.markdown(f"- {pref}")

        st.markdown("---")

    # ========================================================================
    # LANGUAGE REQUIREMENTS DETAILS (Always show if exists)
    # ========================================================================
    if (
        selected_program.eligibility
        and selected_program.eligibility.language_requirements
    ):
        if language == "EN":
            st.markdown("### 🌍 Language Requirements")
        else:
            st.markdown("### 🌍 Sprachanforderungen")

        lang_req = selected_program.eligibility.language_requirements

        if should_show_field(lang_req.notes):
            st.info(f"ℹ️ {lang_req.notes}")

        # German requirements
        if lang_req.german:
            st.markdown(
                f"**{'German' if language == 'EN' else 'Deutsch'}:** {lang_req.german.minimum_level}"
            )
            if should_show_field(lang_req.german.accepted_proofs):
                st.markdown(
                    f"*{'Accepted certificates' if language == 'EN' else 'Akzeptierte Zertifikate'}:*"
                )
                for proof in lang_req.german.accepted_proofs:
                    st.markdown(f"- {proof}")

        # English requirements
        if lang_req.english:
            st.markdown(
                f"**{'English' if language == 'EN' else 'Englisch'}:** {lang_req.english.minimum_level}"
            )
            if should_show_field(lang_req.english.accepted_proofs):
                st.markdown(
                    f"*{'Accepted certificates' if language == 'EN' else 'Akzeptierte Zertifikate'}:*"
                )
                for proof in lang_req.english.accepted_proofs:
                    st.markdown(f"- {proof}")

        st.markdown("---")

    # ========================================================================
    # PROGRAMME SPECIFIC REQUIREMENTS (Only if not "None")
    # ========================================================================
    if (
        selected_program.eligibility
        and selected_program.eligibility.programme_specific_requirements
    ):
        desc = selected_program.eligibility.programme_specific_requirements.description
        if should_show_field(desc):
            if language == "EN":
                st.markdown("### ℹ️ Programme-Specific Requirements")
            else:
                st.markdown("### ℹ️ Programmspezifische Anforderungen")
            st.info(desc)
            st.markdown("---")

    # ========================================================================
    # REQUIRED DOCUMENTS (Tabs for student category)
    # ========================================================================
    if selected_program.required_documents:
        if language == "EN":
            st.markdown("### 📄 Required Documents")
        else:
            st.markdown("### 📄 Erforderliche Dokumente")

        # Determine level (normalize to lowercase)
        level_key = selected_program.degree_level.lower()

        # Check if we have documents for this level
        docs_for_level = None
        if "bachelor" in level_key and selected_program.required_documents.bachelor:
            docs_for_level = selected_program.required_documents.bachelor
        elif "master" in level_key and selected_program.required_documents.master:
            docs_for_level = selected_program.required_documents.master

        if docs_for_level:
            # Create tabs for categories
            doc_tabs = st.tabs(["International (Non-EU)", "EU/EEA", "German"])

            # Helper to show docs
            def show_docs(category_key, tab_idx):
                with doc_tabs[tab_idx]:
                    documents = docs_for_level.get(category_key)
                    if documents:
                        for doc in documents:
                            st.markdown(f"- {doc}")
                    else:
                        st.info(
                            "No specific documents listed."
                            if language == "EN"
                            else "Keine spezifischen Dokumente aufgeführt."
                        )

            show_docs("international_non_eu", 0)
            show_docs("eu_eea", 1)
            show_docs("domestic_german", 2)
        else:
            st.info(
                "Document requirements not available."
                if language == "EN"
                else "Dokumentanforderungen nicht verfügbar."
            )

        st.markdown("---")

    # ========================================================================
    # POLICIES (Always show if exists)
    # ========================================================================
    if selected_program.policies:
        if language == "EN":
            st.markdown("### 📋 Policies")
        else:
            st.markdown("### 📋 Richtlinien")

        policies = selected_program.policies

        if should_show_field(policies.late_documents):
            st.markdown(
                f"**{'Late Documents' if language == 'EN' else 'Verspätete Dokumente'}:**"
            )
            st.info(policies.late_documents)

        if should_show_field(policies.recognition_of_priors):
            st.markdown(
                f"**{'Recognition of Prior Learning' if language == 'EN' else 'Anerkennung von Vorleistungen'}:**"
            )
            st.info(policies.recognition_of_priors)

        if should_show_field(policies.visa_requirement):
            st.markdown(
                f"**{'Visa Requirements' if language == 'EN' else 'Visumsanforderungen'}:**"
            )
            st.info(policies.visa_requirement)

        st.markdown("---")

    # ========================================================================
    # FAQs (Only if data exists)
    # ========================================================================
    if should_show_field(selected_program.faqs):
        if language == "EN":
            st.markdown("### ❓ Frequently Asked Questions")
        else:
            st.markdown("### ❓ Häufig gestellte Fragen")

        for faq in selected_program.faqs:
            with st.expander(f"**Q:** {faq.q}"):
                st.write(f"**A:** {faq.a}")

        st.markdown("---")

    # ========================================================================
    # CONTACT INFORMATION (Always show if exists)
    # ========================================================================
    if selected_program.contacts:
        if language == "EN":
            st.markdown("### 📞 Contact Information")
        else:
            st.markdown("### 📞 Kontaktinformationen")

        contacts = selected_program.contacts

        if should_show_field(contacts.programme_page):
            st.markdown(
                f"🌐 [{'Program Website' if language == 'EN' else 'Programm-Website'}]({contacts.programme_page})"
            )

        if should_show_field(contacts.admissions_email):
            st.markdown(
                f"📧 {'Admissions' if language == 'EN' else 'Zulassung'}: [{contacts.admissions_email}](mailto:{contacts.admissions_email})"
            )

        if should_show_field(contacts.international_office_email):
            st.markdown(
                f"🌍 {'International Office' if language == 'EN' else 'Internationales Büro'}: [{contacts.international_office_email}](mailto:{contacts.international_office_email})"
            )

        if should_show_field(contacts.office_hours_url):
            st.markdown(
                f"🕐 [{'Office Hours' if language == 'EN' else 'Sprechzeiten'}]({contacts.office_hours_url})"
            )

        st.markdown("---")

    # ========================================================================
    # APPLICATION PORTAL (Always show if exists)
    # ========================================================================
    if selected_program.application_portal:
        if language == "EN":
            st.markdown("### 🚀 Application Portal")
        else:
            st.markdown("### 🚀 Bewerbungsportal")

        portal = selected_program.application_portal
        st.markdown(
            f"**{portal.label}:** [{'Apply Here' if language == 'EN' else 'Hier bewerben'}]({portal.url})"
        )

    # ========================================================================
    # IMPORTANT NOTES (Only if data exists)
    # ========================================================================
    if should_show_field(selected_program.notes):
        st.markdown("---")
        if language == "EN":
            st.markdown("### 📌 Important Notes")
        else:
            st.markdown("### 📌 Wichtige Hinweise")

        for note in selected_program.notes:
            st.warning(note)


# ============================================================================
# COLUMN 2 - SIDEBAR INFO
# ============================================================================

with col2:
    # ========================================================================
    # FEES SECTION (Fixed fees based on student category from settings)
    # ========================================================================
    if language == "EN":
        st.markdown("### 💰 Tuition Fees")
    else:
        st.markdown("### 💰 Studiengebühren")

    # Get student category from session state
    student_category = st.session_state.get("student_category", "EU/EEA")
    
    # Debug: Show current category
    # st.write(f"DEBUG: Current category = '{student_category}'")

    # Fixed fees for THD (same for all programs)
    if student_category == "International":
        category_label = "International (Non-EU)" if language == "EN" else "International (Nicht-EU)"
        st.info(f"📊 {('Showing fees for' if language == 'EN' else 'Gebühren für')}: **{category_label}**")
        
        st.markdown("**" + ("One-Time Fees:" if language == "EN" else "Einmalige Gebühren:") + "**")
        st.markdown(f"- {('Application Fee' if language == 'EN' else 'Bewerbungsgebühr')}: €60")
        st.markdown("")
        
        st.markdown("**" + ("Per Semester:" if language == "EN" else "Pro Semester:") + "**")
        st.markdown(f"- {('Tuition' if language == 'EN' else 'Studiengebühren')}: €0")
        st.markdown(f"- {('Service Fee' if language == 'EN' else 'Servicegebühr')}: €500")
        st.markdown(f"- {('Student Union' if language == 'EN' else 'Studentenwerk')}: €82")
        st.markdown(f"- **{('Total per semester' if language == 'EN' else 'Gesamt pro Semester')}: €582**")
        
    elif student_category == "EU/EEA":
        category_label = "EU/EEA"
        st.info(f"📊 {('Showing fees for' if language == 'EN' else 'Gebühren für')}: **{category_label}**")
        
        st.markdown("**" + ("One-Time Fees:" if language == "EN" else "Einmalige Gebühren:") + "**")
        st.markdown(f"- {('Application Fee' if language == 'EN' else 'Bewerbungsgebühr')}: €60")
        st.markdown("")
        
        st.markdown("**" + ("Per Semester:" if language == "EN" else "Pro Semester:") + "**")
        st.markdown(f"- {('Tuition' if language == 'EN' else 'Studiengebühren')}: €0")
        st.markdown(f"- {('Student Union' if language == 'EN' else 'Studentenwerk')}: €82")
        st.markdown(f"- **{('Total per semester' if language == 'EN' else 'Gesamt pro Semester')}: €82**")
        
    else:  # German
        category_label = "German" if language == "EN" else "Deutsch"
        st.info(f"📊 {('Showing fees for' if language == 'EN' else 'Gebühren für')}: **{category_label}**")
        
        st.markdown("**" + ("One-Time Fees:" if language == "EN" else "Einmalige Gebühren:") + "**")
        st.markdown(f"- {('Application Fee' if language == 'EN' else 'Bewerbungsgebühr')}: €60")
        st.markdown("")
        
        st.markdown("**" + ("Per Semester:" if language == "EN" else "Pro Semester:") + "**")
        st.markdown(f"- {('Tuition' if language == 'EN' else 'Studiengebühren')}: €0")
        st.markdown(f"- {('Student Union' if language == 'EN' else 'Studentenwerk')}: €82")
        st.markdown(f"- **{('Total per semester' if language == 'EN' else 'Gesamt pro Semester')}: €82**")
    
    st.markdown("---")

    # ========================================================================
    # QUICK ACTIONS
    # ========================================================================
    if language == "EN":
        st.markdown("### ⚡ Quick Actions")

        if st.button("🔍 Search Programs", use_container_width=True):
            st.switch_page("pages/1_🔍_Program_Search.py")

        if st.button("🏠 Back to Home", use_container_width=True):
            st.switch_page("Home.py")
    else:
        st.markdown("### ⚡ Schnellaktionen")

        if st.button("🔍 Programme suchen", use_container_width=True):
            st.switch_page("pages/1_🔍_Program_Search.py")

        if st.button("🏠 Zur Startseite", use_container_width=True):
            st.switch_page("Home.py")

    st.markdown("---")

    # ========================================================================
    # PROGRAM METADATA
    # ========================================================================
    if language == "EN":
        st.markdown("### 📊 Program Info")
        st.markdown(f"""
        - **Code:** {selected_program.code}
        - **Level:** {selected_program.degree_level.title()}
        - **Language:** {selected_program.language_of_instruction.upper()}
        - **Duration:** {selected_program.duration_semesters} Semesters
        - **ECTS:** {selected_program.ects_total}
        """)
    else:
        st.markdown("### 📊 Programminfo")
        st.markdown(f"""
        - **Code:** {selected_program.code}
        - **Niveau:** {selected_program.degree_level.title()}
        - **Sprache:** {selected_program.language_of_instruction.upper()}
        - **Dauer:** {selected_program.duration_semesters} Semester
        - **ECTS:** {selected_program.ects_total}
        """)

    # ========================================================================
    # COMMON QUERIES (Only if data exists)
    # ========================================================================
    if should_show_field(selected_program.common_queries):
        st.markdown("---")
        if language == "EN":
            st.markdown("### 💬 Common Questions")
        else:
            st.markdown("### 💬 Häufige Fragen")

        for query in selected_program.common_queries:
            st.markdown(f"• {query}")
