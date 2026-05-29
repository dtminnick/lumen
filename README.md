
# Lumen: A Transparent, Deterministic Forecasting Engine

Lumen is a lightweight, interpretable, diagnostics‑first forecasting engine built around a clean multiplicative trend + seasonality model. It is designed for teams who need **clarity**, **reproducibility**, and **auditability** in their forecasting workflows — not black‑box machine learning.

Lumen grew out of a real production need:  
to formalize, standardize, and mature the forecasting workflow used inside a large organization.

Instead of treating forecasting as a mysterious box that outputs numbers, Lumen emphasizes:

- Diagnostics over predictions  
- Interpretability over opacity  
- Reproducibility over intuition  
- Determinism over randomness  
- Model‑agnostic evaluation over model‑specific tricks  

Lumen helps you understand *why* a forecast behaves the way it does — not just *what* the forecast is.

# Why Lumen Exists

Forecasting inside real organizations often evolves organically:

- Different teams use different tools  
- Assumptions vary  
- Diagnostics are inconsistent or missing  
- Continuity issues go unnoticed  
- Seasonality is assumed rather than measured  
- Structural breaks cause silent failures  
- Forecasts are difficult to explain or defend  

Lumen was created to solve this.

> It began as an internal initiative to formalize and mature our forecasting workflow.  
> We needed a diagnostics‑first approach — something interpretable, testable, and reproducible.

This repository contains the engine, orchestrator, diagnostics, plotting, export tools, and documentation that grew out of that work.

# Core Features

## Deterministic Forecasting Engine

- Multiplicative trend + seasonality model  
- Frequency‑aware decomposition  
- Linear trend extrapolation  
- Repeated seasonal cycle  
- No randomness, no hyperparameters  

## Diagnostics‑First Design

- Multiplicative residuals  
- Residual z‑scores  
- Anomaly detection  
- Continuity checks  
- Trend strength  
- Seasonal strength  
- Variance contributions  
- Structural break indicators  

## Multi‑Series Forecasting

- Run multiple series in parallel  
- Per‑series decomposition models  
- Per‑series diagnostics  
- Bottom‑up aggregation  
- Aggregated diagnostics  
- Unified export payloads 

## Plotting Engine

- Decomposition plots  
- Seasonal cycle  
- Residuals + distribution  
- Z‑scores  
- Anomalies  
- Continuity  
- Forecast vs actual  
- Strength bars  
- Variance contributions  

## Export Engine

- Clean Excel exports  
- History, forecast, components, diagnostics  
- Per‑series + aggregated sheets  
- BI‑friendly structure  

## Synthetic Test Datasets

- Hourly, daily, weekly, monthly  
- Known trend/seasonality/break patterns  
- Reproducible diagnostics  
- Ideal for validation and regression testing  
