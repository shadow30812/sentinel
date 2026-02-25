import numpy as np


def update_mean(mu_t: np.ndarray, x_t: np.ndarray, lambda_factor: float) -> np.ndarray:
    """
    Computes the online mean update:
    mu_{t+1} = (1 - lambda) * mu_t + lambda * x_t
    """
    return (1.0 - lambda_factor) * mu_t + lambda_factor * x_t


def update_covariance(
    cov_t: np.ndarray, mu_t: np.ndarray, x_t: np.ndarray, lambda_factor: float
) -> np.ndarray:
    """
    Computes the online covariance update using the previous mean:
    Sigma_{t+1} = (1 - lambda) * Sigma_t + lambda * (x_t - mu_t)(x_t - mu_t)^T
    """
    diff = (x_t - mu_t).reshape(-1, 1)  # Ensure column vector
    rank_one_update = diff @ diff.T
    return (1.0 - lambda_factor) * cov_t + lambda_factor * rank_one_update
