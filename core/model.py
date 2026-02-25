import numpy as np

from config import defaults
from core.stability import safe_invert
from core.updates import update_covariance, update_mean
from utils.math_utils import calculate_mahalanobis


class StatisticalModel:
    def __init__(self, lambda_factor: float):
        self.lambda_factor = lambda_factor
        self.mu: np.ndarray | None = None
        self.cov: np.ndarray | None = None
        self.cov_inv: np.ndarray | None = None
        self.threshold: float = 0.0
        self.is_initialized: bool = False
        self.is_frozen: bool = False

    def initialize_from_batch(self, data: np.ndarray):
        """
        Initializes the model from a 30-minute batch of data.
        data shape expected: (N_samples, n_features)
        """
        self.mu = np.mean(data, axis=0)
        self.cov = np.cov(data, rowvar=False)

        # Initial safe inversion & regularization
        self.cov_inv, self.is_frozen, _ = safe_invert(self.cov)

        # Calculate Mahalanobis distances for the training batch to set Threshold
        distances = []
        for x in data:
            d = calculate_mahalanobis(x, self.mu, self.cov_inv)
            distances.append(d)

        # Set T = 99th percentile
        self.threshold = float(np.percentile(distances, 99))
        self.is_initialized = True

    def update(
        self,
        x_t: np.ndarray,
        severity: float,
        severity_limit: float = defaults.CONTAMINATION_LIMIT,
    ):
        """
        Performs the online update if contamination severity allows.
        """
        if not self.is_initialized or self.is_frozen:
            return

        # Contamination gating: S < S_update
        if severity >= severity_limit:
            return  # Skip update to prevent anomaly absorption

        # 1. Update Covariance (using current mean)
        new_cov = update_covariance(self.cov, self.mu, x_t, self.lambda_factor)

        # 2. Update Mean
        new_mu = update_mean(self.mu, x_t, self.lambda_factor)

        # 3. Assess Stability and Invert
        new_cov_inv, freeze_flag, _ = safe_invert(new_cov)

        if freeze_flag:
            self.is_frozen = True  # Temporarily freeze if mathematically unstable
            return

        # Commit updates
        self.cov = new_cov
        self.mu = new_mu
        self.cov_inv = new_cov_inv
