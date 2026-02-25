"""
Drift detection algorithms for long-term changes.
"""

import numpy as np

from config import defaults


class DriftDetector:
    """Detects concept drift using the CUSUM algorithm."""

    def __init__(
        self, k: float = defaults.CUSUM_K, threshold: float = defaults.CUSUM_THRESHOLD
    ):
        """Initializes the drift detector.

        Args:
            k (float, optional): The sensitivity parameter. Defaults to defaults.CUSUM_K.
            threshold (float, optional): The threshold for signaling drift. Defaults to defaults.CUSUM_THRESHOLD.
        """
        self.c_t: float = 0.0
        self.k: float = k
        self.threshold: float = threshold

    def update_cusum(self, severity: float) -> bool:
        """Updates the CUSUM statistic and evaluates drift.

        Args:
            severity (float): The current severity value.

        Returns:
            bool: True if drift is detected, False otherwise.
        """
        self.c_t = max(0.0, self.c_t + (severity - self.k))

        is_drift = self.c_t > self.threshold

        if is_drift:
            self.c_t = 0.0

        return is_drift


def calculate_divergence(mu_short: np.ndarray, mu_long: np.ndarray) -> float:
    """Calculates the divergence between short and long term means.

    Args:
        mu_short (np.ndarray): The short-term mean vector.
        mu_long (np.ndarray): The long-term mean vector.

    Returns:
        float: The L2 norm of the difference between the means.
    """
    return float(np.linalg.norm(mu_short - mu_long))
