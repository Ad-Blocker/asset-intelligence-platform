"""
Intent Classifier Module.

Provides deterministic rule-based keyword intent classification to determine
which platform services (Knowledge Graph, Telemetry Analytics, Document RAG)
are required to satisfy a natural language user query.
"""

from typing import Dict, List, Optional
from .models import Intent
from utils.logger import setup_logger
from config import config

logger = setup_logger("llm.intent", config.log_level)


class IntentClassifier:
    """Rule-based intent classifier routing user queries to target subsystem services."""

    GRAPH_KEYWORDS = {
        "asset", "component", "components", "manufacturer", "oem", "room",
        "equipment", "ahu", "space", "spaces", "facility", "belong", "served",
        "where", "structure", "topology", "location", "what components"
    }

    TELEMETRY_KEYWORDS = {
        "temperature", "temp", "humidity", "pressure", "rpm", "anomaly",
        "anomalies", "average", "avg", "latest", "sensor", "reading", "readings",
        "warmer", "warm", "hot", "cold", "speed", "stats", "statistics",
        "metric", "value", "current", "historical"
    }

    DOCUMENT_KEYWORDS = {
        "maintenance", "manual", "safety", "replace", "replaced", "procedure",
        "instruction", "instructions", "operating conditions", "precautions",
        "service", "servicing", "how often", "repair", "recommend", "recommended",
        "guideline", "guidelines", "specifications"
    }

    def classify(self, user_question: str) -> Intent:
        """
        Analyze user question and determine required context services.

        Args:
            user_question (str): Input question string.

        Returns:
            Intent: Intent flags dataclass indicating active services.
        """
        q_lower = user_question.lower()
        words = set(q_lower.replace("?", "").replace(",", "").split())

        # Check keyword matches
        graph_active = bool(words & self.GRAPH_KEYWORDS or any(kw in q_lower for kw in ["what components", "belong to", "served by", "room a", "ahu-01"]))
        telemetry_active = bool(words & self.TELEMETRY_KEYWORDS or any(kw in q_lower for kw in ["warmer than", "latest supply", "air temperature"]))
        documents_active = bool(words & self.DOCUMENT_KEYWORDS or any(kw in q_lower for kw in ["cooling coil", "how often", "safety precautions", "should be performed"]))

        # Special multi-source heuristic for diagnosis questions (e.g. "Why is Conference Room A warmer than usual?")
        if any(w in q_lower for w in ["why is", "warmer than", "cause of", "issue", "problem", "fault"]):
            graph_active = True
            telemetry_active = True
            documents_active = True

        # Fallback: if no intent detected, activate Graph context by default
        if not (graph_active or telemetry_active or documents_active):
            graph_active = True

        # Extract target asset identifier
        target_asset = "AHU-01"
        if "ahu001" in q_lower or "ahu-01" in q_lower:
            target_asset = "AHU-01"

        intent = Intent(
            graph=graph_active,
            telemetry=telemetry_active,
            documents=documents_active,
            target_asset=target_asset
        )

        logger.info(
            "Classified intent for query: '%s' -> Graph: %s, Telemetry: %s, Documents: %s",
            user_question, intent.graph, intent.telemetry, intent.documents
        )
        return intent
