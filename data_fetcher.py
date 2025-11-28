"""
Data fetcher module for EODHD API
"""
import requests
from datetime import datetime, timedelta
from typing import Optional, Dict, List
import pandas as pd
from loguru import logger
import time
from config import settings
from utils.rate_limiter import AdaptiveRateLimiter
import logging


class EODHDDataFetcher:
    """Fetches historical minute-by-minute data from EODHD API"""

    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the data fetcher

        Args:
            api_key: EODHD API key (optional, will use settings if not provided)
        """
        self.api_key = api_key or settings.eodhd_api_key
        self.base_url = settings.eodhd_base_url
        self.session = requests.Session()
        self.rate_limiter = AdaptiveRateLimiter(settings.api_calls_per_minute, settings.api_calls_per_day)
        self.logger = logging.getLogger(__name__)

    def fetch_intraday_data(
        self,
        symbol: str,
        interval: str = '1m',
        from_date: Optional[str] = None,
        to_date: Optional[str] = None,
        exchange: str = 'US'
    ) -> pd.DataFrame:
        """
        Fetch intraday minute-by-minute data

        Args:
            symbol: Stock symbol (e.g., 'AAPL')
            interval: Time interval ('1m', '5m', '1h')
            from_date: Start date in 'YYYY-MM-DD' format
            to_date: End date in 'YYYY-MM-DD' format
            exchange: Exchange code (default: 'US')

        Returns:
            DataFrame with OHLCV data
        """
        if not from_date:
            from_date = (datetime.now() - timedelta(days=settings.data_fetch_interval_days)).strftime('%Y-%m-%d')
        if not to_date:
            to_date = datetime.now().strftime('%Y-%m-%d')

        url = f"{self.base_url}/intraday/{symbol}.{exchange}"

        base_params = {
            'api_token': self.api_key,
            'interval': interval,
            'fmt': 'json'
        }
        # Convert to unix timestamps (seconds) as per EODHD intraday spec
        try:
            from_ts = int(pd.to_datetime(from_date).timestamp())
            to_ts = int(pd.to_datetime(to_date).timestamp())
        except Exception:
            from_ts = int((datetime.now() - timedelta(days=settings.data_fetch_interval_days)).timestamp())
            to_ts = int(datetime.now().timestamp())
        ranged_params = {**base_params, 'from': from_ts, 'to': to_ts}

        def _request(params):
            response = self.session.get(url, params=params, timeout=30)
            response.raise_for_status()
            return response.json()

        try:
            logger.info(f"Fetching intraday data for {symbol} from {from_date} to {to_date}")
            try:
                data = _request(ranged_params)
            except requests.exceptions.HTTPError as http_err:
                status = getattr(http_err.response, 'status_code', None)
                if status == 422:
                    logger.warning(f"422 from EODHD with from/to range; retrying without date range for {symbol}")
                    # Retry without from/to to let API decide default recent window
                    data = _request(base_params)
                else:
                    raise

            if not data:
                logger.warning(f"No data returned for {symbol}; attempting narrower range")
                # Progressive backoff: try last 3 days, then last 1 day
                for days in (3, 1):
                    try:
                        narrow_from_ts = int((datetime.now() - timedelta(days=days)).timestamp())
                        narrow_to_ts = int(datetime.now().timestamp())
                        narrow_params = {**base_params,'from': narrow_from_ts,'to': narrow_to_ts}
                        data = _request(narrow_params)
                        if data:
                            logger.info(f"Fetched data for {symbol} with last {days} days")
                            break
                    except requests.exceptions.HTTPError as http_err:
                        status = getattr(http_err.response, 'status_code', None)
                        if status == 422:
                            logger.warning(f"Still 422 for {symbol} at {days} days; trying next fallback")
                            continue
                        else:
                            raise

            if not data:
                logger.warning(f"No data returned for {symbol} after fallbacks")
                return pd.DataFrame()

            # Convert to DataFrame
            df = pd.DataFrame(data)

            if df.empty:
                logger.warning(f"Empty dataframe for {symbol}")
                return df

            # Process the dataframe
            # Choose datetime-like column explicitly
            dt_col = None
            if 'datetime' in df.columns:
                dt_col = 'datetime'
            elif 'date' in df.columns:
                dt_col = 'date'
            elif 'timestamp' in df.columns:
                dt_col = 'timestamp'

            if dt_col is None:
                logger.warning(f"No datetime-like column found in response for {symbol}")
                return pd.DataFrame()

            df[dt_col] = pd.to_datetime(df[dt_col], errors='coerce')
            df = df.rename(columns={dt_col: 'datetime'})
            df = df.dropna(subset=['datetime']).sort_values('datetime').reset_index(drop=True)

            # Ensure numeric columns
            numeric_cols = ['open', 'high', 'low', 'close', 'volume']
            for col in numeric_cols:
                if col in df.columns:
                    df[col] = pd.to_numeric(df[col], errors='coerce')

            logger.info(f"Successfully fetched {len(df)} records for {symbol}")
            return df

        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching data for {symbol}: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error processing data for {symbol}: {e}")
            raise

    def fetch_intraday_with_retry(self, symbol: str, from_dt: datetime, to_dt: datetime, interval: str = '1m', exchange: str = 'US', max_retries: int = 3) -> pd.DataFrame:
        for attempt in range(max_retries):
            try:
                self.rate_limiter.wait_if_needed()
                url = f"{self.base_url}/intraday/{symbol}.{exchange}"
                params = {
                    'api_token': self.api_key,
                    'interval': interval,
                    'from': int(from_dt.timestamp()),
                    'to': int(to_dt.timestamp()),
                    'fmt': 'json'
                }
                resp = self.session.get(url, params=params, timeout=30)
                if resp.status_code == 429:
                    self.logger.warning(f"429 Rate limit for {symbol}; backing off")
                    self.rate_limiter.record_error(settings.initial_retry_delay, settings.max_retry_delay)
                    continue
                if resp.status_code == 404:
                    self.logger.warning(f"Symbol {symbol} not found")
                    return pd.DataFrame()
                if resp.status_code != 200:
                    self.logger.error(f"API error {resp.status_code}: {resp.text[:200]}")
                    self.rate_limiter.record_error(settings.initial_retry_delay, settings.max_retry_delay)
                    continue
                self.rate_limiter.record_call()
                data = resp.json()
                if not data:
                    return pd.DataFrame()
                df = pd.DataFrame(data)
                # Normalize
                dt_col = 'datetime' if 'datetime' in df.columns else ('date' if 'date' in df.columns else ('timestamp' if 'timestamp' in df.columns else None))
                if dt_col is None:
                    return pd.DataFrame()
                df[dt_col] = pd.to_datetime(df[dt_col], errors='coerce')
                df = df.rename(columns={dt_col: 'datetime'})
                for col in ['open','high','low','close','volume']:
                    if col in df.columns:
                        df[col] = pd.to_numeric(df[col], errors='coerce')
                return df.dropna(subset=['datetime']).sort_values('datetime').reset_index(drop=True)
            except requests.exceptions.Timeout:
                self.logger.warning(f"Timeout attempt {attempt+1}/{max_retries} for {symbol}")
                self.rate_limiter.record_error(settings.initial_retry_delay, settings.max_retry_delay)
            except Exception as e:
                self.logger.error(f"Unexpected error: {e}")
                self.rate_limiter.record_error(settings.initial_retry_delay, settings.max_retry_delay)
        return pd.DataFrame()

    def fetch_fundamental_data(self, symbol: str, exchange: str = 'US') -> Dict:
        """
        Fetch fundamental data for a company

        Args:
            symbol: Stock symbol
            exchange: Exchange code

        Returns:
            Dictionary with fundamental data
        """
        url = f"{self.base_url}/fundamentals/{symbol}.{exchange}"

        params = {
            'api_token': self.api_key,
            'fmt': 'json'
        }

        try:
            logger.info(f"Fetching fundamental data for {symbol}")
            response = self.session.get(url, params=params, timeout=30)
            response.raise_for_status()

            data = response.json()
            logger.info(f"Successfully fetched fundamental data for {symbol}")
            return data

        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching fundamental data for {symbol}: {e}")
            return {}

    def fetch_multiple_symbols(
        self,
        symbols: List[str],
        interval: str = '1m',
        from_date: Optional[str] = None,
        to_date: Optional[str] = None,
        exchange: str = 'US',
        delay: float = 0.5
    ) -> Dict[str, pd.DataFrame]:
        """
        Fetch data for multiple symbols with rate limiting

        Args:
            symbols: List of stock symbols
            interval: Time interval
            from_date: Start date
            to_date: End date
            exchange: Exchange code
            delay: Delay between requests in seconds

        Returns:
            Dictionary mapping symbols to DataFrames
        """
        results = {}

        for symbol in symbols:
            try:
                df = self.fetch_intraday_data(symbol, interval, from_date, to_date, exchange)
                results[symbol] = df
                time.sleep(delay)  # Rate limiting
            except Exception as e:
                logger.error(f"Failed to fetch data for {symbol}: {e}")
                results[symbol] = pd.DataFrame()

        return results

    def fetch_full_history(
        self,
        symbol: str,
        exchange: str = 'US',
        interval: str = '1m',
        start_year: Optional[int] = None,
        max_years: Optional[int] = None,
        chunk_days: Optional[int] = None
    ) -> pd.DataFrame:
        """Fetch as much historical intraday data as possible in chunks.
        EODHD intraday endpoint supports date ranges; we iterate backwards.
        Args:
            symbol: ticker
            exchange: exchange code
            interval: '1m','5m','1h'
            start_year: earliest year to attempt (default computed)
            max_years: cap on lookback years
            chunk_days: size of each backward fetch window
        Returns:
            Concatenated DataFrame of historical minute data.
        """
        if max_years is None:
            max_years = settings.max_history_years
        if chunk_days is None:
            chunk_days = settings.history_chunk_days
        now = datetime.now()
        if start_year is None:
            start_year = now.year - max_years
        end_cursor = now
        all_chunks: List[pd.DataFrame] = []
        consecutive_empty = 0
        total_chunks = 0
        start_time = datetime.now()
        while end_cursor.year >= start_year and consecutive_empty < 5:
            start_cursor = end_cursor - timedelta(days=chunk_days)
            from_date = start_cursor.strftime('%Y-%m-%d')
            to_date = end_cursor.strftime('%Y-%m-%d')
            try:
                df_chunk = self.fetch_intraday_with_retry(symbol, start_cursor, end_cursor, interval=interval, exchange=exchange)
                if df_chunk.empty:
                    logger.warning(f"No data for {symbol} in chunk {from_date} -> {to_date}")
                    consecutive_empty += 1
                else:
                    consecutive_empty = 0
                    all_chunks.append(df_chunk)
                    logger.info(f"Accumulated {sum(len(c) for c in all_chunks)} rows for {symbol}")
                    total_chunks += 1
            except Exception as e:
                logger.error(f"Chunk fetch failed for {symbol} {from_date}->{to_date}: {e}")
                consecutive_empty += 1
            end_cursor = start_cursor - timedelta(days=1)
        if not all_chunks:
            return pd.DataFrame()
        full = pd.concat(all_chunks, ignore_index=True).drop_duplicates(subset=['datetime']).sort_values('datetime').reset_index(drop=True)
        logger.info(f"Full history assembled for {symbol}: {len(full)} rows from {full['datetime'].min()} to {full['datetime'].max()}")
        duration = (datetime.now() - start_time).total_seconds()
        self.logger.info(f"Backfill duration {duration:.1f}s, chunks {total_chunks}, API calls today {self.rate_limiter.get_stats()['daily_calls']}")
        return full

    def __del__(self):
        """Close the session when the object is destroyed"""
        if hasattr(self, 'session'):
            self.session.close()
