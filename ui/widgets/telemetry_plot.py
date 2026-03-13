from __future__ import annotations

import logging

import numpy as np
import pandas as pd
import pyqtgraph as pg
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QLabel, QVBoxLayout, QWidget


logger = logging.getLogger(__name__)


class TelemetryPlotWidget(QWidget):
    def __init__(self) -> None:
        super().__init__()

        self.plot_widget = pg.PlotWidget(title="Speed Trace")
        self.plot_widget.showGrid(x=True, y=True)
        self.plot_widget.setLabel("left", "Speed (km/h)")
        self.plot_widget.setLabel("bottom", "Distance (m)")

        self.info_label = QLabel("Move the mouse over the plot to inspect telemetry.")
        self.info_label.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)

        layout = QVBoxLayout(self)
        layout.addWidget(self.plot_widget)
        layout.addWidget(self.info_label)

        self.trace_1 = pd.DataFrame()
        self.trace_2 = pd.DataFrame()
        self.driver_1_name = ""
        self.driver_2_name = ""

        self.v_line = pg.InfiniteLine(angle=90, movable=False)
        self.plot_widget.addItem(self.v_line, ignoreBounds=True)

        self.mouse_proxy = pg.SignalProxy(
            self.plot_widget.scene().sigMouseMoved,
            rateLimit=60,
            slot=self._on_mouse_moved,
        )

    def clear_plot(self) -> None:
        self.plot_widget.clear()
        self.plot_widget.addItem(self.v_line, ignoreBounds=True)

        self.trace_1 = pd.DataFrame()
        self.trace_2 = pd.DataFrame()
        self.driver_1_name = ""
        self.driver_2_name = ""
        self.info_label.setText("Move the mouse over the plot to inspect telemetry.")

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
        trace = trace.sort_values("Distance").reset_index(drop=True)

        logger.info("Prepared trace rows=%s", len(trace))
        return trace

    def plot_speed_comparison(
        self,
        telemetry_1: pd.DataFrame,
        driver_1: str,
        team_1_color: str,
        telemetry_2: pd.DataFrame | None = None,
        driver_2: str | None = None,
        team_2_color: str | None = None,
    ) -> None:
        self.plot_widget.clear()
        self.plot_widget.addItem(self.v_line, ignoreBounds=True)

        self.trace_1 = self._prepare_trace(telemetry_1)
        self.trace_2 = self._prepare_trace(telemetry_2) if telemetry_2 is not None else pd.DataFrame()

        self.driver_1_name = driver_1
        self.driver_2_name = driver_2 or ""

        logger.info("Trace 1 rows=%s for driver=%s", len(self.trace_1), driver_1)
        if driver_2:
            logger.info("Trace 2 rows=%s for driver=%s", len(self.trace_2), driver_2)

        if not self.trace_1.empty:
            self.plot_widget.plot(
                self.trace_1["Distance"].to_numpy(),
                self.trace_1["Speed"].to_numpy(),
                pen=pg.mkPen(team_1_color, width=2),
                name=driver_1,
            )

        if not self.trace_2.empty:
            self.plot_widget.plot(
                self.trace_2["Distance"].to_numpy(),
                self.trace_2["Speed"].to_numpy(),
                pen=pg.mkPen(team_2_color or "#FFFFFF", width=2, style=Qt.PenStyle.DashLine),
                name=driver_2 or "Driver 2",
            )

        self.plot_widget.enableAutoRange()

    def _find_nearest_point(self, trace: pd.DataFrame, x_value: float) -> tuple[float, float] | None:
        if trace.empty:
            return None

        distances = trace["Distance"].to_numpy()
        speeds = trace["Speed"].to_numpy()

        idx = int(np.abs(distances - x_value).argmin())
        return float(distances[idx]), float(speeds[idx])

    def _on_mouse_moved(self, event) -> None:
        if self.trace_1.empty and self.trace_2.empty:
            return

        pos = event[0]
        vb = self.plot_widget.getPlotItem().vb

        if not self.plot_widget.sceneBoundingRect().contains(pos):
            return

        mouse_point = vb.mapSceneToView(pos)
        x_value = float(mouse_point.x())

        self.v_line.setPos(x_value)

        point_1 = self._find_nearest_point(self.trace_1, x_value)
        point_2 = self._find_nearest_point(self.trace_2, x_value)

        if point_1 and point_2:
            distance = point_1[0]
            speed_1 = point_1[1]
            speed_2 = point_2[1]
            delta_speed = speed_1 - speed_2

            self.info_label.setText(
                f"Distance: {distance:.1f} m | "
                f"{self.driver_1_name}: {speed_1:.1f} km/h | "
                f"{self.driver_2_name}: {speed_2:.1f} km/h | "
                f"Delta: {delta_speed:+.1f} km/h"
            )

        elif point_1:
            distance = point_1[0]
            speed_1 = point_1[1]

            self.info_label.setText(
                f"Distance: {distance:.1f} m | "
                f"{self.driver_1_name}: {speed_1:.1f} km/h"
            )

        elif point_2:
            distance = point_2[0]
            speed_2 = point_2[1]

            self.info_label.setText(
                f"Distance: {distance:.1f} m | "
                f"{self.driver_2_name}: {speed_2:.1f} km/h"
            )