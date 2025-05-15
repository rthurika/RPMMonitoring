"""
Remote Patient Monitoring Application
Main entry point
"""
import sys

from PySide6.QtWidgets import QApplication

from ui.main_window import RPMApp


def main():
    """Initialize and run the application"""
    app = QApplication(sys.argv)
    app.setStyle("Fusion")

    window = RPMApp()
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
