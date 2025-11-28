# API Reference - Detailed Module Documentation

## Table of Contents

- [Pipeline Module](#pipeline-module)
- [Data Fetcher](#data-fetcher)
- [Feature Engineering](#feature-engineering)
- [MongoDB Storage](#mongodb-storage)
- [Configuration](#configuration)
- [Utilities](#utilities)
- [Dashboard Components](#dashboard-components)

---

## Pipeline Module

### MinuteDataPipeline

Complete orchestrator for the data processing pipeline.

```python
from pipeline import MinuteDataPipeline
```

#### Constructor

```python
MinuteDataPipeline()
```

Initializes:
- EODHDDataFetcher instance
- FeatureEngineer instance
- MongoDBStorage instance
- Logger with file and console output

#### Methods

##### process_symbol()

Process a single symbol through the entire pipeline.

```python
def process_symbol(
    symbol: str,
    exchange: str = 'US',
    interval: str = '1m',
    from_date: Optional[str] = None,
    to_date: Optional[str] = None,
    fetch_fundamentals: bool = True
) -> bool
```

**Parameters:**
- `symbol` (str): Stock symbol (e.g., 'AAPL')
- `exchange` (str): Exchange code (default: 'US')
- `interval` (str): Time interval, '1m'|'5m'|'1h' (default: '1m')
- `from_date` (str): Start date 'YYYY-MM-DD' (optional)
- `to_date` (str): End date 'YYYY-MM-DD' (optional)
- `fetch_fundamentals` (bool): Include company data (default: True)

**Returns:**
- `bool`: True if successful, False otherwise

**Raises:**
- `Exception`: On data fetch or processing errors (caught and logged)

**Example:**
```python
pipeline = MinuteDataPipeline()
success = pipeline.process_symbol('AAPL', fetch_fundamentals=True)
if success:
    print("Symbol processed successfully")
else:
    print("Processing failed")
```

**Process Flow:**
1. Fetch minute-level OHLCV data
2. Fetch fundamental company data
3. Engineer 200+ features
4. Create company profile object
5. Save to MongoDB
6. Log results

##### process_multiple_symbols()

Process multiple symbols in sequence or parallel.

```python
def process_multiple_symbols(
    symbols: List[str],
    exchange: str = 'US',
    interval: str = '1m',
    from_date: Optional[str] = None,
    to_date: Optional[str] = None,
    fetch_fundamentals: bool = True
) -> dict
```

**Parameters:**
- `symbols` (List[str]): List of stock symbols
- `exchange` (str): Exchange code (default: 'US')
- `interval` (str): Time interval (default: '1m')
- `from_date` (str): Start date (optional)
- `to_date` (str): End date (optional)
- `fetch_fundamentals` (bool): Include company data (default: True)

**Returns:**
```python
{
    'successful': ['AAPL', 'MSFT'],
    'failed': ['INVALID'],
    'total': 3
}
```

**Example:**
```python
results = pipeline.process_multiple_symbols(
    symbols=['AAPL', 'MSFT', 'GOOGL'],
    exchange='US',
    fetch_fundamentals=True
)
print(f"Success: {len(results['successful'])}")
print(f"Failed: {len(results['failed'])}")
```

---

## Data Fetcher

### EODHDDataFetcher

Handles API communication with EODHD for data fetching.

```python
from data_fetcher import EODHDDataFetcher
```

#### Constructor

```python
EODHDDataFetcher(api_key: Optional[str] = None)
```

**Parameters:**
- `api_key` (str): EODHD API key (optional, uses config if not provided)

**Attributes:**
- `api_key`: API authentication key
- `base_url`: API endpoint base URL
- `session`: Requests session for connection pooling
- `rate_limiter`: AdaptiveRateLimiter instance
- `cancel_event`: Threading Event for cancellation
- `pause_event`: Threading Event for pausing

#### Methods

##### fetch_intraday_data()

Fetch minute-by-minute price data.

```python
def fetch_intraday_data(
    symbol: str,
    interval: str = '1m',
    from_date: Optional[str] = None,
    to_date: Optional[str] = None,
    exchange: str = 'US'
) -> pd.DataFrame
```

**Parameters:**
- `symbol` (str): Stock symbol
- `interval` (str): '1m'|'5m'|'1h' (default: '1m')
- `from_date` (str): Start date 'YYYY-MM-DD'
- `to_date` (str): End date 'YYYY-MM-DD'
- `exchange` (str): Exchange code (default: 'US')

**Returns:**
```python
DataFrame with columns:
- datetime: Timestamp
- open: Opening price
- high: High price
- low: Low price
- close: Closing price
- volume: Trading volume
```

**Raises:**
- `RuntimeError`: If operation cancelled
- `requests.RequestException`: On API errors

**Example:**
```python
fetcher = EODHDDataFetcher()
df = fetcher.fetch_intraday_data(
    symbol='AAPL',
    from_date='2024-01-01',
    to_date='2024-12-31'
)
print(f"Fetched {len(df)} records")
print(df.head())
```

##### fetch_fundamental_data()

Fetch company fundamental data.

```python
def fetch_fundamental_data(
    symbol: str,
    exchange: str = 'US'
) -> Dict
```

**Parameters:**
- `symbol` (str): Stock symbol
- `exchange` (str): Exchange code (default: 'US')

**Returns:**
```python
{
    'general': {...},
    'valuation': {...},
    'financials': {...},
    'shares_stats': {...}
}
```

**Example:**
```python
fundamentals = fetcher.fetch_fundamental_data('AAPL', 'US')
print(f"Company: {fundamentals['general']['Name']}")
print(f"Market Cap: {fundamentals['valuation']['MarketCapitalization']}")
```

##### get_rate_limiter_status()

Get current API rate limiter status.

```python
def get_rate_limiter_status() -> Dict
```

**Returns:**
```python
{
    'minute_used': 42,
    'minute_remaining': 38,
    'minute_limit': 80,
    'daily_used': 45000,
    'daily_remaining': 50000,
    'daily_limit': 95000
}
```

**Example:**
```python
status = fetcher.get_rate_limiter_status()
if status['minute_remaining'] < 10:
    print("Warning: Near minute limit")
```

---

## Feature Engineering

### FeatureEngineer

Derives 200+ statistical and technical features from price data.

```python
from feature_engineering import FeatureEngineer
```

#### Constructor

```python
FeatureEngineer()
```

Initializes StandardScaler for feature normalization.

#### Methods

##### process_full_pipeline()

Process complete feature engineering pipeline.

```python
def process_full_pipeline(
    df: pd.DataFrame
) -> Dict[str, Any]
```

**Parameters:**
- `df` (pd.DataFrame): DataFrame with OHLCV columns

**Returns:**
```python
{
    'processed_df': DataFrame,
    'technical_features': {...},
    'statistical_features': {...},
    'volatility_features': {...},
    'microstructure_features': {...},
    'risk_metrics': {...},
    'performance_metrics': {...},
    'advanced_statistical': {...},
    'multi_timeframe': {...},
    'regime_features': {...},
    'labels': {...},
    'predictive_labels': {...},
    'summary': {
        'total_records': int,
        'missing_values': int,
        'feature_count': int
    }
}
```

**Example:**
```python
engineer = FeatureEngineer()
results = engineer.process_full_pipeline(df)
features = results['technical_features']
print(f"Generated {results['summary']['feature_count']} features")
```

##### calculate_technical_indicators()

Calculate technical trading indicators.

```python
def calculate_technical_indicators(df: pd.DataFrame) -> pd.DataFrame
```

**Features Generated:**
- Moving Averages: SMA, EMA (5, 10, 20, 50, 100, 200 periods)
- Momentum: MACD, Signal, Histogram, RSI
- Bollinger Bands: Upper, Middle, Lower
- ATR: Average True Range
- And more...

**Example:**
```python
df = engineer.calculate_technical_indicators(df.copy())
print(df[['close', 'sma_20', 'rsi_14']].head())
```

##### calculate_statistical_features()

Calculate statistical features.

```python
def calculate_statistical_features(df: pd.DataFrame) -> Dict
```

**Features Generated:**
- Returns: Simple, Log, Cumulative
- Volatility: Realized, Historical
- Distribution: Skewness, Kurtosis
- Autocorrelation: ACF, PACF
- Stationarity: ADF test results

**Example:**
```python
stats = engineer.calculate_statistical_features(df)
print(f"Skewness: {stats['skewness']}")
print(f"Kurtosis: {stats['kurtosis']}")
```

##### calculate_volatility_features()

Calculate volatility measures.

```python
def calculate_volatility_features(df: pd.DataFrame) -> Dict
```

**Features Generated:**
- Bollinger Bands Width
- ATR and Normalized ATR
- Historical Volatility
- Parkinson Volatility
- Garman-Klass Volatility

---

## MongoDB Storage

### MongoDBStorage

Manages data persistence in MongoDB.

```python
from mongodb_storage import MongoDBStorage
```

#### Constructor

```python
MongoDBStorage(
    uri: Optional[str] = None,
    database: Optional[str] = None,
    collection: Optional[str] = None
)
```

**Parameters:**
- `uri` (str): MongoDB connection URI
- `database` (str): Database name
- `collection` (str): Collection name

**Raises:**
- `ConnectionFailure`: If cannot connect to MongoDB

#### Methods

##### create_company_profile()

Create a company profile object.

```python
def create_company_profile(
    symbol: str,
    exchange: str,
    raw_data: pd.DataFrame,
    features: Dict,
    fundamental_data: Dict
) -> Dict
```

**Returns:**
```python
{
    'symbol': 'AAPL',
    'exchange': 'US',
    'created_at': datetime,
    'last_updated': datetime,
    'data_date_range': {
        'start': '2024-01-01',
        'end': '2024-12-31'
    },
    'raw_data': {...},
    'features': {...},
    'fundamental_data': {...},
    'metadata': {...}
}
```

##### save_profile()

Save profile to MongoDB.

```python
def save_profile(profile: Dict) -> bool
```

**Returns:**
- `bool`: True if successful

**Raises:**
- `DuplicateKeyError`: If profile already exists

**Example:**
```python
storage = MongoDBStorage()
profile = storage.create_company_profile(...)
if storage.save_profile(profile):
    print("Profile saved successfully")
```

##### get_profile()

Retrieve profile by symbol.

```python
def get_profile(symbol: str, exchange: str) -> Optional[Dict]
```

**Returns:**
- Profile dict or None if not found

**Example:**
```python
profile = storage.get_profile('AAPL', 'US')
if profile:
    print(f"Last updated: {profile['last_updated']}")
```

##### get_all_profiles()

Retrieve all profiles with pagination.

```python
def get_all_profiles(
    limit: int = 100,
    skip: int = 0
) -> List[Dict]
```

**Parameters:**
- `limit` (int): Max profiles to return
- `skip` (int): Skip N profiles

**Example:**
```python
profiles = storage.get_all_profiles(limit=50, skip=100)
print(f"Retrieved {len(profiles)} profiles")
```

##### update_profile()

Update existing profile.

```python
def update_profile(
    symbol: str,
    exchange: str,
    update: Dict
) -> bool
```

**Example:**
```python
storage.update_profile('AAPL', 'US', {
    'last_updated': datetime.now(),
    'features': new_features
})
```

##### delete_profile()

Delete profile.

```python
def delete_profile(symbol: str, exchange: str) -> bool
```

---

## Configuration

### Settings

Configuration management using Pydantic.

```python
from config import settings
```

#### Environment Variables

```bash
# EODHD API
EODHD_API_KEY=<your-api-key>
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

# Email (Optional)
PIPELINE_ALERT_EMAIL=your-email@gmail.com
PIPELINE_ALERT_PASSWORD=your-app-password
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
```

#### Accessing Settings

```python
from config import settings

api_key = settings.eodhd_api_key
db_uri = settings.mongodb_uri
rate_limit = settings.api_calls_per_minute
```

---

## Utilities

### AdaptiveRateLimiter

Manages API rate limiting with adaptive backoff.

```python
from utils.rate_limiter import AdaptiveRateLimiter
```

#### Constructor

```python
AdaptiveRateLimiter(
    calls_per_minute: int = 80,
    calls_per_day: int = 95000
)
```

#### Methods

##### wait_if_needed()

Wait if approaching rate limits.

```python
def wait_if_needed() -> None
```

Should be called before making an API call.

##### record_call()

Record that an API call was made.

```python
def record_call() -> None
```

Should be called after successful API call.

##### get_stats()

Get current rate limiter status.

```python
def get_stats() -> Dict
```

**Example:**
```python
limiter = AdaptiveRateLimiter(80, 95000)

for symbol in symbols:
    limiter.wait_if_needed()
    data = fetch_data(symbol)  # API call
    limiter.record_call()

stats = limiter.get_stats()
print(f"Daily calls: {stats['daily_used']}/{stats['daily_limit']}")
```

### CacheStore

Persistent local caching for profile data.

```python
from dashboard.models import CacheStore
```

#### Methods

##### update_daily_api_calls()

Update API call counter.

```python
def update_daily_api_calls(count: int) -> None
```

##### get_daily_api_calls()

Get current daily API call count.

```python
def get_daily_api_calls() -> int
```

##### cache_companies()

Cache company list.

```python
def cache_companies(companies: List[Dict]) -> None
```

##### get_cached_companies()

Retrieve cached companies.

```python
def get_cached_companies() -> Optional[List[Dict]]
```

---

## Dashboard Components

### Main Window

```python
from dashboard.ui.main_window import MainWindow
```

PyQt6 main application window with tab-based interface.

**Tabs:**
1. Pipeline Control - Symbol input and processing controls
2. Monitor - Real-time metrics and logs
3. Database Profiles - Profile browser and editor
4. Settings - Configuration panel

### Controllers

#### PipelineController

```python
from dashboard.controllers.pipeline_controller import PipelineController
```

Manages parallel processing with ThreadPoolExecutor.

**Methods:**
- `start(symbols, options)` - Start processing
- `pause()` - Pause all workers
- `resume()` - Resume paused workers
- `stop()` - Stop and clear queue
- `cancel_symbol(symbol)` - Cancel specific symbol

#### DatabaseController

```python
from dashboard.controllers.database_controller import DatabaseController
```

Manages database operations.

**Methods:**
- `get_profiles()` - List all profiles
- `get_profile(symbol)` - Get specific profile
- `delete_profile(symbol)` - Delete profile
- `export_profiles(path)` - Export to file

### Services

#### MetricsCalculator

```python
from dashboard.services.metrics_calculator import MetricsCalculator
```

Calculates and tracks pipeline metrics.

**Methods:**
- `update_symbol_progress(symbol, progress)` - Update progress
- `calculate_eta()` - Calculate estimated time to completion
- `get_summary()` - Get metrics summary

#### LogEmailAlerter

```python
from dashboard.services.log_emailer import LogEmailAlerter
```

Sends email alerts on critical events.

**Methods:**
- `send_alert(subject, message)` - Send email alert
- `attach_screenshot(path)` - Include screenshot

---

**Last Updated**: November 28, 2025  
**Version**: 1.1.0

