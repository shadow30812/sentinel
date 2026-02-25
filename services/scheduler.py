import threading
import time
from typing import Callable


class EngineScheduler:
    def __init__(self, tick_callback: Callable, hz: float = 1.0):
        self.tick_callback = tick_callback
        self.interval = 1.0 / hz
        self._stop_event = threading.Event()
        self._thread: threading.Thread | None = None

    def start(self):
        """Starts the background 1 Hz scheduling loop."""
        if self._thread is not None and self._thread.is_alive():
            return

        self._stop_event.clear()
        self._thread = threading.Thread(
            target=self._run_loop, daemon=True, name="SentinelScheduler"
        )
        self._thread.start()

    def stop(self):
        """Signals the loop to stop and joins the thread."""
        self._stop_event.set()
        if self._thread is not None:
            self._thread.join(timeout=2.0)

    def _run_loop(self):
        """The precision execution loop."""
        while not self._stop_event.is_set():
            start_time = time.monotonic()

            # Execute the engine pipeline
            try:
                self.tick_callback()
            except Exception as e:
                # We catch bare exceptions here to ensure the background thread never dies silently
                import traceback

                traceback.print_exc()

            # Delta-corrected sleep to maintain exact 1 Hz cadence
            elapsed = time.monotonic() - start_time
            sleep_time = self.interval - elapsed

            if sleep_time > 0:
                self._stop_event.wait(sleep_time)
