import numpy as np

from config import defaults


class DriftDetector:
    def __init__(
        self, k: float = defaults.CUSUM_K, threshold: float = defaults.CUSUM_THRESHOLD
    ):
        self.c_t: float = 0.0
        self.k: float = k
        self.threshold: float = threshold

    def update_cusum(self, severity: float) -> bool:
        """
        Updates the CUSUM statistic: C_t = max(0, C_{t-1} + (S_t - k))
        Returns True if a drift event is detected.
        """
        self.c_t = max(0.0, self.c_t + (severity - self.k))

        is_drift = self.c_t > self.threshold

        if is_drift:
            # Reset C_t after logging a drift event
            self.c_t = 0.0

        return is_drift


def calculate_divergence(mu_short: np.ndarray, mu_long: np.ndarray) -> float:
    """
    Calculates the L2 norm divergence between the short-term and long-term means:
    || mu_short - mu_long ||
    """
    return float(np.linalg.norm(mu_short - mu_long))
