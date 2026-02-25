from collections import deque

import numpy as np


def calculate_mahalanobis(x: np.ndarray, mu: np.ndarray, cov_inv: np.ndarray) -> float:
    """
    Computes the Mahalanobis distance manually without scipy.
    D = sqrt( (x - mu)^T * cov_inv * (x - mu) )
    """
    delta = x - mu
    # Matrix multiplication: delta @ cov_inv @ delta
    m_squared = delta @ cov_inv @ delta

    # Protect against floating-point precision issues yielding tiny negatives
    return float(np.sqrt(max(0.0, m_squared)))


class RollingWindowMath:
    """
    Maintains a rolling window for streaming scalar or vector data
    and computes the rolling mean efficiently.
    """

    def __init__(self, window_size: int = 5):
        self.window_size = window_size
        self.buffer = deque(maxlen=window_size)

    def append(self, value: np.ndarray | float):
        """Adds a new value to the rolling window."""
        self.buffer.append(value)

    def get_mean(self) -> np.ndarray | float:
        """Returns the mean of the current window."""
        if not self.buffer:
            return 0.0
        # For numpy arrays, this efficiently computes the mean along the time axis
        return np.mean(self.buffer, axis=0)

    def is_full(self) -> bool:
        """Checks if the window has reached its target size."""
        return len(self.buffer) == self.window_size
