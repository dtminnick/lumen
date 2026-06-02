
# lumen/breaks/detector.py
from typing import List
import pandas as pd

from .types import Break
from .level_shift import LevelShiftDetector

class BreakDetector:
    def __init__(self):
        self.level_shift_detector = LevelShiftDetector()
        # later: self.trend_shift_detector = TrendShiftDetector()
        # later: self.seasonality_shift_detector = SeasonalityShiftDetector()
        # later: self.variance_shift_detector = VarianceShiftDetector()

    def detect(
        self,
        trend: pd.Series,
        seasonal: pd.Series | None = None,
        remainder: pd.Series | None = None,
    ) -> List[Break]:
        breaks: List[Break] = []

        # 1. Level shifts in trend
        breaks.extend(self.level_shift_detector.detect(trend))

        # 2. Later: add other detectors and extend

        # 3. Optional: merge nearby breaks, dedupe, adjust confidence
        # For now, just return raw list
        return breaks
