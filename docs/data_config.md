
# Data Configuration

`DataConfig` defines all user‑controlled settings for loading, interpreting, and preparing a dataset in Lumen.
It acts as the single source of truth for:

- which columns to read,
- how to interpret dates,
- how to infer or override frequency,
- how to control decomposition behavior, and
- how to format output.

Every component in the pipeline - `DataLoader`, `SeriesDecomposition`, `ForecastEngine`, `DiagnosticsEngine`, `ExportEngine` - reads from this configuration.

## Purpose

`DataConfig` ensures that Lumen behaves predictably, explicitly, and consistently across datasets.
It removes ambiguity by letting the user specify:

- what the data looks like,
- how it should be interpreted, and
- how the model should behave.

This makes the pipeline easier to document, test, and reason about.

## Fields

Below are the fields currently supported by `DataConfig`.

### date_col

Name of the column containing timestamps.

- Default: "date".
- Must be convertible to a `DatetimeIndex`.

Used by the `DataLoader`.

### value_col

Name of the column containing numeric values.

- Default: "value".
- Must be numeric.

### freq

Optional frequency override.

- `"H"` (hourly).
- `"D"` (daily).
- `"W"` (weekly).
- `"M"` (monthly).

If omitted, Lumen infers frequency automatically.

### period

Optional seasonal period override.

Examples:

- 12 for monthly data.
- 7 for weekly data.
- 24 for hourly data.
- 52 for retail weekly cycles.

If provided, it overrides the loader’s frequency‑based mapping.

### loess_frac

Optional LOESS smoothing override for trend estimation.

- Float between 0 and 1.
- Smaller values for more flexible trend.
- Larger values for smoother trend.

If omitted, Lumen chooses a default based on frequency.

### file_type

Optional override for file type.

- `"csv"`.
- `"xlsx"`.

If omitted, Lumen infers from the file extension.

### rounding

Optional rounding for exported forecast values.

- Integer number of decimal places
- `None` if no rounding applied

Used by the `ExportEngine`.

### timezone

Optional timezone for hourly/daily data.

- String like `"UTC"`, `"US/Eastern"`, `"Europe/London"`.
- Applied during index localization.

Timezone ensures correct seasonal indexing and avoids DST issues.

### Example Configuration

```{python}
from lumen.config import DataConfig

config = DataConfig(
    date_col="Month",
    value_col="Sales",
    freq="M",
    period=12,
    loess_frac=0.25,
    rounding=2,
    timezone="US/Eastern"
)
```

## Pipeline Integration

### Data Loader

- Reads `date_col`, `value_col`, `freq`, `file_type`, `timezone`.

### Decomposition Engine

- Uses `period` and `loess_frac`.
- Applies seasonal normalization.
- Computes trend in log‑space.

### Forecast Engine

- Uses `freq` and `period` to generate future timestamps.
- Applies trend and seasonality.

### Diagnostics

- Uses `period` for seasonal strength.
- Uses `freq` for continuity checks.

### Export Engine

- Uses `rounding`.
- Uses `file_type` for output format.

## Design Philosophy

`DataConfig` is intentionally:

- Explicit, no hidden defaults,
- Minimal, only fields that affect behavior,
- Stable, safe for long‑term use, and
- Documentable, every field has a clear purpose.

It keeps the user‑facing API simple while giving advanced users full control.