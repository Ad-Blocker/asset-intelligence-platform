"""
Telemetry Processing Package.

Provides loading, caching, analytical calculation, and anomaly detection functionality
for historical sensor time-series data stored in CSV files.
"""

from .telemetry_reader import TelemetryService, TelemetryReader
from .telemetry_analysis import TelemetryAnalyzer

__all__ = ["TelemetryService", "TelemetryReader", "TelemetryAnalyzer"]
