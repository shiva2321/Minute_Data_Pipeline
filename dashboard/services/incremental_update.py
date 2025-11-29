"""
Incremental Data Update Strategy
Efficiently updates profiles with new data without reprocessing all historical data
"""
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, Optional, Tuple
from loguru import logger


class IncrementalUpdateStrategy:
    """
    Strategy for efficiently updating profiles with new data
    Only processes new data points and merges with existing features
    """

    def __init__(self):
        """Initialize incremental update strategy"""
        pass

    def get_new_data_since_last_update(
        self,
        current_profile: Dict,
        new_data: pd.DataFrame
    ) -> pd.DataFrame:
        """
        Get only the new data points since last profile update

        Args:
            current_profile: Existing profile from MongoDB
            new_data: Newly fetched data

        Returns:
            DataFrame containing only new data points
        """
        try:
            if not current_profile or 'data_date_range' not in current_profile:
                logger.info("No previous profile found, using all new data")
                return new_data

            last_date_str = current_profile['data_date_range'].get('end')
            if not last_date_str:
                logger.warning("Could not find last date in profile, using all new data")
                return new_data

            last_date = pd.to_datetime(last_date_str)

            if 'datetime' not in new_data.columns:
                logger.warning("No datetime column in new data")
                return new_data

            # Filter to get only data after last update
            new_data_only = new_data[pd.to_datetime(new_data['datetime']) > last_date].copy()

            logger.info(f"Found {len(new_data_only)} new data points since {last_date_str}")
            return new_data_only

        except Exception as e:
            logger.error(f"Error getting new data: {e}")
            return new_data

    def merge_historical_features(
        self,
        current_profile: Dict,
        new_features: Dict
    ) -> Dict:
        """
        Merge new features with historical features from profile

        Args:
            current_profile: Existing profile with historical features
            new_features: Newly calculated features

        Returns:
            Merged features dictionary preserving historical aggregates
        """
        try:
            merged_features = {}

            # Copy new features as base
            merged_features.update(new_features)

            # Preserve important historical aggregates
            if 'statistical_features' in current_profile:
                old_stat_features = current_profile['statistical_features']
                new_stat_features = new_features.get('statistical_features', {})

                # Update statistics that can be incrementally computed
                preserved_stats = {}

                # Price statistics - update with new values
                if 'price_min' in old_stat_features and 'price_min' in new_stat_features:
                    preserved_stats['price_min'] = min(
                        old_stat_features['price_min'],
                        new_stat_features['price_min']
                    )

                if 'price_max' in old_stat_features and 'price_max' in new_stat_features:
                    preserved_stats['price_max'] = max(
                        old_stat_features['price_max'],
                        new_stat_features['price_max']
                    )

                # Volatility - keep historical as it's more stable
                if 'returns_std' in old_stat_features:
                    preserved_stats['returns_std_historical'] = old_stat_features['returns_std']

                # Merge preserved stats
                if 'statistical_features' in merged_features:
                    merged_features['statistical_features'].update(preserved_stats)

            # Preserve technical indicators (latest values from new features)
            if 'technical_indicators' in new_features:
                merged_features['technical_indicators_updated_at'] = datetime.utcnow().isoformat()

            # Track data ranges
            if 'data_date_range' in current_profile and 'summary' in new_features:
                merged_features['cumulative_data_range'] = {
                    'first_point': current_profile['data_date_range'].get('start'),
                    'last_point': new_features.get('summary', {}).get('last_datetime'),
                    'total_points': (
                        current_profile.get('data_points_count', 0) +
                        new_features.get('summary', {}).get('total_records', 0)
                    )
                }

            logger.info(f"Merged historical and new features successfully")
            return merged_features

        except Exception as e:
            logger.error(f"Error merging features: {e}")
            return new_features

    def should_retrain_models(
        self,
        current_profile: Dict,
        new_data_points: int,
        retrain_threshold: int = 100
    ) -> bool:
        """
        Determine if ML models should be retrained based on new data

        Args:
            current_profile: Existing profile with model info
            new_data_points: Number of new data points
            retrain_threshold: Minimum new points to trigger retraining

        Returns:
            True if models should be retrained, False otherwise
        """
        try:
            # Always retrain if no existing models
            if 'models' not in current_profile:
                logger.info("No existing models found, will train new models")
                return True

            # Check if we have enough new data
            if new_data_points < retrain_threshold:
                logger.info(f"Only {new_data_points} new points (threshold: {retrain_threshold}), skipping retraining")
                return False

            # Check model age
            if 'trained_at' in current_profile.get('models', {}):
                trained_time = pd.to_datetime(current_profile['models']['trained_at'])
                age_days = (datetime.utcnow() - trained_time).days

                if age_days > 7:  # Retrain if older than 7 days
                    logger.info(f"Models are {age_days} days old, will retrain")
                    return True

            logger.info("Models are recent and have few new points, skipping retraining")
            return False

        except Exception as e:
            logger.error(f"Error checking if retraining needed: {e}")
            return True  # Default to True (be conservative)

    def calculate_update_efficiency(
        self,
        historical_data_points: int,
        new_data_points: int
    ) -> Dict:
        """
        Calculate efficiency metrics for incremental vs full reprocessing

        Args:
            historical_data_points: Total historical data points
            new_data_points: Number of new data points

        Returns:
            Dictionary with efficiency metrics
        """
        total_points = historical_data_points + new_data_points
        new_percentage = (new_data_points / total_points * 100) if total_points > 0 else 0

        efficiency = {
            'historical_points': historical_data_points,
            'new_points': new_data_points,
            'total_points': total_points,
            'new_data_percentage': round(new_percentage, 2),
            'incremental_vs_full_ratio': round(new_data_points / total_points, 4),
            'processing_time_saved_percentage': round(100 - new_percentage, 2)
        }

        logger.info(
            f"Update efficiency: {new_percentage:.1f}% new data, "
            f"~{efficiency['processing_time_saved_percentage']:.1f}% processing time saved"
        )

        return efficiency

    def create_incremental_update_plan(
        self,
        symbol: str,
        current_profile: Optional[Dict],
        new_data: pd.DataFrame,
        new_features: Dict
    ) -> Dict:
        """
        Create a plan for efficiently updating the profile

        Args:
            symbol: Stock symbol
            current_profile: Existing profile (or None for new symbols)
            new_data: Newly fetched data
            new_features: Newly engineered features

        Returns:
            Update plan with strategy and efficiency metrics
        """
        try:
            plan = {
                'symbol': symbol,
                'strategy': 'incremental' if current_profile else 'full_backfill',
                'created_at': datetime.utcnow().isoformat()
            }

            if not current_profile:
                # First time processing this symbol
                plan['action'] = 'create_new_profile'
                plan['data_points'] = len(new_data)
                plan['retrain_models'] = True
                logger.info(f"{symbol}: First time processing, will create new profile")
            else:
                # Incremental update
                new_data_only = self.get_new_data_since_last_update(current_profile, new_data)

                plan['action'] = 'incremental_update' if len(new_data_only) > 0 else 'no_new_data'
                plan['new_data_points'] = len(new_data_only)
                plan['historical_data_points'] = current_profile.get('data_points_count', 0)
                plan['efficiency'] = self.calculate_update_efficiency(
                    plan['historical_data_points'],
                    plan['new_data_points']
                )
                plan['retrain_models'] = self.should_retrain_models(
                    current_profile,
                    len(new_data_only)
                )

                if plan['action'] == 'incremental_update':
                    logger.info(
                        f"{symbol}: Incremental update plan - "
                        f"{len(new_data_only)} new points, "
                        f"retrain={'yes' if plan['retrain_models'] else 'no'}"
                    )
                else:
                    logger.info(f"{symbol}: No new data since last update")

            return plan

        except Exception as e:
            logger.error(f"Error creating update plan for {symbol}: {e}")
            return {
                'symbol': symbol,
                'strategy': 'error',
                'error': str(e)
            }

