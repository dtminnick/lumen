
# lumen/breaks/break.py

from dataclasses import dataclass
from datetime import datetime
from typing import Literal, Optional

BreakType = Literal[
    "level_shift",
    "trend_shift",
    "seasonality_shift",
    "variance_shift",
    "operational_change",
    "migration_shift",
    "reporting_change"
]

ComponentType = Literal["trend", "seasonal", "remainder", "raw"]

@dataclass
class Break:
    timestamp: datetime
    type: BreakType
    component: ComponentType
    magnitude_abs: float
    magnitude_rel: float
    confidence: float
    meta: Optional[dict] = None
