"""
General mathematical and statistical utilities.
"""

from collections import deque

import numpy as np


def calculate_mahalanobis(x: np.ndarray, mu: np.ndarray, cov_inv: np.ndarray) -> float:
    """Computes the Mahalanobis distance.

    Args:
        x (np.ndarray): The input vector.
        mu (np.ndarray): The mean vector.
        cov_inv (np.ndarray): The inverse covariance matrix.

    Returns:
        float: The calculated Mahalanobis distance.
    """
    delta = x - mu
    m_squared = delta @ cov_inv @ delta

    return float(np.sqrt(max(0.0, m_squared)))


class RollingWindowMath:
    """Maintains a rolling window for computing metrics over sequential data."""

    def __init__(self, window_size: int = 5):
        """Initializes the rolling window.

        Args:
            window_size (int, optional): The capacity of the rolling window. Defaults to 5.
        """
        self.window_size = window_size
        self.buffer = deque(maxlen=window_size)

    def append(self, value: np.ndarray | float):
        """Adds a new value to the rolling window.

        Args:
            value (np.ndarray | float): The data point to append.
        """
        self.buffer.append(value)

    def get_mean(self) -> np.ndarray | float:
        """Returns the mean of the current window.

        Returns:
            np.ndarray | float: The calculated mean, or 0.0 if the buffer is empty.
        """
        if not self.buffer:
            return 0.0
        return np.mean(self.buffer, axis=0)

    def is_full(self) -> bool:
        """Checks if the window has reached its target size.

        Returns:
            bool: True if the window is full, False otherwise.
        """
        return len(self.buffer) == self.window_size
