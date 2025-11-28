# Quick Start - Dashboard Enhancements Integration

## 🚀 Get Started in 5 Minutes

### Step 1: Review the Project (2 min)
```bash
# View the status
cat DASHBOARD_ENHANCEMENT_STATUS.md

# Review implementation guide
cat docs/IMPLEMENTATION_GUIDE.md
```

### Step 2: Understand New Components (1 min)
**New Services:**
- `CacheStore` - Persistent data storage (SQLite)
- `LogEmailAlerter` - Email notifications
- `MetricsCalculator` - Real-time ETA and metrics

**New Dialogs:**
- `CompanySelectorDialog` - Browse and select companies
- `ReprocessDialog` - Configure reprocessing

**Enhanced Widgets:**
- `LogViewer` - Font control, filtering
- `SymbolQueueTable` - Micro-stage progress column
- `APIUsageWidget` - Persistent storage

### Step 3: Check File Structure (1 min)
```
dashboard/
├── models/
│   ├── __init__.py
│   └── cache_store.py              [NEW - 550+ lines]
├── services/
│   ├── __init__.py
│   ├── log_emailer.py              [NEW - 400+ lines]
│   └── metrics_calculator.py       [NEW - 300+ lines]
└── dialogs/
    ├── __init__.py
    ├── company_selector_dialog.py  [NEW - 400+ lines]
    └── reprocess_dialog.py         [NEW - 250+ lines]
```

### Step 4: Validation (30 sec)
```bash
# Test syntax of all new modules
python -m py_compile dashboard/models/cache_store.py
python -m py_compile dashboard/services/log_emailer.py
python -m py_compile dashboard/services/metrics_calculator.py
python -m py_compile dashboard/dialogs/company_selector_dialog.py
python -m py_compile dashboard/dialogs/reprocess_dialog.py
```

### Step 5: Review API (30 sec)
- See: `docs/API_REFERENCE_DASHBOARD.md`
- All methods documented with examples
- Copy-paste ready code snippets

---

## 📚 Documentation Map

| Document | Purpose | Read Time |
|----------|---------|-----------|
| **IMPLEMENTATION_GUIDE.md** | How to integrate | 10 min |
| **API_REFERENCE_DASHBOARD.md** | How to use each module | 15 min |
| **DASHBOARD_ENHANCEMENTS.md** | Technical details | 15 min |
| **This File** | Quick start | 5 min |

---

## 🔧 Quick Integration Example

### Initialize Cache in main.py

```python
# dashboard/ui/main_window.py

from dashboard.models import CacheStore
from dashboard.ui.widgets import APIUsageWidget

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        
        # 1. Initialize cache
        self.cache_store = CacheStore()
        
        # 2. Pass to widgets
        self.api_widget = APIUsageWidget(cache_store=self.cache_store)
        
        # 3. That's it!
```

### Connect Metrics

```python
# dashboard/ui/panels/monitor_panel.py

from dashboard.services import MetricsCalculator

class MonitorPanel(QWidget):
    def __init__(self):
        super().__init__()
        self.metrics = MetricsCalculator()
    
    def on_pipeline_started(self, symbols):
        self.metrics.initialize(len(symbols))
    
    def on_symbol_completed(self, symbol):
        self.metrics.mark_symbol_completed(symbol)
        
        # Update ETA display
        eta = self.metrics.calculate_eta_string(processing_count=3)
        self.eta_label.setText(f"ETA: {eta}")
```

### Use Company Selector

```python
# dashboard/ui/panels/control_panel.py

from dashboard.dialogs import CompanySelectorDialog

def _on_browse_companies(self):
    dialog = CompanySelectorDialog(self.cache_store, self)
    dialog.companies_selected.connect(self._on_companies_selected)
    dialog.exec()

def _on_companies_selected(self, symbols):
    self.symbol_input.setText(', '.join(symbols))
```

---

## 🎯 Key Files to Modify

### 1. dashboard/main.py
```python
# Add:
from dashboard.models import CacheStore
cache = CacheStore()
```

### 2. dashboard/ui/main_window.py
```python
# Update APIUsageWidget init:
self.api_usage = APIUsageWidget(cache_store=self.cache_store)

# Update control panel:
self.control_panel.cache_store = self.cache_store
```

### 3. dashboard/controllers/pipeline_controller.py
```python
# Add micro-stage updates:
self.signals.progress_updated.emit(
    symbol, status, progress,
    micro_stage=f"Batch 3/10: 75%"  # NEW
)
```

---

## ⚡ Common Tasks

### Add Email Alerting
```python
from dashboard.services import LogEmailAlerter

alerter = LogEmailAlerter(
    smtp_server='smtp.gmail.com',
    smtp_port=587,
    sender_email='your_email@example.com',
    sender_password='your_password',
    recipient_emails=['admin@example.com']
)

# Test connection
if alerter.test_connection():
    print("Email ready!")
```

### Track API Usage
```python
from dashboard.models import CacheStore

cache = CacheStore()

# Get today's API calls
calls = cache.get_daily_api_calls()

# Update
cache.update_daily_api_calls(45230)

# Persist (automatic)
```

### Search Companies
```python
# Get all companies
all_companies = cache.get_company_list()

# Search
results = cache.search_companies('apple')
# Returns: [{'symbol': 'AAPL', ...}, ...]
```

### Calculate ETA
```python
from dashboard.services import MetricsCalculator

calc = MetricsCalculator()
calc.initialize(total_symbols=10)

# Mark progress
calc.mark_symbol_started('AAPL')
# ... process ...
calc.mark_symbol_completed('AAPL')

# Get ETA
eta = calc.calculate_eta_string(processing_count=3)
# Returns: "7m 30s"
```

---

## 🧪 Quick Test

### Test CacheStore
```python
from dashboard.models import CacheStore

cache = CacheStore(':memory:')  # Use in-memory for testing

# Test API tracking
cache.update_daily_api_calls(100)
assert cache.get_daily_api_calls() == 100
print("✅ CacheStore works!")

cache.close()
```

### Test Metrics
```python
from dashboard.services import MetricsCalculator
import time

calc = MetricsCalculator()
calc.initialize(5)

# Simulate processing
for i in range(5):
    calc.mark_symbol_started(f'SYM{i}', time.time())
    time.sleep(2)  # Simulate work
    calc.mark_symbol_completed(f'SYM{i}')

# Check results
stats = calc.get_summary_stats(processing_count=0)
print(f"Progress: {stats['progress_percent']}%")
print(f"Throughput: {stats['throughput_symbols_per_minute']:.1f} sym/min")
print("✅ MetricsCalculator works!")
```

---

## 📋 Integration Checklist

Quick checklist to track integration progress:

```
PHASE 1: BASIC SETUP
  ☐ Create CacheStore in main.py
  ☐ Initialize cache on app startup
  ☐ Pass to APIUsageWidget
  ☐ Test app starts without errors

PHASE 2: WIDGETS
  ☐ Test LogViewer font control
  ☐ Test SymbolQueueTable micro-stage
  ☐ Test APIUsageWidget persistence
  ☐ Verify all widgets display correctly

PHASE 3: SERVICES
  ☐ Initialize MetricsCalculator
  ☐ Connect to pipeline controller
  ☐ Test ETA calculations
  ☐ Verify metrics display updates

PHASE 4: DIALOGS
  ☐ Test CompanySelectorDialog
  ☐ Test ReprocessDialog
  ☐ Verify signals emit correctly
  ☐ Test company selection flow

PHASE 5: FEATURES
  ☐ Implement company fetching
  ☐ Test email alerts
  ☐ Implement reprocess logic
  ☐ Full end-to-end test
```

---

## 🐛 Troubleshooting

### Import Error
```python
# Error: ModuleNotFoundError: No module named 'dashboard.models'
# Solution: Make sure __init__.py exists in each directory
```

### Database Lock
```python
# Error: Database is locked
# Solution: Close cache connection properly
cache.close()
# Or use context manager:
with CacheStore() as cache:
    # Use cache
    pass  # Auto-closes
```

### Email Not Sending
```python
# Error: SMTP connection failed
# Solution: Check credentials and firewall
alerter.test_connection()  # Test SMTP first
```

### ETA Returns None
```python
# Error: ETA calculation returns None
# Solution: Need at least one completed symbol for calculation
# Mark symbol_completed() before calling calculate_eta_seconds()
```

---

## 📞 Need Help?

1. **For Integration Questions**
   - See: `docs/IMPLEMENTATION_GUIDE.md`

2. **For API Questions**
   - See: `docs/API_REFERENCE_DASHBOARD.md`

3. **For Technical Details**
   - See: `docs/DASHBOARD_ENHANCEMENTS.md`

4. **For File Details**
   - See: `docs/FILE_MANIFEST.md`

---

## ✅ Success Criteria

You'll know integration is successful when:

- [ ] App starts without errors
- [ ] CacheStore initializes automatically
- [ ] LogViewer displays with font size control
- [ ] SymbolQueueTable shows micro-stage column
- [ ] APIUsageWidget shows API stats
- [ ] Company selector dialog opens
- [ ] Metrics calculate correctly
- [ ] ETA updates every 10 seconds
- [ ] Data persists across app restarts
- [ ] All signals emit correctly

---

## 🎉 Done!

Once all checks pass, integration is complete. 
Proceed with feature testing and optimization.

---

**Quick Start Complete - Ready for Integration!**

Start with: `docs/IMPLEMENTATION_GUIDE.md`

