"""
Quick Start Script - Run this after setup to test the pipeline
"""
from pipeline import MinuteDataPipeline
from loguru import logger
import sys

# Simple logger setup
logger.remove()
logger.add(sys.stderr, level="INFO")


def quick_start_demo():
    """
    Quick demonstration of the pipeline with a single symbol
    This uses mock/sample data if API key is not configured
    """
    print("\n" + "=" * 80)
    print("MINUTE DATA PIPELINE - QUICK START DEMO")
    print("=" * 80 + "\n")

    # Check if API key is configured
    from config import settings

    if not settings.eodhd_api_key:
        print("⚠️  WARNING: EODHD_API_KEY not configured in .env file")
        print("\nTo use real data:")
        print("1. Get an API key from https://eodhd.com/")
        print("2. Add it to your .env file: EODHD_API_KEY=your_key_here")
        print("\nFor now, showing feature engineering with sample data...\n")

        # Create sample data
        import pandas as pd
        import numpy as np
        from datetime import datetime, timedelta
        from feature_engineering import FeatureEngineer

        dates = pd.date_range(end=datetime.now(), periods=1000, freq='1min')
        df = pd.DataFrame({
            'datetime': dates,
            'open': np.random.uniform(180, 185, 1000),
            'high': np.random.uniform(185, 190, 1000),
            'low': np.random.uniform(175, 180, 1000),
            'close': np.random.uniform(180, 185, 1000),
            'volume': np.random.randint(10000, 100000, 1000)
        })

        print(f"✓ Created sample data with {len(df)} rows")

        # Process features
        fe = FeatureEngineer()
        features = fe.process_full_pipeline(df)

        print(f"\n📊 Feature Engineering Results:")
        print(f"   - Statistical Features: {len(features['statistical_features'])}")
        print(f"   - Time-Based Features: {len(features['time_features'])}")
        print(f"   - Microstructure Features: {len(features['microstructure_features'])}")

        # Show some features
        stats = features['statistical_features']
        print(f"\n📈 Sample Statistical Features:")
        print(f"   - Average Price: ${stats.get('price_mean', 0):.2f}")
        print(f"   - Price Volatility: {stats.get('price_std', 0):.4f}")
        print(f"   - Sharpe Ratio: {stats.get('sharpe_ratio', 0):.4f}")
        print(f"   - Price Skewness: {stats.get('price_skewness', 0):.4f}")
        print(f"   - Current Price: ${stats.get('current_price', 0):.2f}")

        print("\n✓ Feature engineering working correctly!")
        print("\n" + "=" * 80)

    else:
        print("✓ API Key configured! Running real data test...\n")

        try:
            pipeline = MinuteDataPipeline()

            print("📥 Processing AAPL with 5-minute intervals (faster for demo)...")
            print("   Date range: Last 7 days")
            print("   This may take 30-60 seconds...\n")

            from datetime import datetime, timedelta
            from_date = (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')
            to_date = datetime.now().strftime('%Y-%m-%d')

            success = pipeline.process_symbol(
                symbol='AAPL',
                exchange='US',
                interval='5m',  # 5-minute intervals for faster demo
                from_date=from_date,
                to_date=to_date,
                fetch_fundamentals=True
            )

            if success:
                print("\n✓ Successfully processed AAPL!")

                # Retrieve and display profile
                profile = pipeline.get_profile('AAPL')

                if profile:
                    print("\n" + "=" * 80)
                    print("📋 COMPANY PROFILE SUMMARY")
                    print("=" * 80)
                    print(f"\nCompany: {profile.get('company_name', 'N/A')}")
                    print(f"Sector: {profile.get('sector', 'N/A')}")
                    print(f"Industry: {profile.get('industry', 'N/A')}")
                    print(f"Data Points: {profile.get('data_points_count', 0):,}")

                    date_range = profile.get('data_date_range', {})
                    print(f"\nDate Range:")
                    print(f"  Start: {date_range.get('start', 'N/A')}")
                    print(f"  End: {date_range.get('end', 'N/A')}")

                    # Statistical Features
                    stats = profile.get('statistical_features', {})
                    print(f"\n📊 Statistical Features:")
                    print(f"  Average Price: ${stats.get('price_mean', 0):.2f}")
                    print(f"  Price Range: ${stats.get('price_min', 0):.2f} - ${stats.get('price_max', 0):.2f}")
                    print(f"  Volatility (Std Dev): {stats.get('price_std', 0):.4f}")
                    print(f"  Returns Mean: {stats.get('returns_mean', 0):.6f}")
                    print(f"  Sharpe Ratio: {stats.get('sharpe_ratio', 0):.4f}")

                    # Technical Indicators
                    tech = profile.get('technical_indicators', {})
                    print(f"\n📈 Technical Indicators (Latest Values):")
                    print(f"  SMA(20): ${tech.get('sma_20', 0):.2f}")
                    print(f"  SMA(50): ${tech.get('sma_50', 0):.2f}")
                    print(f"  RSI(14): {tech.get('rsi_14', 0):.2f}")
                    print(f"  MACD: {tech.get('macd', 0):.4f}")

                    # Performance Metrics
                    perf = profile.get('performance_metrics', {})
                    print(f"\n💰 Performance Metrics:")
                    print(f"  Total Return: {perf.get('total_return', 0):.2%}")
                    print(f"  Period High: ${perf.get('period_high', 0):.2f}")
                    print(f"  Period Low: ${perf.get('period_low', 0):.2f}")

                    # Risk Metrics
                    risk = profile.get('risk_metrics', {})
                    print(f"\n⚠️  Risk Metrics:")
                    print(f"  Max Drawdown: {risk.get('max_drawdown', 0):.2%}")
                    print(f"  VaR (95%): {risk.get('var_95', 0):.4f}")
                    print(f"  CVaR (95%): {risk.get('cvar_95', 0):.4f}")

                    # Advanced Sections Summary
                    adv_stats = profile.get('advanced_statistical', {})
                    multi_tf = profile.get('multi_timeframe', {})
                    quality = profile.get('quality_metrics', {})
                    labels = profile.get('labels', {})
                    tech_ext = profile.get('technical_extended_latest', {})

                    print(f"\n🔬 Advanced Statistical Features: {len(adv_stats)} items")
                    print(f"   Sample: returns_entropy={adv_stats.get('returns_entropy','N/A')} hurst_exponent={adv_stats.get('hurst_exponent','N/A')}")
                    print(f"\n🕒 Multi-Timeframe Keys: {len(multi_tf)}")
                    print(f"   Includes: {', '.join(list(multi_tf.keys())[:6])}{'...' if len(multi_tf)>6 else ''}")
                    print(f"\n✅ Data Quality Metrics: missing_total={profile.get('data_summary',{}).get('data_quality',{}).get('missing_values','N/A')} ADF_p={quality.get('adf_pvalue_returns','N/A')}")
                    print(f"\n🎯 Label Targets Available: {', '.join([k for k in labels.keys() if k.startswith('forward_return_')])}")
                    print(f"   Next Move Up/Down: {labels.get('next_move_up','N/A')}/{labels.get('next_move_down','N/A')}")
                    print(f"\n🧪 Extended Technical Latest: {', '.join(f'{k}={v:.4f}' for k,v in list(tech_ext.items())[:5])}")

                    print("\n" + "=" * 80)
                    print("✓ Profile stored in MongoDB successfully!")
                    print("=" * 80)
            else:
                print("\n✗ Failed to process AAPL")
                print("  Check your API key and internet connection")

            pipeline.close()

        except Exception as e:
            print(f"\n✗ Error: {e}")
            logger.error(f"Error in quick start: {e}", exc_info=True)

    print("\n📚 Next Steps:")
    print("   1. Check examples.py for more usage patterns")
    print("   2. Modify pipeline.py to process your symbols")
    print("   3. Review SETUP.md for detailed configuration")
    print("   4. Explore the MongoDB data using MongoDB Compass")
    print("\n" + "=" * 80 + "\n")


if __name__ == "__main__":
    try:
        quick_start_demo()
    except KeyboardInterrupt:
        print("\n\nDemo interrupted by user")
    except Exception as e:
        logger.error(f"Demo failed: {e}", exc_info=True)
        print(f"\n✗ Demo failed: {e}")
        print("  Check the logs for more details")
