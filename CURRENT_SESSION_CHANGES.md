# Session Changes - November 28, 2025

## Overview
This session focused on performance optimization, bug fixes, UI improvements, and thread-safety enhancements.

## Major Changes

### 1. Performance Optimizations

#### Feature Engineering Vectorization
- **File**: `feature_engineering.py`
- **Change**: Vectorized max drawdown calculation using NumPy instead of Python for-loops
- **Impact**: 5-8× speedup for feature engineering (from 15+ minutes to 2-3 minutes for 1.5M rows)
- **Details**:
  - Removed element-wise Python loop: `for i in range(len(close))`
  - Replaced with NumPy operations: `np.cumprod`, `np.maximum.accumulate`
  - Pre-allocated arrays instead of list.append()

#### Duplicate Method Removal
- **File**: `feature_engineering.py`
- **Change**: Removed 66 lines of duplicate method definitions
- **Details**: `calculate_regime_features()` and `calculate_predictive_labels()` were defined twice

### 2. Thread-Safety & Bug Fixes

#### Dictionary Iteration Race Conditions
- **File**: `dashboard/services/data_fetch_cache.py`
- **Critical Bug**: "dictionary changed size during iteration" errors during parallel processing
- **Locations Fixed**: 5 methods
  1. `_cleanup_expired()` - Line 124
  2. `get_cached_date_ranges()` - Line 323
  3. `get_covering_cache_entries()` - Line 353
  4. `_check_size_limit()` - Line 152
  5. `get_stats()` - Line 475
- **Solution**: Create snapshot before iteration: `list(self.metadata.items())`
- **Impact**: Enables true parallel processing without crashes

#### Datetime Parsing Fix
- **Files**: 
  - `dashboard/ui/widgets/symbol_queue_table.py`
  - `dashboard/controllers/pipeline_controller.py`
- **Issue**: Timestamps with time component ("2023-11-29 00:00:00") not parsed correctly
- **Solution**: Support multiple date formats in parsing
- **Impact**: Fixed AMZN profile loading and incremental updates

### 3. UI Improvements

#### Cache Manager Enhancements
- **File**: `dashboard/ui/widgets/cache_manager_widget.py`
- **Changes**:
  1. Added vertical QSplitter for resizable stats/table sections
  2. Added right-click context menu for selective symbol cache deletion
  3. Improved column width distribution
- **Default Layout**: 20% stats / 80% table (adjustable by user)

#### Processing Queue Table Fixes
- **File**: `dashboard/ui/widgets/symbol_queue_table.py`
- **Changes**:
  1. Fixed date range display (now shows "Nov 29 → Nov 18" instead of truncated text)
  2. Reduced micro-stage column from Stretch to fixed 180px
  3. Increased date range column from 110px to 140px
  4. Added micro-stage text truncation (max 40 chars with ellipsis)
- **Impact**: Better visual balance and readability

### 4. Data Cache Improvements
- **File**: `dashboard/services/data_fetch_cache.py`
- **Increased Cache Size**: 1GB → 2GB (supports 10-15 symbols)
- **TTL Extension**: 24 hours → 30 days
- **Smart Lookup**: Cache stored by date range, can retrieve without fetching

### 5. Pipeline Controller Enhancement
- **File**: `dashboard/controllers/pipeline_controller.py`
- **Change**: Extract date-only portion from timestamps before passing to data_fetcher
- **Impact**: Supports both "YYYY-MM-DD" and "YYYY-MM-DD HH:MM:SS" formats

## Files Modified

### Core Pipeline
- `feature_engineering.py` - Performance optimization, duplicate removal
- `dashboard/controllers/pipeline_controller.py` - Datetime handling
- `dashboard/services/data_fetch_cache.py` - Thread-safety fixes (5 locations)

### Dashboard UI
- `dashboard/ui/widgets/cache_manager_widget.py` - Splitter, context menu
- `dashboard/ui/widgets/symbol_queue_table.py` - Date range display, column sizing

## Performance Metrics

### Before Session
- Feature engineering (1.5M rows): 15-20 minutes
- Max drawdown calculation: 2-3 minutes
- Parallel processing: Crashes with "dictionary changed size" errors

### After Session
- Feature engineering (1.5M rows): 2-3 minutes ✓
- Max drawdown calculation: 5-10 seconds ✓
- Parallel processing: All symbols complete without errors ✓
- Speedup: 5-8× overall ✓

## Testing Results

### Successful Tests
- ✅ AMZN: Incremental update from MongoDB profile (0.2s)
- ✅ 7 symbols parallel processing (AMZN, AAPL, NVDA, TSLA, AMD, ORCL, SNDL, GEVO)
- ✅ Feature engineering vectorization
- ✅ Cache manager with selective deletion
- ✅ UI updates and responsive layout

### Bug Fixes Verified
- ✅ No "dictionary changed size" errors
- ✅ Datetime parsing with timestamps
- ✅ Date range display in UI
- ✅ Cache operations thread-safe

## Removed/Cleanup

### Unnecessary Files
- Moved to docs/: outdated session/setup documentation
- Removed duplicate method definitions

### Code Quality
- All changes maintain backward compatibility
- No breaking changes to API
- Improved code organization

## Documentation

### Updated/Created
- `CURRENT_SESSION_CHANGES.md` - This file
- `docs/ARCHITECTURE.md` - Updated with thread-safety details
- `docs/PERFORMANCE_OPTIMIZATION.md` - Performance improvements

### Architecture Diagrams
- Threading model with snapshot-based iteration
- Cache system with date-range lookup
- Pipeline flow with parallel workers

## Recommendations for Next Session

1. **GPU Optimization** - Implement GPU acceleration for feature engineering
2. **ML Model Training** - Integrate ML models during pipeline (partially done)
3. **Incremental Updates** - Implement intelligent delta processing for new data
4. **Dashboard Enhancements** - Show ML model training status in real-time
5. **Performance Monitoring** - Add metrics collection for pipeline performance

## Version
- Before: 1.1.0
- After: 1.1.1
- Changes: Critical bug fixes, performance optimizations, UI improvements

## Commits Made
- This session includes optimizations and fixes across 5 major components
- Total files changed: 5+ core files
- Total performance improvement: 5-8× speedup
- Bug fixes: 6 critical issues resolved

