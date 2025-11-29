"""
Symbol queue table widget
Displays processing status for all symbols with micro-stage progress
"""
from PyQt6.QtWidgets import (QTableWidget, QTableWidgetItem, QMenu,
                              QWidget, QVBoxLayout, QHeaderView, QAbstractItemView)
from PyQt6.QtCore import Qt, pyqtSignal, pyqtSlot
from PyQt6.QtGui import QColor, QAction
from typing import Dict


class SymbolQueueTable(QWidget):
    """
    Table widget showing symbol processing queue and status with micro-stage details
    """

    # Signals
    retry_requested = pyqtSignal(str)  # symbol
    remove_requested = pyqtSignal(str)  # symbol
    view_profile_requested = pyqtSignal(str)  # symbol
    export_requested = pyqtSignal(str)  # symbol
    # Per-symbol control signals
    pause_symbol_requested = pyqtSignal(str)  # symbol
    resume_symbol_requested = pyqtSignal(str)  # symbol
    cancel_symbol_requested = pyqtSignal(str)  # symbol
    skip_symbol_requested = pyqtSignal(str)  # symbol

    def __init__(self, parent=None):
        super().__init__(parent)

        # Column definitions - includes Micro-Stage
        self.columns = ['Symbol', 'Status', 'Progress', 'Micro-Stage', 'Data Pts', 'Date Range', 'API Calls', 'Duration']
        self.status_colors = {
            'queued': QColor(150, 150, 150),       # Gray
            'processing': QColor(14, 99, 156),     # Blue
            'Fetching': QColor(14, 99, 156),       # Blue
            'Engineering': QColor(14, 99, 156),    # Blue
            'Storing': QColor(14, 99, 156),        # Blue
            'success': QColor(14, 124, 14),        # Green
            'Complete': QColor(14, 124, 14),       # Green
            'failed': QColor(197, 15, 31),         # Red
            'skipped': QColor(247, 99, 12)         # Orange
        }

        self.symbol_rows = {}  # symbol -> row_index
        self.symbol_data = {}  # symbol -> data dict
        self.symbol_statuses = {}  # symbol -> raw status string (for context menu)
        self.symbol_paused = {}  # symbol -> is_paused boolean

        self.init_ui()

    def init_ui(self):
        """Initialize UI components"""
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)

        # Create table
        self.table = QTableWidget()
        self.table.setColumnCount(len(self.columns))
        self.table.setHorizontalHeaderLabels(self.columns)

        # Table settings
        self.table.setAlternatingRowColors(True)
        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)

        # Column sizing - adjusted for new micro-stage column
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Fixed)
        header.resizeSection(0, 70)   # Symbol
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Fixed)
        header.resizeSection(1, 100)  # Status
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.Fixed)
        header.resizeSection(2, 70)   # Progress
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.Fixed)
        header.resizeSection(3, 200)  # Micro-Stage (fixed, not stretch)
        header.setSectionResizeMode(4, QHeaderView.ResizeMode.Fixed)
        header.resizeSection(4, 85)   # Data Points
        header.setSectionResizeMode(5, QHeaderView.ResizeMode.Fixed)
        header.resizeSection(5, 200)  # Date Range (wider for full display)
        header.setSectionResizeMode(6, QHeaderView.ResizeMode.Fixed)
        header.resizeSection(6, 75)   # API Calls
        header.setSectionResizeMode(7, QHeaderView.ResizeMode.Fixed)
        header.resizeSection(7, 85)   # Duration

        # Context menu
        self.table.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.table.customContextMenuRequested.connect(self._show_context_menu)

        layout.addWidget(self.table)
        self.setLayout(layout)

    @pyqtSlot(str, str, int)
    def update_symbol(self, symbol: str, status: str, progress: int = 0, **kwargs):
        """
        Update or add symbol to table with micro-stage details

        Args:
            symbol: Ticker symbol
            status: Status string
            progress: Progress percentage
            **kwargs: Additional data (data_points, date_range, api_calls, duration, micro_stage)
        """
        # Get or create row
        if symbol not in self.symbol_rows:
            # NEW SYMBOL - add to END of table
            row = self.table.rowCount()
            self.table.insertRow(row)
            self.symbol_rows[symbol] = row
            self.symbol_data[symbol] = {}  # Track symbol data

            # Add symbol cell
            symbol_item = QTableWidgetItem(symbol)
            symbol_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.table.setItem(row, 0, symbol_item)
        else:
            # EXISTING SYMBOL - update in place
            row = self.symbol_rows[symbol]

        # Store raw status for context menu
        self.symbol_statuses[symbol] = status.lower()

        # Store pause state for context menu
        self.symbol_paused[symbol] = kwargs.get('is_paused', False)

        # Format and display status
        # If paused, show pause indicator instead of status
        if kwargs.get('is_paused', False):
            status_text = "⏸ Paused"
            status_item = QTableWidgetItem(status_text)
            status_item.setForeground(QColor(255, 200, 0))  # Yellow for paused
        else:
            status_text = self._format_status(status)
            status_item = QTableWidgetItem(status_text)
            status_item.setForeground(self.status_colors.get(status, QColor(220, 220, 220)))

        self.table.setItem(row, 1, status_item)

        # Progress
        progress_text = f"{progress}%" if progress > 0 else "-"
        progress_item = QTableWidgetItem(progress_text)
        progress_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
        self.table.setItem(row, 2, progress_item)

        # Micro-stage (NEW COLUMN) - truncate if too long
        micro_stage = kwargs.get('micro_stage', '-')
        micro_stage_str = str(micro_stage)
        if len(micro_stage_str) > 40:
            micro_stage_str = micro_stage_str[:37] + '...'
        micro_stage_item = QTableWidgetItem(micro_stage_str)
        micro_stage_item.setTextAlignment(Qt.AlignmentFlag.AlignVCenter)
        self.table.setItem(row, 3, micro_stage_item)

        # Data points
        data_points = kwargs.get('data_points', 0)
        data_points_text = f"{data_points:,}" if data_points > 0 else "-"
        data_points_item = QTableWidgetItem(data_points_text)
        data_points_item.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        self.table.setItem(row, 4, data_points_item)

        # Date range - format compactly
        date_range = kwargs.get('date_range', '-')
        if date_range != '-' and '→' in str(date_range):
            # Parse and compact: "2023-11-29 00:00:00 → 2025-11-18 00:00:00" -> "Nov 29 → Nov 18"
            try:
                parts = str(date_range).split(' → ')
                if len(parts) == 2:
                    from datetime import datetime
                    start_str = parts[0].strip()
                    end_str = parts[1].strip()

                    # Try parsing with and without time component
                    start = None
                    end = None

                    # Try full format with time first
                    for fmt in ['%Y-%m-%d %H:%M:%S', '%Y-%m-%d']:
                        try:
                            start = datetime.strptime(start_str, fmt)
                            break
                        except ValueError:
                            continue

                    for fmt in ['%Y-%m-%d %H:%M:%S', '%Y-%m-%d']:
                        try:
                            end = datetime.strptime(end_str, fmt)
                            break
                        except ValueError:
                            continue

                    if start and end:
                        date_range = f"{start.strftime('%b %d')} → {end.strftime('%b %d')}"
            except Exception:
                pass  # Keep original format if parsing fails

        date_range_item = QTableWidgetItem(str(date_range))
        date_range_item.setTextAlignment(Qt.AlignmentFlag.AlignVCenter)
        self.table.setItem(row, 5, date_range_item)

        # API calls
        api_calls = kwargs.get('api_calls', 0)
        api_calls_text = str(api_calls) if api_calls > 0 else "-"
        api_calls_item = QTableWidgetItem(api_calls_text)
        api_calls_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
        self.table.setItem(row, 6, api_calls_item)

        # Duration
        duration = kwargs.get('duration', 0)
        if isinstance(duration, float):
            duration_seconds = duration
        else:
            try:
                duration_seconds = float(duration)
            except Exception:
                duration_seconds = 0.0
        duration_text = self._format_duration(duration_seconds)
        duration_item = QTableWidgetItem(duration_text)
        duration_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
        self.table.setItem(row, 7, duration_item)

        # Scroll to show newest items
        self.table.scrollToBottom()

    def _format_status(self, status: str) -> str:
        """Format status with emoji icons"""
        icons = {
            'queued': '⏳',
            'processing': '🔄',
            'Fetching': '⬇️',
            'Engineering': '⚙️',
            'Creating': '🧩',
            'Storing': '💾',
            'Complete': '✅',
            'success': '✅',
            'failed': '❌',
            'skipped': '⏭️'
        }
        icon = icons.get(status, '•')
        return f"{icon} {status.title()}"

    def _format_duration(self, seconds: float) -> str:
        """Format duration in human-readable format"""
        if seconds < 1:
            return "-"
        elif seconds < 60:
            return f"{seconds:.1f}s"
        else:
            minutes = int(seconds / 60)
            secs = int(seconds % 60)
            return f"{minutes}m {secs}s"

    def _show_context_menu(self, position):
        """Show context menu on right-click"""
        menu = QMenu()

        # Get selected symbol
        current_row = self.table.currentRow()
        if current_row < 0:
            return

        symbol_item = self.table.item(current_row, 0)
        if not symbol_item:
            return

        symbol = symbol_item.text()

        # Get raw status (not formatted with emojis)
        status = self.symbol_statuses.get(symbol, '').lower()

        # Get pause state - check BOTH the dictionary and kwargs stored during last update
        is_paused = self.symbol_paused.get(symbol, False)

        # Profile actions
        view_action = QAction("👁 View Profile", self)
        view_action.triggered.connect(lambda: self.view_profile_requested.emit(symbol))
        menu.addAction(view_action)

        # Per-symbol control actions
        menu.addSeparator()

        # Show pause option if running or processing (and not already paused)
        if (('running' in status or 'fetching' in status or 'engineering' in status or 'storing' in status)
            and not is_paused):
            pause_action = QAction("⏸ Pause This Symbol", self)
            pause_action.triggered.connect(lambda: self.pause_symbol_requested.emit(symbol))
            menu.addAction(pause_action)

        # Show resume option if paused (regardless of status)
        if is_paused:
            resume_action = QAction("▶ Resume This Symbol", self)
            resume_action.triggered.connect(lambda: self.resume_symbol_requested.emit(symbol))
            menu.addAction(resume_action)

        if 'queued' in status or 'running' in status or 'paused' in status:
            cancel_action = QAction("🛑 Cancel This Symbol", self)
            cancel_action.triggered.connect(lambda: self.cancel_symbol_requested.emit(symbol))
            menu.addAction(cancel_action)

            skip_action = QAction("⏭ Skip This Symbol", self)
            skip_action.triggered.connect(lambda: self.skip_symbol_requested.emit(symbol))
            menu.addAction(skip_action)

        if 'failed' in status:
            retry_action = QAction("🔄 Retry", self)
            retry_action.triggered.connect(lambda: self.retry_requested.emit(symbol))
            menu.addAction(retry_action)

        # Separator before remove
        menu.addSeparator()

        remove_action = QAction("🗑 Remove", self)
        remove_action.triggered.connect(lambda: self.remove_requested.emit(symbol))
        menu.addAction(remove_action)

        export_action = QAction("📤 Export JSON", self)
        export_action.triggered.connect(lambda: self.export_requested.emit(symbol))
        menu.addAction(export_action)

        menu.exec(self.table.viewport().mapToGlobal(position))

    def clear(self):
        """Clear all rows"""
        self.table.setRowCount(0)
        self.symbol_rows.clear()
        self.symbol_data.clear()
        self.symbol_statuses.clear()
        self.symbol_paused.clear()

    def remove_symbol(self, symbol: str):
        """Remove symbol from table"""
        if symbol in self.symbol_rows:
            row = self.symbol_rows[symbol]
            self.table.removeRow(row)

            # Update row indices
            del self.symbol_rows[symbol]
            if symbol in self.symbol_data:
                del self.symbol_data[symbol]
            if symbol in self.symbol_statuses:
                del self.symbol_statuses[symbol]
            if symbol in self.symbol_paused:
                del self.symbol_paused[symbol]
            for sym, r in list(self.symbol_rows.items()):
                if r > row:
                    self.symbol_rows[sym] = r - 1

    def set_symbol_paused(self, symbol: str, is_paused: bool):
        """
        Explicitly set the paused state for a symbol
        Used by controller to update pause state
        """
        if symbol in self.symbol_paused:
            self.symbol_paused[symbol] = is_paused
        else:
            self.symbol_paused[symbol] = is_paused

        # Update the visual status in the table
        if symbol in self.symbol_rows:
            row = self.symbol_rows[symbol]
            status_col = 1

            if is_paused:
                # Show paused indicator
                status_item = QTableWidgetItem("⏸ Paused")
                status_item.setForeground(QColor(255, 200, 0))  # Yellow
            else:
                # Show current status (get from status dict and reformat)
                current_status = self.symbol_statuses.get(symbol, 'unknown')
                status_item = QTableWidgetItem(self._format_status(current_status))
                status_item.setForeground(self.status_colors.get(current_status, QColor(220, 220, 220)))

            self.table.setItem(row, status_col, status_item)
