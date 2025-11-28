import sys
import traceback

print("=" * 60)
print("Testing Dashboard Imports")
print("=" * 60)

try:
    print("\n1. Testing PyQt6...")
    import PyQt6
    print("   [OK] PyQt6 imported successfully")
except Exception as e:
    print(f"   [FAIL] PyQt6 import failed: {e}")
    traceback.print_exc()

try:
    print("\n2. Testing dashboard.ui.panels.control_panel...")
    from dashboard.ui.panels.control_panel import ControlPanel
    print("   [OK] ControlPanel imported successfully")
except Exception as e:
    print(f"   [FAIL] ControlPanel import failed: {e}")
    traceback.print_exc()

try:
    print("\n3. Testing dashboard.ui.panels.monitor_panel...")
    from dashboard.ui.panels.monitor_panel import MonitorPanel
    print("   [OK] MonitorPanel imported successfully")
except Exception as e:
    print(f"   [FAIL] MonitorPanel import failed: {e}")
    traceback.print_exc()

try:
    print("\n4. Testing dashboard.ui.main_window...")
    from dashboard.ui.main_window import MainWindow
    print("   [OK] MainWindow imported successfully")
except Exception as e:
    print(f"   [FAIL] MainWindow import failed: {e}")
    traceback.print_exc()

print("\n" + "=" * 60)
print("Import test completed")
print("=" * 60)

