from typing import Dict

import numpy as np

from data.features import build_feature_vector
from utils.math_utils import RollingWindowMath


class DataSmoother:
    def __init__(self, window_size: int = 5):
        self.window_size = window_size
        self.window = RollingWindowMath(window_size=self.window_size)

    def process(self, raw_metrics: Dict[str, float]) -> np.ndarray | None:
        """
        Ingests raw metrics, constructs the feature vector, and applies
        the rolling mean.

        Returns the smoothed numpy array, or None if the buffer isn't full yet
        (e.g., during the first 5 seconds of application startup).
        """
        # 1. Convert dictionary to R^d vector
        x_raw = build_feature_vector(raw_metrics)

        # 2. Add to rolling window
        self.window.append(x_raw)

        # 3. Only return smoothed data once we have a full window
        if self.window.is_full():
            return self.window.get_mean()

        return None
