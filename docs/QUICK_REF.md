# Dashboard Quick Reference Card

## 🚀 Launch
```bash
run_dashboard.bat
# or
python dashboard/main.py
```

## ⚙️ First-Time Setup (Settings Tab)
```
API Key: [paste your key] → Test → Save
MongoDB: mongodb://localhost:27017 → Test → Save
Workers: 10 (optimal for Ryzen 5 7600)
```

## 📊 Process Symbols (Pipeline Control Tab)

### Quick Test (3 symbols)
```
Input: AAPL, MSFT, GOOGL
Mode: ⦿ Incremental
Workers: 10
Click: ▶ Start Pipeline
```

### Batch Processing (file)
```
✓ Load from file → Browse → symbols_sample.txt
Mode: ⦿ Incremental
Click: ▶ Start Pipeline
```

## 📈 Monitor Progress

### Metrics Bar
```
Total: 10 | Queue: 2 | Processing: 3 | ✅ Success: 5 | ❌ Failed: 0
```

### API Usage (Color Coded)
```
🟢 Green (0-60%): Safe
🟡 Yellow (60-80%): Moderate  
🔴 Red (80%+): Slow down!
```

### Status Icons
```
⏳ Queued   → Waiting
🔄 Processing → Working
✅ Success   → Done
❌ Failed    → Error
```

## 🗂 View Profiles (Database Tab)
```
Search: AAPL
Click row → View → See all features
Export → Save JSON file
```

## ⌨️ Keyboard Shortcuts
```
Ctrl+R : Refresh profiles
Ctrl+Q : Quit
F5     : Refresh view
Ctrl+S : Save settings
```

## 🎯 Optimal Settings (Your System)
```
CPU: Ryzen 5 7600 (6 cores)
Workers: 10 threads
Chunk: 5 days
Mode: Incremental (after first run)
```

## 📊 Capacity
```
Per Symbol: ~250 API calls (2 years)
Daily Limit: 95,000 calls
Capacity: ~380 symbols/day

Incremental: ~5 calls/symbol
Capacity: ~19,000 symbols/day
```

## ⏱ Speed Estimates
```
10 symbols  : 2-3 minutes
50 symbols  : 10-15 minutes
100 symbols : 20-30 minutes
380 symbols : 2-3 hours
```

## 🐛 Common Issues

### Dashboard won't start
```bash
pip install -r requirements.txt
python test_dashboard.py
```

### MongoDB error
```bash
# Start MongoDB
net start MongoDB
# Test in Settings tab
```

### API errors
```
401: Invalid API key → Check Settings
429: Rate limit → Wait or reduce workers
404: Invalid symbol → Check spelling
```

### UI slow
```
Reduce workers: 10 → 5
Clear queue: Click 🗑
Restart dashboard
```

## 📁 Important Files
```
run_dashboard.bat       → Launch script
DASHBOARD_GUIDE.md      → Full user guide
README_DASHBOARD.md     → Technical docs
symbols_sample.txt      → Example symbols
logs/                   → Error logs
~/.pipeline_dashboard_config.json → Settings
```

## 💡 Pro Tips
```
✓ Start with 5-10 symbols to test
✓ Use Incremental mode for daily updates
✓ Monitor API usage widget (avoid red!)
✓ Export important profiles to JSON
✓ Check logs/ directory for errors
✓ Keep workers at 8-10 for best speed
```

## 🎯 Daily Workflow
```
1. Launch dashboard
2. Load watchlist (50-100 symbols)
3. Select Incremental mode
4. Start pipeline (10 workers)
5. Monitor API usage
6. Review results in Database tab
7. Export key profiles
```

## 🆘 Get Help
```
Logs: logs/pipeline_*.log
Test: python test_dashboard.py
Guide: DASHBOARD_GUIDE.md
Docs: README_DASHBOARD.md
```

---

**Remember**: Dashboard is optimized for YOUR hardware!
- Ryzen 5 7600: 10 workers perfect
- 32GB RAM: Can handle 100s of symbols
- RTX 3060: Ready for ML features

**Start small → Test → Scale up!** 🚀

