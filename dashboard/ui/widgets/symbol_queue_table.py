"""
Symbol queue table widget
Displays processing status for all symbols
"""
from PyQt6.QtWidgets import (QTableWidget, QTableWidgetItem, QMenu,
                              QWidget, QVBoxLayout, QHeaderView, QAbstractItemView)
from PyQt6.QtCore import Qt, pyqtSignal, pyqtSlot
from PyQt6.QtGui import QColor, QAction
from typing import Dict


class SymbolQueueTable(QWidget):
    """
    Table widget showing symbol processing queue and status
    """

    # Signals
    retry_requested = pyqtSignal(str)  # symbol
    remove_requested = pyqtSignal(str)  # symbol
    view_profile_requested = pyqtSignal(str)  # symbol
    export_requested = pyqtSignal(str)  # symbol

    def __init__(self, parent=None):
        super().__init__(parent)

        # Column definitions
        self.columns = ['Symbol', 'Status', 'Progress', 'Data Points', 'Date Range', 'API Calls', 'Duration']
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

        # Column sizing
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Fixed)
        header.resizeSection(0, 80)  # Symbol
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Fixed)
        header.resizeSection(1, 120)  # Status
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.Fixed)
        header.resizeSection(2, 80)  # Progress
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.Fixed)
        header.resizeSection(3, 100)  # Data Points
        header.setSectionResizeMode(4, QHeaderView.ResizeMode.Stretch)  # Date Range
        header.setSectionResizeMode(5, QHeaderView.ResizeMode.Fixed)
        header.resizeSection(5, 90)  # API Calls
        header.setSectionResizeMode(6, QHeaderView.ResizeMode.Fixed)
        header.resizeSection(6, 80)  # Duration

        # Context menu
        self.table.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.table.customContextMenuRequested.connect(self._show_context_menu)

        layout.addWidget(self.table)
        self.setLayout(layout)

    @pyqtSlot(str, str, int)
    def update_symbol(self, symbol: str, status: str, progress: int = 0, **kwargs):
        """
        Update or add symbol to table

        Args:
            symbol: Ticker symbol
            status: Status string
            progress: Progress percentage
            **kwargs: Additional data (data_points, date_range, api_calls, duration)
        """
        # Get or create row
        if symbol in self.symbol_rows:
            row = self.symbol_rows[symbol]
        else:
            row = self.table.rowCount()
            self.table.insertRow(row)
            self.symbol_rows[symbol] = row

            # Add symbol cell
            symbol_item = QTableWidgetItem(symbol)
            symbol_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.table.setItem(row, 0, symbol_item)

        # Status with icon
        status_text = self._format_status(status)
        status_item = QTableWidgetItem(status_text)
        status_item.setForeground(self.status_colors.get(status, QColor(220, 220, 220)))
        self.table.setItem(row, 1, status_item)

        # Progress
        progress_text = f"{progress}%" if progress > 0 else "-"
        progress_item = QTableWidgetItem(progress_text)
        progress_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
        self.table.setItem(row, 2, progress_item)

        # Data points
        data_points = kwargs.get('data_points', 0)
        data_points_text = f"{data_points:,}" if data_points > 0 else "-"
        data_points_item = QTableWidgetItem(data_points_text)
        data_points_item.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        self.table.setItem(row, 3, data_points_item)

        # Date range
        date_range = kwargs.get('date_range', '-')
        date_range_item = QTableWidgetItem(str(date_range))
        self.table.setItem(row, 4, date_range_item)

        # API calls
        api_calls = kwargs.get('api_calls', 0)
        api_calls_text = str(api_calls) if api_calls > 0 else "-"
        api_calls_item = QTableWidgetItem(api_calls_text)
        api_calls_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
        self.table.setItem(row, 5, api_calls_item)

        # Duration
        duration = kwargs.get('duration', 0)
        duration_text = self._format_duration(duration)
        duration_item = QTableWidgetItem(duration_text)
        duration_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
        self.table.setItem(row, 6, duration_item)

    def _format_status(self, status: str) -> str:
        """Format status with emoji icons"""
        icons = {
            'queued': '⏳',
            'processing': '🔄',
            'Fetching': '⬇️',
            'Engineering': '⚙️',
            'Storing': '💾',
            'success': '✅',
            'Complete': '✅',
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
        status_item = self.table.item(current_row, 1)
        status = status_item.text().split()[-1].lower() if status_item else ""

        # Add actions based on status
        view_action = QAction("View Profile", self)
        view_action.triggered.connect(lambda: self.view_profile_requested.emit(symbol))
        menu.addAction(view_action)

        if 'failed' in status:
            retry_action = QAction("Retry", self)
            retry_action.triggered.connect(lambda: self.retry_requested.emit(symbol))
            menu.addAction(retry_action)

        remove_action = QAction("Remove", self)
        remove_action.triggered.connect(lambda: self.remove_requested.emit(symbol))
        menu.addAction(remove_action)

        menu.addSeparator()

        export_action = QAction("Export JSON", self)
        export_action.triggered.connect(lambda: self.export_requested.emit(symbol))
        menu.addAction(export_action)

        menu.exec(self.table.viewport().mapToGlobal(position))

    def clear(self):
        """Clear all rows"""
        self.table.setRowCount(0)
        self.symbol_rows.clear()

    def remove_symbol(self, symbol: str):
        """Remove symbol from table"""
        if symbol in self.symbol_rows:
            row = self.symbol_rows[symbol]
            self.table.removeRow(row)

            # Update row indices
            del self.symbol_rows[symbol]
            for sym, r in list(self.symbol_rows.items()):
                if r > row:
                    self.symbol_rows[sym] = r - 1

