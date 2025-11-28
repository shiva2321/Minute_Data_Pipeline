import time
import logging
from collections import deque
from datetime import datetime, timedelta

class AdaptiveRateLimiter:
    """
    Rate limiter with:
    - Per-minute throttling
    - Daily quota tracking
    - Exponential backoff on errors
    - Automatic recovery
    """
    def __init__(self, calls_per_minute=80, calls_per_day=95000):
        self.calls_per_minute = calls_per_minute
        self.calls_per_day = calls_per_day
        self.minute_window = deque(maxlen=calls_per_minute)
        self.daily_calls = 0
        self.daily_reset_time = datetime.now() + timedelta(days=1)
        self.consecutive_errors = 0
        self.current_delay = 0
        self.logger = logging.getLogger(__name__)

    def wait_if_needed(self):
        now = datetime.now()
        if now >= self.daily_reset_time:
            self.daily_calls = 0
            self.daily_reset_time = now + timedelta(days=1)
            self.logger.info("Daily API quota reset")
        if self.daily_calls >= self.calls_per_day:
            wait_seconds = (self.daily_reset_time - now).total_seconds()
            self.logger.warning(f"Daily limit reached. Sleeping {wait_seconds:.0f}s")
            time.sleep(wait_seconds)
            return
        if len(self.minute_window) >= self.calls_per_minute:
            oldest_call = self.minute_window[0]
            elapsed = (now - oldest_call).total_seconds()
            if elapsed < 60:
                sleep_time = 60 - elapsed + 0.5
                self.logger.debug(f"Rate limit: sleeping {sleep_time:.1f}s")
                time.sleep(sleep_time)
        if self.current_delay > 0:
            self.logger.info(f"Backoff delay: {self.current_delay}s")
            time.sleep(self.current_delay)

    def record_call(self):
        self.minute_window.append(datetime.now())
        self.daily_calls += 1
        if self.consecutive_errors > 0:
            self.logger.info("API call successful, resetting backoff")
            self.consecutive_errors = 0
            self.current_delay = 0

    def record_error(self, initial_delay=5, max_delay=300):
        self.consecutive_errors += 1
        self.current_delay = min(initial_delay * (2 ** (self.consecutive_errors - 1)), max_delay)
        self.logger.warning(
            f"API error #{self.consecutive_errors}. Next delay: {self.current_delay}s"
        )

    def get_stats(self):
        return {
            'daily_calls': self.daily_calls,
            'daily_remaining': self.calls_per_day - self.daily_calls,
            'minute_calls': len(self.minute_window),
            'consecutive_errors': self.consecutive_errors,
            'current_delay': self.current_delay
        }

