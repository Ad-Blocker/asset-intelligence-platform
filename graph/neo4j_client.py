"""
Neo4j Client Module.

Manages connection pooling, session lifecycle, and low-level Cypher query execution
against the Neo4j Knowledge Graph database instance using the official Neo4j Python driver.
"""

from typing import Any, Dict, List, Optional
from neo4j import GraphDatabase, Driver, Session
from neo4j.exceptions import Neo4jError, DriverError

from config import Neo4jConfig, config
from utils.logger import setup_logger
from utils.exceptions import GraphQueryException

logger = setup_logger("graph.neo4j_client", config.log_level)


class Neo4jClient:
    """Connection manager and query execution client for Neo4j database."""

    def __init__(self, config_override: Optional[Neo4jConfig] = None) -> None:
        """
        Initialize Neo4j client using global application config or provided configuration.

        Args:
            config_override (Optional[Neo4jConfig]): Optional configuration override.
        """
        cfg = config_override or config.neo4j
        self.uri: str = cfg.uri
        self.user: str = cfg.user
        self.password: str = cfg.password
        self.database: str = cfg.database
        self._driver: Optional[Driver] = None

    def connect(self) -> None:
        """
        Establish driver connection pool to the Neo4j database.

        Raises:
            GraphQueryException: If database connection or driver creation fails.
        """
        if self._driver is not None:
            logger.debug("Neo4j driver connection is already established.")
            return

        try:
            logger.info("Connecting to Neo4j instance at %s (database: %s)...", self.uri, self.database)
            self._driver = GraphDatabase.driver(
                self.uri,
                auth=(self.user, self.password)
            )
            self.verify_connectivity()
            logger.info("Successfully connected and verified Neo4j driver connection.")
        except (Neo4jError, DriverError, Exception) as e:
            self._driver = None
            logger.error("Failed to connect to Neo4j instance at %s: %s", self.uri, e)
            raise GraphQueryException(f"Failed to connect to Neo4j database at {self.uri}: {e}") from e

    def close(self) -> None:
        """Close Neo4j driver connection pool cleanly."""
        if self._driver is not None:
            try:
                self._driver.close()
                logger.info("Neo4j driver connection closed successfully.")
            except Exception as e:
                logger.warning("Error encountered while closing Neo4j driver: %s", e)
            finally:
                self._driver = None

    def verify_connectivity(self) -> bool:
        """
        Verify database connectivity and authorization.

        Returns:
            bool: True if database connection is active and healthy.

        Raises:
            GraphQueryException: If verification fails.
        """
        if self._driver is None:
            raise GraphQueryException("Neo4j driver is not connected. Call connect() first.")

        try:
            self._driver.verify_connectivity()
            return True
        except Exception as e:
            logger.error("Neo4j connectivity verification failed: %s", e)
            raise GraphQueryException(f"Neo4j connectivity check failed: {e}") from e

    def run_query(self, cypher: str, parameters: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """
        Execute a Cypher query against the configured Neo4j database.

        Args:
            cypher (str): Parameterized Cypher query string.
            parameters (Optional[Dict[str, Any]]): Map of query parameter key-value pairs.

        Returns:
            List[Dict[str, Any]]: Query results transformed into a list of record dictionaries.

        Raises:
            GraphQueryException: If driver is not connected or query execution encounters errors.
        """
        if self._driver is None:
            raise GraphQueryException("Neo4j driver is not connected. Call connect() first.")

        params = parameters or {}
        try:
            with self._driver.session(database=self.database) as session:
                result = session.run(cypher, parameters=params)
                records = [record.data() for record in result]
                logger.debug("Query executed successfully. Result count: %d records.", len(records))
                return records
        except Neo4jError as e:
            logger.error("Cypher execution error [Code: %s]: %s | Query: %s", e.code, e.message, cypher)
            raise GraphQueryException(f"Cypher execution failed [{e.code}]: {e.message}") from e
        except Exception as e:
            logger.error("Unexpected error executing Cypher query: %s | Query: %s", e, cypher)
            raise GraphQueryException(f"Unexpected query error: {e}") from e

    def execute_query(self, cypher: str, parameters: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """Alias for run_query for backwards compatibility."""
        return self.run_query(cypher, parameters)

    def __enter__(self: "Neo4jClient") -> "Neo4jClient":
        """Context manager entry point."""
        self.connect()
        return self

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """Context manager exit point ensuring clean connection teardown."""
        self.close()
