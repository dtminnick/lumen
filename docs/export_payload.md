
# Export Payload

The `ExportPayload` is the central data structure that connects the multi‑series forecasting pipeline to downstream consumers such as the `Plotter`, `ExportEngine`, and any custom integrations. It acts as the output contract of the `Orchestrator` and the input contract for plotting and exporting.

It is not a model, not an engine, and not a loader.  It is the container that carries all results produced by the engines.

## Architecture Role

In the `Lumen` architecture, the `ExportPayload` sits at the boundary between computation (decomposition, forecasting, diagnostics) and presentation (plots, exports, reports).

It is produced by `Orchestrator` and consumed by `Plotter` and `ExportEngine`.

The `ExportPayload` is the only object that contains:

- All per‑series results,
- All aggregated results,
- All diagnostics,
- All models, and
- All metadata.

It is the complete representation of a multi‑series forecasting run.

## Payload Structure

The payload is a dataclass with the following fields:


| Field	| Description |
| ----- | ----------- |
| individual | Per‑series forecast DataFrames |
| models | Decomposition models for each series |
| diagnostics | Diagnostics per series |
| metadata | History, loader info, frequency, periods |
| aggregated | Aggregated forecast (optional) |
| aggregated_diagnostics | Diagnostics for aggregated series |

## How `ExportPayload` Is Constructed

Inside `Orchestrator.run_multi()`:

1. Each series is loaded
2. Each series is decomposed
3. Each series is forecasted
4. Each series is diagnosed
5. Each series’ model is captured
6. Aggregation is applied (optional)
7. Aggregated diagnostics are computed
8. Everything is assembled into an `ExportPayload`

This ensures that all components remain synchronized.

## How ExportPayload Supports Exporting

The ExportEngine uses the payload to write a combined XLSX:

- one sheet per series,
- one sheet for aggregated results,
- one sheet for diagnostics, and
- one sheet for metadata.

This is possible because the payload contains all components in a predictable structure.

## Extending ExportPayload

Because it is a dataclass, you can safely extend it to include:

- custom metrics,
- custom metadata,
- custom aggregation outputs, and
- custom diagnostics.

The orchestrator can populate these fields without breaking existing consumers.