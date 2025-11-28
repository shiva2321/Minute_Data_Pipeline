"""
Pytest Configuration and Shared Fixtures
Provides common test setup, path configuration, and PyQt6 fixtures
"""
import sys
import os
from pathlib import Path

import pytest
from loguru import logger

# Add parent directories to path for imports
ROOT_DIR = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT_DIR))

# Configure logging for tests
logger.remove()
logger.add(sys.stderr, level="DEBUG", format="{time} | {level} | {message}")


# ============================================================================
# PyQt6 Application Fixture
# ============================================================================

@pytest.fixture(scope="session")
def qapp():
    """
    Create a QApplication instance for the entire test session.
    Required for any PyQt6 GUI testing.
    """
    try:
        from PyQt6.QtWidgets import QApplication

        # Check if QApplication already exists
        app = QApplication.instance()
        if app is None:
            app = QApplication([])

        yield app

        # Cleanup
        app.quit()
    except ImportError:
        pytest.skip("PyQt6 not installed")


@pytest.fixture
def qapp_with_cleanup(qapp):
    """
    QApplication fixture with automatic cleanup between tests.
    Use this if you need a fresh state for each test.
    """
    yield qapp
    # Optional: Add cleanup code if needed
    qapp.processEvents()


# ============================================================================
# Database and Cache Fixtures
# ============================================================================

@pytest.fixture
def in_memory_cache():
    """Provide an in-memory SQLite cache for testing"""
    try:
        from dashboard.models import CacheStore

        cache = CacheStore(':memory:')
        yield cache
        cache.close()
    except ImportError:
        pytest.skip("CacheStore not available")


@pytest.fixture
def temp_cache_file(tmp_path):
    """Provide a temporary cache file for testing"""
    try:
        from dashboard.models import CacheStore

        cache_path = tmp_path / "test_cache.db"
        cache = CacheStore(str(cache_path))
        yield cache
        cache.close()
    except ImportError:
        pytest.skip("CacheStore not available")


# ============================================================================
# Pipeline and Configuration Fixtures
# ============================================================================

@pytest.fixture
def pipeline_config():
    """Provide default pipeline configuration for testing"""
    return {
        'max_workers': 3,
        'mode': 'incremental',
        'api_calls_per_minute': 80,
        'api_calls_per_day': 95000,
        'symbols': ['TEST1', 'TEST2', 'TEST3'],
        'data_dir': './test_data'
    }


@pytest.fixture
def test_symbols():
    """Provide test symbols"""
    return ['AAPL', 'MSFT', 'GOOGL', 'AMZN']


# ============================================================================
# Feature Engineering Fixtures
# ============================================================================

@pytest.fixture
def sample_price_data():
    """Provide sample OHLCV price data for testing"""
    try:
        import pandas as pd
        import numpy as np
        from datetime import datetime, timedelta

        rows = 500
        now = datetime.now()
        dt_index = pd.date_range(end=now, periods=rows, freq='1min')
        base = 100 + np.cumsum(np.random.normal(0, 0.05, rows))

        return pd.DataFrame({
            'datetime': dt_index,
            'open': base + np.random.uniform(-0.05, 0.05, rows),
            'high': base + np.random.uniform(0.01, 0.2, rows),
            'low': base - np.random.uniform(0.01, 0.2, rows),
            'close': base,
            'volume': np.random.randint(1000, 50000, rows)
        })
    except ImportError:
        pytest.skip("pandas/numpy not installed")


@pytest.fixture
def feature_engineer():
    """Provide a FeatureEngineer instance for testing"""
    try:
        from feature_engineering import FeatureEngineer
        return FeatureEngineer()
    except ImportError:
        pytest.skip("FeatureEngineer not available")


# ============================================================================
# Rate Limiter Fixtures
# ============================================================================

@pytest.fixture
def rate_limiter():
    """Provide a rate limiter instance for testing"""
    try:
        from utils.rate_limiter import AdaptiveRateLimiter
        return AdaptiveRateLimiter(calls_per_minute=100, calls_per_day=1000)
    except ImportError:
        pytest.skip("AdaptiveRateLimiter not available")


# ============================================================================
# Pytest Hooks and Configuration
# ============================================================================

def pytest_configure(config):
    """Configure pytest with custom markers"""
    config.addinivalue_line(
        "markers", "unit: mark test as a unit test"
    )
    config.addinivalue_line(
        "markers", "integration: mark test as an integration test"
    )
    config.addinivalue_line(
        "markers", "diagnostic: mark test as a diagnostic test"
    )
    config.addinivalue_line(
        "markers", "slow: mark test as slow running"
    )
    config.addinivalue_line(
        "markers", "requires_pyqt: mark test as requiring PyQt6"
    )


def pytest_collection_modifyitems(config, items):
    """Automatically mark tests based on their location"""
    for item in items:
        # Mark tests based on directory
        if "unit" in str(item.fspath):
            item.add_marker(pytest.mark.unit)
        elif "integration" in str(item.fspath):
            item.add_marker(pytest.mark.integration)
        elif "diagnostics" in str(item.fspath):
            item.add_marker(pytest.mark.diagnostic)


# ============================================================================
# Utility Functions for Tests
# ============================================================================

@pytest.fixture
def log_output():
    """Capture log output during tests"""
    import io
    log_capture = io.StringIO()
    logger.add(log_capture, level="DEBUG", format="{time} | {level} | {message}")
    yield log_capture
    logger.remove(log_capture)

