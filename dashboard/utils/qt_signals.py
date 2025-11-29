"""
Custom Qt signals for pipeline updates
Thread-safe communication between workers and UI
"""
from PyQt6.QtCore import QObject, pyqtSignal


class PipelineSignals(QObject):
    """Signals for pipeline controller updates"""

    # Symbol processing signals (extended: micro_stage, api_calls_used, duration_seconds, is_paused)
    symbol_started = pyqtSignal(str)  # symbol
    symbol_progress = pyqtSignal(str, str, int, str, int, int, float, bool, str)  # symbol, status, progress%, micro_stage, data_points, api_calls_used, duration_seconds, is_paused, date_range
    symbol_completed = pyqtSignal(str, dict)  # symbol, profile
    symbol_failed = pyqtSignal(str, str)  # symbol, error_message
    symbol_skipped = pyqtSignal(str, str)  # symbol, reason

    # Pipeline-wide signals
    pipeline_started = pyqtSignal(int)  # total_symbols
    pipeline_completed = pyqtSignal(dict)  # summary stats
    pipeline_paused = pyqtSignal()
    pipeline_stopped = pyqtSignal()
    pipeline_error = pyqtSignal(str)  # error_message
    pipeline_cleared = pyqtSignal()  # emitted when queue cleared

    # API and resource monitoring
    api_stats_updated = pyqtSignal(dict)  # rate limiter stats
    eta_updated = pyqtSignal(int)  # seconds remaining
    metrics_updated = pyqtSignal(dict)  # comprehensive metrics (eta, throughput, progress, etc.)

    # Logging
    log_message = pyqtSignal(str, str)  # level, message


class DatabaseSignals(QObject):
    """Signals for database operations"""

    profiles_loaded = pyqtSignal(list)  # list of profile dicts
    profile_updated = pyqtSignal(str, dict)  # symbol, updated_profile
    profile_deleted = pyqtSignal(str)  # symbol
    database_error = pyqtSignal(str)  # error_message
    connection_status = pyqtSignal(bool, str)  # connected, message
