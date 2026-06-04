
# Diagnostics Engine

The Diagnostics Engine evaluates model performance, continuity, and component behavior after fitting or forecasting.

## Responsibilities

- Compute residuals and accuracy metrics (MAE, RMSE, MAPE, SMAPE), 
- Assess continuity between the last fitted point and the first forecasted point, 
- Detect anomalies in the historical series, 
- Calculate trend strength and seasonality strength, and
- Produce a structured diagnostics object for export and model‑selection logic.

## Accessors

```{python}
diagnostics.residuals
diagnostics.mae
diagnostics.rmse
diagnostics.mape
diagnostics.smape
diagnostics.continuity_relative_jump
diagnostics.anomaly_count
diagnostics.trend_strength
diagnostics.seasonal_strength
```

## Computing Diagnostics

```{python}
diagnostics = DiagnosticsEngine(
    history, 
    fitted, 
    forecast, 
    freq,
    trend = model.trend_,
    seasonal = model.seasonal_factors_
)

diagnostics.compute_all()
```