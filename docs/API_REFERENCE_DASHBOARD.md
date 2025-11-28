# API Reference - New Dashboard Components

## Module Index

### Models
- [CacheStore](#cachestore) - SQLite persistence layer

### Services
- [LogEmailAlerter](#logoemailer) - Email notifications
- [MetricsCalculator](#metricscalculator) - Real-time metrics
- [APIStatsTracker](#apistats tracker) - API rate tracking

### Dialogs
- [CompanySelectorDialog](#companyselectordialog) - Company browser
- [ReprocessDialog](#reprocessdialog) - Reprocess options

### Widgets
- [LogViewer](#logviewer-enhanced) - Enhanced log display
- [SymbolQueueTable](#symbolqueuetable-enhanced) - Queue with micro-stages
- [APIUsageWidget](#apiusagewidget-enhanced) - Persistent API display

---

## CacheStore

**Module:** `dashboard.models.cache_store`

SQLite-backed persistent data storage.

### Constructor

```python
from dashboard.models import CacheStore

# Default location: ~/.pipeline_cache.db
cache = CacheStore()

# Custom location
cache = CacheStore(db_path=Path('/path/to/cache.db'))

# In-memory (for testing)
cache = CacheStore(db_path=Path(':memory:'))
```

### API Usage Methods

#### `get_daily_api_calls(date=None) -> int`
Get API call count for a specific date (default: today).

```python
calls_today = cache.get_daily_api_calls()
calls_yesterday = cache.get_daily_api_calls(datetime(2025, 11, 27))
```

#### `update_daily_api_calls(calls, date=None)`
Update API call count for a date.

```python
cache.update_daily_api_calls(50230)  # Today
cache.update_daily_api_calls(95000, datetime(2025, 11, 27))
```

#### `increment_daily_api_calls(increment=1, date=None)`
Increment API call count.

```python
cache.increment_daily_api_calls(5)  # Add 5 calls today
```

#### `reset_daily_api_calls_if_new_day() -> bool`
Auto-reset if calendar day changed.

```python
if cache.reset_daily_api_calls_if_new_day():
    print("API stats reset for new day")
```

#### `is_company_list_stale(max_age_days=7) -> bool`
Check if company list cache is outdated.

```python
if cache.is_company_list_stale(max_age_days=7):
    print("Company list is more than 7 days old")
```

### Company List Methods

#### `save_company_list(companies: List[Dict])`
Cache company list from EODHD.

```python
companies = [
    {'Code': 'AAPL', 'Exchange': 'NASDAQ', 'Name': 'Apple Inc.', ...},
    {'Code': 'MSFT', 'Exchange': 'NASDAQ', 'Name': 'Microsoft Corp.', ...}
]
cache.save_company_list(companies)
```

#### `get_company_list() -> List[Dict]`
Get all cached companies.

```python
all_companies = cache.get_company_list()
# Returns list of dicts: [symbol, exchange, company_name]
```

#### `search_companies(query: str) -> List[Dict]`
Search by symbol or name (case-insensitive).

```python
results = cache.search_companies('apple')
# Returns companies matching "apple" in symbol or name
```

### Session Settings Methods

#### `save_session_settings(settings: Dict[str, Any])`
Persist user settings.

```python
settings = {
    'last_symbols': ['AAPL', 'MSFT'],
    'window_geometry': (100, 100, 800, 600),
    'theme': 'dark'
}
cache.save_session_settings(settings)
```

#### `load_session_settings() -> Dict[str, Any]`
Load persisted settings.

```python
settings = cache.load_session_settings()
symbols = settings.get('last_symbols', [])
```

### Cleanup

```python
# Close database connection
cache.close()

# Use context manager for automatic cleanup
with CacheStore() as cache:
    cache.update_daily_api_calls(100)
    # Automatically closes on exit
```

---

## LogEmailAlerter

**Module:** `dashboard.services.log_emailer`

Send email notifications for critical errors.

### Constructor

```python
from dashboard.services import LogEmailAlerter

alerter = LogEmailAlerter(
    smtp_server='smtp.gmail.com',
    smtp_port=587,
    sender_email='your_email@gmail.com',
    sender_password='app_password_here',
    recipient_emails=['admin@example.com', 'ops@example.com'],
    use_tls=True
)
```

### Methods

#### `send_critical_error_alert(error_message, error_type='CRITICAL ERROR', context=None, screenshot_path=None, additional_logs=None) -> bool`

Send error alert email.

```python
alerter.send_critical_error_alert(
    error_message='Database connection failed: Connection refused',
    error_type='DATABASE_ERROR',
    context='While processing AAPL',
    screenshot_path=Path('/tmp/dashboard.png'),
    additional_logs=[
        '[14:32:15] INFO | Starting AAPL',
        '[14:32:20] ERROR | Connection refused'
    ]
)
```

#### `send_processing_summary(summary_stats, successful_symbols, failed_symbols, duration_seconds) -> bool`

Send end-of-run summary.

```python
alerter.send_processing_summary(
    summary_stats={
        'api_calls': 250,
        'data_points': 6546,
        'features_count': 200
    },
    successful_symbols=['AAPL', 'MSFT', 'GOOGL'],
    failed_symbols=['NVDA'],
    duration_seconds=3614.2
)
```

#### `test_connection() -> bool`

Test email configuration.

```python
if alerter.test_connection():
    print("Email configuration valid")
else:
    print("Email configuration failed")
```

### Rate Limiting

Emails are rate-limited to prevent spam (default: 5-minute minimum between same error type).

```python
alerter.min_alert_interval = 300  # Seconds between alerts of same type
```

---

## MetricsCalculator

**Module:** `dashboard.services.metrics_calculator`

Real-time ETA and performance metrics.

### Constructor & Initialization

```python
from dashboard.services import MetricsCalculator

calc = MetricsCalculator()

# Initialize at pipeline start
calc.initialize(total_symbols=10, start_time=time.time())
```

### Methods

#### `mark_symbol_started(symbol, start_time=None)`
Record symbol processing start.

```python
calc.mark_symbol_started('AAPL', time.time())
```

#### `mark_symbol_completed(symbol)`
Record symbol processing completion and calculate duration.

```python
calc.mark_symbol_completed('AAPL')
# Duration automatically calculated from start time
```

#### `calculate_eta_seconds(processing_count=0) -> Optional[int]`
Get ETA in seconds (None if cannot calculate).

```python
eta_seconds = calc.calculate_eta_seconds(processing_count=3)
# Returns: 450 (seconds)
```

#### `calculate_eta_string(processing_count=0) -> str`
Get human-readable ETA.

```python
eta = calc.calculate_eta_string(processing_count=3)
# Returns: "7m 30s" or "3h 15m 22s" or "Complete"
```

#### `calculate_progress_percent() -> int`
Get overall progress percentage.

```python
progress = calc.calculate_progress_percent()
# Returns: 45 (45% complete)
```

#### `get_throughput_symbols_per_minute() -> float`
Calculate processing speed.

```python
speed = calc.get_throughput_symbols_per_minute()
# Returns: 1.5 (1.5 symbols/minute)
```

#### `get_summary_stats(processing_count=0) -> Dict`
Get comprehensive metrics summary.

```python
stats = calc.get_summary_stats(processing_count=3)
# Returns:
# {
#     'completed': 4,
#     'remaining': 6,
#     'processing': 3,
#     'progress_percent': 40,
#     'average_time_per_symbol': 145.3,
#     'eta_seconds': 450,
#     'eta_string': '7m 30s',
#     'throughput_symbols_per_minute': 1.65,
#     'elapsed_seconds': 348.5
# }
```

#### `get_formatted_metrics(processing_count=0) -> str`
Get formatted display string.

```python
display = calc.get_formatted_metrics(processing_count=3)
# Returns: "Progress: 40% | Completed: 4/10 | ETA: 7m 30s | Throughput: 1.65 sym/min"
```

---

## APIStatsTracker

**Module:** `dashboard.services.metrics_calculator`

Track API rate limiting.

### Constructor

```python
from dashboard.services import APIStatsTracker

tracker = APIStatsTracker()
```

### Methods

#### `add_call(calls=1)`
Record API calls made.

```python
tracker.add_call(5)  # Add 5 calls
```

#### `reset_minute_if_needed() -> bool`
Reset minute counter if 60 seconds elapsed.

```python
if tracker.reset_minute_if_needed():
    print("Minute counter reset")
```

#### `reset_daily_if_needed() -> bool`
Reset daily counter if 24 hours elapsed.

```python
if tracker.reset_daily_if_needed():
    print("Daily counter reset")
```

#### `get_minute_remaining(limit) -> int`
Get remaining calls for this minute.

```python
remaining = tracker.get_minute_remaining(limit=80)
# Returns: 42 (42 calls remaining)
```

#### `get_daily_remaining(limit) -> int`
Get remaining calls for today.

```python
remaining = tracker.get_daily_remaining(limit=95000)
```

#### `get_stats(minute_limit, daily_limit) -> Dict`
Get comprehensive API stats.

```python
stats = tracker.get_stats(minute_limit=80, daily_limit=95000)
# Returns:
# {
#     'minute_calls': 38,
#     'minute_remaining': 42,
#     'minute_limit': 80,
#     'minute_percent': 47,
#     'daily_calls': 45230,
#     'daily_remaining': 49770,
#     'daily_limit': 95000,
#     'daily_percent': 47,
#     'total_calls': 45230
# }
```

---

## CompanySelectorDialog

**Module:** `dashboard.dialogs.company_selector_dialog`

Browse and select companies.

### Constructor

```python
from dashboard.dialogs import CompanySelectorDialog
from dashboard.models import CacheStore

cache = CacheStore()
dialog = CompanySelectorDialog(cache, parent=main_window)
```

### Signals

#### `companies_selected(List[str])`
Emitted when user selects companies.

```python
dialog.companies_selected.connect(on_companies_selected)

def on_companies_selected(symbols):
    print(f"Selected: {symbols}")  # ['AAPL', 'MSFT']
```

### Usage

```python
if dialog.exec() == QDialog.DialogCode.Accepted:
    # User confirmed selection
    pass
else:
    # User cancelled
    pass
```

---

## ReprocessDialog

**Module:** `dashboard.dialogs.reprocess_dialog`

Configure reprocessing strategy.

### Constructor

```python
from dashboard.dialogs import ReprocessDialog

profile = {
    'symbol': 'AAPL',
    'data_points_count': 6546,
    'data_date_range': {
        'start': '2023-11-01',
        'end': '2025-11-28'
    },
    'last_updated': '2025-11-28T14:30:00Z'
}

dialog = ReprocessDialog(symbol='AAPL', profile=profile, parent=main_window)
```

### Signals

#### `reprocess_requested(Dict)`
Emitted when user starts reprocessing.

```python
dialog.reprocess_requested.connect(on_reprocess_requested)

def on_reprocess_requested(settings):
    print(settings)
    # {
    #     'mode': 'full_rebuild' or 'incremental',
    #     'history_years': 5,
    #     'chunk_days': 30,
    #     'create_backup': True
    # }
```

---

## LogViewer (Enhanced)

**Module:** `dashboard.ui.widgets.log_viewer`

Enhanced log display with categorization and font control.

### Constructor

```python
from dashboard.ui.widgets import LogViewer

log_viewer = LogViewer(parent=parent_widget)
```

### Methods

#### `append_log(level, message)`
Add log entry with auto-categorization.

```python
log_viewer.append_log('INFO', 'Pipeline started for AAPL')
log_viewer.append_log('WARNING', 'API rate limit approaching')
log_viewer.append_log('ERROR', 'MongoDB connection failed')
log_viewer.append_log('CRITICAL', 'Fatal error in processing')
log_viewer.append_log('SUCCESS', 'AAPL processing completed')
```

**Available Levels:** DEBUG, INFO, WARNING, ERROR, CRITICAL, SUCCESS

**Auto-detected Categories:** MongoDB, Pipeline, API, General

#### `clear()`
Clear all logs.

```python
log_viewer.clear()
```

### UI Features

- **Font Size Selector:** 9pt-14pt dropdown
- **Filter Dropdown:** Level or Category-based
- **Auto-scroll Toggle:** Enable/disable auto-scroll
- **Clear Button:** Remove all logs

---

## SymbolQueueTable (Enhanced)

**Module:** `dashboard.ui.widgets.symbol_queue_table`

Processing queue with micro-stage progress.

### Constructor

```python
from dashboard.ui.widgets import SymbolQueueTable

queue_table = SymbolQueueTable(parent=parent_widget)
```

### Methods

#### `update_symbol(symbol, status, progress=0, **kwargs)`
Update symbol row with all details.

```python
queue_table.update_symbol(
    symbol='AAPL',
    status='Fetching',
    progress=45,
    micro_stage='Batch 3/8: 45%',
    data_points=2890,
    date_range='2025-11-01 to 2025-11-28',
    api_calls=125,
    duration=145.2
)
```

**Column Definitions:**
- Symbol: Ticker symbol
- Status: Current status (Queued, Fetching, Engineering, Storing, Complete, Failed)
- Progress: Overall progress percentage
- **Micro-Stage**: Detailed sub-task progress (NEW)
- Data Points: Number of rows fetched
- Date Range: Historical date coverage
- API Calls: Number of API calls used
- Duration: Total processing time in minutes

### Signals

- `retry_requested(symbol)` - User clicked "Retry"
- `remove_requested(symbol)` - User clicked "Remove"
- `view_profile_requested(symbol)` - User clicked "View Profile"
- `export_requested(symbol)` - User clicked "Export"

---

## APIUsageWidget (Enhanced)

**Module:** `dashboard.ui.widgets.api_usage_widget`

Persistent API usage display.

### Constructor

```python
from dashboard.ui.widgets import APIUsageWidget
from dashboard.models import CacheStore

cache = CacheStore()
api_widget = APIUsageWidget(cache_store=cache, parent=parent_widget)
```

### Methods

#### `update_stats(stats)`
Update API usage display.

```python
api_widget.update_stats({
    'daily_calls': 45230,
    'minute_calls': 48,
    'daily_remaining': 49770
})
```

#### `load_persisted_stats()`
Load stats from database on startup (automatic).

#### `save_stats(daily_calls)`
Save to persistent storage (automatic).

#### `reset()`
Reset all counters to zero.

```python
api_widget.reset()
```

### Color Coding

- **Green:** ≤ 60% usage
- **Orange:** 60-80% usage
- **Red:** 80%+ usage

---

## Data Fetcher Extensions

**Module:** `data_fetcher.py`

### New Method

#### `fetch_exchange_symbols(exchange='US', skip_delisted=True) -> List[Dict]`
Fetch all symbols on an exchange from EODHD API.

```python
from data_fetcher import EODHDDataFetcher

fetcher = EODHDDataFetcher()

# Fetch all active companies on US exchanges
symbols = fetcher.fetch_exchange_symbols(exchange='US', skip_delisted=True)

# Returns list of dicts:
# [
#     {
#         'Code': 'AAPL',
#         'Name': 'Apple Inc.',
#         'Exchange': 'NASDAQ',
#         'Country': 'US',
#         'Currency': 'USD',
#         ...other fields...
#     },
#     ...
# ]
```

---

## Usage Examples

### Full Integration Example

```python
# main.py
from dashboard.models import CacheStore
from dashboard.services import MetricsCalculator, LogEmailAlerter
from dashboard.ui.widgets import LogViewer, APIUsageWidget, SymbolQueueTable
from dashboard.dialogs import CompanySelectorDialog, ReprocessDialog

class DashboardApp:
    def __init__(self):
        # Initialize persistence
        self.cache = CacheStore()
        
        # Initialize services
        self.metrics = MetricsCalculator()
        self.emailer = LogEmailAlerter(
            smtp_server='smtp.gmail.com',
            smtp_port=587,
            sender_email='app@example.com',
            sender_password='password',
            recipient_emails=['admin@example.com']
        )
        
        # Initialize UI
        self.log_viewer = LogViewer()
        self.api_widget = APIUsageWidget(cache_store=self.cache)
        self.queue_table = SymbolQueueTable()
        
    def start_pipeline(self, symbols):
        self.metrics.initialize(len(symbols))
        
        for symbol in symbols:
            self.process_symbol(symbol)
    
    def process_symbol(self, symbol):
        self.metrics.mark_symbol_started(symbol)
        self.log_viewer.append_log('INFO', f'Processing {symbol}...')
        
        # Process...
        
        self.metrics.mark_symbol_completed(symbol)
        eta = self.metrics.calculate_eta_string(processing_count=2)
        self.log_viewer.append_log('INFO', f'ETA: {eta}')
```

---

**Complete API Reference. Ready for implementation.**

