"""
Monitor Panel - Live monitoring of pipeline progress
"""
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QGroupBox,
                              QLabel, QProgressBar)
from PyQt6.QtCore import pyqtSlot, Qt
from dashboard.ui.widgets.symbol_queue_table import SymbolQueueTable
from dashboard.ui.widgets.log_viewer import LogViewer
from dashboard.ui.widgets.api_usage_widget import APIUsageWidget
from typing import Dict
import time


class MonitorPanel(QWidget):
    """
    Live monitoring panel with queue table, logs, and statistics
    """

    def __init__(self, parent=None):
        super().__init__(parent)

        self.start_time = None
        self.stats = {
            'total': 0,
            'queued': 0,
            'processing': 0,
            'completed': 0,
            'failed': 0,
            'skipped': 0
        }

        self.init_ui()

    def init_ui(self):
        """Initialize UI components"""
        layout = QVBoxLayout()

        # Metrics Bar
        metrics_group = QGroupBox("Real-time Metrics")
        metrics_layout = QVBoxLayout()

        # Stats row
        stats_row = QHBoxLayout()

        self.total_label = QLabel("Total: 0")
        self.total_label.setStyleSheet("font-weight: bold; color: #e0e0e0;")
        stats_row.addWidget(self.total_label)

        stats_row.addWidget(QLabel("|"))

        self.queued_label = QLabel("⏳ Queue: 0")
        stats_row.addWidget(self.queued_label)

        stats_row.addWidget(QLabel("|"))

        self.processing_label = QLabel("🔄 Processing: 0")
        stats_row.addWidget(self.processing_label)

        stats_row.addWidget(QLabel("|"))

        self.completed_label = QLabel("✅ Success: 0")
        self.completed_label.setStyleSheet("color: #0e7c0e;")
        stats_row.addWidget(self.completed_label)

        stats_row.addWidget(QLabel("|"))

        self.failed_label = QLabel("❌ Failed: 0")
        self.failed_label.setStyleSheet("color: #c50f1f;")
        stats_row.addWidget(self.failed_label)

        stats_row.addWidget(QLabel("|"))

        self.skipped_label = QLabel("⏭ Skipped: 0")
        self.skipped_label.setStyleSheet("color: #f7630c;")
        stats_row.addWidget(self.skipped_label)

        stats_row.addWidget(QLabel("|"))

        self.eta_label = QLabel("⏱ ETA: --")
        self.eta_label.setStyleSheet("font-weight: bold; color: #007acc;")
        stats_row.addWidget(self.eta_label)

        stats_row.addStretch()

        metrics_layout.addLayout(stats_row)

        metrics_group.setLayout(metrics_layout)
        layout.addWidget(metrics_group)

        # API Usage Widget
        self.api_usage = APIUsageWidget()
        layout.addWidget(self.api_usage)

        # Symbol Queue Table
        queue_group = QGroupBox("Processing Queue")
        queue_layout = QVBoxLayout()

        self.queue_table = SymbolQueueTable()
        queue_layout.addWidget(self.queue_table)

        queue_group.setLayout(queue_layout)
        layout.addWidget(queue_group)

        # Live Logs
        logs_group = QGroupBox("Live Logs")
        logs_layout = QVBoxLayout()

        self.log_viewer = LogViewer()
        logs_layout.addWidget(self.log_viewer)

        logs_group.setLayout(logs_layout)
        layout.addWidget(logs_group)

        # Set proportions
        layout.setStretch(2, 2)  # Queue table
        layout.setStretch(3, 1)  # Log viewer

        self.setLayout(layout)

    @pyqtSlot(str, str, int)
    def update_progress(self, symbol: str, status: str, progress: int, **kwargs):
        """
        Update symbol progress

        Args:
            symbol: Ticker symbol
            status: Status string
            progress: Progress percentage
            **kwargs: Additional metadata
        """
        self.queue_table.update_symbol(symbol, status, progress, **kwargs)

    @pyqtSlot(str, dict)
    def mark_completed(self, symbol: str, profile: Dict):
        """
        Mark symbol as completed

        Args:
            symbol: Ticker symbol
            profile: Profile data
        """
        self.stats['completed'] += 1
        self.stats['processing'] = max(0, self.stats['processing'] - 1)

        # Update table
        data_points = profile.get('data_points_count', 0)
        date_range = profile.get('data_date_range', {})
        start = date_range.get('start', '')
        end = date_range.get('end', '')
        date_range_str = f"{start[:10]} to {end[:10]}" if start and end else "-"

        self.queue_table.update_symbol(
            symbol,
            'Complete',
            100,
            data_points=data_points,
            date_range=date_range_str
        )

        self._update_stats_display()

    @pyqtSlot(str, str)
    def mark_failed(self, symbol: str, error: str):
        """
        Mark symbol as failed

        Args:
            symbol: Ticker symbol
            error: Error message
        """
        self.stats['failed'] += 1
        self.stats['processing'] = max(0, self.stats['processing'] - 1)

        self.queue_table.update_symbol(
            symbol,
            'failed',
            0,
            date_range=f"Error: {error[:50]}"
        )

        self._update_stats_display()

    @pyqtSlot(str, str)
    def mark_skipped(self, symbol: str, reason: str):
        """
        Mark symbol as skipped

        Args:
            symbol: Ticker symbol
            reason: Reason for skipping
        """
        self.stats['skipped'] += 1
        self.stats['processing'] = max(0, self.stats['processing'] - 1)

        self.queue_table.update_symbol(
            symbol,
            'skipped',
            0,
            date_range=f"Skipped: {reason[:50]}"
        )

        self._update_stats_display()

    @pyqtSlot(dict)
    def update_api_stats(self, stats: Dict):
        """
        Update API usage statistics

        Args:
            stats: API stats dictionary
        """
        self.api_usage.update_stats(stats)

    @pyqtSlot(str, str)
    def append_log(self, level: str, message: str):
        """
        Append log message

        Args:
            level: Log level
            message: Log message
        """
        self.log_viewer.append_log(level, message)

    @pyqtSlot(int)
    def update_eta(self, seconds: int):
        """
        Update ETA display

        Args:
            seconds: Estimated seconds remaining
        """
        if seconds <= 0:
            self.eta_label.setText("⏱ ETA: --")
        elif seconds < 60:
            self.eta_label.setText(f"⏱ ETA: {seconds}s")
        elif seconds < 3600:
            minutes = seconds // 60
            secs = seconds % 60
            self.eta_label.setText(f"⏱ ETA: {minutes}m {secs}s")
        else:
            hours = seconds // 3600
            minutes = (seconds % 3600) // 60
            self.eta_label.setText(f"⏱ ETA: {hours}h {minutes}m")

    def pipeline_started(self, total_symbols: int):
        """
        Called when pipeline starts

        Args:
            total_symbols: Total number of symbols to process
        """
        self.start_time = time.time()
        self.stats = {
            'total': total_symbols,
            'queued': total_symbols,
            'processing': 0,
            'completed': 0,
            'failed': 0,
            'skipped': 0
        }

        # Clear previous data
        self.queue_table.clear()

        self._update_stats_display()
        self.append_log('INFO', f'Pipeline started with {total_symbols} symbols')

    def pipeline_completed(self, summary: Dict):
        """
        Called when pipeline completes

        Args:
            summary: Summary statistics
        """
        duration = summary.get('duration', 0)
        completed = summary.get('completed', 0)
        failed = summary.get('failed', 0)
        skipped = summary.get('skipped', 0)

        self.append_log(
            'SUCCESS',
            f'Pipeline completed in {duration:.1f}s: '
            f'{completed} succeeded, {failed} failed, {skipped} skipped'
        )

        self.eta_label.setText("⏱ ETA: Complete")

    def _update_stats_display(self):
        """Update statistics labels"""
        self.total_label.setText(f"Total: {self.stats['total']}")
        self.queued_label.setText(f"⏳ Queue: {self.stats['queued']}")
        self.processing_label.setText(f"🔄 Processing: {self.stats['processing']}")
        self.completed_label.setText(f"✅ Success: {self.stats['completed']}")
        self.failed_label.setText(f"❌ Failed: {self.stats['failed']}")
        self.skipped_label.setText(f"⏭ Skipped: {self.stats['skipped']}")

    def clear(self):
        """Clear all monitoring data"""
        self.queue_table.clear()
        self.log_viewer.clear()
        self.api_usage.reset()

        self.stats = {
            'total': 0,
            'queued': 0,
            'processing': 0,
            'completed': 0,
            'failed': 0,
            'skipped': 0
        }

        self._update_stats_display()
        self.eta_label.setText("⏱ ETA: --")

