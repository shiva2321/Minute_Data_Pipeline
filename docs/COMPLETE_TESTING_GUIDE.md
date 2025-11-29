# Complete Testing Guide - Phase 2

**Date**: November 28, 2025  
**Last Updated**: After ML Training Implementation

---

## Pre-Testing Setup

### 1. Verify Dependencies
```bash
cd "D:\development project\Minute_Data_Pipeline"
.venv\Scripts\pip list | grep -E "scikit-learn|yfinance|pymongo|pandas"
```

Expected output:
```
pandas >=2.1.0 ✓
numpy >=1.24.0 ✓
scikit-learn >=1.3.0 ✓
yfinance >=0.2.32 ✓
pymongo >=4.5.0 ✓
```

### 2. Verify MongoDB Running
```bash
mongosh
> use Entities
> show collections
```

Should show collections (or will be created automatically).

### 3. Start Dashboard
```bash
.venv\Scripts\python dashboard/main.py
```

---

## Test Scenario 1: Full History Processing (New Symbol)

### Setup
- Symbol: `AAPL`
- History Years: **All Available**
- Processing Mode: Full Rebuild

### Expected Behavior

#### At 10% (Initializing)
```
Log: "AAPL: Fetching establishment date for all available data"
Log: "AAPL: Attempting to fetch IPO date from EODHD..."
Log: "AAPL: ✓ Found IPO date from EODHD: 1980-12-12"
Micro-stage: "Range: 1980-12-12 to 2025-11-28 (45yr)"
```

#### At 1-45% (Fetching Batches)
```
Micro-stage: "Fetch batch 1/550"
Micro-stage: "Fetch batch 2/550"
Data Pts: Updated progressively
Duration: Growing
```

#### At 48% (Fetch Complete)
```
Micro-stage: "Retrieved 1,854,961 data points"
Log: "AAPL: Fetched 1,854,961 data points (1980-01-03 to 2025-11-28)"
Data Pts: 1,854,961
```

#### At 50-68% (Feature Engineering)
```
Micro-stage progression:
52% - "Technical: Moving Averages"
54% - "Technical: Bollinger Bands"
56% - "Technical: RSI"
58% - "Technical: MACD"
60% - "Technical: ATR & Stochastic"
62% - "Technical: Volume & Momentum"
64% - "Statistical: Basic stats"
68% - "Features complete"
```

#### At 71-75% (ML Training) ✨ NEW
```
71% - Status: "ML Training"
      Micro-stage: "Initializing ML trainer"
      
55% - Progress: 55% (inside ML Training)
      Log: "AAPL: Preparing training data"
      
60% - Progress: 60%
      Log: "AAPL: Training regression model"
      
65% - Progress: 65%
      Log: "AAPL: Training classification model"
      
70% - Progress: 70%
      Log: "AAPL: Training gradient boosting model"
      
72% - Progress: 72%
      Log: "AAPL: Regression model trained - R²: X.XXX"
      Log: "AAPL: Classification model trained - Accuracy: X.XXX"
      Log: "AAPL: Gradient Boosting model trained - R²: X.XXX"
```

#### At 85% (Storing) ✨ NEW
```
Micro-stage: "Saving profiles"
Log: "AAPL: Saved 3 profile types (original, ML, statistical)"
```

#### At 100% (Complete)
```
Micro-stage: "Done"
Log: "SUCCESS: AAPL completed successfully"
Status: ✓ Success (green checkmark)
Duration: ~3 minutes total
```

### MongoDB Verification

```bash
mongosh
> use Entities

# Check all 3 profiles
> db.company_profiles.findOne({symbol: "AAPL"})
> db.ml_profiles.findOne({symbol: "AAPL"})
> db.statistical_profiles.findOne({symbol: "AAPL"})
```

**Expected Output**:

```javascript
// company_profiles
{
  "symbol": "AAPL",
  "data_points_count": 1854961,
  "technical_indicators": {...},
  "risk_metrics": {...}
}

// ml_profiles ✨ NEW
{
  "symbol": "AAPL",
  "profile_type": "ml",
  "models_trained": ["regression_rf", "classification_rf", "regression_gb"],
  "metrics": {
    "regression_rf": {"r2": 0.75, "rmse": 0.0145, ...},
    "classification_rf": {"accuracy": 0.62, "precision": 0.63, ...},
    "regression_gb": {"r2": 0.78, "rmse": 0.0128, ...}
  }
}

// statistical_profiles ✨ NEW
{
  "symbol": "AAPL",
  "profile_type": "statistical",
  "features": {
    "technical_indicators": {...},
    "statistical_features": {...},
    "risk_metrics": {...}
  }
}
```

---

## Test Scenario 2: Incremental Update (Existing Symbol)

### Setup
- Symbol: `AAPL` (already processed in Scenario 1)
- History Years: **2** (only new data)
- Processing Mode: Incremental

### Expected Behavior

#### Processing
```
Micro-stage: "Updating existing profile"
Log: "AAPL: Incremental update - 390 new points, retrain=yes"
Time: ~15 seconds (vs 3 minutes for full)
```

#### Models Decision
```
New data points: 390
Threshold: 100 points
Retrain triggered: YES (390 > 100)
```

#### Result
```
- Original profile updated
- ML profile retrained
- Statistical profile updated
- Efficiency: ~90% faster
```

### MongoDB Verification

```bash
> db.ml_profiles.findOne({symbol: "AAPL"})
# trained_at should be recent timestamp
# metrics should be updated

> db.statistical_profiles.findOne({symbol: "AAPL"})
# created_at should be recent
# new features reflected
```

---

## Test Scenario 3: Multiple Symbols with Parallel Processing

### Setup
- Symbols: `AAPL, MSFT, GOOGL, AMZN, NVDA`
- History Years: **2**
- Max Workers: **10**
- Processing Mode: Full Rebuild

### Expected Behavior

#### Parallel Processing
```
Processing Queue shows:
1. AAPL    - Fetching (44%)
2. MSFT    - Engineering (60%)
3. GOOGL   - ML Training (75%)
4. AMZN    - Storing (90%)
5. NVDA    - Storing (85%)
```

#### Total Time
```
Expected: ~5 minutes (not 15 minutes)
5 symbols × 3 min each = 15 min sequential
But parallel: only 5 × 3 = 5 min for longest
```

#### Completion
```
All 5 symbols complete within 5-7 minutes
Each symbol has 3 profiles saved
Total documents in MongoDB: 15 (5 × 3 types)
```

---

## Test Scenario 4: yfinance Fallback

### Setup
- Symbol: `ORCL` (Oracle - older company)
- History Years: **All Available**

### Expected Behavior

#### If EODHD Works
```
Log: "ORCL: ✓ Found IPO date from EODHD: 1986-03-12"
```

#### If EODHD Fails (or no data)
```
Log: "ORCL: EODHD fundamental data unavailable: ..."
Log: "ORCL: Attempting to fetch IPO date from yfinance (fallback)..."
Log: "ORCL: ✓ Found first trade date from yfinance: 1986-03-12"
Micro-stage: "Range: 1986-03-12 to 2025-11-28 (39yr)"
```

#### If Both Fail
```
Log: "ORCL: yfinance fallback failed: ..."
Log: "ORCL: ✗ OPTION SELECTED: No establishment date found, using 10 years as DEFAULT"
Micro-stage: "Default 10yr (no IPO date)"
```

---

## Test Scenario 5: Date Range Verification

### Setup
- Symbol: `TSLA`
- History Years: **5**

### Expected Timing

#### At 10% (Should see date range immediately)
```
Micro-stage: "Range: 2020-11-28 to 2025-11-28 (5yr)"
Log: "TSLA: Date range: 2020-11-28 to 2025-11-28 (~1830 days)"
```

#### At 48% (After fetching, should see actual data)
```
Micro-stage: "Retrieved 710,700 data points"
Log: "TSLA: Fetched 710,700 data points (2020-06-29 to 2025-11-28)"
```

**Verification**: Both timestamps should match expected range.

---

## Test Scenario 6: ML Model Quality

### Setup
- Symbol: Any (check metrics after training)
- Look at logs or MongoDB query

### Expected Metrics

```javascript
Regression Models:
- R² score: 0.60-0.85 (higher is better)
- RMSE: 0.01-0.03

Classification Models:
- Accuracy: 50-65% (better than random 50%)
- Precision: 50-70%
- Recall: 50-70%
- F1: 50-65%
```

**Query in MongoDB**:
```bash
> db.ml_profiles.findOne({symbol: "AAPL"})
# Check metrics in .models.metrics
```

---

## Troubleshooting

### Issue 1: ML Training Stage Doesn't Appear

**Check**:
1. Logs show "ML Training" at 71%?
2. No error messages?

**Solution**:
```bash
# Check if sklearn installed
.venv\Scripts\pip show scikit-learn

# If not installed
.venv\Scripts\pip install scikit-learn>=1.3.0
```

### Issue 2: ML Profiles Not in MongoDB

**Check**:
```bash
mongosh
> db.ml_profiles.countDocuments()  # Should be > 0
> db.statistical_profiles.countDocuments()
```

**Solution**:
1. Check logs for errors during save
2. Verify MongoDB connection
3. Verify write permissions

### Issue 3: Incremental Update Not Triggered

**Check**:
1. Logs show "Incremental" or "no new data"?
2. Set History Years to same value as before

**Solution**:
1. Make sure symbol was processed before
2. Add new data to source (wait a day or mock)
3. Check MongoDB for existing profile

### Issue 4: Date Range Shows Later Than 10%

**Check**:
1. Progress: Is it at 48% instead of 10%?

**Solution**:
1. Restart dashboard
2. Clear pipeline state
3. Check pipeline_controller.py integration

---

## Performance Benchmarks

### Expected Times

| Operation | Time | Symbols |
|-----------|------|---------|
| Full backfill (25 years) | 3 min | 1 |
| Full backfill (5 years) | 45 sec | 1 |
| Daily incremental | 15 sec | 1 |
| Parallel 5 symbols | 5-7 min | 5 |
| Parallel 10 symbols | 5-7 min | 10 |

### Expected Logs

Full processing should show ~50+ log lines:
- Initialization
- Date range detection
- Fetching batches
- Feature engineering stages
- ML training stages
- Storage operations
- Completion

---

## Sign-Off Checklist

- [ ] Dashboard starts without errors
- [ ] Date range appears at 10%
- [ ] ML Training stages visible (71-75%)
- [ ] All models train successfully
- [ ] 3 profile types appear in MongoDB
- [ ] Incremental updates work (~90% faster)
- [ ] Logs show all progress stages
- [ ] Parallel processing works (5+ symbols)
- [ ] Metrics look reasonable (R²>0.6)
- [ ] No data loss or corruption

---

## Success Criteria

✅ **PASS** if:
1. All 3 profile types saved for each symbol
2. ML training completes without errors
3. Progress shows 71-75% for ML stage
4. Date range shown at 10%
5. Incremental updates are faster
6. Logs show detailed progress
7. Models have reasonable metrics

---

## Reporting Issues

If you encounter issues, provide:
1. Full log output from console
2. MongoDB query results
3. Which test scenario failed
4. Expected vs actual behavior
5. Timestamp of issue

---

**Testing Status**: READY  
**Last Verified**: Nov 28, 2025  
**Next Action**: Run Test Scenario 1

