"""
ML Model Training Module
Trains machine learning models on processed features and stores results in MongoDB
"""
import numpy as np
import pandas as pd
from datetime import datetime
from typing import Dict, Optional, Tuple
from loguru import logger
import joblib
from pathlib import Path
import json

from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor, RandomForestClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, r2_score, accuracy_score, precision_score, recall_score, f1_score


class MLModelTrainer:
    """
    Trains ML models on stock features
    Creates both regression (price prediction) and classification (direction prediction) models
    """

    def __init__(self, progress_callback=None):
        """
        Initialize model trainer

        Args:
            progress_callback: Optional callback function(stage: str, progress: int) for progress updates
        """
        self.progress_callback = progress_callback
        self.models = {}
        self.scalers = {}
        self.metrics = {}

    def _report_progress(self, stage: str, progress: int = None):
        """Report progress if callback is set"""
        if self.progress_callback:
            self.progress_callback(stage, progress)

    def prepare_training_data(self, features: Dict, df: pd.DataFrame) -> Tuple[pd.DataFrame, pd.Series, pd.Series]:
        """
        Prepare features and labels for training

        Args:
            features: Dictionary of engineered features from FeatureEngineer
            df: Raw DataFrame with price data

        Returns:
            Tuple of (X_train, y_regression, y_classification)
        """
        self._report_progress('ML: Preparing training data', 52)

        # Extract features into DataFrame
        feature_cols = []
        X_data = {}

        # Technical indicators
        if 'technical_indicators' in features:
            for col, val in features['technical_indicators'].items():
                if isinstance(val, (int, float)) and not np.isnan(val):
                    X_data[f'tech_{col}'] = val
                    feature_cols.append(f'tech_{col}')

        # Statistical features
        if 'statistical_features' in features:
            for col, val in features['statistical_features'].items():
                if isinstance(val, (int, float)) and not np.isnan(val):
                    X_data[f'stat_{col}'] = val
                    feature_cols.append(f'stat_{col}')

        # Risk metrics
        if 'risk_metrics' in features:
            for col, val in features['risk_metrics'].items():
                if isinstance(val, (int, float)) and not np.isnan(val):
                    X_data[f'risk_{col}'] = val
                    feature_cols.append(f'risk_{col}')

        # Multi-timeframe
        if 'multi_timeframe' in features:
            for col, val in features['multi_timeframe'].items():
                if isinstance(val, (int, float)) and not np.isnan(val):
                    X_data[f'mtf_{col}'] = val
                    feature_cols.append(f'mtf_{col}')

        # Create feature matrix
        X = pd.DataFrame([X_data])

        # Create regression target: next day return
        if len(df) > 1:
            next_return = (df['close'].iloc[-1] - df['close'].iloc[-2]) / df['close'].iloc[-2]
        else:
            next_return = 0.0

        y_regression = pd.Series([next_return])

        # Create classification target: direction (1=up, 0=down/flat)
        y_classification = pd.Series([1 if next_return > 0 else 0])

        self._report_progress('ML: Data prepared', 54)

        return X, y_regression, y_classification

    def train_models(self, features: Dict, df: pd.DataFrame, symbol: str) -> Dict:
        """
        Train regression and classification models

        Args:
            features: Dictionary of engineered features
            df: Raw price data
            symbol: Stock symbol

        Returns:
            Dictionary with trained models and metrics
        """
        self._report_progress('ML: Training models', 55)

        try:
            X, y_regression, y_classification = self.prepare_training_data(features, df)

            # If not enough data, return dummy results
            if len(X) < 2 or len(y_regression) == 0:
                logger.warning(f"{symbol}: Not enough data for training, using placeholder model")
                return {
                    'status': 'insufficient_data',
                    'message': 'Not enough data points for training',
                    'models_trained': []
                }

            models_result = {
                'symbol': symbol,
                'trained_at': datetime.utcnow().isoformat(),
                'models_trained': [],
                'metrics': {}
            }

            # Train regression model (Random Forest for price prediction)
            self._report_progress('ML: Training regression model', 60)
            try:
                rf_reg = RandomForestRegressor(
                    n_estimators=50,
                    max_depth=10,
                    random_state=42,
                    n_jobs=-1
                )
                # Use features from entire dataset for training
                rf_reg.fit(X, y_regression)

                # Evaluate on same data (as baseline)
                y_pred = rf_reg.predict(X)
                mse = mean_squared_error(y_regression, y_pred)
                r2 = r2_score(y_regression, y_pred)

                models_result['models_trained'].append('regression_rf')
                models_result['metrics']['regression_rf'] = {
                    'mse': float(mse),
                    'rmse': float(np.sqrt(mse)),
                    'r2': float(r2),
                    'model_type': 'RandomForestRegressor'
                }
                self.models['regression_rf'] = rf_reg
                logger.info(f"{symbol}: Regression model trained - R²: {r2:.4f}")

            except Exception as e:
                logger.error(f"{symbol}: Failed to train regression model: {e}")

            # Train classification model (direction prediction)
            self._report_progress('ML: Training classification model', 65)
            try:
                rf_clf = RandomForestClassifier(
                    n_estimators=50,
                    max_depth=10,
                    random_state=42,
                    n_jobs=-1
                )
                rf_clf.fit(X, y_classification)

                # Evaluate
                y_pred = rf_clf.predict(X)
                accuracy = accuracy_score(y_classification, y_pred)
                precision = precision_score(y_classification, y_pred, zero_division=0)
                recall = recall_score(y_classification, y_pred, zero_division=0)
                f1 = f1_score(y_classification, y_pred, zero_division=0)

                models_result['models_trained'].append('classification_rf')
                models_result['metrics']['classification_rf'] = {
                    'accuracy': float(accuracy),
                    'precision': float(precision),
                    'recall': float(recall),
                    'f1': float(f1),
                    'model_type': 'RandomForestClassifier'
                }
                self.models['classification_rf'] = rf_clf
                logger.info(f"{symbol}: Classification model trained - Accuracy: {accuracy:.4f}")

            except Exception as e:
                logger.error(f"{symbol}: Failed to train classification model: {e}")

            # Train gradient boosting regression (more advanced)
            self._report_progress('ML: Training gradient boosting model', 70)
            try:
                gb_reg = GradientBoostingRegressor(
                    n_estimators=50,
                    max_depth=5,
                    learning_rate=0.1,
                    random_state=42
                )
                gb_reg.fit(X, y_regression)

                y_pred = gb_reg.predict(X)
                mse = mean_squared_error(y_regression, y_pred)
                r2 = r2_score(y_regression, y_pred)

                models_result['models_trained'].append('regression_gb')
                models_result['metrics']['regression_gb'] = {
                    'mse': float(mse),
                    'rmse': float(np.sqrt(mse)),
                    'r2': float(r2),
                    'model_type': 'GradientBoostingRegressor'
                }
                self.models['regression_gb'] = gb_reg
                logger.info(f"{symbol}: Gradient Boosting model trained - R²: {r2:.4f}")

            except Exception as e:
                logger.error(f"{symbol}: Failed to train gradient boosting model: {e}")

            self._report_progress('ML: Models trained successfully', 72)

            return models_result

        except Exception as e:
            logger.error(f"{symbol}: Error during model training: {e}")
            return {
                'status': 'error',
                'error': str(e),
                'models_trained': []
            }

    def create_ml_profile(self, symbol: str, models_result: Dict, features: Dict) -> Dict:
        """
        Create ML profile with trained models and metadata

        Args:
            symbol: Stock symbol
            models_result: Result from train_models()
            features: Engineered features dictionary

        Returns:
            ML profile dictionary for MongoDB storage
        """
        ml_profile = {
            'symbol': symbol,
            'profile_type': 'ml',
            'created_at': datetime.utcnow().isoformat(),
            'models': models_result,
            'feature_count': len([f for f in features.keys() if f.endswith('features')]),
            'training_data_size': features.get('summary', {}).get('total_records', 0),
            'status': 'trained' if models_result.get('models_trained') else 'failed'
        }

        return ml_profile

    def create_statistical_profile(self, symbol: str, features: Dict) -> Dict:
        """
        Create statistical profile from engineered features

        Args:
            symbol: Stock symbol
            features: Engineered features dictionary

        Returns:
            Statistical profile dictionary for MongoDB storage
        """
        statistical_profile = {
            'symbol': symbol,
            'profile_type': 'statistical',
            'created_at': datetime.utcnow().isoformat(),
            'features': {
                'technical_indicators': features.get('technical_indicators', {}),
                'statistical_features': features.get('statistical_features', {}),
                'risk_metrics': features.get('risk_metrics', {}),
                'volatility_features': features.get('volatility_features', {}),
                'multi_timeframe': features.get('multi_timeframe', {}),
                'regime_features': features.get('regime_features', {})
            },
            'summary': features.get('summary', {}),
            'status': 'ready'
        }

        return statistical_profile

