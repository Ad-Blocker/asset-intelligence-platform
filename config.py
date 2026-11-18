"""
Configuration Module for Asset Intelligence Platform.

Handles environment variable loading, default fallback values,
and global application settings using dataclasses and python-dotenv.
"""

import os
from dataclasses import dataclass
from typing import Optional
from dotenv import load_dotenv

# Load environment variables from .env file if present
load_dotenv()


@dataclass(frozen=True)
class Neo4jConfig:
    """Configuration settings for Neo4j database connection."""
    uri: str = os.getenv("NEO4J_URI", "neo4j://127.0.0.1:7687")
    user: str = os.getenv("NEO4J_USER", "neo4j")
    password: str = os.getenv("NEO4J_PASSWORD", "")
    database: str = os.getenv("NEO4J_DATABASE", "neo4j")


@dataclass(frozen=True)
class TelemetryConfig:
    """Configuration settings for historical telemetry data processing."""
    data_dir: str = os.getenv("TELEMETRY_CSV_DIR", "./telemetry/data")


@dataclass(frozen=True)
class DocumentConfig:
    """Configuration settings for technical document RAG store."""
    documents_dir: str = os.getenv("DOCUMENTS_DIR", "./documents/data")


@dataclass(frozen=True)
class LLMConfig:
    """Configuration settings for LLM orchestration."""
    api_key: Optional[str] = os.getenv("OPENAI_API_KEY")
    model_name: str = os.getenv("LLM_MODEL_NAME", "gpt-4o")


@dataclass(frozen=True)
class AppConfig:
    """Centralized application settings container."""
    neo4j: Neo4jConfig = Neo4jConfig()
    telemetry: TelemetryConfig = TelemetryConfig()
    documents: DocumentConfig = DocumentConfig()
    llm: LLMConfig = LLMConfig()
    log_level: str = os.getenv("LOG_LEVEL", "INFO")

    # TODO: Add validation methods for required config values (e.g., API keys, database credentials)
    # TODO: Add support for dynamic environment profiles (development, staging, production)


# Instantiated global configuration instance
config = AppConfig()
