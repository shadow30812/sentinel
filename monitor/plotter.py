import numpy as np
import pyqtgraph as pg
from PySide6.QtWidgets import QVBoxLayout, QWidget


class RealTimePlotter(QWidget):
    def __init__(self, max_points: int = 600):
        super().__init__()
        self.max_points = max_points

        # UI Setup
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)

        self.plot_widget = pg.PlotWidget(title="System Severity & Risk")
        self.plot_widget.setBackground("w")
        self.plot_widget.showGrid(x=True, y=True)
        self.plot_widget.setYRange(0, 25)  # Cap initial view, but pyqtgraph auto-scales

        self.layout.addWidget(self.plot_widget)

        # Data Buffers
        self.time_data = np.arange(-max_points, 0, dtype=float)
        self.severity_data = np.zeros(max_points, dtype=float)
        self.risk_data = np.zeros(max_points, dtype=float)

        # Curves
        self.severity_curve = self.plot_widget.plot(
            self.time_data,
            self.severity_data,
            pen=pg.mkPen("b", width=2),
            name="Severity (S)",
        )
        self.risk_curve = self.plot_widget.plot(
            self.time_data, self.risk_data, pen=pg.mkPen("r", width=2), name="Risk"
        )

    def update_plot(self, severity: float, risk: float):
        """Rolls the buffers and updates the pyqtgraph curves."""
        # Roll data arrays
        self.severity_data[:-1] = self.severity_data[1:]
        self.severity_data[-1] = severity

        self.risk_data[:-1] = self.risk_data[1:]
        self.risk_data[-1] = risk

        # Update curves
        self.severity_curve.setData(self.time_data, self.severity_data)
        self.risk_curve.setData(self.time_data, self.risk_data)
