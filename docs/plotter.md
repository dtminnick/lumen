
# Plotter

The `Plotter` is Lumen’s visualization engine. It generates decomposition, diagnostics, and forecast plots for both single‑series and multi‑series workflows. It consumes the structured outputs of the forecasting pipeline—history, model components, forecasts, and diagnostics—and produces a consistent suite of interpretable visualizations.

The `Plotter` is intentionally decoupled from the forecasting engines. It does not compute anything; it only renders what the engines produce.

## Architecture Role

The `Plotter` sits at the presentation layer of Lumen’s architecture.  It depends on:

- history,
- decomposition model,
- forecast,
- future index, and
- diagnostics.

All of these are provided by the ExportPayload.