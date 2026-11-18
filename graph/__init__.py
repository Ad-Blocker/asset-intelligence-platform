"""
Knowledge Graph Package for Neo4j Interaction.

Provides database connection management and Cypher query templates
for enterprise topology, equipment relationships, and metadata retrieval.
"""

from .neo4j_client import Neo4jClient
from .graph_queries import GraphQueries

__all__ = ["Neo4jClient", "GraphQueries"]
