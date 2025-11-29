"""
Monitor Panel - Live monitoring of pipeline progress
"""
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QGroupBox,
                              QLabel, QProgressBar, QSplitter)
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

    def __init__(self, cache_store=None, parent=None):
        super().__init__(parent)

        self.cache_store = cache_store
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
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(5)

        # Compact Metrics Bar (single line, no group box)
        metrics_layout = QHBoxLayout()
        metrics_layout.setContentsMargins(0, 0, 0, 0)
        metrics_layout.setSpacing(10)

        self.total_label = QLabel("Total: 0")
        self.total_label.setStyleSheet("font-weight: bold; color: #e0e0e0; font-size: 11px;")
        metrics_layout.addWidget(self.total_label)

        self.queued_label = QLabel("⏳ Queue: 0")
        self.queued_label.setStyleSheet("color: #888; font-size: 11px;")
        metrics_layout.addWidget(self.queued_label)

        self.processing_label = QLabel("🔄 Processing: 0")
        self.processing_label.setStyleSheet("color: #0078d4; font-size: 11px;")
        metrics_layout.addWidget(self.processing_label)

        self.completed_label = QLabel("✅ Success: 0")
        self.completed_label.setStyleSheet("color: #0e7c0e; font-weight: bold; font-size: 11px;")
        metrics_layout.addWidget(self.completed_label)

        self.failed_label = QLabel("❌ Failed: 0")
        self.failed_label.setStyleSheet("color: #c50f1f; font-weight: bold; font-size: 11px;")
        metrics_layout.addWidget(self.failed_label)

        self.skipped_label = QLabel("⏭ Skipped: 0")
        self.skipped_label.setStyleSheet("color: #f7630c; font-weight: bold; font-size: 11px;")
        metrics_layout.addWidget(self.skipped_label)

        self.eta_label = QLabel("🕐 ETA: --")
        self.eta_label.setStyleSheet("font-weight: bold; color: #007acc; font-size: 11px;")
        metrics_layout.addWidget(self.eta_label)

        metrics_layout.addStretch()

        # API usage indicator
        self.api_calls_label = QLabel("API: 0/95000")
        self.api_calls_label.setStyleSheet("color: #666; font-size: 10px;")
        metrics_layout.addWidget(self.api_calls_label)

        layout.addLayout(metrics_layout)

        # Splitter for resizable queue and logs
        splitter = QSplitter()
        splitter.setOrientation(Qt.Orientation.Vertical)

        # Symbol Queue Group (minimal formatting)
        queue_group = QGroupBox("Processing Queue")
        queue_group.setStyleSheet("QGroupBox { font-weight: bold; font-size: 11px; }")
        queue_layout = QVBoxLayout()
        queue_layout.setContentsMargins(5, 5, 5, 5)
        queue_layout.setSpacing(3)

        self.queue_table = SymbolQueueTable()
        queue_layout.addWidget(self.queue_table)

        queue_group.setLayout(queue_layout)

        # Live Logs Group (minimal formatting)
        logs_group = QGroupBox("Live Logs")
        logs_group.setStyleSheet("QGroupBox { font-weight: bold; font-size: 11px; }")
        logs_layout = QVBoxLayout()
        logs_layout.setContentsMargins(5, 5, 5, 5)
        logs_layout.setSpacing(3)

        self.log_viewer = LogViewer()
        self.log_viewer.setStyleSheet("font-size: 10px;")
        logs_layout.addWidget(self.log_viewer)

        logs_group.setLayout(logs_layout)

        splitter.addWidget(queue_group)
        splitter.addWidget(logs_group)
        splitter.setStretchFactor(0, 4)  # Queue gets 4x space
        splitter.setStretchFactor(1, 1)  # Logs get 1x space

        layout.addWidget(splitter)

        self.setLayout(layout)

    @pyqtSlot(str, str, int, str, int, int, float, bool)
    def update_progress(self, symbol: str, status: str, progress: int, micro_stage: str, data_points: int, api_calls_used: int, duration_seconds: float, is_paused: bool, date_range: str = '-'):
        """
        Update symbol progress with extended metrics

        Args:
            symbol: Ticker symbol
            status: Status string
            progress: Progress percentage
            micro_stage: Current micro stage
            data_points: Number of data points
            api_calls_used: Number of API calls used
            duration_seconds: Duration in seconds
            is_paused: Whether symbol is paused
        """
        try:
            # Track if symbol is new (first update)
            is_new_symbol = symbol not in self.queue_table.symbol_data

            if is_new_symbol and status not in ['Complete', 'failed', 'skipped']:
                # First time seeing this symbol and it's processing
                if self.stats['queued'] > 0:
                    self.stats['queued'] -= 1
                self.stats['processing'] += 1

            # ALWAYS update pause state first (critical for context menu)
            # Initialize if not exists
            if symbol not in self.queue_table.symbol_paused:
                self.queue_table.symbol_paused[symbol] = False
            self.queue_table.symbol_paused[symbol] = is_paused

            self.queue_table.update_symbol(
                symbol,
                status,
                progress,
                micro_stage=micro_stage,
                data_points=data_points,
                date_range=date_range,
                api_calls=api_calls_used,
                duration=duration_seconds,
                is_paused=is_paused
            )

            self._update_stats_display()

        except Exception as e:
            # Silently handle errors to prevent crashes
            print(f"Error updating progress for {symbol}: {e}")

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
            date_range=date_range_str,
            micro_stage='Done'
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
        # Update API label
        daily_calls = stats.get('daily_calls', 0)
        self.api_calls_label.setText(f"API: {daily_calls}/95000")

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

    @pyqtSlot(dict)
    def on_metrics_updated(self, metrics: dict):
        """Update ETA and metrics display"""
        eta_string = metrics.get('eta_string', 'Calculating...')
        progress_pct = metrics.get('progress_percent', 0)
        throughput = metrics.get('throughput', 0)

        # Update ETA label
        self.eta_label.setText(f"⏱ ETA: {eta_string}")

        # Update total label with progress
        self.total_label.setText(f"Progress: {progress_pct}%")

        # Log ETA update occasionally (every 30 seconds to avoid spam)
        import time
        if not hasattr(self, '_last_log_time'):
            self._last_log_time = time.time()

        if time.time() - self._last_log_time >= 30:
            self.log_viewer.append_log(
                'INFO',
                f"ETA: {eta_string} | Progress: {progress_pct}% | Throughput: {throughput:.2f} sym/min"
            )
            self._last_log_time = time.time()

    @pyqtSlot(dict)
    def on_api_stats_updated(self, stats: dict):
        """Update API usage stats"""
        self.api_usage.update_stats(stats)

    def _update_stats_display(self):
        """Update statistics labels"""
        # Calculate queued as: total - processing - completed - failed - skipped
        queued = max(0, self.stats['total'] - self.stats['processing'] -
                    self.stats['completed'] - self.stats['failed'] - self.stats['skipped'])

        self.total_label.setText(f"Total: {self.stats['total']}")
        self.queued_label.setText(f"⏳ Queue: {queued}")
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
