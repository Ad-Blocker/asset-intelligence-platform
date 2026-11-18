"""
Header Component Module.

Renders the top enterprise header displaying platform title, facility, and dashboard classification.
"""

import streamlit as st


def render_header(facility: str = "Bommanahalli Office") -> None:
    """
    Render top application header.

    Args:
        facility (str): Facility name string.
    """
    st.markdown(
        f"""
        <div class="enterprise-header">
            <div style="display: flex; justify-content: space-between; align-items: center;">
                <div>
                    <h1 class="header-title">Asset Intelligence Platform</h1>
                    <div class="header-meta">
                        Facility: <strong>{facility}</strong> &nbsp;|&nbsp; 
                        Enterprise Asset Operations Dashboard
                    </div>
                </div>
                <div>
                    <span class="status-badge">System Status: Connected</span>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )
