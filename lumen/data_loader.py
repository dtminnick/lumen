
"""
Data loading, validation, and frequency inference for Lumen time series modeling.

This module defines the `DataLoader` and `DataConfig` classes,
which together form the foundation of the Lumen forecasting pipeline.

Responsibilities
---------------
The loader performs all preprocessing required before modeling:

* Load raw time series from CSV or XLSX.
* Validate schema (date column, numeric values, duplicates, emptiness).
* Parse and index by datetime.
* Infer or normalize frequency (e.g., "MS", "W", "D").
* Map frequency to seasonal period and LOESS span.
* Detect missing timestamps (gaps).
* Provide a clean, regularized DataFrame for modeling.

The loader is intentionally strict — it enforces clean, well-formed time
series so that downstream STL decomposition and forecasting behave reliably.
"""

from __future__ import annotations
from dataclasses import dataclass
from typing import Optional

import numpy as np
import pandas as pd

# Frequency normalization map
# Collapses Pandas' many frequency variants into a canonical set.

FREQ_MAP = {
    "H": "H", "h": "H",
    "D": "D", "d": "D",
    "W": "W", "W-SUN": "W",
    "M": "ME", "MS": "MS", "ME": "ME",
    "Q": "QE", "QS": "QS", "QE": "QE",
    "A": "YE", "AS": "YS", "YE": "YE",
}

# Frequency to seasonal period
# Defines how many observations make up one seasonal cycle.

FREQ_TO_PERIOD = {
    "H": 24,     # hourly → 24 hours
    "D": 7,      # daily → 7 days
    "W": 52,     # weekly → 52 weeks
    "MS": 12,    # month-start → 12 months
    "ME": 12,    # month-end → 12 months
    "QS": 4,     # quarter-start → 4 quarters
    "QE": 4,     # quarter-end → 4 quarters
    "YS": 1,     # year-start → 1 cycle
    "YE": 1,     # year-end → 1 cycle
}

# Frequency to recommended LOESS span
# Based on STL literature: trend smoother must span > 1 seasonal cycle.

FREQ_TO_LOESS_FRAC = {
    "H": 0.02,
    "D": 0.05,
    "W": 0.10,
    "MS": 0.35,
    "ME": 0.35,
    "QS": 0.5,
    "QE": 0.5,
    "YS": 0.8,
    "YE": 0.8,
}

@dataclass
class DataConfig:

    """
    Configuration for loading and preparing time series data.

    This dataclass defines how the class `DataLoader` interprets input files.
    It allows users to override frequency, file type, seasonal period, LOESS
    span, and output rounding.

    Parameters
    ----------
    **date_col : str, default "date"**

    Name of the date column in the input file.

    **value_col : str, default "value"**
    
    Name of the numeric value column.

    **freq : str, optional**
        
    Explicit frequency override (e.g., "MS", "D", "W"). If provided,
    frequency inference is skipped.

    **file_type : str, optional**

    Explicit file type ("csv" or "xlsx"). If omitted, the loader infers
    file type from the file extension.

    **period : int, optional**

    Explicit seasonal period override. If omitted, the loader uses data
    `FREQ_TO_PERIOD`.

    **loess_frac : float, optional**
        
    Explicit LOESS span override. If omitted, the loader uses
    data `FREQ_TO_LOESS_FRAC`.

    **rounding : int, optional**
    
    Optional rounding applied during export formatting.

    **continuity_method : str**

    How to handle continuity at the history / forecast boundary.
    Options none, hard, blend, both, default none.

    **continuity_blend_points : int**
        
    How many points blend for blend, both options,
    default 5.

    Notes
    -----
    This configuration object is lightweight and does not validate values.
    Validation occurs inside class `DataLoader`.
    """

    date_col: str = "date"

    value_col: str = "value"

    freq: Optional[str] = None

    file_type: Optional[str] = None

    period: Optional[int] = None

    loess_frac: Optional[float] = None

    rounding: Optional[int] = None

    continuity_method: str = "none"

    continuity_blend_points: int = 5

class DataLoader:

    """
    Load, validate, regularize, and summarize time series data.

    The class `DataLoader` is responsible for preparing raw input files for
    modeling. It ensures that the dataset is:

        * Chronologically sorted
        * Indexed by datetime
        * Free of duplicates
        * Free of missing values
        * Numeric
        * Regularly spaced with a known frequency

    After loading, the cleaned DataFrame is accessible via attribute `data`.
    """

    def __init__(self, config: DataConfig):

        """
        Initialize the loader.

        Parameters
        ----------
        **config : DataConfig**
        
        Configuration defining how the loader interprets input files.

        Notes
        -----
        The loader does not immediately load data. Call method `load_file`
        to populate attribute `data`.
        """
        
        self.config = config

        self._data: Optional[pd.DataFrame] = None

        self._freq: Optional[str] = None

    # Public API.

    def load_file(self, path: str) -> None:

        """
        Load a CSV or XLSX file and prepare it for modeling.

        Workflow
        --------
        1. Determine file type (CSV/XLSX).
        2. Load raw file into a DataFrame.
        3. Validate required columns.
        4. Parse date column and set as index.
        5. Validate schema (duplicates, missing values, numeric types).
        6. Infer or normalize frequency.

        Parameters
        ----------
        **path : str**
        
        Path to the input file.

        Raises
        ------
        **ValueError**

        If required columns are missing, file type is unsupported,
        or frequency cannot be inferred.

        Notes
        -----
        After calling this method, the cleaned DataFrame is available via
        attribute `data`, and the canonical frequency via attribute `freq`.
        """

        file_type = self._resolve_file_type(path)

        if file_type == "csv":

            df = pd.read_csv(path)

        elif file_type == "xlsx":

            df = pd.read_excel(path)

        else:

            raise ValueError(f"Unsupported file type '{file_type}'")

        if self.config.date_col not in df.columns:

            raise ValueError(f"Missing date column '{self.config.date_col}'")

        if self.config.value_col not in df.columns:

            raise ValueError(f"Missing value column '{self.config.value_col}'")

        df[self.config.date_col] = pd.to_datetime(df[self.config.date_col])

        df = df.sort_values(self.config.date_col).set_index(self.config.date_col)

        df = df[[self.config.value_col]].astype(float)

        self._validate_dataframe(df)

        self._data = df

        self._infer_or_set_frequency()

    def summary(self) -> None:

        """
        Print a human-readable summary of the dataset.

        Displays:
            * Frequency
            * Seasonal period
            * LOESS span
            * Start/end dates
            * Observation count
            * Missing timestamps
            * Value statistics

        Notes
        -----
        This method prints directly to stdout and is intended for interactive
        exploration.
        """

        df = self.data

        print("\nModel Data Summary\n")
        print(f"Frequency:          {self.freq}")
        print(f"Seasonal Period:    {self.seasonal_period}")
        print(f"LOESS Span (frac):  {self.loess_frac}")
        print(f"Start Date:         {df.index.min()}")
        print(f"End Date:           {df.index.max()}")
        print(f"Observation Count:  {len(df)}")

        missing = self._detect_gaps()

        print(f"Missing Periods:    {len(missing)}")

        print("\nValue Statistics:")
        print(df.describe())
        print("\n")

    def gap_summary(self) -> None:

        """
        Print a summary of missing timestamps.

        Displays frequency, number of missing periods, first 10 missing timestamps, if any.

        Notes
        -----
        Useful for diagnosing irregular or incomplete datasets.
        """

        missing = self._detect_gaps()

        print("\nGap Summary\n")
        print(f"Frequency:       {self.freq}")
        print(f"Missing periods: {len(missing)}")

        if len(missing) > 0:
            print("\nFirst 10 missing timestamps:")
            print(missing[:10])

        print("\n")

    def get_series(self) -> pd.Series:

        """
        Return the primary value series.

        Returns
        -------
        **pd.Series**

        The value column extracted from :attr:`data`.
        """

        return self.data[self.config.value_col]

    # Properties.

    @property
    def data(self) -> pd.DataFrame:

        """
        Return the validated, regularized DataFrame.

        Returns
        -------
        **pd.DataFrame**

        Cleaned time series data.

        Raises
        ------
        **ValueError**

        If data has not been loaded yet.
        """

        if self._data is None:

            raise ValueError("Data has not been loaded yet.")
        
        return self._data

    @property
    def freq(self) -> str:

        """
        Return the canonical frequency string.

        Returns
        -------
        **str**
            
        Canonical frequency (e.g., "MS", "D", "W").

        Raises
        ------
        **ValueError**

        If frequency has not been determined.
        """

        if self._freq is None:

            raise ValueError("Frequency has not been determined.")
        
        return self._freq

    @property
    def loess_frac(self) -> float:

        """
        Return the recommended LOESS span for this frequency.

        Returns
        -------
        **float**
            
        LOESS span fraction.

        Raises
        ------
        **ValueError**
        
        If no LOESS span is defined for this frequency.
        """

        freq = self.freq

        if freq not in FREQ_TO_LOESS_FRAC:

            raise ValueError(f"No LOESS frac defined for frequency '{freq}'")
        
        return FREQ_TO_LOESS_FRAC[freq]

    @property
    def seasonal_period(self) -> int:

        """
        Return the seasonal period for this frequency.

        Returns
        -------
        **int**
        
        Number of observations per seasonal cycle.

        Raises
        ------
        **ValueError**

        If no seasonal period is defined for this frequency.
        """

        freq = self.freq

        if freq not in FREQ_TO_PERIOD:

            raise ValueError(f"No seasonal period defined for frequency '{freq}'")
        
        return FREQ_TO_PERIOD[freq]

    # Internl helpers.

    def _detect_gaps(self) -> pd.DatetimeIndex:

        """
        Return missing timestamps based on inferred frequency.

        Returns
        -------
        **pd.DatetimeIndex**
            
        All timestamps missing from the expected date range.

        Notes
        -----
        This method does not modify the dataset. It is used for diagnostics
        and summary reporting.
        """

        df = self._data

        full_range = pd.date_range(df.index.min(), df.index.max(), freq=self.freq)
        
        return full_range.difference(df.index)

    def _infer_or_set_frequency(self) -> None:

        """
        Infer frequency from index or use explicit override.

        Order of precedence:

            1. Explicit `config.freq`.
            2. `pandas.infer_freq` applied to the index.

        Raises
        ------
        **ValueError**

        If no frequency can be inferred.
        """

        if self.config.freq:

            self._freq = self._normalize_freq(self.config.freq)
            
            return

        inferred = pd.infer_freq(self._data.index)

        if inferred is None:

            raise ValueError(
                "Could not infer frequency. "
                "Specify freq explicitly in DataConfig."
            )

        self._freq = self._normalize_freq(inferred)

    def _normalize_freq(self, freq: str) -> str:

        """
        Normalize a raw frequency string to canonical form.

        Parameters
        ----------
        **freq : str**

        Raw frequency string (e.g., "M", "MS", "W-SUN").

        Returns
        -------
        **str**
            
    Canonical frequency.

        Raises
        ------
        **ValueError**

        If frequency is unrecognized.
        """

        freq = freq.upper()

        if freq in FREQ_MAP:

            return FREQ_MAP[freq]

        if freq.startswith("W-"):

            return "W"

        raise ValueError(f"Unsupported or unrecognized frequency '{freq}'")

    def _resolve_file_type(self, path: str) -> str:

        """
        Determine file type from extension or config override.

        Parameters
        ----------
        **path : str**

        Path to the input file.

        Returns
        -------
        **str**
            
        Either ``"csv"`` or ``"xlsx"``.

        Raises
        ------
        **ValueError**
            If file type cannot be determined.
        """

        if self.config.file_type:

            return self.config.file_type.lower()

        ext = path.split(".")[-1].lower()

        if ext == "csv":

            return "csv"
        
        if ext in ("xlsx", "xls"):

            return "xlsx"

        raise ValueError(
            f"Could not determine file type from extension [.{ext}]. "
            "Specify file_type explicitly in DataConfig."
        )

    def _validate_dataframe(self, df: pd.DataFrame) -> None:
        
        """
        Validate the loaded DataFrame before modeling.

        Ensures:

            * No missing dates.
            * No duplicate timestamps.
            * Numeric value column.
            * No missing values.
            * Non‑empty dataset.

        Parameters
        ----------
        **df : pd.DataFrame**
            
        DataFrame to validate.

        Raises
        ------
        **ValueError**
        
        If any validation rule fails.
        """

        if df.index.isna().any():

            raise ValueError("Date column contains missing values after parsing.")

        if df.index.duplicated().any():

            raise ValueError("Duplicate timestamps found. Ensure unique dates.")

        value_col = self.config.value_col

        if not np.issubdtype(df[value_col].dtype, np.number):

            raise ValueError(f"Value column '{value_col}' must be numeric.")

        if df[value_col].isna().any():

            raise ValueError(f"Value column '{value_col}' contains missing values.")

        if len(df) == 0:

            raise ValueError("Loaded dataset is empty.")
