
# lumen/orchetrator.py

"""
High-level orchestration layer for multi-series and single-series Lumen workflows.

This module defines the :class:`Orchestrator`, the central coordination layer
responsible for running Lumen forecasting pipelines across one or many input
series, applying optional aggregation strategies, and producing a unified
:class:`ExportPayload` for downstream export.

The orchestrator handles:
    * Single-series forecasting
    * Multi-series forecasting
    * Aggregation (bottom-up, top-down, etc)
    * Construction of export-ready payloads

It does **not** perform forecasting itself - forecasting is delegated to
:class:`Lumen`, and aggregation is delegated to subclasses of 
:class:`Aggregator`.
"""

from __future__ import annotations
from typing import Dict, Optional

from lumen.lumen import Lumen
from lumen.export_payload import ExportPayload
from lumen.export_engine import ExportEngine, ExportConfig
from lumen.aggregator import Aggregator

class Orchestrator:

    """
    Multi-series orchestration layer for Lumen.

    This class coordinates the full forecasting workflow, including:
        * Running single-series forecasts
        * Running multi-series forecasts
        * Applying optional aggregation strategies
        * Building :class:`ExportPayload` objects for export

    The orchestrator is intentionally lightweight.  It delegates:
        * Forecasting to :class:`Lumen'
        * Aggregation to :class:`Aggregator`
        * Export to :class:`ExportEngine`

    Parameters
    ----------
    data_config : DataConfig
        Configuration describing how input time series should be parsed.

    export_config : ExportConfig, optional
        Configuration for the export engine.  If omitted, a default
        :class:`ExportConfig` is created.

    Attributes
    ----------
    data_config : DataConfig
        Configuration for loading and interpreting input data.

    export_config : ExportConfig
        Configuration for export formatting and output behavior.

    exporter : ExportEngine
        Engine responsible for writing :class:`ExportPayload` objects to disk.
    """

    def __init__(self, data_config, export_config: Optional[ExportConfig] = None):
        self.data_config = data_config
        self.export_config = export_config or ExportConfig()
        self.exporter = ExportEngine(self.export_config)

    # Single-series flow.

    def run_single(self, path: str, steps: int) -> ExportPayload:

        """
        Run a complete single-series Lumen forecast workflow.

        This method:
            1. Loads a single input file.
            2. Fits a Lumen model.
            3. Produces a forecast.
            4. Packages results into an :class:`ExportPayload`

        Parameters
        ----------
        path : str
            Path to the input time series file.

        steps : int
            Number of forecast periods to generate.

        Returns
        -------
        ExportPayload
            Contains:
                * ``individual`` - forecast for the single series
                * ``aggregated`` - None
                * ``diagnostics`` - model diagnostics
                * ``metadata`` - mode = "single_series"

        Notes
        -----
        This method does not perform aggregation.  It is a thin wrapper around 
        the :class:`Lumen` single-series pipeline.
        """

        lumen = Lumen(self.data_config, self.export_config)

        lumen.load_file(path)

        lumen.fit()

        forecast = lumen.forecast(steps)

        return ExportPayload(
            individual={"default": forecast},
            aggregated=None,
            diagnostics={"default": lumen.diagnostics},
            aggregated_diagnostics=None,
            metadata={"mode": "single_series"}
        )

    # Multi-series flow.

    def run_multi(
        self,
        paths: Dict[str, str],
        steps: int,
        aggregator: Optional[Aggregator] = None,
        **agg_kwargs
    ) -> ExportPayload:

        """
        Run a multi-series forecasting workflow with optional aggregation.

        This method:
            1. Runs Lumen independently for each work type.
            2. Collects histories, forecasts, and diagnostics.
            3. Applies an aggregation strategy (if provided).
            4. Builds a unified :class:`ExportPayload`.

        Parameters
        ----------
        paths : dict[str, str]
            Mapping of work type to input file path.

        steps : int
            Number of forecast periods for each series.

        aggregator : Aggregator, optional
            Aggregation strategy to apply.  If omitted, no aggregation is
            performed and ``aggregated`` fields in the payload are ``None``.

        **agg_kwargs :
            Additional keyword arguments passed directly to the aggregator's
            :meth:`aggregate` method.  Examples include:
                * ``proportions`` (top-down constant)
                * ``periodic_proportions`` (top-down per period)

        Returns
        -------
        ExportPayload
            Contains:
                * ``individual`` - per-series forecasts
                * ``aggregated`` - aggregated forecast (if applicable)
                * ``diagnostics`` - per-series diagnostics
                * ``aggregated_diagnostics`` - aggregator diagnostics (if any)
                * ``metadata`` - histories, strategy name, combined frames, etc.

        Notes
        -----
        The orchestrator does **not** validate aggregator semantics.  It simply
        forwards inputs to the aggregator and packages the result.
        """

        forecasts = {}

        diagnostics = {}

        histories = {}

        models = {}

        # Run Lumen for each type.

        for work_type, path in paths.items():

            lumen = Lumen(self.data_config, self.export_config)

            lumen.load_file(path)

            lumen.fit()

            # Store history.

            histories[work_type] = lumen.loader.data.copy()

            # Store forecast + diagnostics.

            forecasts[work_type] = lumen.forecast(steps)

            diagnostics[work_type] = lumen.diagnostics

            models[work_type] = lumen.engine.model

        # Apply aggregation strategy (optional).

        if aggregator is not None:

            agg_result = aggregator.aggregate(

                forecasts=forecasts,

                histories=histories,

                **agg_kwargs

            )

            aggregated = agg_result.aggregated

            aggregated_diag = agg_result.metadata.get("diagnostics")

            metadata = {

                "mode": "multi_series",

                "strategy": agg_result.metadata.get("strategy"),

                "history": histories,

                "aggregated_history": agg_result.metadata.get("aggregated_history"),

                "aggregated_combined": agg_result.metadata.get("aggregated_combined"),

                **agg_result.metadata

            }

        else:

            aggregated = None

            aggregated_diag = None

            metadata = {

                "mode": "multi_series",

                "strategy": None,

                "history": histories

            }

        # Build ExportPayload.

        return ExportPayload(

            individual=forecasts,

            aggregated=aggregated,

            diagnostics=diagnostics,

            aggregated_diagnostics=aggregated_diag,

            metadata=metadata,

            models = models

        )

    # Export wrapper.

    def export(self, path: str, payload: ExportPayload):

        self.exporter.export_payload(path, payload)
