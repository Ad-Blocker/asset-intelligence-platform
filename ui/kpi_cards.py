"""
KPI Cards Component Module.

Renders top KPI metric summary cards for immediate operational awareness.
"""

from typing import Optional
import streamlit as st
from llm.models import OrchestratorResponse


def render_kpi_cards(response: Optional[OrchestratorResponse] = None) -> None:
    """
    Render top KPI cards summary row.

    Args:
        response (Optional[OrchestratorResponse]): Current orchestrator response bundle if available.
    """
    col1, col2, col3, col4 = st.columns(4)

    # Asset Target Card
    with col1:
        st.markdown(
            """
            <div class="kpi-card">
                <div class="kpi-title">Primary Asset</div>
                <div class="kpi-value">AHU-01</div>
                <div class="kpi-sub">Carrier Custom Air Handler</div>
            </div>
            """,
            unsafe_allow_html=True
        )

    # Health Score Card
    with col2:
        st.markdown(
            """
            <div class="kpi-card" style="border-top-color: #166534;">
                <div class="kpi-title">Health Score</div>
                <div class="kpi-value" style="color: #166534;">100 <span style="font-size: 14px; color: #64748b;">/ 100</span></div>
                <div class="kpi-sub">Grade: Optimal / Healthy</div>
            </div>
            """,
            unsafe_allow_html=True
        )

    # Operating State Card
    with col3:
        st.markdown(
            """
            <div class="kpi-card" style="border-top-color: #0284c7;">
                <div class="kpi-title">Operating State</div>
                <div class="kpi-value">Running</div>
                <div class="kpi-sub">Mode: VAV Supply Air</div>
            </div>
            """,
            unsafe_allow_html=True
        )

    # Evidence & Performance Card
    with col4:
        if response:
            active_count = sum([response.intent.graph, response.intent.telemetry, response.intent.documents])
            lat_ms = response.total_execution_time_ms
            st.markdown(
                f"""
                <div class="kpi-card" style="border-top-color: #475569;">
                    <div class="kpi-title">System Performance</div>
                    <div class="kpi-value">{active_count} / 3 <span style="font-size: 13px; color: #64748b;">Sources</span></div>
                    <div class="kpi-sub">Latency: {lat_ms:.1f} ms</div>
                </div>
                """,
                unsafe_allow_html=True
            )
        else:
            st.markdown(
                """
                <div class="kpi-card" style="border-top-color: #475569;">
                    <div class="kpi-title">System Performance</div>
                    <div class="kpi-value">Ready</div>
                    <div class="kpi-sub">Latency: 0.0 ms</div>
                </div>
                """,
                unsafe_allow_html=True
            )
