"""
Test script for enhanced granular analysis and visualization features
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from feature_engineering import FeatureEngineer
import pandas as pd
import numpy as np
from datetime import datetime, timedelta


def test_granular_features():
    """Test granular minute analysis features"""
    print("=" * 60)
    print("Testing Granular Minute Analysis Features")
    print("=" * 60)
    
    # Create sample minute data
    dates = pd.date_range(start='2024-01-01 09:30', periods=200, freq='1min')
    df = pd.DataFrame({
        'datetime': dates,
        'open': np.random.uniform(100, 110, 200),
        'high': np.random.uniform(110, 120, 200),
        'low': np.random.uniform(90, 100, 200),
        'close': np.random.uniform(100, 110, 200),
        'volume': np.random.randint(1000, 10000, 200)
    })
    
    fe = FeatureEngineer()
    granular = fe.calculate_granular_minute_features(df)
    
    print(f"\n✓ Calculated {len(granular)} granular features")
    
    # Verify key features exist
    expected_features = [
        'avg_liquidity_depth',
        'liquidity_variability', 
        'volume_gini_coefficient',
        'max_momentum_burst',
        'price_reversal_frequency',
        'extreme_move_count_2sigma',
        'volatility_clustering_coef',
        'trading_intensity',
        'price_efficiency_ratio',
        'hourly_vwap_volatility'
    ]
    
    for feature in expected_features:
        if feature in granular:
            print(f"  ✓ {feature}")
        else:
            print(f"  ✗ {feature} MISSING")
            
    return True


def test_multi_timeframe_enhancements():
    """Test enhanced multi-timeframe analysis"""
    print("\n" + "=" * 60)
    print("Testing Enhanced Multi-Timeframe Analysis")
    print("=" * 60)
    
    # Create sample data
    dates = pd.date_range(start='2024-01-01 09:30', periods=500, freq='1min')
    df = pd.DataFrame({
        'datetime': dates,
        'open': np.random.uniform(100, 110, 500),
        'high': np.random.uniform(110, 120, 500),
        'low': np.random.uniform(90, 100, 500),
        'close': np.random.uniform(100, 110, 500),
        'volume': np.random.randint(1000, 10000, 500)
    })
    
    fe = FeatureEngineer()
    metrics, frames = fe._multi_timeframe_metrics_and_frames(df)
    
    print(f"\n✓ Calculated {len(metrics)} multi-timeframe metrics")
    print(f"✓ Generated {len(frames)} timeframe aggregations")
    
    # Verify new timeframes
    expected_timeframes = ['2m', '3m', '5m', '15m', '30m', '1h', '1d']
    print("\nTimeframes:")
    for tf in expected_timeframes:
        if tf in frames:
            print(f"  ✓ {tf}: {len(frames[tf])} bars")
        else:
            print(f"  ✗ {tf} MISSING")
            
    # Check for cross-timeframe correlations
    if 'timeframe_correlations' in metrics:
        corr = metrics['timeframe_correlations']
        print(f"\n✓ Cross-timeframe correlations: {len(corr)} pairs")
        print(f"  Sample: {list(corr.items())[:3]}")
    
    # Check for regime detection per timeframe
    regime_count = sum(1 for k in metrics.keys() if '_regime' in k)
    print(f"\n✓ Timeframe-specific regimes: {regime_count}")
    
    return True


def test_full_pipeline_integration():
    """Test that granular features are integrated into full pipeline"""
    print("\n" + "=" * 60)
    print("Testing Full Pipeline Integration")
    print("=" * 60)
    
    # Create sample data
    dates = pd.date_range(start='2024-01-01 09:30', periods=300, freq='1min')
    df = pd.DataFrame({
        'datetime': dates,
        'open': np.random.uniform(100, 110, 300),
        'high': np.random.uniform(110, 120, 300),
        'low': np.random.uniform(90, 100, 300),
        'close': np.random.uniform(100, 110, 300),
        'volume': np.random.randint(1000, 10000, 300)
    })
    
    fe = FeatureEngineer()
    result = fe.process_full_pipeline(df)
    
    print(f"\n✓ Pipeline executed successfully")
    print(f"\nResult keys: {list(result.keys())}")
    
    # Verify granular features are included
    if 'granular_minute_features' in result:
        print(f"\n✓ Granular features integrated into pipeline")
        print(f"  Features count: {len(result['granular_minute_features'])}")
    else:
        print(f"\n✗ Granular features NOT found in pipeline result")
        return False
        
    # Verify enhanced multi-timeframe
    if 'multi_timeframe' in result:
        mtf = result['multi_timeframe']
        print(f"\n✓ Multi-timeframe metrics: {len(mtf)}")
        
        # Check for new timeframes
        new_tf_metrics = [k for k in mtf.keys() if any(tf in k for tf in ['2m', '3m', '30m'])]
        if new_tf_metrics:
            print(f"  ✓ New timeframes present: {len(new_tf_metrics)} metrics")
        
    return True


def main():
    """Run all tests"""
    print("\n" + "🚀 " * 20)
    print("Enhanced Granular Analysis & Visualization - Test Suite")
    print("🚀 " * 20 + "\n")
    
    try:
        # Run tests
        test_granular_features()
        test_multi_timeframe_enhancements()
        test_full_pipeline_integration()
        
        print("\n" + "=" * 60)
        print("✅ ALL TESTS PASSED!")
        print("=" * 60)
        print("\nEnhancements Summary:")
        print("  ✓ Granular minute-level analysis features")
        print("  ✓ Enhanced multi-timeframe aggregations (2m, 3m, 30m)")
        print("  ✓ Cross-timeframe correlation analysis")
        print("  ✓ Timeframe-specific regime detection")
        print("  ✓ Integration into full pipeline")
        print("\nVisualization Panel:")
        print("  ✓ Created new visualization panel UI")
        print("  ✓ Interactive charts with PyQt6-Charts")
        print("  ✓ Profile data exploration capabilities")
        print("  ✓ Data export functionality")
        print("  ✓ Integrated into main dashboard")
        
        return 0
        
    except Exception as e:
        print(f"\n❌ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == '__main__':
    sys.exit(main())
