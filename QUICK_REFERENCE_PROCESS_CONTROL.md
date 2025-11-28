# Quick Reference - Process Control v3.0

## 🎯 Global Controls (Dashboard Top)

| Button | Function | Effect |
|--------|----------|--------|
| ⏸ | Pause | Pauses ALL workers between API calls |
| ▶ | Resume | Resumes ALL workers |
| ⏹ | Stop | Stops ALL workers immediately |
| 🗑 | Clear | Stops all + clears queue |

**Behavior:** Global actions affect every symbol

---

## 🎯 Per-Symbol Controls (Right-Click Menu)

| Option | Function | Effect |
|--------|----------|--------|
| ⏸ Pause This Symbol | Pause one symbol | Pauses ONE worker (others continue) |
| ▶ Resume This Symbol | Resume one symbol | Resumes ONE paused worker |
| 🛑 Cancel This Symbol | Cancel one symbol | Stops ONE worker immediately |
| ⏭ Skip This Symbol | Skip one symbol | Prevents ONE symbol from running |
| 🔄 Retry | Retry failed | Retries only if failed |
| 🗑 Remove | Remove from queue | Removes ONE row from display |
| 📤 Export JSON | Export profile | Exports ONE symbol's data |

**Behavior:** Per-symbol actions affect only the selected symbol

---

## 📊 Status Indicator Legend

| Status | Color | Meaning |
|--------|-------|---------|
| ⏳ Queued | Gray | Waiting to start |
| 🔄 Running | Blue | Currently processing |
| ⏸ Paused | Yellow | Paused by user (waiting) |
| ✅ Completed | Green | Successfully finished |
| ❌ Failed | Red | Encountered error |
| ⏭ Skipped | Orange | Skipped by user |
| 🛑 Cancelled | Red | Cancelled by user |

---

## 🔄 Control Flow Examples

### Example 1: Pause One Symbol
```
User: Right-click AAPL → "⏸ Pause This Symbol"
      ↓
AAPL: Pauses between API calls
MSFT: Continues normally
GOOGL: Continues normally
      ↓
Queue: Shows AAPL as "⏸ Paused" (yellow)
```

### Example 2: Cancel One Symbol
```
User: Right-click MSFT → "🛑 Cancel This Symbol" → Confirm
      ↓
MSFT: Stops within 2-5 seconds
AAPL: Continues normally
GOOGL: Continues normally
      ↓
Queue: Shows MSFT as "🛑 Cancelled" (red)
```

### Example 3: Global Control
```
User: Click "⏸ Pause" button
      ↓
AAPL: Pauses between API calls
MSFT: Pauses between API calls
GOOGL: Pauses between API calls
      ↓
Queue: All show pause state
      ↓
User: Click "▶ Resume" button
      ↓
All: Resume from pause
```

---

## ✅ When to Use What

| Scenario | Use | Result |
|----------|-----|--------|
| Take a break | Global Pause | All pause |
| Slow symbol blocks others | Per-Symbol Pause | One pauses, others continue |
| Symbol stuck/erroring | Per-Symbol Cancel | One stops, others continue |
| Don't want a symbol | Per-Symbol Skip | One never runs |
| All done for today | Global Clear | Stop all + clear UI |
| Resume one symbol | Per-Symbol Resume | One continues |
| Resume everything | Global Resume | All continue |

---

## 🔧 Python API Quick Reference

```python
# Create controller
controller = PipelineController(symbols, config)
controller.start()

# Global operations
controller.pause()          # Pause all
controller.resume()         # Resume all
controller.stop()           # Stop all
controller.clear()          # Stop + clear

# Per-symbol operations
controller.pause_symbol('AAPL')      # Pause one
controller.resume_symbol('AAPL')     # Resume one
controller.cancel_symbol('AAPL')     # Cancel one
controller.skip_symbol('AAPL')       # Skip one

# Status queries
status = controller.get_symbol_status('AAPL')
statuses = controller.get_all_statuses()
```

---

## ⚡ Tips & Tricks

### Tip 1: Pause Before Major Change
```
Global pause → Per-symbol control → Resume
Ensures stable state before single-symbol operation
```

### Tip 2: Skip Problematic Symbols
```
Right-click problem symbols → Skip
Saves API calls and time upfront
```

### Tip 3: Check Status First
```
Look at Status column before controlling
Can't control completed/skipped symbols effectively
```

### Tip 4: Mix Global + Per-Symbol
```
Global pause → Skip a few → Resume
Filters symbols mid-run
```

---

## 📈 Real-World Workflows

### Workflow 1: Focused Processing
```
1. Start 20 symbols
2. Global Pause after 30 seconds
3. Skip the 5 slow ones (right-click)
4. Global Resume
5. Only 15 fast ones process
6. Result: Faster completion
```

### Workflow 2: Priority Processing
```
1. Start 10 symbols
2. Pause the most important one (AAPL)
3. Wait for others to complete
4. Resume AAPL
5. Result: AAPL processed when resources available
```

### Workflow 3: Error Recovery
```
1. Pipeline running
2. Noticed MSFT erroring
3. Right-click MSFT → Cancel
4. Others continue unaffected
5. Manually check MSFT later
6. Result: No cascading failures
```

---

## ⚠️ Important Notes

- **Pause** happens between API calls (5-30 sec per chunk)
- **Cancel** happens within 2-5 seconds (waits for current API call)
- **Skip** prevents symbol from ever starting
- **All operations are thread-safe** - use freely
- **No breaking changes** - old code still works

---

## 🔍 Troubleshooting

| Problem | Solution |
|---------|----------|
| Controls don't appear | Start pipeline first |
| Controls too slow | Waiting for API call to finish (normal) |
| Status not updating | Queue table refreshes every ~10 seconds |
| Process won't stop | May take 2-5 seconds for cleanup |
| Status stuck | Refresh dashboard (F5) |

---

## 📞 Need Help?

**See documentation:**
- `docs/PROCESS_CONTROL_COMPLETE.md` - Full reference
- `docs/ADVANCED_PROCESS_CONTROL.md` - Detailed guide
- `docs/PROCESS_CONTROL_USAGE_EXAMPLES.md` - Code examples

**Run tests:**
```bash
python test_advanced_control.py
```

---

## Version Info

- **Version:** 3.0 - Advanced Process Control
- **Status:** ✅ Production Ready
- **Tests:** 11/11 Passing
- **Date:** November 28, 2025

---

**Ready to use!** Start dashboard:
```bash
.\run_dashboard.bat
```

Enjoy granular process control! 🚀

