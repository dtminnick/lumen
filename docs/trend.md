
# Trend Interpretation

The trend represents the long‑term direction of a time series, its growth, decline, or structural shape over time. In Lumen, the trend is modeled using a locally adaptive smoother, not a strict straight line. This allows the trend to bend, curve, and adapt to real‑world series that don’t follow perfect exponential growth.

## What Trend Represents

Trend captures the underlying movement of the series after removing short‑term fluctuations and seasonal patterns. It answers questions like:

- Is the series rising or falling over time
- Are there structural changes or bends
- Is the long‑term movement smooth or irregular

Trend is one of the two components in Lumen’s multiplicative model:

$$
y_t = T_t \cdot S_t
$$

where $T_t$ is the trend component.

## Why Trend Is Not Linear

Earlier versions of Lumen used a linear regression in log‑space, which produced a strictly straight trend line. This worked for simple exponential growth but failed when:

- growth slowed down,
- growth accelerated,
- the series had structural breaks, or
- the trend curved over time.

To fix this, Lumen now uses a LOESS‑style locally weighted smoother, the same approach used in STL decomposition.

This produces a trend that:

- bends smoothly,
- adapts to curvature,
- handles structural changes,
- avoids overfitting, and
- remains interpretable.

This is why your trend plots show smooth curves, not straight lines.

## How Trend Is Computed

Lumen applies a LOESS smoother to the log-transformed series:

1. Take logs: $\ell_t = log \space y_y$.
2. Apply a locally weighted regression (LOESS) where each point is fit using nearby points, weights decrease with distance, and the smoother adapts to curvature.
3. Exponentiate back to multiplicative space: $T_t = e^{\tau_t}$.

This produces a trend that is smooth, stable, and frequency-aware.

## Interpreting Trend Shape

Because the trend is locally adaptive, you may see:

- Gentle curves,
- Flattening or acceleration,
- Structural shifts, or
- Plateaus.

These shapes reflect real changes in the underlying process, not noise.

## Trend Strength

Lumen computes a trend strength metric that measures how much of the series’ variance is explained by the trend component.

Values range from 0 to 1:

- 0.0 means no meaningful trend,
- 0.5 means moderate trend, and
- 1.0 means trend dominates the series.
