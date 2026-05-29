
# Installation

Lumen is lightweight and only has a few core dependencies.  You can install everything you need in a single step.

## 1. Requirements

Lumen requires:

- Python 3.9+,
- pandas,
- numpy,
- openpyxl (for Excel support), and 
- matplotlib (for plotting).

## 2. Install Core Dependencies

```{bash}
pip install pandas numpy openpyxl matplotlib
```

This gives you everything needed to load data, fit the model, forecast, run diagnostics, and export results.

## 3. Install Documentation Tools (Optional)

If you want to build the Lumen documentation locally:

```{bash}
pip install mkdocs-material
pip install mkdocstrings-python
```

These enable the Material theme, automatic API documentation, and live preview with `mkdocs serve`.
