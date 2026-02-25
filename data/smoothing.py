"""
Data smoothing pipeline for features.
"""

from typing import Dict

import numpy as np

from data.features import build_feature_vector
from utils.math_utils import RollingWindowMath


class DataSmoother:
    """Applies rolling window smoothing to incoming metric data."""

    def __init__(self, window_size: int = 5):
        """Initializes the data smoother.

        Args:
            window_size (int, optional): The capacity of the smoothing window. Defaults to 5.
        """
        self.window_size = window_size
        self.window = RollingWindowMath(window_size=self.window_size)

    def process(self, raw_metrics: Dict[str, float]) -> np.ndarray | None:
        """Ingests raw metrics and applies the rolling mean if buffer is full.

        Args:
            raw_metrics (Dict[str, float]): The raw dictionary of system metrics.

        Returns:
            np.ndarray | None: The smoothed feature vector, or None if the window is incomplete.
        """
        x_raw = build_feature_vector(raw_metrics)

        self.window.append(x_raw)

        if self.window.is_full():
            return self.window.get_mean()

        return None
