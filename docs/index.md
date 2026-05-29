
# Lumen Forecasting Engine

Lumen is a lightweight, interpretable, production‑ready forecasting engine built around a clean multiplicative trend + seasonality model. It produces fast, stable, transparent forecasts with no randomness, no hyperparameters, and no black‑box behavior.

> **Lumen in one line: ** 
A deterministic forecasting engine for teams who need clarity, reproducibility, and auditability — not machine‑learning guesswork.

## Quick Example

```{python}
from lumen.lumen import Lumen
from lumen.data_loader import DataConfig

lumen = Lumen(DataConfig(date_col="Date", value_col="Value"))
lumen.load_file("path/to/input.xlsx")
lumen.fit()
forecast = lumen.forecast(24)
lumen.export("path/to/output.xlsx")
```

## Why Lumen?

- **Interpretable**: explicit trend growth rate, seasonal factors, fitted values, and residuals.
- **Deterministic**: No randomness, no hyperparameters, no tuning loops.
- **Fast**: pure Python with NumPy and Pandas; fits in milliseconds.
- **Flexible**: works with multiple frequencies.
- **Diagnostics-Driven**: built-in residuals analysis, anomaly detection, continuity checks, and error metrics.
- **Export-Friendly**: produces clean csv or xlsx files with history, forecast, components, and diagnostics.
- **Plot-Ready**: automatic decomposition, forecast, and diagnostic plots.

## How Lumen Works

Lumen follows a simple, transparent pipeline:

- **Load Data**: parse timestamps, infer frequency, validate continuity.
- **Decompose Series**: Fit multiplicative trend and seasonal factors.
- **Forecast**: Extend trend forward and repeat seasonal cycle.
- **Diagnose**: Compute residuals, error metrics, anomalies, and continuity.
- **Plot**: Decomposition, seasonal cycle, residuals, z-scores, anomalies, forecast versus actual.
- **Export**: write csv or xlsx with all components and diagnostics.

## Philosophy

Lumen is built on three principles:

- Transparency over complexity
- Determinism over randomness
- Interpretability over black‑box accuracy

If you need a forecasting engine that behaves the same way every time, is easy to debug, and produces clean, auditable outputs, Lumen is for you.
