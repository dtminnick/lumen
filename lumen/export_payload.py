
# lumen/export_payload.py

"""
Unified export container for single-series and multi-series Lumen forecasting.

The :class:`ExportPayload` dataclass defined the canonical data contract between
the forecasting/orchestration layer and the export layer.  It encapsulates all
outputs required to write a complete export file, including:

    * Per-work-type forecasts
    * Optional aggregated forecast
    * Diagnostics for each work type
    * Optional aggregated diagnostics
    * Rich metadata describing histories, combined frames, strategy details, etc.

This object is produced by :class:`Orchestrator` and consumed by
:class:`ExportEngine`.  It is intentionally flexible and strategy-agnostic.
"""

from __future__ import annotations
from dataclasses import dataclass
from typing import Dict, Any
import pandas as pd
from lumen.diagnostics_engine import DiagnosticsEngine
from lumen.series_decomposition import SeriesDecomposition

@dataclass
class ExportPayload:

    """
    Container for all forecast, diagnostic, and metadata outputs required for export.

    This dataclass is the standardized output format used by the Lumen
    orchestration layer. It supports both single-series and multi-series
    workflows, with or without aggregation.

    Parameters
    ----------
    individual : dict[str, pd.Series | pd.DataFrame]
        Mapping of work type → forecast output.  
        For single-series workflows, this contains a single entry:
        ``{"default": forecast}``.

        Each forecast may be:
            * A ``pd.Series`` (single value column)
            * A ``pd.DataFrame`` (multi-column forecast)

    aggregated : pd.Series | pd.DataFrame | None
        The aggregated forecast produced by an aggregation strategy.
        ``None`` if no aggregation was applied.

        Examples:
            * Bottom-up is sum of component forecasts  
            * Top-down is allocated forecast based on proportions

    diagnostics : dict[str, DiagnosticsEngine]
        Mapping of work type → diagnostics object produced by Lumen.
        Each :class:`DiagnosticsEngine` contains:
            * residuals
            * anomaly detection
            * model fit metrics
            * seasonal/trend strength
            * plots (if enabled)

    aggregated_diagnostics : DiagnosticsEngine | None
        Diagnostics for the aggregated forecast, if the aggregation strategy
        produces them. ``None`` for strategies that do not compute diagnostics.

    metadata : dict[str, Any]
        Arbitrary metadata describing the run. Common fields include:

            * ``mode`` — "single_series" or "multi_series"
            * ``strategy`` — name of the aggregation strategy
            * ``history`` — per-work-type historical series
            * ``aggregated_history`` — aggregated historical series
            * ``aggregated_combined`` — combined history+forecast DataFrame
            * aggregator-specific fields (e.g., proportions, weights)

        The export engine does not enforce a schema — it simply writes
        metadata to the output file where appropriate.

    Notes
    -----
    This class is intentionally minimal. It does not validate shapes,
    enforce column names, or interpret metadata. All semantic meaning is
    defined by the orchestrator and aggregation strategies.

    The :class:`ExportEngine` relies on this object to determine which sheets
    to write, how to structure combined frames, and how to include diagnostics.
    """

    # Forecasts.

    individual: Dict[str, pd.Series | pd.DataFrame]

    aggregated: pd.Series | pd.DataFrame | None

    # Diagnostics.

    diagnostics: Dict[str, DiagnosticsEngine]

    aggregated_diagnostics: DiagnosticsEngine | None

    # Metadata (now includes histories + combined frames).
    
    metadata: Dict[str, Any]

    models: Dict[str, SeriesDecomposition]
