# --- Training Defaults ---
DEFAULT_TRAINING_SECONDS = 1800  # 30 minutes

# --- Statistical Model ---
LAMBDA_SHORT = 0.01
LAMBDA_LONG = 0.001
EPSILON_BASE = 1e-4
CONDITION_NUMBER = 1e6

# --- Anomaly & Contamination ---
CONTAMINATION_LIMIT = 0.8
RISK_ALERT_THRESHOLD = 20.0
AUDIO_ALARM_THRESHOLD = 25.0  # Point at which the physical alarm sounds

# --- Drift (CUSUM) ---
CUSUM_K = 0.05
CUSUM_THRESHOLD = 10.0
