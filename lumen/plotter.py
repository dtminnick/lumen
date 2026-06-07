
"""
Plotting utilities built on top of Altair.

This module defines the `Plotter` class, which provides a unified interface
for generating a wide range of diagnostic and exploratory time-series
visualizations. It standardizes figure dimensions, manages an optional
output directory, and wraps Altair chart construction for consistency
across plots.
"""

import altair as alt
import pandas as pd
import numpy as np
from pathlib import Path

class Plotter:

    """A convenience wrapper for creating and saving Altair charts.

    The `Plotter` class centralizes common plotting configuration such as
    default figure size, pixel conversion, and output directory management.
    It provides a suite of visualization methods for decomposition,
    seasonality, residuals, anomalies, forecast comparison, and diagnostic
    metrics.

    Attributes
    ----------
    
    **save_dir : Path | None**
     
    Directory where generated charts will be saved. If None, charts are not written to disk.
    
    **width_px : int** 
    
    Default chart width in pixels.
    
    **height_px : int**
     
    Default chart height in pixels.
    """

    def __init__(self, save_dir=None, width=12, height=6):

        """
        Create a new `Plotter`.

        Parameters
        ----------
        **save_dir : str | Path | None**
         
        Optional path to a directory where charts should be saved. If provided, the directory
        is created if it does not already exist.

        **width : int**
        
        Default width in inches for charts.

        **height : int** 
        
        Default height in inches for charts.

        Raises
        ------
        **OSError**
        
        If the save directory cannot be created.
        """

        self.save_dir = Path(save_dir) if save_dir else None
        if self.save_dir:
            self.save_dir.mkdir(parents=True, exist_ok=True)

        # Altair uses pixels, not inches
        self.width_px = int(width * 80)
        self.height_px = int(height * 80)

    def _save(self, chart, filename):

        """
        Save a chart to disk if a save directory is configured.

        Parameters
        ----------
        **chart : alt.Chart** 
        
        The Altair chart to save.

        **filename : str** 
        
        Name of the output file.

        Notes
        -----
        
        If no save directory is set, this method does nothing.
        """

        if self.save_dir:
            chart.save(str(self.save_dir / filename))

    def plot_decomposition(self, series, trend, fitted, filename="decomposition.png"):

        """
        Plot actual, trend, and fitted components of a decomposition.

        Parameters
        ----------
        **series : pd.Series**
         
        Original time series.
        
        **trend : pd.Series** 
        
        Trend component.
        
        **fitted : pd.Series** 
        
        Fitted values from the model.
        **filename : str** 
        
        Output filename.

        Returns
        -------
        **alt.Chart** 
        
        The generated decomposition chart.
        """

        df = pd.DataFrame({
            "date": series.index,
            "Actual": np.asarray(series.values).ravel(),
            "Trend": np.asarray(trend.values).ravel(),
            "Fitted": np.asarray(fitted.values).ravel()
        })

        chart = (
            alt.Chart(df)
            .transform_fold(["Actual", "Trend", "Fitted"], as_=["Component", "Value"])
            .mark_line()
            .encode(
                x=alt.X("date:T", title="Date", axis=alt.Axis(format="%Y-%m", labelAngle=270)),
                y=alt.Y("Value:Q", title="Value"),
                color="Component:N"
            )
            .properties(
                width=self.width_px,
                height=self.height_px,
                title="Decomposition: Actual vs Trend vs Fitted"
            )
        )

        self._save(chart, filename)
        return chart

    def plot_seasonal_cycle(self, seasonal_cycle, filename="seasonal_cycle.png"):

        """
        Plot a single seasonal cycle.

        Parameters
        ----------
        **seasonal_cycle : array-like** 
        
        Seasonal factors for one cycle.
        
        **filename : str**
        
        Output filename.

        Returns
        -------
        **alt.Chart**
        
        The seasonal cycle chart.
        """

        vals = np.asarray(seasonal_cycle).ravel()
        df = pd.DataFrame({
            "index": range(len(vals)),
            "value": vals
        })

        chart = (
            alt.Chart(df)
            .mark_line(point=True)
            .encode(
                x=alt.X("index:Q", title="Seasonal Position"),
                y=alt.Y("value:Q", title="Seasonal Factor")
            )
            .properties(
                width=self.width_px,
                height=self.height_px,
                title="Seasonal Cycle"
            )
        )

        self._save(chart, filename)
        return chart

    def plot_seasonal_factors_over_time(self, series, seasonal_factors_full, filename="seasonal_factors_over_time.png"):

        """
        Plot seasonal factors aligned with the time index.

        Parameters
        ----------
        **series : pd.Series** 
        
        Original time series (for index).
        
        **seasonal_factors_full : pd.Series**
        
        Full seasonal factors.
        
        **filename : str**
        
        Output filename.

        Returns
        -------
        **alt.Chart**
        
        The seasonal factors chart.
        """

        df = pd.DataFrame({
            "date": series.index,
            "value": np.asarray(seasonal_factors_full.values).ravel()
        })

        chart = (
            alt.Chart(df)
            .mark_line()
            .encode(
                x=alt.X("date:T", title="Date", axis=alt.Axis(format="%Y-%m", labelAngle=270)),
                y=alt.Y("value:Q", title = "Value")
            )
            .properties(
                width=self.width_px,
                height=self.height_px,
                title="Seasonal Factors Over Time"
            )
        )

        self._save(chart, filename)
        return chart

    def plot_residuals(self, residuals, filename="residuals.png"):

        """
        Plot residuals over time.

        Parameters
        ----------
        **residuals : pd.Series**
        
        Model residuals.
        
        **filename : str**
        
        Output filename.

        Returns
        -------
        **alt.Chart**
        
        The residual time-series chart.
        """

        df = pd.DataFrame({
            "date": residuals.index,
            "value": np.asarray(residuals.values).ravel()
        })

        chart = (
            alt.Chart(df)
            .mark_line()
            .encode(
                x=alt.X("date:T", title="Date", axis=alt.Axis(format="%Y-%m", labelAngle=270)),
                y=alt.Y("value:Q", title = "Value")
            )
            .properties(
                width=self.width_px,
                height=self.height_px,
                title="Residuals Over Time (Multiplicative)"
            )
        )

        self._save(chart, filename)
        return chart

    def plot_residual_distribution(self, residuals, filename="residual_distribution.png"):

        """
        Plot a histogram of residuals.

        Parameters
        ----------
        **residuals : pd.Series**
        
        Model residuals.
        
        **filename : str**
        
        Output filename.

        Returns
        -------
        **alt.Chart**
        
        The residual distribution chart.
        """

        df = pd.DataFrame({"value": np.asarray(residuals.values).ravel()})

        chart = (
            alt.Chart(df)
            .mark_bar()
            .encode(
                x=alt.X("value:Q", bin=alt.Bin(maxbins=30), title = "Value (Binned)"),
                y=alt.Y("count()", title = "Count")
            )
            .properties(
                width=self.width_px,
                height=self.height_px,
                title="Residual Distribution"
            )
        )

        self._save(chart, filename)
        return chart

    def plot_residual_zscores(self, diagnostics, filename="residual_zscores.png"):

        """
        Plot z-scores of residuals with threshold lines.

        Parameters
        ----------
        **diagnostics**
         
           Object containing residuals and configuration.
        **filename : str**
        
        Output filename.

        Returns
        -------
        **alt.Chart**
        
        The z-score chart with threshold rules.
        """

        r = diagnostics.residuals
        r_vals = np.asarray(r.values).ravel()
        z = (r_vals - r_vals.mean()) / (r_vals.std() + 1e-8)

        df = pd.DataFrame({"date": r.index, "z": z})
        threshold = diagnostics.config.residual_zscore_threshold

        chart = (
            alt.Chart(df)
            .mark_line()
            .encode(x=alt.X("date:T", title="Date", axis=alt.Axis(format="%Y-%m", labelAngle=270)), 
                    y=alt.Y("z:Q", title = "Value"))
            .properties(width=self.width_px, height=self.height_px)
        )

        rule = alt.Chart(
            pd.DataFrame({"y": [threshold, -threshold]})
        ).mark_rule(color="red").encode(y="y:Q")

        final = (chart + rule).properties(title="Residual Z-Scores")

        self._save(final, filename)
        return final

    def plot_anomalies(self, diagnostics, filename="anomalies.png"):

        """
        Plot detected anomalies as red points.

        Parameters
        ----------
        **diagnostics**
        
        Object containing anomaly information.

        **filename : str**
        
        Output filename.

        Returns
        -------
        **alt.Chart | None**
        
        The anomaly chart, or None if no anomalies exist.
        """

        if diagnostics.anomalies is None or diagnostics.anomalies.empty:
            return None

        df = diagnostics.anomalies.reset_index().rename(columns={"index": "date"})

        chart = (
            alt.Chart(df)
            .mark_circle(color="red", size=60)
            .encode(
                x=alt.X("date:T", title="Date", axis=alt.Axis(format="%Y-%m", labelAngle=270)),
                y=alt.Y("residual:Q", title = "Value")
            )
            .properties(
                width=self.width_px,
                height=self.height_px,
                title="Detected Anomalies"
            )
        )

        self._save(chart, filename)
        return chart

    def plot_continuity(self, diagnostics, filename="continuity.png"):

        """
        Plot continuity between last history point and first forecast.

        Parameters
        ----------
        **diagnostics**
        
        Object containing continuity report.
        
        **filename : str**
        
        Output filename.

        Returns
        -------
        **alt.Chart | None**
        
        The continuity chart, or None if unavailable.
        """

        report = diagnostics.continuity_report
        if not report:
            return None

        df = pd.DataFrame({
            "label": ["Last History", "First Forecast"],
            "value": [report["last_history"], report["first_forecast"]]
        })

        bars = (
            alt.Chart(df)
            .mark_bar()
            .encode(
                x="label:N",
                y="value:Q"
            )
        )

        labels = (
            alt.Chart(df)
            .mark_text(
                align="center",
                baseline="middle",
                dy=-10,          # move text upward inside the bar
                color="white",   # white text reads well inside bars
                fontSize=12
            )
            .encode(
                x="label:N",
                y="value:Q",
                text=alt.Text("value:Q", format=".2f")
            )
        )

        final = (bars + labels).properties(
            width=self.width_px,
            height=self.height_px,
            title="Continuity Check"
        )

        self._save(final, filename)
        
        return final

    def plot_error_metrics(self, diagnostics, filename="error_metrics.png"):

        """
        Plot error metrics as a bar chart.

        Parameters
        ----------
        **diagnostics**
        
        Object containing error metrics.

        **filename : str**
        
        Output filename.

        Returns
        -------
        **alt.Chart**
        
        The error metrics chart.
        """

        metrics = diagnostics.error_metrics

        df = pd.DataFrame({
            "metric": list(metrics.keys()),
            "value": list(metrics.values())
        })

        chart = (
            alt.Chart(df)
            .mark_bar()
            .encode(x="metric:N", y="value:Q")
            .properties(
                width=self.width_px,
                height=self.height_px,
                title="Error Metrics"
            )
        )

        self._save(chart, filename)
        return chart

    def plot_forecast_vs_actual(self, history, forecast, future_index, filename="forecast_vs_actual.png"):

        """
        Plot actual history and forecasted values together.

        Parameters
        ----------
        **history : pd.Series**
        
        Historical values.
        
        **forecast : array-like**
        
        Forecasted values.
        
        **future_index : pd.Index**
        
        Index for forecast horizon.
        
        **filename : str**
        
        Output filename.

        Returns
        -------
        **alt.Chart**
        
        The forecast vs actual chart.
        """

        hist_vals = np.asarray(history.values).ravel()
        fc_vals = np.asarray(forecast).ravel()

        df_hist = pd.DataFrame({"date": history.index, "value": hist_vals, "type": "Actual"})
        df_fc = pd.DataFrame({"date": future_index, "value": fc_vals, "type": "Forecast"})
        df = pd.concat([df_hist, df_fc])

        chart = (
            alt.Chart(df)
            .mark_line()
            .encode(
                x=alt.X("date:T", title="Date", axis=alt.Axis(format="%Y-%m", labelAngle=270)),
                y=alt.Y("value:Q", title = "Value"),
                color="type:N"
            )
            .properties(
                width=self.width_px,
                height=self.height_px,
                title="Forecast vs Actual"
            )
        )

        self._save(chart, filename)
        return chart

    def plot_strength_bars(self, diagnostics, filename="strength_bars.png"):

        """
        Plot trend and seasonal strength values.

        Parameters
        ----------
        **diagnostics**
        
        Object containing strength metrics.
        
        **filename : str**
        
        Output filename.

        Returns
        -------
        **alt.Chart | None**
        
        The strength bar chart, or None if diagnostics missing.
        """

        if diagnostics is None:
            return None

        df = pd.DataFrame({
            "component": ["Trend Strength", "Seasonal Strength"],
            "value": [diagnostics.trend_strength, diagnostics.seasonal_strength]
        })

        chart = (
            alt.Chart(df)
            .mark_bar()
            .encode(x="component:N", 
                    y=alt.Y("value:Q", title = "Value"))
            .properties(
                width=self.width_px,
                height=self.height_px,
                title="Trend vs Seasonal Strength"
            )
        )

        self._save(chart, filename)
        return chart

    def plot_variance_contributions(self, diagnostics, filename="variance_contributions.png"):

        """
        Plot variance contributions of trend, seasonality, and residuals.

        Parameters
        ----------
        **diagnostics**
        
        Object containing decomposition components.
        
        **filename : str**
        
        Output filename.

        Returns
        -------
        **alt.Chart | None**
        
        The variance contribution chart, or None if diagnostics missing.
        """

        if diagnostics is None:
            return None

        E_add = np.asarray(diagnostics.history.values).ravel() - np.asarray(diagnostics.fitted.values).ravel()
        S_add = np.asarray(diagnostics.trend.values).ravel() * (np.asarray(diagnostics.seasonal_full.values).ravel() - 1)
        T_vals = np.asarray(diagnostics.trend.values).ravel()
        T_add = T_vals - T_vals.mean()

        df = pd.DataFrame({
            "component": ["Trend", "Seasonality", "Residual"],
            "value": [
                np.var(T_add, ddof=1),
                np.var(S_add, ddof=1),
                np.var(E_add, ddof=1)
            ]
        })

        chart = (
            alt.Chart(df)
            .mark_bar()
            .encode(x="component:N",
                    y=alt.Y("value:Q", title = "Value"))
            .properties(
                width=self.width_px,
                height=self.height_px,
                title="Variance Contributions"
            )
        )

        self._save(chart, filename)
        return chart

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
        Generate all available plots for a model and its diagnostics.

        Parameters
        ----------
        **series : pd.Series**
        
        Original time series.

        **model**
        
        Fitted model object with trend_, fitted_, residual_, seasonal_factors, and seasonal_factors_ attributes.
        
        **forecast : array-like | None**
        
        Forecasted values.
        
        **future_index : pd.Index | None**
        
        Index for forecast horizon.
        **diagnostics : object | None**
        
        Diagnostics object containing residuals, anomalies, continuity report, and metrics.
        
        **prefix : str | None**
        
        Optional prefix for output filenames.

        Notes
        -----
        This method orchestrates the full suite of visualizations,
        saving each one with a numbered filename for easy browsing.
        """
    
        prefix = f"{prefix}_" if prefix else ""

        self.plot_decomposition(series, model.trend_, model.fitted_, f"{prefix}01_decomposition.png")
        self.plot_seasonal_cycle(model.seasonal_factors, f"{prefix}02_seasonal_cycle.png")
        self.plot_seasonal_factors_over_time(series, model.seasonal_factors_, f"{prefix}03_seasonal_factors_over_time.png")

        self.plot_residuals(model.residual_, f"{prefix}04_residuals.png")
        self.plot_residual_distribution(model.residual_, f"{prefix}05_residual_distribution.png")

        if diagnostics is not None:
            self.plot_residual_zscores(diagnostics, f"{prefix}06_residual_zscores.png")
            self.plot_anomalies(diagnostics, f"{prefix}07_anomalies.png")
            self.plot_continuity(diagnostics, f"{prefix}08_continuity.png")
            self.plot_error_metrics(diagnostics, f"{prefix}09_error_metrics.png")

        if forecast is not None and future_index is not None:
            self.plot_forecast_vs_actual(series, forecast, future_index, f"{prefix}10_forecast_vs_actual.png")

        self.plot_strength_bars(diagnostics, f"{prefix}11_strength_bars.png")
        self.plot_variance_contributions(diagnostics, f"{prefix}12_variance_contributions.png")
