# Minute Data Pipeline Feature Guide

This document explains the engineered feature blocks produced by `FeatureEngineer` and stored in MongoDB profiles, plus recommended ML usage patterns and anti-patterns.

## Profile Structure (Key Blocks)
```
{
  "statistical_features": { ... },
  "time_features": { ... },
  "microstructure_features": { ... },
  "advanced_statistical": { ... },
  "multi_timeframe": { ... },
  "regime_features": { ... },
  "predictive_labels": { ... },
  "predictive_label_series": DataFrame-like columns,
  "multi_timeframe_frames": { "5m": DataFrame, ... },
  "quality_metrics": { ... },
  "technical_extended_latest": { ... }
}
```

## 1. Statistical Features
Core distribution metrics of prices & returns.
- `price_mean`, `price_std`, `price_skewness`, `price_kurtosis`
- `returns_mean`, `returns_std`, `returns_skewness`, `returns_kurtosis`
- `sharpe_ratio` (minute-scaled -> annualized proxy)
- Trend regression: `trend_slope`, `trend_r_squared`, `trend_p_value`

Use Case: Baseline descriptive analysis, priors for risk models.

## 2. Time Features
Intraday temporal dynamics.
- Hour-based segmentation: morning vs afternoon volume & volatility
- `first_hour_return`, `last_hour_return`

Use Case: Capture seasonality (open volatility spike, lunch lull, close ramp).

## 3. Microstructure Features
Liquidity & order flow proxies.
- `avg_spread`, `spread_volatility`
- `avg_price_impact` = |Δprice|/volume
- `amihud_illiquidity` = |return|/volume (lower => higher liquidity)
- `order_flow_imbalance` = signed volume ratio

Use Case: Regime-aware execution modeling; liquidity-sensitive signals.

## 4. Advanced Statistical
Higher-order stability & tail metrics.
- Autocorrelations lag 1/2/5/10/20
- Entropy of returns histogram (`returns_entropy`)
- Downside risk: `downside_volatility`, `sortino_ratio`
- Persistence: `hurst_exponent` (≈0.5 random, >0.5 trending, <0.5 mean-reverting)
- Tail heaviness: `hill_tail_index`
- `calmar_ratio` (return vs drawdown)

Use Case: Feature enrichment for regime & risk adaptation.

## 5. Multi-Timeframe Metrics
Resampled OHLCV windows (5m / 15m / 1h / 1d).
- `{tf}_volatility` (std of resampled returns)
- `{tf}_avg_volume`
- `{tf}_return`
- `{tf}_trend_slope`

Stored frames in `multi_timeframe_frames` for hierarchical modeling (e.g., cross-scale attention).

## 6. Regime Features
Simple categorical & coded states.
- `volatility_regime` ∈ {low, medium, high}
- `trend_regime` ∈ {choppy, weak_trend, strong_uptrend, strong_downtrend}
- `liquidity_regime` ∈ {illiquid, normal, high_liquidity}
- `session_regime` ∈ {pre_market, open, midday, power_hour, close}
- Numeric codes: `{name}_code`

Use Case: Conditional modeling (train separate models per regime or use as embedding).

## 7. Predictive Labels (Snapshot)
Single-value targets derived from the predictive label series to seed supervised tasks:
- `next_{h}m_return`
- `next_{h}m_realized_vol`
- `next_{h}m_parkinson_vol`
- `next_{h}m_max_drawdown`
- `next_{h}m_var_95`
- `next_{h}m_direction` (−1/0/1)
- `next_{h}m_breakout` (0/1)
- Regime-conditional: `next_30m_return_low_vol`, `next_30m_return_high_vol`

Series versions (time-aligned) are in `predictive_label_series` with tail masking to prevent leakage.

## 8. Quality Metrics
Data health & integrity.
- `row_count`
- `missing_by_column`
- `price_outliers` (IQR-based counts)
- `adf_pvalue_returns` (stationarity test; small p-value => stable mean)

Use Case: Filter degraded segments before model training.

## 9. Extended Technical Latest
Latest snapshot of advanced indicators: `vwap`, `obv`, `cmf_20`, `kama_10_30`, `pvo` (if available).

## Leakage Prevention
Forward-looking labels are masked for the final h rows so models cannot accidentally train on incomplete targets.

## Recommended Modeling Patterns
```python
# Return prediction (15m horizon)
X = df[[
  'rsi_14','macd','hurst_exponent','volatility_regime_code',
  'order_flow_imbalance','trend_slope','5m_volatility'
]]
y = df['next_15m_return']

# Volatility forecasting
vol_target = df['next_30m_realized_vol']
```

### Regime Conditioning
```python
for regime in ['low','medium','high']:
    subset = df[df['volatility_regime'] == regime]
    model = train_model(subset[feature_cols], subset['next_15m_return'])
```

### Multi-Task Learning
Jointly predict return & volatility:
- Advantage: captures coupling between directional movement & uncertainty.

## Anti-Patterns
| Pitfall | Correction |
|---------|------------|
| Using raw price levels directly | Use returns, differences, or normalized deviations |
| Training on last h rows with NaN targets | Drop NaNs before fitting |
| Mixing unaligned timeframes (1m close + future 5m bar) | Use lagged / completed resample bars only |
| Ignoring regimes in validation splits | Stratify by regime to assess generalization |

## Baseline Importance (Indicative)
1. `hurst_exponent` – Trend persistence
2. `volatility_regime_code` – Conditional variance
3. `order_flow_imbalance` – Microstructure edge
4. `rsi_14` – Momentum normalization
5. `5m_volatility` – Short-term risk context

## Benchmark Execution
Use `scripts/benchmark_features.py` to time feature generation scaling.

## Next Extensions
- Hidden Markov Model for regime probabilities
- Adaptive window selection (auto-tuned horizons)
- SHAP-based feature importance caching

---
Questions or extension requests? Add them to the project backlog.

