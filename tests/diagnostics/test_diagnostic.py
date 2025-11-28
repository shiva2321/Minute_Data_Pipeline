#!/usr/bin/env python
"""Quick diagnostic test"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

print("Testing imports...")

try:
    print("  1. Importing CacheStore...", end=" ")
    from dashboard.models import CacheStore
    print("✅")
except Exception as e:
    print(f"❌ {e}")
    sys.exit(1)

try:
    print("  2. Creating CacheStore...", end=" ")
    cache = CacheStore(':memory:')
    print("✅")
except Exception as e:
    print(f"❌ {e}")
    sys.exit(1)

try:
    print("  3. Testing API usage...", end=" ")
    cache.update_daily_api_calls(100)
    result = cache.get_daily_api_calls()
    assert result == 100
    print(f"✅ (got {result})")
except Exception as e:
    print(f"❌ {e}")
    sys.exit(1)

try:
    print("  4. Closing cache...", end=" ")
    cache.close()
    print("✅")
except Exception as e:
    print(f"❌ {e}")
    sys.exit(1)

print("\n✅ All imports and basic operations successful!")

