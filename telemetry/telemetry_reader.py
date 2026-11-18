"""
Telemetry Reader & Service Module.

Provides the TelemetryService class responsible for loading, caching,
and validating CSV telemetry files referenced by the Neo4j Knowledge Graph.
Hides all raw Pandas I/O logic behind a clean interface.
"""

import os
from typing import Dict, List, Optional
import pandas as pd

from config import config
from utils.logger import setup_logger
from utils.exceptions import TelemetryException

logger = setup_logger("telemetry.reader", config.log_level)


class TelemetryService:
    """Service manager for loading, caching, and validating CSV telemetry streams."""

    def __init__(self, base_dir: Optional[str] = None) -> None:
        """
        Initialize TelemetryService with optional base search directory.

        Args:
            base_dir (Optional[str]): Base directory for resolving CSV relative paths.
        """
        self.base_dir = base_dir or config.telemetry.data_dir
        self._cache: Dict[str, pd.DataFrame] = {}

    def resolve_file_path(self, csv_path: str) -> str:
        """
        Resolve relative or absolute CSV file path across common repository locations.

        Args:
            csv_path (str): CSV file path or filename.

        Returns:
            str: Resolved existing absolute or normalized path.

        Raises:
            TelemetryException: If file cannot be found in configured search locations.
        """
        candidate_paths = [
            csv_path,
            os.path.join(self.base_dir, csv_path),
            os.path.join("telemetry", csv_path),
            os.path.join("telemetry", "data", csv_path),
            os.path.join(".", csv_path)
        ]

        for path in candidate_paths:
            if os.path.isfile(path):
                return os.path.abspath(path)

        logger.error("Telemetry CSV file not found: '%s' (searched: %s)", csv_path, candidate_paths)
        raise TelemetryException(f"Telemetry CSV file '{csv_path}' not found on disk.")

    def load_stream(self, csv_path: str) -> pd.DataFrame:
        """
        Load and validate a CSV telemetry file into an internal Pandas DataFrame with caching.

        Args:
            csv_path (str): Relative or absolute CSV file path.

        Returns:
            pd.DataFrame: Validated telemetry DataFrame with parsed timestamp index/column.

        Raises:
            TelemetryException: If file missing, malformed, or missing required 'timestamp' schema.
        """
        resolved_path = self.resolve_file_path(csv_path)

        # Check in-memory cache
        if resolved_path in self._cache:
            logger.info("Telemetry cache hit for '%s'.", resolved_path)
            return self._cache[resolved_path]

        logger.info("Telemetry cache miss for '%s'. Reading CSV from disk...", resolved_path)

        try:
            df = pd.read_csv(resolved_path)

            if df.empty:
                raise TelemetryException(f"Telemetry CSV file '{resolved_path}' is empty.")

            # Schema validation
            if "timestamp" not in df.columns:
                logger.error("Missing required 'timestamp' column in '%s'. Found: %s", resolved_path, df.columns.tolist())
                raise TelemetryException(f"Telemetry CSV '{resolved_path}' missing required 'timestamp' column.")

            # Timestamp parsing validation
            try:
                df["timestamp"] = pd.to_datetime(df["timestamp"])
            except Exception as parse_err:
                logger.error("Malformed timestamp format in '%s': %s", resolved_path, parse_err)
                raise TelemetryException(f"Malformed timestamps in CSV '{resolved_path}': {parse_err}") from parse_err

            # Sort by timestamp chronologically
            df = df.sort_values("timestamp").reset_index(drop=True)

            # Store in cache
            self._cache[resolved_path] = df
            logger.info("Successfully loaded and cached %d telemetry records from '%s'.", len(df), resolved_path)
            return df

        except TelemetryException:
            raise
        except Exception as e:
            logger.error("Failed to read telemetry CSV '%s': %s", resolved_path, e)
            raise TelemetryException(f"Error reading telemetry CSV '{resolved_path}': {e}") from e

    def clear_cache(self) -> None:
        """Clear all cached telemetry DataFrames from memory."""
        count = len(self._cache)
        self._cache.clear()
        logger.info("Telemetry cache cleared (%d entries removed).", count)


# Alias TelemetryReader for backward compatibility
TelemetryReader = TelemetryService
