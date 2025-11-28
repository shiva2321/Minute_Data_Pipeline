"""
Profile Editor Dialog
Multi-tab editor with JSON validation and syntax highlighting
"""
from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QTabWidget,
                              QPushButton, QTextEdit, QLabel, QGridLayout,
                              QWidget, QMessageBox, QScrollArea, QGroupBox,
                              QFileDialog)
from PyQt6.QtCore import pyqtSignal, Qt
from PyQt6.QtGui import QFont
import json
from typing import Dict, Optional
from pygments import highlight
from pygments.lexers import JsonLexer
from pygments.formatters import HtmlFormatter


class ProfileEditor(QDialog):
    """
    Multi-tab profile editor with JSON validation
    """

    profile_updated = pyqtSignal(str, dict)  # symbol, updated_profile
    reprocess_requested = pyqtSignal(str)  # symbol

    def __init__(self, symbol: str, profile: Dict, parent=None):
        super().__init__(parent)

        self.symbol = symbol
        self.original_profile = profile.copy()
        self.current_profile = profile.copy()

        self.setWindowTitle(f"Profile Editor: {symbol}")
        self.setMinimumSize(900, 700)

        # Remap legacy or missing keys to available sections
        self._feature_key_map = {
            'price_features': ['statistical_features','performance_metrics'],
            'volume_features': ['microstructure_features'],
            'volatility_features': ['risk_metrics','performance_metrics']
        }

        self.init_ui()

    def init_ui(self):
        """Initialize UI components"""
        layout = QVBoxLayout()

        # Tab widget
        self.tabs = QTabWidget()

        # Overview tab
        self.tabs.addTab(self._create_overview_tab(), "Overview")

        # Features tabs
        self.tabs.addTab(self._create_features_tab('price_features', 'Price Features'), "Price")
        self.tabs.addTab(self._create_features_tab('volume_features', 'Volume Features'), "Volume")
        self.tabs.addTab(self._create_features_tab('volatility_features', 'Volatility Features'), "Volatility")
        self.tabs.addTab(self._create_features_tab('technical_indicators', 'Technical Indicators'), "Indicators")
        self.tabs.addTab(self._create_features_tab('regime_features', 'Regime Features'), "Regimes")
        self.tabs.addTab(self._create_features_tab('predictive_labels', 'Predictive Labels'), "Predictions")

        # Raw JSON tab
        self.tabs.addTab(self._create_json_tab(), "Raw JSON")

        layout.addWidget(self.tabs)

        # Action buttons
        button_layout = QHBoxLayout()

        self.save_btn = QPushButton("💾 Save Changes")
        self.save_btn.clicked.connect(self._save_changes)

        self.reprocess_btn = QPushButton("🔄 Re-process")
        self.reprocess_btn.clicked.connect(self._reprocess)

        self.export_btn = QPushButton("📤 Export JSON")
        self.export_btn.clicked.connect(self._export_json)

        cancel_btn = QPushButton("❌ Cancel")
        cancel_btn.clicked.connect(self.reject)

        button_layout.addWidget(self.save_btn)
        button_layout.addWidget(self.reprocess_btn)
        button_layout.addWidget(self.export_btn)
        button_layout.addStretch()
        button_layout.addWidget(cancel_btn)

        layout.addLayout(button_layout)
        self.setLayout(layout)

    def _create_overview_tab(self) -> QWidget:
        """Create overview tab with summary info"""
        widget = QWidget()
        layout = QVBoxLayout()

        # Scroll area for content
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)

        content = QWidget()
        content_layout = QGridLayout()

        row = 0

        # Basic info
        content_layout.addWidget(QLabel("<b>Symbol:</b>"), row, 0)
        content_layout.addWidget(QLabel(self.current_profile.get('symbol', 'N/A')), row, 1)
        row += 1

        content_layout.addWidget(QLabel("<b>Exchange:</b>"), row, 0)
        content_layout.addWidget(QLabel(self.current_profile.get('exchange', 'US')), row, 1)
        row += 1

        content_layout.addWidget(QLabel("<b>Data Points:</b>"), row, 0)
        content_layout.addWidget(QLabel(f"{self.current_profile.get('data_points_count', 0):,}"), row, 1)
        row += 1

        # Date range
        date_range = self.current_profile.get('data_date_range', {})
        start = date_range.get('start', 'N/A')
        end = date_range.get('end', 'N/A')
        content_layout.addWidget(QLabel("<b>Date Range:</b>"), row, 0)
        content_layout.addWidget(QLabel(f"{start} to {end}"), row, 1)
        row += 1

        # Last updated - handle datetime object
        last_updated = self.current_profile.get('last_updated', 'N/A')
        from datetime import datetime
        if isinstance(last_updated, datetime):
            last_updated_str = last_updated.strftime('%Y-%m-%d %H:%M:%S')
        else:
            last_updated_str = str(last_updated)

        content_layout.addWidget(QLabel("<b>Last Updated:</b>"), row, 0)
        content_layout.addWidget(QLabel(last_updated_str), row, 1)
        row += 1

        # Backfill metadata
        backfill = self.current_profile.get('backfill_metadata', {})
        if backfill:
            content_layout.addWidget(QLabel("<b>History Complete:</b>"), row, 0)
            content_layout.addWidget(QLabel(str(backfill.get('history_complete', 'N/A'))), row, 1)
            row += 1

            content_layout.addWidget(QLabel("<b>API Calls Used:</b>"), row, 0)
            content_layout.addWidget(QLabel(str(backfill.get('api_calls_used', 'N/A'))), row, 1)
            row += 1

            content_layout.addWidget(QLabel("<b>Fetch Duration:</b>"), row, 0)
            duration = backfill.get('fetch_duration_seconds', 0)
            content_layout.addWidget(QLabel(f"{duration:.1f} seconds"), row, 1)
            row += 1

        content_layout.setRowStretch(row, 1)
        content.setLayout(content_layout)

        scroll.setWidget(content)
        layout.addWidget(scroll)

        widget.setLayout(layout)
        return widget

    def _create_features_tab(self, feature_key: str, title: str) -> QWidget:
        """Create tab for specific feature group"""
        widget = QWidget()
        layout = QVBoxLayout()

        # Scroll area
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)

        content = QWidget()
        content_layout = QGridLayout()

        # Get features
        raw_features = self.current_profile.get(feature_key, {})
        if not raw_features and feature_key in self._feature_key_map:
            merged = {}
            for alt_key in self._feature_key_map[feature_key]:
                merged.update(self.current_profile.get(alt_key, {}) or {})
            features = merged
        else:
            features = raw_features

        if features:
            row = 0
            for key, value in sorted(features.items()):
                # Feature name
                label = QLabel(f"<b>{key.replace('_', ' ').title()}:</b>")
                content_layout.addWidget(label, row, 0)

                # Feature value (formatted)
                from datetime import datetime

                if isinstance(value, datetime):
                    value_str = value.strftime('%Y-%m-%d %H:%M:%S')
                elif isinstance(value, float):
                    value_str = f"{value:.6f}"
                elif isinstance(value, dict):
                    # Handle dicts with potential datetime values
                    try:
                        def json_serial(obj):
                            if isinstance(obj, datetime):
                                return obj.isoformat()
                            raise TypeError
                        value_str = json.dumps(value, indent=2, default=json_serial)
                    except:
                        value_str = str(value)
                else:
                    value_str = str(value)

                value_label = QLabel(value_str)
                value_label.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
                content_layout.addWidget(value_label, row, 1)

                row += 1

            content_layout.setRowStretch(row, 1)
        else:
            content_layout.addWidget(QLabel(f"No {title.lower()} available"), 0, 0)

        content.setLayout(content_layout)
        scroll.setWidget(content)

        layout.addWidget(scroll)
        widget.setLayout(layout)
        return widget

    def _create_json_tab(self) -> QWidget:
        """Create raw JSON editor tab"""
        widget = QWidget()
        layout = QVBoxLayout()

        # Info label
        info_label = QLabel("⚠️ Advanced: Edit raw JSON (be careful with formatting)")
        info_label.setStyleSheet("color: #ca5010; font-weight: bold;")
        layout.addWidget(info_label)

        # JSON editor
        self.json_editor = QTextEdit()
        self.json_editor.setFont(QFont('Consolas', 10))

        # Serialize with datetime handling
        from datetime import datetime

        def json_serial(obj):
            """JSON serializer for objects not serializable by default"""
            if isinstance(obj, datetime):
                return obj.isoformat()
            raise TypeError(f"Type {type(obj)} not serializable")

        try:
            json_str = json.dumps(self.current_profile, indent=2, default=json_serial)
            self.json_editor.setPlainText(json_str)
        except Exception as e:
            self.json_editor.setPlainText(f"Error serializing profile: {str(e)}")

        layout.addWidget(self.json_editor)

        # Validate button
        validate_btn = QPushButton("✓ Validate JSON")
        validate_btn.clicked.connect(self._validate_json)
        layout.addWidget(validate_btn)

        widget.setLayout(layout)
        return widget

    def _validate_json(self):
        """Validate JSON syntax"""
        try:
            json.loads(self.json_editor.toPlainText())
            QMessageBox.information(self, "Valid JSON", "JSON syntax is valid!")
        except json.JSONDecodeError as e:
            QMessageBox.critical(self, "Invalid JSON", f"JSON syntax error:\n{str(e)}")

    def _save_changes(self):
        """Validate and save changes"""
        try:
            # Parse JSON from editor
            updated_profile = json.loads(self.json_editor.toPlainText())

            # Validate required fields
            if 'symbol' not in updated_profile:
                raise ValueError("Profile must have 'symbol' field")

            # Emit update signal
            self.profile_updated.emit(self.symbol, updated_profile)

            QMessageBox.information(self, "Success", f"Profile for {self.symbol} updated successfully!")
            self.accept()

        except json.JSONDecodeError as e:
            QMessageBox.critical(self, "Invalid JSON", f"JSON syntax error:\n{str(e)}")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to save profile:\n{str(e)}")

    def _reprocess(self):
        """Request re-processing of symbol"""
        reply = QMessageBox.question(
            self,
            "Confirm Re-process",
            f"Re-process {self.symbol}?\n\nThis will fetch new data and recalculate all features.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            self.reprocess_requested.emit(self.symbol)
            self.accept()

    def _export_json(self):
        """Export profile to JSON file"""
        try:
            # Get save path
            file_path, _ = QFileDialog.getSaveFileName(
                self,
                "Export Profile",
                f"{self.symbol}_profile.json",
                "JSON Files (*.json)"
            )

            if file_path:
                # Parse current JSON
                profile = json.loads(self.json_editor.toPlainText())

                # Write to file
                with open(file_path, 'w') as f:
                    json.dump(profile, f, indent=2)

                QMessageBox.information(self, "Success", f"Profile exported to:\n{file_path}")

        except Exception as e:
            QMessageBox.critical(self, "Export Failed", f"Failed to export profile:\n{str(e)}")
