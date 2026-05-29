
# Multiplicative Decomposition Model

Lumen uses a clean multiplicative model:

$y(t) = \text{Trend}(t) \times \text{Seasonality}(t)

## Trend

Trend is modeled in log-space:

$log(y) = Slope * t + Intercept$

## Growth Rate

$\text{Growth Rate} = exp(Slope) - 1$

## Seasonality

Seasonal factors are computed by:

- Removing trend,
- Grouping by seasonal index,
- Averaging, and 
- Normalizing to mean = 1.

Seasonal period:

- Hourly = 24,
- Daily = 7, 
- Weekly = 52, and
- Monthly = 12.

## Outputs

- `growth_rate`, and
- `seasonal_factors`.
