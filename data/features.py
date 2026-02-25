"""
Feature vector generation from raw metrics.
"""

from typing import Dict

import numpy as np

FEATURE_KEYS = [
    "cpu_percent",
    "ram_percent",
    "disk_read_rate",
    "disk_write_rate",
    "net_bytes_sent_rate",
    "net_bytes_recv_rate",
    "cpu_temperature",
]


def build_feature_vector(metrics: Dict[str, float]) -> np.ndarray:
    """Converts a metrics dictionary into a strict numpy array vector.

    Args:
        metrics (Dict[str, float]): The incoming metrics dictionary.

    Returns:
        np.ndarray: A feature vector representation of the metrics.

    Raises:
        ValueError: If the resulting feature vector exceeds dimension length 10.
    """
    vector_data = []
    for key in FEATURE_KEYS:
        vector_data.append(metrics.get(key, 0.0))

    x_t = np.array(vector_data, dtype=np.float64)

    if len(x_t) > 10:
        raise ValueError(f"Feature vector dimension {len(x_t)} exceeds maximum of 10.")

    return x_t
