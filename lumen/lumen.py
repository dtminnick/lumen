
"""
High-level orchestration class for the Lumen forecasting pipeline.

The `Lumen` class provides a simple, unified interface for running the
entire single-series forecasting workflow:

* Load and validate data,
* Fit multiplicative STL decomposition,
* Generate forecasts,
* Compute diagnostics (residuals, anomalies, strengths, continuity), and
* Export results to csv or xlsx.

This class is intentionally lightweight. It delegates:

* Data loading to class `DataLoader`,
* Decomposition and forecasting class `ForecastEngine`,
* Diagnostics to class `DiagnosticsEngine`, and
* Export to class `ExportEngine`.

Most users interact with class `Lumen` directly for single-series forecasting,
or with class `Orchestrator` for multi-series workflows.
"""

from __future__ import annotations

from lumen.data_loader import DataLoader, DataConfig
from lumen.forecast_engine import ForecastEngine
from lumen.export_engine import ExportEngine, ExportConfig
from lumen.diagnostics_engine import DiagnosticsEngine

class Lumen:

    """
    High-level orchestration class for single-series Lumen forecasting.

    This class provides a clean, minimal API for running the full forecasting
    pipeline on a single time series. It handles:

    * Data loading,
    * STL decomposition,
    * Forecast generation,
    * Diagnostics computation, and
    * Export to disk.

    Parameters
    ----------
    **data_config : DataConfig**

    Configuration for loading and validating the input time series.

    **export_config : ExportConfig, optional**

    Configuration for controlling export format and rounding.

    Attributes
    ----------
    **loader : DataLoader**

    Responsible for loading, validating, and regularizing the dataset.

    **engine : ForecastEngine or None**

    Forecasting engine created during method `fit`.

    **exporter : ExportEngine**

    Writes results to disk.

    **diagnostics : DiagnosticsEngine or None**

    Diagnostics computed after fitting or forecasting.

    **_forecast : pd.Series or None**

    Forecasted values (if method `forecast` has been called).

    **_future_index : pd.DatetimeIndex or None**

    Index corresponding to the forecast horizon.
        """

    def __init__(self, data_config: DataConfig, export_config: ExportConfig = ExportConfig()):
        
        """
        Initialize the high-level Lumen forecasting pipeline.

        This constructor wires together all major components required for a
        single-series forecasting workflow, including:

        * `DataLoader`, loads and validates the input time series,
        * `ForecastEngine`, performs STL decomposition + forecasting,
        * `ExportEngine`, writes results to disk, and
        * `DiagnosticsEngine`, computed after fitting or forecasting.

        No data is loaded and no model is fitted at initialization time.  
        Call method `load_file` followed by method `fit` and method `forecast` to run
        the full pipeline.

        Parameters
        ----------
        **data_config : DataConfig**

        Configuration describing how input data should be parsed, validated,
        and interpreted (date column, value column, frequency override, etc.).

        **export_config : ExportConfig, optional**

        Configuration controlling export format (csv or xlsx) and rounding.
        Defaults to a new class `ExportConfig` instance.

        Attributes
        ----------
        **loader : DataLoader**

        Responsible for loading, validating, and regularizing the dataset.

        **engine : ForecastEngine or None**

        Created during method `fit`. Performs STL decomposition and forecasting.

        **exporter : ExportEngine**

        Writes decomposition, forecast, diagnostics, and metadata to disk.

        **diagnostics : DiagnosticsEngine or None**

        Computed after fitting or forecasting. Contains residuals, anomalies,
        error metrics, continuity checks, and component strengths.

        **_is_fitted : bool**

        Indicates whether method `fit` has been successfully called.

        **_forecast : pd.Series or None**

        Forecasted values produced by method `forecast`.

        **_future_index : pd.DatetimeIndex or None**
            
        Index corresponding to the forecast horizon.

        Notes
        -----
        This class is intentionally minimal. It does not perform decomposition,
        forecasting, or diagnostics itself, it orchestrates the components that do.
        """
        
        self.data_config = data_config

        self.export_config = export_config

        self.loader = DataLoader(self.data_config)

        self.engine = None

        self.exporter = ExportEngine(self.export_config)

        self._is_fitted = False

        self._forecast = None

        self._future_index = None

        self.diagnostics = None

    def load_file(self, path: str) -> None:

        """
        Load and validate a time series file.

        Parameters
        ----------
        **path : str**

        Path to a CSV or XLSX file.

        Notes
        -----
        After loading, the cleaned DataFrame is available via
        `self.loader.data`.
        """

        self.loader.load_file(path)

    def fit(self) -> None:

        """
        Fit the STL decomposition model on the loaded series.

        This method:

        * Creates a class `ForecastEngine`,
        * Fits the multiplicative STL decomposition,
        * Computes diagnostics (without forecast), and
        * Resets any previous forecast state.

        Raises
        ------
        **ValueError**

        If data has not been loaded.
        """

        self.engine = ForecastEngine(self.loader)

        self.engine.fit()

        self._is_fitted = True

        self._forecast = None

        self._future_index = None

        # Diagnostics with no forecast yet

        series = self.loader.get_series()

        self.diagnostics = DiagnosticsEngine(
            history=series,
            fitted=self.engine.model.fitted_,
            forecast=None,
            trend=self.engine.model.trend_,
            seasonal_full=self.engine.model.seasonal_factors_
        )

        self.diagnostics.compute_all()

    def forecast(self, steps: int):

        """
        Generate a forecast for the specified number of periods.

        This method:

        * Ensures the model has been fitted,
        * Calls method `ForecastEngine.forecast`, and
        * Recomputes diagnostics including continuity and anomalies.

        Parameters
        ----------
        **steps : int**

        Number of periods to forecast.

        Returns
        -------
        **pd.Series**

        Forecasted values indexed by future timestamps.

        Raises
        ------
        **ValueError**

        If method `fit` has not been called.
        """

        if not self._is_fitted:

            raise ValueError("Call fit() before forecast().")

        self._forecast = self.engine.forecast(steps)

        self._future_index = self.engine.future_index_

        # Recompute diagnostics with forecast

        series = self.loader.get_series()

        self.diagnostics = DiagnosticsEngine(
            history=series,
            fitted=self.engine.model.fitted_,
            forecast=self._forecast,
            trend=self.engine.model.trend_,
            seasonal_full=self.engine.model.seasonal_factors_
        )

        self.diagnostics.compute_all()

        return self._forecast

    def export(self, path: str) -> None:

        """
        Export decomposition, forecast, and diagnostics to disk.

        Parameters
        ----------
        **path : str**

        Output file path (csv or xlsx).

        Raises
        ------
        **ValueError**

        If method `forecast` has not been called.
        """

        if self._forecast is None:

            raise ValueError("Call forecast() before export().")

        self.exporter.export(
            path=path,
            loader=self.loader,
            model=self.engine.model,
            forecast=self._forecast,
            future_index=self._future_index,
            diagnostics=self.diagnostics
        )

    @property
    def forecast_df(self):

        """
        Return the forecasted values as a Series or DataFrame.
        """

        return self._forecast

    @property
    def trend(self):

        """
        Return the trend component from the decomposition.
        """

        return self.engine.model.trend_

    @property
    def seasonal_factors(self):

        """
        Return the seasonal cycle (one full seasonal period).
        """

        return self.engine.model.seasonal_factors

    @property
    def seasonal_factors_(self):

        """
        Return seasonal factors expanded across the full timeline.
        """

        return self.engine.model.seasonal_factors_

    @property
    def residuals(self):

        """
        Return residuals from the diagnostics engine.
        """

        return self.diagnostics.residuals if self.diagnostics else None
