import time
from utils.rate_limiter import AdaptiveRateLimiter

def test_per_minute_throttling():
    limiter = AdaptiveRateLimiter(calls_per_minute=5, calls_per_day=1000)
    start = time.time()
    for _ in range(5):
        limiter.wait_if_needed()
        limiter.record_call()
    elapsed = time.time() - start
    assert elapsed < 2.0
    start = time.time()
    limiter.wait_if_needed()
    elapsed = time.time() - start
    assert elapsed >= 55

def test_daily_quota_enforcement():
    limiter = AdaptiveRateLimiter(calls_per_minute=100, calls_per_day=3)
    for _ in range(3):
        limiter.wait_if_needed()
        limiter.record_call()
    stats = limiter.get_stats()
    assert stats['daily_remaining'] == 0

def test_exponential_backoff():
    limiter = AdaptiveRateLimiter(calls_per_minute=100, calls_per_day=1000)
    limiter.record_error(initial_delay=1, max_delay=16)
    assert limiter.current_delay == 1
    limiter.record_error(initial_delay=1, max_delay=16)
    assert limiter.current_delay == 2
    limiter.record_error(initial_delay=1, max_delay=16)
    assert limiter.current_delay == 4
    limiter.record_error(initial_delay=1, max_delay=16)
    assert limiter.current_delay == 8
    limiter.record_error(initial_delay=1, max_delay=16)
    assert limiter.current_delay == 16

def test_backoff_reset_on_success():
    limiter = AdaptiveRateLimiter(calls_per_minute=100, calls_per_day=1000)
    limiter.record_error(initial_delay=1, max_delay=16)
    assert limiter.current_delay > 0
    limiter.record_call()
    assert limiter.current_delay == 0
    assert limiter.consecutive_errors == 0

