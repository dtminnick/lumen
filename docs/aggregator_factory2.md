
# Aggregator Factory

The `AggregatorFactory` is the component responsible for instantiating aggregation strategies in Lumen’s multi‑series forecasting pipeline. It provides a clean, extensible mechanism for selecting and constructing aggregation logic without hard‑coding strategy classes inside the orchestrator.

Aggregation is optional in Lumen, but when enabled, the factory ensures that:

- the orchestrator remains decoupled from specific aggregation implementations,

- new aggregation strategies can be added without modifying core code,

- users can register custom strategies dynamically, and

- bottom‑up aggregation remains the default, deterministic behavior.

## Architecture Role

`AggregatorFactory` sits between `Orchestrator` (which requests an aggregator) and `Aggregator` implementations (which perform the actual aggregation)

It acts as a registry + constructor, mapping string names to concrete classes.

