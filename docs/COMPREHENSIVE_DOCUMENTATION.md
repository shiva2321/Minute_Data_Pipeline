# Minute Data Pipeline - Complete Documentation

## Quick Navigation

- **[Getting Started](#getting-started)** - Installation and first run
- **[Architecture](#architecture)** - System design and components
- **[User Guide](#user-guide)** - Dashboard usage
- **[API Reference](#api-reference)** - Module documentation
- **[Features Guide](#features-guide)** - Detailed feature descriptions
- **[Development Guide](#development-guide)** - Contributing and extending
- **[Troubleshooting](#troubleshooting)** - Common issues and solutions

---

## Quick Start

### Installation

```bash
# Clone repository
git clone <repo-url>
cd Minute_Data_Pipeline

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your API keys and MongoDB connection
```

### Running the Dashboard

**Windows:**
```bash
run_dashboard.bat
```

**Linux/Mac:**
```bash
python dashboard/main.py
```

### First Steps

1. **Configure Settings** (in Dashboard Settings tab):
   - EODHD API Key
   - MongoDB Connection String
   - Optional: Email alert credentials

2. **Add Symbols**:
   - Use "Load from Cache" to fetch cached company list
   - Select symbols to process
   - Choose incremental or full history mode

3. **Monitor Processing**:
   - Watch real-time progress in Monitor tab
   - Check API usage gauge
   - View detailed logs

---

## Architecture

### System Overview

The Minute Data Pipeline is a complete stock market data processing system with three core components:

```
┌─────────────────────────────────────────────────────┐
│        Desktop Dashboard (PyQt6 UI)                 │
│   - Pipeline Control                                │
│   - Real-time Monitoring                            │
│   - Profile Management                              │
└────────────────┬────────────────────────────────────┘
                 │
      ┌──────────┴──────────┐
      ▼                     ▼
┌──────────────────┐  ┌─────────────────┐
│ Pipeline Core    │  │ Data Storage    │
│ - Data Fetcher   │  │ - MongoDB       │
│ - Feature Eng.   │  │ - Cache Store   │
│ - Rate Limiter   │  └─────────────────┘
└──────────────────┘
      │
      ▼
┌──────────────────┐
│  EODHD API       │
│  (Data Source)   │
└──────────────────┘
```

### Core Components

#### 1. **Pipeline Module** (`pipeline.py`)
Orchestrates the entire data processing workflow:
- Fetches minute-level OHLCV data
- Processes features
- Manages storage
- Handles errors and retries

#### 2. **Data Fetcher** (`data_fetcher.py`)
Integrates with EODHD API:
- Fetches intraday minute data
- Retrieves fundamental company data
- Implements adaptive rate limiting
- Supports pause/resume/cancel operations

#### 3. **Feature Engineering** (`feature_engineering.py`)
Generates 200+ features:
- Technical indicators (SMA, EMA, MACD, RSI, etc.)
- Statistical features (returns, skewness, kurtosis)
- Volatility measures (ATR, Bollinger Bands)
- Microstructure features (volume-related)
- Multi-timeframe analysis

#### 4. **Storage** (`mongodb_storage.py`)
Persists processed data:
- MongoDB for profile storage
- IndexedDB for company lists
- Cache store for API usage tracking
- Backup and recovery features

#### 5. **Dashboard** (`dashboard/`)
PyQt6-based user interface:
- Real-time pipeline control
- Live monitoring and metrics
- Profile browser and editor
- Configuration management

### Data Flow

```
User Input (Dashboard)
    │
    ├─ Symbols
    ├─ Mode (Incremental/Full)
    └─ Options (Years, Workers, etc.)
    │
    ▼
┌─────────────────────────────────────┐
│  PipelineController (QThread)       │
│  ├─ ThreadPoolExecutor (10 workers) │
│  └─ Shared Rate Limiter             │
└─────────────────────────────────────┘
    │
    ├─ Worker 1: Fetch → Engineer → Store
    ├─ Worker 2: Fetch → Engineer → Store
    ├─ Worker 3: Fetch → Engineer → Store
    └─ ... (up to 10 workers)
    │
    ▼
┌─────────────────────────────────────┐
│  Data Processing Pipeline           │
│  1. Fetch minute data (EODHD)       │
│  2. Fetch fundamentals              │
│  3. Engineer features               │
│  4. Create company profile          │
│  5. Save to MongoDB                 │
└─────────────────────────────────────┘
    │
    ▼
Real-time Metrics Update (Qt Signals)
```

---

## User Guide

### Dashboard Tabs

#### Tab 1: Pipeline Control

**Input Section:**
- **Symbol Input**: Enter symbols comma-separated (AAPL, MSFT, GOOGL)
- **File Browser**: Load symbols from a text file
- **Mode Selection**: 
  - Incremental: Fetches only new data since last update
  - Full: Complete historical backfill

**Configuration:**
- **Years**: How many years of history (1-30)
- **Chunk Size**: Days per fetch (1-30, default 30)
- **Workers**: Parallel processing threads (1-20, default 10)

**Controls:**
- **▶ Start**: Begin processing
- **⏸ Pause**: Pause current operations
- **⏹ Stop**: Halt and reset
- **🗑 Clear**: Clear queue

#### Tab 2: Monitor

**Metrics Bar:**
- Total symbols, Succeeded, Failed, Skipped
- Queue Count, Processing, ETA, API Usage %

**API Usage Gauge:**
- Minute: Calls per minute (limit: 80)
- Daily: Calls per day (limit: 95,000)
- Visual progress bars with color coding

**Processing Queue:**
- Real-time symbol status
- Progress per symbol (0-100%)
- Phase indicator (Fetching/Processing/Storing)
- Timestamps

**Live Log Viewer:**
- Color-coded log levels
- DEBUG (cyan), INFO (green), WARNING (yellow)
- ERROR (red), SUCCESS (blue)
- Auto-scroll and search

#### Tab 3: Database Profiles

**Profile Browser:**
- Search profiles by symbol
- View profile details
- Edit JSON structure
- Export profiles
- Delete unused entries

**Features Tab:**
- View engineered features by category
- Price features
- Volume features
- Volatility features
- Statistical features

#### Tab 4: Settings

**API Configuration:**
- EODHD API Key
- API base URL
- Timeout settings

**Database:**
- MongoDB URI
- Database name
- Collection name

**Pipeline Defaults:**
- Default years for history
- Default chunk size
- Default worker count

**UI Settings:**
- Theme selection
- Font size
- Auto-scroll options

---

## Features Guide

### Processing Modes

#### Incremental Update
- Checks last stored data point
- Fetches only newer data
- Recomputes features for complete data
- Faster, suitable for daily updates
- Preserves historical metadata

#### Full Historical Backfill
- Fetches entire available history
- Uses 30-day chunks to optimize API calls
- Processes all years selected
- More comprehensive, used for initial setup
- Can take significant time for 30 years

### Feature Categories

#### Technical Indicators
- **Moving Averages**: SMA (5, 10, 20, 50, 100, 200), EMA
- **Momentum**: MACD, RSI, Stochastic
- **Trend**: ADX, Aroon, KeltnerChannel
- **Volatility**: Bollinger Bands, ATR, NATR

#### Statistical Features
- **Return Metrics**: Returns, log returns, cumulative returns
- **Volatility**: Realized volatility, rolling std
- **Distribution**: Skewness, kurtosis, jarque-bera
- **Autocorrelation**: ACF, PACF lags

#### Microstructure Features
- **Volume Analysis**: Volume, VWAP, OBV
- **Spread Analysis**: Price spread, volume imbalance
- **Flow Analysis**: Accumulation/Distribution

#### Risk Metrics
- **Drawdown**: Maximum drawdown, drawdown duration
- **VaR**: Value at Risk (95%, 99%)
- **Sharpe Ratio**: Risk-adjusted returns
- **Beta**: Market sensitivity

#### Multi-Timeframe Analysis
- **Aggregated Features** at 5m, 15m, 1h, 1d levels
- **Cross-timeframe** momentum and volatility
- **Regime Detection**: Trend vs Range

---

## API Reference

### Core Classes

#### MinuteDataPipeline

Main orchestrator for data processing.

```python
from pipeline import MinuteDataPipeline

pipeline = MinuteDataPipeline()

# Process single symbol
success = pipeline.process_symbol(
    symbol='AAPL',
    exchange='US',
    interval='1m',
    from_date='2024-01-01',
    to_date='2024-12-31',
    fetch_fundamentals=True
)

# Process multiple symbols
results = pipeline.process_multiple_symbols(
    symbols=['AAPL', 'MSFT', 'GOOGL'],
    exchange='US',
    fetch_fundamentals=True
)
# Returns: {'successful': [...], 'failed': [...], 'total': 3}
```

#### EODHDDataFetcher

Handles API communication with EODHD.

```python
from data_fetcher import EODHDDataFetcher

fetcher = EODHDDataFetcher(api_key='YOUR_API_KEY')

# Fetch intraday data
df = fetcher.fetch_intraday_data(
    symbol='AAPL',
    interval='1m',
    from_date='2024-01-01',
    exchange='US'
)
# Returns: DataFrame with columns [datetime, open, high, low, close, volume]

# Fetch fundamentals
fundamentals = fetcher.fetch_fundamental_data('AAPL', 'US')
# Returns: Dict with company data

# Rate limiter status
stats = fetcher.rate_limiter.get_stats()
# Returns: {'minute_used': X, 'minute_remaining': Y, 'daily_used': Z, ...}
```

#### FeatureEngineer

Generates features from price data.

```python
from feature_engineering import FeatureEngineer

engineer = FeatureEngineer()

# Process complete pipeline
features = engineer.process_full_pipeline(df)
# Returns: Dict with all feature categories

# Individual feature calculations
engineer.calculate_technical_indicators(df)
engineer.calculate_statistical_features(df)
engineer.calculate_microstructure_features(df)
```

#### MongoDBStorage

Manages data persistence.

```python
from mongodb_storage import MongoDBStorage

storage = MongoDBStorage(
    uri='mongodb+srv://user:pass@cluster.mongodb.net',
    database='stock_data',
    collection='profiles'
)

# Save profile
profile = storage.create_company_profile(
    symbol='AAPL',
    exchange='US',
    raw_data=df,
    features=features,
    fundamental_data=fundamentals
)
success = storage.save_profile(profile)

# Retrieve profile
profile = storage.get_profile('AAPL', 'US')

# List all profiles
profiles = storage.get_all_profiles(limit=100, skip=0)

# Update profile
storage.update_profile('AAPL', 'US', update_dict)

# Delete profile
storage.delete_profile('AAPL', 'US')
```

#### CacheStore

Persistent local caching.

```python
from dashboard.models import CacheStore

cache = CacheStore()

# API usage tracking
cache.update_daily_api_calls(100)
current = cache.get_daily_api_calls()

# Company list caching
cache.cache_companies(companies_list)
companies = cache.get_cached_companies()
cache.clear_company_cache()

# Custom caching
cache.set('key', value)
value = cache.get('key')
cache.delete('key')
```

### Configuration

See `config.py` for all configuration options.

**Key Environment Variables:**
```bash
# EODHD API
EODHD_API_KEY=your_api_key
EODHD_BASE_URL=https://eodhd.com/api

# MongoDB
MONGODB_URI=mongodb+srv://user:pass@cluster.mongodb.net
MONGODB_DATABASE=stock_data
MONGODB_COLLECTION=profiles

# Rate Limiting
API_CALLS_PER_MINUTE=80
API_CALLS_PER_DAY=95000

# Pipeline
DATA_FETCH_INTERVAL_DAYS=30
DEFAULT_CHUNK_SIZE=30
DEFAULT_HISTORY_YEARS=5

# Email Alerts
PIPELINE_ALERT_EMAIL=your_email@gmail.com
PIPELINE_ALERT_PASSWORD=your_app_password
```

---

## Development Guide

### Project Structure

```
Minute_Data_Pipeline/
├── pipeline.py              # Main orchestrator
├── data_fetcher.py          # EODHD API integration
├── feature_engineering.py   # Feature calculations
├── mongodb_storage.py       # Data persistence
├── config.py                # Configuration management
│
├── dashboard/               # PyQt6 UI
│   ├── main.py             # Entry point
│   ├── ui/                 # Panels and widgets
│   ├── controllers/        # Business logic
│   ├── services/           # Email, metrics
│   ├── models/             # Data models
│   └── utils/              # Theme, signals
│
├── utils/                   # Utilities
│   ├── rate_limiter.py     # API rate limiting
│   └── backfill_checkpoint.py  # Progress tracking
│
├── tests/                   # Test suite
│   ├── unit/               # Unit tests
│   ├── integration/        # Integration tests
│   └── diagnostics/        # Diagnostic tests
│
└── docs/                    # Documentation
```

### Adding a New Feature

1. **Add to Feature Engineer**:
```python
def calculate_custom_features(self, df: pd.DataFrame) -> pd.DataFrame:
    """Calculate custom features"""
    df = df.copy()
    df['custom_feature'] = ...  # Your calculation
    return df
```

2. **Integrate into Pipeline**:
```python
def process_full_pipeline(self, df):
    # ... existing features ...
    df = self.calculate_custom_features(df)
    # ... return results ...
```

3. **Add Tests**:
```python
def test_custom_features():
    engineer = FeatureEngineer()
    df = create_test_data()
    result = engineer.calculate_custom_features(df)
    assert 'custom_feature' in result.columns
```

### Adding a New UI Panel

1. Create panel class in `dashboard/ui/panels/`:
```python
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel

class CustomPanel(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout()
        layout.addWidget(QLabel("Custom Panel"))
        self.setLayout(layout)
```

2. Add to main window tabs:
```python
# In dashboard/ui/main_window.py
self.tabs.addTab(CustomPanel(), "Custom")
```

### Running Tests

```bash
# All tests
pytest tests/

# By category
pytest tests/unit/
pytest tests/integration/
pytest tests/diagnostics/

# With coverage
pytest --cov tests/

# Specific test
pytest tests/unit/test_rate_limiter.py::test_per_minute_throttling
```

### Building for Distribution

```bash
# Create standalone executable (Windows)
pyinstaller --onefile --windowed --icon=icon.ico dashboard/main.py

# Output: dist/main.exe
```

---

## Troubleshooting

### Common Issues

#### Dashboard Won't Launch

**Error**: "ModuleNotFoundError: No module named 'PyQt6'"

**Solution**:
```bash
pip install PyQt6 PyQt6-WebEngine PyQt6-Charts
```

**Error**: "Cannot connect to MongoDB"

**Solution**:
1. Check MongoDB connection string in Settings
2. Verify network access (MongoDB Atlas whitelist)
3. Check username/password
4. Test connection: `mongosh "mongodb+srv://user:pass@cluster.mongodb.net"`

#### API Rate Limiting Issues

**Error**: "Rate limit exceeded"

**Solution**:
1. Reduce number of workers (Settings → Default Workers)
2. Increase chunk size to reduce API calls
3. Wait for rate limit reset (90 calls/day per worker)
4. Check if previous runs had pending calls

#### Feature Engineering Slow

**Error**: "Processing taking too long"

**Solution**:
1. Use Incremental mode instead of Full backfill
2. Reduce history years (e.g., 5 instead of 30)
3. Increase workers (if system has capacity)
4. Check system resources (CPU, RAM)

#### MongoDB Storage Full

**Error**: "Write operation failed"

**Solution**:
1. Check MongoDB storage quota
2. Archive old profiles to backup
3. Delete unused symbols
4. Consider upgrading MongoDB tier

### Performance Tuning

**For 6-core CPU (Ryzen 5 7600):**
- Workers: 8-10
- Chunk size: 30 days
- Parallel workers: 3-4 for data fetch, rest for processing

**For 16GB RAM:**
- Max symbols: 100-200
- Cache size: 2GB
- Log retention: 30 days

**For Network:**
- Chunk size: 30 days (optimal for API)
- Retry delay: 60-90 seconds
- Timeout: 30 seconds

---

## FAQ

**Q: How often should I update symbols?**  
A: Recommended weekly for active trading, daily for high-frequency analysis.

**Q: What's the maximum history?**  
A: EODHD provides up to 30 years for US stocks.

**Q: How many features are calculated?**  
A: 200+ features across 7 categories.

**Q: Can I run the pipeline headless?**  
A: Yes, use `pipeline.py` directly without the dashboard.

**Q: How do I backup my data?**  
A: Export profiles via Dashboard Profile Browser or use MongoDB backup utilities.

**Q: What's the license?**  
A: Internal/Proprietary (update as needed).

---

## Support & Resources

- **API Documentation**: https://eodhd.com/financial-apis/
- **MongoDB Docs**: https://docs.mongodb.com/
- **PyQt6 Guide**: https://www.riverbankcomputing.com/static/Docs/PyQt6/
- **Pandas Reference**: https://pandas.pydata.org/docs/
- **Scipy/Statsmodels**: https://docs.scipy.org/, https://www.statsmodels.org/

---

**Version**: 1.1.0  
**Last Updated**: November 28, 2025  
**Status**: Production Ready

