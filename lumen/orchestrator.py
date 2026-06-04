
"""
Provides high-level orchestration layer for multi-series and single-series Lumen workflows.

This module defines the class `Orchestrator`, the central coordination layer
responsible for running Lumen forecasting pipelines across one or many input
series, applying optional aggregation strategies, and producing a unified
class `ExportPayload` for downstream export.

The Orchestrator handles single-series and multi-series forecasting, series aggregation, and 
construction of export-ready payloads.

The Orchestrator does not perform forecasting itself.  Forecasting is delegated to
class `Lumen`, and aggregation is delegated to subclasses of class `Aggregator`.
"""

from __future__ import annotations
from typing import Dict, Optional

from lumen.lumen import Lumen
from lumen.export_payload import ExportPayload
from lumen.export_engine import ExportEngine, ExportConfig
from lumen.aggregator import Aggregator

class Orchestrator:

    """
    Provides the orchestration layer for Lumen.

    This class coordinates the full forecasting workflow, including running single-series
    and multi-series forecasts, applying optional aggregation strategies, and 
    building class `ExportPayload` objects for exporting forecast data.

    The orchestrator is intentionally lightweight.  It delegates forecasting to
    class `Lumen`, aggregation to class `Aggregator`, and export to class `ExportEngine`.

    Parameters
    ----------
    **data_config : DataConfig**
    
    Configuration describing how input time series should be parsed.

    **export_config : ExportConfig, optional**
    
    Configuration for the export engine.  If omitted, a default class `ExportConfig` is created.

    Attributes
    ----------
    **data_config : DataConfig**
    
    Configuration for loading and interpreting input data.

    **export_config : ExportConfig**
    
    Configuration for export formatting and output behavior.

    **exporter : ExportEngine**
    
    Engine responsible for writing class `ExportPayload` objects to disk.
    """

    def __init__(self, data_config, export_config: Optional[ExportConfig] = None):

        """
        Initialize the orchestrator with data-loading and export configuration.

        The orchestrator wires together the data configuration and export engine.
        It does not load data or run any forecasting logic at initialization.

        Parameters
        ----------
        **data_config : DataConfig**

        Configuration describing the input series, frequency, and preprocessing.

        **export_config : ExportConfig, optional**

        Settings controlling export format and behavior. If omitted, a default 
        class `ExportConfig` instance is created.
        """

        self.data_config = data_config

        self.export_config = export_config or ExportConfig()
        
        self.exporter = ExportEngine(self.export_config)

    def run_single(self, path: str, steps: int) -> ExportPayload:

        """
        Run a complete single-series Lumen forecast workflow.

        This method loads a single input file, fits a Lumen model, 
        produces a forecast, and packages results into a class `ExportPayload`.

        Parameters
        ----------
        **path : str**
            
        Path to the input time series file.

        **steps : int**
        
        Number of forecast periods to generate.

        Returns
        -------
        **ExportPayload**
            
        Contains:
                
        * `individual`, dictionary containing the actual forecast output for the single series, returned as a pandas Series or DataFrame.
        * `aggregated`, always `None` in single-series mode because there's nothing to aggregate.
        * `diagnostics`, dictionary containing the model diagnostics (residuals, metrics, decomposition, etc.) for the single series.
        * `metadata`, dictionary describing the context of the run, including that the mode is "single-series" and the original input history.

        Notes
        -----
        This method does not perform aggregation.  It is a thin wrapper around 
        the class `Lumen` single-series pipeline.
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

    def run_multi(
        self,
        paths: Dict[str, str],
        steps: int,
        aggregator: Optional[Aggregator] = None,
        **agg_kwargs
    ) -> ExportPayload:

        """
        Run a multi-series forecasting workflow with optional aggregation.

        This method runs Lumen independently for each work type, collects histories, 
        forecasts, and diagnostics, applies an aggregation strategy, if provided, 
        and builds a unified class `ExportPayload`.

        Parameters
        ----------
        **paths : dict[str, str]**
        
        Mapping of work type to input file path.

        **steps : int**
        
        Number of forecast periods for each series.

        **aggregator : Aggregator, optional**
        
        Aggregation strategy to apply; if omitted, no aggregation is
        performed and `aggregated` fields in the payload are `None`.

        ****agg_kwargs : dict[str, Any]**
        
        Additional keyword arguments passed directly to the aggregator's 
        `aggregate` method.  Examples include `proportions` (top-down constant) and
        `periodic_proportions` (top-down per period).

        Returns
        -------
        **ExportPayload**
            
        Contains:

        * `individual`, dictionary containing per-series forecasts.
        * `aggregated`, dictionary containing aggregated forecast, if applicable.
        * `diagnostics`, dictionary containing per-series diagnostics.
        * `aggregated_diagnostics`, dictionary containing aggregator diagnostics, if any.
        * `metadata`, dictionary containing histories, strategy name, combined frames, etc.

        Notes
        -----
        The orchestrator does not validate aggregator semantics.  It simply
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

    def export(self, path: str, payload: ExportPayload):

        """
        Write a fully‑constructed class `ExportPayload` to disk.

        This method is a thin wrapper around `ExportEngine.export_payload`,
        delegating the actual serialization and file writing to the configured
        export engine. It does not modify the payload or perform validation.

        Parameters
        ----------
        **path : str**

        Destination file path for the exported output.

        **payload : ExportPayload**

        The forecast results, diagnostics, and metadata produced by `Orchestrator.run_single` 
        or `Orchestrator.run_multi`.
        """

        self.exporter.export_payload(path, payload)
