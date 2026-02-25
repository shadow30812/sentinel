from typing import Dict

import numpy as np

# Hardcoded feature order to ensure deterministic vector construction
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
    """
    Converts a metrics dictionary into a strict numpy array vector x_t.
    Ensures dimension d <= 10 constraint is met.
    """
    vector_data = []
    for key in FEATURE_KEYS:
        vector_data.append(metrics.get(key, 0.0))

    x_t = np.array(vector_data, dtype=np.float64)

    # Assert hard constraint d <= 10
    if len(x_t) > 10:
        raise ValueError(f"Feature vector dimension {len(x_t)} exceeds maximum of 10.")

    return x_t
