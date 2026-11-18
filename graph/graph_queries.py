"""
Graph Queries Module.

Encapsulates all domain Cypher queries matching the project ontology.
Provides clean query abstraction methods for assets, components, spaces, health,
operating states, OEMs, documents, telemetry streams, and maintenance history.
"""

from typing import Any, Dict, List, Optional
from .neo4j_client import Neo4jClient
from utils.logger import setup_logger
from config import config

logger = setup_logger("graph.graph_queries", config.log_level)


class GraphQueries:
    """Encapsulates parameterized Cypher queries for the Knowledge Graph ontology."""

    def __init__(self, client: Neo4jClient) -> None:
        """
        Initialize GraphQueries wrapper with an active Neo4jClient instance.

        Args:
            client (Neo4jClient): Connected Neo4j database client.
        """
        self.client = client

    def get_asset(self, asset_id: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve core properties of an Asset node by its ID or Name.

        Args:
            asset_id (str): Asset unique identifier or name (e.g., 'AHU-01' or 'AHU001').

        Returns:
            Optional[Dict[str, Any]]: Asset node properties, or None if not found.
        """
        cypher = """
        MATCH (a:Asset)
        WHERE a.id = $asset_id OR a.name = $asset_id
        RETURN a {.*} AS asset
        """
        results = self.client.run_query(cypher, {"asset_id": asset_id})
        if results and "asset" in results[0]:
            return results[0]["asset"]
        return None

    def get_components(self, asset_id: str) -> List[Dict[str, Any]]:
        """
        Retrieve sub-assembly components belonging to an asset.

        Args:
            asset_id (str): Asset unique identifier or name.

        Returns:
            List[Dict[str, Any]]: List of Component node property maps.
        """
        cypher = """
        MATCH (a:Asset)-[:HAS_COMPONENT]->(c:Component)
        WHERE a.id = $asset_id OR a.name = $asset_id
        RETURN c {.*} AS component
        ORDER BY c.name
        """
        results = self.client.run_query(cypher, {"asset_id": asset_id})
        return [record["component"] for record in results if "component" in record]

    def get_served_spaces(self, asset_id: str) -> List[Dict[str, Any]]:
        """
        Retrieve physical spaces or zones conditioned/served by an asset.

        Args:
            asset_id (str): Asset unique identifier or name.

        Returns:
            List[Dict[str, Any]]: List of Space node property maps.
        """
        cypher = """
        MATCH (a:Asset)-[:SERVES]->(sp:Space)
        WHERE a.id = $asset_id OR a.name = $asset_id
        RETURN sp {.*} AS space
        ORDER BY sp.name
        """
        results = self.client.run_query(cypher, {"asset_id": asset_id})
        return [record["space"] for record in results if "space" in record]

    def get_health_status(self, asset_id: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve dynamic health status or condition score associated with an asset.

        Args:
            asset_id (str): Asset unique identifier or name.

        Returns:
            Optional[Dict[str, Any]]: HealthStatus node properties, or None if not found.
        """
        cypher = """
        MATCH (a:Asset)-[:HAS_HEALTH]->(h:HealthStatus)
        WHERE a.id = $asset_id OR a.name = $asset_id
        RETURN h {.*} AS health_status
        """
        results = self.client.run_query(cypher, {"asset_id": asset_id})
        if results and "health_status" in results[0]:
            return results[0]["health_status"]
        return None

    def get_operating_state(self, asset_id: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve current runtime operating state of an asset.

        Args:
            asset_id (str): Asset unique identifier or name.

        Returns:
            Optional[Dict[str, Any]]: OperatingState node properties, or None if not found.
        """
        cypher = """
        MATCH (a:Asset)-[:HAS_STATE]->(st:OperatingState)
        WHERE a.id = $asset_id OR a.name = $asset_id
        RETURN st {.*} AS operating_state
        """
        results = self.client.run_query(cypher, {"asset_id": asset_id})
        if results and "operating_state" in results[0]:
            return results[0]["operating_state"]
        return None

    def get_manufacturer(self, asset_id: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve Original Equipment Manufacturer (OEM) of an asset.

        Args:
            asset_id (str): Asset unique identifier or name.

        Returns:
            Optional[Dict[str, Any]]: Manufacturer node properties, or None if not found.
        """
        cypher = """
        MATCH (a:Asset)-[:MANUFACTURED_BY]->(m:Manufacturer)
        WHERE a.id = $asset_id OR a.name = $asset_id
        RETURN m {.*} AS manufacturer
        """
        results = self.client.run_query(cypher, {"asset_id": asset_id})
        if results and "manufacturer" in results[0]:
            return results[0]["manufacturer"]
        return None

    def get_documents(self, asset_id: str) -> List[Dict[str, Any]]:
        """
        Retrieve technical manuals, schematics, and document references for an asset.

        Args:
            asset_id (str): Asset unique identifier or name.

        Returns:
            List[Dict[str, Any]]: List of Document metadata dictionaries.
        """
        cypher = """
        MATCH (a:Asset)-[:HAS_DOCUMENT]->(doc:Document)
        WHERE a.id = $asset_id OR a.name = $asset_id
        RETURN doc {.*} AS document
        ORDER BY doc.id
        """
        results = self.client.run_query(cypher, {"asset_id": asset_id})
        return [record["document"] for record in results if "document" in record]

    def get_telemetry_streams(self, asset_id: str) -> List[Dict[str, Any]]:
        """
        Retrieve CSV telemetry metadata streams associated with an asset or its components.

        Args:
            asset_id (str): Asset unique identifier or name.

        Returns:
            List[Dict[str, Any]]: List of TelemetryStream metadata maps containing file_path.
        """
        cypher = """
        MATCH (a:Asset)
        WHERE a.id = $asset_id OR a.name = $asset_id
        OPTIONAL MATCH (a)-[:HAS_SENSOR]->(s1:Sensor)-[:MEASURES]->(ts1:TelemetryStream)
        OPTIONAL MATCH (a)-[:HAS_COMPONENT]->(c:Component)-[:HAS_SENSOR]->(s2:Sensor)-[:MEASURES]->(ts2:TelemetryStream)
        WITH coalesce(s1, s2) AS sensor, coalesce(ts1, ts2) AS stream, coalesce(c.name, a.name) AS attached_to
        WHERE stream IS NOT NULL
        RETURN DISTINCT stream {.*, sensor_name: sensor.name, attached_to: attached_to} AS telemetry_stream
        """
        results = self.client.run_query(cypher, {"asset_id": asset_id})
        return [record["telemetry_stream"] for record in results if "telemetry_stream" in record]

    def get_maintenance_history(self, asset_id: str) -> List[Dict[str, Any]]:
        """
        Retrieve component-level maintenance history and performing technician info.

        Args:
            asset_id (str): Asset unique identifier or name.

        Returns:
            List[Dict[str, Any]]: List of maintenance records with serviced components and technicians.
        """
        cypher = """
        MATCH (a:Asset)-[:HAS_MAINTENANCE]->(mr:MaintenanceRecord)
        WHERE a.id = $asset_id OR a.name = $asset_id
        OPTIONAL MATCH (mr)-[:SERVICED]->(c:Component)
        OPTIONAL MATCH (mr)-[:PERFORMED_BY]->(tech:Technician)
        RETURN mr {.*, serviced_component: c.name, technician_name: tech.name} AS maintenance_record
        ORDER BY mr.date DESC
        """
        results = self.client.run_query(cypher, {"asset_id": asset_id})
        return [record["maintenance_record"] for record in results if "maintenance_record" in record]
