#!/usr/bin/env python
"""
v1.1.0 Stability Test Suite
Tests all critical components to ensure production readiness
"""

import sys
from pathlib import Path

# Add parent directory to Python path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

def test_core_modules():
    """Test all core module imports"""
    print("\n" + "="*70)
    print("Testing Core Modules")
    print("="*70)

    try:
        from config import settings
        print("✓ config.py - Settings management")

        from data_fetcher import EODHDDataFetcher
        print("✓ data_fetcher.py - API integration")

        from feature_engineering import FeatureEngineer
        print("✓ feature_engineering.py - Feature calculations")

        from mongodb_storage import MongoDBStorage
        print("✓ mongodb_storage.py - Database operations")

        from pipeline import MinuteDataPipeline
        print("✓ pipeline.py - Main orchestration")

        from utils.rate_limiter import AdaptiveRateLimiter
        print("✓ utils/rate_limiter.py - Rate limiting")

        print("\n✅ Core Modules: PASSED")
        return True
    except Exception as e:
        print(f"\n❌ Core Modules: FAILED - {e}")
        return False

def test_dashboard():
    """Test all dashboard components"""
    print("\n" + "="*70)
    print("Testing Dashboard Components")
    print("="*70)

    try:
        from dashboard.ui.panels.control_panel import ControlPanel
        print("✓ ControlPanel - Symbol input & options")

        from dashboard.ui.panels.monitor_panel import MonitorPanel
        print("✓ MonitorPanel - Live metrics & queue")

        from dashboard.ui.panels.profile_browser import ProfileBrowser
        print("✓ ProfileBrowser - Database viewer")

        from dashboard.ui.panels.settings_panel import SettingsPanel
        print("✓ SettingsPanel - Configuration")

        from dashboard.ui.widgets.symbol_queue_table import SymbolQueueTable
        print("✓ SymbolQueueTable - Processing queue display")

        from dashboard.ui.widgets.log_viewer import LogViewer
        print("✓ LogViewer - Live logs")

        from dashboard.ui.widgets.api_usage_widget import APIUsageWidget
        print("✓ APIUsageWidget - Rate limit gauge")

        from dashboard.dialogs.company_selector_dialog import CompanySelectorDialog
        print("✓ CompanySelectorDialog - Company browser")

        from dashboard.ui.main_window import MainWindow
        print("✓ MainWindow - Application window")

        print("\n✅ Dashboard Components: PASSED")
        return True
    except Exception as e:
        print(f"\n❌ Dashboard Components: FAILED - {e}")
        import traceback
        traceback.print_exc()
        return False

def test_database_connection():
    """Test MongoDB connection"""
    print("\n" + "="*70)
    print("Testing Database Connection")
    print("="*70)

    try:
        from mongodb_storage import MongoDBStorage
        from config import settings

        storage = MongoDBStorage(
            uri=settings.mongodb_uri,
            db_name=settings.database_name
        )

        # Try to get collection count
        profiles = storage.get_all_profiles()
        profile_count = len(profiles)

        print(f"✓ MongoDB connected")
        print(f"✓ Profiles in database: {profile_count}")

        storage.close()
        print("\n✅ Database Connection: PASSED")
        return True
    except Exception as e:
        print(f"\n❌ Database Connection: FAILED - {e}")
        return False

def test_config():
    """Test configuration loading"""
    print("\n" + "="*70)
    print("Testing Configuration")
    print("="*70)

    try:
        from config import settings

        assert settings.eodhd_api_key, "EODHD API key not set"
        assert settings.mongodb_uri, "MongoDB URI not set"
        assert settings.database_name, "Database name not set"

        print(f"✓ EODHD API key: {'*' * 8}")
        print(f"✓ MongoDB URI: {settings.mongodb_uri}")
        print(f"✓ Database name: {settings.database_name}")
        print(f"✓ History years: {settings.max_history_years}")
        print(f"✓ API calls/min: {settings.api_calls_per_minute}")
        print(f"✓ API calls/day: {settings.api_calls_per_day}")

        print("\n✅ Configuration: PASSED")
        return True
    except Exception as e:
        print(f"\n❌ Configuration: FAILED - {e}")
        return False

def main():
    """Run all tests"""
    print("\n" + "="*70)
    print("Stock Market Minute Data Pipeline - v1.1.0 Stability Test")
    print("="*70)

    results = []

    # Run all tests
    results.append(("Core Modules", test_core_modules()))
    results.append(("Configuration", test_config()))
    results.append(("Database Connection", test_database_connection()))
    results.append(("Dashboard Components", test_dashboard()))

    # Summary
    print("\n" + "="*70)
    print("TEST SUMMARY")
    print("="*70)

    passed = sum(1 for _, result in results if result)
    total = len(results)

    for name, result in results:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{name:.<50} {status}")

    print(f"\nTotal: {passed}/{total} tests passed")

    if passed == total:
        print("\n🎉 ALL TESTS PASSED - PRODUCTION READY ✅")
        return 0
    else:
        print("\n⚠️  SOME TESTS FAILED - REVIEW REQUIRED")
        return 1

if __name__ == "__main__":
    sys.exit(main())

