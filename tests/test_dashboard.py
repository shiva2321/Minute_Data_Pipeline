"""
Quick test to verify dashboard components can be imported
"""
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

print("Testing dashboard imports...")

try:
    # Test Qt imports
    from PyQt6.QtWidgets import QApplication
    from PyQt6.QtCore import Qt
    print("✓ PyQt6 imports successful")

    # Test theme
    from dashboard.utils.theme import load_stylesheet
    print("✓ Theme module loaded")

    # Test signals
    from dashboard.utils.qt_signals import PipelineSignals, DatabaseSignals
    print("✓ Qt signals loaded")

    # Test controllers
    from dashboard.controllers.queue_manager import QueueManager
    from dashboard.controllers.database_controller import DatabaseController
    print("✓ Controllers loaded")

    # Test widgets
    from dashboard.ui.widgets.log_viewer import LogViewer
    from dashboard.ui.widgets.api_usage_widget import APIUsageWidget
    from dashboard.ui.widgets.symbol_queue_table import SymbolQueueTable
    print("✓ Widgets loaded")

    # Test panels
    from dashboard.ui.panels.control_panel import ControlPanel
    from dashboard.ui.panels.monitor_panel import MonitorPanel
    from dashboard.ui.panels.profile_browser import ProfileBrowser
    from dashboard.ui.panels.settings_panel import SettingsPanel
    print("✓ Panels loaded")

    # Test main window
    from dashboard.ui.main_window import MainWindow
    print("✓ Main window loaded")

    print("\n✅ All imports successful!")
    print("Dashboard is ready to launch.")
    print("\nRun: python dashboard/main.py")

except ImportError as e:
    print(f"\n❌ Import error: {e}")
    print("\nPlease install missing dependencies:")
    print("  pip install -r requirements.txt")
    sys.exit(1)
except Exception as e:
    print(f"\n[ERROR] {e}")
    sys.exit(1)

