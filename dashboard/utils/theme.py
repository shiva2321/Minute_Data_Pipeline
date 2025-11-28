"""
Qt stylesheet and theming
Professional dark theme optimized for data applications
"""

DARK_THEME = """
/* Global Styles */
QWidget {
    background-color: #1e1e1e;
    color: #e0e0e0;
    font-family: 'Segoe UI', Arial, sans-serif;
    font-size: 9pt;
}

/* Main Window */
QMainWindow {
    background-color: #1e1e1e;
}

/* Tab Widget */
QTabWidget::pane {
    border: 1px solid #3c3c3c;
    background-color: #252526;
    border-radius: 4px;
}

QTabBar::tab {
    background-color: #2d2d30;
    color: #cccccc;
    padding: 8px 16px;
    margin-right: 2px;
    border-top-left-radius: 4px;
    border-top-right-radius: 4px;
}

QTabBar::tab:selected {
    background-color: #007acc;
    color: #ffffff;
}

QTabBar::tab:hover:!selected {
    background-color: #3e3e42;
}

/* Buttons */
QPushButton {
    background-color: #0e639c;
    color: #ffffff;
    border: none;
    padding: 6px 16px;
    border-radius: 4px;
    font-weight: 500;
}

QPushButton:hover {
    background-color: #1177bb;
}

QPushButton:pressed {
    background-color: #005a9e;
}

QPushButton:disabled {
    background-color: #3c3c3c;
    color: #6e6e6e;
}

/* Success Button */
QPushButton#startButton {
    background-color: #0e7c0e;
}

QPushButton#startButton:hover {
    background-color: #13a10e;
}

/* Warning Button */
QPushButton#pauseButton {
    background-color: #ca5010;
}

QPushButton#pauseButton:hover {
    background-color: #e8590c;
}

/* Danger Button */
QPushButton#stopButton {
    background-color: #c50f1f;
}

QPushButton#stopButton:hover {
    background-color: #e81123;
}

/* Input Fields */
QLineEdit, QTextEdit, QPlainTextEdit {
    background-color: #2d2d30;
    color: #e0e0e0;
    border: 1px solid #3c3c3c;
    border-radius: 4px;
    padding: 4px 8px;
}

QLineEdit:focus, QTextEdit:focus, QPlainTextEdit:focus {
    border: 1px solid #007acc;
}

/* ComboBox */
QComboBox {
    background-color: #2d2d30;
    color: #e0e0e0;
    border: 1px solid #3c3c3c;
    border-radius: 4px;
    padding: 4px 8px;
}

QComboBox:hover {
    border: 1px solid #007acc;
}

QComboBox::drop-down {
    border: none;
    width: 20px;
}

QComboBox::down-arrow {
    image: url(data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMTYiIGhlaWdodD0iMTYiIHZpZXdCb3g9IjAgMCAxNiAxNiIgZmlsbD0ibm9uZSIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj4KPHBhdGggZD0iTTQgNkw4IDEwTDEyIDYiIHN0cm9rZT0iI2UwZTBlMCIgc3Ryb2tlLXdpZHRoPSIyIiBzdHJva2UtbGluZWNhcD0icm91bmQiIHN0cm9rZS1saW5lam9pbj0icm91bmQiLz4KPC9zdmc+);
}

QComboBox QAbstractItemView {
    background-color: #2d2d30;
    color: #e0e0e0;
    selection-background-color: #007acc;
    border: 1px solid #3c3c3c;
}

/* SpinBox */
QSpinBox, QDoubleSpinBox {
    background-color: #2d2d30;
    color: #e0e0e0;
    border: 1px solid #3c3c3c;
    border-radius: 4px;
    padding: 4px 8px;
}

/* CheckBox */
QCheckBox {
    spacing: 8px;
    color: #e0e0e0;
}

QCheckBox::indicator {
    width: 16px;
    height: 16px;
    border-radius: 3px;
    border: 1px solid #3c3c3c;
    background-color: #2d2d30;
}

QCheckBox::indicator:checked {
    background-color: #007acc;
    border: 1px solid #007acc;
}

QCheckBox::indicator:hover {
    border: 1px solid #007acc;
}

/* RadioButton */
QRadioButton {
    spacing: 8px;
    color: #e0e0e0;
}

QRadioButton::indicator {
    width: 16px;
    height: 16px;
    border-radius: 8px;
    border: 1px solid #3c3c3c;
    background-color: #2d2d30;
}

QRadioButton::indicator:checked {
    background-color: #007acc;
    border: 1px solid #007acc;
}

/* ProgressBar */
QProgressBar {
    background-color: #2d2d30;
    border: 1px solid #3c3c3c;
    border-radius: 4px;
    text-align: center;
    color: #e0e0e0;
    height: 20px;
}

QProgressBar::chunk {
    background-color: #0e639c;
    border-radius: 3px;
}

QProgressBar.success::chunk {
    background-color: #0e7c0e;
}

QProgressBar.warning::chunk {
    background-color: #ca5010;
}

QProgressBar.danger::chunk {
    background-color: #c50f1f;
}

/* TableWidget */
QTableWidget {
    background-color: #252526;
    alternate-background-color: #2d2d30;
    gridline-color: #3c3c3c;
    border: 1px solid #3c3c3c;
    border-radius: 4px;
}

QTableWidget::item {
    padding: 4px;
    color: #e0e0e0;
}

QTableWidget::item:selected {
    background-color: #007acc;
    color: #ffffff;
}

QHeaderView::section {
    background-color: #2d2d30;
    color: #cccccc;
    padding: 6px;
    border: none;
    border-right: 1px solid #3c3c3c;
    border-bottom: 1px solid #3c3c3c;
    font-weight: 600;
}

/* ScrollBar */
QScrollBar:vertical {
    background-color: #1e1e1e;
    width: 14px;
    margin: 0px;
}

QScrollBar::handle:vertical {
    background-color: #424242;
    min-height: 20px;
    border-radius: 7px;
}

QScrollBar::handle:vertical:hover {
    background-color: #4e4e4e;
}

QScrollBar:horizontal {
    background-color: #1e1e1e;
    height: 14px;
    margin: 0px;
}

QScrollBar::handle:horizontal {
    background-color: #424242;
    min-width: 20px;
    border-radius: 7px;
}

QScrollBar::handle:horizontal:hover {
    background-color: #4e4e4e;
}

QScrollBar::add-line, QScrollBar::sub-line {
    border: none;
    background: none;
}

/* GroupBox */
QGroupBox {
    border: 1px solid #3c3c3c;
    border-radius: 4px;
    margin-top: 8px;
    padding-top: 12px;
    font-weight: 600;
}

QGroupBox::title {
    subcontrol-origin: margin;
    subcontrol-position: top left;
    padding: 0 8px;
    color: #007acc;
}

/* StatusBar */
QStatusBar {
    background-color: #007acc;
    color: #ffffff;
    border-top: 1px solid #005a9e;
}

/* ToolTip */
QToolTip {
    background-color: #2d2d30;
    color: #e0e0e0;
    border: 1px solid #007acc;
    padding: 4px;
    border-radius: 4px;
}

/* Menu */
QMenu {
    background-color: #2d2d30;
    border: 1px solid #3c3c3c;
    padding: 4px;
}

QMenu::item {
    padding: 6px 24px;
    border-radius: 4px;
}

QMenu::item:selected {
    background-color: #007acc;
    color: #ffffff;
}

/* Splitter */
QSplitter::handle {
    background-color: #3c3c3c;
}

QSplitter::handle:hover {
    background-color: #007acc;
}
"""


def load_stylesheet():
    """Load the dark theme stylesheet"""
    return DARK_THEME

