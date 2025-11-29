# Quick Reference Guide

Fast lookup for common tasks and commands.

## Command Reference

### Starting the Dashboard

```bash
# Using batch file (Windows)
run_dashboard.bat

# Using PowerShell
.venv\Scripts\python dashboard/main.py

# Using quick start
python quick_start.py
```

### Environment Setup

```bash
# Create virtual environment
python -m venv .venv
.venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Update dependencies
pip install -r requirements.txt --upgrade
```

### Testing

```bash
# Run all tests
pytest tests/

# Run specific test file
pytest tests/unit/test_feature_engineering.py

# Run with verbose output
pytest -v tests/

# Run with coverage
pytest --cov=dashboard tests/
```

## Dashboard Quick Tasks

### Process Symbols

1. Enter tickers: `AAPL,MSFT,GOOGL`
2. Set history: `2 years` or `All Available`
3. Click "Start Pipeline"

### Browse Companies

1. Click "Browse Companies" button
2. Search for company name
3. Select checkbox for symbol
4. Click "Select Top N"

### Monitor Progress

- **Queue Tab**: Shows all processing symbols
- **Status Column**: Current stage (Fetching/Engineering/Storing)
- **Progress Bar**: Percentage complete
- **Live Logs**: Real-time activity log

### Manage Cache

1. Click "Cache Manager" tab
2. View cached symbols and date ranges
3. Right-click symbol → "Delete Cache"
4. Or use "Clear All Cache" button

### View Results

1. Click "Database Profiles" tab
2. Select symbol from list
3. View profile details
4. Export if needed

## Configuration Shortcuts

### Environment Variables (.env)

```ini
EODHD_API_KEY=your_key_here
MONGODB_URI=mongodb://localhost:27017/
MONGODB_DB=Entities
DEBUG=false
LOG_LEVEL=INFO
```

### Common Settings (config.py)

```python
# Number of parallel workers
MAX_WORKERS = 10

# Cache settings
CACHE_SIZE_MB = 2048  # 2GB
CACHE_TTL_HOURS = 720  # 30 days

# API limits
API_CALLS_PER_MINUTE = 80
API_CALLS_PER_DAY = 95000
```

## Performance Tuning

### Optimal Settings

| Setting | Value | Notes |
|---------|-------|-------|
| Workers | 10 | For 6-core CPU, 32GB RAM |
| Chunk Size | 30 days | Recommended by API |
| History | 2-5 years | Start small, scale up |
| Cache TTL | 30 days | Balance storage/freshness |
| Cache Size | 2GB | Supports 10-15 symbols |

### Troubleshooting Performance

```
Slow processing?
├─ Reduce workers (check CPU usage)
├─ Increase history gradually
├─ Clear old cache entries
└─ Check system resources

High memory usage?
├─ Reduce number of workers
├─ Reduce number of symbols
├─ Clear cache
└─ Check for memory leaks
```

## Common Errors & Fixes

### "API Rate Limit Exceeded"
- Wait 1 minute for minute limit reset
- Or wait until midnight for daily reset
- Reduce number of workers

### "MongoDB Connection Error"
```bash
# Verify MongoDB running
mongod --dbpath "C:\data\db"

# Or check connection string in .env
MONGODB_URI=mongodb://localhost:27017/
```

### "Module Not Found"
```bash
# Reinstall dependencies
pip install -r requirements.txt --force-reinstall
```

### "Dashboard Won't Start"
```bash
# Run with error output
python dashboard/main.py

# Check Python version
python --version  # Should be 3.8+
```

## File Organization

```
Minute_Data_Pipeline/
├── config.py                  # Configuration
├── requirements.txt           # Dependencies
├── .env.example              # Example env vars
├── dashboard/                # Dashboard app
├── pipeline.py               # Core pipeline
├── feature_engineering.py    # Feature extraction
├── data_fetcher.py           # API interactions
├── mongodb_storage.py        # Database layer
├── logs/                     # Log files
├── tests/                    # Unit tests
├── samples/                  # Sample data
├── scripts/                  # Utility scripts
└── docs/                     # Documentation
```

## API Keys & Credentials

### Getting EODHD API Key

1. Visit https://eodhd.com
2. Sign up for account
3. Get free or paid plan
4. Copy API key
5. Add to `.env` file

### MongoDB Connection

```
Local MongoDB:
mongodb://localhost:27017/

Remote MongoDB Atlas:
mongodb+srv://user:password@cluster.mongodb.net/
```

## Data Structures

### Profile Object

```python
{
    'symbol': 'AAPL',
    'data_date_range': {
        'start': '2023-01-01',
        'end': '2025-11-28'
    },
    'data_points_count': 390588,
    'statistical_features': {...},
    'technical_indicators': {...},
    'ml_profile': {...},
    'risk_metrics': {...}
}
```

### Cache Entry

```python
{
    'symbol': 'AAPL',
    'start_date': '2023-01-01',
    'end_date': '2023-02-01',
    'rows': 4390,
    'created_at': '2025-11-28T10:00:00',
    'size_bytes': 1256000
}
```

## Rate Limiting Details

### Global Limits
- Per minute: 80 calls
- Per day: 95,000 calls

### Per-Worker Allocation (10 workers)
- Per worker per minute: 7 calls (with 0.9 safety factor)
- Per worker per day: 8,550 calls

### Adaptive Throttling
- Automatic backoff when approaching limits
- Exponential retry on failures
- Per-minute limit resets every minute
- Per-day limit resets at midnight UTC

## Logs Location

```
logs/
├── pipeline_2025-11-28.log    # Daily pipeline logs
├── error_2025-11-28.log       # Error log
└── api_calls_2025-11-28.log   # API activity
```

### Viewing Logs

```bash
# View latest log
type logs\pipeline_2025-11-28.log

# Follow log in real-time
Get-Content logs\pipeline_2025-11-28.log -Wait
```

## Keyboard Shortcuts (Dashboard)

| Shortcut | Action |
|----------|--------|
| `Ctrl+S` | Start Pipeline |
| `Ctrl+P` | Pause Pipeline |
| `Ctrl+X` | Stop Pipeline |
| `Ctrl+C` | Clear Queue |
| `Ctrl+L` | Clear Logs |
| `Ctrl+Q` | Quit Dashboard |

## Status Codes

| Status | Meaning |
|--------|---------|
| Queued | Waiting to process |
| Fetching | Downloading data |
| Engineering | Computing features |
| Storing | Saving to MongoDB |
| Complete | Successfully finished |
| Failed | Error occurred |
| Skipped | Intentionally skipped |
| Paused | User paused processing |

## Feature Categories

### Statistical Features (27)
- Price stats: mean, std, skewness, kurtosis
- Return stats: mean, std, skewness, kurtosis
- Volume stats: mean, median, std
- Volatility: intraday, close-to-close, trend

### Technical Indicators (13)
- Moving Averages: SMA, EMA
- Bollinger Bands: upper, middle, lower
- RSI: 14, 28 period
- MACD: value, signal, histogram
- ATR, Stochastic

### Microstructure Features (6)
- Spread: average, volatility
- Price impact: average
- Amihud illiquidity
- Volume weighted price
- Order flow imbalance

### Multi-Timeframe (16)
- 5m, 15m, 1h, 1d volatility
- Volume metrics
- Returns
- Trend slopes

## Documentation Links

| Document | Purpose |
|----------|---------|
| [README](./README.md) | Documentation index |
| [Architecture](./ARCHITECTURE.md) | System design |
| [Getting Started](./GETTING_STARTED.md) | Setup guide |
| [API Reference](./API_REFERENCE.md) | Code documentation |
| [Dashboard Guide](./DASHBOARD_USER_GUIDE.md) | UI guide |
| [Troubleshooting](./TROUBLESHOOTING.md) | Common issues |

---

**Last Updated**: November 28, 2025  
**Version**: 1.1.1

