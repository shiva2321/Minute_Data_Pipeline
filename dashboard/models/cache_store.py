"""
Cache Store - Persistent data storage for dashboard state
Handles API usage stats, company lists, and session data
"""
import sqlite3
import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any
import logging

logger = logging.getLogger(__name__)


class CacheStore:
    """SQLite-backed persistent cache for dashboard data"""

    def __init__(self, db_path: Optional[Path] = None):
        """
        Initialize cache store

        Args:
            db_path: Path to SQLite database. Defaults to ~/.pipeline_cache.db
        """
        if db_path is None:
            db_path = Path.home() / '.pipeline_cache.db'

        self.db_path = db_path
        self.connection: Optional[sqlite3.Connection] = None

        self._init_db()

    def _init_db(self):
        """Initialize database schema"""
        try:
            self.connection = sqlite3.connect(str(self.db_path), timeout=10)
            self.connection.row_factory = sqlite3.Row
            cursor = self.connection.cursor()

            # API Usage Stats Table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS api_usage (
                    id INTEGER PRIMARY KEY,
                    date_key TEXT UNIQUE,  -- YYYY-MM-DD
                    daily_calls INTEGER DEFAULT 0,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')

            # Company List Cache Table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS company_list (
                    id INTEGER PRIMARY KEY,
                    symbol TEXT UNIQUE,
                    exchange TEXT,
                    company_name TEXT,
                    country TEXT,
                    currency TEXT,
                    fetched_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')

            # Cache Metadata Table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS cache_metadata (
                    id INTEGER PRIMARY KEY,
                    key TEXT UNIQUE,
                    value TEXT,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')

            # Session Settings Table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS session_settings (
                    id INTEGER PRIMARY KEY,
                    key TEXT UNIQUE,
                    value TEXT,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')

            # Selected Companies Table (accumulated across sessions)
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS selected_companies (
                    id INTEGER PRIMARY KEY,
                    symbol TEXT UNIQUE,
                    added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')

            self.connection.commit()
            logger.info(f"Cache database initialized at {self.db_path}")

        except Exception as e:
            logger.error(f"Failed to initialize cache database: {e}")
            raise

    def close(self):
        """Close database connection"""
        if self.connection:
            self.connection.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    # ==================== API Usage Methods ====================

    def get_daily_api_calls(self, date: Optional[datetime] = None) -> int:
        """Get API call count for a specific date (default: today)"""
        if date is None:
            date = datetime.now()

        date_key = date.strftime('%Y-%m-%d')

        try:
            cursor = self.connection.cursor()
            cursor.execute(
                'SELECT daily_calls FROM api_usage WHERE date_key = ?',
                (date_key,)
            )
            result = cursor.fetchone()
            return result['daily_calls'] if result else 0

        except Exception as e:
            logger.error(f"Failed to get daily API calls: {e}")
            return 0

    def update_daily_api_calls(self, calls: int, date: Optional[datetime] = None):
        """Update API call count for a date"""
        if date is None:
            date = datetime.now()

        date_key = date.strftime('%Y-%m-%d')

        try:
            cursor = self.connection.cursor()
            cursor.execute('''
                INSERT INTO api_usage (date_key, daily_calls)
                VALUES (?, ?)
                ON CONFLICT(date_key) DO UPDATE SET
                    daily_calls = excluded.daily_calls,
                    updated_at = CURRENT_TIMESTAMP
            ''', (date_key, calls))
            self.connection.commit()

        except Exception as e:
            logger.error(f"Failed to update daily API calls: {e}")

    def increment_daily_api_calls(self, increment: int = 1, date: Optional[datetime] = None):
        """Increment API call count for a date"""
        current = self.get_daily_api_calls(date)
        self.update_daily_api_calls(current + increment, date)

    def reset_daily_api_calls_if_new_day(self) -> bool:
        """Reset API calls if calendar day changed. Returns True if reset occurred"""
        last_reset_key = 'last_api_reset_date'
        today = datetime.now().strftime('%Y-%m-%d')

        try:
            cursor = self.connection.cursor()

            # Get last reset date
            cursor.execute(
                'SELECT value FROM cache_metadata WHERE key = ?',
                (last_reset_key,)
            )
            result = cursor.fetchone()
            last_reset = result['value'] if result else None

            # If different day, reset
            if last_reset != today:
                self.update_daily_api_calls(0, datetime.now())
                self._set_cache_metadata(last_reset_key, today)
                logger.info(f"API usage reset for new day: {today}")
                return True

            return False

        except Exception as e:
            logger.error(f"Failed to check/reset API calls: {e}")
            return False

    # ==================== Company List Methods ====================

    def save_company_list(self, companies: List[Dict[str, Any]]):
        """Save company list to cache"""
        try:
            cursor = self.connection.cursor()

            # Clear existing
            cursor.execute('DELETE FROM company_list')

            # Insert new
            for company in companies:
                cursor.execute('''
                    INSERT INTO company_list
                    (symbol, exchange, company_name, country, currency)
                    VALUES (?, ?, ?, ?, ?)
                ''', (
                    company.get('Code'),
                    company.get('Exchange'),
                    company.get('Name'),
                    company.get('Country'),
                    company.get('Currency')
                ))

            self.connection.commit()
            self._set_cache_metadata('company_list_fetched_at', datetime.now().isoformat())
            logger.info(f"Saved {len(companies)} companies to cache")

        except Exception as e:
            logger.error(f"Failed to save company list: {e}")

    def get_company_list(self) -> List[Dict[str, str]]:
        """Get cached company list"""
        try:
            cursor = self.connection.cursor()
            cursor.execute('SELECT symbol, exchange, company_name FROM company_list ORDER BY symbol')
            rows = cursor.fetchall()
            return [dict(row) for row in rows]

        except Exception as e:
            logger.error(f"Failed to get company list: {e}")
            return []

    def search_companies(self, query: str) -> List[Dict[str, str]]:
        """Search company list by symbol or name"""
        try:
            cursor = self.connection.cursor()
            search_pattern = f"%{query.upper()}%"
            cursor.execute('''
                SELECT symbol, exchange, company_name FROM company_list
                WHERE symbol LIKE ? OR company_name LIKE ?
                ORDER BY symbol
                LIMIT 100
            ''', (search_pattern, search_pattern))
            rows = cursor.fetchall()
            return [dict(row) for row in rows]

        except Exception as e:
            logger.error(f"Failed to search companies: {e}")
            return []

    def get_company_list_fetch_time(self) -> Optional[datetime]:
        """Get when company list was last fetched"""
        try:
            value = self._get_cache_metadata('company_list_fetched_at')
            if value:
                return datetime.fromisoformat(value)
        except Exception as e:
            logger.error(f"Failed to get company list fetch time: {e}")
        return None

    def is_company_list_stale(self, max_age_hours: int = 24) -> bool:
        """Check if company list is stale (older than max_age_hours)

        Args:
            max_age_hours: Maximum age in hours before considering stale. Default 24 hours.
        """
        fetch_time = self.get_company_list_fetch_time()
        if fetch_time is None:
            return True
        return datetime.now() - fetch_time > timedelta(hours=max_age_hours)

    # ==================== Cache Metadata Methods ====================

    def _set_cache_metadata(self, key: str, value: str):
        """Set cache metadata value"""
        try:
            cursor = self.connection.cursor()
            cursor.execute('''
                INSERT INTO cache_metadata (key, value)
                VALUES (?, ?)
                ON CONFLICT(key) DO UPDATE SET
                    value = excluded.value,
                    updated_at = CURRENT_TIMESTAMP
            ''', (key, value))
            self.connection.commit()

        except Exception as e:
            logger.error(f"Failed to set cache metadata: {e}")

    def _get_cache_metadata(self, key: str) -> Optional[str]:
        """Get cache metadata value"""
        try:
            cursor = self.connection.cursor()
            cursor.execute('SELECT value FROM cache_metadata WHERE key = ?', (key,))
            result = cursor.fetchone()
            return result['value'] if result else None

        except Exception as e:
            logger.error(f"Failed to get cache metadata: {e}")
            return None

    # ==================== Session Settings Methods ====================

    def save_session_settings(self, settings: Dict[str, Any]):
        """Save session settings"""
        try:
            cursor = self.connection.cursor()
            for key, value in settings.items():
                cursor.execute('''
                    INSERT INTO session_settings (key, value)
                    VALUES (?, ?)
                    ON CONFLICT(key) DO UPDATE SET
                        value = excluded.value,
                        updated_at = CURRENT_TIMESTAMP
                ''', (key, json.dumps(value) if not isinstance(value, str) else value))
            self.connection.commit()

        except Exception as e:
            logger.error(f"Failed to save session settings: {e}")

    def load_session_settings(self) -> Dict[str, Any]:
        """Load session settings"""
        try:
            cursor = self.connection.cursor()
            cursor.execute('SELECT key, value FROM session_settings')
            rows = cursor.fetchall()

            settings = {}
            for row in rows:
                try:
                    settings[row['key']] = json.loads(row['value'])
                except (json.JSONDecodeError, TypeError):
                    settings[row['key']] = row['value']

            return settings

        except Exception as e:
            logger.error(f"Failed to load session settings: {e}")
            return {}

    def clear_cache(self):
        """Clear all cache data"""
        try:
            cursor = self.connection.cursor()
            cursor.execute('DELETE FROM api_usage')
            cursor.execute('DELETE FROM company_list')
            cursor.execute('DELETE FROM cache_metadata')
            cursor.execute('DELETE FROM session_settings')
            cursor.execute('DELETE FROM selected_companies')
            self.connection.commit()
            logger.info("Cache cleared")

        except Exception as e:
            logger.error(f"Failed to clear cache: {e}")

    # ==================== Selected Companies Methods (Persistent) ====================

    def add_selected_company(self, symbol: str):
        """Add a company to persistent selected list"""
        try:
            cursor = self.connection.cursor()
            cursor.execute('''
                INSERT OR IGNORE INTO selected_companies (symbol)
                VALUES (?)
            ''', (symbol.upper(),))
            self.connection.commit()
            logger.info(f"Added {symbol} to selected companies")
        except Exception as e:
            logger.error(f"Failed to add selected company: {e}")

    def add_selected_companies(self, symbols: List[str]):
        """Add multiple companies to persistent selected list"""
        try:
            cursor = self.connection.cursor()
            for symbol in symbols:
                cursor.execute('''
                    INSERT OR IGNORE INTO selected_companies (symbol)
                    VALUES (?)
                ''', (symbol.upper(),))
            self.connection.commit()
            logger.info(f"Added {len(symbols)} companies to selected list")
        except Exception as e:
            logger.error(f"Failed to add selected companies: {e}")

    def get_selected_companies(self) -> List[str]:
        """Get all persistently selected companies"""
        try:
            cursor = self.connection.cursor()
            cursor.execute('SELECT symbol FROM selected_companies ORDER BY added_at DESC')
            rows = cursor.fetchall()
            return [row[0] for row in rows]
        except Exception as e:
            logger.error(f"Failed to get selected companies: {e}")
            return []

    def remove_selected_company(self, symbol: str):
        """Remove a company from selected list"""
        try:
            cursor = self.connection.cursor()
            cursor.execute('DELETE FROM selected_companies WHERE symbol = ?', (symbol.upper(),))
            self.connection.commit()
            logger.info(f"Removed {symbol} from selected companies")
        except Exception as e:
            logger.error(f"Failed to remove selected company: {e}")

    def clear_selected_companies(self):
        """Clear all selected companies"""
        try:
            cursor = self.connection.cursor()
            cursor.execute('DELETE FROM selected_companies')
            self.connection.commit()
            logger.info("Cleared all selected companies")
        except Exception as e:
            logger.error(f"Failed to clear selected companies: {e}")
