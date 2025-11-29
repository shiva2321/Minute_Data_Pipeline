"""
MongoDB storage module for company profiles
"""
from pymongo import MongoClient, ASCENDING, DESCENDING
from pymongo.errors import ConnectionFailure, DuplicateKeyError
from datetime import datetime
from typing import Dict, List, Optional
import pandas as pd
from loguru import logger
from config import settings


class MongoDBStorage:
    """Handles storage and retrieval of company profiles in MongoDB"""

    def __init__(self, uri: Optional[str] = None, database: Optional[str] = None, collection: Optional[str] = None):
        """
        Initialize MongoDB connection

        Args:
            uri: MongoDB connection URI
            database: Database name
            collection: Collection name
        """
        self.uri = uri or settings.mongodb_uri
        self.database_name = database or settings.mongodb_database
        self.collection_name = collection or settings.mongodb_collection

        try:
            self.client = MongoClient(self.uri, serverSelectionTimeoutMS=5000)
            # Test connection
            self.client.admin.command('ping')
            logger.info(f"Successfully connected to MongoDB at {self.uri}")

            self.db = self.client[self.database_name]
            self.collection = self.db[self.collection_name]

            # Create indexes
            self._create_indexes()

        except ConnectionFailure as e:
            logger.error(f"Failed to connect to MongoDB: {e}")
            raise

    def _create_indexes(self):
        """Create indexes for efficient querying"""
        try:
            # Index on symbol and exchange
            self.collection.create_index([("symbol", ASCENDING), ("exchange", ASCENDING)], unique=True)

            # Index on last updated
            self.collection.create_index([("last_updated", DESCENDING)])

            # Index on company name for text search
            self.collection.create_index([("company_name", ASCENDING)])

            logger.info("Indexes created successfully")
        except Exception as e:
            logger.warning(f"Error creating indexes: {e}")

    def create_company_profile(
        self,
        symbol: str,
        exchange: str,
        raw_data: pd.DataFrame,
        features: Dict,
        fundamental_data: Optional[Dict] = None
    ) -> Dict:
        """
        Create a comprehensive company profile

        Args:
            symbol: Stock symbol
            exchange: Exchange code
            raw_data: DataFrame with minute data
            features: Dictionary of engineered features
            fundamental_data: Fundamental company data

        Returns:
            Company profile dictionary
        """
        profile = {
            'symbol': symbol,
            'exchange': exchange,
            'last_updated': datetime.utcnow(),

            # Basic info
            'company_name': fundamental_data.get('General', {}).get('Name', '') if fundamental_data else '',
            'sector': fundamental_data.get('General', {}).get('Sector', '') if fundamental_data else '',
            'industry': fundamental_data.get('General', {}).get('Industry', '') if fundamental_data else '',

            # Data summary
            'data_summary': features.get('summary', {}),

            # Statistical features
            'statistical_features': features.get('statistical_features', {}),

            # Time-based features
            'time_based_features': features.get('time_features', {}),

            # Market microstructure
            'microstructure_features': features.get('microstructure_features', {}),

            # Technical analysis snapshot (latest values)
            'technical_indicators': self._extract_latest_indicators(features.get('processed_df', pd.DataFrame())),

            # Performance metrics
            'performance_metrics': self._calculate_performance_metrics(raw_data),

            # Risk metrics
            'risk_metrics': self._calculate_risk_metrics(raw_data, features.get('statistical_features', {})),

            # Fundamental data (if available)
            'fundamental_data': fundamental_data if fundamental_data else {},

            # Raw data statistics
            'data_points_count': len(raw_data),
            'data_date_range': {
                'start': str(raw_data['datetime'].min()) if 'datetime' in raw_data.columns and len(raw_data) > 0 else None,
                'end': str(raw_data['datetime'].max()) if 'datetime' in raw_data.columns and len(raw_data) > 0 else None
            },

            # Advanced Feature Sections
            'advanced_statistical': features.get('advanced_statistical', {}),
            'multi_timeframe': features.get('multi_timeframe', {}),
            'quality_metrics': features.get('quality_metrics', {}),
            'labels': features.get('labels', {}),
            'technical_extended_latest': features.get('technical_extended_latest', {}),
            'feature_metadata': features.get('feature_metadata', {}),
            'regime_features': features.get('regime_features', {}),
            'predictive_labels': features.get('predictive_labels', {})
        }

        return profile

    def _extract_latest_indicators(self, df: pd.DataFrame) -> Dict:
        """Extract the latest values of technical indicators"""
        if df.empty:
            return {}

        indicators = {}
        latest = df.iloc[-1]

        # List of indicator columns to extract
        indicator_cols = [
            'sma_20', 'sma_50', 'sma_200',
            'ema_20', 'ema_50', 'ema_200',
            'rsi_14', 'rsi_28',
            'macd', 'macd_signal', 'macd_histogram',
            'atr_14',
            'bb_upper_20', 'bb_lower_20', 'bb_middle_20',
            'stoch_14'
        ]

        for col in indicator_cols:
            if col in df.columns:
                value = latest[col]
                if pd.notna(value):
                    indicators[col] = float(value)

        return indicators

    def _calculate_performance_metrics(self, df: pd.DataFrame) -> Dict:
        """Calculate performance metrics"""
        if df.empty:
            return {}

        metrics = {}

        if 'close' in df.columns and len(df) > 0:
            # Period returns
            metrics['total_return'] = float((df['close'].iloc[-1] - df['close'].iloc[0]) / df['close'].iloc[0])

            # High/Low levels
            metrics['period_high'] = float(df['high'].max())
            metrics['period_low'] = float(df['low'].min())

            # Average daily range
            if 'datetime' in df.columns:
                df_copy = df.copy()
                df_copy['date'] = pd.to_datetime(df_copy['datetime']).dt.date
                daily_ranges = df_copy.groupby('date').apply(
                    lambda x: (x['high'].max() - x['low'].min()) / x['close'].mean()
                )
                metrics['avg_daily_range_pct'] = float(daily_ranges.mean())

        return metrics

    def _calculate_risk_metrics(self, df: pd.DataFrame, statistical_features: Dict) -> Dict:
        """Calculate risk metrics"""
        metrics = {}

        if df.empty:
            return metrics

        # Value at Risk (VaR)
        if 'close' in df.columns:
            returns = df['close'].pct_change().dropna()
            if len(returns) > 0:
                metrics['var_95'] = float(returns.quantile(0.05))
                metrics['var_99'] = float(returns.quantile(0.01))

                # Conditional VaR (CVaR/Expected Shortfall)
                metrics['cvar_95'] = float(returns[returns <= returns.quantile(0.05)].mean())
                metrics['cvar_99'] = float(returns[returns <= returns.quantile(0.01)].mean())

        # Max drawdown
        if 'close' in df.columns:
            cumulative = (1 + df['close'].pct_change()).cumprod()
            running_max = cumulative.expanding().max()
            drawdown = (cumulative - running_max) / running_max
            metrics['max_drawdown'] = float(drawdown.min())

        # Volatility metrics from statistical features
        if 'returns_std' in statistical_features:
            # Annualized volatility (assuming 252 trading days, 390 minutes per day)
            metrics['annualized_volatility'] = float(statistical_features['returns_std'] * np.sqrt(252 * 390))

        return metrics

    def save_profile(self, profile: Dict) -> bool:
        """
        Save or update a company profile

        Args:
            profile: Company profile dictionary

        Returns:
            True if successful, False otherwise
        """
        try:
            # Use upsert to update if exists, insert if not
            result = self.collection.update_one(
                {'symbol': profile['symbol'], 'exchange': profile['exchange']},
                {'$set': profile},
                upsert=True
            )

            if result.upserted_id:
                logger.info(f"Inserted new profile for {profile['symbol']}")
            else:
                logger.info(f"Updated profile for {profile['symbol']}")

            return True

        except Exception as e:
            logger.error(f"Error saving profile for {profile['symbol']}: {e}")
            return False

    def save_profile_with_backfill_metadata(self, profile: Dict, backfill_info: Dict) -> bool:
        """Save or update profile with backfill metadata tracking."""
        try:
            profile['backfill_metadata'] = {
                'history_complete': backfill_info.get('complete', False),
                'history_rows': backfill_info.get('total_rows', 0),
                'history_fetch_timestamp': datetime.utcnow(),
                'history_date_range': backfill_info.get('date_range', {}),
                'api_calls_used': backfill_info.get('api_calls', 0),
                'fetch_duration_seconds': backfill_info.get('duration', 0)
            }
            result = self.collection.update_one(
                {'symbol': profile['symbol'], 'exchange': profile['exchange']},
                {'$set': profile},
                upsert=True
            )
            return True
        except Exception as e:
            logger.error(f"Error saving profile with backfill metadata for {profile['symbol']}: {e}")
            return False

    def get_profile(self, symbol: str, exchange: str = 'US') -> Optional[Dict]:
        """
        Retrieve a company profile

        Args:
            symbol: Stock symbol
            exchange: Exchange code

        Returns:
            Company profile or None if not found
        """
        try:
            profile = self.collection.find_one({'symbol': symbol, 'exchange': exchange})
            if profile:
                logger.info(f"Retrieved profile for {symbol}")
            else:
                logger.warning(f"Profile not found for {symbol}")
            return profile
        except Exception as e:
            logger.error(f"Error retrieving profile for {symbol}: {e}")
            return None

    def get_all_profiles(self, limit: Optional[int] = None) -> List[Dict]:
        """
        Retrieve all company profiles

        Args:
            limit: Maximum number of profiles to return

        Returns:
            List of company profiles
        """
        try:
            query = self.collection.find()
            if limit:
                query = query.limit(limit)

            profiles = list(query)
            logger.info(f"Retrieved {len(profiles)} profiles")
            return profiles
        except Exception as e:
            logger.error(f"Error retrieving profiles: {e}")
            return []

    def list_all_profiles(self, limit: Optional[int] = None) -> List[Dict]:
        """
        Alias for get_all_profiles for dashboard compatibility

        Args:
            limit: Maximum number of profiles to return

        Returns:
            List of company profiles
        """
        return self.get_all_profiles(limit)

    def update_profile(self, symbol: str, profile: Dict, exchange: str = 'US') -> bool:
        """
        Update an existing profile

        Args:
            symbol: Stock symbol
            profile: Updated profile dictionary
            exchange: Exchange code

        Returns:
            True if successful, False otherwise
        """
        try:
            profile['last_updated'] = datetime.utcnow()

            result = self.collection.update_one(
                {'symbol': symbol, 'exchange': exchange},
                {'$set': profile},
                upsert=True
            )

            if result.modified_count > 0 or result.upserted_id:
                logger.info(f"Updated profile for {symbol}")
                return True
            else:
                logger.warning(f"No changes made to profile for {symbol}")
                return False

        except Exception as e:
            logger.error(f"Error updating profile for {symbol}: {e}")
            return False

    def delete_profile(self, symbol: str, exchange: str = 'US') -> bool:
        """
        Delete a company profile

        Args:
            symbol: Stock symbol
            exchange: Exchange code

        Returns:
            True if successful, False otherwise
        """
        try:
            result = self.collection.delete_one({'symbol': symbol, 'exchange': exchange})
            if result.deleted_count > 0:
                logger.info(f"Deleted profile for {symbol}")
                return True
            else:
                logger.warning(f"Profile not found for {symbol}")
                return False
        except Exception as e:
            logger.error(f"Error deleting profile for {symbol}: {e}")
            return False

    def get_profiles_by_sector(self, sector: str) -> List[Dict]:
        """Get all profiles for a specific sector"""
        try:
            profiles = list(self.collection.find({'sector': sector}))
            logger.info(f"Retrieved {len(profiles)} profiles for sector {sector}")
            return profiles
        except Exception as e:
            logger.error(f"Error retrieving profiles by sector: {e}")
            return []

    def save_ml_profile(self, ml_profile: Dict) -> bool:
        """
        Save ML model profile to MongoDB

        Args:
            ml_profile: ML profile dictionary

        Returns:
            True if successful, False otherwise
        """
        try:
            ml_collection = self.db['ml_profiles']
            ml_collection.create_index([('symbol', ASCENDING)], unique=True)

            result = ml_collection.update_one(
                {'symbol': ml_profile['symbol']},
                {'$set': ml_profile},
                upsert=True
            )
            logger.info(f"Saved ML profile for {ml_profile['symbol']}")
            return True
        except Exception as e:
            logger.error(f"Error saving ML profile for {ml_profile['symbol']}: {e}")
            return False

    def save_statistical_profile(self, stat_profile: Dict) -> bool:
        """
        Save statistical profile to MongoDB

        Args:
            stat_profile: Statistical profile dictionary

        Returns:
            True if successful, False otherwise
        """
        try:
            stat_collection = self.db['statistical_profiles']
            stat_collection.create_index([('symbol', ASCENDING)], unique=True)

            result = stat_collection.update_one(
                {'symbol': stat_profile['symbol']},
                {'$set': stat_profile},
                upsert=True
            )
            logger.info(f"Saved statistical profile for {stat_profile['symbol']}")
            return True
        except Exception as e:
            logger.error(f"Error saving statistical profile for {stat_profile['symbol']}: {e}")
            return False

    def get_ml_profile(self, symbol: str) -> Optional[Dict]:
        """
        Retrieve ML profile for a symbol

        Args:
            symbol: Stock symbol

        Returns:
            ML profile or None if not found
        """
        try:
            ml_collection = self.db['ml_profiles']
            profile = ml_collection.find_one({'symbol': symbol})
            if profile:
                logger.info(f"Retrieved ML profile for {symbol}")
            else:
                logger.warning(f"ML profile not found for {symbol}")
            return profile
        except Exception as e:
            logger.error(f"Error retrieving ML profile for {symbol}: {e}")
            return None

    def get_statistical_profile(self, symbol: str) -> Optional[Dict]:
        """
        Retrieve statistical profile for a symbol

        Args:
            symbol: Stock symbol

        Returns:
            Statistical profile or None if not found
        """
        try:
            stat_collection = self.db['statistical_profiles']
            profile = stat_collection.find_one({'symbol': symbol})
            if profile:
                logger.info(f"Retrieved statistical profile for {symbol}")
            else:
                logger.warning(f"Statistical profile not found for {symbol}")
            return profile
        except Exception as e:
            logger.error(f"Error retrieving statistical profile for {symbol}: {e}")
            return None

    def close(self):
        """Close the MongoDB connection"""
        if hasattr(self, 'client'):
            self.client.close()
            logger.info("MongoDB connection closed")

    def __del__(self):
        """Ensure connection is closed when object is destroyed"""
        self.close()


# Import numpy for risk calculations
import numpy as np
