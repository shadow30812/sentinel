import numpy as np

from config import defaults

DEFAULT_EPSILON = defaults.EPSILON_BASE
MAX_CONDITION_NUMBER = defaults.CONDITION_NUMBER


def apply_regularization(
    cov: np.ndarray, epsilon: float = DEFAULT_EPSILON
) -> np.ndarray:
    """Adds epsilon to the diagonal of the covariance matrix."""
    return cov + np.eye(cov.shape[0]) * epsilon


def check_condition_number(cov: np.ndarray) -> float:
    """Computes the condition number of a matrix."""
    try:
        # Use 2-norm condition number
        return np.linalg.cond(cov)
    except np.linalg.LinAlgError:
        return float("inf")


def safe_invert(
    cov: np.ndarray, base_epsilon: float = DEFAULT_EPSILON
) -> tuple[np.ndarray, bool, float]:
    """
    Attempts to safely invert the covariance matrix.
    Returns: (inverse_matrix, is_frozen, applied_epsilon)
    """
    current_eps = base_epsilon
    max_retries = 5

    for _ in range(max_retries):
        reg_cov = apply_regularization(cov, current_eps)
        cond_num = check_condition_number(reg_cov)

        if cond_num < MAX_CONDITION_NUMBER:
            try:
                inv_cov = np.linalg.inv(reg_cov)
                return inv_cov, False, current_eps
            except np.linalg.LinAlgError:
                pass

        # Scale epsilon aggressively if unstable
        current_eps *= 10.0

    # If all retries fail, return pseudo-inverse and flag to freeze updates
    return np.linalg.pinv(apply_regularization(cov, base_epsilon)), True, base_epsilon
