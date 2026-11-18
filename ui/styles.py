"""
Enterprise UI Styles Module.

Provides compact, high-density CSS styles for an industrial operations dashboard.
Eliminates excess whitespace, fixes bullet alignment, and enhances readability.
"""

import streamlit as st


def inject_custom_css() -> None:
    """Inject high-density CSS rules for enterprise software styling."""
    st.markdown("""
        <style>
        /* Global Page Background & Font Settings */
        .stApp {
            background-color: #f8fafc;
            color: #0f172a;
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
        }

        /* Top Header Container */
        .enterprise-header {
            background-color: #ffffff;
            border-bottom: 1px solid #cbd5e1;
            padding: 12px 20px;
            margin-bottom: 16px;
            border-radius: 4px;
        }
        .header-title {
            font-size: 20px;
            font-weight: 700;
            color: #0f172a;
            margin: 0;
            letter-spacing: -0.3px;
        }
        .header-meta {
            font-size: 12px;
            color: #475569;
            margin-top: 2px;
            font-weight: 500;
        }
        .status-badge {
            display: inline-block;
            background-color: #f1f5f9;
            color: #1e293b;
            border: 1px solid #cbd5e1;
            font-size: 11px;
            font-weight: 600;
            padding: 3px 8px;
            border-radius: 3px;
        }

        /* Top KPI Cards */
        .kpi-card {
            background-color: #ffffff;
            border: 1px solid #cbd5e1;
            border-top: 3px solid #1e3a8a;
            border-radius: 4px;
            padding: 10px 14px;
            margin-bottom: 12px;
        }
        .kpi-title {
            font-size: 11px;
            font-weight: 700;
            color: #64748b;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }
        .kpi-value {
            font-size: 18px;
            font-weight: 700;
            color: #0f172a;
            margin-top: 2px;
        }
        .kpi-sub {
            font-size: 11px;
            color: #475569;
            margin-top: 2px;
        }

        /* Sidebar Styling */
        section[data-testid="stSidebar"] {
            background-color: #0f172a;
            color: #f8fafc;
            border-right: 1px solid #1e293b;
        }
        section[data-testid="stSidebar"] .stMarkdown, 
        section[data-testid="stSidebar"] h1, 
        section[data-testid="stSidebar"] h2, 
        section[data-testid="stSidebar"] h3 {
            color: #f8fafc !important;
        }
        .sidebar-status-table {
            width: 100%;
            border-collapse: collapse;
            font-size: 12px;
            margin-bottom: 12px;
        }
        .sidebar-status-table td {
            padding: 6px 0;
            border-bottom: 1px solid #1e293b;
        }
        .badge-connected {
            color: #22c55e;
            font-weight: 600;
            font-size: 11px;
        }
        .badge-ready {
            color: #38bdf8;
            font-weight: 600;
            font-size: 11px;
        }

        /* Primary Operational Assessment Card */
        .summary-card {
            background-color: #ffffff;
            border: 1px solid #cbd5e1;
            border-left: 4px solid #1e3a8a;
            border-radius: 4px;
            padding: 16px 20px;
            margin-bottom: 16px;
            box-shadow: 0 1px 2px 0 rgba(0, 0, 0, 0.03);
        }
        .summary-title {
            font-size: 15px;
            font-weight: 700;
            color: #1e3a8a;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }
        .summary-body {
            font-size: 14px;
            line-height: 1.5;
            color: #0f172a;
            margin-bottom: 12px;
        }
        .summary-body p {
            margin-bottom: 8px !important;
        }
        .summary-body ul, .summary-body ol {
            margin-top: 4px !important;
            margin-bottom: 8px !important;
            padding-left: 20px !important;
        }
        .summary-body li {
            margin-bottom: 4px !important;
        }

        /* Evidence Badges */
        .evidence-tag {
            display: inline-block;
            background-color: #eff6ff;
            color: #1d4ed8;
            border: 1px solid #bfdbfe;
            font-size: 11px;
            font-weight: 600;
            padding: 2px 8px;
            border-radius: 3px;
            margin-right: 4px;
        }
        .evidence-tag-inactive {
            display: inline-block;
            background-color: #f1f5f9;
            color: #94a3b8;
            border: 1px solid #e2e8f0;
            font-size: 11px;
            font-weight: 500;
            padding: 2px 8px;
            border-radius: 3px;
            margin-right: 4px;
        }

        /* Evidence Cards */
        .evidence-card {
            background-color: #ffffff;
            border: 1px solid #cbd5e1;
            border-radius: 4px;
            padding: 16px;
            margin-bottom: 16px;
        }
        .evidence-title {
            font-size: 14px;
            font-weight: 700;
            color: #0f172a;
            border-bottom: 1px solid #e2e8f0;
            padding-bottom: 8px;
            margin-bottom: 12px;
        }

        /* Property Labels & Values */
        .prop-label {
            font-size: 10px;
            font-weight: 700;
            color: #64748b;
            text-transform: uppercase;
            letter-spacing: 0.4px;
        }
        .prop-value {
            font-size: 13px;
            font-weight: 500;
            color: #0f172a;
            margin-bottom: 8px;
        }

        /* Status Badges for Alarms */
        .alarm-badge-critical {
            background-color: #fee2e2;
            color: #991b1b;
            border: 1px solid #fca5a5;
            font-weight: 700;
            padding: 2px 6px;
            border-radius: 3px;
            font-size: 10px;
        }
        .alarm-badge-warning {
            background-color: #fef3c7;
            color: #92400e;
            border: 1px solid #fde68a;
            font-weight: 700;
            padding: 2px 6px;
            border-radius: 3px;
            font-size: 10px;
        }
        .alarm-badge-normal {
            background-color: #dcfce7;
            color: #166534;
            border: 1px solid #86efac;
            font-weight: 700;
            padding: 2px 6px;
            border-radius: 3px;
            font-size: 10px;
        }

        /* Streamlit native component tight spacing */
        .block-container {
            padding-top: 1rem !important;
            padding-bottom: 2rem !important;
        }
        div[data-testid="stVerticalBlock"] > div {
            gap: 0.5rem !important;
        }

        /* Buttons Styling */
        div.stButton > button {
            background-color: #ffffff;
            color: #1e293b;
            border: 1px solid #cbd5e1;
            border-radius: 4px;
            font-size: 12px;
            font-weight: 500;
            padding: 4px 10px;
            transition: all 0.15s ease-in-out;
        }
        div.stButton > button:hover {
            background-color: #f1f5f9;
            border-color: #94a3b8;
            color: #0f172a;
        }

        /* Hide Streamlit default header elements */
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        </style>
    """, unsafe_allow_html=True)
