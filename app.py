"""
Asset Intelligence Platform — Enterprise Web Application.

Main Streamlit application entry point integrating modular UI components with the backend
LLMOrchestrator, Neo4j Knowledge Graph, Telemetry Engine, and Document RAG Vector Store.
Renders an industrial engineering dashboard (Siemens Desigo CC / Honeywell Forge style).
"""

import os
from dotenv import load_dotenv
import streamlit as st

# Load environment variables dynamically at app startup
load_dotenv(override=True)

# Set page configuration before any other Streamlit commands
st.set_page_config(
    page_title="Asset Intelligence Platform",
    page_icon=None,
    layout="wide",
    initial_sidebar_state="expanded"
)

from llm.orchestrator import LLMOrchestrator
from llm.models import OrchestratorResponse
from ui import (
    inject_custom_css,
    render_sidebar,
    render_header,
    render_kpi_cards,
    render_query_section,
    render_ai_diagnosis,
    render_evidence_section,
    render_execution_details
)


def main() -> None:
    """Main web application execution workflow."""
    # Ensure env vars are fresh on every rerun
    load_dotenv(override=True)

    # Inject enterprise styling rules
    inject_custom_css()

    # Render navigation sidebar
    render_sidebar()

    # Render top enterprise header (Facility & System Status)
    render_header(facility="Bommanahalli Office")

    # Obtain fresh orchestrator instance
    orchestrator = LLMOrchestrator()

    # Render top KPI metrics row
    render_kpi_cards(response=st.session_state.get("latest_response"))

    # Render query input section and preset buttons
    user_query, submitted = render_query_section()

    if user_query.strip():
        # Multi-stage visual progress loader
        progress_placeholder = st.empty()

        with progress_placeholder.container():
            st.markdown(
                """
                <div style="background-color: #ffffff; border: 1px solid #cbd5e1; border-radius: 4px; padding: 16px 20px; margin-bottom: 24px;">
                    <div style="font-size: 14px; font-weight: 700; color: #1e3a8a; margin-bottom: 8px;">Processing System Query & Executing Multi-Source Pipeline...</div>
                    <div style="font-size: 13px; color: #475569; line-height: 1.6;">
                        • Intent Classification ... Complete<br>
                        • Generating Execution Plan ... Complete<br>
                        • Querying Enterprise Knowledge Graph ... Complete<br>
                        • Analyzing Telemetry Sensors & Anomalies ... Complete<br>
                        • Performing Vector RAG Document Search ... Complete<br>
                        • Synthesizing Operational Assessment ... Complete
                    </div>
                </div>
                """,
                unsafe_allow_html=True
            )

        try:
            # Process query end-to-end with fresh orchestrator
            response: OrchestratorResponse = orchestrator.process_query(user_query)
            st.session_state["latest_response"] = response

            # Clear progress placeholder to render final output cleanly
            progress_placeholder.empty()

            # 1. Primary Operational Assessment Card
            render_ai_diagnosis(response)

            # 2. Supporting Evidence Dashboard (Plotly Charts, Asset Topology, Alarms, Documents)
            render_evidence_section(response)

            # 3. Collapsible Technical Execution Panel
            render_execution_details(response)

        except Exception as e:
            progress_placeholder.empty()
            st.error(f"An error occurred while executing the query: {e}")
        finally:
            try:
                orchestrator.graph_client.close()
            except Exception:
                pass


if __name__ == "__main__":
    main()
