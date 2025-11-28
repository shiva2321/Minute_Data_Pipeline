# Project Summary: Minute Data Pipeline

## Overview
A production-ready Python pipeline for fetching, processing, and analyzing historical minute-by-minute stock market data from the EODHD API. The pipeline performs comprehensive feature engineering, derives statistical and ML features, and stores company profiles in MongoDB.

## Project Structure

```
Minute_Data_Pipeline/
│
├── Core Pipeline Modules
│   ├── config.py                    # Configuration and settings management
│   ├── data_fetcher.py              # EODHD API data fetching
│   ├── feature_engineering.py       # Feature calculation engine
│   ├── mongodb_storage.py           # MongoDB storage layer
│   └── pipeline.py                  # Main pipeline orchestrator
│
├── Usage & Examples
│   ├── examples.py                  # Comprehensive usage examples
│   ├── quick_start.py              # Quick demo script
│   └── test_setup.py               # Setup verification tests
│
├── Configuration
│   ├── .env                        # Environment variables (add your API key here)
│   ├── .env.example                # Environment template
│   └── requirements.txt            # Python dependencies
│
├── Documentation
│   ├── README.md                   # Main documentation
│   ├── SETUP.md                    # Setup instructions
│   └── PROJECT_SUMMARY.md          # This file
│
└── Data & Logs
    ├── logs/                       # Application logs
    └── .gitignore                  # Git ignore rules
```

## Key Features

### 1. Data Fetching (data_fetcher.py)
- **EODHD API Integration**: Fetch minute-by-minute historical data
- **Flexible Intervals**: Support for 1m, 5m, 1h intervals
- **Fundamental Data**: Company fundamentals integration
- **Rate Limiting**: Built-in API rate limiting
- **Batch Processing**: Process multiple symbols efficiently

### 2. Feature Engineering (feature_engineering.py)

#### Technical Indicators (40+ indicators)
- **Moving Averages**: SMA and EMA (5, 10, 20, 50, 100, 200 periods)
- **Bollinger Bands**: Upper, lower, middle, width (20, 50 periods)
- **RSI**: Relative Strength Index (14, 28 periods)
- **MACD**: Moving Average Convergence Divergence
- **ATR**: Average True Range
- **Stochastic Oscillator**: With smoothing
- **Volume Indicators**: Volume ratios, moving averages
- **Momentum**: Price momentum across multiple periods
- **ROC**: Rate of Change indicators

#### Statistical Features (20+ features)
- **Price Statistics**: Mean, median, std, variance, min, max, range
- **Distribution Metrics**: Skewness, kurtosis
- **Returns Analysis**: Returns mean, std, skewness, kurtosis
- **Performance Metrics**: Sharpe ratio, total return
- **Volatility**: Multiple volatility measures
- **Trend Analysis**: Linear regression slope, R², p-value

#### Time-Based Features
- **Session Analysis**: Morning vs afternoon patterns
- **Volume Patterns**: Time-of-day volume analysis
- **Volatility Patterns**: Intraday volatility distribution
- **Hour Analysis**: First/last hour performance

#### Market Microstructure
- **Spread Analysis**: Bid-ask spread estimates
- **Price Impact**: Volume-adjusted price changes
- **Liquidity Measures**: Amihud illiquidity ratio
- **Order Flow**: Order flow imbalance approximation
- **VWAP**: Volume-weighted average price

#### ML Features (50+ features)
- **Lagged Features**: Price, volume, returns lags (1, 5, 10, 20 periods)
- **Rolling Statistics**: Mean, std, min, max (10, 20, 50 windows)
- **Price Position**: Relative position in recent range
- **Pattern Recognition**: Higher highs, lower lows
- **Candlestick Features**: Body, shadows, ratios
- **Volume Dynamics**: Changes and acceleration

#### Risk Metrics
- **Value at Risk (VaR)**: 95% and 99% confidence levels
- **Conditional VaR**: Expected shortfall
- **Maximum Drawdown**: Peak-to-trough decline
- **Volatility Metrics**: Annualized volatility

### 3. MongoDB Storage (mongodb_storage.py)
- **Profile Creation**: Comprehensive company profiles
- **CRUD Operations**: Create, Read, Update, Delete
- **Indexing**: Optimized queries with indexes
- **Batch Operations**: Efficient bulk operations
- **Query Support**: Sector-based queries, filtering

### 4. Pipeline Orchestration (pipeline.py)
- **End-to-End Processing**: Complete workflow automation
- **Error Handling**: Robust error handling and logging
- **Progress Tracking**: Real-time progress with tqdm
- **Statistics**: Pipeline performance metrics
- **Logging**: Comprehensive logging with loguru

## Data Flow

```
1. Data Fetching
   ↓
   EODHD API → fetch_intraday_data() → Raw OHLCV DataFrame
   ↓
2. Feature Engineering
   ↓
   Raw Data → calculate_technical_indicators() → Technical features
            → calculate_statistical_features() → Statistical metrics
            → calculate_time_based_features() → Time patterns
            → calculate_ml_features() → ML-ready features
            → calculate_market_microstructure() → Microstructure metrics
   ↓
3. Profile Creation
   ↓
   All Features → create_company_profile() → Comprehensive Profile
   ↓
4. Storage
   ↓
   Profile → MongoDB → Indexed & Queryable
```

## Company Profile Schema

Each stored profile contains:

```json
{
  // Basic Information
  "symbol": "AAPL",
  "exchange": "US",
  "company_name": "Apple Inc.",
  "sector": "Technology",
  "industry": "Consumer Electronics",
  "last_updated": "2024-11-27T...",
  
  // Data Summary
  "data_summary": {
    "total_records": 15000,
    "date_range": {
      "start": "2024-10-28",
      "end": "2024-11-27"
    },
    "data_quality": {
      "missing_values": 0,
      "duplicate_rows": 0
    }
  },
  
  // Statistical Features (20+ metrics)
  "statistical_features": {
    "price_mean": 185.50,
    "price_std": 2.35,
    "returns_mean": 0.00012,
    "sharpe_ratio": 1.85,
    "volatility_close_to_close": 0.015,
    // ... more stats
  },
  
  // Technical Indicators (40+ indicators)
  "technical_indicators": {
    "sma_20": 182.30,
    "sma_50": 180.15,
    "rsi_14": 65.5,
    "macd": 2.35,
    "bb_upper_20": 188.40,
    // ... more indicators
  },
  
  // Time-Based Features
  "time_based_features": {
    "morning_avg_volume": 125000,
    "afternoon_volatility": 0.018,
    "first_hour_return": 0.005,
    // ... more time features
  },
  
  // Market Microstructure
  "microstructure_features": {
    "avg_spread": 0.015,
    "amihud_illiquidity": 0.000012,
    "order_flow_imbalance": 0.15,
    // ... more microstructure
  },
  
  // Performance Metrics
  "performance_metrics": {
    "total_return": 0.05,
    "period_high": 190.25,
    "period_low": 180.10,
    "avg_daily_range_pct": 0.025
  },
  
  // Risk Metrics
  "risk_metrics": {
    "max_drawdown": -0.15,
    "var_95": -0.025,
    "cvar_95": -0.035,
    "annualized_volatility": 0.25
  },
  
  // Fundamental Data (if fetched)
  "fundamental_data": {
    "General": {...},
    "Highlights": {...},
    "Valuation": {...}
  }
}
```

## Usage Examples

### 1. Process Single Symbol
```python
from pipeline import MinuteDataPipeline

pipeline = MinuteDataPipeline()
pipeline.process_symbol(
    symbol='AAPL',
    interval='1m',
    from_date='2024-11-01',
    to_date='2024-11-27'
)
```

### 2. Batch Processing
```python
symbols = ['AAPL', 'MSFT', 'GOOGL', 'TSLA']
results = pipeline.process_multiple_symbols(symbols, interval='5m')
```

### 3. Retrieve and Analyze
```python
profile = pipeline.get_profile('AAPL')
stats = profile['statistical_features']
print(f"Sharpe Ratio: {stats['sharpe_ratio']}")
```

### 4. Export Data
```python
profile = pipeline.export_profile_to_dict('AAPL')
# Export to JSON, analyze, visualize, etc.
```

## Technology Stack

- **Python 3.8+**: Core language
- **pandas**: Data manipulation
- **numpy**: Numerical computations
- **scipy**: Statistical analysis
- **scikit-learn**: ML preprocessing
- **pymongo**: MongoDB driver
- **requests**: API communication
- **loguru**: Logging
- **pydantic**: Configuration validation
- **tqdm**: Progress bars

## Configuration

All configuration via environment variables in `.env`:

```env
# Required
EODHD_API_KEY=your_api_key_here

# Optional (defaults shown)
EODHD_BASE_URL=https://eodhd.com/api
MONGODB_URI=mongodb://localhost:27017/
MONGODB_DATABASE=stock_data
MONGODB_COLLECTION=company_profiles
DATA_FETCH_INTERVAL_DAYS=30
MAX_WORKERS=5
BATCH_SIZE=100
```

## Quick Start

1. **Setup**:
   ```bash
   pip install -r requirements.txt
   cp .env.example .env
   # Edit .env with your API key
   ```

2. **Test**:
   ```bash
   python test_setup.py
   ```

3. **Run Demo**:
   ```bash
   python quick_start.py
   ```

4. **Process Data**:
   ```bash
   python pipeline.py
   ```

## Performance Characteristics

- **Throughput**: ~100-500 symbols/hour (depends on interval and API limits)
- **Memory**: ~500MB-2GB (depends on data volume)
- **Storage**: ~1-10MB per symbol profile
- **API Calls**: Rate-limited, configurable delays
- **Processing Speed**: ~1000 rows/second for feature engineering

## Error Handling

- **API Errors**: Retry logic with exponential backoff
- **Data Validation**: Schema validation with pydantic
- **MongoDB Errors**: Connection pooling and retry
- **Missing Data**: Graceful handling with warnings
- **Logging**: Comprehensive logging at all levels

## Logging

- **Console Output**: INFO level with colors
- **File Logging**: Daily rotating logs in `logs/`
- **Log Levels**: DEBUG, INFO, WARNING, ERROR
- **Structured Logging**: Context-rich log messages

## Testing

- **test_setup.py**: Verify installation and configuration
- **quick_start.py**: End-to-end functionality test
- **examples.py**: Various usage patterns

## Future Enhancements

- [ ] Real-time data streaming
- [ ] Advanced ML models (LSTM, Transformers)
- [ ] Backtesting framework
- [ ] Web dashboard for visualization
- [ ] Multi-exchange support
- [ ] Data quality monitoring
- [ ] Automated scheduling
- [ ] REST API wrapper
- [ ] WebSocket support for live data
- [ ] Advanced pattern recognition

## License

MIT License

## Support

- **Documentation**: See README.md and SETUP.md
- **Examples**: See examples.py
- **Issues**: Check logs/ directory
- **Testing**: Run test_setup.py

## Performance Tips

1. Use 5m or 1h intervals for faster processing
2. Limit date ranges during testing
3. Process symbols in batches
4. Monitor API rate limits
5. Index MongoDB collections
6. Use connection pooling
7. Enable MongoDB caching

## Security Best Practices

- Never commit `.env` file
- Use MongoDB authentication
- Rotate API keys regularly
- Use HTTPS for MongoDB Atlas
- Validate all inputs
- Sanitize data before storage

---

**Ready to analyze market data at scale!** 🚀

