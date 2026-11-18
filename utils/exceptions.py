"""
Custom Exception Classes.

Defines the domain-specific exception hierarchy for the Asset Intelligence Platform.
"""


class AssetIntelligenceException(Exception):
    """Base exception class for all Asset Intelligence Platform errors."""
    pass


class GraphQueryException(AssetIntelligenceException):
    """Raised when errors occur during Neo4j database connection or Cypher execution."""
    pass


class TelemetryException(AssetIntelligenceException):
    """Raised when errors occur during CSV telemetry reading, parsing, or analysis."""
    pass


class DocumentException(AssetIntelligenceException):
    """Raised when errors occur during PDF loading, text extraction, or RAG retrieval."""
    pass


class LLMOrchestratorException(AssetIntelligenceException):
    """Raised when errors occur during multi-source context fusion or LLM prompt processing."""
    pass
