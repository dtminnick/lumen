
"""
Diagnostics for Lumen decomposition and forecasting.

The class `DiagnosticsEngine` computes a comprehensive suite of diagnostic
statistics for a Lumen model, including:

* Residuals (multiplicative + percent residuals),
* Error metrics (MAE, RMSE, MAPE, SMAPE),
* Continuity between history and forecast,
* Anomaly detection using z-scores, and
* Trend and seasonal strength (Hyndman definition).

These diagnostics help evaluate model fit, detect structural issues, and
quantify the contribution of trend and seasonality.
"""

from dataclasses import dataclass
import numpy as np
import pandas as pd

@dataclass
class DiagnosticsConfig:

    """
    Configuration for diagnostics computation.

    Parameters
    ----------
    **continuity_threshold : float, default 0.10**

    Maximum allowed relative jump between the last historical value and
    the first forecast value before continuity is considered broken.

    **residual_zscore_threshold : float, default 3.0**

    Z-score threshold for anomaly detection.

    **eps : float, default 1e-8**
    
    Small constant added to denominators to avoid division by zero.
    
    Notes
    -----
    This configuration object is lightweight and does not validate values.
    Validation occurs inside class `DiagnosticsEngine`.
    
    """

    continuity_threshold: float = 0.10

    residual_zscore_threshold: float = 3.0

    eps: float = 1e-8

class DiagnosticsEngine:

    """
    Compute diagnostics for a Lumen decomposition and forecast.

    This engine evaluates model fit, continuity, anomalies, and component
    strengths.  It supports multiplicative decomposition by converting
    components to additive form where required.

    Parameters
    ----------
    **history : pd.Series**
    
    Original observed time series.

    **fitted : pd.Series**

    Fitted values from STL decomposition.

    **forecast : pd.Series or None**
    
    Forecasted values.  May be `None` for decomposition-only workflows.

    **trend : pd.Series**
    
    Trend component from STL.

    **seasonal_full : pd.Series**

    Seasonal component expanded across the full timeline.

    **config : DiagnosticsConfig, optional**
    
    Configuration for thresholds and numerical stability.

    Attributes
    ----------
    **residuals : pd.Series or None**
    
    Multiplicative residuals `y / y_hat`.

    **percent_residuals : pd.Series or None**

    Percent residuals.

    **error_metrics : dict**
        
    Dictionary containing MAE, RMSE, MAPE, SMAPE.

    **continuity_report : dict**

    Summary of continuity between history and forecast.

    **anomalies : pd.DataFrame or None**

    Rows flagged as anomalies based on z-score threshold.

    **trend_strength : float or None**

    Hyndman trend strength metric.

    **seasonal_strength : float or None**

    Hyndman seasonal strength metric.
    """

    def __init__(
        self,
        history: pd.Series,
        fitted: pd.Series,
        forecast: pd.Series | None,
        trend: pd.Series,
        seasonal_full: pd.Series,
        config: DiagnosticsConfig = DiagnosticsConfig()
    ):
        
        """
        Initialize the diagnostics engine for a Lumen decomposition + forecast.

        This constructor defines the full diagnostic context: the observed series,
        fitted values, optional forecast, and the STL components required to compute
        residuals, continuity, anomaly detection, and component strengths.

        Parameters
        ----------
        **history : pd.Series**

        Original observed time series. Must be indexed by datetime and aligned
        with the fitted values. Values are coerced to float.

        **fitted : pd.Series**

        Fitted values from the STL decomposition. Must share the same index as
        `history`. Values are coerced to float.

        **forecast : pd.Series or None**
        
        Forecasted values extending beyond the historical index. May be `None`
        for decomposition-only workflows. If provided, values are coerced to float.

        **trend : pd.Series**
        
        Trend component from STL decomposition. Must be aligned with `history`.
        Values are coerced to float.

        **seasonal_full : pd.Series**

        Seasonal component expanded across the full timeline (history + forecast).
        Must be multiplicative seasonal factors (e.g., 1.12, 0.94). Values are
        coerced to float.

        **config : DiagnosticsConfig, optional**

        Configuration controlling continuity thresholds, anomaly z-score
        thresholds, and numerical stability constants.

        Notes
        -----
        All inputs are converted to float to ensure numerical consistency.
        
        Residuals are computed multiplicatively (`y / y_hat`), but strength
        metrics convert components to additive form following Hyndman's definitions.
        
        No diagnostics are computed during initialization; call `compute_all` to 
        populate residuals, metrics, anomalies, and strengths.
        """

        self.history = history.astype(float)

        self.fitted = fitted.astype(float)

        self.forecast = None if forecast is None else forecast.astype(float)

        self.trend = trend.astype(float)

        self.seasonal_full = seasonal_full.astype(float)

        self.config = config

        # Outputs.

        self.residuals = None

        self.percent_residuals = None

        self.error_metrics = {}

        self.continuity_report = {}

        self.anomalies = None

        self.trend_strength = None

        self.seasonal_strength = None

    # Public API.

    def compute_all(self):

        """
        Compute all diagnostics in the correct order.

        This method runs:

        * Residuals,
        * Error metrics,
        * Continuity check,
        * Anomaly detection, and
        * Trend and seasonal strength.

        Notes
        -----
        This is the primary entry point for diagnostic computation.
        """

        self._compute_residuals()
        self._compute_error_metrics()
        self._compute_continuity()
        self._detect_anomalies()
        self._compute_strengths()

    # Residuals.

    def _compute_residuals(self):

        """
        Compute multiplicative residuals and percent residuals.

        Residual definition:

        residual = y / (y_hat * eps)

        Percent residual:

        percent_residual = residual - 1

        Notes
        -----
        Multiplicative residuals are used because Lumen uses a multiplicative
        STL decomposition.
        """

        aligned = self.history.align(self.fitted, join="inner")
        
        y = aligned[0]
        
        y_hat = aligned[1]

        # Multiplicative residuals.

        residuals = y / (y_hat + self.config.eps)

        self.residuals = residuals

        self.percent_residuals = residuals - 1.0

    # Error metrics.
    
    def _compute_error_metrics(self):

        """
        Compute MAE, RMSE, MAPE, and SMAPE

        Notes
        -----
        Although the residuals are multiplicative, error metrics are computed
        using additive residuals `y - y_hat` for interpretability.
        """

        if self.residuals is None:

            self._compute_residuals()

        y = self.history.loc[self.residuals.index]

        y_hat = self.fitted.loc[self.residuals.index]

        # Convert multiplicative residuals to additive for metrics
        
        additive_r = y - y_hat

        abs_r = additive_r.abs()

        sq_r = additive_r ** 2

        mae = abs_r.mean()

        rmse = np.sqrt(sq_r.mean())

        denom_mape = (y.abs() + self.config.eps)

        mape = (abs_r / denom_mape).mean() * 100.0

        denom_smape = (y.abs() + y_hat.abs() + self.config.eps)
        
        smape = (abs_r / denom_smape).mean() * 200.0

        self.error_metrics = {
            "MAE": float(mae),
            "RMSE": float(rmse),
            "MAPE": float(mape),
            "SMAPE": float(smape),
        }

    # Continuity.
    
    def _compute_continuity(self):

        """
        Evaluate continuity between the last historical point and the first forecast.
        
        A relative jump is computed as:

        rel_jump = (forecast[0] - history[-1]) / abs(history[-1])

        If the jump exceeds `continuity_threshold`, continuity is considered
        broken.

        Notes
        -----
        If no forecast is provided, continuity is marked as unavailable.
        """

        if self.forecast is None or self.forecast.empty:
            
            self.continuity_report = {

                "has_continuity": False,

                "reason": "No forecast provided",

            }

            return

        last_hist = float(self.history.iloc[-1])

        first_fc = float(self.forecast.iloc[0])

        if abs(last_hist) < self.config.eps:

            rel_jump = np.nan

        else:

            rel_jump = (first_fc - last_hist) / abs(last_hist)

        self.continuity_report = {
            "last_history": last_hist,
            "first_forecast": first_fc,
            "relative_jump": rel_jump,
            "threshold": self.config.continuity_threshold,
            "has_continuity": (
                np.isnan(rel_jump)
                or abs(rel_jump) <= self.config.continuity_threshold
            ),
        }

    # Anomaly detection.
    
    def _detect_anomalies(self):

        """
        Detect anomalies using z-scores of multiplicative residuals.

        A point is considered anomalous if:

        |z| >= residual_zscore_threshold

        where z = (residual - mean) / std.

        Returns
        -------
        None
            Results stored in attribute `anomalies` as a DataFrame.
        """

        if self.residuals is None:

            self._compute_residuals()

        r = self.residuals

        mu = r.mean()

        sigma = r.std(ddof=0) + self.config.eps

        z = (r - mu) / sigma

        is_anomaly = z.abs() >= self.config.residual_zscore_threshold

        df = pd.DataFrame({
            "actual": self.history.loc[r.index],
            "fitted": self.fitted.loc[r.index],
            "residual": r,
            "z_score": z,
            "is_anomaly": is_anomaly,
        })

        self.anomalies = df[df["is_anomaly"]]

    # Strength metrics.
    
    def _compute_strengths(self):

        """
        Compute trend and seasonal strength using Hyndman's definitions.

        Strength definitions (additive form):

        seasonal_strength = 1 - Var(E) / Var(E + S)

        trend_strength = 1 - Var(E) / Var(E + T)

        where:

        * E = additive residuals
        * S = additive seasonal component
        * T = additive trend component

        Notes
        -----
        Lumen uses multiplicative decomposition, so components are converted
        to additive form before computing strengths.
        """

        # Need residuals, trend, and seasonal

        if self.residuals is None:

            self._compute_residuals()

        if self.trend is None or self.seasonal_full is None:

            return

        # Convert multiplicative residuals to additive residuals
        # e_add = y - y_hat

        E_add = (self.history.values - self.fitted.values)

        # Convert multiplicative seasonal factors to additive seasonal effect:
        # S_add = T * (S_mult - 1)

        S_add = self.trend.values * (self.seasonal_full.values - 1)

        # Convert trend to additive deviation from mean
        # T_add = T - mean(T)

        T_add = self.trend.values - self.trend.values.mean()

        var_e = np.var(E_add, ddof=1)

        # Seasonal strength

        var_e_plus_s = np.var(E_add + S_add, ddof=1)

        if var_e_plus_s > 0:

            self.seasonal_strength = max(0.0, 1.0 - var_e / var_e_plus_s)

        else:

            self.seasonal_strength = 0.0

        # Trend strength
        var_e_plus_t = np.var(E_add + T_add, ddof=1)

        if var_e_plus_t > 0:

            self.trend_strength = max(0.0, 1.0 - var_e / var_e_plus_t)

        else:

            self.trend_strength = 0.0

    # Output helpers.
    
    def residuals_frame(self):

        """
        Return a DataFrame containing actual, fitted, residual, and percent residual.

        Returns
        -------
        **pd.DataFrame**

        Residual diagnostics aligned on the residual index.
        """

        return pd.DataFrame({
            "actual": self.history.loc[self.residuals.index],
            "fitted": self.fitted.loc[self.residuals.index],
            "residual": self.residuals,
            "percent_residual": self.percent_residuals,
        })

    def summary(self):

        """
        Return a compact summary of all diagnostics.

        Returns
        -------
        **pd.DataFrame**

        Table containing:

        * Error metrics,
        * Continuity report,
        * Anomaly count,
        * Trend strength, and
        * Seasonal strength.
        """
        
        rows = []

        for k, v in self.error_metrics.items():

            rows.append({"Metric": k, "Value": v})

        for k, v in self.continuity_report.items():

            rows.append({"Metric": f"continuity_{k}", "Value": v})

        anomaly_count = 0 if self.anomalies is None else len(self.anomalies)

        rows.append({"Metric": "anomaly_count", "Value": anomaly_count})

        rows.append({"Metric": "trend_strength", "Value": self.trend_strength})

        rows.append({"Metric": "seasonal_strength", "Value": self.seasonal_strength})

        return pd.DataFrame(rows)
