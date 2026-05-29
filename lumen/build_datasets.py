
import numpy as np
import pandas as pd
from pathlib import Path

np.random.seed(42)

def add_noise(size, scale=2.0):
    return np.random.normal(0, scale, size)

def seasonal_component(t, period, amplitude):
    return amplitude * np.sin(2 * np.pi * t / period)

def save_excel(df, filename):
    df.to_excel(filename, index=True)
    print(f"Saved: {filename}")

def build_hourly():
    idx = pd.date_range("2024-01-01", periods=60*24, freq="h")
    t = np.arange(len(idx))

    df = pd.DataFrame(index=idx)

    df["value_flat"] = 100 + add_noise(len(t))

    df["value_trend"] = 50 + 0.05 * t + add_noise(len(t))

    df["value_seasonal"] = 100 + seasonal_component(t, period=24, amplitude=20) + add_noise(len(t))

    df["value_trend_seasonal"] = (
        50 + 0.05 * t + seasonal_component(t, 24, 20) + add_noise(len(t))
    )

    # Structural break at day 30
    break_point = 30 * 24
    y = 50 + 0.05 * t + add_noise(len(t))
    y[break_point:] += 150
    df["value_break_trend"] = y

    df["value_decline_seasonal"] = (
        300 - 0.1 * t + seasonal_component(t, 24, 20) + add_noise(len(t))
    )

    save_excel(df, "./data/inputs/test/test_hourly.xlsx")
    return df

def build_daily():
    idx = pd.date_range("2020-01-01", periods=365*3, freq="D")
    t = np.arange(len(idx))

    df = pd.DataFrame(index=idx)

    df["value_flat"] = 100 + add_noise(len(t))

    df["value_trend"] = 50 + 0.02 * t + add_noise(len(t))

    df["value_seasonal"] = 100 + seasonal_component(t, 7, 15) + add_noise(len(t))

    df["value_trend_seasonal"] = (
        50 + 0.02 * t + seasonal_component(t, 7, 15) + add_noise(len(t))
    )

    break_point = 365
    y = 50 + 0.02 * t + add_noise(len(t))
    y[break_point:] += 200
    df["value_break_trend"] = y

    df["value_decline_seasonal"] = (
        300 - 0.05 * t + seasonal_component(t, 7, 15) + add_noise(len(t))
    )

    save_excel(df, "./data/inputs/test/test_daily.xlsx")
    return df

def build_weekly():
    idx = pd.date_range("2018-01-01", periods=52*6, freq="W")
    t = np.arange(len(idx))

    df = pd.DataFrame(index=idx)

    df["value_flat"] = 100 + add_noise(len(t))

    df["value_trend"] = 50 + 0.5 * t + add_noise(len(t))

    df["value_seasonal"] = 100 + seasonal_component(t, 52, 30) + add_noise(len(t))

    df["value_trend_seasonal"] = (
        50 + 0.5 * t + seasonal_component(t, 52, 30) + add_noise(len(t))
    )

    break_point = 52 * 3
    y = 50 + 0.5 * t + add_noise(len(t))
    y[break_point:] += 300
    df["value_break_trend"] = y

    df["value_decline_seasonal"] = (
        500 - 1.0 * t + seasonal_component(t, 52, 30) + add_noise(len(t))
    )

    save_excel(df, "./data/inputs/test/test_weekly.xlsx")
    return df

def build_monthly():
    idx = pd.date_range("2014-01-01", periods=12*10, freq="ME")
    t = np.arange(len(idx))

    df = pd.DataFrame(index=idx)

    df["value_flat"] = 100 + add_noise(len(t))

    df["value_trend"] = 50 + 0.3 * t + add_noise(len(t))

    df["value_seasonal"] = 100 + seasonal_component(t, 12, 25) + add_noise(len(t))

    df["value_trend_seasonal"] = (
        50 + 0.3 * t + seasonal_component(t, 12, 25) + add_noise(len(t))
    )

    break_point = 12 * 5
    y = 50 + 0.3 * t + add_noise(len(t))
    y[break_point:] += 400
    df["value_break_trend"] = y

    df["value_decline_seasonal"] = (
        800 - 2.0 * t + seasonal_component(t, 12, 25) + add_noise(len(t))
    )

    save_excel(df, "./data/inputs/test/test_monthly.xlsx")
    return df

if __name__ == "__main__":
    build_hourly()
    build_daily()
    build_weekly()
    build_monthly()
