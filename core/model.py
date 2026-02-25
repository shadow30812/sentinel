"""
Adaptive statistical model representing the system baseline.
"""

import numpy as np

from config import defaults
from core.stability import safe_invert
from core.updates import update_covariance, update_mean
from utils.math_utils import calculate_mahalanobis


class StatisticalModel:
    """Maintains and updates the statistical properties of a dataset."""

    def __init__(self, lambda_factor: float):
        """Initializes the model.

        Args:
            lambda_factor (float): The exponential forgetting factor.
        """
        self.lambda_factor = lambda_factor
        self.mu: np.ndarray | None = None
        self.cov: np.ndarray | None = None
        self.cov_inv: np.ndarray | None = None
        self.threshold: float = 0.0
        self.is_initialized: bool = False
        self.is_frozen: bool = False

    def initialize_from_batch(self, data: np.ndarray):
        """Initializes the model parameters from a batch of data.

        Args:
            data (np.ndarray): The batch data matrix.
        """
        self.mu = np.mean(data, axis=0)
        self.cov = np.cov(data, rowvar=False)

        self.cov_inv, self.is_frozen, _ = safe_invert(self.cov)

        distances = []
        for x in data:
            d = calculate_mahalanobis(x, self.mu, self.cov_inv)
            distances.append(d)

        self.threshold = float(np.percentile(distances, 99))
        self.is_initialized = True

    def update(
        self,
        x_t: np.ndarray,
        severity: float,
        severity_limit: float = defaults.CONTAMINATION_LIMIT,
    ):
        """Performs the online update if contamination severity allows.

        Args:
            x_t (np.ndarray): The incoming feature vector.
            severity (float): The anomaly severity of the vector.
            severity_limit (float, optional): The contamination limit. Defaults to defaults.CONTAMINATION_LIMIT.
        """
        if not self.is_initialized or self.is_frozen:
            return

        if severity >= severity_limit:
            return

        new_cov = update_covariance(self.cov, self.mu, x_t, self.lambda_factor)

        new_mu = update_mean(self.mu, x_t, self.lambda_factor)

        new_cov_inv, freeze_flag, _ = safe_invert(new_cov)

        if freeze_flag:
            self.is_frozen = True
            return

        self.cov = new_cov
        self.mu = new_mu
        self.cov_inv = new_cov_inv
