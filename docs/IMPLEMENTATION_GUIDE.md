# Dashboard Enhancements - Implementation Guide

## Phase-by-Phase Integration

### Phase 1: Foundation (Data Persistence) ✅ COMPLETE
- [x] CacheStore module created with SQLite backend
- [x] API usage stats persistence implemented
- [x] Company list caching ready
- [x] Session settings storage ready

**Action Items:**
1. Initialize CacheStore in main.py
2. Pass cache_store to APIUsageWidget
3. Test persistence on app restart

### Phase 2: Log System Overhaul ✅ COMPLETE
- [x] LogViewer font size increased to 11pt (configurable)
- [x] Resizable container added
- [x] Category-based filtering implemented
- [x] LogEmailAlerter service created
- [x] Email formatting with dashboard snapshots ready

**Action Items:**
1. Add email settings UI panel (SMTP config)
2. Integrate LogEmailAlerter with dashboard
3. Add screenshot capture on critical errors
4. Test email delivery

### Phase 3: Symbol & Company Selection ✅ COMPLETE
- [x] CompanySelectorDialog created with 4 tabs
- [x] Top N companies browser ready
- [x] Search interface implemented
- [x] File upload support (CSV/TXT)
- [x] Custom input parsing ready
- [x] Control panel buttons added
- [x] fetch_exchange_symbols() method added to data_fetcher.py

**Action Items:**
1. Implement company list fetching from EODHD API
2. Cache refresh mechanism
3. Test company selector with real data
4. Add company management to Settings panel

### Phase 4: Queue & Metrics ✅ COMPLETE
- [x] Micro-stage column added to SymbolQueueTable
- [x] MetricsCalculator service created
- [x] APIStatsTracker service created
- [x] Real-time ETA calculation ready
- [x] Throughput metrics ready

**Action Items:**
1. Connect MetricsCalculator to PipelineController
2. Update micro-stage from worker processes
3. Emit progress signals from pipeline workers
4. Display ETA in real-time in monitor panel

### Phase 5: Profile Management ✅ PARTIAL
- [x] ReprocessDialog created
- [ ] Full rebuild implementation
- [ ] Incremental update strategy discussion needed
- [ ] Backup mechanism needed

**Action Items:**
1. Implement full_rebuild logic in pipeline.py
2. Design incremental update strategy
3. Add profile backup before reprocessing
4. Test reprocess with sample profiles

---

## Integration Checklist

### Main Application Changes

```python
# dashboard/main.py or dashboard/ui/main_window.py

# 1. Import new modules
from dashboard.models import CacheStore
from dashboard.services import LogEmailAlerter, MetricsCalculator, APIStatsTracker
from dashboard.dialogs import CompanySelectorDialog, ReprocessDialog

# 2. Initialize in MainWindow.__init__()
self.cache_store = CacheStore()

# 3. Pass to widgets
self.api_usage = APIUsageWidget(cache_store=self.cache_store)

# 4. Initialize services
self.metrics_calc = MetricsCalculator()
self.api_stats = APIStatsTracker()

# 5. Connect signals
pipeline_controller.metrics_updated.connect(self.on_metrics_updated)
```

### Settings Panel Updates

Add email configuration fields:
```python
# dashboard/ui/panels/settings_panel.py

class SettingsPanel(QWidget):
    # Add to __init__
    
    # Email Configuration Group
    email_group = QGroupBox("Email Alerts")
    email_layout = QVBoxLayout()
    
    # SMTP Server
    self.smtp_server_input = QLineEdit("smtp.gmail.com")
    # SMTP Port
    self.smtp_port_spin = QSpinBox(value=587)
    # Sender Email
    self.sender_email_input = QLineEdit()
    # Sender Password (use keyring for security)
    self.sender_password_input = QLineEdit(echoMode=QLineEdit.EchoMode.Password)
    # Recipient Email(s)
    self.recipient_emails_input = QLineEdit()
    
    # Test button
    self.test_email_btn = QPushButton("Test Connection")
```

### Pipeline Controller Integration

```python
# dashboard/controllers/pipeline_controller.py

def process_symbol_worker(self, symbol, config):
    """Worker with micro-stage progress updates"""
    
    # ... existing code ...
    
    # Emit micro-stage updates
    for batch_num, batch in enumerate(batches):
        progress = int((batch_num / len(batches)) * 100)
        micro_stage = f"Batch {batch_num + 1}/{len(batches)}: {progress}%"
        
        self.signals.progress_updated.emit(
            symbol,
            'Fetching',
            progress,
            micro_stage=micro_stage
        )
        
        # Fetch batch
        fetch_data(batch)
    
    # Engineering features with progress
    total_features = len(feature_list)
    for feat_idx, feature in enumerate(feature_list):
        progress = int((feat_idx / total_features) * 100)
        micro_stage = f"Feature {feat_idx + 1}/{total_features}: {progress}%"
        
        self.signals.progress_updated.emit(
            symbol,
            'Engineering',
            progress,
            micro_stage=micro_stage
        )
        
        # Engineer feature
        calculate_feature(feature)
```

### Monitor Panel Real-time Updates

```python
# dashboard/ui/panels/monitor_panel.py

class MonitorPanel(QWidget):
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # Initialize metrics calculator
        self.metrics_calc = MetricsCalculator()
        
        # Timer for 10-second updates
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self.update_metrics_display)
        self.update_timer.start(10000)  # 10 seconds
    
    def on_pipeline_started(self, symbol_count):
        """Called when pipeline starts"""
        self.metrics_calc.initialize(symbol_count)
    
    def update_symbol_progress(self, symbol, status, progress):
        """Update symbol progress"""
        self.metrics_calc.mark_symbol_started(symbol)
        self.queue_table.update_symbol(symbol, status, progress)
    
    def on_symbol_completed(self, symbol, profile):
        """Called when symbol finishes"""
        self.metrics_calc.mark_symbol_completed(symbol)
        
        # Get updated stats
        stats = self.metrics_calc.get_summary_stats(
            processing_count=self.get_current_processing_count()
        )
        
        self.eta_label.setText(f"⏱ ETA: {stats['eta_string']}")
    
    @pyqtSlot()
    def update_metrics_display(self):
        """Update metrics every 10 seconds"""
        if not self.metrics_calc.total_symbols:
            return
        
        stats = self.metrics_calc.get_summary_stats(
            processing_count=len(self.current_processing)
        )
        
        # Update ETA
        self.eta_label.setText(f"⏱ ETA: {stats['eta_string']}")
        
        # Update throughput
        self.throughput_label.setText(
            f"Throughput: {stats['throughput_symbols_per_minute']:.1f} sym/min"
        )
```

---

## Testing Strategy

### Unit Tests

```python
# tests/test_dashboard_enhancements.py

import pytest
from dashboard.models import CacheStore
from dashboard.services import MetricsCalculator, APIStatsTracker
from dashboard.dialogs import CompanySelectorDialog, ReprocessDialog

class TestCacheStore:
    def test_api_usage_persistence(self):
        cache = CacheStore(':memory:')  # In-memory for testing
        cache.update_daily_api_calls(100)
        assert cache.get_daily_api_calls() == 100
    
    def test_company_list_caching(self):
        companies = [
            {'Code': 'AAPL', 'Name': 'Apple'},
            {'Code': 'MSFT', 'Name': 'Microsoft'}
        ]
        cache.save_company_list(companies)
        assert len(cache.get_company_list()) == 2
    
    def test_daily_reset(self):
        cache.update_daily_api_calls(100, date=datetime(2025, 1, 1))
        # Simulate next day
        cache.reset_daily_api_calls_if_new_day()
        assert cache.get_daily_api_calls() == 0

class TestMetricsCalculator:
    def test_eta_calculation(self):
        calc = MetricsCalculator()
        calc.initialize(10)
        
        # Simulate 5 completed in 30 seconds
        for i in range(5):
            calc.mark_symbol_started(f'SYM{i}', 0)
            calc.mark_symbol_completed(f'SYM{i}')
        
        eta = calc.calculate_eta_seconds(processing_count=2)
        assert eta is not None
        assert eta > 0
```

### Integration Tests

1. **Full Dashboard Startup**
   - Launch dashboard
   - Verify CacheStore initializes
   - Check API usage loads from cache
   - Confirm UI responsive

2. **Company Selection Workflow**
   - Click "Browse Companies"
   - Search for a company
   - Select and submit
   - Verify symbols populate control panel

3. **Processing with Metrics**
   - Start pipeline with 3 symbols
   - Monitor micro-stage updates
   - Verify ETA updates every 10 seconds
   - Check API usage stats update

4. **Email Alerting**
   - Configure email in settings
   - Simulate critical error
   - Verify email received with screenshot

---

## Deployment Checklist

- [ ] All new modules syntax checked
- [ ] CacheStore database initializes on first run
- [ ] Email configuration stored securely (use keyring)
- [ ] Company cache refreshes appropriately
- [ ] Micro-stage messages clear and informative
- [ ] ETA displays in human-readable format
- [ ] No performance degradation with new features
- [ ] Logging includes all new components
- [ ] Error handling comprehensive
- [ ] Documentation updated

---

## Performance Considerations

### Hardware Utilization (Ryzen 5 7600)

**CPU Cores:** 6 cores / 12 threads
**Recommended Settings:**
```python
MAX_WORKERS = 6  # Use all cores
HISTORY_CHUNK_DAYS = 30  # Minimize API calls
```

**Projected Performance:**
- 3 concurrent symbol processing
- ~2-3 minutes per symbol (including feature engineering)
- API calls: ~250 per symbol (with 30-day chunks)
- Total processing time for 10 symbols: ~7-10 minutes

### Memory Usage

- Dashboard base: ~150MB
- Per active worker: ~50-100MB
- Cache database (100K companies): ~50MB
- Total with 6 workers: ~500MB (within 32GB available)

### API Rate Limiting

**Per-worker allocation:**
- Calls/minute: 80 ÷ 6 workers ≈ 13 calls/minute/worker (with 0.9 safety margin = ~7/min)
- Calls/day: 95,000 ÷ 6 workers ≈ 15,833 calls/day/worker (with 0.9 safety margin ≈ 8,550/day)

---

## Support & Troubleshooting

### Email Not Sending

1. Check SMTP credentials in settings
2. Verify SMTP server allows app connection
3. Check firewall rules
4. Review email logs in terminal

### Company List Stale

1. Update cache: Settings > Company Management > Fetch
2. Clear cache: Settings > Developer > Clear Cache
3. Restart dashboard

### ETA Not Updating

1. Check MetricsCalculator initialized
2. Verify 10-second timer running
3. Check symbol completion signals connected
4. Review console logs for errors

### Micro-stage Not Showing

1. Verify worker emitting progress signals
2. Check queue table column sizing
3. Ensure pipeline_controller connected correctly
4. Review symbol_queue_table.py for signal handling

---

**Implementation ready. Begin Phase 1 integration.**

