# Quick Start Guide - Updated Dashboard (v2.0)

## Launching the Dashboard

### Windows PowerShell (Recommended)
```powershell
cd "D:\development project\Minute_Data_Pipeline"
.\run_dashboard.bat
```

### Direct Python Launch
```powershell
python dashboard\main.py
```

---

## Key Features & How to Use

### 1. **Rate Limited API Calls** 🚦
**What Changed:** API calls now respect 80 calls/minute and 95,000 calls/day limits.

**How to Verify:**
- Start processing a symbol
- Watch "Live Logs" section
- You'll see messages like: `"Rate limit: sleeping 2.5s"` when approaching limits
- "API Usage Today" counter increments gradually (not instant burst)

**Tips:**
- Increase workers to maintain throughput while respecting limits
- Each worker gets ~7 calls/min (80 total / 10 workers = 8, with safety margin)
- Daily counter persists across app restarts

---

### 2. **Resizable Queue & Logs** 📊
**What Changed:** Processing Queue and Live Logs now use a draggable splitter.

**How to Use:**
1. Start pipeline with 5+ symbols
2. Move mouse to the line between "Processing Queue" and "Live Logs"
3. Cursor changes to resize icon (↕)
4. Click and drag up/down to allocate more space to queue or logs

**Default Split:**
- Processing Queue: 75% (shows ~6-8 rows)
- Live Logs: 25%

---

### 3. **Working Pause/Resume** ⏸️▶️
**What Changed:** Pause button now actually pauses workers between API calls.

**How to Use:**

#### To Pause:
1. Start pipeline (3+ symbols recommended)
2. Click "⏸ Pause" button
3. **Observe:**
   - Button text changes to "▶ Resume"
   - Live Logs stop scrolling (after current API call completes)
   - Processing Queue rows show paused state
   - Workers sleep and check every 0.25 seconds for resume signal

#### To Resume:
1. Click "▶ Resume" button
2. **Observe:**
   - Button text changes back to "⏸ Pause"
   - Live Logs resume scrolling
   - Processing continues from where it paused

**Important Notes:**
- Pause happens BETWEEN API calls (not during)
- In-flight requests complete before pausing
- Typical pause delay: 0.5-2 seconds

---

### 4. **Reliable Stop** 🛑
**What Changed:** Stop button now properly cancels all workers and cleans up threads.

**How to Use:**
1. Click "⏹ Stop" button during processing
2. **Observe:**
   - All workers receive cancel signal
   - Processing stops within 1-5 seconds (after current API calls complete)
   - No lingering Python processes (verify in Task Manager)
   - Can start new pipeline immediately after

**Difference from Clear:**
- **Stop:** Halts processing, keeps queue visible
- **Clear:** Halts processing AND empties queue table

---

### 5. **Full Clear** 🗑️
**What Changed:** Clear button now ensures complete thread cleanup.

**How to Use:**
1. Click "🗑 Clear" button
2. **Observe:**
   - All workers stopped
   - Queue table cleared
   - Logs cleared
   - API usage widget NOT cleared (persists for the day)
   - Dashboard ready for new batch

**When to Use:**
- Switching to different symbol set
- Resetting dashboard state
- After errors/failed runs

---

### 6. **Persistent API Counter** 💾
**What Changed:** Daily API usage now saves to disk and persists across restarts.

**Storage Location:**
```
C:\Users\YourName\.pipeline_api_usage.json
```

**Behavior:**
- **Same Day:** Counter accumulates (dashboard restart doesn't reset)
- **New Day:** Counter auto-resets to 0
- **Data Structure:**
  ```json
  {
    "day": "2025-11-28",
    "stats": {
      "daily_calls": 4523,
      "minute_calls": 12
    }
  }
  ```

**Manual Reset (if needed):**
```powershell
Remove-Item ~\.pipeline_api_usage.json
```

---

### 7. **Extended History Options** 📅
**What Changed:** Can now fetch up to 30 years or "All Available" history.

**How to Use:**
1. In "Processing Options" section
2. Click "History Years" dropdown
3. Select from:
   - **1-30:** Specific number of years
   - **All Available:** Fetch back to IPO (company start date)

**API Call Estimates:**
- 1 year ≈ 12 chunks ≈ 12 API calls
- 5 years ≈ 60 chunks ≈ 60 API calls
- 10 years ≈ 120 chunks ≈ 120 API calls
- 30 years ≈ 360 chunks ≈ 360 API calls
- All Available: Depends on company age (could be 1,000+ calls for old companies)

**Chunk Size:**
- Default: 30 days per API call (recommended)
- Adjustable: 1-30 days in settings

---

## Common Workflows

### Workflow 1: Quick Test (1 Symbol)
```
1. Enter "AAPL" in Symbol Input
2. Select "Incremental" mode
3. History Years: "2"
4. Click "▶ Start Pipeline"
5. Watch Processing Queue and Live Logs
6. Verify rate limiting (should see ~1-2 second gaps between API calls)
```

### Workflow 2: Batch Processing (Top 10)
```
1. Click "📊 Top 10" quick select button
2. Symbols auto-populate: AAPL, MSFT, GOOGL, AMZN, NVDA, TSLA, META, BRK, JNJ, V
3. Select "Full Rebuild" mode
4. History Years: "5"
5. Max Workers: "10" (default)
6. Click "▶ Start Pipeline"
7. Monitor "API Usage Today" - should increment slowly
8. ETA displayed in Real-time Metrics
```

### Workflow 3: Pause & Resume Test
```
1. Start pipeline with 5+ symbols
2. Wait for 2-3 symbols to start processing
3. Click "⏸ Pause"
4. Verify: Button changes to "▶ Resume", logs stop scrolling
5. Wait 10 seconds
6. Click "▶ Resume"
7. Verify: Processing continues smoothly
```

### Workflow 4: Stop & Restart
```
1. Start pipeline with 10 symbols
2. Let 3-4 complete
3. Click "⏹ Stop"
4. Verify: All processing stops, no lingering processes
5. Enter new symbols
6. Click "▶ Start Pipeline" again
7. Verify: New pipeline starts fresh
```

---

## Troubleshooting

### Issue: "Rate limit: sleeping 60s" messages constantly
**Cause:** Daily quota approaching or per-minute limit hit
**Solution:**
- Reduce max workers (try 5 instead of 10)
- Increase chunk size (30 days recommended)
- Check "API Usage Today" - if near 95,000, wait for next day

### Issue: Pause button doesn't seem to work
**Cause:** Workers pause BETWEEN API calls, not during
**Solution:**
- Wait 2-5 seconds for current API call to complete
- Look for logs to stop scrolling as confirmation
- If using 30-day chunks, each chunk takes ~2 seconds

### Issue: Stop button leaves processes running
**Cause:** Old issue - should be fixed in v2.0
**Verification:**
1. Click Stop
2. Open Task Manager
3. Search for "python" processes
4. Should only see 1 (the dashboard itself)
5. If multiple: Report bug (check logs for error traces)

### Issue: API counter reset to 0 unexpectedly
**Cause:** Date changed or file deleted
**Solution:**
- Check `~\.pipeline_api_usage.json` exists
- Verify "day" field matches today's date
- If corrupted, delete file and restart dashboard

### Issue: Queue table still too small
**Solution:**
1. Drag splitter UP (towards API Usage section)
2. Queue table expands
3. Logs section shrinks
4. Dashboard remembers position (saved in Qt settings)

---

## Keyboard Shortcuts

- `F5` - Refresh Profiles (in Database Profiles tab)
- `Ctrl+Q` - Quit dashboard
- `Esc` - Close dialogs

---

## Performance Tips

### Optimize for Ryzen 5 7600 (6 cores / 12 threads)
**Recommended Settings:**
- Max Workers: **10** (leaves 2 threads for UI + system)
- Chunk Size: **30 days** (balances API calls vs data volume)
- History Years: **2-5** (good balance)

### For Large Batches (50+ symbols)
```
Max Workers: 8-10
Chunk Size: 30 days
Mode: Full Rebuild
Enable Parallel: ✓
```

### For Quick Updates (existing profiles)
```
Max Workers: 5-6
Mode: Incremental
History Years: N/A (only fetches new data)
```

---

## Dashboard Sections Explained

### Real-time Metrics Bar
- **Total:** Total symbols in queue
- **⏳ Queue:** Waiting to start
- **🔄 Processing:** Currently being processed
- **✅ Success:** Completed successfully
- **❌ Failed:** Errored out
- **⏭ Skipped:** Skipped (e.g., no data available)
- **⏱ ETA:** Estimated time to completion (updates every 10 seconds)

### Processing Queue Table (Columns)
1. **Symbol:** Ticker
2. **Status:** Current stage (Fetching, Engineering, Creating, Storing, Complete)
3. **Progress:** Percentage (0-100%)
4. **Micro-Stage:** Detailed step (e.g., "Fetch batch 5/24", "Starting feature pipeline")
5. **Data Pts:** Number of minute bars fetched
6. **Date Range:** Start to end date of data
7. **API Calls:** Number of API calls used for this symbol
8. **Duration:** Time elapsed for this symbol (minutes:seconds)

### Live Logs (Color Coded)
- **Gray:** DEBUG
- **White:** INFO
- **Yellow:** WARNING
- **Red:** ERROR
- **Green:** SUCCESS

### API Usage Widget
- **Top Bar:** Daily total (persists across restarts)
- **Bottom Bar:** Current minute (resets every 60 seconds)
- **Colors:**
  - Green: < 70k calls
  - Orange: 70k - 90k calls
  - Red: > 90k calls (approaching limit)

---

## Next Steps After Processing

1. **View Profiles:**
   - Go to "🗂 Database Profiles" tab
   - Double-click a profile to view/edit
   - Tabs: Overview, Price, Volume, Volatility, Indicators, Regimes, Predictions, Raw JSON

2. **Export Data:**
   - Right-click profile in table
   - Select "Export JSON"
   - Save to file for external analysis

3. **Re-process Symbol:**
   - Select profile
   - Click "🔄 Re-process" button
   - Choose: Full Rebuild or Incremental Update

---

## Support & Logs

**Log Files:**
```
D:\development project\Minute_Data_Pipeline\logs\pipeline_YYYY-MM-DD.log
```

**Configuration:**
```
C:\Users\YourName\.pipeline_dashboard_config.json
```

**API Usage:**
```
C:\Users\YourName\.pipeline_api_usage.json
```

---

**Version:** 2.0  
**Last Updated:** 2025-11-28  
**Status:** ✅ Production Ready

