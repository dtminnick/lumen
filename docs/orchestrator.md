
# Orchestrator

The `Orchestrator` is the central coordination layer of the Lumen forecasting engine.

It manages the full forecasting workflow:

- loading data,
- running forecasts,
- aggregating multi‑series results,
- packaging outputs, and
- exporting results.

It is designed to be stateless, deterministic, and fully pluggable, allowing you to swap in different aggregators, data loaders, and export strategies without changing user code.

## Overview

The orchestrator exposes two primary entry points:

- `run_single()` to forecast a single dataset, and
- `run_multi()` to forecast multiple datasets and optionally aggregate them.

Both return an ExportPayload object, which contains:

-individual forecasts,
-aggregated forecasts,
-diagnostics,
-metadata,
-histories, and
-combined frames.

This payload is then passed to the export engine.