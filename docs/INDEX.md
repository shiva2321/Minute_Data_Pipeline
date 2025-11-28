# 📁 Project File Index

## Quick Navigation

### 🚀 Getting Started
1. **[QUICK_REF.md](QUICK_REF.md)** - Quick reference card (START HERE!)
2. **[DASHBOARD_GUIDE.md](DASHBOARD_GUIDE.md)** - Complete walkthrough
3. **[README_DASHBOARD.md](README_DASHBOARD.md)** - Technical documentation
4. **[DASHBOARD_SUMMARY.md](DASHBOARD_SUMMARY.md)** - What was built

### 🎯 Launch Files
- **[run_dashboard.bat](run_dashboard.bat)** - Windows launcher ⭐
- **[dashboard/main.py](dashboard/main.py)** - Direct Python launcher
- **[test_dashboard.py](test_dashboard.py)** - Test components

### 📊 Data Files
- **[symbols_sample.txt](symbols_sample.txt)** - Example symbols
- **[.env](.env)** - Configuration (API keys, MongoDB)
- **[requirements.txt](requirements.txt)** - Python dependencies

---

## 📂 Dashboard Structure

### Entry Point
```
dashboard/
└── main.py                 # Start here (application launcher)
```

### Controllers (Business Logic)
```
dashboard/controllers/
├── pipeline_controller.py  # Parallel processing engine ⚙️
├── queue_manager.py        # Thread-safe symbol queue
└── database_controller.py  # MongoDB operations + caching
```

**Key Features:**
- 10-worker ThreadPoolExecutor
- Shared rate limiter (thread-safe)
- Real-time Qt signal emissions

### UI Components

#### Main Window
```
dashboard/ui/
└── main_window.py         # Main application window 🪟
```
Coordinates all panels and controllers

#### Panels (Main Screens)
```
dashboard/ui/panels/
├── control_panel.py       # Symbol input & controls 🎮
├── monitor_panel.py       # Live monitoring dashboard 📊
├── profile_browser.py     # Database viewer 🗂️
└── settings_panel.py      # Configuration ⚙️
```

**What Each Does:**
- **Control**: Enter symbols, configure processing
- **Monitor**: Watch progress, logs, API usage
- **Browser**: Search/view/edit profiles
- **Settings**: API keys, MongoDB, defaults

#### Widgets (Reusable Components)
```
dashboard/ui/widgets/
├── symbol_queue_table.py  # Processing queue table 📋
├── log_viewer.py          # Color-coded logs 📝
├── profile_editor.py      # JSON editor ✏️
└── api_usage_widget.py    # Rate limit gauges 📊
```

### Utilities
```
dashboard/utils/
├── qt_signals.py          # Custom Qt signals 📡
├── worker_thread.py       # Background processing 🔄
└── theme.py               # Dark theme styles 🎨
```

---

## 📚 Existing Pipeline (Integrated)

### Core Modules
```
config.py                  # Pydantic settings (env vars)
data_fetcher.py           # EODHD API client
feature_engineering.py    # 200+ technical features
mongodb_storage.py        # Database operations
pipeline.py               # Main orchestrator
```

### Utilities
```
utils/
├── rate_limiter.py       # API throttling (80/min, 95K/day)
└── backfill_checkpoint.py # Progress tracking
```

### Scripts
```
scripts/
├── backfill_historical.py
├── benchmark_features.py
├── test_eodhd_api.py
└── verify_backfill.py
```

### Tests
```
tests/
├── test_rate_limiter.py
test_feature_engineering.py
test_setup.py
```

---

## 📖 Documentation Hierarchy

### Level 1: Quick Start
- **QUICK_REF.md** - 1-page cheat sheet
- **symbols_sample.txt** - Example data

### Level 2: User Guide  
- **DASHBOARD_GUIDE.md** - Step-by-step walkthrough
  - Part 1: Setup
  - Part 2: Configuration
  - Part 3: Processing
  - Part 4: Monitoring
  - Part 5: Results
  - Parts 6-10: Advanced

### Level 3: Technical Docs
- **README_DASHBOARD.md** - Architecture, API, troubleshooting
- **DASHBOARD_SUMMARY.md** - What was built, how it works

### Level 4: Original Docs
- **README.md** - Original pipeline README
- **API_REFERENCE.md** - API details
- **FEATURE_GUIDE.md** - Feature explanations
- **PROJECT_SUMMARY.md** - Original project summary

---

## 🎯 Common Tasks → Files

### Task: Launch Dashboard
**Files:**
1. `run_dashboard.bat` (Windows)
2. `dashboard/main.py` (Direct)

### Task: Process Symbols
**Flow:**
1. User input → `ui/panels/control_panel.py`
2. Start pipeline → `controllers/pipeline_controller.py`
3. Fetch data → `data_fetcher.py`
4. Calculate features → `feature_engineering.py`
5. Store → `mongodb_storage.py`
6. Display → `ui/panels/monitor_panel.py`

### Task: View Profile
**Flow:**
1. Browse → `ui/panels/profile_browser.py`
2. Load → `controllers/database_controller.py`
3. Edit → `ui/widgets/profile_editor.py`
4. Save → `mongodb_storage.py`

### Task: Configure Settings
**Files:**
1. UI → `ui/panels/settings_panel.py`
2. Storage → `~/.pipeline_dashboard_config.json`
3. Env → `.env`
4. Validation → `config.py`

### Task: Debug Issues
**Files:**
1. Test → `test_dashboard.py`
2. Logs → `logs/pipeline_*.log`
3. Console → Run `python dashboard/main.py`
4. Docs → `README_DASHBOARD.md` (Troubleshooting)

---

## 🔧 Development Files

### Python Modules (Dashboard)
```
dashboard/
├── __init__.py
├── main.py                    (305 lines)
├── controllers/
│   ├── __init__.py
│   ├── pipeline_controller.py  (320 lines) ⭐
│   ├── queue_manager.py        (180 lines)
│   └── database_controller.py  (210 lines)
├── ui/
│   ├── __init__.py
│   ├── main_window.py         (290 lines) ⭐
│   ├── panels/
│   │   ├── __init__.py
│   │   ├── control_panel.py    (350 lines)
│   │   ├── monitor_panel.py    (270 lines)
│   │   ├── profile_browser.py  (310 lines)
│   │   └── settings_panel.py   (380 lines)
│   └── widgets/
│       ├── __init__.py
│       ├── symbol_queue_table.py (240 lines)
│       ├── log_viewer.py         (150 lines)
│       ├── profile_editor.py     (330 lines)
│       └── api_usage_widget.py   (120 lines)
└── utils/
    ├── __init__.py
    ├── qt_signals.py          (40 lines)
    ├── worker_thread.py       (30 lines)
    └── theme.py               (240 lines)
```

**Total**: ~3,500 lines of new code!

### Configuration Files
```
.env                       # Environment variables
requirements.txt           # Python dependencies (updated)
~/.pipeline_dashboard_config.json  # User settings (auto-created)
```

### Documentation Files
```
QUICK_REF.md              # Quick reference (1 page)
DASHBOARD_GUIDE.md        # User guide (10 parts)
README_DASHBOARD.md       # Technical docs
DASHBOARD_SUMMARY.md      # Project summary
INDEX.md                  # This file
```

---

## 📊 File Size Summary

### Code
- Dashboard Python: ~3,500 lines
- Existing Pipeline: ~2,000 lines
- **Total**: ~5,500 lines

### Documentation
- Dashboard docs: ~2,000 lines
- Existing docs: ~1,500 lines
- **Total**: ~3,500 lines

### Assets
- Sample files: ~50 lines
- Config files: ~100 lines
- **Total**: ~150 lines

---

## 🎯 Recommended Reading Order

### For Users (Non-Technical)
1. **QUICK_REF.md** (5 min) - Get oriented
2. **DASHBOARD_GUIDE.md** Parts 1-5 (30 min) - Basic usage
3. **symbols_sample.txt** - Copy and test
4. **DASHBOARD_GUIDE.md** Parts 6-10 (1 hour) - Advanced usage

### For Developers
1. **DASHBOARD_SUMMARY.md** (15 min) - Architecture overview
2. **README_DASHBOARD.md** (30 min) - Technical details
3. **dashboard/main.py** - Entry point
4. **dashboard/ui/main_window.py** - Main coordination
5. **dashboard/controllers/pipeline_controller.py** - Core engine

### For Troubleshooting
1. **QUICK_REF.md** - Common issues
2. **logs/pipeline_*.log** - Error messages
3. **test_dashboard.py** - Component health
4. **README_DASHBOARD.md** - Troubleshooting section

---

## 🔍 Find By Feature

### Parallel Processing
- **Implementation**: `controllers/pipeline_controller.py`
- **Configuration**: `ui/panels/control_panel.py` (Max Workers)
- **Monitoring**: `ui/panels/monitor_panel.py`
- **Docs**: `DASHBOARD_SUMMARY.md` (Threading Model)

### Rate Limiting
- **Implementation**: `utils/rate_limiter.py`
- **Integration**: `controllers/pipeline_controller.py`
- **Visualization**: `ui/widgets/api_usage_widget.py`
- **Docs**: `README_DASHBOARD.md` (API Quota)

### Profile Management
- **Browser**: `ui/panels/profile_browser.py`
- **Editor**: `ui/widgets/profile_editor.py`
- **Database**: `controllers/database_controller.py`
- **Storage**: `mongodb_storage.py`

### Real-time Updates
- **Signals**: `utils/qt_signals.py`
- **Emission**: `controllers/pipeline_controller.py`
- **Reception**: `ui/panels/monitor_panel.py`
- **Display**: `ui/widgets/` (all)

### Configuration
- **UI**: `ui/panels/settings_panel.py`
- **Backend**: `config.py`
- **Storage**: `~/.pipeline_dashboard_config.json`
- **Env**: `.env`

---

## 🚀 Quick Commands

```bash
# Launch
run_dashboard.bat

# Test
python test_dashboard.py

# Install
pip install -r requirements.txt

# Logs
type logs\pipeline_*.log

# Config
notepad .env
notepad ~/.pipeline_dashboard_config.json
```

---

**Navigation Tip**: Use Ctrl+F to search this index for specific files or features!

