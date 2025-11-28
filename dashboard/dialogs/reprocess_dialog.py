"""
Reprocess Dialog - Options for reprocessing profiles
"""
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QGroupBox,
    QRadioButton, QLabel, QPushButton, QMessageBox, QCheckBox, QSpinBox
)
from PyQt6.QtCore import pyqtSignal, pyqtSlot, Qt
from typing import Dict
import logging

logger = logging.getLogger(__name__)


class ReprocessDialog(QDialog):
    """Dialog for selecting reprocessing strategy"""

    # Signals
    reprocess_requested = pyqtSignal(dict)  # mode, settings

    def __init__(self, symbol: str, profile: Dict, parent=None):
        """
        Initialize reprocess dialog

        Args:
            symbol: Ticker symbol
            profile: Current profile data
            parent: Parent widget
        """
        super().__init__(parent)
        self.symbol = symbol
        self.profile = profile

        self.setWindowTitle(f"Reprocess {symbol}")
        self.setGeometry(200, 200, 600, 500)

        self.init_ui()

    def init_ui(self):
        """Initialize UI components"""
        layout = QVBoxLayout()

        # Profile info
        info_text = f"""
        <b>Symbol:</b> {self.symbol}<br>
        <b>Current Data Points:</b> {self.profile.get('data_points_count', 0):,}<br>
        <b>Date Range:</b> {self._format_date_range()}<br>
        <b>Last Updated:</b> {self._format_last_updated()}<br>
        """

        info_label = QLabel(info_text)
        layout.addWidget(info_label)

        layout.addSpacing(15)

        # Reprocess mode selection
        mode_group = QGroupBox("Reprocessing Mode")
        mode_layout = QVBoxLayout()

        # Option 1: Full Rebuild
        self.full_rebuild_radio = QRadioButton(
            "Full Historical Rebuild (from IPO date)"
        )
        self.full_rebuild_radio.setChecked(True)
        self.full_rebuild_radio.toggled.connect(self.on_mode_changed)
        mode_layout.addWidget(self.full_rebuild_radio)

        full_rebuild_detail = QLabel(
            "  • Delete current profile and data\n"
            "  • Fetch minute-by-minute data from company IPO date\n"
            "  • Re-engineer all features from scratch\n"
            "  ⚠️ This will take significantly longer (may take hours for older companies)"
        )
        full_rebuild_detail.setStyleSheet("color: #666; font-size: 10pt;")
        mode_layout.addWidget(full_rebuild_detail)

        mode_layout.addSpacing(10)

        # Option 2: Incremental Update
        self.incremental_radio = QRadioButton(
            "Incremental Update (add new data only)"
        )
        self.incremental_radio.toggled.connect(self.on_mode_changed)
        mode_layout.addWidget(self.incremental_radio)

        incremental_detail = QLabel(
            "  • Keep existing data points and features\n"
            "  • Fetch only new data since last update\n"
            "  • Merge new features with existing ones\n"
            "  ✓ Faster, preserves existing feature engineering"
        )
        incremental_detail.setStyleSheet("color: #666; font-size: 10pt;")
        mode_layout.addWidget(incremental_detail)

        mode_group.setLayout(mode_layout)
        layout.addWidget(mode_group)

        layout.addSpacing(15)

        # Options for each mode
        self.options_group = QGroupBox("Options")
        self.options_layout = QVBoxLayout()

        # History years (for full rebuild)
        history_layout = QHBoxLayout()
        history_layout.addWidget(QLabel("History Years:"))

        self.history_spin = QSpinBox()
        self.history_spin.setMinimum(1)
        self.history_spin.setMaximum(10)
        self.history_spin.setValue(5)
        self.history_spin.setSuffix(" years (1-10)")
        history_layout.addWidget(self.history_spin)

        history_layout.addStretch()
        self.options_layout.addLayout(history_layout)

        # Chunk size
        chunk_layout = QHBoxLayout()
        chunk_layout.addWidget(QLabel("Chunk Size:"))

        self.chunk_spin = QSpinBox()
        self.chunk_spin.setMinimum(1)
        self.chunk_spin.setMaximum(30)
        self.chunk_spin.setValue(30)
        self.chunk_spin.setSuffix(" days")
        chunk_layout.addWidget(self.chunk_spin)

        chunk_layout.addStretch()
        self.options_layout.addLayout(chunk_layout)

        # Backup option
        self.backup_check = QCheckBox("Create backup of current profile before reprocessing")
        self.backup_check.setChecked(True)
        self.options_layout.addWidget(self.backup_check)

        self.options_group.setLayout(self.options_layout)
        layout.addWidget(self.options_group)

        layout.addStretch()

        # Action buttons
        button_layout = QHBoxLayout()

        start_btn = QPushButton("▶ Start Reprocessing")
        start_btn.clicked.connect(self.on_start_clicked)
        button_layout.addWidget(start_btn)

        cancel_btn = QPushButton("✗ Cancel")
        cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(cancel_btn)

        layout.addLayout(button_layout)

        self.setLayout(layout)

    @pyqtSlot()
    def on_mode_changed(self):
        """Handle mode radio button changes"""
        self.update_options_visibility()

    def update_options_visibility(self):
        """Update option visibility based on selected mode"""
        if self.full_rebuild_radio.isChecked():
            self.history_spin.setEnabled(True)
            self.chunk_spin.setEnabled(True)
        else:
            self.history_spin.setEnabled(False)
            self.chunk_spin.setEnabled(False)

    def _format_date_range(self) -> str:
        """Format date range from profile"""
        date_range = self.profile.get('data_date_range', {})
        start = date_range.get('start', 'Unknown')[:10]
        end = date_range.get('end', 'Unknown')[:10]
        return f"{start} to {end}"

    def _format_last_updated(self) -> str:
        """Format last updated time"""
        last_updated = self.profile.get('last_updated', 'Never')
        if isinstance(last_updated, str):
            return last_updated[:19]
        return str(last_updated)

    @pyqtSlot()
    def on_start_clicked(self):
        """Start reprocessing"""
        mode = "full_rebuild" if self.full_rebuild_radio.isChecked() else "incremental"

        settings = {
            'mode': mode,
            'history_years': self.history_spin.value(),
            'chunk_days': self.chunk_spin.value(),
            'create_backup': self.backup_check.isChecked()
        }

        # Confirmation
        msg = f"""
        You are about to start a {'FULL REBUILD' if mode == 'full_rebuild' else 'INCREMENTAL UPDATE'} for {self.symbol}.

        Mode: {mode.replace('_', ' ').title()}
        History: {settings['history_years']} years
        Chunk Size: {settings['chunk_days']} days
        Backup: {'Yes' if settings['create_backup'] else 'No'}

        Continue?
        """

        reply = QMessageBox.question(
            self,
            "Confirm Reprocessing",
            msg,
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            self.reprocess_requested.emit(settings)
            self.accept()

