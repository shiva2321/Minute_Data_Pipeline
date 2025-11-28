"""
Dashboard Import and Component Test Suite
Tests all dashboard components and dependencies
Combines test_dashboard.py and test_imports.py
"""
import sys
import traceback
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

def test_core_dependencies():
    """Test core Qt and Python dependencies"""
    print("\n" + "=" * 60)
    print("Testing Core Dependencies")
    print("=" * 60)

    try:
        print("\n1. Testing PyQt6...")
        import PyQt6
        from PyQt6.QtWidgets import QApplication
        from PyQt6.QtCore import Qt
        print("   ✓ PyQt6 imported successfully")
        return True
    except Exception as e:
        print(f"   ✗ PyQt6 import failed: {e}")
        traceback.print_exc()
        return False

def test_dashboard_utils():
    """Test dashboard utility modules"""
    print("\n" + "=" * 60)
    print("Testing Dashboard Utils")
    print("=" * 60)

    try:
        print("\n1. Testing theme module...")
        from dashboard.utils.theme import load_stylesheet
        print("   ✓ Theme module loaded")

        print("\n2. Testing Qt signals...")
        from dashboard.utils.qt_signals import PipelineSignals, DatabaseSignals
        print("   ✓ Qt signals loaded")

        return True
    except Exception as e:
        print(f"   ✗ Utils test failed: {e}")
        traceback.print_exc()
        return False

def test_dashboard_controllers():
    """Test dashboard controllers"""
    print("\n" + "=" * 60)
    print("Testing Dashboard Controllers")
    print("=" * 60)

    try:
        print("\n1. Testing queue manager...")
        from dashboard.controllers.queue_manager import QueueManager
        print("   ✓ Queue manager loaded")

        print("\n2. Testing database controller...")
        from dashboard.controllers.database_controller import DatabaseController
        print("   ✓ Database controller loaded")

        print("\n3. Testing pipeline controller...")
        from dashboard.controllers.pipeline_controller import PipelineController
        print("   ✓ Pipeline controller loaded")

        return True
    except Exception as e:
        print(f"   ✗ Controllers test failed: {e}")
        traceback.print_exc()
        return False

def test_dashboard_ui_components():
    """Test dashboard UI components"""
    print("\n" + "=" * 60)
    print("Testing Dashboard UI Components")
    print("=" * 60)

    try:
        print("\n[Widgets]")
        print("  1. Testing log viewer...", end=" ")
        from dashboard.ui.widgets.log_viewer import LogViewer
        print("✓")

        print("  2. Testing API usage widget...", end=" ")
        from dashboard.ui.widgets.api_usage_widget import APIUsageWidget
        print("✓")

        print("  3. Testing symbol queue table...", end=" ")
        from dashboard.ui.widgets.symbol_queue_table import SymbolQueueTable
        print("✓")

        print("\n[Panels]")
        print("  1. Testing control panel...", end=" ")
        from dashboard.ui.panels.control_panel import ControlPanel
        print("✓")

        print("  2. Testing monitor panel...", end=" ")
        from dashboard.ui.panels.monitor_panel import MonitorPanel
        print("✓")

        print("  3. Testing profile browser...", end=" ")
        from dashboard.ui.panels.profile_browser import ProfileBrowser
        print("✓")

        print("  4. Testing settings panel...", end=" ")
        from dashboard.ui.panels.settings_panel import SettingsPanel
        print("✓")

        print("\n[Main Window]")
        print("  1. Testing main window...", end=" ")
        from dashboard.ui.main_window import MainWindow
        print("✓")

        return True
    except Exception as e:
        print(f"   ✗ UI components test failed: {e}")
        traceback.print_exc()
        return False

def main():
    """Run all dashboard tests"""
    print("\n" + "=" * 70)
    print("DASHBOARD IMPORT AND COMPONENT TEST SUITE")
    print("=" * 70)

    results = []

    # Run all tests
    results.append(("Core Dependencies", test_core_dependencies()))
    results.append(("Dashboard Utils", test_dashboard_utils()))
    results.append(("Dashboard Controllers", test_dashboard_controllers()))
    results.append(("Dashboard UI Components", test_dashboard_ui_components()))

    # Print summary
    print("\n" + "=" * 70)
    print("TEST SUMMARY")
    print("=" * 70)

    all_passed = True
    for test_name, passed in results:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{test_name:<35} {status}")
        if not passed:
            all_passed = False

    print("\n" + "=" * 70)
    if all_passed:
        print("✅ ALL TESTS PASSED - Dashboard is ready to launch!")
        print("\nRun: python dashboard/main.py")
        return 0
    else:
        print("❌ SOME TESTS FAILED - Please install missing dependencies:")
        print("   pip install -r requirements.txt")
        return 1

if __name__ == "__main__":
    sys.exit(main())

