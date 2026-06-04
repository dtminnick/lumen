
# Data Loader

The `DataLoader` is responsible for ingesting, validating, and preparing the input time series for decomposition and forecasting. It ensures that the data is clean, well‑structured, and ready for downstream components such as the Decomposition Engine and Forecast Engine.

The loader is intentionally simple and predictable: it performs only the operations required to guarantee a stable, monotonic, frequency‑aware time series.

## Responsibilities

The `DataLoader` performs five core tasks:

- Load CSV or XLSX files,
- Parse and normalize date columns,
- Validate structure and monotonicity,
- Infer or confirm frequency, and
- Expose the cleaned series to the rest of the pipeline.

These steps ensure that the decomposition and forecast engines receive a consistent, well‑formed dataset.

## File Loading

The loader accepts:

- `.csv`, or
- `.xlsx`.

It uses the configuration object `DataConfig` to determine:

- which column contains dates,
- which column contains values, and
- whether frequency is provided or should be inferred.

Example:

```{python}
lumen.load_file("path/to/file/input.xlsx")
```

## Date Parsing

The loader:

- converts the date column to a `DatetimeIndex`,
- sorts the index,
- removes duplicates, and
- ensures the index is strictly monotonic.

If the date column cannot be parsed, the loader raises a clear, user‑friendly error.

## Frequency Inference

If the user does not specify a frequency, the loader attempts to infer it from the datetime index.

Supported frequencies:

- hourly,
- daily,
- weekly, and
- monthly.

The inferred frequency is stored and passed to the `DecompositionEngine`.

## Validation

The loader validates:

- the presence of required columns,
- that values are numeric,
- that the index is monotonic, and
- that the dataset contains enough history for decomposition.

If validation fails, the loader raises a descriptive exception.

## Output

After loading and validation, the loader exposes the following.

### Cleaned Series

A `pandas.Series` with:

- datetime index,
- float values,
- no missing timestamps, and
- no duplicates.

Accessed via:

```{python}
series = lumen.loader.get_series()
```

### Frequency

A string such as `"D"`, `"W"`, `"M"`, or `"H"`.

### Metadata

Stored in the loader and passed to downstream components.

## Pipeline Integration

The Data Loader feeds directly into:

- `SeriesDecomposition`,
- `ForecastEngine`, and
- `DiagnosticsEngine`.

It is the first step in the Lumen pipeline and ensures that all subsequent components receive a clean, validated, frequency‑aware series.

## Example Workflow

```{python}
lumen = Lumen(config)

# Load and validate
lumen.load_file("path/to/data/input.xlsx")

# Fit decomposition
lumen.fit()

# Forecast
lumen.forecast(steps = 30)
```
