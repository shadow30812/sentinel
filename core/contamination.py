from config import defaults


def is_contaminated(
    severity: float, severity_limit: float = defaults.CONTAMINATION_LIMIT
) -> bool:
    """
    Evaluates whether the current metric vector is too anomalous to be absorbed
    into the baseline statistical model.

    Returns True if Severity (S) >= S_update, meaning the update should be skipped.
    """
    return severity >= severity_limit
