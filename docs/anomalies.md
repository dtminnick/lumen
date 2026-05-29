
# Anomalies

Anomalies are observations that deviate significantly from the expected behavior of the model.  Lumen detects anomalies using a combination of:

- Multiplicative residuals,
- Z-scores,
- Continuity checks, and
- Optional threshold rules.

Anomalies are flagged automatically during `fit()` and `forcast()` and appear in the diagnostics summary and the exported Excel file.

## What Counts as an Anomaly?

Lumen considers a point anomalous when:

- The residual is unusually large or small,
- The z-score exceeds a statistical threshold,
- The point disrupts continuity at the forecast boundary, 
- The deviation cannot be explained by trend or seasonality.

This approach is robust, interpretable, and scale-aware.

## Residual-Based Detection

Residuals measure how far the actual value deviates from the fitted model:

$$
e_t = \frac{y_t}{\hat{y}_t}
$$

- $e_t > 1 \rightarrow$ unusually high actual value, and
- $e_t < 1 \rightarrow$ unusually low actual value.

Large spikes may indicate anomalies, cluster of spikes may indicate structural change, and smooth behavior suggests a stable model.

## Z-Score Detection

Residuals are standardized to identify statistically significant deviations:

$$
z_t = \frac{e_t - \mu_e}{\sigma_e}
$$

Points beyond +/-3 are considered statistically unusual.  Consecutive high z-scores may indicate a regime shift.  Mostly $|z| < 2$ indicates a stable model.

## Continuity-Based Detection

Lumen checks the transition between the last historical point and the first forecast point:

- Last history value,
- First forecast value,
- Relative jump,
- Continuity threshold, and
- Continuity flag.

A large jump may indicate:

- Misaligned seasonal phase,
- Trend curvature mismatch,
- Insufficient history, or
- A structural break.