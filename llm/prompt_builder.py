"""
Prompt Builder Module.

Provides the PromptBuilder class responsible for formatting structured outputs
retrieved from Graph, Telemetry, and Document services into a single unified prompt.
"""

from typing import List, Optional
from .models import PromptContext, AssetContext, TelemetryContext, DocumentContext
from utils.logger import setup_logger
from config import config

logger = setup_logger("llm.prompt", config.log_level)


class PromptBuilder:
    """Formatter constructing grounded LLM prompts from multi-source service context."""

    def build_prompt(self, context: PromptContext) -> str:
        """
        Format prompt context into a structured system/user prompt string.

        Args:
            context (PromptContext): Container holding active service contexts.

        Returns:
            str: Complete formatted prompt string.
        """
        sections: List[str] = [
            "You are an AI Asset Intelligence Assistant for an enterprise facility system.",
            "Answer the user's question accurately and concisely using ONLY the supplied context below from the enterprise Knowledge Graph, Telemetry Analytics, and Technical OEM Documentation.",
            "Synthesize relationships, live/historical metrics, anomalies, and maintenance guidelines into a clear explanation where applicable.\n"
        ]

        # 1. Knowledge Graph Section
        if context.graph_context and context.intent.graph:
            g = context.graph_context
            g_lines = ["--- KNOWLEDGE GRAPH CONTEXT ---"]
            if g.asset_info:
                g_lines.append(f"Asset: {g.asset_info.get('name')} (ID: {g.asset_id}, Type: {g.asset_info.get('assetType')})")
            if g.manufacturer:
                g_lines.append(f"Manufacturer (OEM): {g.manufacturer.get('name')}")
            if g.components:
                comp_names = [c.get("name") for c in g.components]
                g_lines.append(f"Components: {', '.join(comp_names)}")
            if g.served_spaces:
                space_names = [s.get("name") for s in g.served_spaces]
                g_lines.append(f"Served Spaces / Zones: {', '.join(space_names)}")
            if g.health_status:
                g_lines.append(f"Health Status: {g.health_status.get('status')} (Score: {g.health_status.get('score')})")
            if g.operating_state:
                g_lines.append(f"Operating State: {g.operating_state.get('name')}")
            if g.maintenance_history:
                latest_m = g.maintenance_history[0]
                g_lines.append(f"Recent Maintenance: {latest_m.get('type')} on '{latest_m.get('serviced_component')}' by technician {latest_m.get('technician_name')} on {latest_m.get('date')} ('{latest_m.get('description')}')")

            sections.append("\n".join(g_lines))

        # 2. Telemetry Section
        if context.telemetry_context and context.intent.telemetry:
            t = context.telemetry_context
            t_lines = ["--- TELEMETRY ANALYTICS CONTEXT ---"]
            if t.latest_readings:
                latest_str = ", ".join([f"{m}: {data.get('value')} (at {data.get('timestamp')})" for m, data in t.latest_readings.items() if data.get('value') is not None])
                t_lines.append(f"Latest Sensor Readings: {latest_str}")
            if t.averages:
                avg_str = ", ".join([f"{m}: {val}" for m, val in t.averages.items()])
                t_lines.append(f"24-Hour Averages: {avg_str}")
            if t.anomalies:
                t_lines.append("Detected Operational Anomalies:")
                for metric, anomaly_list in t.anomalies.items():
                    for a in anomaly_list[:3]:  # Top 3 per metric
                        t_lines.append(f"  • [{metric}] {a.get('reason')} at {a.get('timestamp')}")

            sections.append("\n".join(t_lines))

        # 3. Document RAG Section
        if context.document_context and context.intent.documents:
            d = context.document_context
            d_lines = ["--- TECHNICAL DOCUMENTATION RAG CONTEXT ---"]
            if d.retrieved_chunks:
                for idx, chunk in enumerate(d.retrieved_chunks[:3], 1):
                    doc_name = getattr(chunk, "source_document", "").replace("\\", "/").split("/")[-1]
                    page_num = getattr(chunk, "page_number", "?")
                    score = getattr(chunk, "similarity_score", 0.0)
                    text_snippet = getattr(chunk, "text", "").replace("\n", " ")
                    d_lines.append(f"Passage #{idx} (Page {page_num}, Score: {score:.4f}, Source: {doc_name}):\n  \"{text_snippet}\"")
            else:
                d_lines.append("No matching document passages retrieved.")

            sections.append("\n".join(d_lines))

        # 4. User Question Section
        sections.append(f"User Question: \"{context.user_question}\"")
        sections.append("Response:")

        prompt = "\n\n".join(sections)
        logger.debug("Constructed LLM Prompt (Length: %d characters).", len(prompt))
        return prompt
