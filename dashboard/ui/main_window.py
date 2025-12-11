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
from dashboard.ui.panels.visualization_panel import VisualizationPanel
from dashboard.ui.widgets.cache_manager_widget import CacheManagerWidget
from dashboard.controllers.pipeline_controller import PipelineController
from dashboard.services.email_alert import EmailAlerter
from typing import List, Dict, Optional


class MainWindow(QMainWindow):
    """
    Main application window
    Coordinates all panels and controllers
    """

    def __init__(self, cache_store=None):
        super().__init__()

        self.cache_store = cache_store
        self.pipeline_controller: Optional[PipelineController] = None

        self.setWindowTitle("Minute Data Pipeline Control Dashboard")
        self.setGeometry(100, 100, 1400, 900)

        self.init_ui()
        self.create_menu_bar()
        self.create_status_bar()

        # Initialize email alerter (after settings panel exists)
        self.email_alerter = EmailAlerter(self.settings_panel.get_email_settings())

    def init_ui(self):
        """Initialize UI components"""
        # Central widget with tabs
        central_widget = QWidget()
        layout = QVBoxLayout()

        self.tabs = QTabWidget()

        # Tab 1: Pipeline Control & Monitoring
        self.control_panel = ControlPanel(cache_store=self.cache_store)
        self.monitor_panel = MonitorPanel(cache_store=self.cache_store)

        main_tab = QWidget()
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)

        # Use QSplitter to allow resizing between control and monitor panels
        from PyQt6.QtWidgets import QSplitter
        from PyQt6.QtCore import Qt

        splitter = QSplitter(Qt.Orientation.Vertical)
        splitter.addWidget(self.control_panel)
        splitter.addWidget(self.monitor_panel)

        # Set initial sizes: control panel 30%, monitor panel 70%
        splitter.setSizes([300, 700])
        splitter.setCollapsible(0, False)  # Don't allow control panel to collapse
        splitter.setCollapsible(1, False)  # Don't allow monitor panel to collapse

        main_layout.addWidget(splitter)
        main_tab.setLayout(main_layout)

        self.tabs.addTab(main_tab, "📊 Pipeline Control")

        # Tab 2: Profile Browser
        self.profile_browser = ProfileBrowser()
        self.tabs.addTab(self.profile_browser, "🗂 Database Profiles")
        
        # Tab 3: Visualization (NEW)
        self.visualization_panel = VisualizationPanel()
        self.visualization_panel._refresh_symbols()  # Load symbols on startup
        self.tabs.addTab(self.visualization_panel, "📈 Data Visualization")

        # Tab 4: Settings
        self.settings_panel = SettingsPanel()
        self.tabs.addTab(self.settings_panel, "⚙ Settings")

        # Tab 5: Cache Manager
        self.cache_manager = CacheManagerWidget()
        self.tabs.addTab(self.cache_manager, "📦 Cache Manager")

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

        self.pipeline_controller.signals.metrics_updated.connect(
            self.monitor_panel.on_metrics_updated
        )

        self.pipeline_controller.signals.eta_updated.connect(
            self.monitor_panel.update_eta
        )

        self.pipeline_controller.signals.log_message.connect(
            self._on_log_message
        )

        self.pipeline_controller.signals.pipeline_completed.connect(
            self._on_pipeline_completed
        )

        self.pipeline_controller.signals.pipeline_stopped.connect(
            self._on_pipeline_stopped
        )

        self.pipeline_controller.signals.pipeline_cleared.connect(
            lambda: self.status_bar.showMessage('Pipeline cleared')
        )

        # Connect queue table signals for per-symbol control
        self.monitor_panel.queue_table.pause_symbol_requested.connect(self._on_pause_symbol)
        self.monitor_panel.queue_table.resume_symbol_requested.connect(self._on_resume_symbol)
        self.monitor_panel.queue_table.cancel_symbol_requested.connect(self._on_cancel_symbol)
        self.monitor_panel.queue_table.skip_symbol_requested.connect(self._on_skip_symbol)
        self.monitor_panel.queue_table.remove_requested.connect(self._on_remove_symbol)
        self.monitor_panel.queue_table.view_profile_requested.connect(self._on_view_profile)

        # Start processing
        self.pipeline_controller.start()

        self.status_bar.showMessage(f"Pipeline running with {settings['max_workers']} workers...")

    @pyqtSlot()
    def pause_pipeline(self):
        """Pause or resume pipeline processing"""
        if not (self.pipeline_controller and self.pipeline_controller.isRunning()):
            return
        if not self.pipeline_controller.is_paused:
            self.pipeline_controller.pause()
            # Update button label to Resume
            try:
                self.control_panel.pause_btn.setText("▶ Resume")
            except Exception:
                pass
            self.status_bar.showMessage("Pipeline paused")
        else:
            self.pipeline_controller.resume()
            try:
                self.control_panel.pause_btn.setText("⏸ Pause")
            except Exception:
                pass
            self.status_bar.showMessage("Pipeline resumed")

    @pyqtSlot()
    def stop_pipeline(self):
        """Stop pipeline processing"""
        if self.pipeline_controller and self.pipeline_controller.isRunning():
            self.pipeline_controller.stop()
            try:
                self.control_panel.pause_btn.setText("⏸ Pause")
            except Exception:
                pass
            self.status_bar.showMessage("Stopping pipeline...")

    @pyqtSlot()
    def clear_queue(self):
        """Clear monitoring queue and stop pipeline"""
        if self.pipeline_controller and self.pipeline_controller.isRunning():
            self.pipeline_controller.clear()
            self.pipeline_controller.wait()
        self.monitor_panel.clear()
        self.control_panel.reset()
        try:
            self.control_panel.pause_btn.setText("⏸ Pause")
        except Exception:
            pass
        self.status_bar.showMessage("Queue cleared and pipeline stopped")

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
        self.email_alerter.update_config(self.settings_panel.get_email_settings())

    @pyqtSlot(str, str)
    def _on_log_message(self, level: str, message: str):
        """Forward log to monitor and trigger email alerts if configured."""
        self.monitor_panel.append_log(level, message)
        if level in ('ERROR','CRITICAL'):
            self.email_alerter.send_alert(
                subject=f"Pipeline {level} Alert",
                message=message,
                window=self
            )

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

    # ==================== PER-SYMBOL CONTROL HANDLERS ====================

    @pyqtSlot(str)
    def _on_pause_symbol(self, symbol: str):
        """Pause a specific symbol's processing"""
        if self.pipeline_controller:
            self.pipeline_controller.pause_symbol(symbol)
            # IMMEDIATELY update UI pause state (don't wait for progress signal)
            self.monitor_panel.queue_table.set_symbol_paused(symbol, True)
            self.status_bar.showMessage(f"Paused {symbol}", 2000)

    @pyqtSlot(str)
    def _on_resume_symbol(self, symbol: str):
        """Resume a specific symbol's processing"""
        if self.pipeline_controller:
            self.pipeline_controller.resume_symbol(symbol)
            # IMMEDIATELY update UI pause state (don't wait for progress signal)
            self.monitor_panel.queue_table.set_symbol_paused(symbol, False)
            self.status_bar.showMessage(f"Resumed {symbol}", 2000)

    @pyqtSlot(str)
    def _on_cancel_symbol(self, symbol: str):
        """Cancel a specific symbol's processing"""
        reply = QMessageBox.question(
            self,
            "Confirm Cancel",
            f"Cancel processing for {symbol}?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if reply == QMessageBox.StandardButton.Yes:
            if self.pipeline_controller:
                self.pipeline_controller.cancel_symbol(symbol)
                self.status_bar.showMessage(f"Cancelled {symbol}", 2000)

    @pyqtSlot(str)
    def _on_skip_symbol(self, symbol: str):
        """Skip a specific symbol"""
        reply = QMessageBox.question(
            self,
            "Confirm Skip",
            f"Skip processing for {symbol}?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if reply == QMessageBox.StandardButton.Yes:
            if self.pipeline_controller:
                self.pipeline_controller.skip_symbol(symbol)
                self.status_bar.showMessage(f"Skipped {symbol}", 2000)

    @pyqtSlot(str)
    def _on_remove_symbol(self, symbol: str):
        """Remove a symbol from queue table"""
        self.monitor_panel.queue_table.remove_symbol(symbol)
        self.status_bar.showMessage(f"Removed {symbol} from queue", 2000)

    @pyqtSlot(str)
    def _on_view_profile(self, symbol: str):
        """View symbol profile"""
        # TODO: Open profile viewer dialog
        self.status_bar.showMessage(f"Viewing profile for {symbol}", 2000)
        print(f"View profile for {symbol}")
