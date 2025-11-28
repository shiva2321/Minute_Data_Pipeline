"""
API Usage Visualization Widget
Shows rate limit usage with progress bars and color coding
"""
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QProgressBar, QGroupBox
from PyQt6.QtCore import pyqtSlot


class APIUsageWidget(QWidget):
    """
    Visual gauge for API rate limit usage
    Color-coded based on usage percentage
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.daily_limit = 95000
        self.minute_limit = 80

        self.init_ui()

    def init_ui(self):
        """Initialize UI components"""
        layout = QVBoxLayout()

        # Group box
        group = QGroupBox("API Usage")
        group_layout = QVBoxLayout()

        # Daily usage
        self.daily_label = QLabel(f"Daily: 0 / {self.daily_limit:,}")
        self.daily_bar = QProgressBar()
        self.daily_bar.setMaximum(self.daily_limit)
        self.daily_bar.setValue(0)
        self.daily_bar.setFormat("%v / %m (%p%)")

        group_layout.addWidget(self.daily_label)
        group_layout.addWidget(self.daily_bar)

        # Per-minute usage
        self.minute_label = QLabel(f"This Minute: 0 / {self.minute_limit}")
        self.minute_bar = QProgressBar()
        self.minute_bar.setMaximum(self.minute_limit)
        self.minute_bar.setValue(0)
        self.minute_bar.setFormat("%v / %m (%p%)")

        group_layout.addWidget(self.minute_label)
        group_layout.addWidget(self.minute_bar)

        # Remaining calls
        self.remaining_label = QLabel("Remaining Today: 95,000")
        group_layout.addWidget(self.remaining_label)

        group.setLayout(group_layout)
        layout.addWidget(group)

        self.setLayout(layout)

    @pyqtSlot(dict)
    def update_stats(self, stats: dict):
        """
        Update API usage statistics

        Args:
            stats: Dictionary with 'daily_calls', 'minute_calls', 'daily_remaining'
        """
        daily_calls = stats.get('daily_calls', 0)
        minute_calls = stats.get('minute_calls', 0)
        daily_remaining = stats.get('daily_remaining', self.daily_limit)

        # Update daily usage
        self.daily_label.setText(f"Daily: {daily_calls:,} / {self.daily_limit:,}")
        self.daily_bar.setValue(daily_calls)

        # Color code based on usage
        daily_pct = (daily_calls / self.daily_limit) * 100 if self.daily_limit > 0 else 0

        if daily_pct >= 95:
            self.daily_bar.setStyleSheet("QProgressBar::chunk { background-color: #c50f1f; }")
        elif daily_pct >= 80:
            self.daily_bar.setStyleSheet("QProgressBar::chunk { background-color: #ca5010; }")
        elif daily_pct >= 60:
            self.daily_bar.setStyleSheet("QProgressBar::chunk { background-color: #f7630c; }")
        else:
            self.daily_bar.setStyleSheet("QProgressBar::chunk { background-color: #0e7c0e; }")

        # Update per-minute usage
        self.minute_label.setText(f"This Minute: {minute_calls} / {self.minute_limit}")
        self.minute_bar.setValue(minute_calls)

        # Color code minute bar
        minute_pct = (minute_calls / self.minute_limit) * 100 if self.minute_limit > 0 else 0

        if minute_pct >= 90:
            self.minute_bar.setStyleSheet("QProgressBar::chunk { background-color: #c50f1f; }")
        elif minute_pct >= 70:
            self.minute_bar.setStyleSheet("QProgressBar::chunk { background-color: #ca5010; }")
        else:
            self.minute_bar.setStyleSheet("QProgressBar::chunk { background-color: #0e7c0e; }")

        # Update remaining
        self.remaining_label.setText(f"Remaining Today: {daily_remaining:,}")

    def reset(self):
        """Reset all counters to zero"""
        self.daily_bar.setValue(0)
        self.minute_bar.setValue(0)
        self.daily_label.setText(f"Daily: 0 / {self.daily_limit:,}")
        self.minute_label.setText(f"This Minute: 0 / {self.minute_limit}")
        self.remaining_label.setText(f"Remaining Today: {self.daily_limit:,}")

