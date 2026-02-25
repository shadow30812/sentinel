import numpy as np

from config import defaults
from utils.math_utils import calculate_mahalanobis


def calculate_severity(
    x_t: np.ndarray, mu: np.ndarray, cov_inv: np.ndarray, threshold: float
) -> float:
    """
    Calculates the severity S = D / T, where D is the Mahalanobis distance.
    """
    distance = calculate_mahalanobis(x_t, mu, cov_inv)

    # Protect against division by zero if threshold is uninitialized/malformed
    if threshold <= 0.0:
        return 0.0

    return distance / threshold


class RiskAccumulator:
    def __init__(self, alert_threshold: float = defaults.RISK_ALERT_THRESHOLD):
        self.risk: float = 0.0
        self.alert_threshold: float = alert_threshold

    def update(self, severity: float) -> tuple[float, bool]:
        """
        Updates the risk score based on severity.
        Returns: (current_risk, is_anomaly)
        """
        if severity > 1.0:
            # Nonlinear accumulation for compounding severe states
            self.risk += 4.0 * (severity - 1.0) ** 2
        else:
            # Exponential decay for normal behavior
            self.risk *= 0.95

        # Check for anomaly
        is_anomaly = self.risk > self.alert_threshold

        if is_anomaly:
            # Penalize the risk pool but do not reset entirely to prevent alert flapping
            self.risk *= 0.5

        return self.risk, is_anomaly
