
# lumen/series_decomposition.py

"""
Frequency-aware multiplicative STL-style decomposition for Lumen.

This module implements a lightweight, dependency-minimal decomposition engine
designed specifically for Lumen's forecasting workflow. It performs a
multiplicative decomposition of the form:

    series = trend * seasonal * residual

Key features
------------
* Frequency-aware seasonal indexing (hourly, daily, weekly, monthly)
* LOESS-based trend extraction
* Iterative seasonal refinement
* Strictly multiplicative structure for stability and interpretability
* Forecasting via linear trend extrapolation + seasonal cycle

Outputs
-------
After fitting, the model provides:

* ``trend_`` — LOESS-smoothed trend component
* ``seasonal_factors`` — seasonal cycle of length ``period``
* ``seasonal_factors_`` — seasonal factors expanded across the full timeline
* ``fitted_`` — reconstructed fitted values
* ``residual_`` — multiplicative residuals (y / fitted)

This class is intentionally minimal and does not depend on statsmodels’ STL
implementation. It is optimized for clarity, reproducibility, and integration
with Lumen's diagnostics and forecasting layers.
"""

from statsmodels.nonparametric.smoothers_lowess import lowess
import numpy as np
import pandas as pd

class SeriesDecomposition:

    """
    Frequency-aware multiplicative STL-style decomposition engine.

    This class performs a custom implementation of STL-like decomposition using:

        * LOESS smoothing for trend extraction
        * Frequency-aware seasonal indexing
        * Iterative seasonal refinement
        * Multiplicative reconstruction

    It is designed to work seamlessly with :class:`DataLoader` and
    :class:`ForecastEngine`, using the loader's inferred frequency, seasonal
    period, and LOESS span.

    Notes
    -----
    * Input series must be strictly positive due to multiplicative structure.
    * Seasonal indexing is derived from the canonical frequency (hour, weekday,
      week-of-year, month).
    * The algorithm is intentionally simple and transparent, suitable for
      diagnostics and educational use.
    """

    def __init__(self, freq: str, period: int, loess_frac: float, n_iter: int = 5):

        """
        Initialize the multiplicative decomposition engine.

        Parameters
        ----------
        freq : str
            Canonical frequency string (e.g., ``"H"``, ``"D"``, ``"W"``, ``"MS"``).
            Determines how timestamps map to seasonal indices.

        period : int
            Number of observations in one seasonal cycle. Examples:
                * 24 → hourly
                * 7  → daily
                * 52 → weekly
                * 12 → monthly

        loess_frac : float
            Fraction of data used for LOESS smoothing (0-1). Controls trend
            smoothness. Larger values → smoother trend.

        n_iter : int, default 5
            Number of seasonal-trend refinement iterations. Each iteration:
                1. Remove seasonality
                2. Fit LOESS trend
                3. Remove trend
                4. Recompute seasonal factors

        Attributes
        ----------
        seasonal_factors : np.ndarray or None
            Seasonal cycle of length ``period`` after fitting.

        seasonal_factors_ : pd.Series or None
            Seasonal factors expanded across the full timeline.

        trend_ : pd.Series or None
            LOESS-smoothed trend component.

        fitted_ : pd.Series or None
            Reconstructed fitted values: ``trend_ * seasonal_factors_``.

        residual_ : pd.Series or None
            Multiplicative residuals: ``series / fitted_``.
        """

        self.freq = freq

        self.period = period

        self.loess_frac = loess_frac

        self.n_iter = n_iter

        self.seasonal_factors = None

        self.seasonal_factors_ = None

        self.trend_ = None

        self.fitted_ = None

        self.residual_ = None

    @classmethod
    def from_loader(cls, loader):

        """
        Create a decomposition model using parameters from a :class:`DataLoader`.

        Parameters
        ----------
        loader : DataLoader
            Provides canonical frequency, seasonal period, and LOESS span.

        Returns
        -------
        SeriesDecomposition
            A decomposition engine configured with loader-derived parameters.

        Notes
        -----
        This is the recommended way to construct a decomposition model inside
        Lumen's forecasting pipeline.
        """

        return cls(
            freq=loader.freq,
            period=loader.seasonal_period,
            loess_frac=loader.loess_frac
        )

    def fit(self, series: pd.Series) -> None:

        """
        Fit multiplicative decomposition to a strictly positive time series.

        The algorithm performs iterative STL-style refinement:

            1. Initialize seasonal cycle to ones
            2. Repeat for ``n_iter`` iterations:
                a. Remove seasonality
                b. Fit LOESS trend
                c. Remove trend
                d. Recompute seasonal factors
            3. Construct final components and residuals

        Parameters
        ----------
        series : pd.Series
            Time series indexed by ``DatetimeIndex``. All values must be
            strictly positive.

        Raises
        ------
        ValueError
            If any values are non-positive.

        Notes
        -----
        * Seasonal indexing is derived from the timestamp (hour, weekday,
          week-of-year, or month).
        * LOESS smoothing is performed using ``statsmodels.lowess``.
        """

        if (series <= 0).any():

            raise ValueError("Multiplicative decomposition requires strictly positive values.")

        seasonal_index = self._seasonal_index(series.index)

        values = series.values.astype(float)

        # Initialize seasonal cycle

        seasonal = np.ones(self.period, dtype=float)

        # Iterative refinement loop

        for _ in range(self.n_iter):

            seasonal_full = seasonal[seasonal_index]

            deseasonalized = values / seasonal_full

            trend_vals = self._loess_trend(deseasonalized)

            trend_vals = np.where(trend_vals <= 0, np.finfo(float).eps, trend_vals)

            detrended = values / trend_vals

            seasonal = self._recompute_seasonal(detrended, seasonal_index)

        # Final components

        seasonal_full = seasonal[seasonal_index]

        self.seasonal_factors = seasonal

        self.seasonal_factors_ = pd.Series(seasonal_full, index=series.index)

        self.trend_ = pd.Series(trend_vals, index=series.index)

        self.fitted_ = pd.Series(trend_vals * seasonal_full, index=series.index)

        # Multiplicative residuals

        self.residual_ = series / self.fitted_

    def predict(self, steps: int, future_index: pd.DatetimeIndex) -> np.ndarray:

        """
        Forecast using linear trend extrapolation + seasonal cycle.

        Forecasting procedure:
            1. Fit a linear model to the historical trend component
            2. Extrapolate trend forward ``steps`` periods
            3. Apply seasonal cycle using frequency-aware seasonal indexing
            4. Multiply trend and seasonal components

        Parameters
        ----------
        steps : int
            Number of forecast periods.

        future_index : pd.DatetimeIndex
            Index corresponding to the forecast horizon.

        Returns
        -------
        np.ndarray
            Forecasted values.

        Raises
        ------
        ValueError
            If the model has not been fitted.

        Notes
        -----
        * Trend extrapolation uses simple linear regression (polyfit).
        * Seasonal factors are repeated according to the seasonal period.
        """

        if self.trend_ is None or self.seasonal_factors is None:

            raise ValueError("Model must be fitted before calling predict().")

        # Linear trend extrapolation

        t_hist = np.arange(len(self.trend_))

        t_future = np.arange(len(self.trend_), len(self.trend_) + steps)

        slope, intercept = np.polyfit(t_hist, self.trend_.values, 1)

        trend_vals = slope * t_future + intercept

        # Seasonal component

        seasonal_index = self._seasonal_index(future_index)

        seasonal_vals = self.seasonal_factors[seasonal_index]

        return (trend_vals * seasonal_vals).astype(float)

    def _loess_trend(self, values: np.ndarray) -> np.ndarray:

        """
        Compute LOESS-smoothed trend component.

        Parameters
        ----------
        values : np.ndarray
            Deseasonalized values.

        Returns
        -------
        np.ndarray
            LOESS-smoothed trend.

        Notes
        -----
        Uses ``statsmodels.nonparametric.lowess`` with ``return_sorted=False``.
        """

        t = np.arange(len(values))

        return lowess(
            endog=values,
            exog=t,
            frac=self.loess_frac,
            return_sorted=False
        )

    def _recompute_seasonal(self, detrended: np.ndarray, seasonal_index: np.ndarray) -> np.ndarray:

        """
        Recompute normalized seasonal factors from detrended values.

        Parameters
        ----------
        detrended : np.ndarray
            Values with trend removed.

        seasonal_index : np.ndarray
            Integer seasonal index for each timestamp.

        Returns
        -------
        np.ndarray
            Normalized seasonal cycle of length ``period``.

        Notes
        -----
        Seasonal factors are normalized to have mean 1.0 to preserve
        multiplicative structure.
        """

        df = pd.DataFrame({"value": detrended, "season": seasonal_index})

        seasonal = df.groupby("season")["value"].mean().values

        return seasonal / seasonal.mean()

    def _seasonal_index(self, index: pd.DatetimeIndex) -> np.ndarray:

        """
        Map timestamps to integer seasonal indices based on frequency.

        Parameters
        ----------
        index : pd.DatetimeIndex
            Timestamp index.

        Returns
        -------
        np.ndarray
            Integer seasonal index for each timestamp.

        Raises
        ------
        ValueError
            If the seasonal period is unsupported.

        Notes
        -----
        Supported mappings:
            * 24 → hour of day
            * 7  → day of week
            * 52 → ISO week of year (0-51)
            * 12 → month of year (0-11)
        """

        if self.period == 24:

            return index.hour
        
        if self.period == 7:

            return index.dayofweek
        
        if self.period == 52:

            return index.isocalendar().week.astype(int) - 1
        
        if self.period == 12:

            return index.month - 1

        raise ValueError(f"Unsupported seasonal period '{self.period}'")
