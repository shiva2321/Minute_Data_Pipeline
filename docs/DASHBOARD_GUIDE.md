# Dashboard User Guide

## Complete Walkthrough

### Part 1: Initial Setup (5 minutes)

#### Step 1: Install Dependencies
```bash
# Navigate to project directory
cd "D:\development project\Minute_Data_Pipeline"

# Activate virtual environment
.venv\Scripts\activate

# Install all dependencies (if not already done)
pip install -r requirements.txt
```

#### Step 2: Configure Environment
Edit `.env` file:
```env
EODHD_API_KEY=your_actual_api_key_here
MONGODB_URI=mongodb://localhost:27017
DATABASE_NAME=stock_analysis
```

#### Step 3: Start MongoDB
```bash
# Make sure MongoDB is running
mongod --version
# If not installed, download from: https://www.mongodb.com/try/download/community
```

#### Step 4: Launch Dashboard
```bash
# Windows
run_dashboard.bat

# Or directly
python dashboard/main.py
```

---

### Part 2: First Run Configuration (3 minutes)

When dashboard opens:

#### 1. Navigate to Settings Tab
Click "⚙ Settings" at the top

#### 2. Configure API
- **EODHD API Key**: Paste your API key
- Click **"Test"** button → Should show "✅ API key configured"
- **Calls per Minute**: 80 (default for Extended plan)
- **Calls per Day**: 95,000 (default)

#### 3. Configure MongoDB
- **Connection URI**: `mongodb://localhost:27017` (default)
- **Database Name**: `stock_analysis` (default)
- Click **"Test"** button → Should show "✅ Connected successfully"

#### 4. Set Pipeline Defaults
- **History Years**: 2 (recommended for most use cases)
- **Chunk Size**: 5 days (optimal for API efficiency)
- **Max Workers**: 10 (optimized for Ryzen 5 7600)
- ✓ **Store Backfill Metadata**: Keep checked
- ✓ **Enable Auto-Retry**: Keep checked

#### 5. UI Settings
- **Theme**: Dark (default, easier on eyes)
- **Log Level**: INFO (shows important messages)
- **Refresh Rate**: 2 seconds
- Desktop Notifications: Optional
- Minimize to Tray: Optional

#### 6. Save Settings
Click **"💾 Save Settings"** at bottom

---

### Part 3: Processing Your First Symbols (10 minutes)

#### Go to Pipeline Control Tab

#### Option A: Manual Input (Quick Test)
1. In "Ticker Symbol(s)" field, enter:
   ```
   AAPL, MSFT, GOOGL
   ```

2. Select Processing Mode:
   - **⦿ Incremental**: Choose this (faster for first-time)

3. Configure Options:
   - History Years: **2**
   - Chunk Size: **5 days**
   - ✓ Enable Parallel Processing
   - Max Workers: **10 threads**

4. Click **"▶ Start Pipeline"**

#### Option B: File Input (Batch Processing)
1. Use the provided sample file:
   - ✓ Check "Load from file"
   - Click "Browse"
   - Select `symbols_sample.txt`

2. Click **"▶ Start Pipeline"**

---

### Part 4: Monitoring Progress (During Processing)

#### Real-time Metrics Bar
Watch the top metrics update:
```
Total: 3  |  Queue: 0  |  Processing: 2  |  ✅ Success: 1  |  ❌ Failed: 0  |  ⏱ ETA: 4m 32s
```

#### API Usage Widget
Shows rate limit usage:
```
Daily: 756 / 95,000 (0.8%)    [████░░░░░░░░░░]  ← Green = Safe
This Minute: 12 / 80 (15%)    [███░░░░░░░░░░]   ← Green = Safe
```

**Color Codes:**
- 🟢 Green (0-60%): Safe
- 🟡 Yellow (60-80%): Moderate
- 🟠 Orange (80-95%): High
- 🔴 Red (95%+): Critical

#### Processing Queue Table
| Symbol | Status | Progress | Data Points | Date Range | API | Time |
|--------|--------|----------|-------------|------------|-----|------|
| AAPL   | ✅ Success | 100% | 6,546 | 2023-11 to now | 252 | 2.3m |
| MSFT   | 🔄 Fetching | 45% | 2,890 | 2024-01 to now | 115 | 1.1m |
| GOOGL  | ⏳ Queued | 0% | - | - | - | - |

**Status Icons:**
- ⏳ Queued (gray) - Waiting to start
- 🔄 Processing (blue) - Currently working
- ⬇️ Fetching (blue) - Downloading data
- ⚙️ Engineering (blue) - Calculating features
- 💾 Storing (blue) - Saving to database
- ✅ Success (green) - Completed successfully
- ❌ Failed (red) - Error occurred
- ⏭️ Skipped (orange) - Skipped for some reason

#### Live Logs
```
[2025-11-28 14:32:15] INFO     | Starting AAPL
[2025-11-28 14:32:16] DEBUG    | Fetching 2023-11-01...
[2025-11-28 14:32:18] INFO     | Fetched 390 rows
[2025-11-28 14:32:19] WARNING  | Rate limit: waiting 2s
[2025-11-28 14:32:22] INFO     | Engineering features
[2025-11-28 14:32:25] SUCCESS  | Saved profile to DB
```

**Log Levels:**
- 🔵 DEBUG (gray) - Detailed technical info
- ⚪ INFO (white) - Normal operations
- 🟡 WARNING (yellow) - Attention needed
- 🔴 ERROR (red) - Something failed
- 🟢 SUCCESS (green) - Operation succeeded

#### Right-Click Context Menu
Right-click any symbol in the table:
- **View Profile**: Open profile editor
- **Retry**: Retry failed symbol
- **Remove**: Remove from queue
- **Export JSON**: Save profile to file

---

### Part 5: Viewing Results (After Completion)

#### When Pipeline Completes
A dialog shows:
```
Processing finished!

Succeeded: 3
Failed: 0
Duration: 145.2s
```

Click **OK**

#### Navigate to Database Profiles Tab

#### Browse Profiles
You'll see all processed symbols:
| Symbol | Exchange | Data Points | Date Range | Last Updated |
|--------|----------|-------------|------------|--------------|
| AAPL   | US | 6,546 | 2023-11-01 to 2025-11-28 | 2025-11-28 14:30 |
| MSFT   | US | 7,120 | 2023-10-15 to 2025-11-28 | 2025-11-28 13:45 |
| GOOGL  | US | 5,890 | 2024-01-05 to 2025-11-28 | 2025-11-27 16:20 |

#### Search and Filter
- **Search box**: Type "AAPL" to filter
- **Sort dropdown**: 
  - Last Updated (Newest) ← Default
  - Symbol (A-Z)
  - Data Points (Most)

#### View a Profile
1. Click on a row (e.g., AAPL)
2. Click **"👁 View"** button
3. Profile Editor opens with tabs:

**Overview Tab:**
```
Symbol:       AAPL
Exchange:     US
Data Points:  6,546
Date Range:   2023-11-01 to 2025-11-28
Last Updated: 2025-11-28 14:30:15

Backfill Status: ✅ Complete
API Calls Used:  252
Duration:        145.2 seconds
```

**Price Features Tab:**
```
Current Price:     $277.55
Log Return (1m):   0.0004
Price Velocity:    0.15
Rolling Mean (20): 278.19
Price Acceleration: -0.02
```

**Technical Indicators Tab:**
```
RSI (14):         54.32
MACD:             1.23
MACD Signal:      0.98
MACD Histogram:   0.25
Bollinger Upper:  285.67
Bollinger Lower:  270.43
```

**Regime Features Tab:**
```
Volatility Regime:  Low
Trend Regime:       Uptrend
Liquidity Regime:   High
Market Regime:      Normal
```

**Raw JSON Tab:**
Full JSON with syntax highlighting:
```json
{
  "symbol": "AAPL",
  "data_points_count": 6546,
  "price_features": {
    "current_price": 277.55,
    "log_return_1m": 0.0004,
    ...
  },
  ...
}
```

#### Export Profile
1. Click **"📤 Export JSON"**
2. Choose save location
3. File saved: `AAPL_profile.json`

---

### Part 6: Advanced Operations

#### Incremental Updates
To update existing profiles with new data:

1. Enter symbols that already exist in database
2. Select **⦿ Incremental** mode
3. Click **"▶ Start Pipeline"**
4. Pipeline fetches only new data since last update

**Benefits:**
- Faster (only new data)
- Lower API usage
- Maintains historical data

#### Full Rebuild
To completely recreate profiles:

1. Select **○ Full Rebuild** mode
2. Set History Years (1-5)
3. Click **"▶ Start Pipeline"**
4. Fetches complete history from scratch

**When to use:**
- Data corruption suspected
- Want different time range
- First-time processing

#### Batch Processing Large Lists
For 100+ symbols:

**Step 1: Prepare file**
Create `my_symbols.txt`:
```
# Tech stocks
AAPL
MSFT
GOOGL
# ... (100+ more)
```

**Step 2: Load file**
- ✓ Check "Load from file"
- Browse to your file
- Pipeline validates and shows count

**Step 3: Monitor API quotas**
Watch the API Usage widget closely:
- If approaching daily limit (95K), pipeline auto-pauses
- Resume tomorrow or reduce worker count

**Step 4: Adjust workers if needed**
If hitting minute limit (80 calls):
- Pause pipeline (⏸ button)
- Reduce Max Workers from 10 → 5
- Resume

#### Handling Failures
If symbols fail:

1. Check error in Date Range column
2. Common errors:
   - "404": Invalid symbol
   - "Rate limit": Temporary, will retry
   - "No data": Symbol has no minute data
3. Right-click failed symbol → **Retry**
4. Or remove invalid symbols

---

### Part 7: Optimization Tips

#### For Ryzen 5 7600 (Your System)
**Optimal settings:**
```
Max Workers: 10 threads
Chunk Size: 5 days
Mode: Incremental (after first run)
```

**Why?**
- 6 cores × 2 threads = 12 threads total
- 10 workers leaves 2 threads for UI + OS
- Maximizes throughput without freezing

#### API Quota Planning
**Math:**
- 1 symbol × 2 years ≈ 250 API calls
- 95,000 daily limit ÷ 250 = **~380 symbols/day**
- 10 workers × 2 min/symbol = **30 symbols/hour**

**Strategy for 500+ symbols:**
1. Day 1: Process 380 symbols
2. Day 2: Process 120 symbols
3. Total: 2 days for 500 symbols

**Or use incremental:**
- Day 1: Full rebuild (380 symbols)
- Day 2+: Incremental updates (5 calls/symbol)
- Can update 19,000 symbols/day!

#### Memory Management
Dashboard automatically manages memory:
- Logs limited to 1000 lines
- Profiles loaded on demand
- Workers cleaned after completion

**If experiencing slowness:**
1. Click **"🗑 Clear"** to clear queue
2. Restart application
3. Reduce worker count to 5-6

---

### Part 8: Troubleshooting

#### Dashboard won't start
```bash
# Check Python version
python --version  # Should be 3.10+

# Reinstall PyQt6
pip uninstall PyQt6 PyQt6-WebEngine PyQt6-Charts
pip install PyQt6>=6.6.0 PyQt6-WebEngine PyQt6-WebEngine PyQt6-Charts>=6.6.0

# Run test
python test_dashboard.py
```

#### MongoDB connection failed
1. Check if MongoDB is running:
   ```bash
   mongo --version
   ```
2. Start MongoDB service:
   ```bash
   # Windows (as admin)
   net start MongoDB
   ```
3. Verify in Settings tab with "Test" button

#### API errors
Common errors in logs:
- **"401 Unauthorized"**: Invalid API key
- **"429 Too Many Requests"**: Rate limit hit
- **"404 Not Found"**: Invalid symbol
- **"500 Server Error"**: EODHD API issue (retry later)

#### UI freezing
Should never happen (all processing is threaded), but if it does:
1. Click Stop button
2. Wait 10 seconds
3. If still frozen, close and restart
4. Reduce worker count

#### Slow processing
If pipeline is slower than expected:
1. Check API Usage widget - might be rate limited
2. Check network connection
3. Try reducing chunk size to 3 days
4. Reduce workers to 5-6

---

### Part 9: Keyboard Shortcuts

| Shortcut | Action |
|----------|--------|
| Ctrl+R | Refresh profiles |
| Ctrl+Q | Quit application |
| F5 | Refresh current view |
| Ctrl+S | Save settings (in Settings tab) |

---

### Part 10: Best Practices

#### Daily Workflow
1. **Morning**: Start incremental update for watchlist
2. **Monitor**: Check for failures
3. **Review**: Browse new profiles
4. **Export**: Save important profiles to JSON

#### Weekly Maintenance
1. Review failed symbols
2. Clean up old/unused profiles
3. Check API quota usage trends
4. Update symbol lists

#### Production Tips
- Use **incremental mode** for daily updates
- Schedule large batches during off-hours
- Keep worker count at 8-10 for optimal speed
- Monitor logs for recurring errors

---

## Summary Checklist

### Initial Setup
- [ ] Install dependencies (`pip install -r requirements.txt`)
- [ ] Configure `.env` file with API key
- [ ] Start MongoDB
- [ ] Launch dashboard (`run_dashboard.bat`)
- [ ] Configure settings (API, MongoDB, defaults)
- [ ] Test with 3-5 symbols

### Regular Usage
- [ ] Enter symbols or load file
- [ ] Choose mode (incremental vs full)
- [ ] Set worker count (8-10 for speed)
- [ ] Monitor API usage
- [ ] Review results in Database tab
- [ ] Export important profiles

### Troubleshooting
- [ ] Check logs for errors
- [ ] Verify API quota remaining
- [ ] Test MongoDB connection
- [ ] Reduce workers if rate limiting
- [ ] Retry failed symbols

---

**You're all set!** The dashboard is now ready for production use. Start with a small batch to familiarize yourself with the interface, then scale up to hundreds of symbols.

For questions, check:
- `README_DASHBOARD.md` - Complete documentation
- `API_REFERENCE.md` - API details
- `FEATURE_GUIDE.md` - Feature explanations
- Logs in `logs/` directory

