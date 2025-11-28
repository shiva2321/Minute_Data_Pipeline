"""
API Usage Visualization Widget
Shows rate limit usage with progress bars and color coding
Persists data across sessions using CacheStore
"""
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QProgressBar, QGroupBox
from PyQt6.QtCore import pyqtSlot
import os, json
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class APIUsageWidget(QWidget):
    """
    Visual gauge for API rate limit usage
    """
    def __init__(self, parent=None, cache_store=None):
        super().__init__(parent)
        self.cache_store = cache_store
        self._cache_path = os.path.expanduser('~/.pipeline_api_usage.json')
        self._current_day_key = datetime.now().strftime('%Y-%m-%d')
        self._state = self._load_state()
        self.init_ui()
        # Initialize display from state
        self.update_stats(self._state.get('stats', {}))

    def init_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(6, 6, 6, 6)
        layout.setSpacing(4)
        # Daily usage
        self.daily_label = QLabel("API Usage Today: 0 / 95,000")
        self.daily_label.setStyleSheet("font-size: 11px;")
        self.daily_bar = QProgressBar()
        self.daily_bar.setMaximum(95000)
        self.daily_bar.setTextVisible(False)
        # Per-minute usage
        self.minute_label = QLabel("API This Minute: 0 / 80")
        self.minute_label.setStyleSheet("font-size: 11px;")
        self.minute_bar = QProgressBar()
        self.minute_bar.setMaximum(80)
        self.minute_bar.setTextVisible(False)
        layout.addWidget(self.daily_label)
        layout.addWidget(self.daily_bar)
        layout.addWidget(self.minute_label)
        layout.addWidget(self.minute_bar)
        self.setLayout(layout)

    def _load_state(self) -> dict:
        """Load persisted API usage for today"""
        if self.cache_store and hasattr(self.cache_store, 'load_api_usage'):
            state = self.cache_store.load_api_usage()
        else:
            if os.path.exists(self._cache_path):
                try:
                    with open(self._cache_path, 'r') as f:
                        state = json.load(f)
                except Exception:
                    state = {}
            else:
                state = {}
        # Reset if date changed
        if state.get('day') != self._current_day_key:
            return {'day': self._current_day_key, 'stats': {'daily_calls': 0, 'minute_calls': 0}}
        return state

    def _save_state(self):
        """Persist API usage for today"""
        self._state['day'] = self._current_day_key
        if self.cache_store and hasattr(self.cache_store, 'save_api_usage'):
            try:
                self.cache_store.save_api_usage(self._state)
            except Exception:
                pass
        else:
            try:
                with open(self._cache_path, 'w') as f:
                    json.dump(self._state, f)
            except Exception:
                pass

    @pyqtSlot(dict)
    def update_stats(self, stats):
        """Update gauges with rate limiter stats and persist for the day"""
        daily_calls = max(stats.get('daily_calls', 0), self._state.get('stats', {}).get('daily_calls', 0))
        minute_calls = stats.get('minute_calls', 0)
        self._state['stats'] = {'daily_calls': daily_calls, 'minute_calls': minute_calls}
        self._save_state()
        # Update UI
        self.daily_label.setText(f"API Usage Today: {daily_calls:,} / 95,000")
        self.daily_bar.setValue(min(daily_calls, self.daily_bar.maximum()))
        if daily_calls > 90000:
            self.daily_bar.setStyleSheet("QProgressBar::chunk { background-color: #c50f1f; }")
        elif daily_calls > 70000:
            self.daily_bar.setStyleSheet("QProgressBar::chunk { background-color: #f7630c; }")
        else:
            self.daily_bar.setStyleSheet("QProgressBar::chunk { background-color: #107c10; }")
        self.minute_label.setText(f"API This Minute: {minute_calls} / 80")
        self.minute_bar.setValue(min(minute_calls, self.minute_bar.maximum()))

    def reset(self):
        """Reset UI and state (used when clearing)"""
        self._state = {'day': self._current_day_key, 'stats': {'daily_calls': 0, 'minute_calls': 0}}
        self._save_state()
        self.update_stats(self._state['stats'])
