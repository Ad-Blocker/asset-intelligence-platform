"""
Telemetry Analysis Module.

Provides analytical calculations, rolling averages, statistical aggregations,
and anomaly detection for telemetry metrics while hiding Pandas DataFrames
behind clean Python native data structures (dicts, floats, lists).
"""

from typing import Any, Dict, List, Optional
import pandas as pd
import numpy as np

from utils.logger import setup_logger
from utils.exceptions import TelemetryException
from config import config

logger = setup_logger("telemetry.analysis", config.log_level)


class TelemetryAnalyzer:
    """Analytical engine encapsulating statistics and anomaly detection over a telemetry stream."""

    def __init__(self, df: pd.DataFrame) -> None:
        """
        Initialize TelemetryAnalyzer with a loaded telemetry DataFrame.

        Args:
            df (pd.DataFrame): Validated telemetry DataFrame containing 'timestamp' and metric columns.

        Raises:
            TelemetryException: If DataFrame is empty or missing 'timestamp'.
        """
        if df.empty or "timestamp" not in df.columns:
            raise TelemetryException("TelemetryAnalyzer requires a non-empty DataFrame with a 'timestamp' column.")

        self._df = df.copy()

    def get_available_metrics(self) -> List[str]:
        """
        Return list of available metric names present in the dataset.

        Returns:
            List[str]: Column names excluding 'timestamp'.
        """
        return [col for col in self._df.columns if col != "timestamp"]

    def _validate_metric(self, metric_name: str) -> None:
        """
        Validate metric existence in the dataset.

        Raises:
            TelemetryException: If metric_name is not present.
        """
        available = self.get_available_metrics()
        if metric_name not in available:
            logger.error("Metric '%s' not found. Available metrics: %s", metric_name, available)
            raise TelemetryException(f"Metric '{metric_name}' not found in telemetry data. Available: {available}")

    def latest_value(self, metric_name: str) -> Dict[str, Any]:
        """
        Get the most recent sensor reading for a metric.

        Args:
            metric_name (str): Target metric column name.

        Returns:
            Dict[str, Any]: Dictionary containing 'timestamp' (ISO string) and 'value'.
        """
        self._validate_metric(metric_name)
        latest_row = self._df.iloc[-1]
        val = float(latest_row[metric_name]) if pd.notnull(latest_row[metric_name]) else None
        ts = latest_row["timestamp"].isoformat() if hasattr(latest_row["timestamp"], "isoformat") else str(latest_row["timestamp"])
        logger.debug("Latest value for '%s': %s at %s", metric_name, val, ts)
        return {"timestamp": ts, "value": val}

    def average(self, metric_name: str) -> float:
        """
        Calculate the mean value of a metric across the entire dataset.

        Args:
            metric_name (str): Target metric column name.

        Returns:
            float: Arithmetic mean rounded to 2 decimal places.
        """
        self._validate_metric(metric_name)
        mean_val = float(self._df[metric_name].mean())
        logger.debug("Average for '%s': %.2f", metric_name, mean_val)
        return round(mean_val, 2)

    def minimum(self, metric_name: str) -> Dict[str, Any]:
        """
        Get the minimum sensor reading and timestamp for a metric.

        Args:
            metric_name (str): Target metric column name.

        Returns:
            Dict[str, Any]: Dictionary containing 'timestamp' and 'value'.
        """
        self._validate_metric(metric_name)
        min_idx = self._df[metric_name].idxmin()
        row = self._df.loc[min_idx]
        val = float(row[metric_name])
        ts = row["timestamp"].isoformat() if hasattr(row["timestamp"], "isoformat") else str(row["timestamp"])
        return {"timestamp": ts, "value": round(val, 2)}

    def maximum(self, metric_name: str) -> Dict[str, Any]:
        """
        Get the maximum sensor reading and timestamp for a metric.

        Args:
            metric_name (str): Target metric column name.

        Returns:
            Dict[str, Any]: Dictionary containing 'timestamp' and 'value'.
        """
        self._validate_metric(metric_name)
        max_idx = self._df[metric_name].idxmax()
        row = self._df.loc[max_idx]
        val = float(row[metric_name])
        ts = row["timestamp"].isoformat() if hasattr(row["timestamp"], "isoformat") else str(row["timestamp"])
        return {"timestamp": ts, "value": round(val, 2)}

    def statistics(self, metric_name: str) -> Dict[str, float]:
        """
        Compute summary statistics (min, max, average, median, std, count) for a metric.

        Args:
            metric_name (str): Target metric column name.

        Returns:
            Dict[str, float]: Summary statistics map.
        """
        self._validate_metric(metric_name)
        series = self._df[metric_name].dropna()
        stats = {
            "count": int(series.count()),
            "average": round(float(series.mean()), 2),
            "minimum": round(float(series.min()), 2),
            "maximum": round(float(series.max()), 2),
            "median": round(float(series.median()), 2),
            "std_dev": round(float(series.std()), 2)
        }
        logger.debug("Computed statistics for '%s': %s", metric_name, stats)
        return stats

    def between(self, metric_name: str, start_time: str, end_time: str) -> List[Dict[str, Any]]:
        """
        Filter metric readings within a specific time interval.

        Args:
            metric_name (str): Target metric column name.
            start_time (str): ISO-formatted start timestamp string.
            end_time (str): ISO-formatted end timestamp string.

        Returns:
            List[Dict[str, Any]]: List of timestamp-value reading dictionaries.
        """
        self._validate_metric(metric_name)
        try:
            start_dt = pd.to_datetime(start_time)
            end_dt = pd.to_datetime(end_time)
        except Exception as e:
            raise TelemetryException(f"Invalid timestamp boundary '{start_time}' or '{end_time}': {e}") from e

        filtered = self._df[(self._df["timestamp"] >= start_dt) & (self._df["timestamp"] <= end_dt)]
        results = []
        for _, row in filtered.iterrows():
            ts = row["timestamp"].isoformat() if hasattr(row["timestamp"], "isoformat") else str(row["timestamp"])
            results.append({"timestamp": ts, "value": round(float(row[metric_name]), 2)})
        return results

    def last(self, metric_name: str, hours: float = 1.0) -> List[Dict[str, Any]]:
        """
        Retrieve readings for the last N hours relative to the latest available timestamp.

        Args:
            metric_name (str): Target metric column name.
            hours (float): Duration in hours.

        Returns:
            List[Dict[str, Any]]: Readings during the specified recent window.
        """
        self._validate_metric(metric_name)
        latest_ts = self._df["timestamp"].max()
        cutoff_ts = latest_ts - pd.Timedelta(hours=hours)

        filtered = self._df[self._df["timestamp"] >= cutoff_ts]
        results = []
        for _, row in filtered.iterrows():
            ts = row["timestamp"].isoformat() if hasattr(row["timestamp"], "isoformat") else str(row["timestamp"])
            results.append({"timestamp": ts, "value": round(float(row[metric_name]), 2)})
        return results

    def moving_average(self, metric_name: str, window: int = 5) -> List[Dict[str, Any]]:
        """
        Calculate rolling moving average for a metric over a window size.

        Args:
            metric_name (str): Target metric column name.
            window (int): Rolling window size in samples.

        Returns:
            List[Dict[str, Any]]: List of dictionaries containing 'timestamp' and 'moving_avg'.
        """
        self._validate_metric(metric_name)
        rolling = self._df[metric_name].rolling(window=window, min_periods=1).mean()
        results = []
        for i, row in self._df.iterrows():
            ts = row["timestamp"].isoformat() if hasattr(row["timestamp"], "isoformat") else str(row["timestamp"])
            results.append({"timestamp": ts, "moving_avg": round(float(rolling.iloc[i]), 2)})
        return results

    def detect_simple_anomalies(self, metric_name: str, z_threshold: float = 2.5) -> List[Dict[str, Any]]:
        """
        Detect sensor reading anomalies using Z-score statistical thresholding.

        Args:
            metric_name (str): Target metric column name.
            z_threshold (float): Z-score cutoff limit (default: 2.5 std devs).

        Returns:
            List[Dict[str, Any]]: List of detected anomaly dictionaries with metric details.
        """
        self._validate_metric(metric_name)
        series = self._df[metric_name]
        mean_val = series.mean()
        std_val = series.std()

        if std_val == 0:
            return []

        z_scores = (series - mean_val) / std_val
        anomaly_mask = np.abs(z_scores) >= z_threshold
        anomalies_df = self._df[anomaly_mask]

        anomalies = []
        for idx, row in anomalies_df.iterrows():
            val = float(row[metric_name])
            zs = float(z_scores.iloc[idx])
            ts = row["timestamp"].isoformat() if hasattr(row["timestamp"], "isoformat") else str(row["timestamp"])

            direction = "HIGH" if zs > 0 else "LOW"
            reason = f"Value {val} is {abs(zs):.2f} standard deviations {direction}er than mean ({mean_val:.2f})"

            anomalies.append({
                "timestamp": ts,
                "metric": metric_name,
                "value": round(val, 2),
                "z_score": round(zs, 2),
                "mean": round(float(mean_val), 2),
                "std_dev": round(float(std_val), 2),
                "reason": reason
            })

        logger.info("Detected %d anomaly samples for '%s' (threshold: %.1f z-score).", len(anomalies), metric_name, z_threshold)
        return anomalies
