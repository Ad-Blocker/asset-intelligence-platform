"""
Sidebar Component Module.

Renders System Services status badges and simplified Project Statistics in the left sidebar.
"""

import streamlit as st


def render_sidebar() -> None:
    """Render sidebar services status badges and project statistics."""
    with st.sidebar:
        st.markdown("<h3 style='font-size: 16px; font-weight: 700; margin-bottom: 12px; color: #f8fafc;'>Services</h3>", unsafe_allow_html=True)

        st.markdown(
            """
            <table class="sidebar-status-table">
                <tr>
                    <td>Knowledge Graph</td>
                    <td style="text-align: right;" class="badge-connected">Connected</td>
                </tr>
                <tr>
                    <td>Telemetry Engine</td>
                    <td style="text-align: right;" class="badge-connected">Connected</td>
                </tr>
                <tr>
                    <td>Document Index</td>
                    <td style="text-align: right;" class="badge-connected">Connected</td>
                </tr>
                <tr>
                    <td>AI Orchestrator</td>
                    <td style="text-align: right;" class="badge-ready">Ready</td>
                </tr>
            </table>
            """,
            unsafe_allow_html=True
        )

        st.markdown("<hr style='border-color: #334155; margin: 20px 0 16px 0;'>", unsafe_allow_html=True)
        st.markdown("<h3 style='font-size: 16px; font-weight: 700; margin-bottom: 12px; color: #f8fafc;'>Project Statistics</h3>", unsafe_allow_html=True)

        stats = [
            ("Knowledge Graph", "35 Nodes, 39 Relationships"),
            ("Telemetry Engine", "288 Records (24h)"),
            ("Documentation", "1 Manual (1,433 Chunks)")
        ]

        for s_name, s_val in stats:
            st.markdown(
                f"""
                <div style="margin-bottom: 12px;">
                    <div style="font-size: 11px; font-weight: 700; color: #94a3b8; text-transform: uppercase;">{s_name}</div>
                    <div style="font-size: 13px; font-weight: 600; color: #f8fafc;">{s_val}</div>
                </div>
                """,
                unsafe_allow_html=True
            )
