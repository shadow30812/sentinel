import json
from pathlib import Path
from typing import Any, Dict, Optional

import numpy as np

from config import paths
from utils.atomic_write import atomic_write


class PersistenceManager:
    def __init__(self):
        self.state_file = paths.STATE_FILE
        self.short_model_file = paths.SHORT_MODEL_FILE
        self.long_model_file = paths.LONG_MODEL_FILE

    def save_model(
        self, filepath: Path, mu: np.ndarray, cov: np.ndarray, cov_inv: np.ndarray
    ):
        """Atomically saves matrix states using numpy's compressed format."""
        if mu is None or cov is None or cov_inv is None:
            return

        with atomic_write(filepath, mode="wb") as f:
            np.savez_compressed(f, mu=mu, cov=cov, cov_inv=cov_inv)

    def load_model(self, filepath: Path) -> Optional[Dict[str, np.ndarray]]:
        """Loads matrix states if the file exists."""
        if not filepath.exists():
            return None

        try:
            with np.load(filepath) as data:
                return {
                    "mu": data["mu"],
                    "cov": data["cov"],
                    "cov_inv": data["cov_inv"],
                }
        except Exception:
            # Corrupted file handling (e.g., manual user deletion while running)
            return None

    def save_state(self, state_dict: Dict[str, Any]):
        """Atomically saves scalar configuration, thresholds, and risk state."""
        with atomic_write(self.state_file, mode="w") as f:
            json.dump(state_dict, f, indent=4)

    def load_state(self) -> Dict[str, Any]:
        """Loads the JSON state file."""
        if not self.state_file.exists():
            return {}

        try:
            with open(self.state_file, "r", encoding="utf-8") as f:
                return json.load(f)
        except json.JSONDecodeError:
            return {}
