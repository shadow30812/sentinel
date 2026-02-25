"""
System metrics collection service.
"""

import time
from typing import Dict

import psutil


class SystemCollector:
    """Collects hardware and OS performance metrics."""

    def __init__(self):
        """Initializes the collector and internal counters."""
        self.last_time = time.time()

        self.last_disk = psutil.disk_io_counters()
        self.last_net = psutil.net_io_counters()

        psutil.cpu_percent()

    def collect(self) -> Dict[str, float]:
        """Samples system metrics to calculate rates.

        Returns:
            Dict[str, float]: A dictionary containing current system metrics.
        """
        current_time = time.time()
        dt = current_time - self.last_time

        if dt <= 0:
            dt = 1.0

        current_disk = psutil.disk_io_counters()
        current_net = psutil.net_io_counters()

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

        try:
            temps = psutil.sensors_temperatures()
            if temps and "coretemp" in temps:
                metrics["cpu_temperature"] = temps["coretemp"][0].current
            elif temps:
                metrics["cpu_temperature"] = list(temps.values())[0][0].current
            else:
                metrics["cpu_temperature"] = 0.0
        except Exception:
            metrics["cpu_temperature"] = 0.0

        self.last_time = current_time
        self.last_disk = current_disk
        self.last_net = current_net

        return metrics
