"""
Feature engineering module for deriving statistical and ML features
"""
import pandas as pd
import numpy as np
from typing import Dict, List, Optional
from scipy import stats
from scipy.stats import skew, kurtosis
from sklearn.preprocessing import StandardScaler
from loguru import logger
import warnings
warnings.filterwarnings('ignore')
import statsmodels.api as sm
from statsmodels.tsa.stattools import adfuller, acf
from datetime import datetime

try:
    import pandas_ta as pta  # optional advanced TA
except ImportError:  # safe fallback
    pta = None


class FeatureEngineer:
    """Derives comprehensive statistical and ML features from minute data"""

    def __init__(self, progress_callback=None):
        """Initialize the feature engineer

        Args:
            progress_callback: Optional callback function(stage_name: str, progress: int) for progress updates
        """
        self.scaler = StandardScaler()
        self.progress_callback = progress_callback

    def _report_progress(self, stage: str, progress: int = None):
        """Report progress if callback is set"""
        if self.progress_callback:
            self.progress_callback(stage, progress)

    def calculate_technical_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Calculate technical indicators

        Args:
            df: DataFrame with OHLCV data

        Returns:
            DataFrame with added technical indicators
        """
        if df.empty:
            return df

        df = df.copy()

        self._report_progress('Technical: Moving Averages', 52)

        # Moving Averages
        for window in [5, 10, 20, 50, 100, 200]:
            df[f'sma_{window}'] = df['close'].rolling(window=window).mean()
            df[f'ema_{window}'] = df['close'].ewm(span=window, adjust=False).mean()

        self._report_progress('Technical: Bollinger Bands', 54)

        # Bollinger Bands
        for window in [20, 50]:
            rolling_mean = df['close'].rolling(window=window).mean()
            rolling_std = df['close'].rolling(window=window).std()
            df[f'bb_upper_{window}'] = rolling_mean + (rolling_std * 2)
            df[f'bb_lower_{window}'] = rolling_mean - (rolling_std * 2)
            df[f'bb_middle_{window}'] = rolling_mean
            df[f'bb_width_{window}'] = (df[f'bb_upper_{window}'] - df[f'bb_lower_{window}']) / rolling_mean

        self._report_progress('Technical: RSI', 56)

        # RSI (Relative Strength Index)
        for period in [14, 28]:
            delta = df['close'].diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
            rs = gain / loss
            df[f'rsi_{period}'] = 100 - (100 / (1 + rs))

        self._report_progress('Technical: MACD', 58)

        # MACD
        exp1 = df['close'].ewm(span=12, adjust=False).mean()
        exp2 = df['close'].ewm(span=26, adjust=False).mean()
        df['macd'] = exp1 - exp2
        df['macd_signal'] = df['macd'].ewm(span=9, adjust=False).mean()
        df['macd_histogram'] = df['macd'] - df['macd_signal']

        self._report_progress('Technical: ATR & Stochastic', 60)

        # ATR (Average True Range)
        high_low = df['high'] - df['low']
        high_close = np.abs(df['high'] - df['close'].shift())
        low_close = np.abs(df['low'] - df['close'].shift())
        ranges = pd.concat([high_low, high_close, low_close], axis=1)
        true_range = np.max(ranges, axis=1)
        df['atr_14'] = true_range.rolling(14).mean()

        # Stochastic Oscillator
        for period in [14]:
            low_min = df['low'].rolling(window=period).min()
            high_max = df['high'].rolling(window=period).max()
            df[f'stoch_{period}'] = 100 * (df['close'] - low_min) / (high_max - low_min)
            df[f'stoch_{period}_sma'] = df[f'stoch_{period}'].rolling(window=3).mean()

        self._report_progress('Technical: Volume & Momentum', 62)

        # Volume indicators
        df['volume_sma_20'] = df['volume'].rolling(window=20).mean()
        df['volume_ratio'] = df['volume'] / df['volume_sma_20']

        # Price momentum
        for period in [1, 5, 10, 20, 60]:
            df[f'momentum_{period}'] = df['close'].pct_change(period)

        # Rate of Change (ROC)
        for period in [10, 20]:
            df[f'roc_{period}'] = ((df['close'] - df['close'].shift(period)) / df['close'].shift(period)) * 100

        return df

    def calculate_statistical_features(self, df: pd.DataFrame) -> Dict:
        """
        Calculate statistical features from the data

        Args:
            df: DataFrame with price data

        Returns:
            Dictionary of statistical features
        """
        if df.empty:
            return {}

        features = {}

        self._report_progress('Statistical: Basic stats', 64)

        # Price statistics
        self._report_progress('Statistical: Computing price statistics', 64)
        features['price_mean'] = df['close'].mean()
        features['price_median'] = df['close'].median()
        features['price_std'] = df['close'].std()
        features['price_var'] = df['close'].var()
        features['price_min'] = df['close'].min()
        features['price_max'] = df['close'].max()
        features['price_range'] = features['price_max'] - features['price_min']
        features['price_skewness'] = skew(df['close'].dropna())
        features['price_kurtosis'] = kurtosis(df['close'].dropna())

        # Returns statistics
        self._report_progress('Statistical: Computing returns', 65)
        returns = df['close'].pct_change().dropna()
        features['returns_mean'] = returns.mean()
        features['returns_std'] = returns.std()
        features['returns_skewness'] = skew(returns)
        features['returns_kurtosis'] = kurtosis(returns)
        features['sharpe_ratio'] = (returns.mean() / returns.std()) * np.sqrt(252 * 390) if returns.std() != 0 else 0

        # Volume statistics
        self._report_progress('Statistical: Computing volume', 66)
        features['volume_mean'] = df['volume'].mean()
        features['volume_median'] = df['volume'].median()
        features['volume_std'] = df['volume'].std()
        features['volume_skewness'] = skew(df['volume'].dropna())

        # Volatility measures
        self._report_progress('Statistical: Computing volatility', 67)
        features['volatility_intraday'] = ((df['high'] - df['low']) / df['close']).mean()
        features['volatility_close_to_close'] = df['close'].pct_change().std()

        # Trend statistics
        self._report_progress('Statistical: Computing trend', 68)
        if len(df) > 1:
            x = np.arange(len(df))
            slope, intercept, r_value, p_value, std_err = stats.linregress(x, df['close'].values)
            features['trend_slope'] = slope
            features['trend_r_squared'] = r_value ** 2
            features['trend_p_value'] = p_value

        # Price levels
        self._report_progress('Statistical: Price levels', 69)
        features['current_price'] = df['close'].iloc[-1] if len(df) > 0 else 0
        features['opening_price'] = df['open'].iloc[0] if len(df) > 0 else 0
        features['closing_price'] = df['close'].iloc[-1] if len(df) > 0 else 0
        features['intraday_return'] = ((features['closing_price'] - features['opening_price']) /
                                       features['opening_price']) if features['opening_price'] != 0 else 0

        return features

    def calculate_time_based_features(self, df: pd.DataFrame) -> Dict:
        """
        Calculate time-based features

        Args:
            df: DataFrame with datetime index

        Returns:
            Dictionary of time-based features
        """
        if df.empty or 'datetime' not in df.columns:
            return {}

        features = {}

        df = df.copy()
        df['hour'] = pd.to_datetime(df['datetime']).dt.hour
        df['minute'] = pd.to_datetime(df['datetime']).dt.minute
        df['day_of_week'] = pd.to_datetime(df['datetime']).dt.dayofweek

        # Trading session patterns
        features['morning_avg_volume'] = df[df['hour'] < 12]['volume'].mean()
        features['afternoon_avg_volume'] = df[df['hour'] >= 12]['volume'].mean()

        features['morning_volatility'] = df[df['hour'] < 12]['close'].pct_change().std()
        features['afternoon_volatility'] = df[df['hour'] >= 12]['close'].pct_change().std()

        # First and last hour statistics
        features['first_hour_return'] = df[df['hour'] == df['hour'].min()]['close'].pct_change().sum()
        features['last_hour_return'] = df[df['hour'] == df['hour'].max()]['close'].pct_change().sum()

        return features

    def calculate_ml_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Calculate ML-ready features

        Args:
            df: DataFrame with technical indicators

        Returns:
            DataFrame with ML features
        """
        if df.empty:
            return df

        df = df.copy()

        # Lagged features
        for lag in [1, 5, 10, 20]:
            df[f'close_lag_{lag}'] = df['close'].shift(lag)
            df[f'volume_lag_{lag}'] = df['volume'].shift(lag)
            df[f'return_lag_{lag}'] = df['close'].pct_change().shift(lag)

        # Rolling statistics
        for window in [10, 20, 50]:
            df[f'rolling_mean_{window}'] = df['close'].rolling(window=window).mean()
            df[f'rolling_std_{window}'] = df['close'].rolling(window=window).std()
            df[f'rolling_min_{window}'] = df['close'].rolling(window=window).min()
            df[f'rolling_max_{window}'] = df['close'].rolling(window=window).max()

        # Price position indicators
        for window in [20, 50]:
            rolling_min = df['close'].rolling(window=window).min()
            rolling_max = df['close'].rolling(window=window).max()
            df[f'price_position_{window}'] = ((df['close'] - rolling_min) /
                                              (rolling_max - rolling_min))

        # Volume changes
        df['volume_change'] = df['volume'].pct_change()
        df['volume_acceleration'] = df['volume_change'].diff()

        # Price patterns
        df['higher_high'] = ((df['high'] > df['high'].shift(1)) &
                            (df['high'].shift(1) > df['high'].shift(2))).astype(int)
        df['lower_low'] = ((df['low'] < df['low'].shift(1)) &
                          (df['low'].shift(1) < df['low'].shift(2))).astype(int)

        # Candlestick features
        df['body'] = df['close'] - df['open']
        df['body_pct'] = df['body'] / df['open']
        df['upper_shadow'] = df['high'] - df[['open', 'close']].max(axis=1)
        df['lower_shadow'] = df[['open', 'close']].min(axis=1) - df['low']
        df['shadow_ratio'] = (df['upper_shadow'] + df['lower_shadow']) / df['body'].abs()

        return df

    def calculate_granular_minute_features(self, df: pd.DataFrame) -> Dict:
        """
        Calculate granular minute-level analysis features
        
        Args:
            df: DataFrame with OHLCV minute data
            
        Returns:
            Dictionary of granular minute-level features
        """
        if df.empty or 'datetime' not in df.columns:
            return {}
        
        features = {}
        
        # Intraday volatility patterns
        df_temp = df.copy()
        df_temp['datetime'] = pd.to_datetime(df_temp['datetime'])
        df_temp['hour'] = df_temp['datetime'].dt.hour
        df_temp['minute'] = df_temp['datetime'].dt.minute
        df_temp['returns'] = df_temp['close'].pct_change()
        
        # Volume-weighted volatility by hour
        hourly_vwap_vol = {}
        for hour in df_temp['hour'].unique():
            hour_data = df_temp[df_temp['hour'] == hour]
            if len(hour_data) > 1 and hour_data['volume'].sum() > 0:
                weighted_vol = np.sqrt(np.average(
                    hour_data['returns'].dropna()**2, 
                    weights=hour_data.loc[hour_data['returns'].notna(), 'volume']
                ))
                hourly_vwap_vol[int(hour)] = float(weighted_vol)
        
        features['hourly_vwap_volatility'] = hourly_vwap_vol
        
        # Minute-level liquidity metrics
        df_temp['volume_per_point'] = df_temp['volume'] / (df_temp['high'] - df_temp['low']).replace(0, np.nan)
        features['avg_liquidity_depth'] = float(df_temp['volume_per_point'].mean())
        features['liquidity_variability'] = float(df_temp['volume_per_point'].std())
        
        # Volume concentration (Gini coefficient for volume distribution)
        sorted_volume = np.sort(df_temp['volume'].values)
        n = len(sorted_volume)
        if n > 0:
            cumsum = np.cumsum(sorted_volume)
            gini = (2 * np.sum((np.arange(n) + 1) * sorted_volume)) / (n * cumsum[-1]) - (n + 1) / n
            features['volume_gini_coefficient'] = float(gini)
        
        # High-frequency price action patterns
        # Momentum bursts (rapid price movements)
        df_temp['price_acceleration'] = df_temp['returns'].diff()
        features['max_momentum_burst'] = float(df_temp['price_acceleration'].abs().max())
        features['avg_momentum_burst'] = float(df_temp['price_acceleration'].abs().mean())
        
        # Price reversals (count of sign changes in returns)
        sign_changes = (np.sign(df_temp['returns'].dropna()).diff() != 0).sum()
        features['price_reversal_count'] = int(sign_changes)
        features['price_reversal_frequency'] = float(sign_changes / len(df_temp) if len(df_temp) > 0 else 0)
        
        # Tick-level statistical anomalies
        # Z-score outliers in price movements
        returns_zscore = (df_temp['returns'] - df_temp['returns'].mean()) / df_temp['returns'].std()
        features['extreme_move_count_3sigma'] = int((returns_zscore.abs() > 3).sum())
        features['extreme_move_count_2sigma'] = int((returns_zscore.abs() > 2).sum())
        
        # Intraday volatility clustering (ARCH effects)
        if len(df_temp) >= 10:
            squared_returns = df_temp['returns'].dropna() ** 2
            # Autocorrelation of squared returns at lag 1 (proxy for ARCH)
            if len(squared_returns) > 1:
                arch_effect = squared_returns.autocorr(lag=1)
                features['volatility_clustering_coef'] = float(arch_effect) if not np.isnan(arch_effect) else 0.0
        
        # Trade intensity analysis
        # Average time between trades (approximated by minute intervals with volume)
        active_minutes = df_temp[df_temp['volume'] > 0]
        if len(active_minutes) > 1:
            features['active_trading_minutes'] = len(active_minutes)
            features['trading_intensity'] = float(len(active_minutes) / len(df_temp))
        
        # Price discovery metrics
        # Efficiency ratio: net price change / total price distance
        if len(df_temp) > 0:
            net_change = abs(df_temp['close'].iloc[-1] - df_temp['close'].iloc[0])
            total_distance = df_temp['returns'].abs().sum()
            features['price_efficiency_ratio'] = float(net_change / total_distance if total_distance > 0 else 0)
        
        return features

    def calculate_market_microstructure(self, df: pd.DataFrame) -> Dict:
        """
        Calculate market microstructure features

        Args:
            df: DataFrame with OHLCV data

        Returns:
            Dictionary of microstructure features
        """
        if df.empty:
            return {}

        features = {}

        # Spread measures
        df['spread'] = df['high'] - df['low']
        features['avg_spread'] = df['spread'].mean()
        features['spread_volatility'] = df['spread'].std()

        # Price impact
        df['price_change'] = df['close'].diff().abs()
        features['avg_price_impact'] = (df['price_change'] / df['volume']).mean()

        # Liquidity measures
        features['amihud_illiquidity'] = (df['close'].pct_change().abs() / df['volume']).mean()
        features['volume_weighted_price'] = (df['close'] * df['volume']).sum() / df['volume'].sum()

        # Order flow imbalance (approximation)
        df['returns'] = df['close'].pct_change()
        df['volume_signed'] = df['volume'] * np.sign(df['returns'])
        features['order_flow_imbalance'] = df['volume_signed'].sum() / df['volume'].sum()

        return features

    def _hurst_exponent(self, series: pd.Series) -> Optional[float]:
        if series.dropna().empty:
            return None
        ts = series.dropna().values
        lags = [2, 4, 8, 16, 32]
        if len(ts) < max(lags) + 5:
            return None
        variances = [np.var(ts[lag:] - ts[:-lag]) for lag in lags]
        try:
            log_lags = np.log(lags)
            log_vars = np.log(variances)
            slope, _, _, _, _ = stats.linregress(log_lags, log_vars)
            return 0.5 * slope
        except Exception:
            return None

    def _hill_tail_index(self, returns: pd.Series, tail_fraction: float = 0.05) -> Optional[float]:
        r = returns.dropna()
        if r.empty:
            return None
        tail_cut = int(len(r) * tail_fraction)
        if tail_cut < 5:
            return None
        tail = np.sort(np.abs(r[r < r.quantile(tail_fraction)]))
        if len(tail) == 0:
            return None
        m = len(tail)
        x_m = tail[0]
        try:
            hill = (1 / m) * np.sum(np.log(tail / x_m))
            return float(hill)
        except Exception:
            return None

    def calculate_advanced_technical(self, df: pd.DataFrame) -> pd.DataFrame:
        if df.empty:
            return df
        df = df.copy()
        # VWAP
        if all(c in df.columns for c in ['high','low','close','volume']):
            typical = (df['high'] + df['low'] + df['close']) / 3
            df['vwap'] = (typical * df['volume']).cumsum() / df['volume'].cumsum()
        # OBV
        if 'close' in df.columns and 'volume' in df.columns:
            direction = df['close'].diff().apply(lambda x: 1 if x>0 else (-1 if x<0 else 0))
            df['obv'] = (direction * df['volume']).cumsum()
        # Chaikin Money Flow (CMF)
        if all(c in df.columns for c in ['high','low','close','volume']):
            mfm = ((df['close'] - df['low']) - (df['high'] - df['close'])) / (df['high'] - df['low']).replace(0, np.nan)
            df['cmf_20'] = (mfm * df['volume']).rolling(20).sum() / df['volume'].rolling(20).sum()
        # KAMA (Efficiency Ratio based EMA)
        if 'close' in df.columns:
            window = 10
            change = abs(df['close'] - df['close'].shift(window))
            volatility = df['close'].diff().abs().rolling(window).sum()
            er = (change / volatility).replace([np.inf, -np.inf], np.nan)
            sc = (er * (2/(2+1) - 2/(30+1)) + 2/(30+1))**2
            kama = []
            prev = df['close'].iloc[0]
            for i, (price, s) in enumerate(zip(df['close'], sc)):
                if i == 0 or pd.isna(s):
                    kama.append(price)
                else:
                    prev = prev + s * (price - prev)
                    kama.append(prev)
            df['kama_10_30'] = kama
        # If pandas_ta available add a couple extra indicators
        if pta is not None:
            try:
                df['pvo'] = pta.pvo(df['volume']).iloc[:,0]
            except Exception:
                pass
        return df

    def calculate_multi_timeframe_features(self, df: pd.DataFrame) -> Dict:
        # (legacy kept for backward compat) wrapper now calls new method
        metrics, frames = self._multi_timeframe_metrics_and_frames(df)
        return metrics

    def _multi_timeframe_metrics_and_frames(self, df: pd.DataFrame):
        if df.empty or 'datetime' not in df.columns:
            return {}, {}
        metrics = {}
        frames = {}
        tmp = df.copy()
        tmp.set_index('datetime', inplace=True)
        # Enhanced timeframes: added 2m, 3m, 30m
        spec = {'2m': '2T', '3m': '3T', '5m': '5T', '15m': '15T', '30m': '30T', '1h': '1H', '1d': '1D'}
        
        all_returns = {}
        for label, rule in spec.items():
            try:
                agg = tmp.resample(rule).agg({'open':'first','high':'max','low':'min','close':'last','volume':'sum'})
                agg = agg.dropna(how='all')
                if len(agg)==0:
                    continue
                frames[label] = agg.reset_index()
                r = agg['close'].pct_change().dropna()
                all_returns[label] = r
                
                metrics[f'{label}_volatility'] = r.std()
                metrics[f'{label}_avg_volume'] = agg['volume'].mean()
                metrics[f'{label}_return'] = (agg['close'].iloc[-1]-agg['close'].iloc[0])/agg['close'].iloc[0]
                metrics[f'{label}_trend_slope'] = stats.linregress(np.arange(len(agg)), agg['close']).slope if len(agg)>1 else None
                
                # Timeframe-specific regime detection
                if len(r) >= 20:
                    vol_mean = r.std()
                    vol_rolling = r.rolling(10).std()
                    if not vol_rolling.empty:
                        current_vol = vol_rolling.iloc[-1]
                        if current_vol < vol_mean * 0.7:
                            metrics[f'{label}_regime'] = 'low_volatility'
                        elif current_vol > vol_mean * 1.3:
                            metrics[f'{label}_regime'] = 'high_volatility'
                        else:
                            metrics[f'{label}_regime'] = 'normal'
                
                # Add momentum indicators per timeframe
                if len(agg) >= 5:
                    rsi_period = min(14, len(agg) // 2)
                    if rsi_period >= 2:
                        delta = agg['close'].diff()
                        gain = (delta.where(delta > 0, 0)).rolling(window=rsi_period).mean()
                        loss = (-delta.where(delta < 0, 0)).rolling(window=rsi_period).mean()
                        rs = gain / loss.replace(0, np.nan)
                        rsi = 100 - (100 / (1 + rs))
                        if not rsi.empty and not np.isnan(rsi.iloc[-1]):
                            metrics[f'{label}_rsi'] = float(rsi.iloc[-1])
                
            except Exception:
                continue
        
        # Cross-timeframe correlation analysis
        if len(all_returns) >= 2:
            correlation_matrix = {}
            timeframes = list(all_returns.keys())
            for i, tf1 in enumerate(timeframes):
                for tf2 in timeframes[i+1:]:
                    # Align the two return series
                    try:
                        r1 = all_returns[tf1]
                        r2 = all_returns[tf2]
                        # Use overlapping indices
                        common_len = min(len(r1), len(r2))
                        if common_len >= 5:
                            corr = np.corrcoef(r1.iloc[-common_len:], r2.iloc[-common_len:])[0, 1]
                            if not np.isnan(corr):
                                correlation_matrix[f'{tf1}_vs_{tf2}'] = float(corr)
                    except Exception:
                        continue
            
            if correlation_matrix:
                metrics['timeframe_correlations'] = correlation_matrix
        
        return metrics, frames

    def generate_predictive_label_series(self, df: pd.DataFrame, horizons=None) -> pd.DataFrame:
        if horizons is None:
            horizons = [1,5,15,30]
        if df.empty or 'close' not in df.columns:
            return pd.DataFrame(index=df.index)
        out = pd.DataFrame(index=df.index)
        close = df['close'].astype(float)
        high = df.get('high', close)
        low = df.get('low', close)
        returns = close.pct_change()
        for h in horizons:
            # Forward return series: shift(-h)
            fr = (close.shift(-h) - close) / close
            out[f'next_{h}m_return'] = fr
            # Realized vol next h minutes: std of future returns window
            realized_vol = returns.shift(-1).rolling(h).std()
            out[f'next_{h}m_realized_vol'] = realized_vol
            # Parkinson volatility next h (use future high/low window)
            hl = (np.log(high/low)**2).shift(-1).rolling(h).sum()
            out[f'next_{h}m_parkinson_vol'] = np.sqrt(hl/(4*h*np.log(2)))
            # Max drawdown next h: compute using future window prices (vectorized)
            future_prices = close.shift(-1).fillna(method='ffill').values

            # Vectorized max drawdown calculation
            md_series = np.full(len(close), np.nan)
            for i in range(len(close) - h):
                window = future_prices[i:i+h]
                if len(window) == h:
                    cum = np.cumprod(1 + np.diff(window, prepend=window[0])/np.maximum(window[0], 1e-10))
                    run_max = np.maximum.accumulate(cum)
                    dd = (cum - run_max) / np.maximum(run_max, 1e-10)
                    md_series[i] = np.min(dd)
            out[f'next_{h}m_max_drawdown'] = md_series
            # VaR 95 proxy using past returns (no leakage)
            past_ret_window = returns.iloc[:].rolling(h).apply(lambda x: np.nanquantile(x,0.05), raw=False)
            out[f'next_{h}m_var_95'] = past_ret_window.shift(1)  # ensure not using current bar forward data
            # Direction classification (−1/0/1)
            out[f'next_{h}m_direction'] = out[f'next_{h}m_return'].apply(lambda x: np.nan if pd.isna(x) else (1 if x>0 else (-1 if x<0 else 0)))
            # Breakout flag (>2σ of past h returns, no forward leak)
            past_std = returns.rolling(h).std()
            out[f'next_{h}m_breakout'] = (out[f'next_{h}m_return'].abs() > 2*past_std).astype(int)
        # Regime conditional example for 30m low/high vol
        roll_vol = returns.rolling(60).std()
        q_low, q_high = roll_vol.quantile(0.3), roll_vol.quantile(0.7)
        cond_low = (roll_vol <= q_low)
        cond_high = (roll_vol >= q_high)
        h=30
        fr30 = (close.shift(-h) - close)/close
        out['next_30m_return_low_vol'] = fr30.where(cond_low)
        out['next_30m_return_high_vol'] = fr30.where(cond_high)
        return out

    def calculate_regime_features(self, df: pd.DataFrame) -> Dict:
        if df.empty or 'close' not in df.columns:
            return {}
        regimes = {}
        # Volatility regimes via rolling std of returns
        returns = df['close'].pct_change()
        roll_vol = returns.rolling(60).std()
        if roll_vol.dropna().empty:
            return {}
        q_low, q_med = roll_vol.quantile(0.33), roll_vol.quantile(0.66)
        latest_vol = roll_vol.iloc[-1]
        if latest_vol <= q_low:
            vol_regime = 'low'
        elif latest_vol <= q_med:
            vol_regime = 'medium'
        else:
            vol_regime = 'high'
        regimes['volatility_regime'] = vol_regime
        regimes['volatility_regime_probability'] = float((roll_vol <= latest_vol).mean())  # empirical CDF proxy
        # Trend regime via slope & MACD sign
        if 'macd' in df.columns and len(df) > 30:
            slope = stats.linregress(np.arange(len(df.tail(120))), df['close'].tail(120)).slope if len(df) >= 120 else stats.linregress(np.arange(len(df)), df['close']).slope
            macd_latest = df['macd'].iloc[-1]
            if slope > 0 and macd_latest > 0:
                regimes['trend_regime'] = 'strong_uptrend'
            elif slope < 0 and macd_latest < 0:
                regimes['trend_regime'] = 'strong_downtrend'
            elif abs(slope) < 1e-6:
                regimes['trend_regime'] = 'choppy'
            else:
                regimes['trend_regime'] = 'weak_trend'
        # Liquidity regime via volume z-score
        vol_mean = df['volume'].rolling(120).mean().iloc[-1] if len(df) >= 120 else df['volume'].mean()
        vol_std = df['volume'].rolling(120).std().iloc[-1] if len(df) >= 120 else df['volume'].std()
        latest_volume = df['volume'].iloc[-1]
        if vol_std and vol_std != 0:
            z = (latest_volume - vol_mean)/vol_std
            if z < -1:
                regimes['liquidity_regime'] = 'illiquid'
            elif z > 1:
                regimes['liquidity_regime'] = 'high_liquidity'
            else:
                regimes['liquidity_regime'] = 'normal'
        # Session regime (US market heuristic)
        if 'datetime' in df.columns:
            hour = pd.to_datetime(df['datetime'].iloc[-1]).hour
            if hour < 9:
                regimes['session_regime'] = 'pre_market'
            elif 9 <= hour < 10:
                regimes['session_regime'] = 'open'
            elif 10 <= hour < 15:
                regimes['session_regime'] = 'midday'
            elif 15 <= hour < 16:
                regimes['session_regime'] = 'power_hour'
            else:
                regimes['session_regime'] = 'close'
        # Add numeric codes mapping
        regime_codes = {
            'volatility_regime_code': {'low':0,'medium':1,'high':2}.get(regimes.get('volatility_regime'), None),
            'trend_regime_code': {'choppy':0,'weak_trend':1,'strong_uptrend':2,'strong_downtrend':3}.get(regimes.get('trend_regime'), None),
            'liquidity_regime_code': {'illiquid':0,'normal':1,'high_liquidity':2}.get(regimes.get('liquidity_regime'), None),
            'session_regime_code': {'pre_market':0,'open':1,'midday':2,'power_hour':3,'close':4}.get(regimes.get('session_regime'), None)
        }
        regimes.update(regime_codes)
        return regimes

    def calculate_predictive_labels(self, df: pd.DataFrame, horizons: List[int] = None) -> Dict:
        if horizons is None:
            horizons = [1,5,10,20,60]
        if df.empty:
            return {}
        labels = {}
        returns = df['close'].pct_change()
        for h in horizons:
            if len(returns) > h:
                fr = (df['close'].shift(-h) - df['close']) / df['close']
                # Use valid index (not shifted past data), fill NaN with 0
                idx = min(h, len(fr) - 1)
                val = fr.iloc[idx]
                labels[f'forward_return_{h}'] = float(val) if not pd.isna(val) else 0.0
        # Classification labels (next interval up/down > threshold)
        threshold = 0.001
        if len(returns) > 2:
            next_ret = returns.shift(-1)
            labels['next_move_up'] = int(next_ret.iloc[-2] > threshold) if len(next_ret.dropna())>2 else int(next_ret.iloc[0] > threshold)
            labels['next_move_down'] = int(next_ret.iloc[-2] < -threshold) if len(next_ret.dropna())>2 else int(next_ret.iloc[0] < -threshold)
        return labels

    def calculate_regime_features(self, df: pd.DataFrame) -> Dict:
        if df.empty or 'close' not in df.columns:
            return {}
        regimes = {}
        # Volatility regimes via rolling std of returns
        returns = df['close'].pct_change()
        roll_vol = returns.rolling(60).std()
        if roll_vol.dropna().empty:
            return {}
        q_low, q_med = roll_vol.quantile(0.33), roll_vol.quantile(0.66)
        latest_vol = roll_vol.iloc[-1]
        if latest_vol <= q_low:
            vol_regime = 'low'
        elif latest_vol <= q_med:
            vol_regime = 'medium'
        else:
            vol_regime = 'high'
        regimes['volatility_regime'] = vol_regime
        regimes['volatility_regime_probability'] = float((roll_vol <= latest_vol).mean())  # empirical CDF proxy
        # Trend regime via slope & MACD sign
        if 'macd' in df.columns and len(df) > 30:
            slope = stats.linregress(np.arange(len(df.tail(120))), df['close'].tail(120)).slope if len(df) >= 120 else stats.linregress(np.arange(len(df)), df['close']).slope
            macd_latest = df['macd'].iloc[-1]
            if slope > 0 and macd_latest > 0:
                regimes['trend_regime'] = 'strong_uptrend'
            elif slope < 0 and macd_latest < 0:
                regimes['trend_regime'] = 'strong_downtrend'
            elif abs(slope) < 1e-6:
                regimes['trend_regime'] = 'choppy'
            else:
                regimes['trend_regime'] = 'weak_trend'
        # Liquidity regime via volume z-score
        vol_mean = df['volume'].rolling(120).mean().iloc[-1] if len(df) >= 120 else df['volume'].mean()
        vol_std = df['volume'].rolling(120).std().iloc[-1] if len(df) >= 120 else df['volume'].std()
        latest_volume = df['volume'].iloc[-1]
        if vol_std and vol_std != 0:
            z = (latest_volume - vol_mean)/vol_std
            if z < -1:
                regimes['liquidity_regime'] = 'illiquid'
            elif z > 1:
                regimes['liquidity_regime'] = 'high_liquidity'
            else:
                regimes['liquidity_regime'] = 'normal'
        # Session regime (US market heuristic)
        if 'datetime' in df.columns:
            hour = pd.to_datetime(df['datetime'].iloc[-1]).hour
            if hour < 9:
                regimes['session_regime'] = 'pre_market'
            elif 9 <= hour < 10:
                regimes['session_regime'] = 'open'
            elif 10 <= hour < 15:
                regimes['session_regime'] = 'midday'
            elif 15 <= hour < 16:
                regimes['session_regime'] = 'power_hour'
            else:
                regimes['session_regime'] = 'close'
        # Add numeric codes mapping
        regime_codes = {
            'volatility_regime_code': {'low':0,'medium':1,'high':2}.get(regimes.get('volatility_regime'), None),
            'trend_regime_code': {'choppy':0,'weak_trend':1,'strong_uptrend':2,'strong_downtrend':3}.get(regimes.get('trend_regime'), None),
            'liquidity_regime_code': {'illiquid':0,'normal':1,'high_liquidity':2}.get(regimes.get('liquidity_regime'), None),
            'session_regime_code': {'pre_market':0,'open':1,'midday':2,'power_hour':3,'close':4}.get(regimes.get('session_regime'), None)
        }
        regimes.update(regime_codes)
        return regimes


    def process_full_pipeline(self, df: pd.DataFrame) -> Dict:
        """
        Run the complete feature engineering pipeline

        Args:
            df: Raw OHLCV DataFrame

        Returns:
            Dictionary containing processed dataframe and all features
        """
        if df.empty:
            logger.warning("Empty dataframe provided to feature pipeline")
            return {
                'processed_df': pd.DataFrame(),
                'statistical_features': {},
                'time_features': {},
                'microstructure_features': {},
                'summary': {},
                'advanced_statistical': {},
                'multi_timeframe': {},
                'quality_metrics': {},
                'labels': {},
                'technical_extended_latest': {},
                'feature_metadata': {}
            }

        logger.info(f"Processing {len(df)} rows of data")

        # Calculate technical indicators
        df_with_indicators = self.calculate_technical_indicators(df)

        # Calculate ML features
        df_with_ml = self.calculate_ml_features(df_with_indicators)

        # Calculate statistical features
        statistical_features = self.calculate_statistical_features(df)

        # Calculate time-based features
        time_features = self.calculate_time_based_features(df)

        # Calculate microstructure features
        microstructure_features = self.calculate_market_microstructure(df)
        
        # Calculate granular minute-level features
        self._report_progress('Granular Analysis', 70)
        granular_features = self.calculate_granular_minute_features(df)

        # Advanced technical indicators
        df_adv = self.calculate_advanced_technical(df_with_ml)

        # Extract latest extended indicators
        latest_ext = {}
        if not df_adv.empty:
            latest_row = df_adv.iloc[-1]
            for col in ['vwap','obv','cmf_20','kama_10_30','pvo']:
                if col in df_adv.columns and pd.notna(latest_row.get(col)):
                    latest_ext[col] = float(latest_row[col])

        # Multi timeframe
        multi_tf, multi_frames = self._multi_timeframe_metrics_and_frames(df)

        # Quality metrics (basic implementation)
        quality = {
            'missing_values': int(df.isnull().sum().sum()),
            'duplicate_rows': int(df.duplicated().sum()),
            'total_rows': len(df),
            'data_completeness': 1 - (df.isnull().sum().sum() / (len(df) * len(df.columns))) if len(df) > 0 else 0
        }

        # Regime features
        regime_features = self.calculate_regime_features(df_adv)

        # Predictive labels (extended)
        predictive_labels = self.calculate_predictive_labels(df_adv)

        # Metadata
        feature_metadata = {
            'version': '2.0',
            'generation_timestamp': datetime.utcnow().isoformat(),
            'source_intervals': 'minute',
            'multi_timeframes': list(multi_tf.keys()),
            'label_horizons': [1,5,10,20,60]
        }

        # Merge into final return
        base_result = {
            'processed_df': df_adv,  # enriched dataframe
            'statistical_features': statistical_features,
            'time_features': time_features,
            'microstructure_features': microstructure_features,
            'granular_minute_features': granular_features,  # NEW: Granular minute analysis
            'summary': {
                'total_records': len(df),
                'date_range': {
                    'start': str(df['datetime'].min()) if 'datetime' in df.columns else None,
                    'end': str(df['datetime'].max()) if 'datetime' in df.columns else None
                },
                'data_quality': quality
            },
            'advanced_statistical': {},  # Placeholder for future advanced stats
            'multi_timeframe': multi_tf,
            'quality_metrics': quality,
            'labels': predictive_labels,  # Using predictive_labels as labels
            'technical_extended_latest': latest_ext,
            'feature_metadata': feature_metadata,
            'regime_features': regime_features,
            'predictive_labels': predictive_labels,
            'multi_timeframe_frames': multi_frames,
            'predictive_label_series': self.generate_predictive_label_series(df_adv)
        }
        logger.info("Feature engineering completed successfully")

        return base_result
