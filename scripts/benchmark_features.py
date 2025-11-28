import time
import pandas as pd
import numpy as np
from feature_engineering import FeatureEngineer

sizes = [100, 1000, 5000, 10000]


def make_df(n):
    dt = pd.date_range('2025-01-01 09:30', periods=n, freq='1min')
    base = 100 + np.cumsum(np.random.normal(0, 0.05, n))
    df = pd.DataFrame({
        'datetime': dt,
        'open': base + np.random.uniform(-0.05,0.05,n),
        'high': base + np.random.uniform(0.01,0.2,n),
        'low': base - np.random.uniform(0.01,0.2,n),
        'close': base,
        'volume': np.random.randint(500,20000,n)
    })
    return df


def benchmark():
    fe = FeatureEngineer()
    results = []
    for n in sizes:
        df = make_df(n)
        start = time.time()
        _ = fe.process_full_pipeline(df)
        elapsed = time.time() - start
        results.append({'rows': n, 'seconds': elapsed, 'rows_per_sec': n/elapsed})
        print(f"{n:6d} rows -> {elapsed:.2f}s ({n/elapsed:.0f} rows/sec)")
    return pd.DataFrame(results)

if __name__ == '__main__':
    summary = benchmark()
    print(summary)

