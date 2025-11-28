"""
Simple test script to verify the pipeline setup
"""
import sys
from loguru import logger

# Configure simple logger for tests
logger.remove()
logger.add(sys.stderr, level="INFO")


def test_imports():
    """Test if all modules can be imported"""
    logger.info("Testing imports...")
    try:
        from config import settings
        logger.info("✓ config imported successfully")

        from data_fetcher import EODHDDataFetcher
        logger.info("✓ data_fetcher imported successfully")

        from feature_engineering import FeatureEngineer
        logger.info("✓ feature_engineering imported successfully")

        from mongodb_storage import MongoDBStorage
        logger.info("✓ mongodb_storage imported successfully")

        from pipeline import MinuteDataPipeline
        logger.info("✓ pipeline imported successfully")

        return True
    except Exception as e:
        logger.error(f"✗ Import failed: {e}")
        return False


def test_config():
    """Test configuration loading"""
    logger.info("\nTesting configuration...")
    try:
        from config import settings

        logger.info(f"EODHD Base URL: {settings.eodhd_base_url}")
        logger.info(f"MongoDB URI: {settings.mongodb_uri}")
        logger.info(f"MongoDB Database: {settings.mongodb_database}")
        logger.info(f"Data fetch interval: {settings.data_fetch_interval_days} days")

        if not settings.eodhd_api_key:
            logger.warning("⚠ EODHD_API_KEY not set in .env file")
        else:
            logger.info(f"✓ EODHD API Key configured (length: {len(settings.eodhd_api_key)})")

        return True
    except Exception as e:
        logger.error(f"✗ Configuration test failed: {e}")
        return False


def test_data_structures():
    """Test basic data structure creation"""
    logger.info("\nTesting data structures...")
    try:
        import pandas as pd
        import numpy as np
        from datetime import datetime, timedelta

        # Create sample data
        dates = pd.date_range(end=datetime.now(), periods=100, freq='1min')
        df = pd.DataFrame({
            'datetime': dates,
            'open': np.random.uniform(100, 110, 100),
            'high': np.random.uniform(110, 115, 100),
            'low': np.random.uniform(95, 100, 100),
            'close': np.random.uniform(100, 110, 100),
            'volume': np.random.randint(1000, 10000, 100)
        })

        logger.info(f"✓ Created sample DataFrame with {len(df)} rows")

        # Test feature engineering
        from feature_engineering import FeatureEngineer
        fe = FeatureEngineer()

        result = fe.process_full_pipeline(df)
        logger.info(f"✓ Feature engineering: {len(result['statistical_features'])} statistical features")
        logger.info(f"✓ Feature engineering: {len(result['time_features'])} time-based features")
        logger.info(f"✓ Feature engineering: {len(result['microstructure_features'])} microstructure features")

        return True
    except Exception as e:
        logger.error(f"✗ Data structure test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_mongodb_connection():
    """Test MongoDB connection (optional)"""
    logger.info("\nTesting MongoDB connection...")
    try:
        from mongodb_storage import MongoDBStorage

        storage = MongoDBStorage()
        logger.info("✓ MongoDB connection successful")
        storage.close()
        return True
    except Exception as e:
        logger.warning(f"⚠ MongoDB connection failed: {e}")
        logger.warning("  This is optional if MongoDB is not yet set up")
        return False


def run_all_tests():
    """Run all tests"""
    logger.info("=" * 80)
    logger.info("Running Pipeline Tests")
    logger.info("=" * 80)

    results = {
        'imports': test_imports(),
        'config': test_config(),
        'data_structures': test_data_structures(),
        'mongodb': test_mongodb_connection()
    }

    logger.info("\n" + "=" * 80)
    logger.info("Test Results Summary")
    logger.info("=" * 80)

    for test_name, result in results.items():
        status = "✓ PASSED" if result else "✗ FAILED"
        logger.info(f"{test_name.upper()}: {status}")

    total_passed = sum(results.values())
    total_tests = len(results)

    logger.info("=" * 80)
    logger.info(f"Total: {total_passed}/{total_tests} tests passed")
    logger.info("=" * 80)

    if results['imports'] and results['config'] and results['data_structures']:
        logger.info("\n✓ Core functionality is working!")
        logger.info("You can now:")
        logger.info("  1. Set your EODHD_API_KEY in .env file")
        logger.info("  2. Ensure MongoDB is running (optional for testing)")
        logger.info("  3. Run examples.py to see usage examples")
        logger.info("  4. Run pipeline.py to process stocks")
    else:
        logger.error("\n✗ Some core tests failed. Please check the errors above.")

    return all([results['imports'], results['config'], results['data_structures']])


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)

