#!/usr/bin/env python
"""Quick test to verify the forward_return fix"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

import math
import pandas as pd
import numpy as np
from feature_engineering import FeatureEngineer

def make_df(n):
    return pd.DataFrame({
        'datetime': pd.date_range(periods=n, freq='1min'),
        'open': np.random.uniform(100, 110, n),
        'high': np.random.uniform(110, 115, n),
        'low': np.random.uniform(95, 100, n),
        'close': np.random.uniform(100, 110, n),
        'volume': np.random.randint(1000, 10000, n)
    })

print("Testing forward_return labels fix...")
fe = FeatureEngineer()
df = make_df(200)
res = fe.process_full_pipeline(df)
labels = res['labels']

print(f"Labels: {labels}")

# Check for NaN values
has_nan = False
for h in [1, 5, 10]:
    key = f'forward_return_{h}'
    if key in labels:
        value = labels[key]
        is_nan = math.isnan(value) if isinstance(value, float) else False
        print(f"  {key}: {value} (NaN: {is_nan})")
        if is_nan:
            has_nan = True
            print(f"    ❌ FAILED: NaN found in {key}")
        else:
            print(f"    ✅ PASSED: {key} is valid")

if not has_nan:
    print("\n✅ ALL TESTS PASSED - No NaN values found!")
    sys.exit(0)
else:
    print("\n❌ TESTS FAILED - NaN values still present")
    sys.exit(1)

