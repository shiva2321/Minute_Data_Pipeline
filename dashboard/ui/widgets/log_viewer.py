"""
Live log viewer with color-coded messages and auto-scroll
"""
from PyQt6.QtWidgets import QTextEdit, QWidget, QVBoxLayout, QHBoxLayout, QComboBox, QCheckBox, QLabel
from PyQt6.QtGui import QTextCharFormat, QColor, QFont, QTextCursor
from PyQt6.QtCore import pyqtSlot, Qt
from datetime import datetime


class LogViewer(QWidget):
    """
    Color-coded log viewer with filtering and auto-scroll
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.max_lines = 1000
        self.auto_scroll = True
        self.current_filter = "All"

        self.init_ui()

    def init_ui(self):
        """Initialize UI components"""
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)

        # Text edit for logs
        self.text_edit = QTextEdit()
        self.text_edit.setReadOnly(True)
        self.text_edit.setFont(QFont('Consolas', 9))
        self.text_edit.setLineWrapMode(QTextEdit.LineWrapMode.NoWrap)

        # Color formats
        self.formats = {
            'DEBUG': self._create_format(QColor(150, 150, 150)),
            'INFO': self._create_format(QColor(220, 220, 220)),
            'WARNING': self._create_format(QColor(255, 200, 0)),
            'ERROR': self._create_format(QColor(255, 100, 100)),
            'SUCCESS': self._create_format(QColor(100, 255, 100))
        }

        layout.addWidget(self.text_edit)

        # Control bar
        control_layout = QHBoxLayout()

        control_layout.addWidget(QLabel("Filter:"))

        self.filter_combo = QComboBox()
        self.filter_combo.addItems(['All', 'INFO', 'WARNING', 'ERROR', 'SUCCESS', 'DEBUG'])
        self.filter_combo.currentTextChanged.connect(self._on_filter_changed)
        control_layout.addWidget(self.filter_combo)

        self.auto_scroll_check = QCheckBox("Auto-scroll")
        self.auto_scroll_check.setChecked(True)
        self.auto_scroll_check.stateChanged.connect(self._on_auto_scroll_changed)
        control_layout.addWidget(self.auto_scroll_check)

        control_layout.addStretch()

        layout.addLayout(control_layout)

        self.setLayout(layout)

    def _create_format(self, color: QColor) -> QTextCharFormat:
        """Create text format with color"""
        fmt = QTextCharFormat()
        fmt.setForeground(color)
        return fmt

    @pyqtSlot(str, str)
    def append_log(self, level: str, message: str):
        """
        Append log message with color coding

        Args:
            level: Log level (DEBUG, INFO, WARNING, ERROR, SUCCESS)
            message: Log message
        """
        # Filter check
        if self.current_filter != "All" and level != self.current_filter:
            return

        # Limit total lines
        if self.text_edit.document().lineCount() > self.max_lines:
            cursor = self.text_edit.textCursor()
            cursor.movePosition(QTextCursor.MoveOperation.Start)
            cursor.select(QTextCursor.SelectionType.LineUnderCursor)
            cursor.removeSelectedText()
            cursor.deleteChar()  # Remove newline

        # Format message
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        formatted = f"[{timestamp}] {level:8s} | {message}\n"

        # Append with color
        cursor = self.text_edit.textCursor()
        cursor.movePosition(QTextCursor.MoveOperation.End)

        # Set format and insert text
        cursor.setCharFormat(self.formats.get(level, self.formats['INFO']))
        cursor.insertText(formatted)

        # Auto-scroll
        if self.auto_scroll:
            scrollbar = self.text_edit.verticalScrollBar()
            scrollbar.setValue(scrollbar.maximum())

    def _on_filter_changed(self, filter_text: str):
        """Handle filter change"""
        self.current_filter = filter_text

    def _on_auto_scroll_changed(self, state: int):
        """Handle auto-scroll toggle"""
        self.auto_scroll = (state == Qt.CheckState.Checked.value)

    def clear(self):
        """Clear all logs"""
        self.text_edit.clear()

