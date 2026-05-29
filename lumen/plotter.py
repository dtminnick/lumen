
# lumen/plotter.py

"""
Enhanced plotting utilities for Lumen.

The :class:`Plotter` class provides a suite of visualization tools for
decomposition, forecasting, and diagnostics. It supports:

    * Actual vs trend vs fitted plots
    * Seasonal cycle visualization
    * Seasonal factors over time
    * Residual diagnostics (distribution, z‑scores, anomalies)
    * Continuity checks
    * Error metrics
    * Forecast vs actual
    * Trend vs seasonal strength
    * Variance contribution analysis

Plots may optionally be saved to disk if a ``save_dir`` is provided.
"""

import matplotlib.pyplot as plt
from pathlib import Path
import pandas as pd
import numpy as np

class Plotter:

    """
    Visualization helper for Lumen decomposition, forecasting, and diagnostics.

    This class centralizes all plotting logic used across the Lumen pipeline.
    It supports both interactive use (displaying plots) and batch export
    (saving plots to a directory).

    Parameters
    ----------
    save_dir : str or Path, optional
        Directory where plots should be saved. If ``None``, plots are not saved.
        If provided, the directory is created automatically.

    Attributes
    ----------
    save_dir : Path or None
        Directory where plots are written, or ``None`` if saving is disabled.
    """

    def __init__(self, save_dir=None):

        """
        Initialize the plotter.

        Parameters
        ----------
        save_dir : str or Path, optional
            Directory where plots should be saved. If omitted, plots are not
            written to disk.

        Notes
        -----
        * The directory is created automatically if it does not exist.
        * All plots are saved using ``dpi=150`` for clarity.
        """

        self.save_dir = Path(save_dir) if save_dir else None

        if self.save_dir:

            self.save_dir.mkdir(parents=True, exist_ok=True)

    def _save(self, filename):

        """
        Save the current Matplotlib figure to ``save_dir`` if saving is enabled.

        Parameters
        ----------
        filename : str
            Name of the file to write (e.g., ``"residuals.png"``).
        """

        if self.save_dir:

            plt.savefig(self.save_dir / filename, dpi=150)

    def _validate_series(self, series: pd.Series):

        """
        Ensure that a series is indexed by ``DatetimeIndex``.

        Parameters
        ----------
        series : pd.Series
            Series to validate.

        Raises
        ------
        ValueError
            If the index is not a ``DatetimeIndex``.
        """

        if not isinstance(series.index, pd.DatetimeIndex):

            raise ValueError("Series must be indexed by DatetimeIndex.")

    def plot_decomposition(self, series, trend, fitted, filename="decomposition.png"):

        """
        Plot actual values, trend, and fitted values on a single chart.

        Parameters
        ----------
        series : pd.Series
            Original time series.

        trend : pd.Series
            Trend component.

        fitted : pd.Series
            Fitted values from decomposition.

        filename : str, default "decomposition.png"
            Output filename if saving is enabled.
        """

        self._validate_series(series)

        plt.figure(figsize=(12, 6))

        plt.plot(series.index, series.values, label="Actual", linewidth=2)

        plt.plot(trend.index, trend.values, label="Trend", linewidth=2)

        plt.plot(fitted.index, fitted.values, label="Fitted", linewidth=2)

        plt.title("Decomposition: Actual vs Trend vs Fitted")

        plt.legend()

        plt.tight_layout()

        self._save(filename)

        plt.close()

    def plot_seasonal_cycle(self, seasonal_cycle, filename="seasonal_cycle.png"):

        """
        Plot the seasonal cycle (one full seasonal period).

        Parameters
        ----------
        seasonal_cycle : array-like
            Seasonal factors for one full cycle.

        filename : str, default "seasonal_cycle.png"
            Output filename if saving is enabled.
        """

        plt.figure(figsize=(10, 4))

        plt.plot(seasonal_cycle, marker="o")

        plt.title("Seasonal Cycle")

        plt.tight_layout()

        self._save(filename)

        plt.close()

    def plot_seasonal_factors_over_time(self, series, seasonal_factors_full, filename="seasonal_factors_over_time.png"):

        """
        Plot seasonal factors expanded across the full timeline.

        Parameters
        ----------
        series : pd.Series
            Original time series (used for index).

        seasonal_factors_full : pd.Series
            Seasonal factors aligned with the full timeline.

        filename : str, default "seasonal_factors_over_time.png"
            Output filename if saving is enabled.
        """

        self._validate_series(series)

        plt.figure(figsize=(12, 4))

        plt.plot(series.index, seasonal_factors_full.values, linewidth=2)

        plt.title("Seasonal Factors Over Time")

        plt.tight_layout()

        self._save(filename)

        plt.close()

    def plot_residuals(self, residuals, filename="residuals.png"):

        """
        Plot multiplicative residuals over time.

        Parameters
        ----------
        residuals : pd.Series
            Multiplicative residuals (``y / y_hat``).

        filename : str, default "residuals.png"
            Output filename if saving is enabled.
        """

        self._validate_series(residuals)

        plt.figure(figsize=(12, 4))

        plt.plot(residuals.index, residuals.values)

        plt.axhline(1.0, color="black", linestyle="--")

        plt.title("Residuals Over Time (Multiplicative)")

        plt.tight_layout()

        self._save(filename)

        plt.close()

    def plot_residual_distribution(self, residuals, filename="residual_distribution.png"):

        """
        Plot a histogram of residual values.

        Parameters
        ----------
        residuals : pd.Series
            Multiplicative residuals.

        filename : str, default "residual_distribution.png"
            Output filename if saving is enabled.
        """

        plt.figure(figsize=(8, 4))

        plt.hist(residuals.values, bins=30, edgecolor="black")

        plt.title("Residual Distribution")

        plt.tight_layout()

        self._save(filename)

        plt.close()

    def plot_residual_zscores(self, diagnostics, filename="residual_zscores.png"):

        """
        Plot z‑scores of residuals with anomaly thresholds.

        Parameters
        ----------
        diagnostics : DiagnosticsEngine
            Diagnostics object containing residuals and anomaly thresholds.

        filename : str, default "residual_zscores.png"
            Output filename if saving is enabled.
        """

        z = diagnostics.anomalies["z_score"] if diagnostics.anomalies is not None else None

        r = diagnostics.residuals

        plt.figure(figsize=(12, 4))

        plt.plot(r.index, (r - r.mean()) / (r.std() + 1e-8), label="Z-score")

        plt.axhline(diagnostics.config.residual_zscore_threshold, color="red", linestyle="--")

        plt.axhline(-diagnostics.config.residual_zscore_threshold, color="red", linestyle="--")

        plt.title("Residual Z-Scores")

        plt.tight_layout()

        self._save(filename)

        plt.close()

    def plot_anomalies(self, diagnostics, filename="anomalies.png"):

        """
        Plot detected anomalies as red scatter points.

        Parameters
        ----------
        diagnostics : DiagnosticsEngine
            Diagnostics object containing anomaly DataFrame.

        filename : str, default "anomalies.png"
            Output filename if saving is enabled.
        """

        if diagnostics.anomalies is None or diagnostics.anomalies.empty:

            return

        plt.figure(figsize=(12, 4))

        plt.scatter(
            diagnostics.anomalies.index,
            diagnostics.anomalies["residual"],
            color="red",
            label="Anomaly",
            zorder=5
        )

        plt.title("Detected Anomalies")

        plt.legend()

        plt.tight_layout()

        self._save(filename)

        plt.close()

    def plot_continuity(self, diagnostics, filename="continuity.png"):

        """
        Visualize continuity between the last historical point and first forecast.

        Parameters
        ----------
        diagnostics : DiagnosticsEngine
            Contains continuity report with ``last_history`` and ``first_forecast``.

        filename : str, default "continuity.png"
            Output filename if saving is enabled.
        """

        report = diagnostics.continuity_report

        if not report:

            return

        last_hist = report["last_history"]

        first_fc = report["first_forecast"]

        plt.figure(figsize=(6, 4))

        plt.bar(["Last History", "First Forecast"], [last_hist, first_fc])

        plt.title("Continuity Check")

        plt.tight_layout()

        self._save(filename)

        plt.close()

    def plot_error_metrics(self, diagnostics, filename="error_metrics.png"):

        """
        Plot error metrics (MAE, RMSE, MAPE, SMAPE) as a bar chart.

        Parameters
        ----------
        diagnostics : DiagnosticsEngine
            Contains computed error metrics.

        filename : str, default "error_metrics.png"
            Output filename if saving is enabled.
        """

        metrics = diagnostics.error_metrics

        plt.figure(figsize=(6, 4))

        plt.bar(metrics.keys(), metrics.values())

        plt.title("Error Metrics")

        plt.tight_layout()

        self._save(filename)

        plt.close()

    def plot_forecast_vs_actual(self, history, forecast, future_index, filename="forecast_vs_actual.png"):

        """
        Plot historical values and forecasted values on a single chart.

        Parameters
        ----------
        history : pd.Series
            Historical time series.

        forecast : array-like
            Forecasted values.

        future_index : pd.DatetimeIndex
            Index corresponding to forecast horizon.

        filename : str, default "forecast_vs_actual.png"
            Output filename if saving is enabled.
        """

        self._validate_series(history)

        plt.figure(figsize=(12, 5))

        plt.plot(history.index, history.values, label="Actual", linewidth=2)

        plt.plot(future_index, forecast, label="Forecast", linewidth=2)

        plt.title("Forecast vs Actual")

        plt.legend()

        plt.tight_layout()

        self._save(filename)

        plt.close()

    def plot_strength_bars(self, diagnostics, filename="strength_bars.png"):

        """
        Plot trend strength and seasonal strength as a bar chart.

        Parameters
        ----------
        diagnostics : DiagnosticsEngine
            Contains ``trend_strength`` and ``seasonal_strength``.

        filename : str, default "strength_bars.png"
            Output filename if saving is enabled.
        """

        if diagnostics is None:

            return

        strengths = {

            "Trend Strength": diagnostics.trend_strength,

            "Seasonal Strength": diagnostics.seasonal_strength

        }

        plt.figure(figsize=(6, 4))

        plt.bar(strengths.keys(), strengths.values(), color=["#4C72B0", "#55A868"])
        
        plt.ylim(0, 1)

        plt.title("Trend vs Seasonal Strength")

        plt.tight_layout()

        self._save(filename)

        plt.close()

    def plot_variance_contributions(self, diagnostics, filename="variance_contributions.png"):

        """
        Plot variance contributions of trend, seasonality, and residuals.

        Parameters
        ----------
        diagnostics : DiagnosticsEngine
            Provides history, fitted values, trend, and seasonal factors.

        filename : str, default "variance_contributions.png"
            Output filename if saving is enabled.

        Notes
        -----
        Variance is computed in additive space, consistent with Hyndman's
        definitions of component strength.
        """

        if diagnostics is None:

            return

        # Additive residuals

        E_add = diagnostics.history.values - diagnostics.fitted.values

        # Additive seasonal effect

        S_add = diagnostics.trend.values * (diagnostics.seasonal_full.values - 1)

        # Additive trend deviation

        T_add = diagnostics.trend.values - diagnostics.trend.values.mean()

        var_e = np.var(E_add, ddof=1)

        var_s = np.var(S_add, ddof=1)

        var_t = np.var(T_add, ddof=1)

        contributions = {
            "Trend": var_t,
            "Seasonality": var_s,
            "Residual": var_e
        }

        plt.figure(figsize=(7, 4))

        plt.bar(contributions.keys(), contributions.values(), color=["#4C72B0", "#55A868", "#C44E52"])

        plt.title("Variance Contributions")

        plt.tight_layout()

        self._save(filename)

        plt.close()

    def plot_all(
        self, 
        series, 
        model, 
        forecast=None, 
        future_index=None, 
        diagnostics=None,
        prefix = None
    ):

        """
        Generate a full suite of decomposition, diagnostic, and forecast plots.

        Parameters
        ----------
        series : pd.Series
            Historical time series.

        model : SeriesDecomposition
            Fitted decomposition model.

        forecast : pd.Series or None
            Forecasted values.

        future_index : pd.DatetimeIndex or None
            Index for forecast horizon.

        diagnostics : DiagnosticsEngine or None
            Diagnostics object for residuals, anomalies, strengths, etc.

        prefix : str
            A string prepended to every filename (e.g., "RMD", "TRM", "INS").

        Notes
        -----
        Plots are saved with numbered filenames to ensure ordering.
        """

        # Ensure prefix ends with underscore if provided

        prefix = f"{prefix}_" if prefix else ""

        self.plot_decomposition(series, model.trend_, model.fitted_, f"{prefix}_01_decomposition.png")

        self.plot_seasonal_cycle(model.seasonal_factors, f"{prefix}_02_seasonal_cycle.png")

        self.plot_seasonal_factors_over_time(series, model.seasonal_factors_, f"{prefix}_03_seasonal_factors_over_time.png")

        # Residual diagnostics

        self.plot_residuals(model.residual_, f"{prefix}_04_residuals.png")

        self.plot_residual_distribution(model.residual_, f"{prefix}_05_residual_distribution.png")

        if diagnostics is not None:
            self.plot_residual_zscores(diagnostics, f"{prefix}_06_residual_zscores.png")

            self.plot_anomalies(diagnostics, f"{prefix}_07_anomalies.png")

            self.plot_continuity(diagnostics, f"{prefix}_08_continuity.png")

            self.plot_error_metrics(diagnostics, f"{prefix}_09_error_metrics.png")

        if forecast is not None and future_index is not None:

            self.plot_forecast_vs_actual(series, forecast, future_index, f"{prefix}_10_forecast_vs_actual.png")

        self.plot_strength_bars(diagnostics, f"{prefix}_11_strength_bars.png")

        self.plot_variance_contributions(diagnostics, f"{prefix}_12_variance_contributions.png")
