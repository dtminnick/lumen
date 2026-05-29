
# Seasonality Interpretation

Seasonality represents repeating patterns in a time series — daily cycles, weekly rhythms, monthly peaks, yearly holidays, or any other periodic structure tied to the data’s frequency.

Lumen models seasonality in a way that is stable, interpretable, and frequency‑aware, producing seasonal factors that clearly show how each period deviates from the long‑term trend.

## What Seasonality Represents

Seasonality answers questions like:

- Which months are consistently high or low,
- Which hours of the day spike,
- Which days of the week dip,
- How strong the repeating pattern is, and
- How the seasonal cycle interacts with trend?

In Lumen's multiplicative model:

$$
y_t = T_t \cdot S_t
$$

the seasonal factor $S_t$ represents the relative deviation from the trend line at time $t$.

## Multiplicative Seasonal Factors

Lumen uses multiplicative seasonality, meaning:

- $S_t > 1 \rightarrow$ above-trend period,
- $S_t < 1 \rightarrow$ below-trend period, and
- $S_t = 1 \rightarrow$ neutral period.

Examples:

- $S_t = 1.25 \rightarrow$ 25% above trend, and
- $S_t = 0.80 \rightarrow$ 20% below trend.

This makes seasonal factors easy to interpret and scale-aware.

## How Lumen Computes Seasonality

Seasonality is computed after removing the trend:

$$
d_t = \frac{y_t}{T_t}
$$

Then Lumen:

1. Groups detrended values by seasonal index, e.g. all Januaries, all Mondays, all 3:00pm hours.
2. Averages within each group.
3. Normalizes the cycle so that the mean seasonal factor = 1.
4. Repeats the cycle across the full series.

This produces a stable, interpretable seasonal pattern.

## Seasonal Cycle

The seasonal cycle is the repeating pattern of factors across one full period:

- 12 values for monthly data,
- 7 values for weekly data, and
- 24 values for hourly data, etc.

Lumen exposes this as:

- `seasonal_factors` (cycle only), and
- `seasonal_factors_` (cycle repeated across the series).

## Seasonal Strength

Lumen computes a seasonal strength metric that measures how much of the series’ variance is explained by seasonality.

Values range from 0 to 1:

- 0.0 means no meaningful seasonality,
- 0.5 means moderate seasonality, and
- 1.0 means seasonality dominates the series.

This metric is based on Hyndman’s definition and adapted for multiplicative models.
