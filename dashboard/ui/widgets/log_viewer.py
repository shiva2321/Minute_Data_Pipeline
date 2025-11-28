"""
Live log viewer with color-coded messages, auto-scroll, and categorization
"""
from PyQt6.QtWidgets import (QTextEdit, QWidget, QVBoxLayout, QHBoxLayout,
                              QComboBox, QCheckBox, QLabel, QPushButton, QMessageBox)
from PyQt6.QtGui import QTextCharFormat, QColor, QFont, QTextCursor
from PyQt6.QtCore import pyqtSlot, Qt
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class LogViewer(QWidget):
    """
    Color-coded log viewer with filtering, auto-scroll, and categorization
    Supports categorizing logs by component (mongodb, pipeline, fetcher, etc.)
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.max_lines = 2000
        self.auto_scroll = True
        self.current_filter = "All"
        self.font_size = 11  # Increased from 9

        # Log storage by category
        self.logs_by_category = {}

        self.init_ui()

    def init_ui(self):
        """Initialize UI components"""
        layout = QVBoxLayout()
        layout.setContentsMargins(5, 5, 5, 5)

        # Text edit for logs - resizable and with larger font
        self.text_edit = QTextEdit()
        self.text_edit.setReadOnly(True)
        self.text_edit.setFont(QFont('Consolas', self.font_size))
        self.text_edit.setLineWrapMode(QTextEdit.LineWrapMode.NoWrap)
        self.text_edit.setMinimumHeight(200)  # Resizable minimum

        # Color formats
        self.formats = {
            'DEBUG': self._create_format(QColor(150, 150, 150)),
            'INFO': self._create_format(QColor(220, 220, 220)),
            'WARNING': self._create_format(QColor(255, 200, 0)),
            'ERROR': self._create_format(QColor(255, 100, 100)),
            'CRITICAL': self._create_format(QColor(255, 0, 0)),
            'SUCCESS': self._create_format(QColor(100, 255, 100))
        }

        layout.addWidget(self.text_edit, 1)

        # Control bar - enhanced with font size and clear button
        control_layout = QHBoxLayout()

        control_layout.addWidget(QLabel("Filter:"))

        self.filter_combo = QComboBox()
        self.filter_combo.addItems([
            'All', 'INFO', 'WARNING', 'ERROR', 'CRITICAL', 'SUCCESS', 'DEBUG',
            'Pipeline', 'MongoDB', 'API'
        ])
        self.filter_combo.currentTextChanged.connect(self._on_filter_changed)
        control_layout.addWidget(self.filter_combo)

        control_layout.addWidget(QLabel("Font:"))
        self.font_size_combo = QComboBox()
        self.font_size_combo.addItems(['9', '10', '11', '12', '13', '14'])
        self.font_size_combo.setCurrentText(str(self.font_size))
        self.font_size_combo.currentTextChanged.connect(self._on_font_size_changed)
        control_layout.addWidget(self.font_size_combo)

        self.auto_scroll_check = QCheckBox("Auto-scroll")
        self.auto_scroll_check.setChecked(True)
        self.auto_scroll_check.stateChanged.connect(self._on_auto_scroll_changed)
        control_layout.addWidget(self.auto_scroll_check)

        clear_btn = QPushButton("🗑 Clear")
        clear_btn.clicked.connect(self._clear_logs)
        control_layout.addWidget(clear_btn)

        control_layout.addStretch()

        layout.addLayout(control_layout)

        self.setLayout(layout)

    def _create_format(self, color: QColor) -> QTextCharFormat:
        """Create text format with color"""
        fmt = QTextCharFormat()
        fmt.setForeground(color)
        fmt.setFont(QFont('Consolas', self.font_size))
        return fmt

    def _extract_category(self, message: str) -> str:
        """Extract category/component from log message"""
        if 'mongodb' in message.lower():
            return 'MongoDB'
        if 'pipeline' in message.lower():
            return 'Pipeline'
        if 'fetcher' in message.lower() or 'api' in message.lower():
            return 'API'
        return 'General'

    @pyqtSlot(str, str)
    def append_log(self, level: str, message: str):
        """
        Append log message with color coding and categorization

        Args:
            level: Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL, SUCCESS)
            message: Log message
        """
        # Extract category
        category = self._extract_category(message)

        # Filter check
        if self.current_filter not in ['All', level]:
            if self.current_filter not in ['Pipeline', 'MongoDB', 'API', 'General'] or category != self.current_filter:
                return

        # Limit total lines
        if self.text_edit.document().lineCount() > self.max_lines:
            cursor = self.text_edit.textCursor()
            cursor.movePosition(QTextCursor.MoveOperation.Start)
            cursor.select(QTextCursor.SelectionType.LineUnderCursor)
            cursor.removeSelectedText()
            cursor.deleteChar()  # Remove newline

        # Format message with category
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        formatted = f"[{timestamp}] {level:8s} | [{category}] {message}\n"

        # Append with color
        cursor = self.text_edit.textCursor()
        cursor.movePosition(QTextCursor.MoveOperation.End)

        # Set format and insert text
        fmt = self.formats.get(level, self.formats['INFO'])
        cursor.setCharFormat(fmt)
        cursor.insertText(formatted)

        # Auto-scroll
        if self.auto_scroll:
            scrollbar = self.text_edit.verticalScrollBar()
            scrollbar.setValue(scrollbar.maximum())

    @pyqtSlot()
    def _clear_logs(self):
        """Clear all logs"""
        self.text_edit.clear()
        self.logs_by_category.clear()
        logger.info("Logs cleared by user")

    @pyqtSlot(str)
    def _on_font_size_changed(self, size_str: str):
        """Handle font size change"""
        try:
            size = int(size_str)
            self.font_size = size
            font = QFont('Consolas', size)
            self.text_edit.setFont(font)

            # Update format fonts
            for level in self.formats:
                fmt = self.formats[level]
                fmt.setFont(font)

        except ValueError:
            pass

    def _on_filter_changed(self, filter_text: str):
        """Handle filter change"""
        self.current_filter = filter_text

    def _on_auto_scroll_changed(self, state: int):
        """Handle auto-scroll toggle"""
        self.auto_scroll = (state == Qt.CheckState.Checked.value)

    def clear(self):
        """Clear all logs"""
        self.text_edit.clear()

