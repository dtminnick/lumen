
# Architecture Overview

Lumen is built around a clean, modular pipeline designed for clarity, stability, and interpretability. Each component has a single responsibility, and the `Lumen` class orchestrates them into a cohesive forecasting engine.

## Components

### Data Configuration

The `DataConfig` class defines all user‑controlled settings for loading, interpreting, and preparing a dataset in Lumen.

It acts as the single source of truth for:

- which columns to read,
- how to interpret dates,
- how to infer or override frequency,
- how to control decomposition behavior, and
- how to format output.

### Data Loader

The `DataLoader` class is responsible for ingesting and validating the input series.

- loads csv or xlsx files,
- parses and normalizes date columns,
- infers or validates frequency,
- ensures a monotonic datetime index, and
- exposes the cleaned series to downstream components.

### Series Decomposition

Lumen decomposes the series into trend and seasonality using a stable, interpretable multiplicative model via `SeriesDecomposition` class:

- operates in log‑space,
- applies a LOESS‑style smoother to estimate trend,
- computes seasonal factors by grouping detrended values,
- normalizes seasonality so the mean factor = 1, and
- supports hourly, daily, weekly, and monthly frequencies.

### Forecast Engine

The `ForecastEngine` class extends the decomposition into the future.

- generates future timestamps based on inferred frequency,
- extrapolates the smoothed trend,
- repeats the seasonal cycle,
- multiplies trend × seasonality to produce forecasts, and
- returns a forecast DataFrame with aligned index.

### Diagnostics Engine

The `DiagnosticsEngine` class evaluates model quality and structural behavior.

- computes multiplicative residuals,
- generates z‑scores,
- detects anomalies,
- evaluates continuity at the forecast boundary,
- computes trend and seasonal strength,
- calculates error metrics (MAE, RMSE, MAPE, SMAPE), and
- produces a unified diagnostics object.

### Plotter

The `Plotter` class produces all visual outputs used in the documentation and diagnostics.

- decomposition plots,
- seasonal cycle and seasonal factors,
- residuals and z‑scores,
- anomaly visualization,
- continuity check,
- forecast vs actual, and
- strength metrics and variance contributions.

### Export Engine

The `ExportEngine` class writes results to disk in a clean, analysis‑ready format.

- exports history, forecast, and diagnostics,
- supports csv and xlsx,
- writes multiple sheets (forecast, residuals, diagnostics, components), and
- ensures consistent formatting and column naming.

### Lumen (Orchestrator)

The `Lumen` class ties everything together into a simple, user‑facing API.

- loads data,
- fits decomposition,
- generates forecasts,
- computes diagnostics,
- produces plots, and
- exports results.

It provides a clean, minimal interface.
