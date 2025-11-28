"""
Custom Qt signals for pipeline updates
Thread-safe communication between workers and UI
"""
from PyQt6.QtCore import QObject, pyqtSignal


class PipelineSignals(QObject):
    """Signals for pipeline controller updates"""

    # Symbol processing signals
    symbol_started = pyqtSignal(str)  # symbol
    symbol_progress = pyqtSignal(str, str, int)  # symbol, status, progress%
    symbol_completed = pyqtSignal(str, dict)  # symbol, profile
    symbol_failed = pyqtSignal(str, str)  # symbol, error_message
    symbol_skipped = pyqtSignal(str, str)  # symbol, reason

    # Pipeline-wide signals
    pipeline_started = pyqtSignal(int)  # total_symbols
    pipeline_completed = pyqtSignal(dict)  # summary stats
    pipeline_paused = pyqtSignal()
    pipeline_stopped = pyqtSignal()
    pipeline_error = pyqtSignal(str)  # error_message

    # API and resource monitoring
    api_stats_updated = pyqtSignal(dict)  # rate limiter stats
    eta_updated = pyqtSignal(int)  # seconds remaining

    # Logging
    log_message = pyqtSignal(str, str)  # level, message


class DatabaseSignals(QObject):
    """Signals for database operations"""

    profiles_loaded = pyqtSignal(list)  # list of profile dicts
    profile_updated = pyqtSignal(str, dict)  # symbol, updated_profile
    profile_deleted = pyqtSignal(str)  # symbol
    database_error = pyqtSignal(str)  # error_message
    connection_status = pyqtSignal(bool, str)  # connected, message

