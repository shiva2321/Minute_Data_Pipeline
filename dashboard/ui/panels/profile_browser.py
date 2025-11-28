"""
Profile Browser Panel - Database viewer and editor
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QTableWidget,
                              QTableWidgetItem, QLineEdit, QPushButton, QComboBox,
                              QLabel, QMessageBox, QHeaderView, QAbstractItemView,
                              QFileDialog)
from PyQt6.QtCore import pyqtSlot, Qt
from typing import List, Dict, Optional
import json

from dashboard.controllers.database_controller import DatabaseController
from dashboard.ui.widgets.profile_editor import ProfileEditor


class ProfileBrowser(QWidget):
    """
    Database browser for stored profiles
    """

    def __init__(self, parent=None):
        super().__init__(parent)

        self.db_controller = DatabaseController()
        self.all_profiles = []
        self.filtered_profiles = []

        self.init_ui()
        self._load_profiles()

    def init_ui(self):
        """Initialize UI components"""
        layout = QVBoxLayout()

        # Search and filter bar
        search_layout = QHBoxLayout()

        search_layout.addWidget(QLabel("Search:"))

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Enter symbol...")
        self.search_input.textChanged.connect(self._on_search_changed)
        search_layout.addWidget(self.search_input)

        search_btn = QPushButton("🔍 Search")
        search_btn.clicked.connect(self._search_profiles)
        search_layout.addWidget(search_btn)

        search_layout.addWidget(QLabel("Sort:"))

        self.sort_combo = QComboBox()
        self.sort_combo.addItems([
            'Last Updated (Newest)',
            'Last Updated (Oldest)',
            'Symbol (A-Z)',
            'Symbol (Z-A)',
            'Data Points (Most)',
            'Data Points (Least)'
        ])
        self.sort_combo.currentTextChanged.connect(self._on_sort_changed)
        search_layout.addWidget(self.sort_combo)

        layout.addLayout(search_layout)

        # Connection status
        self.status_label = QLabel("Connecting to database...")
        self.status_label.setStyleSheet("color: #ca5010;")
        layout.addWidget(self.status_label)

        # Profiles table
        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels([
            'Symbol', 'Exchange', 'Data Points', 'Date Range', 'Last Updated'
        ])

        # Table settings
        self.table.setAlternatingRowColors(True)
        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.table.setSortingEnabled(True)

        # Column sizing
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Fixed)
        header.resizeSection(0, 100)  # Symbol
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Fixed)
        header.resizeSection(1, 80)   # Exchange
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.Fixed)
        header.resizeSection(2, 120)  # Data Points
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.Stretch)  # Date Range
        header.setSectionResizeMode(4, QHeaderView.ResizeMode.Fixed)
        header.resizeSection(4, 180)  # Last Updated

        layout.addWidget(self.table)

        # Connect table double-click
        self.table.doubleClicked.connect(self._on_table_double_click)

        # Action buttons
        button_layout = QHBoxLayout()

        view_btn = QPushButton("👁 View")
        view_btn.clicked.connect(self._view_profile)
        button_layout.addWidget(view_btn)

        edit_btn = QPushButton("✏ Edit")
        edit_btn.clicked.connect(self._edit_profile)
        button_layout.addWidget(edit_btn)

        delete_btn = QPushButton("🗑 Delete")
        delete_btn.clicked.connect(self._delete_profile)
        button_layout.addWidget(delete_btn)

        export_btn = QPushButton("📤 Export")
        export_btn.clicked.connect(self._export_profile)
        button_layout.addWidget(export_btn)

        button_layout.addStretch()

        refresh_btn = QPushButton("🔄 Refresh")
        refresh_btn.clicked.connect(self._refresh_profiles)
        button_layout.addWidget(refresh_btn)

        layout.addLayout(button_layout)

        # Stats label
        self.stats_label = QLabel("Loaded 0 profiles")
        layout.addWidget(self.stats_label)

        self.setLayout(layout)

        # Connect database signals
        self.db_controller.signals.connection_status.connect(self._on_connection_status)
        self.db_controller.signals.profiles_loaded.connect(self._on_profiles_loaded)
        self.db_controller.signals.profile_deleted.connect(self._on_profile_deleted)
        self.db_controller.signals.database_error.connect(self._on_database_error)

    def _load_profiles(self):
        """Load all profiles from database"""
        self.all_profiles = self.db_controller.load_all_profiles()
        self.filtered_profiles = self.all_profiles.copy()
        self._populate_table()

    def _populate_table(self):
        """Populate table with profiles"""
        self.table.setRowCount(0)

        for profile in self.filtered_profiles:
            row = self.table.rowCount()
            self.table.insertRow(row)

            # Symbol
            symbol_item = QTableWidgetItem(profile.get('symbol', 'N/A'))
            symbol_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.table.setItem(row, 0, symbol_item)

            # Exchange
            exchange_item = QTableWidgetItem(profile.get('exchange', 'US'))
            exchange_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.table.setItem(row, 1, exchange_item)

            # Data Points
            data_points = profile.get('data_points_count', 0)
            data_points_item = QTableWidgetItem(f"{data_points:,}")
            data_points_item.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            self.table.setItem(row, 2, data_points_item)

            # Date Range
            date_range = profile.get('data_date_range', {})
            start = date_range.get('start', 'N/A')
            end = date_range.get('end', 'N/A')

            # Handle string vs datetime for start/end
            if isinstance(start, str):
                start = start[:10]
            elif hasattr(start, 'strftime'):
                start = start.strftime('%Y-%m-%d')

            if isinstance(end, str):
                end = end[:10]
            elif hasattr(end, 'strftime'):
                end = end.strftime('%Y-%m-%d')

            date_range_item = QTableWidgetItem(f"{start} to {end}")
            self.table.setItem(row, 3, date_range_item)

            # Last Updated
            last_updated = profile.get('last_updated', 'N/A')

            # Handle datetime object or string
            if isinstance(last_updated, str):
                last_updated_str = last_updated[:19]  # Truncate to datetime part
            elif hasattr(last_updated, 'strftime'):
                # It's a datetime object
                last_updated_str = last_updated.strftime('%Y-%m-%d %H:%M:%S')
            else:
                last_updated_str = str(last_updated)

            last_updated_item = QTableWidgetItem(last_updated_str)
            self.table.setItem(row, 4, last_updated_item)

        self.stats_label.setText(f"Loaded {len(self.filtered_profiles)} profiles")

    def _on_search_changed(self, text: str):
        """Handle search text change"""
        if not text:
            self.filtered_profiles = self.all_profiles.copy()
        else:
            text_upper = text.upper()
            self.filtered_profiles = [
                p for p in self.all_profiles
                if text_upper in p.get('symbol', '').upper()
            ]

        self._populate_table()

    def _search_profiles(self):
        """Execute search"""
        query = self.search_input.text().strip()

        if query:
            self.filtered_profiles = self.db_controller.search_profiles(query)
            self._populate_table()

    def _on_sort_changed(self, sort_option: str):
        """Handle sort change"""
        if 'Last Updated (Newest)' in sort_option:
            self.filtered_profiles.sort(key=lambda p: p.get('last_updated', ''), reverse=True)
        elif 'Last Updated (Oldest)' in sort_option:
            self.filtered_profiles.sort(key=lambda p: p.get('last_updated', ''))
        elif 'Symbol (A-Z)' in sort_option:
            self.filtered_profiles.sort(key=lambda p: p.get('symbol', ''))
        elif 'Symbol (Z-A)' in sort_option:
            self.filtered_profiles.sort(key=lambda p: p.get('symbol', ''), reverse=True)
        elif 'Data Points (Most)' in sort_option:
            self.filtered_profiles.sort(key=lambda p: p.get('data_points_count', 0), reverse=True)
        elif 'Data Points (Least)' in sort_option:
            self.filtered_profiles.sort(key=lambda p: p.get('data_points_count', 0))

        self._populate_table()

    def _get_selected_symbol(self) -> Optional[str]:
        """Get currently selected symbol"""
        current_row = self.table.currentRow()

        if current_row < 0:
            QMessageBox.warning(self, "No Selection", "Please select a profile")
            return None

        symbol_item = self.table.item(current_row, 0)
        return symbol_item.text() if symbol_item else None

    def _view_profile(self):
        """View selected profile"""
        symbol = self._get_selected_symbol()

        if symbol:
            try:
                profile = self.db_controller.get_profile(symbol)

                if profile:
                    # Show in editor (read-only mode could be added)
                    editor = ProfileEditor(symbol, profile, self)
                    editor.profile_updated.connect(self._on_profile_updated)
                    editor.exec()
                else:
                    QMessageBox.warning(
                        self,
                        "Profile Not Found",
                        f"Profile for {symbol} could not be loaded.\n\nIt may have been deleted or the database connection failed."
                    )
            except Exception as e:
                QMessageBox.critical(
                    self,
                    "Error Loading Profile",
                    f"Failed to load profile for {symbol}:\n\n{str(e)}\n\nTry refreshing the profiles list."
                )

    def _edit_profile(self):
        """Edit selected profile"""
        self._view_profile()  # Same as view for now

    def _delete_profile(self):
        """Delete selected profile"""
        symbol = self._get_selected_symbol()

        if symbol:
            try:
                reply = QMessageBox.question(
                    self,
                    "Confirm Delete",
                    f"Delete profile for {symbol}?\n\nThis action cannot be undone.",
                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
                )

                if reply == QMessageBox.StandardButton.Yes:
                    self.db_controller.delete_profile(symbol)
                    self._refresh_profiles()
            except Exception as e:
                QMessageBox.critical(
                    self,
                    "Error Deleting Profile",
                    f"Failed to delete profile for {symbol}:\n\n{str(e)}"
                )

    def _export_profile(self):
        """Export selected profile to JSON"""
        symbol = self._get_selected_symbol()

        if symbol:
            try:
                profile = self.db_controller.get_profile(symbol)

                if profile:
                    file_path, _ = QFileDialog.getSaveFileName(
                        self,
                        "Export Profile",
                        f"{symbol}_profile.json",
                        "JSON Files (*.json)"
                    )

                    if file_path:
                        try:
                            # Convert datetime objects to strings for JSON serialization
                            import json
                            from datetime import datetime

                            def json_serial(obj):
                                """JSON serializer for objects not serializable by default json code"""
                                if isinstance(obj, datetime):
                                    return obj.isoformat()
                                raise TypeError(f"Type {type(obj)} not serializable")

                            with open(file_path, 'w') as f:
                                json.dump(profile, f, indent=2, default=json_serial)

                            QMessageBox.information(
                                self,
                                "Success",
                                f"Profile exported to:\n{file_path}"
                            )
                        except Exception as e:
                            QMessageBox.critical(
                                self,
                                "Export Failed",
                                f"Failed to export profile:\n{str(e)}"
                            )
                else:
                    QMessageBox.warning(
                        self,
                        "Profile Not Found",
                        f"Profile for {symbol} could not be loaded."
                    )
            except Exception as e:
                QMessageBox.critical(
                    self,
                    "Error Loading Profile",
                    f"Failed to load profile for export:\n\n{str(e)}"
                )

    def _refresh_profiles(self):
        """Refresh profiles from database"""
        self.db_controller.invalidate_cache()
        self._load_profiles()

    @pyqtSlot(bool, str)
    def _on_connection_status(self, connected: bool, message: str):
        """Handle connection status update"""
        if connected:
            self.status_label.setText(f"✅ {message}")
            self.status_label.setStyleSheet("color: #0e7c0e;")
        else:
            self.status_label.setText(f"❌ {message}")
            self.status_label.setStyleSheet("color: #c50f1f;")

    @pyqtSlot(list)
    def _on_profiles_loaded(self, profiles: List[Dict]):
        """Handle profiles loaded"""
        self.all_profiles = profiles
        self.filtered_profiles = profiles.copy()
        self._populate_table()

    @pyqtSlot(str)
    def _on_profile_deleted(self, symbol: str):
        """Handle profile deleted"""
        QMessageBox.information(self, "Success", f"Profile for {symbol} deleted")
        self._refresh_profiles()

    @pyqtSlot(str)
    def _on_database_error(self, error: str):
        """Handle database error"""
        QMessageBox.critical(self, "Database Error", error)

    @pyqtSlot(str, dict)
    def _on_profile_updated(self, symbol: str, profile: Dict):
        """Handle profile updated"""
        self.db_controller.update_profile(symbol, profile)
        self._refresh_profiles()

    def _on_table_double_click(self, index):
        """Handle double-click on table row"""
        self._view_profile()
