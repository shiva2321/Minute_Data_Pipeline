# API Reference Guide

## Table of Contents
1. [Pipeline Class](#pipeline-class)
2. [Data Fetcher](#data-fetcher)
3. [Feature Engineer](#feature-engineer)
4. [MongoDB Storage](#mongodb-storage)
5. [Configuration](#configuration)

---

## Pipeline Class

**File**: `pipeline.py`

### MinuteDataPipeline

Main orchestrator for the entire pipeline.

#### Initialization
```python
from pipeline import MinuteDataPipeline

pipeline = MinuteDataPipeline()
```

#### Methods

##### `process_symbol()`
Process a single symbol through the entire pipeline.

```python
success = pipeline.process_symbol(
    symbol='AAPL',              # Stock symbol (required)
    exchange='US',              # Exchange code (default: 'US')
    interval='1m',              # Time interval: '1m', '5m', '1h' (default: '1m')
    from_date='2024-11-01',    # Start date YYYY-MM-DD (optional)
    to_date='2024-11-27',      # End date YYYY-MM-DD (optional)
    fetch_fundamentals=True     # Fetch fundamental data (default: True)
)
# Returns: bool (True if successful)
```

##### `process_multiple_symbols()`
Process multiple symbols with progress tracking.

```python
results = pipeline.process_multiple_symbols(
    symbols=['AAPL', 'MSFT', 'GOOGL'],  # List of symbols (required)
    exchange='US',                       # Exchange code
    interval='5m',                       # Time interval
    from_date=None,                     # Start date (optional)
    to_date=None,                       # End date (optional)
    fetch_fundamentals=True             # Fetch fundamentals
)
# Returns: dict with 'successful', 'failed', 'total' keys
```

##### `get_profile()`
Retrieve a stored company profile.

```python
profile = pipeline.get_profile(
    symbol='AAPL',    # Stock symbol
    exchange='US'     # Exchange code
)
# Returns: dict or None
```

##### `get_all_profiles()`
Retrieve all stored profiles.

```python
profiles = pipeline.get_all_profiles(limit=100)
# Returns: list of dicts
```

##### `export_profile_to_dict()`
Export profile with ObjectId converted to string.

```python
profile = pipeline.export_profile_to_dict('AAPL', 'US')
# Returns: dict with serializable values
```

##### `get_pipeline_stats()`
Get statistics about the pipeline.

```python
stats = pipeline.get_pipeline_stats()
# Returns: dict with pipeline statistics
```

---

## Data Fetcher

**File**: `data_fetcher.py`

### EODHDDataFetcher

Handles all API communication with EODHD.

#### Initialization
```python
from data_fetcher import EODHDDataFetcher

fetcher = EODHDDataFetcher(api_key='optional_key')
# Uses settings.eodhd_api_key if not provided
```

#### Methods

##### `fetch_intraday_data()`
Fetch minute-by-minute historical data.

```python
df = fetcher.fetch_intraday_data(
    symbol='AAPL',              # Stock symbol (required)
    interval='1m',              # '1m', '5m', '1h' (default: '1m')
    from_date='2024-11-01',    # Start date (optional)
    to_date='2024-11-27',      # End date (optional)
    exchange='US'               # Exchange code (default: 'US')
)
# Returns: pandas DataFrame with columns:
#   - datetime: timestamp
#   - open, high, low, close: prices
#   - volume: trading volume
```

##### `fetch_fundamental_data()`
Fetch company fundamental data.

```python
fundamentals = fetcher.fetch_fundamental_data(
    symbol='AAPL',
    exchange='US'
)
# Returns: dict with fundamental data sections:
#   - General: company info
#   - Highlights: key metrics
#   - Valuation: valuation metrics
#   - etc.
```

##### `fetch_multiple_symbols()`
Fetch data for multiple symbols with rate limiting.

```python
data_dict = fetcher.fetch_multiple_symbols(
    symbols=['AAPL', 'MSFT'],
    interval='5m',
    from_date=None,
    to_date=None,
    exchange='US',
    delay=0.5  # Delay between requests in seconds
)
# Returns: dict mapping symbols to DataFrames
```

---

## Feature Engineer

**File**: `feature_engineering.py`

### FeatureEngineer

Calculates all technical, statistical, and ML features.

#### Initialization
```python
from feature_engineering import FeatureEngineer

fe = FeatureEngineer()
```

#### Methods

##### `process_full_pipeline()`
Run complete feature engineering pipeline.

```python
result = fe.process_full_pipeline(df)
# Input: DataFrame with OHLCV data
# Returns: dict with keys:
#   - 'processed_df': DataFrame with all features
#   - 'statistical_features': dict of statistical metrics
#   - 'time_features': dict of time-based features
#   - 'microstructure_features': dict of microstructure metrics
#   - 'summary': dict with data summary
```

##### `calculate_technical_indicators()`
Calculate technical indicators.

```python
df_with_indicators = fe.calculate_technical_indicators(df)
# Adds columns for:
#   - SMA/EMA (multiple periods)
#   - Bollinger Bands
#   - RSI
#   - MACD
#   - ATR
#   - Stochastic
#   - Volume indicators
#   - Momentum
#   - ROC
```

##### `calculate_statistical_features()`
Calculate statistical features.

```python
stats = fe.calculate_statistical_features(df)
# Returns dict with:
#   - Price statistics (mean, std, min, max, etc.)
#   - Returns statistics
#   - Volatility measures
#   - Trend analysis
#   - Sharpe ratio
```

##### `calculate_time_based_features()`
Calculate time-based features.

```python
time_features = fe.calculate_time_based_features(df)
# Returns dict with:
#   - Morning/afternoon patterns
#   - Volume by time of day
#   - Volatility patterns
#   - First/last hour performance
```

##### `calculate_ml_features()`
Calculate ML-ready features.

```python
df_ml = fe.calculate_ml_features(df)
# Adds columns for:
#   - Lagged features (price, volume, returns)
#   - Rolling statistics
#   - Price positions
#   - Candlestick features
#   - Pattern recognition
```

##### `calculate_market_microstructure()`
Calculate market microstructure features.

```python
micro = fe.calculate_market_microstructure(df)
# Returns dict with:
#   - Spread measures
#   - Price impact
#   - Liquidity indicators
#   - Order flow imbalance
#   - VWAP
```

---

## MongoDB Storage

**File**: `mongodb_storage.py`

### MongoDBStorage

Handles all database operations.

#### Initialization
```python
from mongodb_storage import MongoDBStorage

storage = MongoDBStorage(
    uri='mongodb://localhost:27017/',  # Optional
    database='stock_data',              # Optional
    collection='company_profiles'       # Optional
)
# Uses settings values if not provided
```

#### Methods

##### `create_company_profile()`
Create a comprehensive company profile.

```python
profile = storage.create_company_profile(
    symbol='AAPL',
    exchange='US',
    raw_data=df,                    # DataFrame with OHLCV
    features=features_dict,         # Dict from FeatureEngineer
    fundamental_data=fundamentals   # Optional fundamental data
)
# Returns: dict with complete profile
```

##### `save_profile()`
Save or update a profile in MongoDB.

```python
success = storage.save_profile(profile)
# Returns: bool (True if successful)
```

##### `get_profile()`
Retrieve a specific profile.

```python
profile = storage.get_profile('AAPL', 'US')
# Returns: dict or None
```

##### `get_all_profiles()`
Retrieve all profiles.

```python
profiles = storage.get_all_profiles(limit=100)
# Returns: list of dicts
```

##### `delete_profile()`
Delete a profile.

```python
success = storage.delete_profile('AAPL', 'US')
# Returns: bool
```

##### `get_profiles_by_sector()`
Get all profiles in a sector.

```python
profiles = storage.get_profiles_by_sector('Technology')
# Returns: list of dicts
```

##### `close()`
Close MongoDB connection.

```python
storage.close()
```

---

## Configuration

**File**: `config.py`

### Settings

Global configuration object.

```python
from config import settings

# Access settings
api_key = settings.eodhd_api_key
db_uri = settings.mongodb_uri
interval_days = settings.data_fetch_interval_days
```

#### Available Settings

| Setting | Environment Variable | Default | Description |
|---------|---------------------|---------|-------------|
| `eodhd_api_key` | `EODHD_API_KEY` | '' | EODHD API key (required) |
| `eodhd_base_url` | `EODHD_BASE_URL` | 'https://eodhd.com/api' | API base URL |
| `mongodb_uri` | `MONGODB_URI` | 'mongodb://localhost:27017/' | MongoDB connection URI |
| `mongodb_database` | `MONGODB_DATABASE` | 'stock_data' | Database name |
| `mongodb_collection` | `MONGODB_COLLECTION` | 'company_profiles' | Collection name |
| `data_fetch_interval_days` | `DATA_FETCH_INTERVAL_DAYS` | 30 | Default data fetch period |
| `max_workers` | `MAX_WORKERS` | 5 | Max concurrent workers |
| `batch_size` | `BATCH_SIZE` | 100 | Batch processing size |

---

## Data Structures

### DataFrame Schema (OHLCV)

Input DataFrame from API:
```python
{
    'datetime': pd.Timestamp,  # Timestamp
    'open': float,             # Opening price
    'high': float,             # High price
    'low': float,              # Low price
    'close': float,            # Closing price
    'volume': int              # Trading volume
}
```

### Processed DataFrame

After feature engineering, includes 100+ additional columns:
- Technical indicators (sma_20, rsi_14, macd, etc.)
- ML features (close_lag_1, rolling_mean_20, etc.)
- Pattern features (higher_high, body_pct, etc.)

### Profile Dictionary Structure

```python
{
    'symbol': str,
    'exchange': str,
    'company_name': str,
    'sector': str,
    'industry': str,
    'last_updated': datetime,
    'data_summary': dict,
    'statistical_features': dict,
    'technical_indicators': dict,
    'time_based_features': dict,
    'microstructure_features': dict,
    'performance_metrics': dict,
    'risk_metrics': dict,
    'fundamental_data': dict,
    'data_points_count': int,
    'data_date_range': dict
}
```

---

## Error Handling

All methods include error handling and logging:

```python
try:
    pipeline.process_symbol('AAPL')
except requests.exceptions.RequestException as e:
    # API communication error
    logger.error(f"API error: {e}")
except pymongo.errors.ConnectionFailure as e:
    # MongoDB connection error
    logger.error(f"MongoDB error: {e}")
except Exception as e:
    # General error
    logger.error(f"Unexpected error: {e}")
```

---

## Examples

### Complete Workflow

```python
from pipeline import MinuteDataPipeline

# Initialize
pipeline = MinuteDataPipeline()

# Process symbol
success = pipeline.process_symbol(
    symbol='AAPL',
    interval='5m',
    from_date='2024-11-01',
    to_date='2024-11-27'
)

if success:
    # Retrieve profile
    profile = pipeline.get_profile('AAPL')
    
    # Access features
    stats = profile['statistical_features']
    tech = profile['technical_indicators']
    risk = profile['risk_metrics']
    
    print(f"Sharpe Ratio: {stats['sharpe_ratio']:.2f}")
    print(f"RSI: {tech['rsi_14']:.2f}")
    print(f"Max Drawdown: {risk['max_drawdown']:.2%}")

# Clean up
pipeline.close()
```

### Custom Feature Engineering

```python
from feature_engineering import FeatureEngineer
import pandas as pd

# Create sample data
df = pd.DataFrame({
    'datetime': pd.date_range('2024-11-01', periods=1000, freq='1min'),
    'open': [100] * 1000,
    'high': [105] * 1000,
    'low': [95] * 1000,
    'close': [102] * 1000,
    'volume': [10000] * 1000
})

# Calculate features
fe = FeatureEngineer()
result = fe.process_full_pipeline(df)

# Access different feature sets
processed_df = result['processed_df']
stats = result['statistical_features']
time_features = result['time_features']
```

### Direct MongoDB Operations

```python
from mongodb_storage import MongoDBStorage

storage = MongoDBStorage()

# Get all tech stocks
tech_profiles = storage.get_profiles_by_sector('Technology')

# Export to analyze
for profile in tech_profiles:
    symbol = profile['symbol']
    sharpe = profile['statistical_features']['sharpe_ratio']
    print(f"{symbol}: {sharpe:.2f}")

storage.close()
```

---

## Best Practices

1. **Always close connections**:
   ```python
   pipeline.close()
   storage.close()
   ```

2. **Use context managers** (future enhancement):
   ```python
   # Not yet implemented, but planned
   with MinuteDataPipeline() as pipeline:
       pipeline.process_symbol('AAPL')
   ```

3. **Handle errors gracefully**:
   ```python
   if not pipeline.process_symbol('AAPL'):
       logger.error("Failed to process AAPL")
   ```

4. **Check data before processing**:
   ```python
   df = fetcher.fetch_intraday_data('AAPL')
   if not df.empty:
       features = fe.process_full_pipeline(df)
   ```

5. **Use appropriate intervals**:
   - Testing: Use '5m' or '1h'
   - Production: Use '1m' for detailed analysis
   - Overview: Use '1h' for quick summaries

---

**For more details, see inline docstrings in each module.**

