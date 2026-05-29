
# Strength Metrics

Strength metrics quantify how much of the series' variance is explained by trend and seasonality.

These metrics help you understand the structure of your data and evaluate whether the model is appropriate for the series.

Lumen captures two strength metrics:

- Trend strength, and
- Seasonality strength.

Both metrics range from 0 to 1, where:

 - 0.0 means the component explains none of the variance, and
 - 0.5 signals a moderate contribution, and 
 - 1.0 indicates the component dominates the series.

 Trend and seasonal strength together describe the shape of the series.  Strong seasonality with moderate trend in common in retail, energy, and traffic data.

 ## Computing Strength Metrics

 Strength metrics are based on comparing:

 - The variance of the detrended or deseasonalized series, and
 - The variance of the residuals.

 ### Trend Strength

 $$
\text{Trend Strength} = 1 - \frac{Var(e_t)}{Car(d_t)}
 $$

 where:

 - $d_t = y_t / S_t$ is the deseasonalized series, and
 - $e_t$ are the residuals.

 ### Seasonal Strength

 $$
\text{Seasonal Strength} = 1 - \frac{Var(e_t)}{Var(y_t / T_t)}}
 $$

 where:

 - $y_t / T_t$ is the detrended series.

 Both formulas measure how much variance remains after removing the component.

 ## Why Strength Metrics Matter

 Strength metrics help you answer:

 - Is the series mostly trend-driven or seasonality driven?
 - Is the seasonal pattern strong enough to trust?
 - Is the trend stable or noisy?
 - Is the model appropriate for this dataset?
 - Should you expect smooth or volatile forecasts?

 They also help diagnose missing seasonal cycles, structural breaks, trend curvature issues, and residual noise problems.

 ## Best Practices

 - **High seasonal strength**:forecasts will strongly follow the seasonal cycle.
- **High trend strength**: long‑term direction is reliable.
- **Low strength values**: consider more history or additional preprocessing.
- **Large residual variance**: inspect anomalies or missing structure.

Strength metrics are especially useful when comparing multiple datasets or monitoring model drift over time.