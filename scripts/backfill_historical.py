import argparse
import logging
from datetime import datetime
from pathlib import Path
import json

from data_fetcher import EODHDDataFetcher
from pipeline import MinuteDataPipeline
from config import settings

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(settings.backfill_log_path),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


def backfill_symbols(symbols, mode='incremental', max_years=None, chunk_days=None):
    pipeline = MinuteDataPipeline()
    fetcher = pipeline.data_fetcher
    storage = pipeline.storage

    results = {
        'started_at': datetime.now().isoformat(),
        'symbols': {},
        'summary': {
            'total': len(symbols),
            'success': 0,
            'failed': 0,
            'skipped': 0
        }
    }

    for idx, symbol in enumerate(symbols, 1):
        logger.info("\n" + ('='*60))
        logger.info(f"Processing {symbol} ({idx}/{len(symbols)})")
        logger.info(('='*60))
        try:
            existing = storage.get_profile(symbol)
            if mode == 'incremental' and existing and existing.get('backfill_metadata', {}).get('history_complete'):
                logger.info(f"Skipping {symbol} - already backfilled")
                results['symbols'][symbol] = {'status': 'skipped', 'reason': 'already_complete'}
                results['summary']['skipped'] += 1
                continue
            start = datetime.now()
            success = pipeline.process_symbol_full_history(
                symbol=symbol,
                exchange='US',
                interval='1m',
                start_year=None,
                max_years=max_years or settings.max_history_years,
                chunk_days=chunk_days or settings.history_chunk_days,
                fetch_fundamentals=True,
                incremental=(mode=='incremental')
            )
            duration = (datetime.now() - start).total_seconds()
            stats = fetcher.rate_limiter.get_stats()
            profile = storage.get_profile(symbol)
            if success and profile:
                backfill_info = {
                    'complete': True,
                    'total_rows': profile.get('data_points_count', 0),
                    'date_range': profile.get('data_date_range', {}),
                    'api_calls': stats['daily_calls'],
                    'duration': duration
                }
                if settings.store_backfill_metadata:
                    storage.save_profile_with_backfill_metadata(profile, backfill_info)
                results['symbols'][symbol] = {
                    'status': 'success',
                    'data_points': profile.get('data_points_count', 0),
                    'date_range': profile.get('data_date_range', {})
                }
                results['summary']['success'] += 1
                logger.info(f"✓ {symbol} completed successfully")
            else:
                results['symbols'][symbol] = {'status': 'failed', 'reason': 'no_data'}
                results['summary']['failed'] += 1
                logger.warning(f"✗ {symbol} failed - no data returned")
        except Exception as e:
            logger.error(f"✗ {symbol} failed with error: {e}", exc_info=True)
            results['symbols'][symbol] = {'status': 'failed', 'reason': str(e)}
            results['summary']['failed'] += 1
        stats = fetcher.rate_limiter.get_stats()
        logger.info(f"API usage: {stats['daily_calls']} calls, {stats['daily_remaining']} remaining")
        if stats['daily_remaining'] < 1000:
            logger.warning("Approaching daily API limit - consider stopping")
    results['completed_at'] = datetime.now().isoformat()
    results_path = Path('logs') / f"backfill_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    results_path.parent.mkdir(exist_ok=True)
    with open(results_path, 'w') as f:
        json.dump(results, f, indent=2)
    logger.info('\n' + ('='*60))
    logger.info("BACKFILL SUMMARY")
    logger.info(('='*60))
    logger.info(f"Total symbols: {results['summary']['total']}")
    logger.info(f"Success: {results['summary']['success']}")
    logger.info(f"Failed: {results['summary']['failed']}")
    logger.info(f"Skipped: {results['summary']['skipped']}")
    logger.info(f"Results saved to: {results_path}")
    pipeline.close()
    return results


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Backfill historical intraday data')
    parser.add_argument('--symbols', nargs='+', help='List of symbols (e.g., AAPL MSFT GOOGL)')
    parser.add_argument('--file', help='Path to file with symbols (one per line)')
    parser.add_argument('--mode', choices=['full', 'incremental'], default='incremental', help='Backfill mode')
    parser.add_argument('--years', type=int, default=None, help='Maximum years of history to fetch')
    parser.add_argument('--chunk', type=int, default=None, help='Days per API call')
    args = parser.parse_args()
    if args.file:
        with open(args.file) as f:
            symbols = [line.strip() for line in f if line.strip()]
    elif args.symbols:
        symbols = args.symbols
    else:
        symbols = ['GEVO']
    logger.info(f"Starting backfill for {len(symbols)} symbols in '{args.mode}' mode")
    backfill_symbols(symbols, mode=args.mode, max_years=args.years, chunk_days=args.chunk)

