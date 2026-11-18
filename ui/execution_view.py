"""
Execution View Component Module.

Renders a collapsible panel containing the ExecutionPlan goal,
Plotly service latency bar chart, and detailed step timing metrics.
"""

import streamlit as st
import pandas as pd
import plotly.express as px
from llm.models import OrchestratorResponse


def render_execution_details(response: OrchestratorResponse) -> None:
    """
    Render collapsible execution plan and latency timing panel.

    Args:
        response (OrchestratorResponse): Complete orchestrator response bundle.
    """
    with st.expander("View Technical Execution Details", expanded=False):
        if response.execution_plan:
            st.markdown(f"<strong>Execution Plan Goal:</strong> <em>{response.execution_plan.goal}</em>", unsafe_allow_html=True)
            st.markdown("<div style='margin-bottom: 12px;'></div>", unsafe_allow_html=True)

            sc_map = {sc.service: sc for sc in response.service_calls}
            table_data = []

            for step in response.execution_plan.steps:
                sc = sc_map.get(step.service_name)
                status_str = "OK" if (sc and sc.success) else "PEND"
                lat_str = f"{sc.execution_time_ms:.1f} ms" if sc else "N/A"
                rec_str = str(sc.records_returned) if sc else "0"

                table_data.append({
                    "Step ID": step.step_id,
                    "Service Target": step.service_name,
                    "Status": status_str,
                    "Latency": lat_str,
                    "Records Returned": rec_str,
                    "Action": step.action
                })

            df_plan = pd.DataFrame(table_data)
            st.dataframe(df_plan, use_container_width=True, hide_index=True)

        st.markdown("<hr style='border-color: #e2e8f0; margin: 16px 0;'>", unsafe_allow_html=True)
        st.markdown("<div class='prop-label' style='margin-bottom: 8px;'>Service Latency Breakdown (Plotly Visualization)</div>", unsafe_allow_html=True)

        # Plotly Horizontal Bar Chart of Service Execution Latencies
        if response.service_calls:
            df_latency = pd.DataFrame([
                {"Service": sc.service, "Latency (ms)": sc.execution_time_ms}
                for sc in response.service_calls
            ])

            fig_lat = px.bar(
                df_latency,
                x="Latency (ms)",
                y="Service",
                orientation="h",
                color="Service",
                color_discrete_sequence=px.colors.qualitative.Bold,
                text_auto=".1f"
            )

            fig_lat.update_layout(
                height=220,
                margin=dict(l=10, r=10, t=10, b=10),
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="#f8fafc",
                showlegend=False,
                font=dict(family="sans-serif", size=11, color="#334155")
            )

            fig_lat.update_xaxes(title_text="Execution Latency (ms)", gridcolor="#e2e8f0")
            fig_lat.update_yaxes(title_text="", gridcolor="#e2e8f0")

            st.plotly_chart(fig_lat, use_container_width=True)

        st.markdown(f"<div style='font-size: 13px; font-weight: 600; color: #475569; margin-top: 8px;'>Total End-to-End Pipeline Execution Time: <strong>{response.total_execution_time_ms:.1f} ms</strong></div>", unsafe_allow_html=True)
