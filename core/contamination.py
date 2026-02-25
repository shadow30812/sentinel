"""
Contamination gating logic for anomaly exclusion.
"""

from config import defaults


def is_contaminated(
    severity: float, severity_limit: float = defaults.CONTAMINATION_LIMIT
) -> bool:
    """Evaluates whether the current metric vector is too anomalous to be absorbed.

    Args:
        severity (float): The calculated anomaly severity.
        severity_limit (float, optional): The threshold for contamination. Defaults to defaults.CONTAMINATION_LIMIT.

    Returns:
        bool: True if the severity equals or exceeds the limit, indicating contamination.
    """
    return severity >= severity_limit
