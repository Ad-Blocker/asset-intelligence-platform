"""
Analysis Summary Component Module.

Renders the primary Analysis Summary card displaying synthesized operational assessment,
factual evidence coverage indicators, actionable recommendations, and evidence badges.
Formatted for high readability without excessive whitespace.
"""

import re
import streamlit as st
from llm.models import OrchestratorResponse


def format_answer_html(text: str) -> str:
    """Format raw response text into compact, readable HTML."""
    # Split text into paragraphs
    lines = [line.strip() for line in text.split("\n") if line.strip()]

    html_parts = []
    in_list = False

    for line in lines:
        # Numbered or bullet list items
        if re.match(r"^(\d+\.|\u2022|\*|-)\s*", line):
            clean_item = re.sub(r"^(\d+\.|\u2022|\*|-)\s*", "", line)
            # Highlight bold headers
            clean_item = re.sub(r"\*\*(.*?)\*\*", r"<strong>\1</strong>", clean_item)
            if not in_list:
                html_parts.append("<ul style='margin: 6px 0 10px 18px; padding-left: 0; font-size: 14px; line-height: 1.5;'>")
                in_list = True
            html_parts.append(f"<li style='margin-bottom: 4px;'>{clean_item}</li>")
        else:
            if in_list:
                html_parts.append("</ul>")
                in_list = False
            clean_p = re.sub(r"\*\*(.*?)\*\*", r"<strong>\1</strong>", line)
            html_parts.append(f"<p style='margin: 0 0 8px 0; font-size: 14px; line-height: 1.5;'>{clean_p}</p>")

    if in_list:
        html_parts.append("</ul>")

    return "".join(html_parts)


def render_ai_diagnosis(response: OrchestratorResponse) -> None:
    """
    Render primary Analysis Summary card.

    Args:
        response (OrchestratorResponse): Complete orchestrator response bundle.
    """
    active_count = sum([response.intent.graph, response.intent.telemetry, response.intent.documents])
    coverage_str = f"Evidence Coverage: {active_count} of 3 Sources Used"

    # Evidence Tags
    g_tag = "<span class='evidence-tag'>Knowledge Graph</span>" if response.intent.graph else "<span class='evidence-tag-inactive'>Knowledge Graph</span>"
    t_tag = "<span class='evidence-tag'>Telemetry Analytics</span>" if response.intent.telemetry else "<span class='evidence-tag-inactive'>Telemetry Analytics</span>"
    d_tag = "<span class='evidence-tag'>Technical Documentation</span>" if response.intent.documents else "<span class='evidence-tag-inactive'>Technical Documentation</span>"

    formatted_body = format_answer_html(response.final_answer)

    # Recommendation extraction
    rec_text = "Inspect equipment and review operational logs."
    if "filter" in response.final_answer.lower():
        rec_text = "Inspect and clean/replace Filter Section assembly on AHU-01."
    elif "cooling coil" in response.final_answer.lower():
        rec_text = "Inspect cooling coil fins for debris and clean condensate drain pan."

    st.markdown(
        f"""
        <div class="summary-card">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px; border-bottom: 1px solid #e2e8f0; padding-bottom: 8px;">
                <div class="summary-title">Operational Assessment & Synthesis</div>
                <span style="font-size: 12px; font-weight: 600; color: #0369a1; background-color: #e0f2fe; padding: 3px 8px; border-radius: 4px;">{coverage_str}</span>
            </div>
            <div class="summary-body">{formatted_body}</div>
            <div style="background-color: #f8fafc; border: 1px solid #cbd5e1; padding: 10px 14px; border-radius: 4px; display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 8px;">
                <div style="font-size: 13px; color: #0f172a;">
                    <strong style="color: #1e3a8a;">Action Recommendation:</strong> {rec_text}
                </div>
                <div>
                    <span style="font-size: 10px; font-weight: 700; color: #64748b; margin-right: 6px; text-transform: uppercase;">GROUNDING:</span>
                    {g_tag} {t_tag} {d_tag}
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )
