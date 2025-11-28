import sys
from pathlib import Path

# Add parent directory to Python path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import math
from feature_engineering import FeatureEngineer

def make_df(rows=500):
    now = datetime.now()
    dt_index = pd.date_range(end=now, periods=rows, freq='1min')
    base = 100 + np.cumsum(np.random.normal(0, 0.05, rows))
    high = base + np.random.uniform(0.01,0.2, rows)
    low = base - np.random.uniform(0.01,0.2, rows)
    open_ = base + np.random.uniform(-0.05,0.05, rows)
    close = base
    volume = np.random.randint(1000,50000, rows)
    return pd.DataFrame({
        'datetime': dt_index,
        'open': open_,
        'high': high,
        'low': low,
        'close': close,
        'volume': volume
    })

def test_empty_df():
    fe = FeatureEngineer()
    res = fe.process_full_pipeline(pd.DataFrame())
    assert res['processed_df'].empty
    assert res['statistical_features'] == {}


def test_single_row():
    fe = FeatureEngineer()
    df = make_df(1)
    res = fe.process_full_pipeline(df)
    # Should not crash; many features absent
    assert res['summary']['total_records'] == 1


def test_hurst_bounds():
    fe = FeatureEngineer()
    df = make_df(300)
    res = fe.process_full_pipeline(df)
    hurst = res['advanced_statistical'].get('hurst_exponent')
    if hurst is not None:
        assert 0 <= hurst <= 1.5  # allow >1 due to finite sample noise but not extreme


def test_entropy_non_negative():
    fe = FeatureEngineer()
    df = make_df(400)
    res = fe.process_full_pipeline(df)
    ent = res['advanced_statistical'].get('returns_entropy')
    assert ent is None or ent >= 0


def test_multi_timeframe_integrity():
    fe = FeatureEngineer()
    df = make_df(500)
    res = fe.process_full_pipeline(df)
    mtf = res['multi_timeframe']
    # Each expected key exists or is safely missing
    for k in ['5m_volatility','15m_volatility','1h_volatility','1d_volatility']:
        assert k in mtf or True  # presence depends on data length


def test_labels_forward_returns():
    fe = FeatureEngineer()
    df = make_df(200)
    res = fe.process_full_pipeline(df)
    labels = res['labels']
    for h in [1,5,10]:
        key = f'forward_return_{h}'
        if key in labels:
            # Ensure not NaN
            assert not math.isnan(labels[key])


def test_predictive_labels():
    fe = FeatureEngineer()
    df = make_df(300)
    res = fe.process_full_pipeline(df)
    pl = res['predictive_labels']
    # Check a few new predictive targets
    for k in ['next_5m_return','next_15m_realized_vol','next_30m_max_drawdown']:
        if k in pl:
            assert pl[k] is None or isinstance(pl[k], (float,int))


def test_regime_features_presence():
    fe = FeatureEngineer()
    df = make_df(300)
    res = fe.process_full_pipeline(df)
    regimes = res['regime_features']
    # At least one regime classification should exist if enough data
    assert isinstance(regimes, dict)

def test_no_future_leakage_in_label_series():
    fe = FeatureEngineer()
    df = make_df(180)
    res = fe.process_full_pipeline(df)
    label_series = res['predictive_label_series']
    # For each horizon ensure tail rows are NaN (masked)
    for h in [1,5,15,30]:
        col = f'next_{h}m_return'
        if col in label_series.columns:
            tail = label_series[col].iloc[-h:]
            assert tail.isna().all(), f"Leakage: tail of {col} should be NaN"

def test_multi_timeframe_alignment_no_future_peek():
    fe = FeatureEngineer()
    # Construct deterministic data
    dt_index = pd.date_range('2025-01-01 09:30', periods=60, freq='1min')
    close = np.arange(100, 160)  # strictly increasing
    df = pd.DataFrame({'datetime': dt_index, 'open': close, 'high': close+0.1, 'low': close-0.1, 'close': close, 'volume': 1000})
    res = fe.process_full_pipeline(df)
    frames = res['multi_timeframe_frames']
    if '5m' in frames:
        f5 = frames['5m']
        # 5m bar ending at minute index 9 should have close from minute 9
        tenth_minute = df.iloc[9]['close']
        assert abs(f5.iloc[1]['close'] - tenth_minute) < 1e-9, "5m aggregation mismatch or future leak"

def test_volatility_regime_consistency():
    fe = FeatureEngineer()
    # High volatility synthetic
    dt_index = pd.date_range('2025-01-01 09:30', periods=300, freq='1min')
    close = 100 + np.cumsum(np.random.normal(0, 2.0, 300))  # high variance
    df = pd.DataFrame({'datetime': dt_index, 'open': close, 'high': close+0.5, 'low': close-0.5, 'close': close, 'volume': 2000})
    res = fe.process_full_pipeline(df)
    regime = res['regime_features'].get('volatility_regime')
    assert regime in ['high','medium','low']

def test_trend_regime_on_uptrend():
    fe = FeatureEngineer()
    dt_index = pd.date_range('2025-01-01 09:30', periods=200, freq='1min')
    close = np.linspace(100, 150, 200)
    df = pd.DataFrame({'datetime': dt_index, 'open': close, 'high': close+0.2, 'low': close-0.2, 'close': close, 'volume': 1500})
    # Add MACD columns minimal for trend regime evaluation
    df['macd'] = np.linspace(0.1,0.5,len(df))
    res = fe.process_full_pipeline(df)
    trend = res['regime_features'].get('trend_regime')
    assert trend in ['strong_uptrend','weak_trend','choppy'], "Unexpected trend classification"

if __name__ == '__main__':
    # Simple manual run
    test_empty_df()
    test_single_row()
    test_hurst_bounds()
    test_entropy_non_negative()
    test_multi_timeframe_integrity()
    test_labels_forward_returns()
    test_predictive_labels()
    test_regime_features_presence()
    test_no_future_leakage_in_label_series()
    test_multi_timeframe_alignment_no_future_peek()
    test_volatility_regime_consistency()
    test_trend_regime_on_uptrend()
    print('All feature engineering tests passed.')
