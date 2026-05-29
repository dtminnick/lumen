
# lumen/export_engine.py

"""
Export utilities for Lumen decomposition, forecasting, and multi-series aggregation.

The :class:`ExportEngine` writes model outputs, diagnostics, and metadata to
disk in either csv or xlsx format.  It supports two export pathways:

1. Single-series export via :meth:`export`
    Writes history, forecast, decomposition components, residuals, and diagnostics.

2. Multi-series + aggregated export via :meth:`export_payload`
    Consumes an :class:`ExportPayload` and writes:
        * Individual forecasts
        * Combined history and forecast per work type
        * Aggregated forecast, history, and combined frames
        * Diagnostics (individual and aggregated)
        * Metadata

The engine is intentionally minimal and formatting-focused.  It does not compute
forecasts, diagnostics, or aggregation, it only writes structured outputs.
"""
from lumen.export_payload import ExportPayload

from dataclasses import dataclass
from pathlib import Path
import pandas as pd

@dataclass
class ExportConfig:

    """
    Configuration for controlling export behavior.

    Parameters
    ----------
    file_type : str, default "xlsx"
        Output format. Supported values:
            * ``"xlsx"`` — multi-sheet Excel export
            * ``"csv"`` — single combined CSV export

    include_history : bool, default True
        Whether to include historical data in CSV exports.

    rounding : int, default 2
        Number of decimal places to round numeric output to.

    Notes
    -----
    Excel exports always include history, forecast, decomposition components,
    diagnostics, and metadata. CSV exports include only the combined frame.
    """

    file_type: str = "xlsx"

    include_history: bool = True

    rounding: int = 0

class ExportEngine:

    """
    Write Lumen model outputs to disk.

    The :class:`ExportEngine` handles all formatting and file writing for both
    single-series and multi-series workflows. It supports:

        * Combined history + forecast frames
        * Decomposition components (trend, seasonal cycle, seasonal factors)
        * Fitted values and residuals
        * Diagnostics summaries and residual frames
        * Aggregated forecasts and histories
        * Metadata sheets

    Parameters
    ----------
    config : ExportConfig, optional
        Export configuration controlling file type and rounding.

    Notes
    -----
    The engine does not compute any values — it only writes what is provided.
    """

    def __init__(self, config: ExportConfig = ExportConfig()):

        """
        Initialize the export engine.

        This constructor sets up the export subsystem responsible for writing
        decomposition results, forecasts, diagnostics, and metadata to disk.
        The engine itself performs no computation — it formats and writes the
        outputs produced by the forecasting and diagnostics layers.

        Parameters
        ----------
        config : ExportConfig, optional
            Configuration controlling export format (``"xlsx"`` or ``"csv"``),
            inclusion of history, and numeric rounding. Defaults to a new
            :class:`ExportConfig` instance.

        Attributes
        ----------
        config : ExportConfig
            Export settings used by all export methods, including:
                * ``file_type`` — output format
                * ``include_history`` — whether to include history in CSV exports
                * ``rounding`` — decimal precision for numeric values

        Notes
        -----
        * Excel exports support multi‑sheet output and full diagnostic detail.
        * CSV exports are intentionally minimal and include only the combined frame.
        * Multi‑series exports via :meth:`export_payload` require ``file_type="xlsx"``.
        """

        self.config = config

    # Public API.

    def export(
        self, 
        path: str, 
        loader, 
        model, 
        forecast=None, 
        future_index=None, 
        diagnostics = None
    ):
        
        """
        Export decomposition + forecast results for a single series.

        This method is used by the single-series workflow and writes either:
            * A combined CSV file, or
            * A multi-sheet Excel workbook containing:
                - Combined history + forecast
                - History
                - Forecast
                - Trend
                - Seasonal factors over time
                - Seasonal cycle
                - Fitted values
                - Residuals
                - Diagnostics summary
                - Anomalies (if present)

        Parameters
        ----------
        path : str
            Output file path (.xlsx or .csv).

        loader : DataLoader
            Provides validated historical data.

        model : SeriesDecomposition
            Fitted decomposition model containing trend, seasonal factors,
            fitted values, and residuals.

        forecast : pd.Series, optional
            Forecasted values for the horizon.

        future_index : pd.DatetimeIndex, optional
            Index corresponding to the forecast horizon.

        diagnostics : DiagnosticsEngine, optional
            Diagnostics object containing error metrics, anomalies, and
            residual frames.

        Raises
        ------
        ValueError
            If the configured file type is unsupported.
        """

        if self.config.file_type.lower() == "csv":

            self._export_csv(path, loader, model, forecast, future_index)

        elif self.config.file_type.lower() == "xlsx":

            self._export_excel(path, loader, model, forecast, future_index, diagnostics)

        else:

            raise ValueError(f"Unsupported export type '{self.config.file_type}'")
        
    def export_payload(self, path: str, payload: ExportPayload) -> None:

        """
        Export a multi‑series or aggregated forecasting run.

        This method consumes an :class:`ExportPayload` and writes a structured
        Excel workbook containing:

            * Individual forecasts
            * Combined history + forecast per work type
            * Aggregated forecast (if present)
            * Aggregated history and combined frames
            * Diagnostics (individual + aggregated)
            * Metadata sheet

        Parameters
        ----------
        path : str
            Output Excel file path.

        payload : ExportPayload
            Unified container holding forecasts, diagnostics, histories,
            aggregated results, and metadata.

        Raises
        ------
        ValueError
            If the configured file type is not ``"xlsx"``.

        Notes
        -----
        CSV export is intentionally not supported for multi‑series payloads.
        """

        if self.config.file_type.lower() != "xlsx":

            raise ValueError("ExportPayload only supports Excel (.xlsx) output.")

        with pd.ExcelWriter(path) as writer:

            # 1. Individual forecasts + combined
           
            histories = payload.metadata.get("history", {})

            for work_type, forecast in payload.individual.items():

                # Forecast sheet

                forecast.to_excel(writer, sheet_name=f"{work_type}_forecast")

                # Combined sheet

                if work_type in histories:

                    hist = histories[work_type]

                    # Ensure DataFrame

                    if isinstance(hist, pd.Series):

                        hist = hist.to_frame(name="value")

                    if isinstance(forecast, pd.Series):

                        fc = forecast.to_frame(name="value")

                    else:

                        fc = forecast

                    combined = pd.concat([

                        hist.assign(is_forecast=False),

                        fc.assign(is_forecast=True)

                    ])

                    combined.to_excel(writer, sheet_name=f"{work_type}_combined")

            # 2. Aggregated forecast
            
            if payload.aggregated is not None:

                agg_fc = payload.aggregated

                if isinstance(agg_fc, pd.Series):

                    agg_fc = agg_fc.to_frame(name="value")

                agg_fc.to_excel(writer, sheet_name="Aggregated")

            # 3. Aggregated history
            
            agg_hist = payload.metadata.get("aggregated_history")

            if agg_hist is not None:

                if isinstance(agg_hist, pd.Series):

                    agg_hist = agg_hist.to_frame(name="value")

                agg_hist.to_excel(writer, sheet_name="Aggregated_History")

            # 4. Aggregated combined
           
            agg_combined = payload.metadata.get("aggregated_combined")

            if agg_combined is not None:

                agg_combined.to_excel(writer, sheet_name="Aggregated_Combined")

            # 5. Diagnostics (individual)
            
            for work_type, diag in payload.diagnostics.items():

                diag.summary().to_excel(writer, sheet_name=f"{work_type}_diagnostics", index=False)

                diag.residuals_frame().to_excel(writer, sheet_name=f"{work_type}_residuals")

            # 6. Aggregated diagnostics
            
            if payload.aggregated_diagnostics is not None:

                ad = payload.aggregated_diagnostics

                ad.summary().to_excel(writer, sheet_name="Aggregated_Diagnostics", index=False)

                ad.residuals_frame().to_excel(writer, sheet_name="Aggregated_Residuals")

            # 7. Metadata sheet
            
            meta_df = pd.DataFrame.from_dict(payload.metadata, orient="index")

            meta_df.to_excel(writer, sheet_name="Metadata")

    def _export_csv(self, path, loader, model, forecast, future_index):

        """
        Write a single combined CSV file containing history + forecast.

        Parameters
        ----------
        path : str
            Output CSV file path.

        loader : DataLoader
            Provides historical data.

        model : SeriesDecomposition
            Fitted decomposition model (unused for CSV export).

        forecast : pd.Series or None
            Forecasted values.

        future_index : pd.DatetimeIndex or None
            Index for forecast horizon.

        Notes
        -----
        CSV export is intentionally minimal and includes only the combined frame.
        """

        combined = self._combined_frame(loader, forecast, future_index)

        combined.to_csv(path, index=False)

    def _export_excel(self, path, loader, model, forecast, future_index, diagnostics = None):

        """
        Write a multi‑sheet Excel workbook for a single‑series run.

        Sheets include:
            * Combined history + forecast
            * History
            * Forecast
            * Trend
            * Seasonal factors over time
            * Seasonal cycle
            * Fitted values
            * Residuals
            * Diagnostics summary
            * Anomalies (if present)

        Parameters
        ----------
        path : str
            Output Excel file path.

        loader : DataLoader
            Provides historical data.

        model : SeriesDecomposition
            Fitted decomposition model.

        forecast : pd.Series or None
            Forecasted values.

        future_index : pd.DatetimeIndex or None
            Index for forecast horizon.

        diagnostics : DiagnosticsEngine, optional
            Diagnostics object for summary and residuals export.
        """

        with pd.ExcelWriter(path) as writer:

            # Combined history + forecast

            combined = self._combined_frame(loader, forecast, future_index)

            combined.to_excel(writer, sheet_name="Combined", index=False)

            # History

            hist = loader.data.copy()

            hist.columns = ["value"]

            hist.to_excel(writer, sheet_name="History", index=True)

            # Forecast

            if forecast is not None:

                fc_df = pd.DataFrame({"forecast": forecast})

                fc_df.to_excel(writer, sheet_name="Forecast", index=True)

            # Trend

            trend_df = pd.DataFrame({"trend": model.trend_})

            trend_df.to_excel(writer, sheet_name="Trend", index=True)

            # Seasonal factors over time

            seasonal_full_df = pd.DataFrame({"seasonal_factor": model.seasonal_factors_})

            seasonal_full_df.to_excel(writer, sheet_name="Seasonal Full", index=True)

            # Seasonal cycle

            cycle_df = pd.DataFrame({

                "season": list(range(len(model.seasonal_factors))),

                "factor": model.seasonal_factors

            })

            cycle_df.to_excel(writer, sheet_name="Seasonal Cycle", index=False)

            # Fitted values

            fitted_df = pd.DataFrame({"fitted": model.fitted_})

            fitted_df.to_excel(writer, sheet_name="Fitted", index=True)

            # Residuals

            residual_df = pd.DataFrame({"residual": model.residual_})

            residual_df.to_excel(writer, sheet_name="Residuals", index=True)

            # Diagnostics summary

            if diagnostics is not None:

                diag_df = diagnostics.summary()

                diag_df.to_excel(writer, sheet_name="Diagnostics", index=False)

                # Residuals

                residuals_df = diagnostics.residuals_frame()

                residuals_df.to_excel(writer, sheet_name="Residuals2", index=True)

                # Anomalies

                if diagnostics.anomalies is not None and not diagnostics.anomalies.empty:

                    diagnostics.anomalies.to_excel(writer, sheet_name="Anomalies", index=True)

    def _combined_frame(self, loader, forecast, future_index):

        """
        Construct a tidy combined DataFrame of history + forecast.

        The output contains:
            * ``timestamp`` — datetime index
            * ``value`` — numeric value
            * ``is_forecast`` — boolean flag

        Parameters
        ----------
        loader : DataLoader
            Provides historical data.

        forecast : pd.Series or None
            Forecasted values.

        future_index : pd.DatetimeIndex or None
            Index for forecast horizon.

        Returns
        -------
        pd.DataFrame
            Combined tidy DataFrame suitable for CSV or Excel export.

        Notes
        -----
        Values are rounded according to :class:`ExportConfig.rounding`.
        """

        hist = loader.data.copy()

        hist.columns = ["value"]

        hist["is_forecast"] = False

        if forecast is not None:

            fc_df = pd.DataFrame({"value": forecast}, index=future_index)

            fc_df["is_forecast"] = True

            combined = pd.concat([hist, fc_df])

        else:

            combined = hist

        combined["value"] = combined["value"].round(self.config.rounding)

        combined = combined.reset_index().rename(columns={"index": "timestamp"})

        return combined
