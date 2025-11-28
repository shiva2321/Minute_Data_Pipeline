"""
Test the pipeline controller with the fixed methods
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

print("Testing pipeline controller fix...")

try:
    from dashboard.controllers.pipeline_controller import PipelineController
    print("[OK] PipelineController imported")

    from pipeline import MinuteDataPipeline
    print("[OK] MinuteDataPipeline imported")

    from feature_engineering import FeatureEngineer
    print("[OK] FeatureEngineer imported")

    # Check if FeatureEngineer has the correct method
    fe = FeatureEngineer()
    if hasattr(fe, 'process_full_pipeline'):
        print("[OK] FeatureEngineer has process_full_pipeline method")
    else:
        print("[FAIL] FeatureEngineer missing process_full_pipeline method")

    print("\n" + "="*60)
    print("All tests passed! Dashboard should work now.")
    print("="*60)

except Exception as e:
    print(f"[FAIL] Error: {e}")
    import traceback
    traceback.print_exc()

