# Telemetry Dataset Specification & Anomaly Catalog

**Dataset File:** `telemetry/sample_ahu_telemetry.csv`  
**Target Asset:** Air Handling Unit `AHU-01`  
**Time Range:** `2026-07-27T00:00:00` to `2026-07-27T23:55:00` (24 Hours)  
**Sampling Frequency:** 5-minute intervals (288 rows total)  
**System Source:** Building Management System (BMS) Sensor Stream  

---

## 1. Column Specifications

| # | Column Name | Engineering Unit | Typical Operating Range | Description |
|---|-------------|------------------|-------------------------|-------------|
| 1 | `timestamp` | ISO 8601 String | `YYYY-MM-DDTHH:MM:SS` | Date and time of sensor sample. |
| 2 | `supply_air_temperature` | Celsius (°C) | 14.0 – 17.0 °C | Temperature of conditioned air delivered to building spaces. |
| 3 | `return_air_temperature` | Celsius (°C) | 22.0 – 25.0 °C | Temperature of air extracted from served zones back to the AHU. |
| 4 | `humidity` | Percentage (%) | 40.0 – 60.0 % | Relative humidity percentage of supply air stream. |
| 5 | `fan_rpm` | RPM | 1450 – 1550 RPM | Rotational speed of the primary Supply Fan. |
| 6 | `energy_consumption` | Kilowatt-hours (kWh) | 15.0 – 22.0 kWh | Electrical power consumption rate of the AHU assembly. |
| 7 | `filter_pressure_drop` | Pascals (Pa) | 80.0 – 120.0 Pa | Differential air pressure across the Filter Section assembly. |

---

## 2. Injected Operational Anomalies

To evaluate anomaly detection algorithms and power the multi-source LLM Orchestrator, **4 realistic operational anomalies** have been injected into the dataset.

```
Metric Thresholds & Anomaly Spikes
──────────────────────────────────────────────────────────────────────────────────────────
08:30 – 08:55  │  Supply Air Temp Spike       (15.5°C ──► 21.71°C Peak ──► 16.0°C)
11:15 – 11:35  │  Supply Fan RPM Drop          (1500 RPM ──► 911.5 RPM Drop ──► 1500 RPM)
14:00 – 14:55  │  Filter Pressure Restriction  (98 Pa ──► 178.5 Pa Peak ──► 100 Pa)
17:40 – 17:55  │  Humidity Excursion           (48% ──► 71.61% Excursion ──► 50%)
──────────────────────────────────────────────────────────────────────────────────────────
```

### 2.1 Anomaly Scenario 1: Chilled Water Valve Failure / Temp Spike
* **Affected Metric**: `supply_air_temperature`
* **Time Interval**: `2026-07-27T08:30:00` to `2026-07-27T08:55:00` (~30 minutes)
* **Baseline Value**: ~15.5 °C
* **Peak Value**: **21.71 °C** at `08:45:00`
* **Operational Cause**: Temporary failure or hunting of the cooling coil control valve under morning peak load.

### 2.2 Anomaly Scenario 2: Supply Fan Belt Slip / Speed Drop
* **Affected Metric**: `fan_rpm`
* **Time Interval**: `2026-07-27T11:15:00` to `2026-07-27T11:35:00` (~20 minutes)
* **Baseline Value**: ~1500 RPM
* **Lowest Value**: **911.5 RPM** at `11:20:00`
* **Operational Cause**: Temporary VFD fault or drive belt slippage before automatic recovery.

### 2.3 Anomaly Scenario 3: Filter Clogging & Differential Pressure Spike
* **Affected Metric**: `filter_pressure_drop`
* **Time Interval**: `2026-07-27T14:00:00` to `2026-07-27T14:55:00` (~55 minutes)
* **Baseline Value**: ~98.0 Pa
* **Peak Value**: **178.5 Pa** at `14:35:00`
* **Operational Cause**: High particulate loading across the Filter Section causing restriction before pressure relief.

### 2.4 Anomaly Scenario 4: Humidifier Overshoot / Excursion
* **Affected Metric**: `humidity`
* **Time Interval**: `2026-07-27T17:40:00` to `2026-07-27T17:55:00` (~20 minutes)
* **Baseline Value**: ~48.0 %
* **Peak Value**: **71.61 %** at `17:50:00`
* **Operational Cause**: Steam humidifier control overshoot during evening zone transition.

---

## 3. Data Integrity & BMS Simulation Characteristics

* **Natural Operational Noise**: Incorporates realistic sensor measurement noise ($\sigma_{temp} \approx 0.15^\circ\text{C}$, $\sigma_{rpm} \approx 4.0\text{ RPM}$, $\sigma_{dp} \approx 1.2\text{ Pa}$).
* **Diurnal Cycles**: Simulates standard daytime load increases between 08:00 and 18:00.
* **ISO 8601 Timestamps**: Formatted as `YYYY-MM-DDTHH:MM:SS` for straightforward Pandas parsing.
