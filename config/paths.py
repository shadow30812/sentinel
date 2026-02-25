import os
from pathlib import Path

# Base directory for all persistence and logging
BASE_DIR = Path(os.path.expanduser("~/.sentinel"))

# File paths
STATE_FILE = BASE_DIR / "state.json"
SHORT_MODEL_FILE = BASE_DIR / "model_short.npz"
LONG_MODEL_FILE = BASE_DIR / "model_long.npz"
LOG_FILE = BASE_DIR / "sentinel.log"
