
# Forecast Engine

The Forecast Engine wraps the decomposition model and produces future predictions.

## Responsibilities

- Generate future timestamps,
- Apply trend x seasonality, and
- Return a forecast series.

## Accessors

```{python}
engine.growth_rate
engine.seasonal_factors
```

## Forecasting

```{python}
forecast = engine.forecast(series, steps = 30)
```
