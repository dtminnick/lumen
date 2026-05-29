
# Diagnostics Overview

Lumen includes a comprehensive diagnostics suite designed to help you understand model fit, detect anomalies, evaluate continuity at the forecast boundary, and quantify the relative strength of trend and seasonality.  

This page introduces each diagnostic category and explains how to interpret results.

## Residuals

Residuals measure the difference between the actual series and the fitted model.  Lumen uses multiplicative residuals:

$$
e_t = \frac{y_t}{\hat{y}_t}
$$

- $e_t = 1 \rightarrow$ perfect fit.
- $e_t > 1 \rightarrow$ actual is above fitted.
- $e_t < 1 \rightarrow$ actual is below fitted.

Residuals help identify model misfit, strctural changes, and unusual spikes or dips.

## Residual Distribution

A histogram of residuals shows how tightly the model fits the output.

- A narrow distribution centered at one indicates good fit.
- Skew or heavy tails may indicate anomalies or missing structure.

## Residual Z-Scores

Residuals are standardized to identify statistically significant deviations:

$$
z_t = \frac{e_t - \mu_e}{\sigma_e}
$$

- Points beyond +/-3 are potential anomalies.
- Clusters of high z-scores may indicate structural change.

## Anomaly Detection

Lumen flags anomalies using:

- residual magnitude
- z‑score thresholds
- optional continuity checks

Anomalies appear in the diagnostics summary and the exported dataset.

## Error Metrics

Lumen computes four standard error metrics:

- MAE — average absolute error
- RMSE — penalizes large errors
- MAPE — percent error
- SMAPE — symmetric percent error

These metrics help compare model performance across datasets.

## Continuity Check

Continuity measures how smoothly the model transitions from the last historical point to the first forecast point.

Lumen computes:

- last historical value,
- first forecast value,
- relative jump,
- continuity threshold, and
- continuity flag.

A large jump may indicate:

- misaligned seasonal phase,
- trend curvature mismatch, or
- insufficient history.

## Trend Strength

Trend strength measures how much of the series’ variance is explained by the trend component.

Values range from 0 to 1:

- 0.0 indicates no meaningful trend,
- 0.5 indicates moderate trend, and
- 1.0 indcates trend dominates.

## Seasonal Strength

Seasonal strength measures how much variance is explained by seasonality.

Values range from 0 to 1:

- 0.0 indicates no seasonality, and
- 1.0 indicates strong repeating pattern.

## Variance Contributions

This plot shows how much variance is attributable to trend, seasonality, and residual noise.

It provides a high‑level view of model structure.
