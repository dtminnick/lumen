
# Continuity

Continuity measures how smoothly the model transitions from the last historical value to the first forecast value.

A well-behaved model should produce a forecast that begins exactly where the historical series ends, with no sudden jumps or drops.

Continuity is one of the most important diagnostics in Lumen because it validates that:

- Trend and seasonality are aligned,
- The seasonal phase is correct,
- The trend curvature is consistent, and
- The model is stable at the forecast boundary.

## Why Continuity Matters

A discontinuity at the forecast boundary often indicates:

- Misaligned seasonal cycle,
- Incorrect seasonal index inference,
- Insufficient historical data,
- A structural break in the series,
- Trend curvature mismatch, or
- A sudden anomaly at the end of history.

Even if error metrics look good, a continuity jump can make the forecast unusable in production.

## Continuity Metrics

Lumen computes several continuity metrics:

### Last History Value

The final observed value in the historical series.

### First Forecast Value

The model's first predicted value.

### Relative Jump

$$
Jump = \frac{\hat{y}_{t + 1} - y_t}{y_t}
$$

- 0.00 is perfect continuity,
- 0.05 is a 5% upward jump, and
- -0.03 is a 3% downward jump.

### Continuity Threshold

A configurable threshold (default 10%) used to flag discontinuities.

### Continuity Flag

A boolean indicating whether the model is continuous at the boundary.

## Causes of Continuity Issues

Continuity problems typically arise from: 

### Seasonal Phase Misalignment

If a seasonal cycle is shifted, e.g. the wrong month index, the first forecast will be off,

### Trend Curvature Mismatch

If the LOESS trend bends sharply near the end, the extrapolated trend may not match the last fitted value.

### Insufficient History

Short series can produce unstable seasonal estimates.

### End-of-History Anomalies

A spike or dip at the end of the series can distort the boundary.

### Incorrect Frequency Detection

If the frequency is mis-inferred, the seasonal cycle may not align.

## How Lumen Ensures Continuity

Lumen includes several mechanisms to maintain continuity:

- multiplicative decomposition ensures smooth scaling,
- LOESS trend smoothing avoids sharp breaks,
- seasonal normalization ensures cycle consistency, and
- continuity metrics detect boundary issues early.

If continuity fails, Lumen still produces a forecast, but the diagnostics flag the issue so you can investigate.
