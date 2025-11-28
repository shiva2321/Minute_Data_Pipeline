"""
Database Controller - MongoDB Operations Wrapper
Thread-safe database operations with caching
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from PyQt6.QtCore import QObject
from typing import List, Dict, Optional
from threading import Lock
from datetime import datetime

from mongodb_storage import MongoDBStorage
from dashboard.utils.qt_signals import DatabaseSignals


class DatabaseController(QObject):
    """
    Thread-safe wrapper for MongoDB operations
    Provides caching and signal emission for UI updates
    """

    def __init__(self):
        super().__init__()
        self.storage = None
        self.signals = DatabaseSignals()
        self.lock = Lock()

        # Cache for profiles (reduces DB queries)
        self.profile_cache = {}
        self.cache_timestamp = None
        self.cache_ttl = 60  # seconds

        # Initialize connection
        self._ensure_connection()

        # Test connection
        self._test_connection()

    def _ensure_connection(self):
        """Ensure database connection is active, reconnect if needed"""
        try:
            # Check if storage exists and connection is alive
            if self.storage is None:
                self.storage = MongoDBStorage()
            else:
                # Test if connection is still alive
                try:
                    self.storage.client.admin.command('ping')
                except:
                    # Connection is dead, recreate
                    self.storage = MongoDBStorage()
        except Exception as e:
            self.signals.database_error.emit(f"Connection error: {str(e)}")
            self.storage = None

    def _test_connection(self):
        """Test database connection and emit status"""
        try:
            self._ensure_connection()
            if self.storage is None:
                self.signals.connection_status.emit(False, "Not connected")
                return

            # Try to list profiles
            profiles = self.storage.list_all_profiles()
            count = len(profiles)

            self.signals.connection_status.emit(
                True,
                f"Connected ({count} profiles)"
            )
        except Exception as e:
            self.signals.connection_status.emit(
                False,
                f"Connection failed: {str(e)}"
            )

    def load_all_profiles(self, force_refresh: bool = False) -> List[Dict]:
        """
        Load all profiles from database

        Args:
            force_refresh: Force refresh from database (bypass cache)

        Returns:
            List of profile dictionaries
        """
        with self.lock:
            # Check cache
            if (not force_refresh and
                self.cache_timestamp and
                (datetime.now() - self.cache_timestamp).seconds < self.cache_ttl):
                profiles = list(self.profile_cache.values())
                self.signals.profiles_loaded.emit(profiles)
                return profiles

            try:
                # Ensure connection is alive
                self._ensure_connection()
                if self.storage is None:
                    self.signals.database_error.emit("Database connection not available")
                    return []

                # Fetch from database
                profiles = self.storage.list_all_profiles()

                # Update cache
                self.profile_cache = {p['symbol']: p for p in profiles}
                self.cache_timestamp = datetime.now()

                self.signals.profiles_loaded.emit(profiles)
                return profiles

            except Exception as e:
                self.signals.database_error.emit(f"Failed to load profiles: {str(e)}")
                return []

    def get_profile(self, symbol: str, use_cache: bool = True) -> Optional[Dict]:
        """
        Get profile for a specific symbol

        Args:
            symbol: Ticker symbol
            use_cache: Use cached profile if available

        Returns:
            Profile dictionary or None
        """
        with self.lock:
            # Check cache first
            if use_cache and symbol in self.profile_cache:
                return self.profile_cache[symbol].copy()  # Return copy to prevent modification

            try:
                # Ensure connection is alive
                self._ensure_connection()
                if self.storage is None:
                    self.signals.database_error.emit("Database connection not available")
                    return None

                profile = self.storage.get_profile(symbol)

                # Update cache
                if profile:
                    self.profile_cache[symbol] = profile.copy()

                return profile

            except Exception as e:
                self.signals.database_error.emit(f"Failed to get profile for {symbol}: {str(e)}")
                # Try to return from cache as fallback
                return self.profile_cache.get(symbol, None)

    def save_profile(self, profile: Dict):
        """
        Save profile to database

        Args:
            profile: Profile dictionary with 'symbol' key
        """
        with self.lock:
            try:
                symbol = profile.get('symbol')
                if not symbol:
                    raise ValueError("Profile must have 'symbol' field")

                self.storage.save_profile(profile)

                # Update cache
                self.profile_cache[symbol] = profile

                self.signals.profile_updated.emit(symbol, profile)

            except Exception as e:
                self.signals.database_error.emit(f"Failed to save profile: {str(e)}")

    def update_profile(self, symbol: str, profile: Dict):
        """
        Update existing profile

        Args:
            symbol: Ticker symbol
            profile: Updated profile dictionary
        """
        with self.lock:
            try:
                self.storage.update_profile(symbol, profile)

                # Update cache
                self.profile_cache[symbol] = profile

                self.signals.profile_updated.emit(symbol, profile)

            except Exception as e:
                self.signals.database_error.emit(f"Failed to update profile for {symbol}: {str(e)}")

    def delete_profile(self, symbol: str):
        """
        Delete profile from database

        Args:
            symbol: Ticker symbol
        """
        with self.lock:
            try:
                self.storage.delete_profile(symbol)

                # Remove from cache
                if symbol in self.profile_cache:
                    del self.profile_cache[symbol]

                self.signals.profile_deleted.emit(symbol)

            except Exception as e:
                self.signals.database_error.emit(f"Failed to delete profile for {symbol}: {str(e)}")

    def search_profiles(self, query: str) -> List[Dict]:
        """
        Search profiles by symbol

        Args:
            query: Search query (symbol substring)

        Returns:
            List of matching profiles
        """
        with self.lock:
            try:
                # Use cache if available
                if not self.profile_cache:
                    self.load_all_profiles()

                # Filter by query
                query_upper = query.upper()
                matching = [
                    profile for symbol, profile in self.profile_cache.items()
                    if query_upper in symbol.upper()
                ]

                return matching

            except Exception as e:
                self.signals.database_error.emit(f"Search failed: {str(e)}")
                return []

    def get_profiles_by_date_range(
        self,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None
    ) -> List[Dict]:
        """
        Get profiles updated within date range

        Args:
            start_date: Start date (ISO format)
            end_date: End date (ISO format)

        Returns:
            List of profiles
        """
        with self.lock:
            try:
                profiles = self.storage.get_profiles_by_date_range(start_date, end_date)
                return profiles

            except Exception as e:
                self.signals.database_error.emit(f"Failed to get profiles by date: {str(e)}")
                return []

    def get_database_stats(self) -> Dict:
        """
        Get database statistics

        Returns:
            Dictionary with stats
        """
        with self.lock:
            try:
                profiles = self.load_all_profiles()

                total_data_points = sum(p.get('data_points_count', 0) for p in profiles)

                return {
                    'total_profiles': len(profiles),
                    'total_data_points': total_data_points,
                    'cache_size': len(self.profile_cache),
                    'last_refresh': self.cache_timestamp.isoformat() if self.cache_timestamp else None
                }

            except Exception as e:
                self.signals.database_error.emit(f"Failed to get stats: {str(e)}")
                return {}

    def invalidate_cache(self):
        """Invalidate the profile cache"""
        with self.lock:
            self.profile_cache.clear()
            self.cache_timestamp = None

