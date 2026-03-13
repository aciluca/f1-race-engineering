from __future__ import annotations

import logging

import pandas as pd
import pyqtgraph as pg
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QVBoxLayout, QWidget


logger = logging.getLogger(__name__)


class TelemetryPlotWidget(QWidget):
    def __init__(self) -> None:
        super().__init__()

        self.plot_widget = pg.PlotWidget(title="Speed Trace")
        self.plot_widget.showGrid(x=True, y=True)
        self.plot_widget.setLabel("left", "Speed (km/h)")
        self.plot_widget.setLabel("bottom", "Distance (m)")

        layout = QVBoxLayout(self)
        layout.addWidget(self.plot_widget)

    def clear_plot(self) -> None:
        self.plot_widget.clear()

    def _prepare_trace(self, telemetry: pd.DataFrame) -> pd.DataFrame:
        if telemetry is None or telemetry.empty:
            return pd.DataFrame()

        required_columns = ["Distance", "Speed"]
        if not all(column in telemetry.columns for column in required_columns):
            logger.warning(
                "Telemetry missing required columns. Available columns: %s",
                list(telemetry.columns),
            )
            return pd.DataFrame()

        trace = telemetry[["Distance", "Speed"]].copy()
        trace["Distance"] = pd.to_numeric(trace["Distance"], errors="coerce")
        trace["Speed"] = pd.to_numeric(trace["Speed"], errors="coerce")
        trace = trace.dropna(subset=["Distance", "Speed"])

        logger.info("Prepared trace rows=%s", len(trace))
        return trace

    def plot_speed_comparison(
        self,
        telemetry_1: pd.DataFrame,
        driver_1: str,
        telemetry_2: pd.DataFrame | None = None,
        driver_2: str | None = None,
    ) -> None:
        self.plot_widget.clear()

        trace_1 = self._prepare_trace(telemetry_1)
        trace_2 = self._prepare_trace(telemetry_2) if telemetry_2 is not None else pd.DataFrame()

        logger.info("Trace 1 rows=%s for driver=%s", len(trace_1), driver_1)
        if driver_2:
            logger.info("Trace 2 rows=%s for driver=%s", len(trace_2), driver_2)

        if not trace_1.empty:
            self.plot_widget.plot(
                trace_1["Distance"].to_numpy(),
                trace_1["Speed"].to_numpy(),
                pen=pg.mkPen(width=2),
                name=driver_1,
            )

        if not trace_2.empty:
            self.plot_widget.plot(
                trace_2["Distance"].to_numpy(),
                trace_2["Speed"].to_numpy(),
                pen=pg.mkPen(width=2, style=Qt.PenStyle.DashLine),
                name=driver_2 or "Driver 2",
            )

        self.plot_widget.enableAutoRange()
