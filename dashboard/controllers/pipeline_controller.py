"""
Pipeline Controller - True Parallel Processing
Each worker processes symbols independently with its own rate limiter
Optimized for Ryzen 5 7600 (6 cores, 12 threads)
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from PyQt6.QtCore import QThread, QTimer
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import List, Dict, Callable
import time
from datetime import datetime

from config import settings
from pipeline import MinuteDataPipeline
from utils.rate_limiter import AdaptiveRateLimiter
from dashboard.utils.qt_signals import PipelineSignals


class PipelineController(QThread):
    """
    Manages truly parallel processing of symbols
    Each worker has independent rate limiter and processes symbols end-to-end
    Updates metrics every 10 seconds
    """

    def __init__(self, symbols: List[str], config: Dict, parent=None):
        super().__init__(parent)

        self.symbols = symbols
        self.config = config
        self.signals = PipelineSignals()

        self.is_paused = False
        self.is_stopped = False

        # Statistics
        self.stats = {
            'total': len(symbols),
            'completed': 0,
            'failed': 0,
            'skipped': 0,
            'start_time': None,
            'end_time': None
        }

        # Thread pool
        max_workers = config.get('max_workers', 10)
        self.executor = ThreadPoolExecutor(max_workers=max_workers)

        # Calculate per-worker rate limits (independent for each worker)
        total_minute_limit = config.get('api_calls_per_minute', 80)
        total_daily_limit = config.get('api_calls_per_day', 95000)

        # Distribute limits across workers with safety margin
        self.per_worker_minute_limit = max(1, int(total_minute_limit / max_workers * 0.9))
        self.per_worker_daily_limit = max(10, int(total_daily_limit / max_workers * 0.9))

        # Metrics update timer (10 seconds)
        self.last_update_time = time.time()
        self.update_interval = 10  # Update every 10 seconds

        # Aggregated API stats from all workers
        self.total_api_calls = 0
        self.total_daily_calls = 0

    def run(self):
        """Main processing loop - truly parallel execution"""
        self.stats['start_time'] = time.time()

        self.signals.log_message.emit('INFO', f'Starting pipeline for {len(self.symbols)} symbols with {self.executor._max_workers} workers')
        self.signals.log_message.emit('INFO', f'Per-worker rate limits: {self.per_worker_minute_limit}/min, {self.per_worker_daily_limit}/day')
        self.signals.pipeline_started.emit(len(self.symbols))

        # Submit all symbols to thread pool at once
        # Each thread processes one symbol completely independently
        futures = {}
        for symbol in self.symbols:
            if self.is_stopped:
                break

            future = self.executor.submit(
                self._process_symbol_worker,
                symbol,
                self.config
            )
            futures[future] = symbol

            # Emit symbol started
            self.signals.symbol_started.emit(symbol)
            self.signals.log_message.emit('INFO', f'Starting {symbol}')

        # Monitor completion with periodic updates
        for future in as_completed(futures):
            symbol = futures[future]

            if self.is_stopped:
                break

            try:
                result = future.result()

                if result['status'] == 'success':
                    self.stats['completed'] += 1
                    self.signals.symbol_completed.emit(symbol, result['profile'])
                    self.signals.log_message.emit('SUCCESS', f'{symbol} completed successfully')
                else:
                    self.stats['failed'] += 1
                    error_msg = result.get('error', 'Unknown error')
                    self.signals.symbol_failed.emit(symbol, error_msg)
                    self.signals.log_message.emit('ERROR', f'{symbol}: {error_msg}')

                # Aggregate API stats
                if 'api_calls' in result:
                    self.total_api_calls += result['api_calls']
                    self.total_daily_calls += result.get('daily_calls', 0)

            except Exception as e:
                self.stats['failed'] += 1
                error_msg = str(e)
                self.signals.symbol_failed.emit(symbol, error_msg)
                self.signals.log_message.emit('ERROR', f'{symbol}: {error_msg}')

            # Update metrics every 10 seconds
            current_time = time.time()
            if current_time - self.last_update_time >= self.update_interval:
                self._emit_progress_update()
                self.last_update_time = current_time

        # Final update
        self.stats['end_time'] = time.time()
        duration = self.stats['end_time'] - self.stats['start_time']

        summary = {
            'completed': self.stats['completed'],
            'failed': self.stats['failed'],
            'skipped': self.stats['skipped'],
            'duration': duration,
            'total_api_calls': self.total_api_calls
        }

        self.signals.pipeline_completed.emit(summary)
        self.signals.log_message.emit(
            'SUCCESS',
            f'Pipeline completed in {duration:.1f}s: {self.stats["completed"]} succeeded, '
            f'{self.stats["failed"]} failed, {self.stats["skipped"]} skipped'
        )

    def _emit_progress_update(self):
        """Emit progress updates for ETA and metrics"""
        if self.stats['start_time']:
            elapsed = time.time() - self.stats['start_time']
            completed = self.stats['completed'] + self.stats['failed']

            if completed > 0:
                avg_time_per_symbol = elapsed / completed
                remaining = self.stats['total'] - completed
                eta_seconds = int(avg_time_per_symbol * remaining)

                self.signals.eta_updated.emit(eta_seconds)

            # Emit aggregated API stats
            api_stats = {
                'minute_calls': 0,  # Can't track per-minute across workers easily
                'daily_calls': self.total_daily_calls,
                'daily_remaining': self.config.get('api_calls_per_day', 95000) - self.total_daily_calls
            }
            self.signals.api_stats_updated.emit(api_stats)

    def _process_symbol_worker(self, symbol: str, config: Dict) -> Dict:
        """
        Worker function - processes ONE symbol completely from start to finish
        This runs in a separate thread with its own independent rate limiter

        Args:
            symbol: Ticker symbol
            config: Configuration dictionary

        Returns:
            Result dictionary with status, profile, and API stats
        """
        api_calls_used = 0

        try:
            # Create independent pipeline for this worker
            pipeline = MinuteDataPipeline()

            # Create independent rate limiter for this worker
            worker_rate_limiter = AdaptiveRateLimiter(
                calls_per_minute=self.per_worker_minute_limit,
                calls_per_day=self.per_worker_daily_limit
            )

            # Inject the independent rate limiter
            pipeline.data_fetcher.rate_limiter = worker_rate_limiter

            # Progress callback
            def progress_callback(status: str, progress: int, **kwargs):
                self.signals.symbol_progress.emit(symbol, status, progress)
                self.signals.log_message.emit('INFO', f'{symbol}: {status} ({progress}%)')

                # Get API stats from this worker's rate limiter
                stats = worker_rate_limiter.get_stats()
                nonlocal api_calls_used
                api_calls_used = stats.get('daily_calls', 0)

                # Update with worker-specific data
                kwargs_with_data = {
                    'data_points': kwargs.get('data_points', 0),
                    'api_calls': api_calls_used,
                    **kwargs
                }
                self.signals.symbol_progress.emit(symbol, status, progress)

            # Log start
            self.signals.log_message.emit('INFO', f'Processing {symbol}...')
            progress_callback('Starting', 0)

            # Check mode
            mode = config.get('mode', 'incremental')
            existing_profile = pipeline.storage.get_profile(symbol)

            if mode == 'incremental' and existing_profile:
                self.signals.log_message.emit('INFO', f'{symbol}: Updating existing profile')
                profile = self._incremental_update(pipeline, symbol, existing_profile, progress_callback)
            else:
                self.signals.log_message.emit('INFO', f'{symbol}: Creating new profile')
                max_years = config.get('max_years', 2)
                profile = self._full_backfill(pipeline, symbol, max_years, progress_callback)

            # Get final API stats
            final_stats = worker_rate_limiter.get_stats()

            return {
                'status': 'success',
                'profile': profile,
                'api_calls': final_stats.get('daily_calls', 0),
                'daily_calls': final_stats.get('daily_calls', 0)
            }

        except Exception as e:
            self.signals.log_message.emit('ERROR', f'{symbol}: {str(e)}')
            return {
                'status': 'failed',
                'error': str(e),
                'api_calls': api_calls_used
            }

    def _full_backfill(
        self,
        pipeline: MinuteDataPipeline,
        symbol: str,
        max_years: int,
        progress_callback: Callable
    ) -> Dict:
        """Full historical backfill with 30-day chunks"""
        progress_callback('Fetching history', 10)

        # Fetch full history (uses 30-day chunks internally in data_fetcher)
        df = pipeline.data_fetcher.fetch_full_history(
            symbol=symbol,
            max_years=max_years
        )

        if df.empty:
            raise ValueError("No data retrieved")

        progress_callback('Engineering features', 50, data_points=len(df))

        # Calculate all features
        features = pipeline.feature_engineer.process_full_pipeline(df)

        progress_callback('Creating profile', 70)

        # Create company profile
        profile = pipeline.storage.create_company_profile(
            symbol=symbol,
            exchange='US',
            raw_data=df,
            features=features,
            fundamental_data={}
        )

        progress_callback('Storing profile', 90)

        # Save to database
        pipeline.storage.save_profile(profile)

        progress_callback('Complete', 100)

        return profile

    def _incremental_update(
        self,
        pipeline: MinuteDataPipeline,
        symbol: str,
        existing_profile: Dict,
        progress_callback: Callable
    ) -> Dict:
        """Incremental update of existing profile"""
        progress_callback('Fetching new data', 10)

        # Get last update date
        last_date = existing_profile.get('data_date_range', {}).get('end')

        # Fetch new data
        df = pipeline.data_fetcher.fetch_intraday_data(
            symbol=symbol,
            from_date=last_date
        )

        if df.empty:
            progress_callback('No new data', 100)
            return existing_profile

        progress_callback('Engineering features', 50, data_points=len(df))

        # Recalculate features
        features = pipeline.feature_engineer.process_full_pipeline(df)

        progress_callback('Creating profile', 70)

        # Create updated profile
        profile = pipeline.storage.create_company_profile(
            symbol=symbol,
            exchange='US',
            raw_data=df,
            features=features,
            fundamental_data={}
        )

        progress_callback('Storing profile', 90)

        # Update in database
        pipeline.storage.update_profile(symbol, profile)

        progress_callback('Complete', 100)

        return profile

    def pause(self):
        """Pause processing"""
        self.is_paused = True
        self.signals.pipeline_paused.emit()
        self.signals.log_message.emit('WARNING', 'Pipeline paused')

    def stop(self):
        """Stop all processing"""
        self.is_stopped = True
        self.executor.shutdown(wait=False, cancel_futures=True)
        self.signals.pipeline_stopped.emit()
        self.signals.log_message.emit('ERROR', 'Pipeline stopped')

