"""
Main application UI and process manager.
"""

import os
import subprocess
import sys
import time
from typing import Any, Dict

from PySide6.QtCore import Qt, QThread, Signal, Slot
from PySide6.QtGui import QIcon, QKeySequence, QShortcut
from PySide6.QtNetwork import QLocalServer, QLocalSocket
from PySide6.QtWidgets import (
    QApplication,
    QComboBox,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QProgressBar,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from config import defaults
from monitor.plotter import RealTimePlotter
from services.engine import SentinelEngine
from services.scheduler import EngineScheduler


class EngineWorker(QThread):
    """Hosts the SentinelEngine and Scheduler in a background QThread."""

    data_emitted = Signal(dict)

    def __init__(self):
        """Initializes the engine worker thread."""
        super().__init__()
        self.engine = SentinelEngine(
            ui_callback=lambda data: self.data_emitted.emit(data)
        )
        self.scheduler = EngineScheduler(tick_callback=self.engine.tick, hz=1.0)

    def run(self):
        """Starts the scheduler within the thread."""
        self.scheduler.start()

    def stop(self):
        """Stops the scheduler and performs engine shutdown."""
        self.scheduler.stop()
        self.engine.shutdown()
        self.quit()
        self.wait()


class SentinelMainWindow(QMainWindow):
    """Main window for the Sentinel application UI."""

    def __init__(self):
        """Initializes the UI layout and background services."""
        super().__init__()
        self.setWindowTitle("Sentinel - Adaptive Monitoring")
        self.resize(800, 600)

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QVBoxLayout(self.central_widget)

        self.status_label = QLabel("Initializing...")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.status_label.setStyleSheet("font-size: 18px; font-weight: bold;")

        self.progress_bar = QProgressBar()
        self.progress_bar.hide()

        self.metrics_label = QLabel("Waiting for data...")
        self.plotter = RealTimePlotter(max_points=600)

        self.layout.addWidget(self.status_label)
        self.layout.addWidget(self.progress_bar)
        self.layout.addWidget(self.metrics_label)
        self.layout.addWidget(self.plotter)

        self.retrain_layout = QHBoxLayout()

        self.retrain_combo = QComboBox()
        self.retrain_combo.addItems(
            ["5 Minutes", "10 Minutes", "30 Minutes", "60 Minutes"]
        )
        self.retrain_combo.setCurrentIndex(1)

        self.btn_retrain = QPushButton("Retrain Baseline")
        self.btn_retrain.clicked.connect(self.start_custom_retraining)

        self.retrain_layout.addWidget(QLabel("Custom Retrain:"))
        self.retrain_layout.addWidget(self.retrain_combo)
        self.retrain_layout.addWidget(self.btn_retrain)
        self.layout.addLayout(self.retrain_layout)

        self.button_layout = QHBoxLayout()

        self.btn_hide = QPushButton("Minimize to Background (Hide)")
        self.btn_hide.clicked.connect(self.hide_to_background)

        self.btn_quit = QPushButton("Stop Engine & Fully Quit")
        self.btn_quit.setStyleSheet(
            "background-color: #8b0000; color: white; font-weight: bold;"
        )
        self.btn_quit.clicked.connect(self.force_quit)

        self.button_layout.addWidget(self.btn_hide)
        self.button_layout.addWidget(self.btn_quit)
        self.layout.addLayout(self.button_layout)

        self.server = QLocalServer(self)
        self.server.removeServer("sentinel_ipc")
        self.server.listen("sentinel_ipc")
        self.server.newConnection.connect(self.handle_wake_up)

        self.worker = EngineWorker()
        self.worker.data_emitted.connect(self.update_ui)
        self.worker.start()

        self._is_force_quitting = False
        self.last_alarm_time = 0.0

        self.shortcut_a = QShortcut(QKeySequence(Qt.Key.Key_A), self)
        self.shortcut_a.activated.connect(self.plotter.plot_widget.enableAutoRange)

        self.shortcut_quit = QShortcut(QKeySequence("Ctrl+Q"), self)
        self.shortcut_quit.activated.connect(self.force_quit)

    def handle_wake_up(self):
        """Called when a new instance of Sentinel tries to start."""
        socket = self.server.nextPendingConnection()
        socket.waitForReadyRead()
        self.showNormal()
        self.raise_()
        self.activateWindow()
        socket.disconnectFromServer()

    def start_custom_retraining(self):
        """Translates the dropdown selection into seconds and triggers the engine."""
        text = self.retrain_combo.currentText()
        minutes = int(text.split()[0])
        seconds = minutes * 60

        self.worker.engine.trigger_retraining(seconds)

    @Slot(dict)
    def update_ui(self, state: Dict[str, Any]):
        """Runs on the Main UI Thread, triggered by the background worker.

        Args:
            state (Dict[str, Any]): A dictionary containing the UI update payload.
        """
        mode = state.get("mode")

        if mode == "training":
            self.progress_bar.show()
            self.plotter.hide()
            self.btn_retrain.setEnabled(False)
            self.progress_bar.setMaximum(state["target"])
            self.progress_bar.setValue(state["progress"])
            self.status_label.setText(
                f"Training Mode: Gathering Baseline ({state['progress']}/{state['target']}s)"
            )
            self.status_label.setStyleSheet(
                "font-size: 18px; font-weight: bold; color: white; background-color: #004080;"
            )

        elif mode == "monitoring":
            self.progress_bar.hide()
            self.plotter.show()

            status = state["status"]
            severity = state["severity"]
            risk = state["risk"]

            if risk > defaults.AUDIO_ALARM_THRESHOLD:
                current_time = time.time()
                if current_time - self.last_alarm_time > 1.0:
                    self._play_linux_alarm()
                    self.last_alarm_time = current_time

            self.status_label.setText(
                f"Status: {status} | Severity: {severity:.2f} | Risk: {risk:.2f}"
            )
            self.plotter.update_plot(severity, risk)

            metrics = state["metrics"]
            m_text = f"CPU: {metrics['cpu_percent']}% | RAM: {metrics['ram_percent']}% | CPU Temp: {metrics.get('cpu_temperature', 0.0)}°C"
            self.metrics_label.setText(m_text)

    def _play_linux_alarm(self):
        """Attempts to play a native Linux warning sound without blocking the UI."""
        try:
            subprocess.Popen(
                ["paplay", "/usr/share/sounds/freedesktop/stereo/dialog-warning.oga"],
                stderr=subprocess.DEVNULL,
                stdout=subprocess.DEVNULL,
            )
        except FileNotFoundError:
            try:
                subprocess.Popen(
                    ["aplay", "/usr/share/sounds/alsa/Front_Center.wav"],
                    stderr=subprocess.DEVNULL,
                    stdout=subprocess.DEVNULL,
                )
            except FileNotFoundError:
                pass

    def hide_to_background(self):
        """Hides the GUI but keeps the monitoring thread running."""
        self.hide()

    def closeEvent(self, event):
        """Intercept the OS 'X' button to hide instead of killing the engine.

        Args:
            event (QCloseEvent): The window close event.
        """
        if not self._is_force_quitting:
            event.ignore()
            self.hide_to_background()
        else:
            event.accept()

    def force_quit(self):
        """Properly shuts down the worker thread and terminates the app."""
        self._is_force_quitting = True
        self.worker.stop()
        QApplication.quit()


def run_application():
    """Initializes and runs the PyQt application."""
    app = QApplication(sys.argv)
    app.setApplicationName("Sentinel")
    app.setDesktopFileName("sentinel.desktop")

    app.setQuitOnLastWindowClosed(False)

    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    icon_path = os.path.join(base_dir, "assets", "icon.png")

    if os.path.exists(icon_path):
        app.setWindowIcon(QIcon(icon_path))
    else:
        print(f"Warning: Icon not found at {icon_path}")

    socket = QLocalSocket()
    socket.connectToServer("sentinel_ipc")
    if socket.waitForConnected(500):
        print("Sentinel daemon is already running. Waking it up...")
        socket.write(b"wake")
        socket.flush()
        socket.disconnectFromServer()
        sys.exit(0)

    window = SentinelMainWindow()
    window.show()

    sys.exit(app.exec())
