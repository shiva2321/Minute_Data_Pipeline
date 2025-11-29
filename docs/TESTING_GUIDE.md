# Testing Guide

Comprehensive guide to testing the pipeline and dashboard.

## Unit Tests

### Running All Tests

```bash
cd "D:\development project\Minute_Data_Pipeline"
.venv\Scripts\pytest tests/ -v
```

### Running Specific Test File

```bash
.venv\Scripts\pytest tests/unit/test_feature_engineering.py -v
```

### Running with Coverage

```bash
.venv\Scripts\pytest --cov=dashboard tests/ --cov-report=html
```

---

## Test Structure

```
tests/
├── unit/
│   ├── test_feature_engineering.py    # Feature extraction tests
│   ├── test_rate_limiter.py           # Rate limiting tests
│   └── test_setup.py                  # Configuration tests
├── integration/
│   ├── test_pipeline_integration.py   # Full pipeline tests
│   └── test_mongodb_operations.py     # Database tests
└── fixtures/
    └── sample_data.py                 # Test data
```

---

## Unit Test Coverage

### Feature Engineering Tests

```bash
.venv\Scripts\pytest tests/unit/test_feature_engineering.py -v
```

**Tests covered**:
- Empty dataframe handling
- Single row processing
- Hurst bounds validation
- Entropy non-negativity
- Multi-timeframe integrity
- Label generation
- Predictive labels
- Regime features presence
- No future leakage
- Volatility regime consistency
- Trend regime detection

**Expected**: All tests pass ✅

---

### Rate Limiter Tests

```bash
.venv\Scripts\pytest tests/unit/test_rate_limiter.py -v
```

**Tests covered**:
- Per-minute throttling
- Daily quota enforcement
- Exponential backoff
- Backoff reset on success

**Expected**: All tests pass ✅

---

### Setup & Configuration Tests

```bash
.venv\Scripts\pytest tests/unit/test_setup.py -v
```

**Tests covered**:
- Import verification
- Configuration validation
- Data structure creation
- MongoDB connection

**Expected**: All tests pass ✅

---

## Integration Tests

### Pipeline Integration

```bash
.venv\Scripts\pytest tests/integration/test_pipeline_integration.py -v
```

**Requires**:
- MongoDB running locally
- EODHD API key in `.env`
- Internet connection

**Tests covered**:
- Full pipeline lifecycle (fetch → engineer → store)
- Single symbol processing
- Multiple symbol processing (parallel)
- Incremental updates

**Duration**: 5-10 minutes

---

## Manual Testing

### 1. Dashboard Launch

```bash
run_dashboard.bat
```

**Verification**:
- ✅ Dashboard window appears
- ✅ All tabs visible (Pipeline Control, Database Profiles, Settings, Cache Manager)
- ✅ No error messages in console

---

### 2. Single Symbol Processing

**Steps**:
1. Enter ticker: `AAPL`
2. Set History: `2 years`
3. Click "Start Pipeline"
4. Monitor progress

**Verification**:
- ✅ Queue table shows AAPL
- ✅ Status progresses: Fetching → Engineering → Storing
- ✅ Progress bar fills to 100%
- ✅ Logs show completion message
- ✅ Profile appears in Database Profiles tab

**Duration**: 2-5 minutes

---

### 3. Multiple Symbol Processing

**Steps**:
1. Enter tickers: `AAPL,MSFT,GOOGL`
2. Set History: `1 year`
3. Click "Start Pipeline"
4. Monitor progress

**Verification**:
- ✅ All 3 symbols appear in queue
- ✅ All process in parallel (different progress values)
- ✅ All complete successfully
- ✅ All 3 profiles appear in Database Profiles tab

**Duration**: 3-8 minutes

---

### 4. Cache Management

**Steps**:
1. Process AAPL (creates cache)
2. Go to Cache Manager tab
3. Verify AAPL is cached
4. Right-click AAPL
5. Select "Delete Cache"
6. Verify AAPL removed from cache

**Verification**:
- ✅ Cache Manager shows cached symbols
- ✅ Date ranges displayed correctly
- ✅ Context menu works
- ✅ Symbol deleted after right-click

---

### 5. Incremental Update

**Steps**:
1. Process AAPL (2 years)
2. Change to Incremental mode
3. Process AAPL again
4. Monitor logs

**Verification**:
- ✅ Second run completes faster
- ✅ Logs show "Incremental update"
- ✅ Only new data fetched
- ✅ Profile updated with new data

---

### 6. API Rate Limiting

**Steps**:
1. Set Max Workers: 1
2. Process multiple symbols: `AAPL,MSFT,GOOGL,NVDA,TSLA`
3. Monitor API gauge in top bar

**Verification**:
- ✅ API gauge shows current usage
- ✅ Gauge updates in real-time
- ✅ No "rate limit exceeded" errors
- ✅ Processing continues smoothly

---

### 7. Database Connection

**Steps**:
1. Click "Database Profiles" tab
2. Verify profiles load
3. Click Settings tab
4. Verify MongoDB URI correct
5. Click "Test Connection"

**Verification**:
- ✅ Profiles table populated
- ✅ Connection test succeeds
- ✅ No connection errors in console

---

## Performance Benchmarks

### Expected Performance Targets

| Task | Expected Time | Tolerance |
|------|---------------|-----------|
| Feature Engineering (1M rows) | 2-3 min | ±30 sec |
| Single Symbol (2 years) | 2-5 min | ±1 min |
| 3 Symbols Parallel (1 year) | 3-8 min | ±2 min |
| Cache Hit | <1 sec | ±0.5 sec |
| Dashboard Launch | <5 sec | ±2 sec |

---

## Stress Testing

### High Volume Processing

```bash
# Process 10+ symbols to test worker pool
```

**Settings**:
- Workers: 10
- Symbols: 10+ (e.g., top 10 tech stocks)
- History: 2 years

**Monitoring**:
- CPU usage: Should stay <80%
- Memory: Should not exceed available RAM
- API gauge: Should respect limits
- All symbols: Should complete successfully

**Expected**: All symbols process without crashes

---

### Long Duration

```bash
# Process symbols with 5-10 years history
```

**Settings**:
- Workers: 10
- Symbols: 5-10
- History: 10 years
- Chunk: 30 days

**Monitoring**:
- Should not crash after extended run
- Logs should show steady progress
- No memory leaks (check Task Manager)

**Expected**: Completes successfully

---

### Cache Scaling

**Steps**:
1. Process 20 different symbols
2. Verify cache grows to ~2GB
3. Add 21st symbol

**Expected**:
- ✅ Cache maintains 2GB limit
- ✅ Oldest entries removed
- ✅ New data cached
- ✅ System stable

---

## Regression Testing

### v1.1.1 Specific Tests

```bash
# Dictionary iteration thread-safety
.venv\Scripts\pytest tests/unit/test_cache_operations.py -v

# Datetime parsing
.venv\Scripts\pytest tests/unit/test_datetime_handling.py -v

# Parallel processing stability
.venv\Scripts\pytest tests/integration/test_parallel_processing.py -v
```

---

## Smoke Testing (Pre-Deployment)

Quick checklist before deployment:

- [ ] Dashboard launches without errors
- [ ] Single symbol processes completely
- [ ] 3+ symbols process in parallel
- [ ] Cache Manager shows cached symbols
- [ ] Database Profiles shows stored profiles
- [ ] Settings saves correctly
- [ ] No critical errors in logs
- [ ] Rate limiting works
- [ ] All unit tests pass
- [ ] Integration tests pass (if time permits)

---

## Test Data

### Sample Symbols for Testing

```
Tech stocks:     AAPL, MSFT, GOOGL, NVDA, TSLA
Finance stocks:  JPM, BAC, C, BLK, GS
Healthcare:      JNJ, PFE, MRNA, UNH, ABBV
```

### Test Histories

- **Quick test**: 1 year (5 min)
- **Normal test**: 2 years (5-10 min)
- **Full test**: 5-10 years (10-30 min)

---

## Continuous Integration

### Running Tests Locally (Before Commit)

```bash
# 1. Run all tests
.venv\Scripts\pytest tests/ -v

# 2. Check coverage
.venv\Scripts\pytest --cov=dashboard tests/

# 3. Run specific test suite
.venv\Scripts\pytest tests/unit/ -v

# 4. If all pass, safe to commit
git add .
git commit -m "commit message"
git push
```

---

## Troubleshooting Tests

### Test Fails with MongoDB Error

```bash
# Start MongoDB
mongod --dbpath "C:\data\db"

# Then re-run tests
.venv\Scripts\pytest tests/integration/ -v
```

### Test Fails with API Error

```bash
# Verify API key in .env
# Wait for rate limit to reset
# Try again in 1 minute
```

### Test Fails with Timeout

```bash
# Increase timeout
.venv\Scripts\pytest tests/ -v --timeout=300
```

---

## Test Results Reporting

### Generate HTML Report

```bash
.venv\Scripts\pytest tests/ --html=report.html --self-contained-html
# Open report.html in browser
```

### View Coverage Report

```bash
.venv\Scripts\pytest --cov=dashboard --cov-report=html tests/
cd htmlcov
start index.html
```

---

## Quality Metrics

### Target Metrics

- **Test Coverage**: >80%
- **All Unit Tests**: PASS ✅
- **All Integration Tests**: PASS ✅
- **Performance Benchmarks**: Met ✅
- **No Critical Bugs**: Verified ✅

---

**Last Updated**: November 28, 2025  
**Version**: 1.1.1

