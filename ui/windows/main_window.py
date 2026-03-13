from pathlib import Path

from PySide6.QtWidgets import (
    QLabel,
    QMainWindow,
    QStatusBar,
    QTabWidget,
    QVBoxLayout,
    QWidget,
)

from data.cache.cache_manager import CacheManager
from ui.panels.weekend_panel import WeekendPanel


class MainWindow(QMainWindow):
    def __init__(self, project_root: Path, cache_manager: CacheManager) -> None:
        super().__init__()

        self.project_root = project_root
        self.cache_manager = cache_manager

        self.setWindowTitle("F1 Race Engineering")
        self.resize(1400, 900)

        self._build_ui()
        self._build_status_bar()

    def _build_ui(self) -> None:
        central_widget = QWidget()
        main_layout = QVBoxLayout(central_widget)

        self.tabs = QTabWidget()
        
        self.weekend_tab = WeekendPanel(
            project_root=self.project_root,
            cache_manager=self.cache_manager,
        )
        self.strategy_tab = self._build_simple_tab(
            "Strategy analysis workspace"
            )
        self.ml_tab = self._build_simple_tab(
            "Machine learning workspace"
            )

        self.tabs.addTab(self.weekend_tab, "Weekend")
        self.tabs.addTab(self.strategy_tab, "Strategy")
        self.tabs.addTab(self.ml_tab, "ML Lab")

        main_layout.addWidget(self.tabs)
        self.setCentralWidget(central_widget)

    def _build_status_bar(self) -> None:
        status_bar = QStatusBar()
        status_bar.showMessage("Ready")
        self.setStatusBar(status_bar)

    def _build_simple_tab(self, text: str) -> QWidget:
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.addWidget(QLabel(text))
        return widget