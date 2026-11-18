"""
Query Section Component Module.

Renders the primary natural language input box, submission button,
and professional quick-query preset buttons.
"""

from typing import Tuple
import streamlit as st


def render_query_section() -> Tuple[str, bool]:
    """
    Render query input box and preset selection buttons.

    Returns:
        Tuple[str, bool]: (selected_question, submitted_flag)
    """
    st.markdown("<div style='font-size: 14px; font-weight: 600; color: #475569; margin-bottom: 6px;'>SYSTEM ANALYSIS QUERY</div>", unsafe_allow_html=True)

    # Manage session state for prompt selection
    if "current_question" not in st.session_state:
        st.session_state["current_question"] = "Why is Conference Room A warmer than usual?"

    col_input, col_btn = st.columns([5, 1])

    with col_input:
        user_query = st.text_input(
            label="Query Input",
            value=st.session_state["current_question"],
            placeholder="Enter natural language inquiry regarding assets, metrics, or documentation...",
            label_visibility="collapsed",
            key="query_input_field"
        )

    with col_btn:
        submitted = st.button("Analyze", type="primary", use_container_width=True)

    st.markdown("<div style='font-size: 12px; font-weight: 600; color: #64748b; margin-top: 10px; margin-bottom: 6px;'>PRESET ANALYSIS QUERIES</div>", unsafe_allow_html=True)

    col1, col2, col3, col4, col5 = st.columns(5)

    with col1:
        if st.button("Diagnose Temp Issue", use_container_width=True):
            st.session_state["current_question"] = "Why is Conference Room A warmer than usual?"
            st.rerun()

    with col2:
        if st.button("Asset Overview", use_container_width=True):
            st.session_state["current_question"] = "What components belong to AHU-01?"
            st.rerun()

    with col3:
        if st.button("Maintenance History", use_container_width=True):
            st.session_state["current_question"] = "What maintenance should be performed on the cooling coil?"
            st.rerun()

    with col4:
        if st.button("Latest Telemetry", use_container_width=True):
            st.session_state["current_question"] = "What is the latest supply air temperature?"
            st.rerun()

    with col5:
        if st.button("OEM Specifications", use_container_width=True):
            st.session_state["current_question"] = "What are the recommended operating conditions?"
            st.rerun()

    st.markdown("<div style='margin-bottom: 24px;'></div>", unsafe_allow_html=True)
    return user_query, submitted
