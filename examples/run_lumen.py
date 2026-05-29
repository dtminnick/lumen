
# python -m examples.run_lumen

from lumen.data_loader import DataConfig
from lumen.lumen import Lumen
from lumen.plotter import Plotter

# Configure Lumen.

config = DataConfig(
    date_col="Month",
    value_col="Value"
)

lumen = Lumen(data_config=config)

plotter = Plotter(save_dir="data/outputs/rmd/")

# Load data.

lumen.load_file("data/inputs/sample_input_data_rmd.xlsx")

# Decompose.

lumen.fit()

# Forecast.

forecast = lumen.forecast(24)

# Plot forecast.

plotter.plot_all(
    series=lumen.loader.get_series(),
    model=lumen.engine.model,
    forecast=forecast,
    future_index=lumen.engine.future_index_,
    diagnostics=lumen.diagnostics
)

# Diagnostics to terminal.

print("\nDiagnostics Summary\n")
print(lumen.diagnostics.summary().to_string(index=False))
print("\n")

# Export.

lumen.export("data/outputs/rmd/lumen_export_rmd.xlsx")
