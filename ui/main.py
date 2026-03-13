import sys
from pathlib import Path

from PySide6.QtWidgets import QApplication

from ui.app import build_application
from ui.windows.main_window import MainWindow


def main() -> int:
    app = QApplication(sys.argv)
    
    project_root = Path(__file__).resolve().parents[1]
    cache_manager = build_application(project_root)
    
    window = MainWindow(project_root=project_root, cache_manager=cache_manager)
    window.show()
    
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())