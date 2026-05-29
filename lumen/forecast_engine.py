
# lumen/forecast_engine.py

"""
Minimal forecasting wrapper for Lumen.

The :class:`ForecastEngine` provides a thin orchestration layer around
:class:`SeriesDecomposition`, handling:

    * Fitting the decomposition model
    * Constructing the future index
    * Generating forecasts
    * Exposing fitted values, trend, seasonal factors, and residuals

It relies on :class:`DataLoader` for:
    * Frequency inference
    * Seasonal period
    * LOESS span
    * Cleaned, validated time series
"""

import pandas as pd
from lumen.series_decomposition import SeriesDecomposition

class ForecastEngine:

    """
    High-level forecasting wrapper around :class:`SeriesDecomposition`.

    This class coordinates the decomposition and forecasting workflow using
    the cleaned, regularized series provided by :class:`DataLoader`. It exposes
    fitted values, trend, seasonal factors, and residuals through convenience
    properties.

    Parameters
    ----------
    loader : DataLoader
        Provides the validated time series, canonical frequency, seasonal
        period, and LOESS span. The loader determines all decomposition
        hyperparameters.
    """

    def __init__(self, loader):

        """
        Initialize the forecasting engine.

        The constructor creates a :class:`SeriesDecomposition` instance using
        the loader's frequency, seasonal period, and LOESS span. No fitting is
        performed until :meth:`fit` is called.

        Parameters
        ----------
        loader : DataLoader
            Provides frequency, seasonal period, LOESS span, and the cleaned
            value series.
        """
        self.loader = loader

        self.model = SeriesDecomposition.from_loader(loader)

        self.fitted_ = None

        self.forecast_ = None

        self.future_index_ = None

    def fit(self):

        """
        Fit the STL decomposition model on the loader's series.

        This method:
            * Extracts the primary value series from the loader
            * Fits the multiplicative STL decomposition
            * Stores the fitted values for convenience

        Notes
        -----
        After calling :meth:`fit`, the following attributes become available:

            * ``fitted_`` — fitted values
            * ``trend`` — trend component
            * ``seasonal_factors`` — seasonal cycle
            * ``seasonal_factors_`` — seasonal factors over time
            * ``residuals`` — model residuals
        """

        series = self.loader.get_series()

        self.model.fit(series)

        self.fitted_ = self.model.fitted_

    def forecast(self, steps: int):

        """
        Forecast future values using the fitted decomposition model.

        This method:
            1. Builds a future datetime index using the loader's canonical frequency.
            2. Calls :meth:`SeriesDecomposition.predict` to generate forecast values.
            3. Stores the forecast and future index for downstream use.

        Parameters
        ----------
        steps : int
            Number of periods to forecast.

        Returns
        -------
        pd.Series
            Forecasted values indexed by future timestamps.

        Notes
        -----
        The forecast is multiplicative, consistent with the decomposition model.
        """

        series = self.loader.get_series()

        last_date = series.index[-1]

        # Build future index

        freq = self.loader.freq

        future_index = pd.date_range(

            start=last_date + pd.tseries.frequencies.to_offset(freq),

            periods=steps,

            freq=freq

        )

        # Predict using decomposition model

        forecast_vals = self.model.predict(steps, future_index)

        # Store results

        self.future_index_ = future_index

        self.forecast_ = pd.Series(forecast_vals, index=future_index, name="forecast")

        return self.forecast_

    @property
    def trend(self):

        """
        Return the trend component from the decomposition.
        """

        return self.model.trend_

    @property
    def seasonal_factors(self):

        """
        Return the seasonal cycle (one full seasonal period).
        """

        return self.model.seasonal_factors

    @property
    def seasonal_factors_(self):

        """
        Return seasonal factors expanded across the full timeline.
        """

        return self.model.seasonal_factors_

    @property
    def fitted(self):

        """
        Return fitted values from the decomposition.
        """

        return self.model.fitted_

    @property
    def residuals(self):

        """
        Return residuals from the decomposition.
        """

        return self.model.residual_
