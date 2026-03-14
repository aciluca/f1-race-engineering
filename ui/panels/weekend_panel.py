from pathlib import Path

import pandas as pd
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QComboBox,
    QFormLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QMessageBox,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from data.cache.cache_manager import CacheManager
from data.providers.fastf1_provider import FastF1Provider
from ui.widgets.telemetry_plot import TelemetryPlotWidget
from ui.resources import get_team_color


class WeekendPanel(QWidget):
    def __init__(self, project_root: Path, cache_manager: CacheManager) -> None:
        super().__init__()

        self.project_root = project_root
        self.cache_manager = cache_manager
        self.provider = FastF1Provider(project_root / "cache" / "raw" / "fastf1")

        self.current_schedule = None
        self.current_laps = None
        self.session_name_map = {}

        self._build_ui()
        self._populate_seasons()

    def _build_ui(self) -> None:
        main_layout = QVBoxLayout(self)

        controls_group = QGroupBox("Session Selection")
        controls_layout = QFormLayout()

        self.season_combo = QComboBox()
        self.gp_combo = QComboBox()
        self.session_combo = QComboBox()
        self.load_button = QPushButton("Load Session")

        controls_layout.addRow("Season", self.season_combo)
        controls_layout.addRow("Grand Prix", self.gp_combo)
        controls_layout.addRow("Session", self.session_combo)

        button_row = QHBoxLayout()
        button_row.addWidget(self.load_button)
        controls_layout.addRow(button_row)

        controls_group.setLayout(controls_layout)

        drivers_group = QGroupBox("Driver Comparison")
        drivers_layout = QFormLayout()

        self.driver_1_combo = QComboBox()
        self.lap_1_combo = QComboBox()

        self.driver_2_combo = QComboBox()
        self.lap_2_combo = QComboBox()

        self.load_telemetry_button = QPushButton("Load Telemetry")

        drivers_layout.addRow("Driver 1", self.driver_1_combo)
        drivers_layout.addRow("Lap 1", self.lap_1_combo)
        drivers_layout.addRow("Driver 2", self.driver_2_combo)
        drivers_layout.addRow("Lap 2", self.lap_2_combo)

        driver_button_row = QHBoxLayout()
        driver_button_row.addWidget(self.load_telemetry_button)
        drivers_layout.addRow(driver_button_row)

        drivers_group.setLayout(drivers_layout)

        info_group = QGroupBox("Session Info")
        info_layout = QVBoxLayout()
        self.info_label = QLabel("No session loaded.")
        self.info_label.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)
        self.info_label.setWordWrap(True)
        info_layout.addWidget(self.info_label)
        info_group.setLayout(info_layout)

        telemetry_group = QGroupBox("Telemetry")
        telemetry_layout = QVBoxLayout()
        self.telemetry_plot = TelemetryPlotWidget()
        telemetry_layout.addWidget(self.telemetry_plot)
        telemetry_group.setLayout(telemetry_layout)

        laps_group = QGroupBox("Laps")
        laps_layout = QVBoxLayout()
        self.laps_table = QTableWidget()
        self.laps_table.setColumnCount(0)
        self.laps_table.setRowCount(0)
        laps_layout.addWidget(self.laps_table)
        laps_group.setLayout(laps_layout)

        main_layout.addWidget(controls_group)
        main_layout.addWidget(drivers_group)
        main_layout.addWidget(info_group)
        main_layout.addWidget(telemetry_group)
        main_layout.addWidget(laps_group)

        self.season_combo.currentIndexChanged.connect(self._on_season_changed)
        self.gp_combo.currentIndexChanged.connect(self._on_grand_prix_changed)
        self.load_button.clicked.connect(self._on_load_session_clicked)
        self.load_telemetry_button.clicked.connect(self._on_load_telemetry_clicked)
        self.driver_1_combo.currentIndexChanged.connect(self._on_driver_1_changed)
        self.driver_2_combo.currentIndexChanged.connect(self._on_driver_2_changed)

    def _populate_seasons(self) -> None:
        seasons = [str(year) for year in range(2018, 2026)]
        self.season_combo.addItems(seasons)
        self.season_combo.setCurrentText("2024")

    def _on_season_changed(self) -> None:
        season_text = self.season_combo.currentText()
        if not season_text:
            return

        season = int(season_text)

        try:
            schedule = self.provider.get_event_schedule(season)
            self.current_schedule = schedule
            self._populate_gp_combo(schedule)
            self._populate_session_combo_for_selected_gp()

        except Exception as ex:
            self._show_error("Failed to load event schedule", str(ex))

    def _on_grand_prix_changed(self) -> None:
        self._populate_session_combo_for_selected_gp()

    def _populate_gp_combo(self, schedule: pd.DataFrame) -> None:
        self.gp_combo.clear()

        if schedule is None or schedule.empty:
            return

        possible_columns = ["EventName", "OfficialEventName", "Country", "Location"]
        event_column = None

        for column in possible_columns:
            if column in schedule.columns:
                event_column = column
                break

        if event_column is None:
            return

        values = schedule[event_column].dropna().astype(str).unique().tolist()
        self.gp_combo.addItems(values)

    def _populate_session_combo_for_selected_gp(self) -> None:
        self.session_combo.clear()
        self.session_name_map = {}

        event_row = self._get_selected_event_row()
        if event_row is None:
            return

        for column_name in ["Session1", "Session2", "Session3", "Session4", "Session5"]:
            if column_name not in event_row.index:
                continue

            session_full_name = event_row[column_name]

            if pd.isna(session_full_name):
                continue

            session_full_name = str(session_full_name).strip()

            if not session_full_name or session_full_name.lower() in {"none", "nan"}:
                continue

            session_label = self._map_session_name_to_label(session_full_name)

            if session_label is None:
                continue

            self.session_combo.addItem(session_label)
            self.session_name_map[session_label] = session_full_name

    def _get_selected_event_row(self) -> pd.Series | None:
        if self.current_schedule is None or self.current_schedule.empty:
            return None

        gp_name = self.gp_combo.currentText()
        if not gp_name:
            return None

        possible_columns = ["EventName", "OfficialEventName", "Country", "Location"]

        for column in possible_columns:
            if column not in self.current_schedule.columns:
                continue

            matched_rows = self.current_schedule[self.current_schedule[column].astype(str) == gp_name]
            if not matched_rows.empty:
                return matched_rows.iloc[0]

        return None

    def _map_session_name_to_label(self, session_name: str) -> str | None:
        normalized = session_name.strip().lower()

        mapping = {
            "practice 1": "FP1",
            "practice 2": "FP2",
            "practice 3": "FP3",
            "qualifying": "Q",
            "race": "R",
            "sprint": "S",
            "sprint qualifying": "SQ",
            "sprint shootout": "SS",
            "shootout": "SS",
        }

        return mapping.get(normalized, session_name)

    def _get_selected_session_value(self) -> str:
        session_label = self.session_combo.currentText()
        if not session_label:
            return ""

        return self.session_name_map.get(session_label, session_label)

    def _on_load_session_clicked(self) -> None:
        season_text = self.season_combo.currentText()
        gp_name = self.gp_combo.currentText()
        session_name = self._get_selected_session_value()

        if not season_text or not gp_name or not session_name:
            self._show_error("Missing selection", "Please select season, Grand Prix and session.")
            return

        season = int(season_text)

        try:
            metadata = self.provider.get_session_metadata(season, gp_name, session_name)
            laps = self.provider.get_laps(season, gp_name, session_name)

            self.current_laps = laps

            self._update_session_info(metadata, laps)
            self._populate_laps_table(laps)
            self._populate_driver_combos(laps)
            self._on_driver_1_changed()
            self._on_driver_2_changed()
            self.telemetry_plot.clear_plot()

        except Exception as ex:
            self._show_error("Failed to load session", str(ex))

    def _populate_driver_combos(self, laps: pd.DataFrame) -> None:
        self.driver_1_combo.clear()
        self.driver_2_combo.clear()

        if laps is None or laps.empty or "Driver" not in laps.columns:
            return

        drivers = sorted(laps["Driver"].dropna().astype(str).unique().tolist())

        self.driver_1_combo.addItems(drivers)
        self.driver_2_combo.addItems(drivers)

        if len(drivers) >= 1:
            self.driver_1_combo.setCurrentIndex(0)

        if len(drivers) >= 2:
            self.driver_2_combo.setCurrentIndex(1)

    def _on_driver_1_changed(self) -> None:
        self._populate_lap_combo_for_driver(self.driver_1_combo, self.lap_1_combo)

    def _on_driver_2_changed(self) -> None:
        self._populate_lap_combo_for_driver(self.driver_2_combo, self.lap_2_combo)

    def _populate_lap_combo_for_driver(self, driver_combo: QComboBox, lap_combo: QComboBox) -> None:
        lap_combo.clear()

        if self.current_laps is None or self.current_laps.empty:
            return

        driver_code = driver_combo.currentText()
        if not driver_code:
            return

        if "Driver" not in self.current_laps.columns or "LapNumber" not in self.current_laps.columns:
            return

        driver_laps = self.current_laps[self.current_laps["Driver"] == driver_code].copy()

        if driver_laps.empty:
            return

        if "LapTime" in driver_laps.columns:
            driver_laps = driver_laps.dropna(subset=["LapTime"])

        if driver_laps.empty:
            return

        lap_numbers = (
            driver_laps["LapNumber"]
            .dropna()
            .astype(int)
            .sort_values()
            .unique()
            .tolist()
        )

        lap_combo.addItem("Fastest Lap")

        for lap_number in lap_numbers:
            lap_combo.addItem(str(lap_number))

    def _get_selected_lap_number(self, lap_combo: QComboBox) -> int | None:
        lap_text = lap_combo.currentText()

        if not lap_text or lap_text == "Fastest Lap":
            return None

        try:
            return int(lap_text)
        except ValueError:
            return None

    def _on_load_telemetry_clicked(self) -> None:
        if self.current_laps is None or self.current_laps.empty:
            self._show_error("No session loaded", "Load a session before loading telemetry.")
            return

        season_text = self.season_combo.currentText()
        gp_name = self.gp_combo.currentText()
        session_name = self._get_selected_session_value()
        driver_1 = self.driver_1_combo.currentText()
        driver_2 = self.driver_2_combo.currentText()

        if not season_text or not gp_name or not session_name or not driver_1:
            self._show_error("Missing selection", "Please select session and at least one driver.")
            return

        season = int(season_text)

        lap_number_1 = self._get_selected_lap_number(self.lap_1_combo)
        lap_number_2 = self._get_selected_lap_number(self.lap_2_combo)

        try:
            telemetry_1 = self.provider.get_telemetry(
                season=season,
                grand_prix=gp_name,
                session_name=session_name,
                driver_code=driver_1,
                lap_number=lap_number_1,
            )

            telemetry_2 = None
            if driver_2 and driver_2 != driver_1:
                telemetry_2 = self.provider.get_telemetry(
                    season=season,
                    grand_prix=gp_name,
                    session_name=session_name,
                    driver_code=driver_2,
                    lap_number=lap_number_2,
                )

            team_1 = self._get_driver_team(driver_1)
            team_1_color = get_team_color(team_1)

            team_2 = self._get_driver_team(driver_2) if driver_2 else None
            team_2_color = get_team_color(team_2) if team_2 else "#FFFFFF"

            self.telemetry_plot.plot_speed_comparison(
                telemetry_1=telemetry_1,
                driver_1=driver_1 if lap_number_1 is None else f"{driver_1} L{lap_number_1}",
                team_1_color=team_1_color,
                telemetry_2=telemetry_2,
                driver_2=(driver_2 if lap_number_2 is None else f"{driver_2} L{lap_number_2}") if driver_2 else None,
                team_2_color=team_2_color,
            )

        except Exception as ex:
            self._show_error("Failed to load telemetry", str(ex))

    def _get_driver_team(self, driver_code: str) -> str | None:
        if self.current_laps is None or self.current_laps.empty:
            return None

        if "Driver" not in self.current_laps.columns or "Team" not in self.current_laps.columns:
            return None

        driver_rows = self.current_laps[self.current_laps["Driver"] == driver_code]

        if driver_rows.empty:
            return None

        team_values = driver_rows["Team"].dropna()
        if team_values.empty:
            return None

        return str(team_values.iloc[0])

    def _update_session_info(self, metadata: dict, laps: pd.DataFrame) -> None:
        if not metadata:
            self.info_label.setText("No metadata available.")
            return

        lines = [
            f"Event: {metadata.get('event_name', 'N/A')}",
            f"Session: {metadata.get('session_name', 'N/A')}",
            f"Date: {metadata.get('date', 'N/A')}",
            f"Laps rows: {len(laps) if laps is not None else 0}",
        ]
        self.info_label.setText("\n".join(lines))

    def _populate_laps_table(self, laps: pd.DataFrame) -> None:
        self.laps_table.clear()

        if laps is None or laps.empty:
            self.laps_table.setRowCount(0)
            self.laps_table.setColumnCount(0)
            return

        preferred_columns = [
            "Driver",
            "LapNumber",
            "LapTime",
            "Sector1Time",
            "Sector2Time",
            "Sector3Time",
            "Compound",
            "TyreLife",
            "IsPersonalBest",
        ]

        visible_columns = [col for col in preferred_columns if col in laps.columns]
        preview = laps[visible_columns].head(50).copy() if visible_columns else laps.head(50).copy()
        preview = preview.fillna("")

        self.laps_table.setRowCount(len(preview))
        self.laps_table.setColumnCount(len(preview.columns))
        self.laps_table.setHorizontalHeaderLabels([str(col) for col in preview.columns])

        for row_index in range(len(preview)):
            for col_index, column_name in enumerate(preview.columns):
                value = str(preview.iloc[row_index][column_name])
                self.laps_table.setItem(row_index, col_index, QTableWidgetItem(value))

        self.laps_table.resizeColumnsToContents()

    def _show_error(self, title: str, message: str) -> None:
        QMessageBox.critical(self, title, message)