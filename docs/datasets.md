
# Test Datasets for Lumen Diagnostics

This page documents the synthetic datasets used to validate Lumen’s diagnostics engine.  

Each dataset is generated at a different frequency (hourly, daily, weekly, monthly) and contains multiple value columns representing different combinations of trend, seasonality, structural breaks, and decline patterns.

These datasets allow you to verify:

- trend strength,
- seasonal strength,
- continuity detection,
- anomaly detection,
- structural break detection, and
- decomposition stability.

## Dataset Structure (All Frequencies)

Each dataset contains the following columns:

| Column | Description |
|--------|-------------|
| **value_flat** | No trend, no seasonality. Baseline noise only. |
| **value_trend** | Linear trend, no seasonality. |
| **value_seasonal** | Pure seasonality, no trend. |
| **value_trend_seasonal** | Trend + seasonality. |
| **value_break_trend** | Trend with a structural break in level. |
| **value_decline_seasonal** | Declining trend with seasonality. |

All datasets use a datetime index appropriate to their frequency.

# Hourly Dataset (`test_hourly.xlsx`)

**Frequency:** Hourly  
**Length:** 60 days (1440 observations)  
**Seasonality:** 24‑hour cycle  
**Noise:** Small Gaussian noise  

### Expected Diagnostics

| Column | Trend Strength | Seasonal Strength | Continuity | Anomalies | Notes |
|--------|----------------|------------------|------------|-----------|-------|
| **value_flat** | ~0.0 | ~0.0 | True | 0 | Pure noise baseline. |
| **value_trend** | ≥0.9 | ~0.0 | True | 0 | Strong linear trend. |
| **value_seasonal** | ~0.0 | ≥0.7 | True | 0 | Strong daily cycle. |
| **value_trend_seasonal** | ≥0.7 | ≥0.5 | True | 0 | Both signals present. |
| **value_break_trend** | 0.4–0.7 | ~0.0 | False | ≥1 | Break causes jump + anomalies. |
| **value_decline_seasonal** | ≥0.8 | 0.2–0.5 | True | 0 | Declining channel with seasonality. |

# Daily Dataset (`test_daily.xlsx`)

**Frequency:** Daily  
**Length:** 3 years (~1095 observations)  
**Seasonality:** Weekly (period 7)  

### Expected Diagnostics

| Column | Trend Strength | Seasonal Strength | Continuity | Anomalies |
|--------|----------------|------------------|------------|-----------|
| **value_flat** | ~0.0 | ~0.0 | True | 0 |
| **value_trend** | ≥0.9 | ~0.0 | True | 0 |
| **value_seasonal** | ~0.0 | ≥0.7 | True | 0 |
| **value_trend_seasonal** | ≥0.7 | ≥0.5 | True | 0 |
| **value_break_trend** | 0.4–0.7 | ~0.0 | False | ≥1 |
| **value_decline_seasonal** | ≥0.8 | 0.2–0.5 | True | 0 |

# Weekly Dataset (`test_weekly.xlsx`)

**Frequency:** Weekly  
**Length:** 6 years (~312 observations)  
**Seasonality:** Annual (period 52)  

### Expected Diagnostics

| Column | Trend Strength | Seasonal Strength | Continuity | Anomalies |
|--------|----------------|------------------|------------|-----------|
| **value_flat** | ~0.0 | ~0.0 | True | 0 |
| **value_trend** | ≥0.9 | ~0.0 | True | 0 |
| **value_seasonal** | ~0.0 | ≥0.8 | True | 0 |
| **value_trend_seasonal** | ≥0.7 | ≥0.7 | True | 0 |
| **value_break_trend** | 0.4–0.7 | ~0.0 | False | ≥1 |
| **value_decline_seasonal** | ≥0.8 | 0.3–0.6 | True | 0 |

# Monthly Dataset (`test_monthly.xlsx`)

**Frequency:** Monthly  
**Length:** 10 years (120 observations)  
**Seasonality:** Annual (period 12)  

### Expected Diagnostics

| Column | Trend Strength | Seasonal Strength | Continuity | Anomalies |
|--------|----------------|------------------|------------|-----------|
| **value_flat** | ~0.0 | ~0.0 | True | 0 |
| **value_trend** | ≥0.9 | ~0.0 | True | 0 |
| **value_seasonal** | ~0.0 | ≥0.8 | True | 0 |
| **value_trend_seasonal** | ≥0.7 | ≥0.7 | True | 0 |
| **value_break_trend** | 0.4–0.7 | ~0.0 | False | ≥1 |
| **value_decline_seasonal** | ≥0.8 | 0.3–0.6 | True | 0 |
