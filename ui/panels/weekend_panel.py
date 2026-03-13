from pathlib import Path

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


class WeekendPanel(QWidget):
    def __init__(self, project_root: Path, cache_manager: CacheManager) -> None:
        super().__init__()

        self.project_root = project_root
        self.cache_manager = cache_manager
        self.provider = FastF1Provider(project_root / "cache" / "raw" / "fastf1")

        self.current_schedule = None
        self.current_laps = None

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

        self.session_combo.addItems(["FP1", "FP2", "FP3", "Q", "S", "SQ", "R"])

        controls_layout.addRow("Season", self.season_combo)
        controls_layout.addRow("Grand Prix", self.gp_combo)
        controls_layout.addRow("Session", self.session_combo)

        button_row = QHBoxLayout()
        button_row.addWidget(self.load_button)
        controls_layout.addRow(button_row)

        controls_group.setLayout(controls_layout)

        info_group = QGroupBox("Session Info")
        info_layout = QVBoxLayout()
        self.info_label = QLabel("No session loaded.")
        self.info_label.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)
        self.info_label.setWordWrap(True)
        info_layout.addWidget(self.info_label)
        info_group.setLayout(info_layout)

        laps_group = QGroupBox("Laps")
        laps_layout = QVBoxLayout()
        self.laps_table = QTableWidget()
        self.laps_table.setColumnCount(0)
        self.laps_table.setRowCount(0)
        laps_layout.addWidget(self.laps_table)
        laps_group.setLayout(laps_layout)

        main_layout.addWidget(controls_group)
        main_layout.addWidget(info_group)
        main_layout.addWidget(laps_group)

        self.season_combo.currentIndexChanged.connect(self._on_season_changed)
        self.load_button.clicked.connect(self._on_load_session_clicked)

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

        except Exception as ex:
            self._show_error("Failed to load event schedule", str(ex))

    def _populate_gp_combo(self, schedule) -> None:
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

    def _on_load_session_clicked(self) -> None:
        season_text = self.season_combo.currentText()
        gp_name = self.gp_combo.currentText()
        session_name = self.session_combo.currentText()

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

        except Exception as ex:
            self._show_error("Failed to load session", str(ex))

    def _update_session_info(self, metadata: dict, laps) -> None:
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

    def _populate_laps_table(self, laps) -> None:
        self.laps_table.clear()

        if laps is None or laps.empty:
            self.laps_table.setRowCount(0)
            self.laps_table.setColumnCount(0)
            return

        preview = laps.head(50).copy()
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