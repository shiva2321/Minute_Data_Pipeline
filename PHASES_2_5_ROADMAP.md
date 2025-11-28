# Integration Roadmap - Phases 2-5

**Status:** Phase 1 Complete ✅ | Next: Phase 2 Metrics Integration

---

## Phase 2: Real-Time Metrics Integration (3-5 hours)

### Objective
Connect MetricsCalculator to pipeline processing and display real-time ETA that updates every 10 seconds.

### Tasks

#### 2.1 Connect MetricsCalculator to PipelineController
```python
# In dashboard/controllers/pipeline_controller.py

def __init__(self, symbols, config, parent=None):
    # ...
    from dashboard.services import MetricsCalculator
    self.metrics_calc = MetricsCalculator()

def run(self):
    # Initialize metrics
    self.metrics_calc.initialize(len(self.symbols))
    
    # Track each symbol
    for symbol in self.symbols:
        self.metrics_calc.mark_symbol_started(symbol)
        # Process symbol...
        self.metrics_calc.mark_symbol_completed(symbol)
```

#### 2.2 Emit Metrics Updates Signal
Add to `dashboard/utils/qt_signals.py`:
```python
metrics_updated = pyqtSignal(dict)  # ETA, throughput, progress
```

#### 2.3 Wire ETA Display in MonitorPanel
```python
# In dashboard/ui/panels/monitor_panel.py

# Add timer for 10-second updates
self.metrics_timer = QTimer()
self.metrics_timer.timeout.connect(self.update_eta_display)
self.metrics_timer.start(10000)  # 10 seconds

def update_eta_display(self):
    if self.metrics_calc:
        eta = self.metrics_calc.calculate_eta_string(processing_count=3)
        self.eta_label.setText(f"⏱ ETA: {eta}")
```

### Deliverables
- [ ] MetricsCalculator integrated with pipeline
- [ ] 10-second update timer working
- [ ] ETA displays in real-time
- [ ] Throughput metrics calculated
- [ ] Tests pass

---

## Phase 3: Company Management (3-5 hours)

### Objective
Enable company selection, searching, and file import with EODHD integration.

### Tasks

#### 3.1 Implement Company Fetching
```python
# In data_fetcher.py - Already added!
# Just needs to be wired to UI

fetcher = EODHDDataFetcher()
symbols = fetcher.fetch_exchange_symbols('US', skip_delisted=True)
```

#### 3.2 Cache Company List
```python
# In ControlPanel when fetching
def on_fetch_exchange_list(self):
    symbols = fetcher.fetch_exchange_symbols()
    self.cache_store.save_company_list(symbols)
    self.show_company_selector()
```

#### 3.3 Integrate CompanySelectorDialog
```python
# Already implemented - just connect button
def _on_browse_companies(self):
    dialog = CompanySelectorDialog(self.cache_store, self)
    dialog.companies_selected.connect(self._on_companies_selected)
    dialog.exec()
```

### Deliverables
- [ ] Company fetching from EODHD working
- [ ] Company list cached
- [ ] CompanySelectorDialog integrated
- [ ] Search functionality working
- [ ] File import working
- [ ] Top 10 quick select working
- [ ] Tests pass

---

## Phase 4: Micro-stage Progress (2-3 hours)

### Objective
Display detailed sub-task progress in queue table (e.g., "Batch 3/10: 75%").

### Tasks

#### 4.1 Emit Micro-stage Signals from Workers
```python
# In pipeline worker thread

# During fetch phase
for batch_num, batch in enumerate(batches):
    progress = int((batch_num / len(batches)) * 100)
    micro_stage = f"Batch {batch_num + 1}/{len(batches)}: {progress}%"
    
    self.signals.progress_updated.emit(
        symbol,
        'Fetching',
        progress,
        micro_stage=micro_stage
    )

# During engineering phase
for feat_idx, feature in enumerate(features):
    progress = int((feat_idx / len(features)) * 100)
    micro_stage = f"Feature {feat_idx + 1}/{len(features)}: {progress}%"
    
    self.signals.progress_updated.emit(
        symbol,
        'Engineering',
        progress,
        micro_stage=micro_stage
    )
```

#### 4.2 Update Queue Table Display
```python
# In dashboard/ui/widgets/symbol_queue_table.py
# Already has micro_stage column - just connect signals

self.queue_table.update_symbol(
    symbol='AAPL',
    status='Fetching',
    progress=45,
    micro_stage='Batch 3/10: 45%'  # This displays!
)
```

### Deliverables
- [ ] Workers emit micro-stage updates
- [ ] Queue table displays batches
- [ ] Progress updates frequently
- [ ] API calls/duration tracked
- [ ] Tests pass

---

## Phase 5: Complete Features & Testing (1-2 days)

### Objective
Implement remaining features, full testing, and production readiness.

### 5.1 Email Alerting

```python
# In main.py or settings panel

alerter = LogEmailAlerter(
    smtp_server='smtp.gmail.com',
    smtp_port=587,
    sender_email=settings['email'],
    sender_password=settings['password'],
    recipient_emails=settings['recipients']
)

# In pipeline error handling
if critical_error:
    screenshot = take_dashboard_screenshot()
    alerter.send_critical_error_alert(
        error_message=str(e),
        screenshot_path=screenshot
    )
```

### 5.2 Profile Reprocessing

```python
# In profile_browser.py when reprocess clicked

dialog = ReprocessDialog('AAPL', profile)
dialog.reprocess_requested.connect(self.on_reprocess)

def on_reprocess(self, settings):
    if settings['mode'] == 'full_rebuild':
        # Delete existing data
        # Fetch from IPO date
    else:
        # Incremental update
        # Fetch only new data since last update
```

### 5.3 Incremental Update Strategy

```python
# New mode in pipeline.py

def process_symbol_incremental(self, symbol):
    # Get last update time from profile
    profile = storage.get_profile(symbol)
    last_update = profile['last_updated']
    
    # Fetch only new data
    new_df = fetcher.fetch_intraday_data(
        symbol,
        from_date=last_update.strftime('%Y-%m-%d')
    )
    
    # Merge with existing
    # Re-engineer only new rows
    # Update profile with new features
```

### 5.4 Comprehensive Testing

```python
# tests/test_dashboard_full_integration.py

def test_full_pipeline_workflow():
    """Full end-to-end test"""
    # 1. Start dashboard
    # 2. Select companies
    # 3. Start pipeline
    # 4. Monitor progress
    # 5. Check results
    # 6. Verify persistence
    # 7. Restart and verify data
```

### Deliverables
- [ ] Email alerting configured
- [ ] Email tests passing
- [ ] Reprocess dialog connected
- [ ] Full rebuild logic working
- [ ] Incremental update logic working
- [ ] Full end-to-end test passing
- [ ] Performance optimized
- [ ] Production ready

---

## Implementation Timeline

| Phase | Tasks | Estimated | Status |
|-------|-------|-----------|--------|
| 1 | Initialize & persistence | ✅ 1 hour | COMPLETE |
| 2 | Real-time metrics | ⏳ 3-5 hrs | READY |
| 3 | Company management | ⏳ 3-5 hrs | READY |
| 4 | Micro-stage progress | ⏳ 2-3 hrs | READY |
| 5 | Features & testing | ⏳ 1-2 days | READY |
| **TOTAL** | **All phases** | **~3-4 days** | **IN PROGRESS** |

---

## Success Criteria by Phase

### Phase 2
- [ ] ETA updates every 10 seconds
- [ ] Throughput calculated correctly
- [ ] Per-symbol timing accurate
- [ ] No performance degradation

### Phase 3
- [ ] Company list fetches successfully
- [ ] Caching works across sessions
- [ ] Search <100ms response
- [ ] File import handles CSV/TXT

### Phase 4
- [ ] Micro-stage updates frequent
- [ ] Progress shows accurate batches
- [ ] Queue table reflects real-time state
- [ ] No display lag

### Phase 5
- [ ] Email sends on critical error
- [ ] Email includes screenshot
- [ ] Reprocess changes modes correctly
- [ ] Incremental update preserves features
- [ ] Full end-to-end test passes

---

## Quick Start for Phase 2

1. **Open** `dashboard/controllers/pipeline_controller.py`
2. **Add** MetricsCalculator initialization
3. **Connect** metrics_updated signal
4. **Update** monitor_panel.py with timer
5. **Test** ETA display updates

See `QUICK_START_INTEGRATION.md` for code examples.

---

## Dependencies Check

All required modules already created:
- ✅ MetricsCalculator (ready)
- ✅ APIStatsTracker (ready)
- ✅ LogEmailAlerter (ready)
- ✅ CompanySelectorDialog (ready)
- ✅ ReprocessDialog (ready)

No additional packages needed.

---

## Architecture Notes

- Each phase builds on previous
- No breaking changes
- Backward compatible throughout
- Can pause/resume at phase boundaries
- Can test each phase independently

---

## Support & Resources

**For Phase 2 (Metrics):**
- See: `docs/API_REFERENCE_DASHBOARD.md` (MetricsCalculator section)
- See: `docs/IMPLEMENTATION_GUIDE.md` (Metrics Integration)

**For Phase 3 (Companies):**
- See: `docs/API_REFERENCE_DASHBOARD.md` (CompanySelectorDialog)
- See: data_fetcher.py (fetch_exchange_symbols method)

**For Phase 4 (Micro-stage):**
- See: `dashboard/ui/widgets/symbol_queue_table.py` (Column structure)
- See: Signal definitions in qt_signals.py

**For Phase 5 (Features):**
- See: `docs/IMPLEMENTATION_GUIDE.md` (Full sections)
- See: Individual dialog/service documentation

---

## Recommended Approach

1. **Do Phase 2 first** - Establishes metrics foundation
2. **Do Phase 3 next** - Independent feature
3. **Do Phase 4 after** - Depends on worker signals
4. **Do Phase 5 last** - Ties everything together

**Estimated total time: 3-4 days for full implementation**

---

**Status: Ready to begin Phase 2**

Next: Connect MetricsCalculator to PipelineController

