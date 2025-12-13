"""
Program Search Page - Search study programs with degree level filter
"""

import streamlit as st
from pathlib import Path
import sys

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Page config
st.set_page_config(
    page_title="Program Search - THD Assistant", page_icon="🔍", layout="wide"
)

# Check if data store is available
if "data_store" not in st.session_state or st.session_state.data_store is None:
    st.error("❌ Program database not loaded. Please return to Home page.")
    st.stop()

data_store = st.session_state.data_store
language = st.session_state.get("language", "EN")

# Title based on language
if language == "EN":
    st.title("🔍 Program Search")
    st.markdown("Search and filter study programs at THD University")
else:
    st.title("🔍 Programmsuche")
    st.markdown("Suchen und filtern Sie Studienprogramme an der THD")

st.markdown("---")

# Degree level filter at the top
col1, col2 = st.columns([1, 3])

with col1:
    if language == "EN":
        degree_filter = st.radio(
            "Select Degree Level",
            options=["All", "Bachelor", "Master"],
            index=0,
            key="degree_filter",
        )
    else:
        degree_filter = st.radio(
            "Abschlussniveau wählen",
            options=["Alle", "Bachelor", "Master"],
            index=0,
            key="degree_filter",
        )
        # Convert German to English for filtering
        degree_map = {"Alle": "All", "Bachelor": "Bachelor", "Master": "Master"}
        degree_filter = degree_map[degree_filter]

# Get all programs
all_programs = data_store.get_all_programs()

if not all_programs:
    st.error(
        "❌ No programs available"
        if language == "EN"
        else "❌ Keine Programme verfügbar"
    )
    st.stop()

# Filter programs by degree level
if degree_filter == "All":
    filtered_programs = all_programs
else:
    # Case-insensitive comparison to fix filter issue
    filtered_programs = [
        p for p in all_programs if p.degree_level.lower() == degree_filter.lower()
    ]

# Search section
with col2:
    if language == "EN":
        search_query = st.text_input(
            "🔍 Type to search programs",
            placeholder="Type anything (e.g., c, cyber, business...)",
            help="Search works as you type - shows all programs containing your text",
            key="search_input",
        )
    else:
        search_query = st.text_input(
            "🔍 Tippen Sie zum Suchen",
            placeholder="Tippen Sie etwas (z.B. c, cyber, business...)",
            help="Suche funktioniert während Sie tippen",
            key="search_input",
        )

st.markdown("---")


# Navigation callback
def set_program_and_switch(code):
    st.session_state.selected_program_id = code


# Perform live search as user types
if search_query and search_query.strip():
    # Simple text search through filtered programs
    search_term = search_query.strip().lower()

    # Search in title and faculty (since description is missing)
    search_results = []
    for program in filtered_programs:
        # Check if search term is in title or faculty
        if (
            search_term in program.title.lower()
            or search_term in program.faculty.lower()
        ):
            search_results.append(program)

    # Display results
    if search_results:
        if language == "EN":
            st.success(
                f"✅ Found {len(search_results)} programs matching '{search_query}'"
            )
        else:
            st.success(
                f"✅ {len(search_results)} Programme gefunden für '{search_query}'"
            )

        # Display each result
        for i, program in enumerate(search_results, 1):
            with st.container():
                col1, col2 = st.columns([4, 1])

                with col1:
                    # Generate tags HTML if tags exist
                    tags_html = ""
                    if program.tags:
                        tags_html = (
                            '<div style="margin-top: 8px;">'
                            + " ".join(
                                [
                                    f'<span style="background: #f5f5f5; color: #666; padding: 2px 8px; border-radius: 10px; font-size: 11px; margin-right: 5px;">#{tag}</span>'
                                    for tag in program.tags[:4]
                                ]
                            )
                            + "</div>"
                        )

                    st.markdown(
                        f"""
                        <div style="background: white; padding: 20px; border-radius: 10px; margin-bottom: 15px; box-shadow: 0 2px 8px rgba(0,0,0,0.1); border-left: 4px solid #667eea;">
                            <div style="font-size: 20px; font-weight: bold; color: #333; margin-bottom: 10px;">
                                {i}. {program.title}
                            </div>
                            <div style="display: flex; gap: 10px; margin-bottom: 10px;">
                                <span style="background: #e3f2fd; color: #1976d2; padding: 4px 10px; border-radius: 12px; font-size: 12px; font-weight: 600;">{program.degree_level}</span>
                                <span style="background: #e8f5e9; color: #388e3c; padding: 4px 10px; border-radius: 12px; font-size: 12px; font-weight: 600;">{program.language_of_instruction}</span>
                            </div>
                            <div style="color: #555;">
                                <strong>Faculty:</strong> {program.faculty}<br>
                                <strong>Duration:</strong> {program.duration_semesters} Semesters ({program.ects_total} ECTS)
                            </div>
                            {tags_html}
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )

                with col2:
                    st.markdown("<br>", unsafe_allow_html=True)
                    btn_label = (
                        "📋 View Details" if language == "EN" else "📋 Details anzeigen"
                    )
                    # Use callback to ensure state is set before navigation
                    if st.button(
                        btn_label,
                        key=f"view_search_{i}",
                        use_container_width=True,
                        on_click=set_program_and_switch,
                        args=(program.code,),
                    ):
                        st.switch_page("pages/2_📋_Program_Details.py")
    else:
        if language == "EN":
            st.warning(
                f"⚠️ No programs found matching '{search_query}'. Try different keywords."
            )
        else:
            st.warning(
                f"⚠️ Keine Programme gefunden für '{search_query}'. Versuchen Sie andere Stichwörter."
            )

else:
    # Show all programs (filtered by degree)
    if language == "EN":
        st.info(f"💡 Showing all {degree_filter} programs. Enter keywords to search.")
        st.markdown(f"### 📚 {len(filtered_programs)} {degree_filter} Programs")
    else:
        filter_text = {"All": "alle", "Bachelor": "Bachelor", "Master": "Master"}[
            degree_filter
        ]
        st.info(
            f"💡 Zeige {filter_text} Programme. Geben Sie Stichwörter ein, um zu suchen."
        )
        st.markdown(f"### 📚 {len(filtered_programs)} {degree_filter}-Programme")

    # Pagination
    programs_per_page = 10
    total_pages = (len(filtered_programs) + programs_per_page - 1) // programs_per_page

    if "current_page" not in st.session_state:
        st.session_state.current_page = 0

    # Reset page if filter changed
    if (
        "last_degree_filter" not in st.session_state
        or st.session_state.last_degree_filter != degree_filter
    ):
        st.session_state.current_page = 0
        st.session_state.last_degree_filter = degree_filter

    # Display programs for current page
    start_idx = st.session_state.current_page * programs_per_page
    end_idx = min(start_idx + programs_per_page, len(filtered_programs))

    for i, program in enumerate(
        filtered_programs[start_idx:end_idx], start=start_idx + 1
    ):
        with st.container():
            col1, col2 = st.columns([4, 1])

            with col1:
                # Generate tags HTML if tags exist
                tags_html = ""
                if program.tags:
                    tags_html = (
                        '<div style="margin-top: 8px;">'
                        + " ".join(
                            [
                                f'<span style="background: #f5f5f5; color: #666; padding: 2px 8px; border-radius: 10px; font-size: 11px; margin-right: 5px;">#{tag}</span>'
                                for tag in program.tags[:4]
                            ]
                        )
                        + "</div>"
                    )

                st.markdown(
                    f"""
                <div style="background: white; padding: 20px; border-radius: 10px; margin-bottom: 15px; box-shadow: 0 2px 8px rgba(0,0,0,0.1); border-left: 4px solid #667eea;">
                    <div style="font-size: 20px; font-weight: bold; color: #333; margin-bottom: 10px;">
                        {i}. {program.title}
                    </div>
                    <div style="display: flex; gap: 10px; margin-bottom: 10px;">
                        <span style="background: #e3f2fd; color: #1976d2; padding: 4px 10px; border-radius: 12px; font-size: 12px; font-weight: 600;">{program.degree_level}</span>
                        <span style="background: #e8f5e9; color: #388e3c; padding: 4px 10px; border-radius: 12px; font-size: 12px; font-weight: 600;">{program.language_of_instruction}</span>
                    </div>
                    <div style="color: #555;">
                        <strong>Faculty:</strong> {program.faculty}<br>
                        <strong>Duration:</strong> {program.duration_semesters} Semesters ({program.ects_total} ECTS)
                    </div>
                    {tags_html}
                </div>
                """,
                    unsafe_allow_html=True,
                )

            with col2:
                st.markdown("<br>", unsafe_allow_html=True)
                btn_label = (
                    "📋 View Details" if language == "EN" else "📋 Details anzeigen"
                )
                # Use callback for pagination buttons too
                if st.button(
                    btn_label,
                    key=f"view_all_{i}",
                    use_container_width=True,
                    on_click=set_program_and_switch,
                    args=(program.code,),
                ):
                    st.switch_page("pages/2_📋_Program_Details.py")

    # Pagination controls
    if total_pages > 1:
        st.markdown("---")
        col1, col2, col3, col4, col5 = st.columns([1, 1, 2, 1, 1])

        with col1:
            first_label = "⏮️ First" if language == "EN" else "⏮️ Erste"
            if st.button(first_label, disabled=(st.session_state.current_page == 0)):
                st.session_state.current_page = 0
                st.rerun()

        with col2:
            prev_label = "◀️ Prev" if language == "EN" else "◀️ Zurück"
            if st.button(prev_label, disabled=(st.session_state.current_page == 0)):
                st.session_state.current_page -= 1
                st.rerun()

        with col3:
            page_text = (
                f"Page {st.session_state.current_page + 1} of {total_pages}"
                if language == "EN"
                else f"Seite {st.session_state.current_page + 1} von {total_pages}"
            )
            st.markdown(
                f"<div style='text-align: center; padding: 10px;'>{page_text}</div>",
                unsafe_allow_html=True,
            )

        with col4:
            next_label = "Next ▶️" if language == "EN" else "Weiter ▶️"
            if st.button(
                next_label, disabled=(st.session_state.current_page >= total_pages - 1)
            ):
                st.session_state.current_page += 1
                st.rerun()

        with col5:
            last_label = "Last ⏭️" if language == "EN" else "Letzte ⏭️"
            if st.button(
                last_label, disabled=(st.session_state.current_page >= total_pages - 1)
            ):
                st.session_state.current_page = total_pages - 1
                st.rerun()
