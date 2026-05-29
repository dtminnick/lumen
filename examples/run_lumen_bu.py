
# python -m examples.run_lumen_bu

from lumen.data_loader import DataConfig
from lumen.orchestrator import Orchestrator
from lumen.aggregator_factory import AggregatorFactory
from lumen.plotter import Plotter

# Configure Lumen

config = DataConfig(
    date_col="Month",
    value_col="Value"
)

orchestrator = Orchestrator(data_config=config)

# Define input files

paths = {
    "RMD": "data/inputs/sample_input_data_rmd.xlsx",
    "TRM": "data/inputs/sample_input_data_term.xlsx",
    "INS": "data/inputs/sample_input_data_ins.xlsx"
}

# Run multi-series forecast with bottom-up aggregation

payload = orchestrator.run_multi(
    paths=paths,
    steps=24,
    aggregator=AggregatorFactory.create("bottom_up")
)

# Create a directory for plots

plotter = Plotter(save_dir="data/outputs/agg/plots")

# Loop through each work type and generate plots

from lumen.plotter import Plotter

# Create a directory for plots
plotter = Plotter(save_dir="data/outputs/agg/plots")

# Loop through each series and generate plots
for work_type in payload.individual.keys():

    history = payload.metadata["history"][work_type]
    forecast = payload.individual[work_type]
    diagnostics = payload.diagnostics[work_type]
    model = payload.models[work_type]   # <-- now available from Step 2

    future_index = forecast.index if forecast is not None else None

    plotter.plot_all(
        series=history,
        model=model,
        forecast=forecast,
        future_index=future_index,
        diagnostics=diagnostics,
        prefix = work_type
    )


# Export combined output file

orchestrator.export(
    "data/outputs/agg/combined_bottom_up.xlsx",
    payload
)
