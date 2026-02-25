"""
Path definitions for the Sentinel configuration.
"""

import os
from pathlib import Path

BASE_DIR = Path(os.path.expanduser("~/.sentinel"))

STATE_FILE = BASE_DIR / "state.json"
SHORT_MODEL_FILE = BASE_DIR / "model_short.npz"
LONG_MODEL_FILE = BASE_DIR / "model_long.npz"
LOG_FILE = BASE_DIR / "sentinel.log"
