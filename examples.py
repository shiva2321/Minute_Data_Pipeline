"""
Example usage and testing script for the Minute Data Pipeline
"""
from pipeline import MinuteDataPipeline
from loguru import logger
import json


def example_single_symbol():
    """Example: Process a single symbol"""
    logger.info("Example 1: Processing a single symbol")

    pipeline = MinuteDataPipeline()

    # Process Apple stock
    success = pipeline.process_symbol(
        symbol='AAPL',
        exchange='US',
        interval='1m',
        from_date='2024-11-01',
        to_date='2024-11-27',
        fetch_fundamentals=True
    )

    if success:
        # Retrieve and display the profile
        profile = pipeline.export_profile_to_dict('AAPL')
        if profile:
            logger.info(f"Profile created for AAPL")
            logger.info(f"Company: {profile.get('company_name')}")
            logger.info(f"Sector: {profile.get('sector')}")
            logger.info(f"Data points: {profile.get('data_points_count')}")
            logger.info(f"Statistical features: {len(profile.get('statistical_features', {}))}")

    pipeline.close()


def example_multiple_symbols():
    """Example: Process multiple symbols"""
    logger.info("Example 2: Processing multiple symbols")

    pipeline = MinuteDataPipeline()

    # Tech stocks
    tech_symbols = ['AAPL', 'MSFT', 'GOOGL', 'NVDA', 'META']

    results = pipeline.process_multiple_symbols(
        symbols=tech_symbols,
        interval='5m',  # 5-minute intervals for faster processing
        fetch_fundamentals=True
    )

    logger.info(f"Processed {results['total']} symbols")
    logger.info(f"Success: {len(results['successful'])}")
    logger.info(f"Failed: {len(results['failed'])}")

    pipeline.close()


def example_retrieve_and_analyze():
    """Example: Retrieve and analyze stored profiles"""
    logger.info("Example 3: Retrieving and analyzing profiles")

    pipeline = MinuteDataPipeline()

    # Get a specific profile
    profile = pipeline.get_profile('AAPL')

    if profile:
        logger.info("AAPL Profile Summary:")
        logger.info(f"  Company: {profile.get('company_name')}")
        logger.info(f"  Sector: {profile.get('sector')}")
        logger.info(f"  Last Updated: {profile.get('last_updated')}")

        # Statistical features
        stats = profile.get('statistical_features', {})
        logger.info(f"  Average Price: ${stats.get('price_mean', 0):.2f}")
        logger.info(f"  Volatility: {stats.get('price_std', 0):.4f}")
        logger.info(f"  Sharpe Ratio: {stats.get('sharpe_ratio', 0):.4f}")

        # Technical indicators
        tech = profile.get('technical_indicators', {})
        logger.info(f"  RSI(14): {tech.get('rsi_14', 0):.2f}")
        logger.info(f"  SMA(50): ${tech.get('sma_50', 0):.2f}")

        # Risk metrics
        risk = profile.get('risk_metrics', {})
        logger.info(f"  Max Drawdown: {risk.get('max_drawdown', 0):.2%}")
        logger.info(f"  VaR(95%): {risk.get('var_95', 0):.4f}")

    # Get all profiles
    all_profiles = pipeline.get_all_profiles(limit=10)
    logger.info(f"\nTotal profiles in database: {len(all_profiles)}")

    pipeline.close()


def example_custom_date_range():
    """Example: Process with custom date range"""
    logger.info("Example 4: Custom date range processing")

    pipeline = MinuteDataPipeline()

    # Process last week's data
    success = pipeline.process_symbol(
        symbol='TSLA',
        exchange='US',
        interval='1m',
        from_date='2024-11-20',
        to_date='2024-11-27',
        fetch_fundamentals=False  # Skip fundamentals for faster processing
    )

    if success:
        profile = pipeline.get_profile('TSLA')
        if profile:
            date_range = profile.get('data_date_range', {})
            logger.info(f"Data range: {date_range.get('start')} to {date_range.get('end')}")
            logger.info(f"Total data points: {profile.get('data_points_count')}")

    pipeline.close()


def example_export_profile():
    """Example: Export profile to JSON"""
    logger.info("Example 5: Exporting profile to JSON")

    pipeline = MinuteDataPipeline()

    profile = pipeline.export_profile_to_dict('AAPL')

    if profile:
        # Save to JSON file
        with open('aapl_profile.json', 'w') as f:
            json.dump(profile, f, indent=2, default=str)

        logger.info("Profile exported to aapl_profile.json")

    pipeline.close()


def example_pipeline_stats():
    """Example: Get pipeline statistics"""
    logger.info("Example 6: Pipeline statistics")

    pipeline = MinuteDataPipeline()

    stats = pipeline.get_pipeline_stats()

    logger.info("Pipeline Statistics:")
    logger.info(f"  Total profiles: {stats.get('total_profiles')}")
    logger.info(f"  Symbols tracked: {stats.get('symbols_tracked')}")

    sector_dist = stats.get('sector_distribution', {})
    if sector_dist:
        logger.info("  Sector distribution:")
        for sector, count in sector_dist.items():
            logger.info(f"    {sector}: {count}")

    pipeline.close()


if __name__ == "__main__":
    # Run examples
    print("\n" + "=" * 80)
    print("Minute Data Pipeline - Examples")
    print("=" * 80 + "\n")

    # Uncomment the examples you want to run:

    # example_single_symbol()
    # example_multiple_symbols()
    # example_retrieve_and_analyze()
    # example_custom_date_range()
    # example_export_profile()
    # example_pipeline_stats()

    logger.info("Check the examples above and uncomment them to run")

