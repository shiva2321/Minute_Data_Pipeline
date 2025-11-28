# Stock Pipeline Desktop Dashboard

## Overview

A **professional native desktop application** built with PyQt6 for controlling and monitoring the stock market data pipeline. This application provides real-time visualization, parallel processing control, and comprehensive profile management.

## Features

### 🚀 High-Performance Processing
- **Parallel Processing**: Utilize up to 12 worker threads (optimized for Ryzen 5 7600)
- **Smart Rate Limiting**: Shared rate limiter across all workers
- **Incremental Updates**: Update existing profiles or rebuild from scratch
- **Auto-Retry**: Automatic retry on failed API calls with exponential backoff

### 📊 Real-Time Monitoring
- **Live Progress Tracking**: Monitor each symbol's processing status
- **Detailed Metrics**: Queue size, success/failure rates, ETA calculations
- **API Usage Visualization**: Color-coded progress bars for rate limits
- **Live Logs**: Color-coded log viewer with filtering

### 🗂 Profile Management
- **Database Browser**: Search, filter, and sort stored profiles
- **Profile Editor**: Multi-tab editor with JSON validation
- **Export Functionality**: Export profiles to JSON files
- **Batch Operations**: Process hundreds of symbols simultaneously

### ⚙️ Advanced Configuration
- **API Settings**: Configure EODHD API key and rate limits
- **MongoDB Settings**: Connection URI and database configuration
- **Pipeline Defaults**: History years, chunk size, worker count
- **UI Customization**: Theme, log level, refresh rate

## System Requirements

### Minimum
- **OS**: Windows 10/11, macOS 10.15+, Linux
- **Python**: 3.10+
- **RAM**: 8GB
- **CPU**: 4 cores

### Recommended (Optimized Configuration)
- **CPU**: AMD Ryzen 5 7600 (6 cores, 12 threads)
- **GPU**: RTX 3060 (for future ML features)
- **RAM**: 32GB DDR5
- **Storage**: SSD with 50GB+ free space

## Installation

### 1. Install Dependencies

```bash
# Activate virtual environment
.venv\Scripts\activate  # Windows
source .venv/bin/activate  # Linux/Mac

# Install all dependencies including PyQt6
pip install -r requirements.txt
```

### 2. Configure Environment

Create/update `.env` file:

```env
# EODHD API Configuration
EODHD_API_KEY=your_api_key_here
EODHD_BASE_URL=https://eodhd.com/api

# MongoDB Configuration
MONGODB_URI=mongodb://localhost:27017
DATABASE_NAME=stock_analysis

# Rate Limiting
API_CALLS_PER_MINUTE=80
API_CALLS_PER_DAY=95000

# Processing Defaults
HISTORY_CHUNK_DAYS=5
MAX_HISTORY_YEARS=2
```

### 3. Launch Dashboard

**Windows:**
```bash
run_dashboard.bat
```

**Linux/Mac:**
```bash
python dashboard/main.py
```

## Quick Start Guide

### 1. First-Time Setup

1. **Launch the application**: Run `run_dashboard.bat`
2. **Go to Settings tab**: Configure API key and MongoDB URI
3. **Test connections**: Click "Test" buttons to verify connectivity
4. **Save settings**: Click "Save Settings"

### 2. Processing Symbols

#### Manual Input
1. Go to **Pipeline Control** tab
2. Enter symbols in the input field (comma-separated): `AAPL, MSFT, GOOGL`
3. Select processing mode:
   - **Incremental**: Update existing profiles
   - **Full Rebuild**: Fetch complete history (1-5 years)
4. Configure options:
   - History Years: 2 (default)
   - Chunk Size: 5 days (default)
   - Max Workers: 10 threads (optimized for Ryzen 5 7600)
5. Click **▶ Start Pipeline**

#### File Input
1. Create a text file with symbols (one per line):
   ```
   AAPL
   MSFT
   GOOGL
   AMZN
   NVDA
   ```
2. Check **"Load from file"**
3. Browse and select your file
4. Click **▶ Start Pipeline**

### 3. Monitoring Progress

The **Monitor Panel** shows:

- **Real-time Metrics**:
  - Total symbols
  - Queue size
  - Processing count
  - Success/failed/skipped counts
  - ETA

- **API Usage**:
  - Daily calls: X / 95,000
  - This minute: X / 80
  - Color-coded warnings (green → yellow → red)

- **Processing Queue Table**:
  - Symbol status with emoji indicators
  - Progress percentage
  - Data points fetched
  - Date range
  - API calls used
  - Processing duration

- **Live Logs**:
  - Color-coded messages (DEBUG, INFO, WARNING, ERROR, SUCCESS)
  - Filter by log level
  - Auto-scroll option

### 4. Browsing Profiles

1. Go to **Database Profiles** tab
2. **Search**: Enter symbol to filter
3. **Sort**: Choose sorting criteria
4. **View**: Select profile and click "View"
5. **Edit**: Modify profile JSON (advanced)
6. **Export**: Save profile to JSON file
7. **Delete**: Remove profile from database

### 5. Viewing Profile Details

The **Profile Editor** shows:

- **Overview Tab**: Summary statistics
  - Symbol, exchange, data points
  - Date range
  - Backfill metadata (API calls, duration)

- **Feature Tabs**: Organized by category
  - Price Features
  - Volume Features
  - Volatility Features
  - Technical Indicators
  - Regime Features
  - Predictions

- **Raw JSON Tab**: Full profile with syntax highlighting
  - Edit and validate JSON
  - Save changes to database

## Architecture

### Project Structure

```
dashboard/
├── main.py                      # Application entry point
├── controllers/
│   ├── pipeline_controller.py   # Parallel processing orchestrator
│   ├── queue_manager.py         # Thread-safe symbol queue
│   └── database_controller.py   # MongoDB operations wrapper
├── ui/
│   ├── main_window.py           # Main application window
│   ├── panels/
│   │   ├── control_panel.py     # Input controls
│   │   ├── monitor_panel.py     # Live progress display
│   │   ├── profile_browser.py   # Database viewer
│   │   └── settings_panel.py    # Configuration
│   └── widgets/
│       ├── symbol_queue_table.py   # Processing queue display
│       ├── log_viewer.py           # Live log viewer
│       ├── profile_editor.py       # JSON editor
│       └── api_usage_widget.py     # Rate limit gauges
└── utils/
    ├── qt_signals.py            # Custom Qt signals
    ├── worker_thread.py         # Background thread wrapper
    └── theme.py                 # Dark theme stylesheet
```

### Threading Model

```
Main Thread (UI)
    │
    ├── QThread: PipelineController
    │       │
    │       └── ThreadPoolExecutor (10 workers)
    │               │
    │               ├── Worker 1: Process Symbol
    │               ├── Worker 2: Process Symbol
    │               ├── ...
    │               └── Worker 10: Process Symbol
    │
    └── Shared: AdaptiveRateLimiter (thread-safe)
```

**Key Points:**
- UI runs on main thread (never blocks)
- Pipeline controller runs on QThread
- Symbol processing uses ThreadPoolExecutor
- All workers share single rate limiter (prevents quota overflow)
- Qt signals for thread-safe UI updates

### Performance Optimization

#### Parallel Processing
- **Default Workers**: 10 threads (for 6-core Ryzen)
- **Max Workers**: 12 (configurable)
- **Thread Safety**: Locks on shared resources
- **Rate Limiting**: Centralized, prevents race conditions

#### Database Caching
- **Cache TTL**: 60 seconds
- **Smart Invalidation**: On updates/deletes
- **Lazy Loading**: Fetch on demand
- **Batch Operations**: Reduce round trips

#### Memory Management
- **Streaming Logs**: 1000-line buffer
- **Profile Pagination**: Load on scroll
- **Garbage Collection**: Clear completed workers

## Configuration

### Settings File

Settings are persisted to `~/.pipeline_dashboard_config.json`:

```json
{
  "api_key": "your_api_key",
  "mongo_uri": "mongodb://localhost:27017",
  "db_name": "stock_analysis",
  "minute_limit": 80,
  "daily_limit": 95000,
  "default_years": 2,
  "default_chunk": 5,
  "max_workers": 10,
  "store_metadata": true,
  "auto_retry": true,
  "theme": "dark",
  "log_level": "INFO",
  "refresh_rate": 2,
  "notifications": false,
  "minimize_tray": false
}
```

### Environment Variables

The dashboard also reads from `.env` file for API/database credentials.

## Troubleshooting

### PyQt6 Import Error

```bash
# Reinstall PyQt6
pip uninstall PyQt6 PyQt6-WebEngine PyQt6-Charts
pip install PyQt6>=6.6.0 PyQt6-WebEngine>=6.6.0 PyQt6-Charts>=6.6.0
```

### MongoDB Connection Failed

1. Check MongoDB is running: `mongod --version`
2. Verify URI in Settings tab
3. Test connection with "Test" button
4. Check firewall settings

### API Rate Limit Exceeded

- Dashboard shows current usage in API Usage widget
- Red bar indicates near/over limit
- Wait for reset (shown in ETA)
- Reduce worker count to slow down calls

### UI Freezing

- Should never happen (processing is threaded)
- If it does, check console for errors
- Try reducing worker count
- Restart application

### Log Errors

Common log messages:

- **"Rate limit: waiting Xs"**: Normal, respecting API limits
- **"API error #N"**: Temporary API issue, auto-retrying
- **"Failed to fetch data"**: Invalid symbol or network issue
- **"Daily limit reached"**: Pause until midnight UTC

## Performance Tips

### Optimal Settings (Ryzen 5 7600)

- **Max Workers**: 10 threads
- **Chunk Size**: 5 days (balances API calls vs data size)
- **History Years**: 2 years (most ML models use 1-2 years)
- **Mode**: Incremental (faster for updates)

### Batch Processing Strategy

For processing 100+ symbols:

1. **Start with small batch** (10-20 symbols) to test
2. **Monitor API usage** in first few minutes
3. **Adjust workers** if hitting rate limits
4. **Use incremental mode** for subsequent runs
5. **Schedule during off-peak** hours

### API Quota Management

- **80 calls/minute** = ~4,800 calls/hour
- **95,000 calls/day** = ~3,958 calls/hour sustained
- Each symbol uses **~250 calls** (2 years, 5-day chunks)
- Daily capacity: **~380 symbols**

## Keyboard Shortcuts

- `Ctrl+R`: Refresh profiles
- `Ctrl+Q`: Quit application
- `F5`: Refresh current view
- `Ctrl+S`: Save settings (in Settings tab)
- `Ctrl+E`: Export profile (in Profile Browser)

## Future Enhancements

- [ ] Export to CSV/Excel
- [ ] Bulk profile operations
- [ ] Advanced filtering (date range, features)
- [ ] Charts and visualizations (PyQt6-Charts)
- [ ] Automated scheduling (cron-like)
- [ ] Email/desktop notifications
- [ ] Profile comparison tool
- [ ] ML model integration
- [ ] Real-time streaming data

## Support

For issues or questions:

1. Check logs in `logs/` directory
2. Review error messages in Log Viewer
3. See `API_REFERENCE.md` for API details
4. Check `FEATURE_GUIDE.md` for feature documentation

## License

© 2025 Minute Data Pipeline. All rights reserved.

---

**Built with**: PyQt6, Python 3.13, MongoDB, EODHD API  
**Optimized for**: AMD Ryzen 5 7600, 32GB RAM, RTX 3060

