"""
Entry point for Stock Pipeline Desktop Dashboard
Optimized for Ryzen 5 7600 (6 cores), RTX 3060, 32GB RAM
"""
import sys
import os
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QIcon
from dashboard.ui.main_window import MainWindow
from dashboard.utils.theme import load_stylesheet
import logging

# Suppress Qt warnings for cleaner output
os.environ["QT_LOGGING_RULES"] = "qt.qpa.window=false"

def main():
    """Application entry point"""
    # Enable high DPI scaling
    QApplication.setHighDpiScaleFactorRoundingPolicy(
        Qt.HighDpiScaleFactorRoundingPolicy.PassThrough
    )

    app = QApplication(sys.argv)

    # Set application metadata
    app.setApplicationName("Stock Pipeline Dashboard")
    app.setOrganizationName("MinuteDataPipeline")
    app.setApplicationVersion("1.0.0")

    # Apply dark theme
    app.setStyleSheet(load_stylesheet())

    # Create and show main window
    window = MainWindow()
    window.show()

    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    sys.exit(app.exec())


if __name__ == '__main__':
    main()

