from typing import Any, Callable, Dict, Optional

import numpy as np

from config import defaults, paths
from core.anomaly import RiskAccumulator, calculate_severity
from core.contamination import is_contaminated
from core.drift import DriftDetector, calculate_divergence
from core.model import StatisticalModel
from core.persistence import PersistenceManager
from data.collector import SystemCollector
from data.smoothing import DataSmoother
from services.logger import logger


class SentinelEngine:
    def __init__(self, ui_callback: Optional[Callable[[Dict[str, Any]], None]] = None):
        # Data Pipeline
        self.collector = SystemCollector()
        self.smoother = DataSmoother(window_size=5)

        # Statistical Core (Dual-Timescale)
        self.lambda_short = defaults.LAMBDA_SHORT
        self.lambda_long = defaults.LAMBDA_LONG
        self.model_short = StatisticalModel(lambda_factor=self.lambda_short)
        self.model_long = StatisticalModel(lambda_factor=self.lambda_long)

        # Anomaly & Drift Monitors
        self.risk_accumulator = RiskAccumulator(
            alert_threshold=defaults.RISK_ALERT_THRESHOLD
        )
        self.drift_detector = DriftDetector(
            k=defaults.CUSUM_K, threshold=defaults.CUSUM_THRESHOLD
        )

        # Persistence & State
        self.persistence = PersistenceManager()
        self.ui_callback = ui_callback

        # Training State (30 mins = 1800 ticks at 1 Hz)
        self.training_target = defaults.DEFAULT_TRAINING_SECONDS
        self.training_buffer = []
        self.is_training = True

        self._attempt_load_state()

    def _attempt_load_state(self):
        """Attempts to load pre-existing models from disk to bypass training."""
        short_state = self.persistence.load_model(self.persistence.short_model_file)
        long_state = self.persistence.load_model(self.persistence.long_model_file)
        system_state = self.persistence.load_state()

        if short_state and long_state and "threshold" in system_state:
            # Restore Short Model
            self.model_short.mu = short_state["mu"]
            self.model_short.cov = short_state["cov"]
            self.model_short.cov_inv = short_state["cov_inv"]
            self.model_short.threshold = system_state["threshold"]
            self.model_short.is_initialized = True

            # Restore Long Model
            self.model_long.mu = long_state["mu"]
            self.model_long.cov = long_state["cov"]
            self.model_long.cov_inv = long_state["cov_inv"]
            self.model_long.threshold = system_state["threshold"]
            self.model_long.is_initialized = True

            # Restore Risk
            self.risk_accumulator.risk = system_state.get("risk", 0.0)

            self.is_training = False
            logger.info("Restored Sentinel models from persistence.")
        else:
            logger.info("No valid persistence found. Entering Training Mode.")

    def tick(self):
        """The main pipeline executed every 1 second by the Scheduler."""
        # 1. Collect and Smooth Data
        raw_metrics = self.collector.collect()
        x_t = self.smoother.process(raw_metrics)

        if x_t is None:
            return  # Buffer not full yet

        # 2. Route based on state (Training vs Monitoring)
        if self.is_training:
            self._handle_training(x_t, raw_metrics)
        else:
            self._handle_monitoring(x_t, raw_metrics)

    def _handle_training(self, x_t: np.ndarray, raw_metrics: Dict[str, float]):
        """Accumulates data for 30 minutes, then initializes the models."""
        self.training_buffer.append(x_t)
        progress = len(self.training_buffer)

        if progress >= self.training_target:
            logger.info("Training complete. Initializing models...")
            batch_data = np.array(self.training_buffer)

            # Initialize both models identically
            self.model_short.initialize_from_batch(batch_data)
            self.model_long.initialize_from_batch(batch_data)

            self._save_all_state()
            self.training_buffer.clear()
            self.is_training = False

        # Push training state to UI
        if self.ui_callback:
            self.ui_callback(
                {
                    "mode": "training",
                    "progress": progress,
                    "target": self.training_target,
                    "metrics": raw_metrics,
                }
            )

    def _handle_monitoring(self, x_t: np.ndarray, raw_metrics: Dict[str, float]):
        """The primary online evaluation and update logic."""
        # A. Calculate Severity using Long-Term (Baseline) model
        severity = calculate_severity(
            x_t, self.model_long.mu, self.model_long.cov_inv, self.model_long.threshold
        )

        # B. Accumulate Risk
        risk_val, is_anomaly = self.risk_accumulator.update(severity)
        if is_anomaly:
            logger.warning(
                f"ANOMALY DETECTED! Risk: {risk_val:.2f}, Severity: {severity:.2f}"
            )

        # C. Detect Drift (CUSUM)
        is_drift = self.drift_detector.update_cusum(severity)
        if is_drift:
            logger.info("System Drift Detected via CUSUM. Adjusting short-term model.")
            # Action: Reinitialize short-term model to track the new normal faster
            self.model_short.mu = self.model_long.mu.copy()
            self.model_short.cov = self.model_long.cov.copy()
            self.model_short.cov_inv = self.model_long.cov_inv.copy()

        # D. Divergence Check
        divergence = calculate_divergence(self.model_short.mu, self.model_long.mu)

        # E. Online Updates (Gated by Contamination)
        if not is_contaminated(severity, severity_limit=defaults.CONTAMINATION_LIMIT):
            self.model_short.update(x_t, severity)
            self.model_long.update(x_t, severity)

        # F. Push State to UI
        if self.ui_callback:
            status = (
                "🔴 Anomaly"
                if is_anomaly
                else ("🟡 Elevated" if risk_val > 5.0 else "🟢 Normal")
            )
            self.ui_callback(
                {
                    "mode": "monitoring",
                    "metrics": raw_metrics,
                    "severity": severity,
                    "risk": risk_val,
                    "status": status,
                    "divergence": divergence,
                    "is_frozen": self.model_long.is_frozen,
                }
            )

    def trigger_retraining(self, target_seconds: int):
        """Forces the system to discard the current model and retrain."""
        from services.logger import (
            logger,  # inline import to avoid circular issues if any
        )

        self.training_target = target_seconds
        self.training_buffer.clear()

        # Reset mathematical states
        self.model_short.is_initialized = False
        self.model_long.is_initialized = False
        self.risk_accumulator.risk = 0.0

        self.is_training = True
        logger.info(f"Manual retraining triggered for {target_seconds} seconds.")

    def _save_all_state(self):
        """Persists the mathematical models and scalar states."""
        self.persistence.save_model(
            self.persistence.short_model_file,
            self.model_short.mu,
            self.model_short.cov,
            self.model_short.cov_inv,
        )
        self.persistence.save_model(
            self.persistence.long_model_file,
            self.model_long.mu,
            self.model_long.cov,
            self.model_long.cov_inv,
        )
        self.persistence.save_state(
            {"threshold": self.model_long.threshold, "risk": self.risk_accumulator.risk}
        )

    def shutdown(self):
        """Called on application exit to ensure final state is saved."""
        if not self.is_training:
            self._save_all_state()
            logger.info("Sentinel shutting down. State saved.")
