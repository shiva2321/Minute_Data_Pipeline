"""
Main Window - Application entry point and coordination
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QTabWidget,
                              QStatusBar, QMessageBox)
from PyQt6.QtCore import pyqtSlot, Qt
from PyQt6.QtGui import QAction

from dashboard.ui.panels.control_panel import ControlPanel
from dashboard.ui.panels.monitor_panel import MonitorPanel
from dashboard.ui.panels.profile_browser import ProfileBrowser
from dashboard.ui.panels.settings_panel import SettingsPanel
from dashboard.controllers.pipeline_controller import PipelineController
from typing import List, Dict, Optional


class MainWindow(QMainWindow):
    """
    Main application window
    Coordinates all panels and controllers
    """

    def __init__(self):
        super().__init__()

        self.pipeline_controller: Optional[PipelineController] = None

        self.setWindowTitle("Stock Pipeline Control Dashboard")
        self.setGeometry(100, 100, 1400, 900)

        self.init_ui()
        self.create_menu_bar()
        self.create_status_bar()

    def init_ui(self):
        """Initialize UI components"""
        # Central widget with tabs
        central_widget = QWidget()
        layout = QVBoxLayout()

        self.tabs = QTabWidget()

        # Tab 1: Pipeline Control & Monitoring
        self.control_panel = ControlPanel()
        self.monitor_panel = MonitorPanel()

        main_tab = QWidget()
        main_layout = QVBoxLayout()
        main_layout.addWidget(self.control_panel)
        main_layout.addWidget(self.monitor_panel)
        main_tab.setLayout(main_layout)

        self.tabs.addTab(main_tab, "📊 Pipeline Control")

        # Tab 2: Profile Browser
        self.profile_browser = ProfileBrowser()
        self.tabs.addTab(self.profile_browser, "🗂 Database Profiles")

        # Tab 3: Settings
        self.settings_panel = SettingsPanel()
        self.tabs.addTab(self.settings_panel, "⚙ Settings")

        layout.addWidget(self.tabs)
        central_widget.setLayout(layout)
        self.setCentralWidget(central_widget)

        # Connect control panel signals
        self.control_panel.start_clicked.connect(self.start_pipeline)
        self.control_panel.pause_clicked.connect(self.pause_pipeline)
        self.control_panel.stop_clicked.connect(self.stop_pipeline)
        self.control_panel.clear_clicked.connect(self.clear_queue)

        # Connect settings panel signals
        self.settings_panel.settings_changed.connect(self._on_settings_changed)

    def create_menu_bar(self):
        """Create menu bar"""
        menubar = self.menuBar()

        # File menu
        file_menu = menubar.addMenu("&File")

        refresh_action = QAction("Refresh Profiles", self)
        refresh_action.triggered.connect(self._refresh_profiles)
        file_menu.addAction(refresh_action)

        file_menu.addSeparator()

        exit_action = QAction("Exit", self)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

        # Pipeline menu
        pipeline_menu = menubar.addMenu("&Pipeline")

        start_action = QAction("Start Pipeline", self)
        start_action.triggered.connect(lambda: self.control_panel._start_pipeline())
        pipeline_menu.addAction(start_action)

        stop_action = QAction("Stop Pipeline", self)
        stop_action.triggered.connect(self.stop_pipeline)
        pipeline_menu.addAction(stop_action)

        pipeline_menu.addSeparator()

        clear_action = QAction("Clear Queue", self)
        clear_action.triggered.connect(self.clear_queue)
        pipeline_menu.addAction(clear_action)

        # Help menu
        help_menu = menubar.addMenu("&Help")

        about_action = QAction("About", self)
        about_action.triggered.connect(self._show_about)
        help_menu.addAction(about_action)

        docs_action = QAction("Documentation", self)
        docs_action.triggered.connect(self._show_docs)
        help_menu.addAction(docs_action)

    def create_status_bar(self):
        """Create status bar"""
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("Ready")

    @pyqtSlot(list, dict)
    def start_pipeline(self, symbols: List[str], settings: Dict):
        """
        Start processing pipeline

        Args:
            symbols: List of ticker symbols
            settings: Processing settings
        """
        if self.pipeline_controller and self.pipeline_controller.isRunning():
            QMessageBox.warning(
                self,
                "Pipeline Running",
                "A pipeline is already running. Please stop it first."
            )
            return

        # Update status
        self.status_bar.showMessage(f"Starting pipeline for {len(symbols)} symbols...")
        self.monitor_panel.pipeline_started(len(symbols))

        # Create pipeline controller
        self.pipeline_controller = PipelineController(symbols, settings)

        # Connect signals
        self.pipeline_controller.signals.symbol_started.connect(
            lambda symbol: self.monitor_panel.append_log('INFO', f'Starting {symbol}')
        )

        self.pipeline_controller.signals.symbol_progress.connect(
            self.monitor_panel.update_progress
        )

        self.pipeline_controller.signals.symbol_completed.connect(
            self.monitor_panel.mark_completed
        )

        self.pipeline_controller.signals.symbol_failed.connect(
            self.monitor_panel.mark_failed
        )

        self.pipeline_controller.signals.symbol_skipped.connect(
            self.monitor_panel.mark_skipped
        )

        self.pipeline_controller.signals.api_stats_updated.connect(
            self.monitor_panel.update_api_stats
        )

        self.pipeline_controller.signals.eta_updated.connect(
            self.monitor_panel.update_eta
        )

        self.pipeline_controller.signals.log_message.connect(
            self.monitor_panel.append_log
        )

        self.pipeline_controller.signals.pipeline_completed.connect(
            self._on_pipeline_completed
        )

        self.pipeline_controller.signals.pipeline_stopped.connect(
            self._on_pipeline_stopped
        )

        # Start processing
        self.pipeline_controller.start()

        self.status_bar.showMessage(f"Pipeline running with {settings['max_workers']} workers...")

    @pyqtSlot()
    def pause_pipeline(self):
        """Pause pipeline processing"""
        if self.pipeline_controller and self.pipeline_controller.isRunning():
            self.pipeline_controller.pause()
            self.status_bar.showMessage("Pipeline paused")

    @pyqtSlot()
    def stop_pipeline(self):
        """Stop pipeline processing"""
        if self.pipeline_controller and self.pipeline_controller.isRunning():
            self.pipeline_controller.stop()
            self.status_bar.showMessage("Stopping pipeline...")

    @pyqtSlot()
    def clear_queue(self):
        """Clear monitoring queue"""
        self.monitor_panel.clear()
        self.status_bar.showMessage("Queue cleared")

    @pyqtSlot(dict)
    def _on_pipeline_completed(self, summary: Dict):
        """Handle pipeline completion"""
        self.monitor_panel.pipeline_completed(summary)
        self.control_panel.pipeline_finished()

        completed = summary.get('completed', 0)
        failed = summary.get('failed', 0)
        duration = summary.get('duration', 0)

        self.status_bar.showMessage(
            f"Pipeline completed: {completed} succeeded, {failed} failed ({duration:.1f}s)"
        )

        # Show notification
        QMessageBox.information(
            self,
            "Pipeline Complete",
            f"Processing finished!\n\n"
            f"Succeeded: {completed}\n"
            f"Failed: {failed}\n"
            f"Duration: {duration:.1f}s"
        )

        # Refresh profile browser
        self.profile_browser._refresh_profiles()

    @pyqtSlot()
    def _on_pipeline_stopped(self):
        """Handle pipeline stopped"""
        self.control_panel.pipeline_finished()
        self.status_bar.showMessage("Pipeline stopped by user")

    @pyqtSlot(dict)
    def _on_settings_changed(self, settings: Dict):
        """Handle settings change"""
        self.status_bar.showMessage("Settings updated", 3000)

    def _refresh_profiles(self):
        """Refresh profile browser"""
        self.profile_browser._refresh_profiles()
        self.status_bar.showMessage("Profiles refreshed", 2000)

    def _show_about(self):
        """Show about dialog"""
        QMessageBox.about(
            self,
            "About Stock Pipeline Dashboard",
            "<h3>Stock Pipeline Control Dashboard</h3>"
            "<p>Version 1.0.0</p>"
            "<p>A professional desktop application for controlling and monitoring "
            "stock market data pipelines.</p>"
            "<p><b>Features:</b></p>"
            "<ul>"
            "<li>Parallel processing with up to 12 workers</li>"
            "<li>Real-time monitoring and logging</li>"
            "<li>200+ technical indicators and features</li>"
            "<li>MongoDB storage and profile management</li>"
            "<li>API rate limiting and optimization</li>"
            "</ul>"
            "<p><b>Optimized for:</b> Ryzen 5 7600, RTX 3060, 32GB RAM</p>"
            "<p>© 2025 Minute Data Pipeline</p>"
        )

    def _show_docs(self):
        """Show documentation"""
        QMessageBox.information(
            self,
            "Documentation",
            "<h3>Quick Start Guide</h3>"
            "<p><b>1. Configure Settings:</b><br>"
            "Go to Settings tab and enter your EODHD API key and MongoDB URI.</p>"
            "<p><b>2. Add Symbols:</b><br>"
            "Enter ticker symbols (comma-separated) or load from a file.</p>"
            "<p><b>3. Choose Processing Mode:</b><br>"
            "- Incremental: Update existing profiles<br>"
            "- Full Rebuild: Fetch complete history</p>"
            "<p><b>4. Start Pipeline:</b><br>"
            "Click 'Start Pipeline' and monitor progress in real-time.</p>"
            "<p><b>5. View Results:</b><br>"
            "Browse and edit profiles in the Database Profiles tab.</p>"
            "<p>For more information, see README.md</p>"
        )

    def closeEvent(self, event):
        """Handle window close event"""
        if self.pipeline_controller and self.pipeline_controller.isRunning():
            reply = QMessageBox.question(
                self,
                "Confirm Exit",
                "Pipeline is still running. Stop and exit?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )

            if reply == QMessageBox.StandardButton.Yes:
                self.pipeline_controller.stop()
                event.accept()
            else:
                event.ignore()
        else:
            event.accept()

