
# Concepts Overview

Lumen is built on a simple, interpretable idea:

> A time series can be understood as the product of a trend and a seasonal pattern.

This page introduces the core concepts behind Lumen's forecasting engine and provides the intuition you need before diving into trend, seasonality, diagnostics, or architecture.

## Multiplicative Model

Lumen models each observation $y_t$ at time $t$ as:

$$
y_t = T_t \cdot S_t
$$

where:

- $T_t$ is the trend component, and
- $S_t$ is the seasonal factor.

This structure is ideal when seasonal effects scale with the level of the series, peaks grow as the series grows, and troughs shrink as the series shrinks.

## Why Multiplicative?

Multiplicative models are:

- **Scale-Aware**: seasonal effects grow with the series,
- **Interpretable**: seasonal factors represent percent deviations,
- **Stable**: no overfitting, no hyperparameters, and 
- **Frequency-Aware**: Works for hourly, daily, weekly, monthly data.

This makes Lumen predictable and easy to reason about.

## Log-Space Transformation

To estimate the trend, Lumen works in log-space, because:

- Multiplicative relationships become additive,
- Linear regression becomes appropriate, and
- Growth rates become interpretable.

Taking logs:

$$
log \space y_t = log \space T_t + log \space S_t
$$

define:

- $\ell_t = log \space y_t$,
- $\tau_t = log \space T_t$, and
- $\sigma_t = log \space S_t$

then:

$$
\ell_t = \tau_t + \sigma_t
$$

## Trend (Long-Term Growth)

Lumen models the trend as a simple linear function of time:

$$
\tau_t = \alpha + \beta t
$$

where:

- $\alpha$ is the intercept, and
- $\beta$ is the slope, or growth in log-space.

This is estimated using Ordinary Least Squares (OLS):

$$
min_{\alpha, \beta} \sum^T_{t = 1} (\ell_t - (\alpha + \beta t))^2
$$

## Growth Rate Interpretation

The slope $\beta$ corresponds to a multiplicative growth rate.  

The per-period growth rate is:

$$
g = e^{\beta} - 1
$$

Examples:

- $g = 0.01 \rightarrow$ 1% growth per period, and
- $g = -0.02 \rightarrow$ 2% decline per period.

The meaning of period depends on the frequency:

- hourly $\rightarrow$ per hour,
- daily $\rightarrow$ per day,
- weekly $\rightarrow$ per week, and
- monthly $\rightarrow$ per month.

## Seasonality (Repeating Patterns)

After removing the trend:

$$
d_t = \frac{y_t}{T_t}
$$

In log-space:

$$
\sigma_t = \ell_t - \tau_t
$$

Seasonality is computed by grouping detrended values by seasonal index, averaging within each group, and normalizing so the mean seasonal factor equals one.

[Insert]

## Forecasting

To forecast $h$ steps ahead:

1. Extend the trend line forward,
2. Repeat the seasonal cycle, and
3. Multiply trend and seasonality.

$$
\hat{y}_{t + h} = \hat{T}_{t + h} \cdot \hat{S}_{t + h}
$$

## Diagnostics

Lumen includes a full diagnostics suite:

- residuals,
- error metrics,
- anomaly detection,
- continuity checks, and
- trend and seasonal strength.

## Plots

Lumen provides visualizations for:

- decomposition,
- seasonal cycle,
- residuals,
- anomalies,
- forecast vs actual, and
- strength metrics.
