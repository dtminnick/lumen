
# Quick Start

This guide walks you through running Lumen end-to-end: load $\rightarrow$ decompose $|rightarrow$ forecast $\rightarrow$ diagnose $\rightarrow$ plot $\rightarrow$ export. for both single-series and multi-series workflows.

## 1. Install Dependencies

Lumen requires:

- `pandas`,
- `numpy`,
- `openpyxl`, and
- `matplotlib`.

Install them with:

```{python}
pip install pandas numpy openpyxl matplotlib
```

## 2. Configure Lumen

Create a `DataConfig` describing your dataset:

```{python}
from lumen.lumen import Lumen
from lumen.data_loader import DataConfig

config = DataConfig(
    date_col="Date",
    value_col="Value"
)

lumen = Lumen(config)
```

## 3. Load Your Data

```{python}
lumen.load_file("path/to/data/input.xlsx")
```

Your file must contain a timestamp column and a numeric value column.  Lumen automatically infers frequency when possible.

## 4. Fit Model

```{python}
lumen.fit()
```

This step fits a multiplicative trend and seasonality, computes fitted values, and initializes diagnostics.

## 5. Forecast

```{python}
forecast = lumen.forecast(steps=30)
```

This produces a 30-step forecast, a future index, and updated diagnostics including continuity checks.

## 6. Diagnostics

Lumen automatically computes:

- Residuals,
- Error metrics, e.g. MAE, RMSE, MAPE, SMAPE,
- Anomaly detection,
- Continuity at the forecast boundary, and 
- Trend and seasonal strength.

Inspect them:

```{python}
lumen.diagnostics.summary()
```

## 7. Plot

Use the `Plotter` to generate decomposition, forecast, and diagnostics plots.

```{python}
from lumen.plotter import Plotter

plotter = Plotter(save_dir="plots/")
plotter.plot_all(
    series=lumen.loader.get_series(),
    model=lumen.engine.model,
    forecast=lumen.forecast_df,
    future_index=lumen.engine.future_index_,
    diagnostics=lumen.diagnostics
)
```

## 8. Export

```{python}
lumen.export("data/output.xlsx")
```

Export includes:

- History,
- Forecast,
- Trend,
- Seasonal cycle,
- Seasonal factors over time,
- Fitted values,
- Residuals,
- Diagnostics summary, and 
- Anomalies.

## Multi-Series Workflow

Lumen also supports multi-series forecasting with bottom-up aggregation.

### 1. Configure the Orchetrator

```{python}
from lumen.data_loader import DataConfig
from lumen.orchestrator import Orchestrator
from lumen.aggregator_factory import AggregatorFactory

config = DataConfig(
    date_col="Month",
    value_col="Value"
)

orchestrator = Orchestrator(data_config=config)
```

### 2. Define Input Files

```{python}
paths = {
    "RMD": "data/inputs/sample_input_data_rmd.xlsx",
    "TRM": "data/inputs/sample_input_data_term.xlsx",
    "INS": "data/inputs/sample_input_data_ins.xlsx"
}
```

### 3. Run Multi-Series Forecast

```{python}
payload = orchestrator.run_multi(
    paths=paths,
    steps=24,
    aggregator=AggregatorFactory.create("bottom_up")
)
```

The payload contains:

- `payload.individual[work_type]` — per‑series forecasts
- `payload.diagnostics[work_type]` — per‑series diagnostics
- `payload.models[work_type]` — per‑series decomposition models
- `payload.metadata["history"][work_type]` — per‑series history
- `payload.aggregated` — aggregated forecast
- `payload.aggregated_diagnostics` — diagnostics for the aggregated series

### 4. Plot Each Series

```{python}
from lumen.plotter import Plotter

plotter = Plotter(save_dir="data/outputs/agg/plots")

for work_type in payload.individual.keys():
    history = payload.metadata["history"][work_type]
    forecast = payload.individual[work_type]
    diagnostics = payload.diagnostics[work_type]
    model = payload.models[work_type]

    future_index = forecast.index if forecast is not None else None

    plotter.plot_all(
        series=history,
        model=model,
        forecast=forecast,
        future_index=future_index,
        diagnostics=diagnostics,
        prefix=work_type
    )
```

Each series gets its own set of plots.

### 5. Export Combined Output

```{python}
orchestrator.export(
    "data/outputs/agg/combined_bottom_up.xlsx",
    payload
)
```
The export includes:

- All individual series,
- Aggregated forecast,
- Diagnostics,
- Components, and
- Metadata.
