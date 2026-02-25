"""
Online updating logic for statistical measures.
"""

import numpy as np


def update_mean(mu_t: np.ndarray, x_t: np.ndarray, lambda_factor: float) -> np.ndarray:
    """Computes the online mean update.

    Args:
        mu_t (np.ndarray): The previous mean vector.
        x_t (np.ndarray): The current incoming vector.
        lambda_factor (float): The exponential weighting factor.

    Returns:
        np.ndarray: The updated mean vector.
    """
    return (1.0 - lambda_factor) * mu_t + lambda_factor * x_t


def update_covariance(
    cov_t: np.ndarray, mu_t: np.ndarray, x_t: np.ndarray, lambda_factor: float
) -> np.ndarray:
    """Computes the online covariance update.

    Args:
        cov_t (np.ndarray): The previous covariance matrix.
        mu_t (np.ndarray): The previous mean vector.
        x_t (np.ndarray): The current incoming vector.
        lambda_factor (float): The exponential weighting factor.

    Returns:
        np.ndarray: The updated covariance matrix.
    """
    diff = (x_t - mu_t).reshape(-1, 1)
    rank_one_update = diff @ diff.T
    return (1.0 - lambda_factor) * cov_t + lambda_factor * rank_one_update
