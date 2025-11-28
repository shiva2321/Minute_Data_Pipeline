"""
Main pipeline orchestrator
"""
import sys
from typing import List, Optional
from datetime import datetime
import pandas as pd
from loguru import logger
from tqdm import tqdm

from data_fetcher import EODHDDataFetcher
from feature_engineering import FeatureEngineer
from mongodb_storage import MongoDBStorage
from config import settings


# Configure logger
logger.remove()
logger.add(
    sys.stderr,
    format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan> - <level>{message}</level>",
    level="INFO"
)
logger.add(
    "logs/pipeline_{time:YYYY-MM-DD}.log",
    rotation="1 day",
    retention="30 days",
    level="DEBUG"
)


class MinuteDataPipeline:
    """Main pipeline for fetching, processing, and storing minute data"""

    def __init__(self):
        """Initialize the pipeline components"""
        logger.info("Initializing Minute Data Pipeline")

        self.data_fetcher = EODHDDataFetcher()
        self.feature_engineer = FeatureEngineer()
        self.storage = MongoDBStorage()

        logger.info("Pipeline initialized successfully")

    def process_symbol(
        self,
        symbol: str,
        exchange: str = 'US',
        interval: str = '1m',
        from_date: Optional[str] = None,
        to_date: Optional[str] = None,
        fetch_fundamentals: bool = True
    ) -> bool:
        """
        Process a single symbol through the entire pipeline

        Args:
            symbol: Stock symbol
            exchange: Exchange code
            interval: Time interval
            from_date: Start date
            to_date: End date
            fetch_fundamentals: Whether to fetch fundamental data

        Returns:
            True if successful, False otherwise
        """
        logger.info(f"Processing {symbol}.{exchange}")

        try:
            # Step 1: Fetch minute data
            logger.info(f"Step 1: Fetching minute data for {symbol}")
            df = self.data_fetcher.fetch_intraday_data(
                symbol=symbol,
                interval=interval,
                from_date=from_date,
                to_date=to_date,
                exchange=exchange
            )

            if df.empty:
                logger.warning(f"No data available for {symbol}")
                return False

            logger.info(f"Fetched {len(df)} data points for {symbol}")

            # Step 2: Fetch fundamental data (optional)
            fundamental_data = {}
            if fetch_fundamentals:
                logger.info(f"Step 2: Fetching fundamental data for {symbol}")
                fundamental_data = self.data_fetcher.fetch_fundamental_data(symbol, exchange)

            # Step 3: Feature engineering
            logger.info(f"Step 3: Engineering features for {symbol}")
            features = self.feature_engineer.process_full_pipeline(df)

            # Step 4: Create company profile
            logger.info(f"Step 4: Creating company profile for {symbol}")
            profile = self.storage.create_company_profile(
                symbol=symbol,
                exchange=exchange,
                raw_data=df,
                features=features,
                fundamental_data=fundamental_data
            )

            # Step 5: Save to MongoDB
            logger.info(f"Step 5: Saving profile for {symbol} to MongoDB")
            success = self.storage.save_profile(profile)

            if success:
                logger.info(f"Successfully processed and saved {symbol}")
                return True
            else:
                logger.error(f"Failed to save profile for {symbol}")
                return False

        except Exception as e:
            logger.error(f"Error processing {symbol}: {e}", exc_info=True)
            return False

    def process_multiple_symbols(
        self,
        symbols: List[str],
        exchange: str = 'US',
        interval: str = '1m',
        from_date: Optional[str] = None,
        to_date: Optional[str] = None,
        fetch_fundamentals: bool = True
    ) -> dict:
        """
        Process multiple symbols through the pipeline

        Args:
            symbols: List of stock symbols
            exchange: Exchange code
            interval: Time interval
            from_date: Start date
            to_date: End date
            fetch_fundamentals: Whether to fetch fundamental data

        Returns:
            Dictionary with success and failure counts
        """
        logger.info(f"Processing {len(symbols)} symbols")

        results = {
            'successful': [],
            'failed': [],
            'total': len(symbols)
        }

        for symbol in tqdm(symbols, desc="Processing symbols"):
            success = self.process_symbol(
                symbol=symbol,
                exchange=exchange,
                interval=interval,
                from_date=from_date,
                to_date=to_date,
                fetch_fundamentals=fetch_fundamentals
            )

            if success:
                results['successful'].append(symbol)
            else:
                results['failed'].append(symbol)

        logger.info(f"Pipeline completed: {len(results['successful'])} successful, {len(results['failed'])} failed")

        return results

    def get_profile(self, symbol: str, exchange: str = 'US') -> Optional[dict]:
        """
        Retrieve a company profile from storage

        Args:
            symbol: Stock symbol
            exchange: Exchange code

        Returns:
            Company profile or None
        """
        return self.storage.get_profile(symbol, exchange)

    def get_all_profiles(self, limit: Optional[int] = None) -> List[dict]:
        """
        Retrieve all company profiles

        Args:
            limit: Maximum number of profiles to return

        Returns:
            List of company profiles
        """
        return self.storage.get_all_profiles(limit)

    def export_profile_to_dict(self, symbol: str, exchange: str = 'US') -> Optional[dict]:
        """
        Export a company profile as a dictionary

        Args:
            symbol: Stock symbol
            exchange: Exchange code

        Returns:
            Profile dictionary or None
        """
        profile = self.get_profile(symbol, exchange)
        if profile and '_id' in profile:
            profile['_id'] = str(profile['_id'])  # Convert ObjectId to string
        return profile

    def get_pipeline_stats(self) -> dict:
        """
        Get statistics about the pipeline

        Returns:
            Dictionary with pipeline statistics
        """
        all_profiles = self.get_all_profiles()

        stats = {
            'total_profiles': len(all_profiles),
            'last_run': datetime.utcnow().isoformat(),
            'symbols_tracked': [p['symbol'] for p in all_profiles],
        }

        if all_profiles:
            # Sector distribution
            sectors = {}
            for profile in all_profiles:
                sector = profile.get('sector', 'Unknown')
                sectors[sector] = sectors.get(sector, 0) + 1
            stats['sector_distribution'] = sectors

            # Last updated times
            updates = [p.get('last_updated') for p in all_profiles if 'last_updated' in p]
            if updates:
                stats['most_recent_update'] = max(updates).isoformat()
                stats['oldest_update'] = min(updates).isoformat()

        return stats

    def close(self):
        """Clean up resources"""
        logger.info("Closing pipeline")
        self.storage.close()

    def process_symbol_full_history(
        self,
        symbol: str,
        exchange: str = 'US',
        interval: str = '1m',
        start_year: Optional[int] = None,
        max_years: Optional[int] = None,
        chunk_days: Optional[int] = None,
        fetch_fundamentals: bool = True,
        incremental: bool = True
    ) -> bool:
        """Fetch and process full historical intraday data for a symbol.
        If incremental=True and existing profile found, only backfill earlier period.
        """
        try:
            existing = self.get_profile(symbol, exchange)
            if incremental and existing and existing.get('data_date_range', {}).get('start'):
                # Determine earliest stored date and backfill earlier only
                earliest = pd.to_datetime(existing['data_date_range']['start'])
                logger.info(f"Incremental backfill for {symbol} before {earliest}")
                # Move cursor earlier than earliest - one day to ensure overlap
                now = datetime.utcnow()
                max_years_eff = max_years or settings.max_history_years
                chunk_days_eff = chunk_days or settings.history_chunk_days
                # Build full history then slice earlier portion
                full_df = self.data_fetcher.fetch_full_history(symbol, exchange, interval, start_year=start_year, max_years=max_years_eff, chunk_days=chunk_days_eff)
                if full_df.empty:
                    logger.warning(f"No historical chunks retrieved for {symbol}")
                    return False
                earlier_df = full_df[full_df['datetime'] < earliest]
                if earlier_df.empty:
                    logger.info(f"No older data to backfill for {symbol}")
                    return True
                combined = pd.concat([earlier_df, self.data_fetcher.fetch_intraday_data(symbol, interval)], ignore_index=True)
                combined = combined.drop_duplicates(subset=['datetime']).sort_values('datetime')
                logger.info(f"Running feature engineering on combined {len(combined)} rows for {symbol}")
                features = self.feature_engineer.process_full_pipeline(combined)
                fundamentals = self.data_fetcher.fetch_fundamental_data(symbol, exchange) if fetch_fundamentals else {}
                profile = self.storage.create_company_profile(symbol, exchange, combined, features, fundamentals)
                saved = self.storage.save_profile(profile)
                return saved
            else:
                logger.info(f"Full history fetch for {symbol}")
                max_years_eff = max_years or settings.max_history_years
                chunk_days_eff = chunk_days or settings.history_chunk_days
                full_df = self.data_fetcher.fetch_full_history(symbol, exchange, interval, start_year=start_year, max_years=max_years_eff, chunk_days=chunk_days_eff)
                if full_df.empty:
                    logger.error(f"Failed to assemble history for {symbol}")
                    return False
                fundamentals = self.data_fetcher.fetch_fundamental_data(symbol, exchange) if fetch_fundamentals else {}
                features = self.feature_engineer.process_full_pipeline(full_df)
                profile = self.storage.create_company_profile(symbol, exchange, full_df, features, fundamentals)
                saved = self.storage.save_profile(profile)
                return saved
        except Exception as e:
            logger.error(f"Full history processing failed for {symbol}: {e}", exc_info=True)
            return False


def main():
    """Main entry point for the pipeline"""
    logger.info("=" * 80)
    logger.info("Starting Minute Data Pipeline")
    logger.info("=" * 80)

    # Initialize pipeline
    pipeline = MinuteDataPipeline()

    # Example: Process a few symbols
    symbols = ['AAPL', 'MSFT', 'GOOGL', 'TSLA', 'AMZN']

    logger.info(f"Processing symbols: {symbols}")

    results = pipeline.process_multiple_symbols(
        symbols=symbols,
        interval='1m',
        fetch_fundamentals=True
    )

    # Print results
    logger.info("=" * 80)
    logger.info("Pipeline Results:")
    logger.info(f"Total symbols processed: {results['total']}")
    logger.info(f"Successful: {len(results['successful'])}")
    logger.info(f"Failed: {len(results['failed'])}")

    if results['successful']:
        logger.info(f"Successful symbols: {', '.join(results['successful'])}")

    if results['failed']:
        logger.warning(f"Failed symbols: {', '.join(results['failed'])}")

    # Get pipeline stats
    stats = pipeline.get_pipeline_stats()
    logger.info("=" * 80)
    logger.info("Pipeline Statistics:")
    for key, value in stats.items():
        if key != 'symbols_tracked':  # Skip long list
            logger.info(f"{key}: {value}")

    logger.info("=" * 80)

    # Clean up
    pipeline.close()
    logger.info("Pipeline completed successfully")


if __name__ == "__main__":
    main()
