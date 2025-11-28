# 🚀 Getting Started with the Dashboard

## ✅ Dashboard is Now Running!

Your desktop dashboard has been successfully launched and is ready to use.

---

## 📋 Quick Start (5 Minutes)

### Step 1: Initial Configuration

When the dashboard opens, you'll see three tabs at the top:
- 📊 **Pipeline Control** (default)
- 🗂 **Database Profiles**
- ⚙ **Settings**

**Click on the "Settings" tab first.**

### Step 2: Configure API & Database

In the Settings tab:

1. **API Configuration**
   - Enter your EODHD API Key
   - Click "Test" button → Should show "✅ API key configured"
   - Keep defaults: 80 calls/minute, 95,000 calls/day

2. **MongoDB Configuration**  
   - Verify URI: `mongodb://localhost:27017`
   - Database Name: `stock_analysis`
   - Click "Test" button → Should show "✅ Connected successfully"

3. **Pipeline Defaults**
   - History Years: 2 (recommended)
   - Chunk Size: 5 days (optimal)
   - Max Workers: 10 (perfect for your Ryzen 5 7600)

4. **Save Settings**
   - Click "💾 Save Settings" button
   - You should see "Settings saved successfully!"

### Step 3: Go Back to Pipeline Control Tab

Click on the **"📊 Pipeline Control"** tab.

### Step 4: Your First Test (3 Symbols)

**In the "Symbol Input" section:**
1. Type in the text box: `AAPL, MSFT, GOOGL`
2. Make sure **"Incremental"** mode is selected
3. Keep **"Enable Parallel Processing"** checked
4. Max Workers should be **10**

**Click the green "▶ Start Pipeline" button**

### Step 5: Watch the Magic! ✨

You'll now see:

**Real-time Metrics Bar** (top):
```
Total: 3  |  Queue: 0  |  Processing: 3  |  ✅ Success: 0  |  ❌ Failed: 0
```

**API Usage Widget** (below metrics):
- Green progress bars showing API calls
- Daily: X / 95,000
- This Minute: X / 80

**Processing Queue Table** (main area):
- Shows each symbol with emoji status
- ⏳ Queued → 🔄 Processing → ✅ Success
- Progress percentage
- Data points fetched
- Duration

**Live Logs** (bottom):
- Color-coded messages
- INFO (white), WARNING (yellow), ERROR (red), SUCCESS (green)
- Auto-scrolls as processing happens

---

## 📊 What Happens During Processing

### Phase 1: Fetching Data (1-2 minutes per symbol)
```
[INFO] Starting AAPL
[INFO] Fetching history from 2023-11-27 to 2025-11-27
[DEBUG] Fetching chunk: 2023-11-27...
[INFO] Fetched 390 rows
[WARNING] Rate limit: waiting 2s
```

The dashboard:
- Makes ~250 API calls per symbol (2 years of data)
- Respects rate limits (will pause if needed)
- Shows progress in real-time

### Phase 2: Engineering Features (10-20 seconds)
```
[INFO] Engineering features for AAPL
[INFO] Calculating 200+ technical indicators
```

The dashboard:
- Calculates all 200+ features
- Price, volume, volatility
- Technical indicators (RSI, MACD, etc.)
- Statistical features
- Regime detection

### Phase 3: Storing (1-2 seconds)
```
[INFO] Saving profile to MongoDB
[SUCCESS] Profile saved: AAPL (6,546 data points)
```

The dashboard:
- Saves to MongoDB
- Marks symbol as ✅ Success
- Updates metrics

### Total Time: 2-3 Minutes for 3 Symbols

With parallel processing, all 3 run simultaneously!

---

## 🎯 After Processing Completes

### Completion Dialog
You'll see a popup:
```
Processing finished!

Succeeded: 3
Failed: 0
Duration: 145.2s
```

Click **OK**.

### View Results

**Click on "🗂 Database Profiles" tab**

You'll see a table with your processed symbols:

| Symbol | Exchange | Data Points | Date Range | Last Updated |
|--------|----------|-------------|------------|--------------|
| AAPL   | US | 6,546 | 2023-11-27 to 2025-11-27 | 2025-11-27 14:30 |
| MSFT   | US | 7,120 | 2023-11-27 to 2025-11-27 | 2025-11-27 14:32 |
| GOOGL  | US | 5,890 | 2023-11-27 to 2025-11-27 | 2025-11-27 14:33 |

### View Profile Details

1. **Click on a row** (e.g., AAPL)
2. **Click "👁 View" button**
3. Profile Editor opens with multiple tabs:

**Overview Tab:**
- Symbol, exchange, data points
- Date range
- Backfill metadata (API calls, duration)

**Price Tab:**
- Current price
- Log returns
- Price velocity
- Rolling statistics

**Indicators Tab:**
- RSI (14)
- MACD
- Bollinger Bands
- ATR
- Stochastic
- And more!

**Regimes Tab:**
- Volatility regime (Low/Medium/High)
- Trend regime (Uptrend/Downtrend/Sideways)
- Liquidity regime

**Raw JSON Tab:**
- Complete profile in JSON
- Can edit and save
- Syntax highlighted

### Export Profile

In the Profile Editor:
1. Click **"📤 Export JSON"** button
2. Choose save location
3. File saved: `AAPL_profile.json`

Now you have your data in a portable format!

---

## 🔥 Processing More Symbols

### Using a File

Go back to **Pipeline Control** tab.

1. **Check "Load from file"**
2. **Click "Browse"** button
3. **Select** `symbols_sample.txt` (provided)
4. **Click "▶ Start Pipeline"**

The file contains:
```
AAPL
MSFT
GOOGL
AMZN
NVDA
META
TSLA
JPM
V
WMT
JNJ
PG
SPY
QQQ
DIA
```

All 15 symbols will process in parallel!

**Time Estimate:** 5-7 minutes for 15 symbols

### Batch Processing (100+ Symbols)

**Create your own file:**
```
# my_watchlist.txt
AAPL
MSFT
GOOGL
... (up to 100+)
```

**Load and process:**
1. Load from file → Browse → Select `my_watchlist.txt`
2. Mode: **Incremental** (after first run)
3. Workers: **10**
4. Start Pipeline

**Monitor API Usage:**
- Watch the API Usage widget
- If bars turn red → Pipeline auto-pauses
- Adjust workers if needed (10 → 5)

---

## 📈 Daily Workflow

### Morning Routine (5 minutes)

1. **Launch Dashboard**
   ```bash
   run_dashboard.bat
   ```

2. **Load Watchlist**
   - Pipeline Control → Load from file → `my_watchlist.txt`

3. **Set Mode to Incremental**
   - This updates existing profiles with new data
   - Much faster (only ~5 API calls per symbol)

4. **Start Processing**
   - Click ▶ Start Pipeline
   - Watch progress

5. **Review Results**
   - Database Profiles → Sort by "Last Updated (Newest)"
   - Check for any failures
   - Export key profiles

---

## ⚙️ Advanced Features

### Pause/Resume

- **⏸ Pause**: Pauses after current jobs complete
- **Resume**: Continue processing
- **⏹ Stop**: Immediately cancels all jobs

### Clear Queue

- **🗑 Clear**: Clears monitoring data
- Useful for starting fresh

### Right-Click Menu

In the Processing Queue table:
- **View Profile**: Opens profile editor
- **Retry**: Retry failed symbol
- **Remove**: Remove from queue
- **Export JSON**: Save profile to file

### Keyboard Shortcuts

- **Ctrl+R**: Refresh profiles
- **Ctrl+Q**: Quit application
- **F5**: Refresh current view

---

## 🐛 Common Issues

### "MongoDB connection failed"

**Solution:**
```bash
# Check if MongoDB is running
mongo --version

# Start MongoDB (Windows, run as admin)
net start MongoDB
```

### "API error 401"

**Solution:**
- Go to Settings tab
- Check API key is correct
- Test connection

### "Rate limit exceeded"

**Solution:**
- This is normal!
- Dashboard automatically waits
- Watch the API Usage widget
- If persistent, reduce workers: 10 → 5

### UI not updating

**Solution:**
- Scroll in the log viewer
- Check "Auto-scroll" is enabled
- Click Refresh in Database Profiles

---

## 📊 Performance Tips

### For Your System (Ryzen 5 7600, 32GB RAM)

**Optimal Settings:**
- Workers: **10** (default)
- Chunk Size: **5 days** (default)
- Mode: **Incremental** (for daily updates)

**Why?**
- 6 cores × 2 threads = 12 total threads
- 10 workers = Maximum throughput
- 2 threads left for UI + OS = Smooth experience

### API Quota Management

**Daily Capacity:**
- Full backfill: ~380 symbols/day
- Incremental updates: ~19,000 symbols/day

**Strategy:**
1. **Week 1**: Full backfill (380 symbols)
2. **Daily**: Incremental updates (all symbols in 5 min)

---

## 📚 Documentation Reference

| Document | Purpose |
|----------|---------|
| **QUICK_REF.md** | 1-page cheat sheet |
| **DASHBOARD_GUIDE.md** | Complete walkthrough |
| **README_DASHBOARD.md** | Technical documentation |
| **INDEX.md** | Find any file/feature |
| **LAUNCH_FIX_SUMMARY.md** | Troubleshooting import issues |

---

## 🎊 Congratulations!

You're now up and running with a professional desktop dashboard for stock data processing!

**What You Can Do:**
- ✅ Process 100s of symbols in parallel
- ✅ Monitor progress in real-time
- ✅ Browse and edit profiles
- ✅ Export data to JSON
- ✅ Manage API quotas efficiently

**Next Steps:**
1. Process your full watchlist
2. Set up daily incremental updates
3. Explore profile features
4. Build your analysis pipeline

---

**Need Help?**
- Check logs: `logs/pipeline_*.log`
- Run test: `python test_imports.py`
- Read docs: `DASHBOARD_GUIDE.md`

**Enjoy your new dashboard! 🚀**

