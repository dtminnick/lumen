
## Forecast Interpretation

Forecasting in Lumen is the natural extension of its multiplicative decomposition model. Once the trend and seasonal components are estimated, producing future values becomes simple, stable, and fully interpretable.

Lumen forecasts by projecting the trend forward and repeating the seasonal cycle, then combining them multiplicatively:

$$
\hat{y}_{t + h} = \hat{T}_{t + h} \cdot \hat{S}_{t + h}
$$

This section explains how each part works and how to interpret the resulting forecasts.

## How Forecasting Works

Lumen’s forecasting pipeline has three steps:

1. Extend the trend into the future.
2. Repeat the seasonal cycle for future timestamps.
3. Multiply trend × seasonality to produce the forecast.

This approach is:

- deterministic,
- interpretable,
- stable,
- frequency‑aware, and
- scale‑aware.

## Extending the Trend

Lumen uses a LOESS‑style smoother to estimate trend.
When forecasting:

- the smoother is extended forward,
- the trend continues in the direction implied by recent history,
- curvature is preserved when appropriate, and
- no randomness or hyperparameters are introduced.

This produces a trend that is smooth, stable, and consistent with the historical pattern.

## Repeating the Seasonal Cycle

Seasonality is inherently periodic.  Once Lumen learns the seasonal cycle:

- monthly data becomes 12 seasonal factors,
- weekly data becomes 7 factors, and
- hourly data becomes 24 factors.

It simply repeats the cycle into the future.  For example, if the last observed point is in March, the next forecast uses April’s seasonal factor, then May’s, then June’s, and so on.

This ensures the seasonal pattern remains consistent and interpretable.

## Combining Trend and Seasonality

The final forecast is: $\hat{y}_{t + h} = \hat{T}_{t + h} \cdot \hat{S}_{t + h}$.

This means:

- if trend is rising, the whole seasonal pattern rises,
- if trend is falling, the seasonal pattern shrinks, and
- seasonal peaks and troughs scale with the level of the series.

This is why multiplicative models feel natural for many real‑world processes.

## Forecast Horizon

Lumen supports forecasting for any number of steps:

```{python}
forecast = lumen.forecast(steps = 30)
```

The meaning of step depends on the data frequency:

- hourly = 30 hours,
- daily = 30 days,
- weekly = 30 weeks, and
- monthly = 30 months.

Lumen automatically infers frequency when possible.
