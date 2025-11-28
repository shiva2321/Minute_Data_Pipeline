"""
Metrics Calculator - Real-time ETA and performance metrics
"""
import time
from typing import Dict, List, Optional
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)


class MetricsCalculator:
    """Calculates real-time metrics like ETA, throughput, and resource utilization"""

    def __init__(self):
        self.symbol_times = {}  # symbol -> completion time in seconds
        self.symbol_start_times = {}  # symbol -> start time timestamp
        self.completed_count = 0
        self.total_symbols = 0
        self.start_time = None
        self.update_interval = 10  # Update metrics every 10 seconds

    def initialize(self, total_symbols: int, start_time: Optional[float] = None):
        """Initialize metrics calculator"""
        self.total_symbols = total_symbols
        self.completed_count = 0
        self.symbol_times.clear()
        self.symbol_start_times.clear()
        self.start_time = start_time or time.time()

    def mark_symbol_started(self, symbol: str, start_time: Optional[float] = None):
        """Mark when a symbol starts processing"""
        self.symbol_start_times[symbol] = start_time or time.time()

    def mark_symbol_completed(self, symbol: str):
        """Mark when a symbol completes processing"""
        if symbol in self.symbol_start_times:
            duration = time.time() - self.symbol_start_times[symbol]
            self.symbol_times[symbol] = duration
            self.completed_count += 1
            del self.symbol_start_times[symbol]

    def calculate_average_time_per_symbol(self) -> float:
        """Calculate average completion time per symbol"""
        if not self.symbol_times:
            return 0.0
        return sum(self.symbol_times.values()) / len(self.symbol_times)

    def calculate_eta_seconds(self, processing_count: int = 0) -> Optional[int]:
        """
        Calculate estimated time to completion in seconds

        Args:
            processing_count: Number of symbols currently being processed

        Returns:
            ETA in seconds, or None if cannot calculate
        """
        remaining = self.total_symbols - self.completed_count - processing_count

        if remaining <= 0:
            return 0

        avg_time = self.calculate_average_time_per_symbol()
        if avg_time <= 0:
            return None

        # Estimate based on remaining symbols and current workers
        # Account for parallel processing
        estimated_seconds = avg_time * remaining / max(1, processing_count)
        return max(0, int(estimated_seconds))

    def calculate_eta_string(self, processing_count: int = 0) -> str:
        """Get human-readable ETA string"""
        eta_seconds = self.calculate_eta_seconds(processing_count)

        if eta_seconds is None:
            return "Calculating..."

        if eta_seconds == 0:
            return "Complete"

        hours = eta_seconds // 3600
        minutes = (eta_seconds % 3600) // 60
        seconds = eta_seconds % 60

        if hours > 0:
            return f"{hours}h {minutes}m {seconds}s"
        elif minutes > 0:
            return f"{minutes}m {seconds}s"
        else:
            return f"{seconds}s"

    def calculate_progress_percent(self) -> int:
        """Calculate overall progress percentage"""
        if self.total_symbols == 0:
            return 0
        return int((self.completed_count / self.total_symbols) * 100)

    def get_throughput_symbols_per_minute(self) -> float:
        """Calculate throughput in symbols per minute"""
        if not self.start_time:
            return 0.0

        elapsed_seconds = time.time() - self.start_time
        if elapsed_seconds < 1:
            return 0.0

        return (self.completed_count / elapsed_seconds) * 60

    def get_summary_stats(self, processing_count: int = 0) -> Dict:
        """Get comprehensive metrics summary"""
        avg_time = self.calculate_average_time_per_symbol()
        eta_seconds = self.calculate_eta_seconds(processing_count)
        eta_str = self.calculate_eta_string(processing_count)

        return {
            'completed': self.completed_count,
            'remaining': self.total_symbols - self.completed_count,
            'processing': processing_count,
            'progress_percent': self.calculate_progress_percent(),
            'average_time_per_symbol': round(avg_time, 2),
            'eta_seconds': eta_seconds,
            'eta_string': eta_str,
            'throughput_symbols_per_minute': round(self.get_throughput_symbols_per_minute(), 2),
            'elapsed_seconds': time.time() - self.start_time if self.start_time else 0
        }

    def get_formatted_metrics(self, processing_count: int = 0) -> str:
        """Get formatted metrics string for display"""
        stats = self.get_summary_stats(processing_count)

        return (
            f"Progress: {stats['progress_percent']}% | "
            f"Completed: {stats['completed']}/{self.total_symbols} | "
            f"ETA: {stats['eta_string']} | "
            f"Throughput: {stats['throughput_symbols_per_minute']} sym/min"
        )


class APIStatsTracker:
    """Track API usage statistics in real-time"""

    def __init__(self):
        self.minute_calls = 0
        self.daily_calls = 0
        self.total_calls = 0
        self.minute_start_time = time.time()
        self.day_start_time = time.time()

    def add_call(self, calls: int = 1):
        """Record API calls"""
        self.minute_calls += calls
        self.daily_calls += calls
        self.total_calls += calls

    def reset_minute_if_needed(self) -> bool:
        """Reset minute counter if 60 seconds have passed"""
        elapsed = time.time() - self.minute_start_time
        if elapsed >= 60:
            self.minute_calls = 0
            self.minute_start_time = time.time()
            return True
        return False

    def reset_daily_if_needed(self) -> bool:
        """Reset daily counter if 24 hours have passed"""
        elapsed = time.time() - self.day_start_time
        if elapsed >= 86400:  # 24 hours
            self.daily_calls = 0
            self.day_start_time = time.time()
            return True
        return False

    def get_minute_remaining(self, limit: int) -> int:
        """Get remaining API calls for this minute"""
        self.reset_minute_if_needed()
        return max(0, limit - self.minute_calls)

    def get_daily_remaining(self, limit: int) -> int:
        """Get remaining API calls for today"""
        self.reset_daily_if_needed()
        return max(0, limit - self.daily_calls)

    def get_stats(self, minute_limit: int, daily_limit: int) -> Dict:
        """Get comprehensive API stats"""
        self.reset_minute_if_needed()
        self.reset_daily_if_needed()

        return {
            'minute_calls': self.minute_calls,
            'minute_remaining': self.get_minute_remaining(minute_limit),
            'minute_limit': minute_limit,
            'minute_percent': int((self.minute_calls / minute_limit) * 100) if minute_limit > 0 else 0,
            'daily_calls': self.daily_calls,
            'daily_remaining': self.get_daily_remaining(daily_limit),
            'daily_limit': daily_limit,
            'daily_percent': int((self.daily_calls / daily_limit) * 100) if daily_limit > 0 else 0,
            'total_calls': self.total_calls
        }

