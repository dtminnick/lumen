
# Residuals

Residuals measure how well the model fits the historical data.  

In Lumen, residuals are multiplicative, meaning they express the ratio between the actual value and the fitted value:

$$
e_t = \frac{y_t}{\hat{y}_t}
$$

This makes the residuals scale-aware and easy to interpret:

- $e_t = 1 \rightarrow$ perfect fit.
- $e_t > 1 \rightarrow$ actual is above fitted.
- $e_t < 1 \rightarrow$ actual is below fitted.

Residuals are the foundation for anomaly detection, error metrics, continuity checks, and strength metrics.

## Residuals Over Time

