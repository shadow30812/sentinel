import time
from typing import Dict

import psutil


class SystemCollector:
    def __init__(self):
        self.last_time = time.time()

        # Initialize I/O counters
        self.last_disk = psutil.disk_io_counters()
        self.last_net = psutil.net_io_counters()

        # Prime the CPU percent calculation
        psutil.cpu_percent()

    def collect(self) -> Dict[str, float]:
        """
        Samples system metrics. Must be called approximately every 1 second.
        Returns a dictionary of raw metrics.
        """
        current_time = time.time()
        dt = current_time - self.last_time

        # Failsafe to prevent division by zero if called too rapidly
        if dt <= 0:
            dt = 1.0

        current_disk = psutil.disk_io_counters()
        current_net = psutil.net_io_counters()

        # Calculate rates (bytes per second)
        disk_read_rate = (current_disk.read_bytes - self.last_disk.read_bytes) / dt
        disk_write_rate = (current_disk.write_bytes - self.last_disk.write_bytes) / dt
        net_sent_rate = (current_net.bytes_sent - self.last_net.bytes_sent) / dt
        net_recv_rate = (current_net.bytes_recv - self.last_net.bytes_recv) / dt

        metrics = {
            "cpu_percent": psutil.cpu_percent(),
            "ram_percent": psutil.virtual_memory().percent,
            "disk_read_rate": disk_read_rate,
            "disk_write_rate": disk_write_rate,
            "net_bytes_sent_rate": net_sent_rate,
            "net_bytes_recv_rate": net_recv_rate,
        }

        # Attempt to get optional CPU temperature (Linux specific)
        try:
            temps = psutil.sensors_temperatures()
            if temps and "coretemp" in temps:
                metrics["cpu_temperature"] = temps["coretemp"][0].current
            elif temps:  # Fallback to any available thermal zone
                metrics["cpu_temperature"] = list(temps.values())[0][0].current
            else:
                metrics["cpu_temperature"] = 0.0
        except Exception:
            metrics["cpu_temperature"] = 0.0

        # Update state
        self.last_time = current_time
        self.last_disk = current_disk
        self.last_net = current_net

        return metrics
