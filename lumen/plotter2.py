
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

    def __init__(self, save_dir=None, width=12, height=6):
        self.save_dir = Path(save_dir) if save_dir else None
        if self.save_dir:
            self.save_dir.mkdir(parents=True, exist_ok=True)

        self.width = width
        self.height = height

    # ---------------------------------------------------------
    # Save helper — now saves the *specific* figure
    # ---------------------------------------------------------
    def _save(self, fig, filename):
        if self.save_dir:
            fig.savefig(
                self.save_dir / filename,
                dpi=150,
                bbox_inches=None,   # prevent auto-trimming
                pad_inches=0.1
            )

    def _validate_series(self, series: pd.Series):
        if not isinstance(series.index, pd.DatetimeIndex):
            raise ValueError("Series must be indexed by DatetimeIndex.")

    # ---------------------------------------------------------
    # Plotting functions — all now pass fig to _save()
    # ---------------------------------------------------------

    def plot_all(
        self, 
        series, 
        model, 
        forecast=None, 
        future_index=None, 
        diagnostics=None,
        prefix=None
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
        """

        # Ensure prefix ends with underscore if provided
        prefix = f"{prefix}_" if prefix else ""

        # 1. Decomposition
        self.plot_decomposition(
            series, 
            model.trend_, 
            model.fitted_, 
            f"{prefix}01_decomposition.png"
        )

        # 2. Seasonal cycle
        self.plot_seasonal_cycle(
            model.seasonal_factors, 
            f"{prefix}02_seasonal_cycle.png"
        )

        # 3. Seasonal factors over time
        self.plot_seasonal_factors_over_time(
            series, 
            model.seasonal_factors_, 
            f"{prefix}03_seasonal_factors_over_time.png"
        )

        # 4. Residual diagnostics
        self.plot_residuals(
            model.residual_, 
            f"{prefix}04_residuals.png"
        )

        self.plot_residual_distribution(
            model.residual_, 
            f"{prefix}05_residual_distribution.png"
        )

        # 5. Diagnostics-dependent plots
        if diagnostics is not None:

            self.plot_residual_zscores(
                diagnostics, 
                f"{prefix}06_residual_zscores.png"
            )

            self.plot_anomalies(
                diagnostics, 
                f"{prefix}07_anomalies.png"
            )

            self.plot_continuity(
                diagnostics, 
                f"{prefix}08_continuity.png"
            )

            self.plot_error_metrics(
                diagnostics, 
                f"{prefix}09_error_metrics.png"
            )

        # 6. Forecast vs actual
        if forecast is not None and future_index is not None:

            self.plot_forecast_vs_actual(
                series, 
                forecast, 
                future_index, 
                f"{prefix}10_forecast_vs_actual.png"
            )

        # 7. Strength bars
        self.plot_strength_bars(
            diagnostics, 
            f"{prefix}11_strength_bars.png"
        )

        # 8. Variance contributions
        self.plot_variance_contributions(
            diagnostics, 
            f"{prefix}12_variance_contributions.png"
        )


    def plot_decomposition(self, series, trend, fitted, filename="decomposition.png"):
        self._validate_series(series)
        fig, ax = plt.subplots(figsize=(self.width, self.height))

        ax.plot(series.index, series.values, label="Actual", linewidth=2)
        ax.plot(trend.index, trend.values, label="Trend", linewidth=2)
        ax.plot(fitted.index, fitted.values, label="Fitted", linewidth=2)

        ax.set_title("Decomposition: Actual vs Trend vs Fitted")
        ax.legend()

        fig.subplots_adjust(left=0.08, right=0.98, top=0.90, bottom=0.12)
        self._save(fig, filename)
        plt.close(fig)

    def plot_seasonal_cycle(self, seasonal_cycle, filename="seasonal_cycle.png"):
        fig, ax = plt.subplots(figsize=(self.width, self.height))
        ax.plot(seasonal_cycle, marker="o")
        ax.set_title("Seasonal Cycle")

        fig.subplots_adjust(left=0.08, right=0.98, top=0.90, bottom=0.12)
        self._save(fig, filename)
        plt.close(fig)

    def plot_seasonal_factors_over_time(self, series, seasonal_factors_full, filename="seasonal_factors_over_time.png"):
        self._validate_series(series)
        fig, ax = plt.subplots(figsize=(self.width, self.height))

        ax.plot(series.index, seasonal_factors_full.values, linewidth=2)
        ax.set_title("Seasonal Factors Over Time")

        fig.subplots_adjust(left=0.08, right=0.98, top=0.90, bottom=0.12)
        self._save(fig, filename)
        plt.close(fig)

    def plot_residuals(self, residuals, filename="residuals.png"):
        self._validate_series(residuals)
        fig, ax = plt.subplots(figsize=(self.width, self.height))

        ax.plot(residuals.index, residuals.values)
        ax.axhline(1.0, color="black", linestyle="--")
        ax.set_title("Residuals Over Time (Multiplicative)")

        fig.subplots_adjust(left=0.08, right=0.98, top=0.90, bottom=0.12)
        self._save(fig, filename)
        plt.close(fig)

    def plot_residual_distribution(self, residuals, filename="residual_distribution.png"):
        fig, ax = plt.subplots(figsize=(self.width, self.height))
        ax.hist(residuals.values, bins=30, edgecolor="black")
        ax.set_title("Residual Distribution")

        fig.subplots_adjust(left=0.08, right=0.98, top=0.90, bottom=0.12)
        self._save(fig, filename)
        plt.close(fig)

    def plot_residual_zscores(self, diagnostics, filename="residual_zscores.png"):
        r = diagnostics.residuals
        fig, ax = plt.subplots(figsize=(self.width, self.height))

        ax.plot(r.index, (r - r.mean()) / (r.std() + 1e-8), label="Z-score")
        ax.axhline(diagnostics.config.residual_zscore_threshold, color="red", linestyle="--")
        ax.axhline(-diagnostics.config.residual_zscore_threshold, color="red", linestyle="--")
        ax.set_title("Residual Z-Scores")

        fig.subplots_adjust(left=0.08, right=0.98, top=0.90, bottom=0.12)
        self._save(fig, filename)
        plt.close(fig)

    def plot_anomalies(self, diagnostics, filename="anomalies.png"):
        if diagnostics.anomalies is None or diagnostics.anomalies.empty:
            return

        fig, ax = plt.subplots(figsize=(self.width, self.height))
        ax.scatter(
            diagnostics.anomalies.index,
            diagnostics.anomalies["residual"],
            color="red",
            label="Anomaly",
            zorder=5
        )
        ax.set_title("Detected Anomalies")
        ax.legend()

        fig.subplots_adjust(left=0.08, right=0.98, top=0.90, bottom=0.12)
        self._save(fig, filename)
        plt.close(fig)

    def plot_continuity(self, diagnostics, filename="continuity.png"):
        report = diagnostics.continuity_report
        if not report:
            return

        fig, ax = plt.subplots(figsize=(self.width, self.height))
        ax.bar(["Last History", "First Forecast"], [report["last_history"], report["first_forecast"]])
        ax.set_title("Continuity Check")

        fig.subplots_adjust(left=0.08, right=0.98, top=0.90, bottom=0.12)
        self._save(fig, filename)
        plt.close(fig)

    def plot_error_metrics(self, diagnostics, filename="error_metrics.png"):
        metrics = diagnostics.error_metrics
        fig, ax = plt.subplots(figsize=(self.width, self.height))

        ax.bar(metrics.keys(), metrics.values())
        ax.set_title("Error Metrics")

        fig.subplots_adjust(left=0.08, right=0.98, top=0.90, bottom=0.12)
        self._save(fig, filename)
        plt.close(fig)

    def plot_forecast_vs_actual(self, history, forecast, future_index, filename="forecast_vs_actual.png"):
        self._validate_series(history)
        fig, ax = plt.subplots(figsize=(self.width, self.height))

        ax.plot(history.index, history.values, label="Actual", linewidth=2)
        ax.plot(future_index, forecast, label="Forecast", linewidth=2)
        ax.set_title("Forecast vs Actual")
        ax.legend()

        fig.subplots_adjust(left=0.08, right=0.98, top=0.90, bottom=0.12)
        self._save(fig, filename)
        plt.close(fig)

    def plot_strength_bars(self, diagnostics, filename="strength_bars.png"):
        if diagnostics is None:
            return

        strengths = {
            "Trend Strength": diagnostics.trend_strength,
            "Seasonal Strength": diagnostics.seasonal_strength
        }

        fig, ax = plt.subplots(figsize=(self.width, self.height))
        ax.bar(strengths.keys(), strengths.values(), color=["#4C72B0", "#55A868"])
        ax.set_ylim(0, 1)
        ax.set_title("Trend vs Seasonal Strength")

        fig.subplots_adjust(left=0.08, right=0.98, top=0.90, bottom=0.12)
        self._save(fig, filename)
        plt.close(fig)

    def plot_variance_contributions(self, diagnostics, filename="variance_contributions.png"):
        if diagnostics is None:
            return

        E_add = diagnostics.history.values - diagnostics.fitted.values
        S_add = diagnostics.trend.values * (diagnostics.seasonal_full.values - 1)
        T_add = diagnostics.trend.values - diagnostics.trend.values.mean()

        contributions = {
            "Trend": np.var(T_add, ddof=1),
            "Seasonality": np.var(S_add, ddof=1),
            "Residual": np.var(E_add, ddof=1)
        }

        fig, ax = plt.subplots(figsize=(self.width, self.height))
        ax.bar(contributions.keys(), contributions.values(), color=["#4C72B0", "#55A868", "#C44E52"])
        ax.set_title("Variance Contributions")

        fig.subplots_adjust(left=0.08, right=0.98, top=0.90, bottom=0.12)
        self._save(fig, filename)
        plt.close(fig)
