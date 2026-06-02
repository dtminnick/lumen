# lumen/breaks/level_shift.py
from typing import List
import numpy as np
import pandas as pd

from .types import Break

class LevelShiftDetector:
    def __init__(self, k: float = 3.0, min_rel_jump: float = 0.05):
        self.k = k
        self.min_rel_jump = min_rel_jump

    def detect(self, trend: pd.Series) -> List[Break]:
        trend = trend.dropna()
        if len(trend) < 5:
            return []

        diffs = trend.diff()
        # robust scale
        mad = np.median(np.abs(diffs.dropna() - diffs.dropna().median()))
        if mad == 0:
            return []

        threshold = self.k * mad
        candidates = diffs[np.abs(diffs) > threshold]

        breaks: List[Break] = []
        for ts, delta in candidates.items():
            prev = trend.loc[ts - pd.offsets.DateOffset(months=1)] if ts in trend.index else None
            if prev is None or prev == 0:
                continue

            rel = delta / prev
            if abs(rel) < self.min_rel_jump:
                continue

            breaks.append(
                Break(
                    timestamp=ts,
                    type="level_shift",
                    component="trend",
                    magnitude_abs=float(delta),
                    magnitude_rel=float(rel),
                    confidence=0.8,  # you can refine later
                    meta={"detector": "level_shift"},
                )
            )

        return breaks
