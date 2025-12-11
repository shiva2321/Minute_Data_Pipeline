# Enhanced Granular Data Analysis & Visualization Features

## Overview

This document describes the enhanced granular minute-level data analysis features and the new interactive visualization tab added to the Minute Data Pipeline dashboard.

## 🎯 New Features

### 1. Enhanced Granular Minute-Level Analysis

The pipeline now includes advanced minute-level statistical analysis that provides deeper insights into price action, liquidity, and market microstructure.

#### Key Metrics Added:

**Intraday Volatility Patterns**
- `hourly_vwap_volatility`: Volume-weighted volatility by hour of trading day
- Identifies periods of high/low volatility concentration
- Useful for understanding time-of-day effects

**Minute-Level Liquidity Metrics**
- `avg_liquidity_depth`: Average liquidity depth (volume per price point)
- `liquidity_variability`: Standard deviation of liquidity depth
- `volume_gini_coefficient`: Gini coefficient measuring volume concentration
  - Values near 0 indicate even distribution
  - Values near 1 indicate high concentration

**High-Frequency Price Action Patterns**
- `max_momentum_burst`: Maximum price acceleration observed
- `avg_momentum_burst`: Average absolute price acceleration
- `price_reversal_count`: Number of price direction changes
- `price_reversal_frequency`: Frequency of reversals relative to data points

**Statistical Anomaly Detection**
- `extreme_move_count_3sigma`: Count of price moves exceeding 3 standard deviations
- `extreme_move_count_2sigma`: Count of price moves exceeding 2 standard deviations
- Helps identify unusual market behavior

**Volatility Clustering Analysis**
- `volatility_clustering_coef`: Measures ARCH effects (volatility persistence)
- Positive values indicate volatility clustering
- Useful for risk modeling

**Trading Intensity Metrics**
- `active_trading_minutes`: Number of minutes with non-zero volume
- `trading_intensity`: Proportion of active minutes
- `price_efficiency_ratio`: Net price change / total distance traveled
  - Higher values indicate more efficient price discovery

### 2. Enhanced Multi-Timeframe Analysis

The multi-timeframe analysis has been significantly expanded:

#### New Timeframes Added:
- **2-minute**: Captures very short-term dynamics
- **3-minute**: Alternative short timeframe
- **30-minute**: Bridge between intraday and hourly

#### Previous Timeframes (Enhanced):
- 5-minute, 15-minute, 1-hour, 1-day

#### New Capabilities:

**Cross-Timeframe Correlation Analysis**
- Calculates correlations between returns across different timeframes
- Stored in `timeframe_correlations` dictionary
- Example: `2m_vs_5m`, `5m_vs_1h`, etc.
- Helps identify multi-scale price patterns

**Timeframe-Specific Regime Detection**
- Each timeframe gets its own volatility regime classification
- Regimes: `low_volatility`, `normal`, `high_volatility`
- Based on rolling volatility relative to timeframe mean
- Stored as: `{timeframe}_regime` (e.g., `5m_regime`)

**Per-Timeframe Momentum Indicators**
- RSI calculated for each timeframe where sufficient data exists
- Stored as: `{timeframe}_rsi` (e.g., `15m_rsi`)
- Enables multi-timeframe momentum analysis

### 3. Interactive Visualization Tab

A new "📈 Data Visualization" tab has been added to the dashboard with comprehensive data exploration capabilities.

#### Features:

**Symbol Selection & Loading**
- Dropdown to select any symbol from the database
- Load button to fetch and display profile data
- Refresh button to update symbol list

**Multiple Chart Views (Tabs)**
- **Price Chart**: Main price and volume visualization
- **Indicators**: Technical indicators display
- **Volume**: Volume analysis charts

**Interactive Chart Controls**
- Symbol selector with database integration
- Chart type selector:
  - Price & Volume
  - Candlestick
  - Technical Indicators
  - Multi-Timeframe
  - Intraday Heatmap
  - Volume Profile
- Display options checkboxes:
  - SMA (Simple Moving Average)
  - EMA (Exponential Moving Average)
  - Bollinger Bands
  - Volume overlay

**Granular Analysis Display**
- Dedicated panel showing all granular minute-level metrics
- Organized by category:
  - Liquidity Metrics
  - Price Action Patterns
  - Volatility Clustering
  - Trading Intensity
  - Hourly VWAP Volatility

**Profile Metadata Display**
- Symbol and exchange information
- Data points count
- Date range coverage
- Statistical summary (price mean, std, volatility, Sharpe ratio)

**Data Preview Table**
- Shows first 20 rows of minute data
- Columns: datetime, open, high, low, close, volume
- Sortable and scrollable

**Export Functionality**
- Export chart data to CSV
- Preserves all OHLCV data and calculated features
- User selects save location

## 📊 Usage Examples

### Accessing Granular Features in Code

```python
from feature_engineering import FeatureEngineer
import pandas as pd

# Load your minute data
df = pd.read_csv('minute_data.csv')

# Initialize feature engineer
fe = FeatureEngineer()

# Calculate granular features
granular = fe.calculate_granular_minute_features(df)

# Access specific metrics
print(f"Average Liquidity Depth: {granular['avg_liquidity_depth']}")
print(f"Volume Gini Coefficient: {granular['volume_gini_coefficient']}")
print(f"Trading Intensity: {granular['trading_intensity']}")

# Get hourly volatility pattern
hourly_vol = granular['hourly_vwap_volatility']
for hour, volatility in hourly_vol.items():
    print(f"Hour {hour}: {volatility:.4f}")
```

### Using Multi-Timeframe Analysis

```python
# Calculate multi-timeframe metrics and frames
metrics, frames = fe._multi_timeframe_metrics_and_frames(df)

# Access timeframe-specific data
df_5min = frames['5m']  # 5-minute bars
df_30min = frames['30m']  # 30-minute bars

# Check volatility regime for 15-minute timeframe
regime_15m = metrics.get('15m_regime', 'unknown')
print(f"15-minute regime: {regime_15m}")

# Get cross-timeframe correlations
correlations = metrics.get('timeframe_correlations', {})
for pair, corr in correlations.items():
    print(f"{pair}: {corr:.4f}")
```

### Using Full Pipeline

```python
# Run complete pipeline (includes all enhancements)
result = fe.process_full_pipeline(df)

# Access granular features
granular = result['granular_minute_features']

# Access enhanced multi-timeframe metrics
mtf = result['multi_timeframe']

# Access timeframe dataframes
frames = result['multi_timeframe_frames']
```

## 🎨 Using the Visualization Tab

### Opening the Visualization Tab

1. Launch the dashboard: `python dashboard/main.py` or `run_dashboard.bat`
2. Click on the "📈 Data Visualization" tab
3. Click "🔄 Refresh" to load available symbols

### Loading and Viewing Data

1. Select a symbol from the dropdown
2. Click "📊 Load Profile" to load data
3. The chart will display automatically
4. Granular analysis metrics appear in the right panel

### Exploring Data

- **Switch chart types**: Use the "Chart Type" dropdown
- **Toggle indicators**: Check/uncheck display options
- **View different timeframes**: Select from multi-timeframe tabs
- **Inspect data**: Scroll through the data preview table
- **Zoom & Pan**: Use mouse wheel and drag on chart (built-in)

### Exporting Data

1. Load a profile
2. Click "📤 Export Chart Data"
3. Choose save location and filename
4. Data saved as CSV with all columns

## 🔧 Technical Details

### Performance Considerations

- Charts limited to 500 data points for smooth performance
- Data table shows first 20 rows by default
- Full dataframes accessible for export
- Calculations vectorized for speed

### Data Flow

```
Raw Minute Data (CSV/API)
    ↓
Feature Engineering Pipeline
    ↓
Granular Analysis + Multi-Timeframe
    ↓
MongoDB Storage
    ↓
Visualization Tab (Load & Display)
```

### Integration Points

The new features integrate seamlessly with existing pipeline:

1. **Feature Engineering**: Added to `process_full_pipeline()` method
2. **Database Storage**: Granular features saved with profile
3. **Main Window**: New tab added to tab widget
4. **Database Controller**: Used for loading profile data

## 📈 Business Value

### For Traders
- Identify optimal trading hours using hourly volatility patterns
- Detect unusual market conditions via anomaly metrics
- Understand liquidity conditions before placing orders
- Multi-timeframe analysis for better entry/exit timing

### For Analysts
- Measure market efficiency via price discovery metrics
- Analyze intraday patterns and seasonality
- Quantify trading intensity and participation
- Cross-timeframe correlation for regime analysis

### For Developers
- Rich feature set for ML model training
- Standardized granular metrics across all symbols
- Easy access via visualization UI
- Exportable data for external analysis

## 🐛 Troubleshooting

### Visualization Tab Not Loading
- Ensure MongoDB is running and accessible
- Check that symbols have processed data
- Try refreshing symbols list
- Check console for error messages

### Missing Granular Features
- Ensure data has 'datetime' column
- Verify minimum data requirements (50+ rows recommended)
- Check that feature engineering completed successfully
- Look for error messages in logs

### Charts Not Displaying
- Verify profile has 'processed_df' data
- Check that datetime column is parseable
- Ensure PyQt6-Charts is installed
- Try different chart types

## 📝 Version History

### Version 1.2.0 (Current)
- ✅ Added 14+ granular minute-level analysis features
- ✅ Enhanced multi-timeframe analysis with 2m, 3m, 30m
- ✅ Cross-timeframe correlation analysis
- ✅ Timeframe-specific regime detection
- ✅ New interactive visualization tab
- ✅ Integrated into full pipeline

### Future Enhancements
- Real-time chart updates
- Additional chart types (candlestick, heatmaps)
- Custom indicator overlays
- Annotation and notes on charts
- Chart comparison mode (multiple symbols)
- Advanced pattern recognition visualization

## 📚 Related Documentation

- [Feature Engineering API](./API_REFERENCE.md)
- [Dashboard User Guide](./DASHBOARD_USER_GUIDE.md)
- [Architecture Overview](./ARCHITECTURE.md)
- [Getting Started](./GETTING_STARTED.md)

---

**Last Updated**: December 11, 2025  
**Version**: 1.2.0
