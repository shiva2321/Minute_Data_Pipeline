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
from dashboard.services import MetricsCalculator


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

        # Initialize metrics calculator
        self.metrics_calc = MetricsCalculator()

        # Aggregated API stats from all workers
        self.total_api_calls = 0
        self.total_daily_calls = 0

        # Track start times for duration
        self.symbol_start_times = {}

        # Cooperative control events
        from threading import Event, Lock
        self._pause_event = Event()  # when set => paused (global)
        self._cancel_event = Event()  # when set => cancel operations (global)

        # Per-symbol control
        self.symbol_control = {}  # symbol -> {'paused': Event, 'cancelled': Event, 'status': str, 'was_paused': bool}
        self.symbol_lock = Lock()
        for symbol in symbols:
            self.symbol_control[symbol] = {
                'paused': Event(),
                'cancelled': Event(),
                'status': 'queued',
                'was_paused': False,  # Track if symbol is currently paused
                'future': None
            }

    def run(self):
        """Main processing loop - truly parallel execution"""
        self.stats['start_time'] = time.time()

        # Initialize metrics calculator
        self.metrics_calc.initialize(len(self.symbols), self.stats['start_time'])

        self.signals.log_message.emit('INFO', f'Starting pipeline for {len(self.symbols)} symbols with {self.executor._max_workers} workers')
        self.signals.log_message.emit('INFO', f'Per-worker rate limits: {self.per_worker_minute_limit}/min, {self.per_worker_daily_limit}/day')
        self.signals.pipeline_started.emit(len(self.symbols))

        # Submit all symbols to thread pool at once
        # Each thread processes one symbol completely independently
        futures = {}
        for symbol in self.symbols:
            if self.is_stopped:
                break

            self.symbol_start_times[symbol] = time.time()

            future = self.executor.submit(
                self._process_symbol_worker,
                symbol,
                self.config
            )
            futures[future] = symbol

            # Track symbol start time for metrics
            self.metrics_calc.mark_symbol_started(symbol, time.time())

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
                    # Mark completion in metrics
                    self.metrics_calc.mark_symbol_completed(symbol)
                    with self.symbol_lock:
                        self.symbol_control[symbol]['status'] = 'completed'
                    self.signals.symbol_completed.emit(symbol, result['profile'])
                    self.signals.log_message.emit('SUCCESS', f'{symbol} completed successfully')
                else:
                    self.stats['failed'] += 1
                    error_msg = result.get('error', 'Unknown error')
                    with self.symbol_lock:
                        self.symbol_control[symbol]['status'] = 'failed'
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
        start_time_val = self.stats.get('start_time') or self.metrics_calc.start_time or time.time()
        duration = self.stats['end_time'] - start_time_val if start_time_val else 0.0

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
        """Emit progress updates for ETA and metrics using MetricsCalculator"""
        # Determine processing count as total - completed - failed
        processing_count = max(0, self.stats.get('total', 0) - self.stats.get('completed', 0) - self.stats.get('failed', 0))

        # Get metrics from calculator
        metrics_stats = self.metrics_calc.get_summary_stats(processing_count)
        eta_seconds = metrics_stats.get('eta_seconds', 0) or 0

        # Emit ETA signal
        self.signals.eta_updated.emit(int(eta_seconds))

        # Emit metrics signal with comprehensive stats
        metrics_data = {
            'progress_percent': metrics_stats.get('progress_percent', 0),
            'completed': metrics_stats.get('completed', 0),
            'remaining': metrics_stats.get('remaining', 0),
            'processing': processing_count,
            'eta_seconds': eta_seconds,
            'eta_string': metrics_stats.get('eta_string', 'Calculating...'),
            'throughput': metrics_stats.get('throughput_symbols_per_minute', 0),
            'elapsed': metrics_stats.get('elapsed_seconds', 0)
        }
        self.signals.metrics_updated.emit(metrics_data)

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

            # Inject cooperative events
            pipeline.data_fetcher.pause_event = self._pause_event
            pipeline.data_fetcher.cancel_event = self._cancel_event
            # Inject per-symbol control events
            pipeline.data_fetcher.symbol_pause_event = self.symbol_control[symbol]['paused']
            pipeline.data_fetcher.symbol_cancel_event = self.symbol_control[symbol]['cancelled']

            # Update status to running
            with self.symbol_lock:
                self.symbol_control[symbol]['status'] = 'running'

            # Progress callback with micro-stage updates
            def progress_callback(status: str, progress: int, micro_stage: str = '-', data_points: int = 0):
                # Gather API stats
                stats = worker_rate_limiter.get_stats()
                api_used = stats.get('daily_calls', 0)
                duration_seconds = time.time() - self.symbol_start_times[symbol]

                # Check if paused
                is_paused = self.symbol_control[symbol]['paused'].is_set()

                # Log the update
                if micro_stage and micro_stage != '-':
                    self.signals.log_message.emit('INFO', f'{symbol}: {status} - {micro_stage} ({progress}%)')
                else:
                    self.signals.log_message.emit('INFO', f'{symbol}: {status} ({progress}%)')

                # Emit positional args with pause state
                self.signals.symbol_progress.emit(symbol, status, int(progress), micro_stage or '-', int(data_points), int(api_used), float(duration_seconds), is_paused)

            # Log start
            self.signals.log_message.emit('INFO', f'Processing {symbol}...')
            progress_callback('Starting', 0, micro_stage='Initialization')

            # Check mode
            mode = config.get('mode', 'incremental')
            existing_profile = pipeline.storage.get_profile(symbol)

            if mode == 'incremental' and existing_profile:
                self.signals.log_message.emit('INFO', f'{symbol}: Updating existing profile')
                profile = self._incremental_update(pipeline, symbol, existing_profile, progress_callback)
            else:
                self.signals.log_message.emit('INFO', f'{symbol}: Creating new profile')
                max_years = config.get('max_years', 2)
                # max_years can be None when "All Available" is selected - this is handled in _full_backfill
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
        """
        Full backfill of historical data with micro-stage updates

        Args:
            pipeline: MinuteDataPipeline instance
            symbol: Ticker symbol
            max_years: Number of years to fetch (None means all available since establishment)
            progress_callback: Callback for progress updates

        Returns:
            Company profile dictionary
        """
        from datetime import datetime, timedelta
        import time

        start_time = time.time()

        # Calculate date range
        end_date = datetime.now()

        # Handle None for max_years (All Available) - fetch from establishment date
        if max_years is None:
            self.signals.log_message.emit('INFO', f'{symbol}: Fetching establishment date for all available data')
            progress_callback('Initializing', 5, micro_stage='Fetching company info')

            ipo_date = None
            date_source = None

            try:
                # OPTION 1: Try EODHD fundamental data first
                self.signals.log_message.emit('INFO', f'{symbol}: Attempting to fetch IPO date from EODHD...')
                fundamental_data = pipeline.data_fetcher.fetch_fundamental_data(symbol, exchange='US')

                # Try to extract IPO date or founding date
                ipo_date = None

                # Check General section for IPO date
                if fundamental_data.get('General', {}).get('IPODate'):
                    ipo_date_str = fundamental_data['General']['IPODate']
                    try:
                        ipo_date = datetime.strptime(ipo_date_str, '%Y-%m-%d')
                        date_source = 'EODHD IPO date'
                        self.signals.log_message.emit('SUCCESS', f'{symbol}: ✓ Found IPO date from EODHD: {ipo_date_str}')
                    except:
                        pass

                # If no IPO date, check for founding date or other date fields
                if not ipo_date and fundamental_data.get('General', {}).get('FoundingDate'):
                    founding_date_str = fundamental_data['General']['FoundingDate']
                    try:
                        ipo_date = datetime.strptime(founding_date_str, '%Y-%m-%d')
                        date_source = 'EODHD founding date'
                        self.signals.log_message.emit('SUCCESS', f'{symbol}: ✓ Found founding date from EODHD: {founding_date_str}')
                    except:
                        pass

            except Exception as e:
                self.signals.log_message.emit('WARNING', f'{symbol}: EODHD fundamental data unavailable: {str(e)}')

            # OPTION 2: Try yfinance as fallback if EODHD didn't work
            if not ipo_date:
                try:
                    import yfinance as yf
                    self.signals.log_message.emit('INFO', f'{symbol}: Attempting to fetch IPO date from yfinance (fallback)...')

                    ticker = yf.Ticker(symbol)
                    info = ticker.info

                    # Try to get firstTradeDateEpochUtc (most reliable for IPO date)
                    if info.get('firstTradeDateEpochUtc'):
                        ipo_timestamp = info['firstTradeDateEpochUtc']
                        ipo_date = datetime.fromtimestamp(ipo_timestamp)
                        date_source = 'yfinance first trade date'
                        self.signals.log_message.emit('SUCCESS', f'{symbol}: ✓ Found first trade date from yfinance: {ipo_date.strftime("%Y-%m-%d")}')

                    # Fallback to ipoDate field if available
                    elif info.get('ipoDate'):
                        ipo_date_str = info['ipoDate']
                        try:
                            ipo_date = datetime.strptime(ipo_date_str, '%Y-%m-%d')
                            date_source = 'yfinance IPO date'
                            self.signals.log_message.emit('SUCCESS', f'{symbol}: ✓ Found IPO date from yfinance: {ipo_date_str}')
                        except:
                            pass

                except ImportError:
                    self.signals.log_message.emit('WARNING', f'{symbol}: yfinance not installed, skipping fallback')
                except Exception as e:
                    self.signals.log_message.emit('WARNING', f'{symbol}: yfinance fallback failed: {str(e)}')

            # Calculate years or use default
            if ipo_date:
                # Calculate years since establishment
                years_since_establishment = (end_date - ipo_date).days / 365.25
                max_years = max(1, int(years_since_establishment))  # At least 1 year
                self.signals.log_message.emit('INFO', f'{symbol}: ✓ OPTION SELECTED: Using {max_years} years of history from {date_source} (since {ipo_date.strftime("%Y-%m-%d")})')
                progress_callback('Initializing', 8, micro_stage=f'Using {max_years}yr from {ipo_date.year}')
            else:
                # OPTION 3: Default to 10 years
                max_years = 10
                self.signals.log_message.emit('WARNING', f'{symbol}: ✗ OPTION SELECTED: No establishment date found from EODHD or yfinance, using {max_years} years as DEFAULT')
                progress_callback('Initializing', 8, micro_stage=f'Default {max_years}yr (no IPO date)')

        start_date = end_date - timedelta(days=365 * max_years)

        # Estimate number of batches (30-day chunks)
        total_days = (end_date - start_date).days
        batch_days = 30
        total_batches = (total_days // batch_days) + 1

        # Fetch data in chunks with micro-stage updates
        all_data = []
        for batch_num in range(total_batches):
            batch_start = start_date + timedelta(days=batch_num * batch_days)
            batch_end = min(batch_start + timedelta(days=batch_days), end_date)

            # Calculate progress
            progress = int((batch_num / max(1,total_batches)) * 45)
            micro_stage = f'Fetch batch {batch_num+1}/{total_batches}'
            progress_callback('Fetching', progress, micro_stage=micro_stage)

            # Fetch this batch
            df_batch = pipeline.data_fetcher.fetch_intraday_data(
                symbol=symbol,
                from_date=batch_start.strftime('%Y-%m-%d'),
                to_date=batch_end.strftime('%Y-%m-%d')
            )

            if not df_batch.empty:
                all_data.append(df_batch)

        # Combine all data
        if not all_data:
            raise ValueError(f"No data retrieved for {symbol}")

        import pandas as pd
        df = pd.concat(all_data, ignore_index=True).drop_duplicates().reset_index(drop=True)

        # Engineering features with micro-stage updates
        total_features = 200  # Approximate
        progress_callback('Engineering', 50, micro_stage='Starting feature pipeline', data_points=len(df))

        # Calculate all features with periodic updates
        features = pipeline.feature_engineer.process_full_pipeline(df)

        progress_callback('Engineering', 65, micro_stage='Finalizing features', data_points=len(df))
        progress_callback('Creating', 70, micro_stage='Building profile object')

        # Create company profile
        profile = pipeline.storage.create_company_profile(
            symbol=symbol,
            exchange='US',
            raw_data=df,
            features=features,
            fundamental_data={}
        )

        progress_callback('Storing', 90, micro_stage='Writing to MongoDB')

        # Save to database
        pipeline.storage.save_profile(profile)

        progress_callback('Complete', 100, micro_stage='Done')

        return profile

    def _incremental_update(
        self,
        pipeline: MinuteDataPipeline,
        symbol: str,
        existing_profile: Dict,
        progress_callback: Callable
    ) -> Dict:
        """Incremental update of existing profile"""
        progress_callback('Fetching', 10, micro_stage='Incremental new data')

        # Get last update date
        last_date = existing_profile.get('data_date_range', {}).get('end')

        # Fetch new data
        df = pipeline.data_fetcher.fetch_intraday_data(
            symbol=symbol,
            from_date=last_date
        )

        if df.empty:
            progress_callback('Complete', 100, micro_stage='No new data')
            return existing_profile

        progress_callback('Engineering', 50, micro_stage='Recomputing features', data_points=len(df))

        # Recalculate features
        features = pipeline.feature_engineer.process_full_pipeline(df)

        progress_callback('Creating', 70, micro_stage='Merging profile')

        # Create updated profile
        profile = pipeline.storage.create_company_profile(
            symbol=symbol,
            exchange='US',
            raw_data=df,
            features=features,
            fundamental_data={}
        )

        progress_callback('Storing', 90, micro_stage='Updating MongoDB')

        # Update in database
        pipeline.storage.update_profile(symbol, profile)

        progress_callback('Complete', 100, micro_stage='Done')

        return profile

    # ==================== GLOBAL PIPELINE CONTROL ====================

    def pause(self):
        """Pause all processing - workers will block before/after API calls"""
        self.is_paused = True
        # Set pause event so fetchers pause cooperatively
        self._pause_event.set()
        self.signals.pipeline_paused.emit()
        self.signals.log_message.emit('WARNING', 'Pipeline paused - all workers pausing between API calls')

    def resume(self):
        """Resume all processing after pause"""
        self.is_paused = False
        self._pause_event.clear()
        self.signals.log_message.emit('INFO', 'Pipeline resumed')

    def stop(self):
        """Stop all processing immediately"""
        self.is_stopped = True
        # Trigger cooperative cancel; in-flight requests will raise and exit
        self._cancel_event.set()
        self._pause_event.clear()
        self.signals.log_message.emit('ERROR', 'Pipeline stopped - terminating all workers')
        try:
            self.executor.shutdown(wait=False, cancel_futures=True)
        except:
            pass
        self.signals.pipeline_stopped.emit()

    def clear(self):
        """Clear the queue and stop processing"""
        self.is_stopped = True
        self.signals.log_message.emit('INFO', 'Clearing pipeline queue')

        self._cancel_event.set()
        self._pause_event.clear()

        # Stop executor
        try:
            self.executor.shutdown(wait=False, cancel_futures=True)
        except:
            pass
        
        # Reset stats
        self.stats = {
            'total': 0,
            'completed': 0,
            'failed': 0,
            'skipped': 0,
            'start_time': None,
            'end_time': None
        }
        
        self.signals.pipeline_cleared.emit()
        self.signals.pipeline_stopped.emit()
        self.signals.log_message.emit('INFO', 'Pipeline cleared')

    # ==================== PER-SYMBOL CONTROL ====================

    def pause_symbol(self, symbol: str):
        """Pause a specific symbol's processing"""
        if symbol not in self.symbol_control:
            return
        with self.symbol_lock:
            self.symbol_control[symbol]['paused'].set()
            self.symbol_control[symbol]['was_paused'] = True
        self.signals.log_message.emit('WARNING', f'⏸ {symbol}: NOW PAUSED (waiting for resume)')

    def resume_symbol(self, symbol: str):
        """Resume a specific symbol's processing"""
        if symbol not in self.symbol_control:
            return
        with self.symbol_lock:
            self.symbol_control[symbol]['paused'].clear()
            self.symbol_control[symbol]['was_paused'] = False
        self.signals.log_message.emit('INFO', f'▶ {symbol}: RESUMED (continuing processing)')

    def cancel_symbol(self, symbol: str):
        """Cancel a specific symbol's processing"""
        if symbol not in self.symbol_control:
            return
        with self.symbol_lock:
            self.symbol_control[symbol]['cancelled'].set()
        self.signals.log_message.emit('WARNING', f'{symbol}: Cancelled')

    def skip_symbol(self, symbol: str):
        """Skip a symbol - remove from queue"""
        if symbol not in self.symbol_control:
            return
        with self.symbol_lock:
            self.symbol_control[symbol]['cancelled'].set()
            self.symbol_control[symbol]['status'] = 'skipped'
        self.stats['skipped'] += 1
        self.signals.log_message.emit('INFO', f'{symbol}: Skipped by user')

    def get_symbol_status(self, symbol: str) -> str:
        """Get current status of a symbol"""
        if symbol not in self.symbol_control:
            return 'unknown'
        with self.symbol_lock:
            return self.symbol_control[symbol]['status']

    def is_symbol_paused(self, symbol: str) -> bool:
        """Check if symbol is currently paused"""
        if symbol not in self.symbol_control:
            return False
        with self.symbol_lock:
            return self.symbol_control[symbol]['paused'].is_set()

    def get_all_statuses(self) -> Dict[str, str]:
        """Get status of all symbols"""
        with self.symbol_lock:
            return {symbol: info['status'] for symbol, info in self.symbol_control.items()}
