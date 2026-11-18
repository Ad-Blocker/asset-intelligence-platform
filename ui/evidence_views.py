"""
Evidence Views Component Module.

Renders visual enterprise evidence panels:
1. Knowledge Graph Summary & Asset Overview
2. Telemetry Analytics with Plotly Interactive Charts & Anomaly Markers
3. Active Alarm Summary Panel
4. Technical Documentation OEM Passages (Full Width)
Formated with tight padding and clean DOM structures.
"""

from typing import Any, Dict, List, Optional
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from llm.models import OrchestratorResponse, AssetContext, TelemetryContext, DocumentContext


def render_asset_overview(graph_ctx: Optional[AssetContext]) -> None:
    """Render Asset Overview & Knowledge Graph Relationships panel."""
    with st.container(border=True):
        st.markdown("<div style='font-size: 14px; font-weight: 700; color: #0f172a; border-bottom: 1px solid #e2e8f0; padding-bottom: 6px; margin-bottom: 12px;'>Asset Overview & Knowledge Graph Topology</div>", unsafe_allow_html=True)

        if graph_ctx:
            col1, col2 = st.columns(2)

            with col1:
                st.markdown("<div class='prop-label'>Current Asset</div>", unsafe_allow_html=True)
                a_name = graph_ctx.asset_info.get("name", graph_ctx.asset_id) if graph_ctx.asset_info else "AHU-01"
                a_type = graph_ctx.asset_info.get("assetType", "Air Handling Unit") if graph_ctx.asset_info else "Air Handling Unit"
                st.markdown(f"<div class='prop-value'><strong>{a_name}</strong> ({graph_ctx.asset_id})<br><span style='font-size:11px; color:#64748b;'>{a_type}</span></div>", unsafe_allow_html=True)

                st.markdown("<div class='prop-label'>Manufacturer (OEM)</div>", unsafe_allow_html=True)
                m_name = graph_ctx.manufacturer.get("name", "Carrier") if graph_ctx.manufacturer else "Carrier"
                st.markdown(f"<div class='prop-value'>{m_name}</div>", unsafe_allow_html=True)

                st.markdown("<div class='prop-label'>Conditioned Spaces / Zones</div>", unsafe_allow_html=True)
                space_names = [s.get("name") for s in graph_ctx.served_spaces] if graph_ctx.served_spaces else ["Conference Room A", "Reception", "Open Workspace"]
                st.markdown(f"<div class='prop-value'>{', '.join(space_names)}</div>", unsafe_allow_html=True)

                st.markdown("<div class='prop-label'>Warranty & Lifecycle</div>", unsafe_allow_html=True)
                st.markdown("<div class='prop-value'>Active 5-Year OEM Warranty</div>", unsafe_allow_html=True)

            with col2:
                st.markdown("<div class='prop-label'>Health Condition</div>", unsafe_allow_html=True)
                h_status = graph_ctx.health_status.get("status", "Healthy") if graph_ctx.health_status else "Healthy"
                h_score = graph_ctx.health_status.get("score", 100) if graph_ctx.health_status else 100
                st.markdown(f"<div class='prop-value'><span style='color:#166534; font-weight:700;'>{h_status}</span> ({h_score}/100)</div>", unsafe_allow_html=True)

                st.markdown("<div class='prop-label'>Operating State</div>", unsafe_allow_html=True)
                st_name = graph_ctx.operating_state.get("name", "Running") if graph_ctx.operating_state else "Running"
                st.markdown(f"<div class='prop-value'>{st_name}</div>", unsafe_allow_html=True)

                st.markdown("<div class='prop-label'>Sub-Assembly Components</div>", unsafe_allow_html=True)
                comp_names = [c.get("name") for c in graph_ctx.components] if graph_ctx.components else ["Mixing Box", "Filter Section", "Cooling Coil", "Heating Coil", "Supply Fan"]
                st.markdown(f"<div class='prop-value'>{', '.join(comp_names)}</div>", unsafe_allow_html=True)

            if graph_ctx.maintenance_history:
                latest_m = graph_ctx.maintenance_history[0]
                st.markdown("<hr style='border-color: #f1f5f9; margin: 6px 0 8px 0;'>", unsafe_allow_html=True)
                st.markdown("<div class='prop-label'>Recent Maintenance Log</div>", unsafe_allow_html=True)
                st.markdown(
                    f"<div class='prop-value' style='font-size:12px;'>{latest_m.get('type')} on <strong>{latest_m.get('serviced_component')}</strong> "
                    f"by {latest_m.get('technician_name')} ({latest_m.get('date')}) — <em>{latest_m.get('description')}</em></div>",
                    unsafe_allow_html=True
                )
        else:
            st.markdown(
                """
                <div style="font-size: 12px; color: #64748b;">
                    <strong>Asset Target: AHU-01</strong> (Carrier Custom Air Handling Unit)<br>
                    Health Grade: Optimal (100/100) | State: Running | Facility: Bommanahalli Office
                </div>
                """,
                unsafe_allow_html=True
            )


def render_telemetry_analytics(telemetry_ctx: Optional[TelemetryContext]) -> None:
    """Render Telemetry Analytics panel with Plotly interactive charts and active alarm summary."""
    with st.container(border=True):
        st.markdown("<div style='font-size: 14px; font-weight: 700; color: #0f172a; border-bottom: 1px solid #e2e8f0; padding-bottom: 6px; margin-bottom: 12px;'>Telemetry Analytics & Interactive Sensor Curves</div>", unsafe_allow_html=True)

        # 1. Active Alarm Summary Panel
        st.markdown(
            """
            <div style="background-color: #f8fafc; border: 1px solid #cbd5e1; padding: 8px 12px; border-radius: 4px; margin-bottom: 12px;">
                <div style="font-size: 11px; font-weight: 700; color: #475569; text-transform: uppercase; margin-bottom: 4px;">Active Sensor Alarms & Status Badges</div>
                <div style="display: flex; gap: 12px; flex-wrap: wrap; font-size: 12px;">
                    <div>Supply Air Temp: <span class="alarm-badge-critical">HIGH TEMP SPIKE (21.71 °C)</span></div>
                    <div>Filter Pressure: <span class="alarm-badge-warning">HIGH RESTRICTION (178.5 Pa)</span></div>
                    <div>Fan Speed: <span class="alarm-badge-normal">NORMAL (1490 RPM)</span></div>
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

        # 2. Key Metrics Summary Row
        if telemetry_ctx and telemetry_ctx.latest_readings:
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                sat = telemetry_ctx.latest_readings.get("supply_air_temperature", {}).get("value", 15.58)
                st.metric(label="Supply Air Temp", value=f"{sat} °C", delta=f"Avg: {telemetry_ctx.averages.get('supply_air_temperature', 15.56)} °C")
            with col2:
                ret = telemetry_ctx.latest_readings.get("return_air_temperature", {}).get("value", 22.40)
                st.metric(label="Return Air Temp", value=f"{ret} °C", delta=f"Avg: {telemetry_ctx.averages.get('return_air_temperature', 23.20)} °C")
            with col3:
                dp = telemetry_ctx.latest_readings.get("filter_pressure_drop", {}).get("value", 98.9)
                st.metric(label="Filter Pressure Drop", value=f"{dp} Pa", delta=f"Avg: {telemetry_ctx.averages.get('filter_pressure_drop', 100.28)} Pa")
            with col4:
                rpm = telemetry_ctx.latest_readings.get("fan_rpm", {}).get("value", 1490.9)
                st.metric(label="Fan Speed", value=f"{rpm} RPM", delta=f"Avg: {telemetry_ctx.averages.get('fan_rpm', 1494.55)} RPM")

        # 3. Interactive Plotly 24-Hour Time-Series Chart
        try:
            df_csv = pd.read_csv("telemetry/sample_ahu_telemetry.csv")
            df_csv["timestamp"] = pd.to_datetime(df_csv["timestamp"])

            fig = make_subplots(specs=[[{"secondary_y": True}]])

            fig.add_trace(
                go.Scatter(
                    x=df_csv["timestamp"],
                    y=df_csv["supply_air_temperature"],
                    name="Supply Air Temp (°C)",
                    line=dict(color="#1e3a8a", width=2)
                ),
                secondary_y=False
            )

            fig.add_trace(
                go.Scatter(
                    x=df_csv["timestamp"],
                    y=df_csv["filter_pressure_drop"],
                    name="Filter Pressure Drop (Pa)",
                    line=dict(color="#d97706", width=2, dash="dash")
                ),
                secondary_y=True
            )

            # Anomaly markers overlay
            anom_sat = df_csv[df_csv["supply_air_temperature"] > 18.0]
            if not anom_sat.empty:
                fig.add_trace(
                    go.Scatter(
                        x=anom_sat["timestamp"],
                        y=anom_sat["supply_air_temperature"],
                        mode="markers",
                        name="Temp Spike Anomaly",
                        marker=dict(color="#dc2626", size=8, symbol="diamond")
                    ),
                    secondary_y=False
                )

            fig.update_layout(
                height=260,
                margin=dict(l=10, r=10, t=20, b=10),
                legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="#f8fafc",
                font=dict(family="sans-serif", size=10, color="#334155")
            )

            fig.update_xaxes(title_text="Timestamp (24h Window)", gridcolor="#e2e8f0")
            fig.update_yaxes(title_text="Supply Air Temp (°C)", secondary_y=False, gridcolor="#e2e8f0")
            fig.update_yaxes(title_text="Pressure Drop (Pa)", secondary_y=True, showgrid=False)

            st.plotly_chart(fig, use_container_width=True)

        except Exception:
            pass


def render_technical_documentation(doc_ctx: Optional[DocumentContext]) -> None:
    """Render full-width Technical Documentation panel displaying extracted OEM passages."""
    with st.container(border=True):
        st.markdown("<div style='font-size: 14px; font-weight: 700; color: #0f172a; border-bottom: 1px solid #e2e8f0; padding-bottom: 6px; margin-bottom: 12px;'>Technical Documentation (OEM Carrier Operation Manual Form 39M-22PD)</div>", unsafe_allow_html=True)

        if doc_ctx and doc_ctx.retrieved_chunks:
            for idx, chunk in enumerate(doc_ctx.retrieved_chunks[:3], 1):
                doc_name = getattr(chunk, "source_document", "39M-22PD.pdf").replace("\\", "/").split("/")[-1]
                page_num = getattr(chunk, "page_number", 1)
                score = getattr(chunk, "similarity_score", 0.0)
                text_snippet = getattr(chunk, "text", "").strip()

                st.markdown(
                    f"""
                    <div style="background-color: #f8fafc; border: 1px solid #e2e8f0; border-left: 3px solid #2563eb; padding: 10px 14px; border-radius: 4px; margin-bottom: 8px;">
                        <div style="display: flex; justify-content: space-between; font-size: 11px; font-weight: 600; color: #475569; margin-bottom: 4px;">
                            <span>OEM Evidence Passage #{idx} — Document: <strong>{doc_name}</strong> (Page {page_num})</span>
                            <span>Vector Similarity Score: {score:.4f}</span>
                        </div>
                        <div style="font-size: 12px; line-height: 1.5; color: #0f172a;">"{text_snippet}"</div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )
        else:
            st.info("No technical document passages retrieved for this query context.")


def render_evidence_section(response: OrchestratorResponse) -> None:
    """
    Render adaptive evidence dashboard layout without empty containers.

    Row 1 (2 Columns): Asset Overview & Telemetry Analytics
    Row 2 (Full Width): Technical Documentation
    """
    st.markdown("<h3 style='font-size: 16px; font-weight: 700; color: #0f172a; margin-top: 12px; margin-bottom: 10px;'>Supporting Evidence Dashboard</h3>", unsafe_allow_html=True)

    has_graph = response.intent.graph
    has_telemetry = response.intent.telemetry
    has_docs = response.intent.documents

    # Row 1: 2 Columns for Asset Overview and Telemetry Analytics
    if has_graph and has_telemetry:
        col1, col2 = st.columns(2)
        with col1:
            render_asset_overview(response.graph_context)
        with col2:
            render_telemetry_analytics(response.telemetry_context)
    elif has_graph:
        render_asset_overview(response.graph_context)
    elif has_telemetry:
        render_telemetry_analytics(response.telemetry_context)
    else:
        render_asset_overview(response.graph_context)

    # Row 2: Full Width for Technical Documentation
    if has_docs:
        render_technical_documentation(response.document_context)
