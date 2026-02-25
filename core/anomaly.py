"""
Anomaly detection and risk scoring mechanisms.
"""

import numpy as np

from config import defaults
from utils.math_utils import calculate_mahalanobis


def calculate_severity(
    x_t: np.ndarray, mu: np.ndarray, cov_inv: np.ndarray, threshold: float
) -> float:
    """Calculates the severity score of an incoming vector.

    Args:
        x_t (np.ndarray): The current vector.
        mu (np.ndarray): The mean vector.
        cov_inv (np.ndarray): The inverse covariance matrix.
        threshold (float): The baseline distance threshold.

    Returns:
        float: The calculated severity score.
    """
    distance = calculate_mahalanobis(x_t, mu, cov_inv)

    if threshold <= 0.0:
        return 0.0

    return distance / threshold


class RiskAccumulator:
    """Accumulates system risk based on sequential severity readings."""

    def __init__(self, alert_threshold: float = defaults.RISK_ALERT_THRESHOLD):
        """Initializes the risk accumulator.

        Args:
            alert_threshold (float, optional): The threshold at which an anomaly is triggered. Defaults to defaults.RISK_ALERT_THRESHOLD.
        """
        self.risk: float = 0.0
        self.alert_threshold: float = alert_threshold

    def update(self, severity: float) -> tuple[float, bool]:
        """Updates the internal risk score given a new severity.

        Args:
            severity (float): The current severity value.

        Returns:
            tuple[float, bool]: A tuple containing the current risk and a boolean indicating if an anomaly state is reached.
        """
        if severity > 1.0:
            self.risk += 4.0 * (severity - 1.0) ** 2
        else:
            self.risk *= 0.95

        is_anomaly = self.risk > self.alert_threshold

        if is_anomaly:
            self.risk *= 0.5

        return self.risk, is_anomaly
