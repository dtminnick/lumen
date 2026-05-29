
# Aggregator

The `Aggregator` is the abstraction that defines how multiple independent time series are combined into a single aggregated forecast. It is used exclusively in the multi‑series pipeline and provides a clean, extensible interface for implementing different aggregation strategies.

Aggregation is optional in Lumen, but when enabled, the `Aggregator` determines:

- how individual forecasts are combined,
- how individual histories are combined,
- how aggregated diagnostics are computed, and
- what metadata is included in the final ExportPayload.

## Architecture Role

The `Aggregator` sits between the per‑series forecasting pipeline, and the `Orchestrator`, which assembles the final payload.

## Aggregation Result

All aggregators return an `AggregationResult`, which contains:

- `aggregated` — the aggregated forecast
- `components` — the aligned per‑series forecasts
- `metadata` — history, aggregated history, combined frames, strategy name

This object is later inserted into the ExportPayload.
