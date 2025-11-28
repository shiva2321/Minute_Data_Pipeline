#!/usr/bin/env python
"""
Integration Test - Verify Phase 1 initialization works
Tests CacheStore, APIUsageWidget, and basic component loading
"""
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

def test_cache_store():
    """Test CacheStore initialization"""
    print("Testing CacheStore initialization...")
    try:
        from dashboard.models import CacheStore
        cache = CacheStore(':memory:')  # In-memory for testing

        # Test API usage tracking
        cache.update_daily_api_calls(100)
        result = cache.get_daily_api_calls()
        assert result == 100, f"Expected 100, got {result}"

        cache.close()
        print("  ✅ CacheStore: PASS")
        return True
    except Exception as e:
        print(f"  ❌ CacheStore: FAIL - {e}")
        return False

def test_log_emailer():
    """Test LogEmailAlerter import"""
    print("Testing LogEmailAlerter import...")
    try:
        from dashboard.services import LogEmailAlerter
        print("  ✅ LogEmailAlerter: PASS")
        return True
    except Exception as e:
        print(f"  ❌ LogEmailAlerter: FAIL - {e}")
        return False

def test_metrics_calculator():
    """Test MetricsCalculator"""
    print("Testing MetricsCalculator...")
    try:
        from dashboard.services import MetricsCalculator
        calc = MetricsCalculator()
        calc.initialize(total_symbols=10)

        # Test basic calculation
        assert calc.calculate_progress_percent() == 0
        print("  ✅ MetricsCalculator: PASS")
        return True
    except Exception as e:
        print(f"  ❌ MetricsCalculator: FAIL - {e}")
        return False

def test_dialogs():
    """Test dialog imports"""
    print("Testing dialog imports...")
    try:
        from dashboard.dialogs import CompanySelectorDialog, ReprocessDialog
        print("  ✅ Dialogs: PASS")
        return True
    except Exception as e:
        print(f"  ❌ Dialogs: FAIL - {e}")
        return False

def test_enhanced_widgets():
    """Test enhanced widget imports"""
    print("Testing enhanced widgets...")
    try:
        from dashboard.ui.widgets import LogViewer, SymbolQueueTable, APIUsageWidget
        print("  ✅ Enhanced Widgets: PASS")
        return True
    except Exception as e:
        print(f"  ❌ Enhanced Widgets: FAIL - {e}")
        return False

def test_main_window_loading():
    """Test MainWindow with cache_store parameter"""
    print("Testing MainWindow initialization with cache_store...")
    try:
        from dashboard.models import CacheStore
        from dashboard.ui.main_window import MainWindow

        # Create cache
        cache = CacheStore(':memory:')

        # Verify MainWindow accepts cache_store
        # (Don't actually create window as it requires display)
        import inspect
        sig = inspect.signature(MainWindow.__init__)
        assert 'cache_store' in sig.parameters, "MainWindow missing cache_store parameter"

        cache.close()
        print("  ✅ MainWindow Integration: PASS")
        return True
    except Exception as e:
        print(f"  ❌ MainWindow Integration: FAIL - {e}")
        return False

def main():
    """Run all integration tests"""
    print("\n" + "="*70)
    print("DASHBOARD ENHANCEMENT - PHASE 1 INTEGRATION TEST")
    print("="*70 + "\n")

    tests = [
        test_cache_store,
        test_log_emailer,
        test_metrics_calculator,
        test_dialogs,
        test_enhanced_widgets,
        test_main_window_loading,
    ]

    results = []
    for test_func in tests:
        try:
            result = test_func()
            results.append(result)
        except Exception as e:
            print(f"Unexpected error in {test_func.__name__}: {e}")
            results.append(False)

    # Summary
    print("\n" + "="*70)
    passed = sum(results)
    total = len(results)

    if passed == total:
        print(f"✅ ALL TESTS PASSED ({passed}/{total})")
        print("="*70)
        print("\n🎉 Phase 1 Integration Successful!")
        print("\nNext Steps:")
        print("1. Review docs/IMPLEMENTATION_GUIDE.md")
        print("2. Connect MetricsCalculator to pipeline")
        print("3. Implement micro-stage worker updates")
        print("4. Test full end-to-end workflow")
        return 0
    else:
        print(f"❌ SOME TESTS FAILED ({passed}/{total} passed)")
        print("="*70)
        return 1

if __name__ == '__main__':
    sys.exit(main())

