# Troubleshooting Guide

Solutions for common issues and errors.

## Dashboard Issues

### Dashboard Won't Start

**Error**: Application crashes or won't launch

**Solutions**:
1. Check Python version:
   ```bash
   python --version  # Should be 3.8 or higher
   ```

2. Reinstall dependencies:
   ```bash
   pip install -r requirements.txt --force-reinstall
   ```

3. Check for errors:
   ```bash
   python dashboard/main.py  # Run directly to see error
   ```

4. Clear PyQt cache:
   ```bash
   rmdir /s /q .cache
   ```

---

## Database Issues

### MongoDB Connection Error

**Error**: "Could not connect to MongoDB" or "Connection refused"

**Solutions**:

1. **Verify MongoDB is running**:
   ```bash
   mongod --dbpath "C:\data\db"
   ```

2. **Check connection string** in `.env`:
   ```
   Local: mongodb://localhost:27017/
   Remote: mongodb+srv://user:pass@cluster.mongodb.net/
   ```

3. **Test connection**:
   ```bash
   python -c "from pymongo import MongoClient; print(MongoClient('mongodb://localhost:27017/'))"
   ```

4. **Verify permissions**: Ensure MongoDB user has appropriate permissions

---

### No Profiles in Database

**Symptom**: Database Profiles tab is empty

**Solutions**:

1. **Check collection names**:
   - Settings → Database tab
   - Verify collection name: `minute_profiles`

2. **Process a symbol**: 
   - Run pipeline to generate profiles
   - Check logs for errors

3. **Verify MongoDB connection**:
   - Click "Database Profiles" tab
   - Check console for connection errors

---

## API Issues

### Rate Limit Exceeded

**Error**: "API rate limit exceeded" or "HTTP 429"

**Symptoms**:
- Processing suddenly stops
- All workers pause
- Error logged repeatedly

**Solutions**:

1. **Wait for reset**:
   - Per-minute limit: Resets every minute
   - Per-day limit: Resets at midnight UTC
   - Check API dashboard at https://eodhd.com

2. **Reduce workers**:
   - Dashboard → Processing Options
   - Lower "Max Workers" value
   - Default 10 → Try 5-7

3. **Increase chunk size**:
   - Dashboard → Processing Options
   - Increase "Chunk Size" from 30 → 60 days
   - Fewer API calls per symbol

4. **Process fewer symbols**:
   - Process 2-3 symbols instead of 10+

---

### Invalid API Key

**Error**: "401 Unauthorized" or "Invalid API key"

**Solutions**:

1. **Verify API key**:
   - Check `.env` file: `EODHD_API_KEY=xxx`
   - No spaces before/after value

2. **Get new API key**:
   - Visit https://eodhd.com
   - Sign in to dashboard
   - Copy API key

3. **Test API key**:
   ```bash
   python -c "import requests; r = requests.get('https://eodhd.com/api/eod/AAPL', params={'api_token': 'YOUR_KEY', 'fmt': 'json'}); print(r.status_code)"
   ```

---

### No Data Returned

**Error**: API returns empty or no data

**Solutions**:

1. **Check ticker symbol**:
   - Verify ticker exists (e.g., `AAPL` not `APPLE`)
   - Try known symbol first: `AAPL`

2. **Check date range**:
   - Ensure dates are within available data
   - Most data available from 2015+

3. **Check API plan**:
   - Free plan: Limited symbols
   - Paid plan: Full coverage
   - Visit dashboard at https://eodhd.com

---

## Processing Issues

### Processing Hangs or Freezes

**Symptom**: Pipeline gets stuck at specific stage

**Causes & Solutions**:

1. **Feature engineering too slow**:
   - Reduce workers → Settings
   - Check system resources (RAM, CPU)
   - Close other applications

2. **API timeout**:
   - Increase chunk size (fewer batches)
   - Reduce number of workers
   - Check internet connection

3. **Database bottleneck**:
   - Verify MongoDB responsive
   - Check MongoDB logs
   - Restart MongoDB service

---

### Processing Crashes

**Error**: "Pipeline stopped unexpectedly"

**Solutions**:

1. **Check logs**:
   ```
   logs/pipeline_2025-11-28.log  # Check for errors
   ```

2. **Look for specific errors**:
   - Memory error: Reduce workers or symbols
   - API error: Wait for rate limit reset
   - Database error: Check MongoDB

3. **Try with fewer symbols**:
   - Start with 1-2 symbols
   - Gradually add more

4. **Reduce workers**:
   - Default 10 → Try 5
   - Less parallel = more stable

---

### High Memory Usage

**Symptom**: System becomes slow, RAM usage >90%

**Causes & Solutions**:

1. **Too many workers**:
   - Reduce "Max Workers" in settings
   - Formula: Available Cores × 1.5 (max 16)
   - Restart dashboard to reset memory

2. **Too many symbols**:
   - Process fewer symbols at once
   - Process in batches of 5-10

3. **Old cache accumulation**:
   - Clear cache: Cache Manager → "Clear All Cache"
   - Check `~/.pipeline_data_cache/` size

4. **MongoDB memory**:
   - Verify MongoDB index usage
   - Restart MongoDB service

---

## Cache Issues

### Cache Getting Too Large

**Symptom**: Cache folder exceeds 2GB

**Solutions**:

1. **Clear specific symbol**:
   - Cache Manager tab
   - Right-click symbol
   - Select "Delete Cache"

2. **Clear all cache**:
   - Cache Manager tab
   - Click "Clear All Cache"

3. **Check cache location**:
   ```
   ~/.pipeline_data_cache/
   C:\Users\YourUsername\.pipeline_data_cache\
   ```

---

### Cache Not Being Used

**Symptom**: Processing re-downloads data even though cached

**Solutions**:

1. **Verify cache exists**:
   - Cache Manager tab
   - Should show cached symbols

2. **Check date range**:
   - Cache stored by date range
   - Ensure requested range overlaps

3. **Clear metadata**:
   - Delete `.cache_metadata.json`
   - Dashboard will rebuild

---

## UI Issues

### Dashboard Display Problems

**Issue**: Buttons cut off, text garbled, layout broken

**Solutions**:

1. **Reset display**:
   - Close dashboard
   - Delete `.cache`
   - Restart

2. **Change resolution**:
   - Lower screen resolution
   - Or change scaling in Windows

3. **Update PyQt6**:
   ```bash
   pip install --upgrade PyQt6
   ```

---

### Logs Not Showing

**Issue**: Live Logs panel empty or not updating

**Solutions**:

1. **Check logging level**:
   - Settings → Log Level
   - Set to "INFO" or "DEBUG"

2. **Check pipeline running**:
   - Logs only appear during processing
   - Start pipeline to generate logs

3. **Scroll to bottom**:
   - Logs auto-scroll (usually)
   - Try scrolling down manually

---

## Performance Issues

### Slow Feature Engineering

**Symptom**: Feature engineering stage takes 10+ minutes

**Solutions**:

1. **Expected for large datasets**:
   - 1M+ rows: 5-10 minutes normal
   - Vectorization already optimized

2. **Check system resources**:
   - Close other applications
   - Monitor CPU/RAM usage
   - Ensure sufficient disk space

3. **Reduce dataset size**:
   - Use fewer years of history
   - Process fewer symbols at once

---

### Slow API Calls

**Symptom**: Fetching stage takes too long

**Solutions**:

1. **Check internet connection**:
   - Verify stable connection
   - Try downloading file to test speed

2. **Optimize chunk size**:
   - Smaller chunks = more API calls (slower)
   - Larger chunks = fewer calls (faster)
   - Try increasing from 30 → 60 days

3. **Reduce workers**:
   - Less parallel = more stable speeds
   - Reduces load on server

---

## Error Messages

### Common Error Messages & Fixes

| Error | Cause | Fix |
|-------|-------|-----|
| "dictionary changed size" | Cache thread issue | Update to v1.1.1+ |
| "Unable to locate Chromedriver" | Browser automation | Not needed, ignore |
| "ENOMEM" | Out of memory | Close apps, reduce workers |
| "Connection reset" | Network issue | Check internet, retry |
| "Invalid JSON" | Corrupted cache | Clear cache, restart |

---

## When All Else Fails

### Nuclear Options

1. **Clear everything**:
   ```bash
   # Delete cache
   rmdir /s /q %USERPROFILE%\.pipeline_data_cache
   
   # Delete logs
   rmdir /s /q logs
   
   # Reinstall dependencies
   pip install -r requirements.txt --force-reinstall
   ```

2. **Restart MongoDB**:
   ```bash
   # Stop MongoDB
   sc stop MongoDB
   
   # Start MongoDB
   sc start MongoDB
   ```

3. **Restart dashboard**:
   - Close completely
   - Open Task Manager → End any Python processes
   - Restart dashboard

---

## Getting Help

If you're still stuck:

1. **Check logs**: `logs/pipeline_YYYY-MM-DD.log`
2. **Review error message**: Usually descriptive
3. **Search docs**: [Quick Reference](./QUICK_REFERENCE.md)
4. **Try test suite**: `pytest tests/`

---

**Last Updated**: November 28, 2025  
**Version**: 1.1.1

