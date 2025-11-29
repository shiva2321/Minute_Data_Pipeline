"""
GPU-Accelerated Feature Engineering Module
Optimizes feature calculation for 1M+ datapoints using CUDA/GPU
"""
import numpy as np
import pandas as pd
from typing import Dict, Optional, Tuple
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

# Try to import GPU libraries, fallback to CPU if not available
GPU_AVAILABLE = False
try:
    import cupy as cp
    GPU_AVAILABLE = True
    logger.info("✅ CuPy (GPU support) loaded successfully")
except ImportError:
    logger.warning("⚠ CuPy not installed. GPU acceleration disabled. Install: pip install cupy-cuda11x")
    cp = None


class GPUAcceleratedFeatureEngineer:
    """
    GPU-optimized feature engineering for large datasets (1M+ datapoints)
    Automatically falls back to CPU if GPU unavailable
    """

    def __init__(self, use_gpu: bool = True, progress_callback=None):
        """
        Initialize GPU feature engineer

        Args:
            use_gpu: Enable GPU if available
            progress_callback: Optional callback for progress updates
        """
        self.use_gpu = use_gpu and GPU_AVAILABLE
        self.progress_callback = progress_callback
        self.gpu_available = GPU_AVAILABLE

        if self.use_gpu:
            logger.info("🚀 GPU acceleration ENABLED")
        else:
            logger.info("⚠ GPU acceleration DISABLED (CPU mode)")

    def _report_progress(self, stage: str, progress: int = None):
        """Report progress"""
        if self.progress_callback:
            self.progress_callback(stage, progress)
        else:
            logger.info(f"{stage}: {progress}%")

    def calculate_technical_indicators_gpu(
        self,
        df: pd.DataFrame,
        windows: Dict[str, list] = None
    ) -> Dict:
        """
        GPU-accelerated technical indicators calculation

        Args:
            df: DataFrame with OHLCV data
            windows: Indicator windows to calculate

        Returns:
            Dictionary of calculated indicators
        """
        if not self.use_gpu:
            return self._calculate_cpu_fallback(df)

        try:
            self._report_progress("GPU: Computing technical indicators", 52)

            close = df['close'].values
            high = df['high'].values
            low = df['low'].values
            volume = df['volume'].values

            # Transfer to GPU
            gpu_close = cp.asarray(close, dtype=cp.float32)
            gpu_high = cp.asarray(high, dtype=cp.float32)
            gpu_low = cp.asarray(low, dtype=cp.float32)
            gpu_volume = cp.asarray(volume, dtype=cp.float32)

            indicators = {}

            # GPU-accelerated Moving Averages
            self._report_progress("GPU: Computing Moving Averages", 54)
            for window in [5, 10, 20, 50, 100, 200]:
                indicators[f'sma_{window}'] = float(cp.asnumpy(self._gpu_sma(gpu_close, window))[-1])
                indicators[f'ema_{window}'] = float(cp.asnumpy(self._gpu_ema(gpu_close, window))[-1])

            # GPU-accelerated RSI
            self._report_progress("GPU: Computing RSI", 56)
            for period in [14, 28]:
                indicators[f'rsi_{period}'] = float(cp.asnumpy(self._gpu_rsi(gpu_close, period))[-1])

            # GPU-accelerated MACD
            self._report_progress("GPU: Computing MACD", 58)
            macd_result = self._gpu_macd(gpu_close)
            indicators['macd'] = float(cp.asnumpy(macd_result['macd'])[-1])
            indicators['macd_signal'] = float(cp.asnumpy(macd_result['signal'])[-1])

            # GPU-accelerated Bollinger Bands
            self._report_progress("GPU: Computing Bollinger Bands", 60)
            for window in [20, 50]:
                bb_result = self._gpu_bollinger_bands(gpu_close, window)
                indicators[f'bb_upper_{window}'] = float(cp.asnumpy(bb_result['upper'])[-1])
                indicators[f'bb_lower_{window}'] = float(cp.asnumpy(bb_result['lower'])[-1])
                indicators[f'bb_middle_{window}'] = float(cp.asnumpy(bb_result['middle'])[-1])

            # GPU-accelerated ATR
            self._report_progress("GPU: Computing ATR", 62)
            atr_result = self._gpu_atr(gpu_high, gpu_low, gpu_close, 14)
            indicators['atr_14'] = float(cp.asnumpy(atr_result)[-1])

            # GPU-accelerated Stochastic
            self._report_progress("GPU: Computing Stochastic", 64)
            stoch_result = self._gpu_stochastic(gpu_high, gpu_low, gpu_close, 14)
            indicators['stoch_14'] = float(cp.asnumpy(stoch_result)[-1])

            # GPU-accelerated Volume indicators
            self._report_progress("GPU: Computing Volume indicators", 66)
            indicators['volume_ratio'] = float(cp.asnumpy(gpu_volume[-1] / cp.mean(gpu_volume[-20:]))[-1])

            self._report_progress("GPU: Technical indicators complete", 68)
            logger.info(f"✅ GPU computed {len(indicators)} technical indicators")

            return indicators

        except Exception as e:
            logger.error(f"GPU calculation failed: {e}. Falling back to CPU.")
            return self._calculate_cpu_fallback(df)

    def calculate_statistical_features_gpu(self, data: np.ndarray) -> Dict:
        """GPU-accelerated statistical features calculation"""
        if not self.use_gpu:
            return self._calculate_statistical_cpu_fallback(data)

        try:
            self._report_progress("GPU: Computing statistical features", 64)

            gpu_data = cp.asarray(data, dtype=cp.float32)

            features = {
                'price_mean': float(cp.mean(gpu_data)),
                'price_median': float(cp.median(gpu_data)),
                'price_std': float(cp.std(gpu_data)),
                'price_var': float(cp.var(gpu_data)),
                'price_min': float(cp.min(gpu_data)),
                'price_max': float(cp.max(gpu_data)),
                'price_skew': float(cp.mean(((gpu_data - cp.mean(gpu_data)) / (cp.std(gpu_data) + 1e-10)) ** 3)),
                'price_kurtosis': float(cp.mean(((gpu_data - cp.mean(gpu_data)) / (cp.std(gpu_data) + 1e-10)) ** 4) - 3),
            }

            logger.info(f"✅ GPU computed {len(features)} statistical features")
            return features

        except Exception as e:
            logger.error(f"GPU statistical calculation failed: {e}")
            return self._calculate_statistical_cpu_fallback(data)

    # ========================================================================
    # GPU Helper Functions (Fast Implementations)
    # ========================================================================

    @staticmethod
    def _gpu_sma(prices: 'cp.ndarray', period: int) -> 'cp.ndarray':
        """GPU-accelerated Simple Moving Average using convolution"""
        kernel = cp.ones(period, dtype=cp.float32) / period
        return cp.convolve(prices, kernel, mode='same')

    @staticmethod
    def _gpu_ema(prices: 'cp.ndarray', period: int) -> 'cp.ndarray':
        """GPU-accelerated Exponential Moving Average"""
        alpha = 2.0 / (period + 1)
        ema = cp.zeros_like(prices)
        ema[0] = prices[0]

        for i in range(1, len(prices)):
            ema[i] = alpha * prices[i] + (1 - alpha) * ema[i - 1]

        return ema

    @staticmethod
    def _gpu_rsi(prices: 'cp.ndarray', period: int = 14) -> 'cp.ndarray':
        """GPU-accelerated Relative Strength Index"""
        delta = cp.diff(prices)
        gain = cp.where(delta > 0, delta, 0)
        loss = cp.where(delta < 0, -delta, 0)

        avg_gain = cp.convolve(gain, cp.ones(period, dtype=cp.float32) / period, mode='same')
        avg_loss = cp.convolve(loss, cp.ones(period, dtype=cp.float32) / period, mode='same')

        rs = avg_gain / (avg_loss + 1e-10)
        rsi = 100 - (100 / (1 + rs))

        return rsi

    @staticmethod
    def _gpu_macd(prices: 'cp.ndarray') -> Dict:
        """GPU-accelerated MACD calculation"""
        # EMA 12
        ema_12 = GPUAcceleratedFeatureEngineer._gpu_ema(prices, 12)
        # EMA 26
        ema_26 = GPUAcceleratedFeatureEngineer._gpu_ema(prices, 26)

        macd_line = ema_12 - ema_26

        # Signal line (EMA 9 of MACD)
        signal = GPUAcceleratedFeatureEngineer._gpu_ema(macd_line, 9)

        return {'macd': macd_line, 'signal': signal}

    @staticmethod
    def _gpu_bollinger_bands(
        prices: 'cp.ndarray',
        period: int = 20,
        std_dev: float = 2.0
    ) -> Dict:
        """GPU-accelerated Bollinger Bands"""
        kernel = cp.ones(period, dtype=cp.float32) / period
        sma = cp.convolve(prices, kernel, mode='same')

        # Rolling standard deviation
        variance = cp.zeros_like(prices)
        for i in range(period, len(prices)):
            variance[i] = cp.var(prices[i - period:i])

        std = cp.sqrt(variance + 1e-10)

        return {
            'upper': sma + (std_dev * std),
            'lower': sma - (std_dev * std),
            'middle': sma
        }

    @staticmethod
    def _gpu_atr(
        high: 'cp.ndarray',
        low: 'cp.ndarray',
        close: 'cp.ndarray',
        period: int = 14
    ) -> 'cp.ndarray':
        """GPU-accelerated Average True Range"""
        tr1 = high - low
        tr2 = cp.abs(high - cp.roll(close, 1))
        tr3 = cp.abs(low - cp.roll(close, 1))

        tr = cp.maximum(cp.maximum(tr1, tr2), tr3)

        atr = cp.zeros_like(tr)
        atr[period - 1] = cp.mean(tr[:period])

        for i in range(period, len(tr)):
            atr[i] = (atr[i - 1] * (period - 1) + tr[i]) / period

        return atr

    @staticmethod
    def _gpu_stochastic(
        high: 'cp.ndarray',
        low: 'cp.ndarray',
        close: 'cp.ndarray',
        period: int = 14
    ) -> 'cp.ndarray':
        """GPU-accelerated Stochastic Oscillator"""
        low_min = cp.zeros_like(close)
        high_max = cp.zeros_like(close)

        for i in range(period, len(close)):
            low_min[i] = cp.min(low[i - period:i])
            high_max[i] = cp.max(high[i - period:i])

        stoch = 100 * (close - low_min) / (high_max - low_min + 1e-10)
        return stoch

    # ========================================================================
    # CPU Fallback Functions
    # ========================================================================

    def _calculate_cpu_fallback(self, df: pd.DataFrame) -> Dict:
        """CPU fallback for technical indicators"""
        logger.info("⚠ Using CPU for technical indicators (slower)")

        indicators = {}
        close = df['close'].values

        # Basic indicators on CPU
        for window in [20, 50]:
            indicators[f'sma_{window}'] = float(pd.Series(close).rolling(window).mean().iloc[-1])
            indicators[f'ema_{window}'] = float(pd.Series(close).ewm(span=window).mean().iloc[-1])

        return indicators

    def _calculate_statistical_cpu_fallback(self, data: np.ndarray) -> Dict:
        """CPU fallback for statistical features"""
        logger.info("⚠ Using CPU for statistical features (slower)")

        return {
            'price_mean': float(np.mean(data)),
            'price_std': float(np.std(data)),
            'price_min': float(np.min(data)),
            'price_max': float(np.max(data)),
        }


# Singleton instance for global use
_gpu_engineer_instance = None


def get_gpu_feature_engineer(use_gpu: bool = True, progress_callback=None):
    """Get or create GPU feature engineer instance"""
    global _gpu_engineer_instance
    if _gpu_engineer_instance is None:
        _gpu_engineer_instance = GPUAcceleratedFeatureEngineer(
            use_gpu=use_gpu,
            progress_callback=progress_callback
        )
    return _gpu_engineer_instance


def check_gpu_availability() -> Dict:
    """Check GPU availability and return status"""
    status = {
        'gpu_available': GPU_AVAILABLE,
        'cupy_installed': cp is not None,
        'message': ''
    }

    if GPU_AVAILABLE:
        try:
            gpu_count = cp.cuda.runtime.getDeviceCount()
            gpu_mem = cp.cuda.runtime.getDeviceProperties(0)

            status['gpu_count'] = gpu_count
            status['message'] = f"✅ {gpu_count} GPU(s) available - GPU acceleration ENABLED"
            logger.info(status['message'])
        except Exception as e:
            status['message'] = f"⚠ GPU detected but error: {e}"
            logger.warning(status['message'])
    else:
        status['message'] = "⚠ GPU not available - Using CPU (slower for 1M+ datapoints)"
        logger.warning(status['message'])

    return status

