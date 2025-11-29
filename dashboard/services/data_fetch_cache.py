"""
Data Fetch Cache System
Caches fetched market data for 24 hours, up to 50MB
Prevents redundant API calls and speeds up re-runs
"""
import os
import json
import pickle
import hashlib
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional, Dict, Tuple
import pandas as pd
from loguru import logger

class DataFetchCache:
    """
    Caches raw market data from EODHD API by date range

    Features:
    - 30-day cache TTL (default)
    - 1GB max storage (10-15 symbols)
    - Per-symbol, per-daterange caching
    - Store complete date ranges (not individual batches)
    - Auto-cleanup after 30 days
    - Cross-session persistence
    """

    def __init__(self, cache_dir: str = None, max_size_mb: int = 2048, ttl_hours: int = 720):
        """
        Initialize data cache

        Args:
            cache_dir: Directory to store cache (default: ~/.pipeline_data_cache)
            max_size_mb: Maximum cache size in MB (default: 2GB = 2048 MB - supports 10-15 symbols)
            ttl_hours: Time to live in hours (default: 720 = 30 days)
        """
        # Use user home directory for cache
        if cache_dir is None:
            cache_dir = os.path.join(os.path.expanduser('~'), '.pipeline_data_cache')

        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)

        self.max_size_bytes = max_size_mb * 1024 * 1024
        self.ttl_hours = ttl_hours
        self.metadata_file = self.cache_dir / 'cache_metadata.json'

        logger.info(f"Data cache initialized at {self.cache_dir}")
        logger.info(f"Cache settings: Max {max_size_mb}MB ({max_size_mb/1024:.1f}GB), TTL {ttl_hours}h ({ttl_hours/24:.0f} days)")

        self._load_metadata()
        self._cleanup_expired()

        # Track which symbols are cached
        self.cached_symbols = {}  # symbol -> {'date_ranges': [(start, end), ...], 'total_rows': int}

    def _load_metadata(self):
        """Load cache metadata"""
        if self.metadata_file.exists():
            try:
                with open(self.metadata_file, 'r') as f:
                    self.metadata = json.load(f)
                logger.info(f"Loaded cache metadata: {len(self.metadata)} entries")
            except json.JSONDecodeError as e:
                logger.warning(f"Corrupted metadata file, rebuilding: {e}")
                self.metadata = {}
                # Attempt to rebuild from actual cache files
                self._rebuild_metadata()
            except Exception as e:
                logger.warning(f"Failed to load metadata: {e}")
                self.metadata = {}
        else:
            self.metadata = {}

    def _rebuild_metadata(self):
        """Rebuild metadata from actual cache files"""
        try:
            import os
            for cache_file in self.cache_dir.glob("*.pkl"):
                if cache_file.is_file():
                    key = cache_file.stem
                    file_size = cache_file.stat().st_size
                    # Estimate basic info
                    self.metadata[key] = {
                        'created_at': datetime.now().isoformat(),
                        'size_bytes': file_size
                    }
            logger.info(f"Rebuilt metadata for {len(self.metadata)} cache files")
        except Exception as e:
            logger.warning(f"Failed to rebuild metadata: {e}")

    def _save_metadata(self):
        """Save cache metadata"""
        try:
            # Convert all numpy types to native Python types for JSON serialization
            serializable_metadata = {}
            for key, info in self.metadata.items():
                serializable_info = {}
                for k, v in info.items():
                    # Convert numpy types to Python native types
                    if hasattr(v, 'item'):  # numpy scalar
                        v = v.item()
                    elif isinstance(v, dict):
                        # Recursively convert nested dicts
                        v = {k2: (v2.item() if hasattr(v2, 'item') else v2) for k2, v2 in v.items()}
                    serializable_info[k] = v
                serializable_metadata[key] = serializable_info

            with open(self.metadata_file, 'w') as f:
                json.dump(serializable_metadata, f, indent=2)
        except Exception as e:
            logger.error(f"Failed to save metadata: {e}")

    def _get_cache_key(self, symbol: str, start_date: str, end_date: str) -> str:
        """Generate cache key for symbol + date range"""
        key_str = f"{symbol}_{start_date}_{end_date}"
        return hashlib.md5(key_str.encode()).hexdigest()

    def _cleanup_expired(self):
        """Remove expired cache entries"""
        now = datetime.now()
        expired_keys = []

        # Create snapshot to avoid "dictionary changed size" error
        metadata_items = list(self.metadata.items())

        for key, info in metadata_items:
            if 'created_at' in info:
                created = datetime.fromisoformat(info['created_at'])
                age_hours = (now - created).total_seconds() / 3600

                if age_hours > self.ttl_hours:
                    expired_keys.append(key)
                    # Delete cache file
                    cache_file = self.cache_dir / f"{key}.pkl"
                    if cache_file.exists():
                        try:
                            cache_file.unlink()
                            logger.info(f"Deleted expired cache: {key}")
                        except Exception as e:
                            logger.warning(f"Failed to delete expired cache {key}: {e}")

        # Update metadata
        for key in expired_keys:
            del self.metadata[key]

        if expired_keys:
            self._save_metadata()

    def _check_size_limit(self):
        """Ensure cache doesn't exceed size limit"""
        # Create copy to avoid "dictionary changed size during iteration" error
        metadata_keys = list(self.metadata.keys())

        total_size = sum(
            (self.cache_dir / f"{key}.pkl").stat().st_size
            for key in metadata_keys
            if (self.cache_dir / f"{key}.pkl").exists()
        )

        if total_size > self.max_size_bytes:
            logger.warning(f"Cache size {total_size / 1024 / 1024:.1f}MB exceeds limit. Cleaning...")

            # Sort by creation time, remove oldest
            sorted_entries = sorted(
                list(self.metadata.items()),
                key=lambda x: x[1].get('created_at', ''),
                reverse=True
            )

            for key, _ in sorted_entries[:-5]:  # Keep last 5, delete oldest
                cache_file = self.cache_dir / f"{key}.pkl"
                if cache_file.exists():
                    try:
                        cache_file.unlink()
                        del self.metadata[key]
                    except:
                        pass

            self._save_metadata()

    def get(self, symbol: str, start_date: str, end_date: str) -> Optional[pd.DataFrame]:
        """
        Get cached data if available and not expired

        Args:
            symbol: Stock symbol
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)

        Returns:
            DataFrame if cache hit, None if expired or not found
        """
        cache_key = self._get_cache_key(symbol, start_date, end_date)

        if cache_key not in self.metadata:
            logger.debug(f"Cache miss for {symbol} ({start_date} to {end_date})")
            return None

        # Check expiration
        info = self.metadata[cache_key]
        created = datetime.fromisoformat(info['created_at'])
        age_hours = (datetime.now() - created).total_seconds() / 3600

        if age_hours > self.ttl_hours:
            logger.info(f"Cache expired for {symbol}: {age_hours:.1f}h old")
            return None

        # Load from disk
        cache_file = self.cache_dir / f"{cache_key}.pkl"
        try:
            if not cache_file.exists():
                logger.warning(f"Cache file missing for {cache_key}")
                return None

            with open(cache_file, 'rb') as f:
                df = pickle.load(f)

            logger.info(f"✓ Cache hit for {symbol}: {len(df):,} rows, {age_hours:.1f}h old")
            return df

        except Exception as e:
            logger.error(f"Failed to load cache {cache_key}: {e}")
            return None

    def set(self, symbol: str, start_date: str, end_date: str, df: pd.DataFrame) -> bool:
        """
        Cache fetched data

        Args:
            symbol: Stock symbol
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)
            df: DataFrame with market data

        Returns:
            True if cached, False otherwise
        """
        if df.empty:
            return False

        cache_key = self._get_cache_key(symbol, start_date, end_date)
        cache_file = self.cache_dir / f"{cache_key}.pkl"

        try:
            # Check size before saving
            df_size = df.memory_usage(deep=True).sum()
            if df_size > self.max_size_bytes:
                logger.warning(f"Skipping cache for {symbol}: {df_size / 1024 / 1024:.1f}MB exceeds limit")
                return False

            # Save to disk
            with open(cache_file, 'wb') as f:
                pickle.dump(df, f)

            # Update metadata
            self.metadata[cache_key] = {
                'symbol': symbol,
                'start_date': start_date,
                'end_date': end_date,
                'created_at': datetime.now().isoformat(),
                'rows': len(df),
                'size_bytes': df_size
            }

            self._save_metadata()
            self._check_size_limit()

            logger.info(f"✓ Cached {symbol}: {len(df):,} rows, {df_size / 1024 / 1024:.2f}MB")
            return True

        except Exception as e:
            logger.error(f"Failed to cache {symbol}: {e}")
            return False

    def clear_symbol(self, symbol: str) -> bool:
        """Clear all cache entries for a symbol"""
        keys_to_delete = [
            key for key, info in self.metadata.items()
            if info.get('symbol') == symbol
        ]

        for key in keys_to_delete:
            cache_file = self.cache_dir / f"{key}.pkl"
            try:
                if cache_file.exists():
                    cache_file.unlink()
                del self.metadata[key]
            except Exception as e:
                logger.error(f"Failed to delete cache {key}: {e}")

        if keys_to_delete:
            self._save_metadata()
            logger.info(f"Cleared {len(keys_to_delete)} cache entries for {symbol}")

        return len(keys_to_delete) > 0

    def clear_all(self) -> bool:
        """Clear all cache"""
        try:
            for file in self.cache_dir.glob("*.pkl"):
                file.unlink()
            self.metadata = {}
            self._save_metadata()
            logger.info("Cleared all cache")
            return True
        except Exception as e:
            logger.error(f"Failed to clear cache: {e}")
            return False

    def get_cached_date_ranges(self, symbol: str) -> list:
        """
        Get all cached date ranges for a symbol

        Args:
            symbol: Stock symbol

        Returns:
            List of tuples: [(start_date, end_date), ...]
        """
        ranges = []
        # Create snapshot to avoid "dictionary changed size" error
        metadata_items = list(self.metadata.items())

        for key, info in metadata_items:
            if info.get('symbol') == symbol:
                start = info.get('start_date')
                end = info.get('end_date')
                if start and end:
                    ranges.append((start, end))

        # Sort by date
        ranges.sort(key=lambda x: x[0])
        logger.debug(f"{symbol} has {len(ranges)} cached date ranges")
        return ranges

    def get_covering_cache_entries(self, symbol: str, from_date: str, to_date: str) -> list:
        """
        Get all cache entries that cover the requested date range
        Merges all cached batches that overlap with or cover the requested range

        Args:
            symbol: Stock symbol
            from_date: Start date (YYYY-MM-DD)
            to_date: End date (YYYY-MM-DD)

        Returns:
            List of cache keys that cover this date range
        """
        from_dt = datetime.strptime(from_date, '%Y-%m-%d')
        to_dt = datetime.strptime(to_date, '%Y-%m-%d')

        covering_keys = []

        # Create snapshot to avoid "dictionary changed size" error
        metadata_items = list(self.metadata.items())

        for key, info in metadata_items:
            if info.get('symbol') != symbol:
                continue

            # Check expiration
            created = datetime.fromisoformat(info.get('created_at', datetime.now().isoformat()))
            age_hours = (datetime.now() - created).total_seconds() / 3600
            if age_hours > self.ttl_hours:
                continue

            # Check if this cache entry overlaps with requested range
            try:
                cache_start = datetime.strptime(info.get('start_date', ''), '%Y-%m-%d')
                cache_end = datetime.strptime(info.get('end_date', ''), '%Y-%m-%d')

                # Check overlap: cache_start <= to_dt AND cache_end >= from_dt
                if cache_start <= to_dt and cache_end >= from_dt:
                    covering_keys.append(key)
            except:
                pass

        return sorted(covering_keys)

    def get_data_for_date_range(self, symbol: str, from_date: str, to_date: str) -> Optional[pd.DataFrame]:
        """
        Get cached data for a date range by merging all covering cache entries
        This is the key method - it loads multiple cached batches and combines them

        Args:
            symbol: Stock symbol
            from_date: Start date (YYYY-MM-DD)
            to_date: End date (YYYY-MM-DD)

        Returns:
            Combined DataFrame if any cached data covers the range, None otherwise
        """
        covering_keys = self.get_covering_cache_entries(symbol, from_date, to_date)

        if not covering_keys:
            logger.debug(f"No cached entries cover {symbol} {from_date} to {to_date}")
            return None

        # Load all covering cache entries
        all_dfs = []
        for key in covering_keys:
            cache_file = self.cache_dir / f"{key}.pkl"
            try:
                if cache_file.exists():
                    with open(cache_file, 'rb') as f:
                        df = pickle.load(f)
                    all_dfs.append(df)
                    logger.debug(f"Loaded cache batch: {key} ({len(df):,} rows)")
            except Exception as e:
                logger.warning(f"Failed to load cache batch {key}: {e}")

        if not all_dfs:
            return None

        # Combine all batches
        import pandas as pd
        combined_df = pd.concat(all_dfs, ignore_index=True)

        # Filter to requested date range
        if 'datetime' in combined_df.columns:
            from_dt = pd.to_datetime(from_date)
            to_dt = pd.to_datetime(to_date)
            combined_df = combined_df[
                (combined_df['datetime'] >= from_dt) &
                (combined_df['datetime'] <= to_dt)
            ]

        # Remove duplicates and sort
        combined_df = combined_df.drop_duplicates().sort_values('datetime').reset_index(drop=True)

        logger.info(f"✓ Merged {len(covering_keys)} cache batches for {symbol}: {len(combined_df):,} rows ({from_date} to {to_date})")
        return combined_df if not combined_df.empty else None

    def is_date_range_cached(self, symbol: str, from_date: str, to_date: str) -> bool:
        """
        Check if a date range is fully covered by cache

        Args:
            symbol: Stock symbol
            from_date: Start date (YYYY-MM-DD)
            to_date: End date (YYYY-MM-DD)

        Returns:
            True if covered by cache, False otherwise
        """
        covering_keys = self.get_covering_cache_entries(symbol, from_date, to_date)

        if not covering_keys:
            return False

        # Check if we have continuous coverage
        from_dt = datetime.strptime(from_date, '%Y-%m-%d')
        to_dt = datetime.strptime(to_date, '%Y-%m-%d')

        # Get coverage info
        coverage_ranges = []
        for key in covering_keys:
            info = self.metadata[key]
            try:
                start = datetime.strptime(info.get('start_date', ''), '%Y-%m-%d')
                end = datetime.strptime(info.get('end_date', ''), '%Y-%m-%d')
                coverage_ranges.append((start, end))
            except:
                pass

        # Sort coverage ranges
        coverage_ranges.sort()

        # Check if we have complete coverage
        current_coverage = from_dt
        for start, end in coverage_ranges:
            if start > current_coverage:
                # Gap in coverage
                return False
            current_coverage = max(current_coverage, end)
            if current_coverage >= to_dt:
                return True

        return current_coverage >= to_dt

    def get_stats(self) -> Dict:
        """Get cache statistics"""
        # Create copy to avoid "dictionary changed size during iteration" error
        metadata_keys = list(self.metadata.keys())

        total_size = 0
        for key in metadata_keys:
            cache_file = self.cache_dir / f"{key}.pkl"
            if cache_file.exists():
                total_size += cache_file.stat().st_size

        return {
            'entries': len(self.metadata),
            'total_size_mb': round(total_size / 1024 / 1024, 2),
            'max_size_mb': self.max_size_bytes / 1024 / 1024,
            'usage_percent': round((total_size / self.max_size_bytes) * 100, 1),
            'cache_dir': str(self.cache_dir)
        }


# Global instance
_cache_instance = None


def get_data_cache() -> DataFetchCache:
    """Get or create global data cache instance"""
    global _cache_instance
    if _cache_instance is None:
        _cache_instance = DataFetchCache()
    return _cache_instance

