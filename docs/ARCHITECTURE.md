# Dashboard Architecture

**Optimized for**: Ryzen 5 7600 (6 cores), 32GB RAM, RTX 3060

## System Overview

```
┌──────────────────────────────────────────────────────────────────┐
│                    DESKTOP DASHBOARD (PyQt6)                     │
│                  Minute Data Pipeline Control Center             │
└──────────────────────────────────────────────────────────────────┘
                              │
              ┌───────────────┴───────────────┐
              ▼                               ▼
    ┌──────────────────────┐        ┌──────────────────────┐
    │   Control Panel      │        │  Monitor Panel       │
    │   (User Input)       │        │  (Live Updates)      │
    └────────┬─────────────┘        └────────▲─────────────┘
             │                               │
             │ Symbols + Settings            │ Qt Signals
             │ Mode, Workers, Years          │ (Thread-Safe)
             │                               │
             ▼                               │
    ┌──────────────────────────────────────────────────┐
    │    PipelineController (QThread)                  │
    │  ┌────────────────────────────────────────────┐  │
    │  │  ThreadPoolExecutor (Independent Workers)  │  │
    │  │  Default: 10 workers (configurable)        │  │
    │  │                                            │  │
    │  │  Each Worker:                              │  │
    │  │  ├─ Independent Rate Limiter               │  │
    │  │  ├─ Own Pipeline Instance                  │  │
    │  │  ├─ Pause/Cancel Events                    │  │
    │  │  └─ Status Tracking                        │  │
    │  │                                            │  │
    │  │  Worker 1 ── Worker 2 ── ... ── Worker N  │  │
    │  └────────────────────────────────────────────┘  │
    │  ┌────────────────────────────────────────────┐  │
    │  │ Metrics Calculator (Real-time stats)       │  │
    │  │ ├─ Progress tracking                       │  │
    │  │ ├─ ETA calculation                         │  │
    │  │ ├─ Success/Failed/Skipped counts           │  │
    │  │ └─ API usage monitoring                    │  │
    │  └────────────────────────────────────────────┘  │
    └──────────────────────────────────────────────────┘
                     │            │
        ┌────────────┼────────────┼────────────┐
        ▼            ▼            ▼            ▼
   ┌────────┐  ┌──────────┐  ┌──────────┐ ┌─────────┐
   │ EODHD  │  │ Feature  │  │ Adaptive │ │ MongoDB │
   │  API   │  │ Engineer │  │   Rate   │ │ Storage │
   │        │  │          │  │ Limiter  │ │         │
   └────────┘  └──────────┘  └──────────┘ └─────────┘
```

## UI Component Hierarchy

```
MainWindow (QMainWindow)
│
├── QTabWidget (4 Tabs)
│   │
│   ├── Tab 1: "Pipeline Control"
│   │   └── ControlPanel
│   │       ├── Input Section
│   │       │   ├── Symbol Input (QLineEdit) - comma-separated
│   │       │   ├── File Browser (QPushButton) - load from file
│   │       │   └── Load Company List (QPushButton) - EODHD/cache
│   │       │
│   │       ├── Configuration Section
│   │       │   ├── Mode Selection (QRadioButton)
│   │       │   │   ├─ Incremental (update only new data)
│   │       │   │   └─ Full History (complete backfill)
│   │       │   │
│   │       │   ├── History Years (QSpinBox) - 1 to 30
│   │       │   ├── Chunk Size (QSpinBox) - 1 to 30 days
│   │       │   └── Max Workers (QSpinBox) - 1 to 20
│   │       │
│   │       └── Action Buttons
│   │           ├─ ▶ Start (begin processing)
│   │           ├─ ⏸ Pause (pause all workers)
│   │           ├─ ⏹ Stop (halt and reset)
│   │           └─ 🗑 Clear (clear queue)
│   │
│   ├── Tab 2: "Monitor"
│   │   └── MonitorPanel (Compact layout - 60% space saved)
│   │       ├── Metrics Bar (Single Line)
│   │       │   ├─ Total symbols
│   │       │   ├─ Succeeded count
│   │       │   ├─ Failed count
│   │       │   ├─ Skipped count
│   │       │   ├─ Queue count
│   │       │   ├─ Currently processing
│   │       │   └─ ETA remaining
│   │       │
│   │       ├── APIUsageWidget
│   │       │   ├─ Minute Gauge (0-80 calls/min)
│   │       │   │   └─ Color: Green (OK) → Yellow (warning) → Red (limit)
│   │       │   └─ Daily Gauge (0-95,000 calls/day)
│   │       │       └─ Color: Green (OK) → Yellow (warning) → Red (limit)
│   │       │
│   │       ├── SymbolQueueTable
│   │       │   ├─ Symbol name
│   │       │   ├─ Status (queued/fetching/processing/storing/completed/failed)
│   │       │   ├─ Progress bar (0-100%)
│   │       │   ├─ Micro-stage (Fetch/Engineer/Store)
│   │       │   ├─ Data points fetched
│   │       │   ├─ API calls used
│   │       │   └─ Duration & context menu (pause/resume/remove)
│   │       │
│   │       └── LogViewer (Auto-scroll, color-coded)
│   │           ├─ DEBUG (cyan)
│   │           ├─ INFO (green)
│   │           ├─ WARNING (yellow)
│   │           ├─ ERROR (red)
│   │           └─ SUCCESS (blue)
│   │
│   ├── Tab 3: "Profiles"
│   │   └── ProfileBrowser
│   │       ├── Search Bar (QLineEdit)
│   │       ├── Profile Table
│   │       │   ├─ Symbol
│   │       │   ├─ Exchange
│   │       │   ├─ Last Updated
│   │       │   ├─ Record Count
│   │       │   └─ Status
│   │       │
│   │       ├── Profile Detail View
│   │       │   ├─ General info
│   │       │   ├─ Feature tabs
│   │       │   │   ├─ Technical
│   │       │   │   ├─ Statistical
│   │       │   │   └─ Risk
│   │       │   └─ JSON editor (ProfileEditor)
│   │       │
│   │       └── Action Buttons
│   │           ├─ View
│   │           ├─ Edit
│   │           ├─ Export
│   │           └─ Delete
│   │
│   └── Tab 4: "Settings"
│       └── SettingsPanel
│           ├── API Configuration
│           │   ├─ EODHD API Key (QLineEdit)
│           │   ├─ Base URL
│           │   └─ API timeout
│           │
│           ├── Database Configuration
│           │   ├─ MongoDB URI (QLineEdit)
│           │   ├─ Database name
│           │   └─ Collection name
│           │
│           ├── Pipeline Defaults
│           │   ├─ Default workers
│           │   ├─ Default chunk size
│           │   └─ Default history years
│           │
│           ├── Email Alerts (Optional)
│           │   ├─ Sender email
│           │   ├─ App password
│           │   ├─ SMTP server
│           │   └─ SMTP port
│           │
│           └── Action Buttons
│               ├─ Test Connection
│               ├─ Save Settings
│               └─ Reset to Defaults
│
└── QStatusBar (Bottom)
    ├─ Connection status
    ├─ Last update time
    └─ Quick stats
```

## Data Flow Diagram

```
USER INPUT (Control Panel)
    │
    ├── Symbols: AAPL, MSFT, GOOGL
    ├── Mode: Incremental or Full History
    ├── Years: 1-30
    ├── Chunk Size: 1-30 days
    └── Max Workers: 1-20
    │
    ▼
┌──────────────────────────────────────────────┐
│   PipelineController.start()                 │
│   ├─ Creates ThreadPoolExecutor              │
│   ├─ Initializes MetricsCalculator           │
│   └─ Submits symbol tasks to workers         │
└──────────────────────────────────────────────┘
    │
    ├── Submit: Worker 1 → Process AAPL
    ├── Submit: Worker 2 → Process MSFT
    ├── Submit: Worker 3 → Process GOOGL
    └── ... (up to N workers - independent)
    │
    ▼
┌──────────────────────────────────────────────┐
│   Worker 1: Parallel Independent Pipeline    │
│   (Each worker has own instances)            │
│                                              │
│   ┌────────────────────────────────────┐    │
│   │ 1. Initialize per-symbol           │    │
│   │    • Create independent            │    │
│   │      AdaptiveRateLimiter          │    │
│   │    • Emit: symbol_started          │    │
│   │    • Set status: fetching          │    │
│   └────────────────────────────────────┘    │
│                                              │
│   ┌────────────────────────────────────┐    │
│   │ 2. Fetch minute data               │    │
│   │    • Rate limiter wait             │    │
│   │    • EODHDDataFetcher call         │    │
│   │    • Record API call               │    │
│   │    • Emit progress at 25%          │    │
│   │    • Returns DataFrame             │    │
│   └────────────────────────────────────┘    │
│                                              │
│   ┌────────────────────────────────────┐    │
│   │ 3. Engineer features               │    │
│   │    • FeatureEngineer pipeline      │    │
│   │    • Calculate 200+ features       │    │
│   │    • Emit progress at 60%          │    │
│   │    • Returns feature dict          │    │
│   └────────────────────────────────────┘    │
│                                              │
│   ┌────────────────────────────────────┐    │
│   │ 4. Store profile                   │    │
│   │    • Create company profile        │    │
│   │    • MongoDBStorage.save()         │    │
│   │    • Emit progress at 90%          │    │
│   │    • Returns success flag          │    │
│   └────────────────────────────────────┘    │
│                                              │
│   Emit: symbol_completed or symbol_failed   │
└──────────────────────────────────────────────┘
    │
    ├─ Qt Signal: symbol_progress
    │   └─ Data: symbol, status, progress%,
    │           micro_stage, api_calls, duration
    │
    ├─ Qt Signal: api_stats_updated
    │   └─ Data: minute_used, daily_used, etc.
    │
    └─ Qt Signal: metrics_updated
        └─ Data: ETA, throughput, totals
    │
    ├─ Qt Signal: log_message
    │   └─ Data: level, message
    │
    └─ Qt Signal: symbol_completed
        └─ Data: symbol, profile_dict
    │
    ▼
┌──────────────────────────────────────────────┐
│   Metrics Calculator (Background Thread)     │
│                                              │
│   Every 10 seconds:                          │
│   ├─ Calculate overall progress              │
│   ├─ Estimate remaining time (ETA)          │
│   ├─ Update success/failed/skipped counts   │
│   ├─ Sum all API calls from workers         │
│   ├─ Calculate throughput                    │
│   └─ Emit metrics_updated signal            │
└──────────────────────────────────────────────┘
    │
    ▼
┌──────────────────────────────────────────────┐
│   Monitor Panel (UI Thread - Qt Signal Slot) │
│                                              │
│   Receives and updates:                      │
│   ├─ symbol_progress → Table row update      │
│   ├─ api_stats_updated → API gauges         │
│   ├─ metrics_updated → ETA & stats bar      │
│   ├─ log_message → Log viewer entries       │
│   └─ symbol_completed → Mark green ✅       │
│                                              │
│   Real-time UI Updates:                      │
│   ├─ Progress bars (0-100%)                 │
│   ├─ Status colors (queued→completed)      │
│   ├─ API usage gauges                       │
│   ├─ Metrics display (totals, ETA)         │
│   ├─ Log entries (color-coded)              │
│   └─ Queue table (auto-scroll)              │
└──────────────────────────────────────────────┘
```

## Threading Model

```
┌─────────────────────────────────────────────────────────┐
│                  MAIN THREAD (UI)                       │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐    │
│  │ Control     │  │ Monitor     │  │ Profile     │    │
│  │ Panel       │  │ Panel       │  │ Browser     │    │
│  └──────┬──────┘  └──────▲──────┘  └─────────────┘    │
│         │                 │                             │
│         │ Start           │ Qt Signals                  │
│         │                 │ (Thread-Safe)               │
└─────────┼─────────────────┼─────────────────────────────┘
          │                 │
          ▼                 │
┌──────────────────────────────────────────────────┐
│         PIPELINE THREAD (QThread)                │
│                                                  │
│  PipelineController                             │
│  ├─ Manages workers                             │
│  ├─ Emits signals ────────────────┘             │
│  ├─ Controls ThreadPoolExecutor                 │
│  └─ Metrics calculation thread                  │
│      │                                           │
│      └─┬─┬─┬─┬─┬─┬─┬─┬─┬─ (N threads)          │
│        │ │ │ │ │ │ │ │ │ │                     │
└────────┼─┼─┼─┼─┼─┼─┼─┼─┼─┼─────────────────────┘
         │ │ │ │ │ │ │ │ │ │
         ▼ ▼ ▼ ▼ ▼ ▼ ▼ ▼ ▼ ▼
┌──────────────────────────────────────────────────┐
│        WORKER POOL (N Threads)                  │
│                                                 │
│  Worker 1  Worker 2  Worker 3  ...  Worker N   │
│     ↓          ↓          ↓            ↓        │
│   AAPL      MSFT      GOOGL        NVDA         │
│     ║          ║          ║            ║        │
│  Each worker has independent:                  │
│  ├─ AdaptiveRateLimiter (per-worker)            │
│  ├─ EODHDDataFetcher instance                  │
│  ├─ FeatureEngineer instance                   │
│  └─ Pipeline status tracking                   │
│                                                 │
│  Per-symbol control events:                    │
│  ├─ pause_event (symbol-level pause)           │
│  ├─ cancel_event (symbol-level cancel)         │
│  └─ status tracking                            │
└──────────────────────────────────────────────────┘

Global Control Events:
├─ _pause_event (pauses all workers)
├─ _cancel_event (cancels all workers)
└─ symbol_control dict (per-symbol tracking)
```

## Signal Flow

```
PipelineController              MonitorPanel
(Background Thread)             (UI Thread)
─────────────────────────────────────────────

emit(symbol_started)        ────►   Log: "Starting AAPL"
                                    Set row status: fetching

emit(symbol_progress)       ────►   Update table row
                                    Progress: 25%
                                    Micro-stage: Fetching
                                    Duration: 5s

emit(api_stats_updated)     ────►   Update API gauges
                                    Minute: 45/80
                                    Daily: 756/95K

emit(log_message)           ────►   Append to log viewer
                                    [INFO] Fetched 390 rows
                                    Color-coded by level

emit(symbol_completed)      ────►   Mark row green ✅
                                    Update stats counters
                                    Log: "AAPL completed"

emit(metrics_updated)       ────►   Update metrics bar
                                    ETA: 4m 32s
                                    Throughput: 2.5 sym/min

emit(pipeline_paused)       ────►   Update UI buttons
                                    Show "Resume" button

emit(pipeline_stopped)      ────►   Reset UI state
                                    Clear queue
                                    Show "Start" button
```

## Rate Limiter Coordination

```
PipelineController
├─ Distributed Rate Limits:
│  ├─ Total Minute Limit: 80 calls/min
│  ├─ Total Daily Limit: 95,000 calls/day
│  └─ Per-Worker Allocation (with safety margin):
│     ├─ Per-Worker Minute: 80 / 10 * 0.9 = 7 calls/min
│     └─ Per-Worker Daily: 95,000 / 10 * 0.9 = 8,550 calls/day
│
└─ Independent Workers:

┌─────────────────────────────────────────────────┐
│  Worker 1 - AdaptiveRateLimiter (Independent)   │
│  ├─ Minute Window: [timestamps...]              │
│  ├─ Daily Calls: 156                            │
│  ├─ Lock: threading.Lock()                      │
│  └─ Limit: 7/min, 8550/day                      │
└─────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────┐
│  Worker 2 - AdaptiveRateLimiter (Independent)   │
│  ├─ Minute Window: [timestamps...]              │
│  ├─ Daily Calls: 234                            │
│  ├─ Lock: threading.Lock()                      │
│  └─ Limit: 7/min, 8550/day                      │
└─────────────────────────────────────────────────┘

...

Flow:
1. Worker 1: rate_limiter.wait_if_needed()
   → Acquires worker's own lock
   → Checks: 4 calls this minute (OK)
   → Releases lock
   → Makes API call
   → rate_limiter.record_call()

2. Worker 2: rate_limiter.wait_if_needed()
   → Acquires worker's own lock
   → Checks: 6 calls this minute (OK)
   → Releases lock
   → Makes API call

3. Worker 3: rate_limiter.wait_if_needed()
   → Acquires worker's own lock
   → Checks: 7 calls (LIMIT REACHED!)
   → Sleeps remaining time in minute
   → Releases lock after wait
   → Continues processing

Benefits:
✓ True parallelism (no single bottleneck)
✓ Global limits respected (80/min total, 95K/day total)
✓ Per-worker independence
✓ Thread-safe operation
```

## Database Caching

```
┌─────────────────────────────────────────┐
│     DatabaseController                  │
│                                         │
│  ┌───────────────────────────────┐     │
│  │ Cache:                        │     │
│  │  {                            │     │
│  │    'AAPL': {...profile...}   │     │
│  │    'MSFT': {...profile...}   │     │
│  │    ...                        │     │
│  │  }                            │     │
│  │ TTL: 60 seconds               │     │
│  └───────────────────────────────┘     │
│                                         │
│  get_profile('AAPL')                   │
│    ├─ Cache hit? → Return cached       │
│    └─ Cache miss? → Query MongoDB      │
│                                         │
│  load_all_profiles()                   │
│    └─ Fetch all → Update cache         │
│                                         │
│  invalidate_cache()                    │
│    └─ Clear cache (on updates)         │
└─────────────────────────────────────────┘
              │
              ▼
      ┌─────────────┐
      │  MongoDB    │
      │             │
      │  Profiles:  │
      │  - AAPL     │
      │  - MSFT     │
      │  - GOOGL    │
      │  ...        │
      └─────────────┘
```

## File Dependencies

```
dashboard/main.py (Entry point)
    │
    ├── imports: PyQt6 framework
    ├── imports: ui/main_window.py
    ├── imports: utils/theme.py
    └── imports: models/cache_store.py

ui/main_window.py (Main window container)
    │
    ├── imports: panels/control_panel.py
    ├── imports: panels/monitor_panel.py
    ├── imports: panels/profile_browser.py
    ├── imports: panels/settings_panel.py
    ├── imports: controllers/pipeline_controller.py
    └── imports: controllers/database_controller.py

controllers/pipeline_controller.py (Worker manager)
    │
    ├── imports: PyQt6.QtCore (QThread)
    ├── imports: concurrent.futures (ThreadPoolExecutor)
    ├── imports: pipeline.py (core pipeline)
    ├── imports: utils/rate_limiter.py
    ├── imports: utils/qt_signals.py
    └── imports: services/metrics_calculator.py

panels/monitor_panel.py (Live monitoring)
    │
    ├── imports: widgets/symbol_queue_table.py
    ├── imports: widgets/log_viewer.py
    ├── imports: widgets/api_usage_widget.py
    └── imports: utils/qt_signals.py

panels/control_panel.py (User input)
    │
    ├── imports: PyQt6 UI components
    └── imports: config.py (settings)

services/metrics_calculator.py (Statistics)
    │
    └── imports: utils/rate_limiter.py

models/cache_store.py (Local cache)
    │
    └── imports: sqlite3, PyQt6.QtSql
```

## Performance Characteristics

```
Input: 100 symbols × 2 years each

┌─────────────────────────────────────────┐
│  Serial Processing (1 worker)           │
│  100 × 2 min = 200 minutes (3.3 hours)  │
└─────────────────────────────────────────┘

┌─────────────────────────────────────────┐
│  Parallel Processing (10 workers)       │
│  100 ÷ 10 × 2 min = 20 minutes          │
│  Speedup: 10× faster! ⚡                │
└─────────────────────────────────────────┘

Bottleneck: API Rate Limit (80 calls/min)
    ├─ Each worker gets 7 calls/min (80/10 * 0.9)
    ├─ Total possible: 70 calls/min (safety margin)
    ├─ Optimal chunk: 30 days (per API design)
    └─ Independent limiters prevent contention
```

---

**Visual Summary**: The dashboard is a multi-threaded PyQt6 application that coordinates parallel data processing while maintaining a responsive UI through Qt's signal/slot mechanism. Each worker has independent rate limiting to avoid contention while respecting global API quotas.

