# Minute Data Pipeline

A comprehensive data pipeline for fetching, processing, and analyzing historical minute-by-minute stock data from EODHD API, with advanced feature engineering and MongoDB storage.

## 🆕 Desktop Dashboard Available!

**NEW**: Professional PyQt6 desktop application for pipeline control and monitoring!

```bash
# Launch the desktop dashboard
run_dashboard.bat
```

Features:
- ✅ **Parallel Processing**: Process 10+ symbols simultaneously
- ✅ **Real-time Monitoring**: Live progress, logs, and API usage
- ✅ **Profile Management**: Browse, edit, and export profiles
- ✅ **Smart Rate Limiting**: Shared limiter across all workers
- ✅ **Professional UI**: Dark theme, responsive, never freezes

📖 **Documentation**:
- **[QUICK_REF.md](QUICK_REF.md)** - Quick reference (START HERE!)
- **[DASHBOARD_GUIDE.md](DASHBOARD_GUIDE.md)** - Complete walkthrough
- **[README_DASHBOARD.md](README_DASHBOARD.md)** - Technical documentation
- **[INDEX.md](INDEX.md)** - File navigation guide

---

## Features

### 📊 Data Fetching
- Historical minute-by-minute data from EODHD API
- Support for multiple time intervals (1m, 5m, 1h)
- Fundamental company data integration
- Rate-limited API calls
- Batch processing for multiple symbols

### 🔬 Feature Engineering
- **Technical Indicators**: 
  - Moving Averages (SMA, EMA)
  - Bollinger Bands
  - RSI (Relative Strength Index)
  - MACD
  - ATR (Average True Range)
  - Stochastic Oscillator
  - Volume indicators

- **Statistical Features**:
  - Price statistics (mean, median, std, variance)
  - Return statistics
  - Skewness and Kurtosis
  - Sharpe Ratio
  - Volatility measures
  - Trend analysis

- **ML Features**:
  - Lagged features
  - Rolling statistics
  - Price position indicators
  - Candlestick patterns
  - Volume dynamics

- **Market Microstructure**:
  - Spread measures
  - Price impact
  - Liquidity indicators
  - Order flow imbalance

- **Risk Metrics**:
  - Value at Risk (VaR)
  - Conditional VaR (CVaR)
  - Maximum Drawdown
  - Volatility metrics

### 💾 Storage
- MongoDB integration for persistent storage
- Comprehensive company profiles
- Indexed for efficient querying
- Support for updates and retrieval

## Installation

1. **Clone the repository**:
```bash
cd "D:\development project\Minute_Data_Pipeline"
```

2. **Create and activate virtual environment**:
```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

3. **Install dependencies**:
```powershell
pip install -r requirements.txt
```

4. **Set up environment variables**:
```powershell
Copy-Item .env.example .env
```

Edit `.env` file and add your credentials:
```
EODHD_API_KEY=your_api_key_here
MONGODB_URI=mongodb://localhost:27017/
```

## Quick Start

### Basic Usage

```python
from pipeline import MinuteDataPipeline

# Initialize pipeline
pipeline = MinuteDataPipeline()

# Process a single symbol
pipeline.process_symbol(
    symbol='AAPL',
    exchange='US',
    interval='1m',
    from_date='2024-11-01',
    to_date='2024-11-27',
    fetch_fundamentals=True
)

# Retrieve the profile
profile = pipeline.get_profile('AAPL')
print(f"Company: {profile['company_name']}")
print(f"Data points: {profile['data_points_count']}")
```

### Process Multiple Symbols

```python
symbols = ['AAPL', 'MSFT', 'GOOGL', 'TSLA', 'AMZN']

results = pipeline.process_multiple_symbols(
    symbols=symbols,
    interval='5m',
    fetch_fundamentals=True
)

print(f"Successful: {len(results['successful'])}")
print(f"Failed: {len(results['failed'])}")
```

### Retrieve and Analyze

```python
# Get a specific profile
profile = pipeline.get_profile('AAPL')

# Access different feature sets
stats = profile['statistical_features']
print(f"Average Price: ${stats['price_mean']:.2f}")
print(f"Sharpe Ratio: {stats['sharpe_ratio']:.4f}")

# Technical indicators
tech = profile['technical_indicators']
print(f"RSI(14): {tech['rsi_14']:.2f}")

# Risk metrics
risk = profile['risk_metrics']
print(f"Max Drawdown: {risk['max_drawdown']:.2%}")
```

## Project Structure

```
Minute_Data_Pipeline/
├── config.py                 # Configuration and settings
├── data_fetcher.py          # EODHD API data fetching
├── feature_engineering.py   # Feature calculation and engineering
├── mongodb_storage.py       # MongoDB storage and retrieval
├── pipeline.py              # Main pipeline orchestrator
├── examples.py              # Usage examples
├── requirements.txt         # Python dependencies
├── .env.example            # Environment variables template
└── README.md               # This file
```

## Configuration

The pipeline uses environment variables for configuration:

- `EODHD_API_KEY`: Your EODHD API key (required)
- `EODHD_BASE_URL`: EODHD API base URL (default: https://eodhd.com/api)
- `MONGODB_URI`: MongoDB connection URI (default: mongodb://localhost:27017/)
- `MONGODB_DATABASE`: Database name (default: stock_data)
- `MONGODB_COLLECTION`: Collection name (default: company_profiles)
- `DATA_FETCH_INTERVAL_DAYS`: Default data fetch interval (default: 30)
- `MAX_WORKERS`: Maximum concurrent workers (default: 5)

## Company Profile Structure

Each company profile stored in MongoDB contains:

```json
{
  "symbol": "AAPL",
  "exchange": "US",
  "company_name": "Apple Inc.",
  "sector": "Technology",
  "industry": "Consumer Electronics",
  "last_updated": "2024-11-27T...",
  
  "data_summary": {
    "total_records": 15000,
    "date_range": {...}
  },
  
  "statistical_features": {
    "price_mean": 185.50,
    "returns_std": 0.015,
    "sharpe_ratio": 1.85,
    ...
  },
  
  "technical_indicators": {
    "sma_50": 182.30,
    "rsi_14": 65.5,
    "macd": 2.35,
    ...
  },
  
  "risk_metrics": {
    "max_drawdown": -0.15,
    "var_95": -0.025,
    ...
  },
  
  "performance_metrics": {...},
  "time_based_features": {...},
  "microstructure_features": {...},
  "fundamental_data": {...}
}
```

## Examples

See `examples.py` for detailed usage examples:

1. **Single Symbol Processing**: Process one stock with full features
2. **Multiple Symbols**: Batch process multiple stocks
3. **Retrieve and Analyze**: Query and analyze stored profiles
4. **Custom Date Range**: Process specific date ranges
5. **Export Profile**: Export profiles to JSON
6. **Pipeline Statistics**: Get overall pipeline statistics

## API Rate Limits

The pipeline includes built-in rate limiting to respect EODHD API limits:
- Configurable delay between requests
- Session management for efficient connections
- Error handling and retry logic

## Logging

The pipeline uses `loguru` for comprehensive logging:
- Console output with colored formatting
- Daily rotating log files in `logs/` directory
- Different log levels (INFO, DEBUG, WARNING, ERROR)

## Requirements

- Python 3.8+
- EODHD API account and API key
- MongoDB instance (local or Atlas)
- See `requirements.txt` for Python package dependencies

## MongoDB Setup

### Local MongoDB:
```powershell
# Install MongoDB and start the service
# Default connection: mongodb://localhost:27017/
```

### MongoDB Atlas (Cloud):
```
# Use connection string from Atlas dashboard
MONGODB_URI=mongodb+srv://username:password@cluster.mongodb.net/
```

## Error Handling

The pipeline includes comprehensive error handling:
- API connection errors
- Data validation
- MongoDB connection issues
- Missing or invalid data
- Rate limiting

## Performance

- Efficient batch processing
- Vectorized operations with pandas/numpy
- Indexed MongoDB queries
- Session pooling for API requests

## Contributing

Contributions are welcome! Please feel free to submit issues or pull requests.

## License

MIT License

## Support

For issues or questions:
1. Check the examples in `examples.py`
2. Review the configuration in `.env`
3. Check logs in `logs/` directory
4. Verify MongoDB connection
5. Confirm EODHD API key is valid

## Roadmap

- [ ] Add real-time data streaming
- [ ] Implement more ML features
- [ ] Add backtesting capabilities
- [ ] Create visualization dashboard
- [ ] Add more exchanges support
- [ ] Implement data quality checks
- [ ] Add scheduling/automation
- [ ] Create REST API wrapper

---

**Note**: Remember to never commit your `.env` file with real API keys. Always use `.env.example` as a template.

