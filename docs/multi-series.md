
# Multi-Series Forecasting

Multi‑series forecasting in Lumen allows you to run multiple independent time series through the full Lumen pipeline—loading, decomposition, forecasting, diagnostics, plotting—and then optionally combine them using a transparent, deterministic aggregation strategy.

This page explains how multi‑series forecasting works conceptually, how Lumen structures the results, and how to interpret diagnostics and plots across multiple series.

## Why Multi-Series?

Many real‑world forecasting problems involve multiple related streams:

- Work types,
- Product lines,
- Regions,
- Departments, or
- Customer segments.

Lumen treats each series as a first‑class citizen:

- Each series is decomposed independently,
- Each series receives its own diagnostics,
- Each series produces its own forecast, and
- Each series can be plotted individually.

Then, if desired, Lumen aggregates them using a bottom‑up approach.

## How Multi-Series Forecasting Works

The multi-series pipeline mirrors the single-series pipeline, but repeated per series: 

Load $\rightarrow$ Decompose $\rightarrow$ Forecast $\rightarrow$ Diagnose $\rightarrow$ Plot $\rightarrow$ Aggregate $\rightarrow$ Export

### 1. Load Each Series

Each file is loaded independently using the same `DataConfig`.

### 2. Decompose Each Series

Each series is decomposed using LOESS trend extraction, frequency‑aware seasonal indexing, and iterative seasonal refinement.

### 3. Forecast Each Series

Each series uses linear trend extrapolation and repeated seasonal cycle.

### 4. Diagnose Each Series

Each series gets its own residuals, error metrics, anomalies, continuity check, and strength metrics.

### 5. Plot Each Series

Each series produces decomposition, seasonal cycle, residuals, Z‑scores, anomalies, continuity, forecast versus actual, strength bars, and variance contributions.

### 6. Aggregate

Lumen supports bottom-up aggregation where the aggregate forecast is the sum of the individual forecasts for each period, the simplest and most interpretable method:

$$
\hat{y}^{(agg)}_t = \sum^N_{i = 1} \hat{y}^{(i)}_t
$$

where $\hat{y}^{(i)}_t$ is the forecast for series $i$ and $\hat{y}^{(agg)}_t}} is the aggregated forecast

## Multi-Series Payload

Running `orchestrator.run_multi()` returns an `ExportPayload` containing everything needed for analysis, plotting, and export.

### Payload Structure


| Field	| Description |
| ----- | ----------- |
| `individual` | Per‑series forecast DataFrames |
| `models` |Per‑series decomposition models |
| `diagnostics` | Per‑series diagnostics objects |
| `metadata["history"]`	| Per‑series historical series |
| `aggregated` | Aggregated forecast (optional) |
| `aggregated_diagnostics` | Diagnostics for aggregated series |
| `metadata` | Frequency, periods, loader info |

## When to Use Multi-Series Forecasting

Use multi-series forecasting when:

- You have multiple independent time series,
- You need per‑series diagnostics,
- You want transparent bottom‑up aggregation,
- You want to compare series behavior (trend, seasonality, anomalies), and
- You want to export everything in one combined file.

## When Not to Use Multi-Series Forecasting

Avoid multi-series forecasting when:

- You need hierarchical reconciliation,
- You need cross‑series interactions,
- You need probabilistic forecasts, and
- You need machine‑learning‑based accuracy.
