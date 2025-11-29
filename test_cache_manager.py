#!/usr/bin/env python
"""Quick test of cache manager functionality"""
import sys
sys.path.insert(0, '/root/workspace/Minute_Data_Pipeline')

try:
    print("Testing cache system...")
    from dashboard.services.data_fetch_cache import get_data_cache
    
    print("✓ Cache import successful")
    cache = get_data_cache()
    print("✓ Cache initialized")
    
    stats = cache.get_stats()
    print(f"✓ Cache stats retrieved: {stats}")
    
    print("\n✅ ALL TESTS PASSED - Cache manager ready!")
    
except Exception as e:
    print(f"❌ ERROR: {e}")
    import traceback
    traceback.print_exc()

