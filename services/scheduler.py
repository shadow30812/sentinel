"""
Execution scheduler for the Sentinel engine.
"""

import threading
import time
import traceback
from typing import Callable


class EngineScheduler:
    """Schedules the execution of engine callbacks at a precise frequency."""

    def __init__(self, tick_callback: Callable, hz: float = 1.0):
        """Initializes the scheduler.

        Args:
            tick_callback (Callable): The function to call on each tick.
            hz (float, optional): The frequency of execution in Hertz. Defaults to 1.0.
        """
        self.tick_callback = tick_callback
        self.interval = 1.0 / hz
        self._stop_event = threading.Event()
        self._thread: threading.Thread | None = None

    def start(self):
        """Starts the background scheduling loop."""
        if self._thread is not None and self._thread.is_alive():
            return

        self._stop_event.clear()
        self._thread = threading.Thread(
            target=self._run_loop, daemon=True, name="SentinelScheduler"
        )
        self._thread.start()

    def stop(self):
        """Signals the loop to stop and waits for thread completion."""
        self._stop_event.set()
        if self._thread is not None:
            self._thread.join(timeout=2.0)

    def _run_loop(self):
        """Executes the precision timing loop."""
        while not self._stop_event.is_set():
            start_time = time.monotonic()

            try:
                self.tick_callback()
            except Exception:
                traceback.print_exc()

            elapsed = time.monotonic() - start_time
            sleep_time = self.interval - elapsed

            if sleep_time > 0:
                self._stop_event.wait(sleep_time)
