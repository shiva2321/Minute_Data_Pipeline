"""
Cache Manager Widget - Shows cached symbols and date ranges
"""
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QGroupBox, QTableWidget,
                              QTableWidgetItem, QPushButton, QLabel, QProgressBar, QHeaderView, QSplitter,
                              QMenu)
from PyQt6.QtCore import Qt, pyqtSlot
from PyQt6.QtGui import QColor
from dashboard.services.data_fetch_cache import get_data_cache
from loguru import logger


class CacheManagerWidget(QWidget):
    """
    Widget to display and manage cache
    Shows which symbols are cached and their date ranges
    """

    def __init__(self, parent=None):
        super().__init__(parent)

        self.cache = get_data_cache()
        self.init_ui()
        self.refresh_cache_info()

    def init_ui(self):
        """Initialize UI components"""
        layout = QVBoxLayout()
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(5)

        # Title
        title = QLabel("📦 Cache Manager - Cached Data & Date Ranges")
        title.setStyleSheet("font-weight: bold; font-size: 12px; color: #00ccff;")
        layout.addWidget(title)

        # Create splitter for resizable areas
        splitter = QSplitter(Qt.Orientation.Vertical)

        # ===== TOP SECTION: Statistics =====
        stats_widget = QWidget()
        stats_layout = QVBoxLayout()
        stats_layout.setContentsMargins(0, 0, 0, 0)
        stats_layout.setSpacing(5)

        # Statistics row
        stats_line_layout = QHBoxLayout()

        self.entries_label = QLabel("Entries: 0")
        self.entries_label.setStyleSheet("color: #888; font-size: 10px;")
        stats_line_layout.addWidget(self.entries_label)

        self.size_label = QLabel("Size: 0 MB / 2048 MB")
        self.size_label.setStyleSheet("color: #888; font-size: 10px;")
        stats_line_layout.addWidget(self.size_label)

        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setMaximumHeight(15)
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                border: 1px solid #444;
                border-radius: 5px;
                background: #1a1a1a;
            }
            QProgressBar::chunk {
                background: #0066cc;
            }
        """)
        stats_line_layout.addWidget(self.progress_bar)

        stats_layout.addLayout(stats_line_layout)
        stats_widget.setLayout(stats_layout)
        stats_widget.setMaximumHeight(50)

        splitter.addWidget(stats_widget)

        # ===== BOTTOM SECTION: Table =====
        # Cache table
        self.cache_table = QTableWidget()
        self.cache_table.setColumnCount(4)
        self.cache_table.setHorizontalHeaderLabels([
            'Symbol', 'Date Range', 'Rows', 'Size (MB)'
        ])
        self.cache_table.setStyleSheet("""
            QTableWidget {
                background: #1a1a1a;
                gridline-color: #333;
                color: #e0e0e0;
            }
            QHeaderView::section {
                background: #0a0a0a;
                color: #00ccff;
                padding: 3px;
                border: none;
                font-size: 10px;
                font-weight: bold;
            }
            QTableWidget::item {
                padding: 3px;
            }
        """)

        # Configure columns
        header = self.cache_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)  # Symbol
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)  # Date Range
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)  # Rows
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)  # Size

        # Enable context menu for deletion
        self.cache_table.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.cache_table.customContextMenuRequested.connect(self._show_context_menu)

        splitter.addWidget(self.cache_table)

        # Set initial sizes: stats 20%, table 80%
        splitter.setSizes([100, 400])
        splitter.setCollapsible(0, False)  # Don't allow stats to collapse
        splitter.setCollapsible(1, False)  # Don't allow table to collapse

        layout.addWidget(splitter)

        # ...existing code...
        # Buttons
        button_layout = QHBoxLayout()

        self.refresh_btn = QPushButton("🔄 Refresh")
        self.refresh_btn.setMaximumWidth(100)
        self.refresh_btn.clicked.connect(self.refresh_cache_info)
        button_layout.addWidget(self.refresh_btn)

        self.clear_btn = QPushButton("🗑️ Clear Cache")
        self.clear_btn.setMaximumWidth(100)
        self.clear_btn.clicked.connect(self.clear_cache)
        button_layout.addWidget(self.clear_btn)

        button_layout.addStretch()

        layout.addLayout(button_layout)

        self.setLayout(layout)

    @pyqtSlot()
    def refresh_cache_info(self):
        """Refresh cache information display"""
        try:
            stats = self.cache.get_stats()

            # Update statistics
            entries = stats.get('entries', 0)
            total_size = stats.get('total_size_mb', 0)
            max_size = stats.get('max_size_mb', 2048)
            usage_percent = stats.get('usage_percent', 0)

            self.entries_label.setText(f"Entries: {entries}")
            self.size_label.setText(f"Size: {total_size:.1f} MB / {max_size:.0f} MB")
            self.progress_bar.setValue(int(usage_percent))

            # Update progress bar color
            if usage_percent > 80:
                self.progress_bar.setStyleSheet("""
                    QProgressBar::chunk { background: #ff3333; }
                """)
            elif usage_percent > 50:
                self.progress_bar.setStyleSheet("""
                    QProgressBar::chunk { background: #ffaa00; }
                """)
            else:
                self.progress_bar.setStyleSheet("""
                    QProgressBar::chunk { background: #0066cc; }
                """)

            # Populate cache table
            self.cache_table.setRowCount(0)

            # Group by symbol
            symbol_ranges = {}
            for key, info in self.cache.metadata.items():
                symbol = info.get('symbol', 'Unknown')
                if symbol not in symbol_ranges:
                    symbol_ranges[symbol] = []

                start = info.get('start_date', '?')
                end = info.get('end_date', '?')
                rows = info.get('rows', 0)
                size_bytes = info.get('size_bytes', 0)

                symbol_ranges[symbol].append({
                    'start': start,
                    'end': end,
                    'rows': rows,
                    'size_bytes': size_bytes
                })

            # Add rows for each symbol
            row = 0
            for symbol in sorted(symbol_ranges.keys()):
                ranges = symbol_ranges[symbol]

                # Sort ranges by start date
                ranges.sort(key=lambda x: x['start'])

                # Calculate total rows and size
                total_rows = sum(r['rows'] for r in ranges)
                total_size_bytes = sum(r['size_bytes'] for r in ranges)

                # Date range (first to last)
                first_date = ranges[0]['start']
                last_date = ranges[-1]['end']
                date_range = f"{first_date} → {last_date}"

                # Add row
                self.cache_table.insertRow(row)

                symbol_item = QTableWidgetItem(symbol)
                symbol_item.setForeground(QColor("#00ccff"))
                symbol_item.setFont(symbol_item.font())
                symbol_item.font().setBold(True)
                self.cache_table.setItem(row, 0, symbol_item)

                range_item = QTableWidgetItem(date_range)
                range_item.setForeground(QColor("#88ff88"))
                self.cache_table.setItem(row, 1, range_item)

                rows_item = QTableWidgetItem(f"{total_rows:,}")
                rows_item.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
                self.cache_table.setItem(row, 2, rows_item)

                size_item = QTableWidgetItem(f"{total_size_bytes / 1024 / 1024:.1f}")
                size_item.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
                self.cache_table.setItem(row, 3, size_item)

                row += 1

            logger.debug(f"Cache manager refreshed: {entries} entries, {total_size:.1f}MB used")

        except Exception as e:
            logger.error(f"Error refreshing cache info: {e}")

    @pyqtSlot()
    def clear_cache(self):
        """Clear all cache"""
        try:
            self.cache.clear_all()
            logger.info("Cache cleared by user")
            self.refresh_cache_info()
        except Exception as e:
            logger.error(f"Error clearing cache: {e}")

    @pyqtSlot('QPoint')
    def _show_context_menu(self, position):
        """Show context menu for cache table"""
        item = self.cache_table.itemAt(position)
        if not item:
            return

        row = item.row()
        symbol_item = self.cache_table.item(row, 0)
        if not symbol_item:
            return

        symbol = symbol_item.text()

        menu = QMenu()
        delete_action = menu.addAction(f"🗑️ Delete {symbol} cache")
        delete_action.triggered.connect(lambda: self._delete_symbol_cache(symbol))

        menu.exec(self.cache_table.mapToGlobal(position))

    @pyqtSlot(str)
    def _delete_symbol_cache(self, symbol: str):
        """Delete cache for specific symbol"""
        try:
            self.cache.clear_symbol(symbol)
            logger.info(f"Cleared cache for {symbol}")
            self.refresh_cache_info()
        except Exception as e:
            logger.error(f"Error clearing cache for {symbol}: {e}")

