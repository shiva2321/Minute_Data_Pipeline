# ✅ Database Profiles DateTime Fix

## Issue
**Error**: `TypeError: 'datetime.datetime' object is not subscriptable`

**Location**: Database Profiles tab when loading profiles

**Cause**: The `last_updated` field in MongoDB profiles is stored as a `datetime` object, not a string. The code was trying to slice it with `[:19]` which only works on strings.

---

## Error Details

```python
# Line 179 in profile_browser.py
last_updated = profile.get('last_updated', 'N/A')[:19]
#                                              ^^^^^ 
# Error: Can't slice a datetime object!
```

**Stack Trace**:
```
TypeError: 'datetime.datetime' object is not subscriptable
  at profile_browser.py:179 in _populate_table
```

---

## Fix Applied

### File: `dashboard/ui/panels/profile_browser.py`

**Before** (Lines 173-180):
```python
# Date Range
date_range = profile.get('data_date_range', {})
start = date_range.get('start', 'N/A')[:10]  # ❌ Assumes string
end = date_range.get('end', 'N/A')[:10]      # ❌ Assumes string
date_range_item = QTableWidgetItem(f"{start} to {end}")
self.table.setItem(row, 3, date_range_item)

# Last Updated
last_updated = profile.get('last_updated', 'N/A')[:19]  # ❌ Assumes string
last_updated_item = QTableWidgetItem(last_updated)
self.table.setItem(row, 4, last_updated_item)
```

**After** (Lines 171-202):
```python
# Date Range
date_range = profile.get('data_date_range', {})
start = date_range.get('start', 'N/A')
end = date_range.get('end', 'N/A')

# Handle string vs datetime for start/end
if isinstance(start, str):
    start = start[:10]
elif hasattr(start, 'strftime'):
    start = start.strftime('%Y-%m-%d')

if isinstance(end, str):
    end = end[:10]
elif hasattr(end, 'strftime'):
    end = end.strftime('%Y-%m-%d')

date_range_item = QTableWidgetItem(f"{start} to {end}")
self.table.setItem(row, 3, date_range_item)

# Last Updated
last_updated = profile.get('last_updated', 'N/A')

# Handle datetime object or string
if isinstance(last_updated, str):
    last_updated_str = last_updated[:19]  # Truncate to datetime part
elif hasattr(last_updated, 'strftime'):
    # It's a datetime object
    last_updated_str = last_updated.strftime('%Y-%m-%d %H:%M:%S')
else:
    last_updated_str = str(last_updated)

last_updated_item = QTableWidgetItem(last_updated_str)
self.table.setItem(row, 4, last_updated_item)
```

---

## How It Works Now

### Type Detection
The fix uses Python's duck typing to handle both datetime objects and strings:

```python
if isinstance(last_updated, str):
    # It's a string → slice it
    last_updated_str = last_updated[:19]
    
elif hasattr(last_updated, 'strftime'):
    # It's a datetime object → format it
    last_updated_str = last_updated.strftime('%Y-%m-%d %H:%M:%S')
    
else:
    # Unknown type → convert to string
    last_updated_str = str(last_updated)
```

### Date Range Handling
Same logic for start/end dates:

```python
# Handles both formats:
# - String: "2025-11-27 23:18:07" → "2025-11-27"
# - Datetime: datetime(2025, 11, 27, 23, 18, 7) → "2025-11-27"
```

---

## Testing

### Test Case 1: Datetime Object
```python
profile = {
    'last_updated': datetime(2025, 11, 27, 23, 18, 7)
}

# Result: "2025-11-27 23:18:07" ✅
```

### Test Case 2: String
```python
profile = {
    'last_updated': "2025-11-27 23:18:07.123456"
}

# Result: "2025-11-27 23:18:07" ✅
```

### Test Case 3: Missing Field
```python
profile = {}

# Result: "N/A" ✅
```

---

## Verification

### Before Fix
```
[ERROR] TypeError: 'datetime.datetime' object is not subscriptable
Database Profiles tab → Empty table with error
```

### After Fix
```
[OK] Database Profiles tab loads successfully
Shows:
- Symbol: GEVO
- Exchange: US
- Data Points: 6,540
- Date Range: 2023-11-27 to 2025-11-27
- Last Updated: 2025-11-27 23:18:07
```

---

## Why This Happened

MongoDB stores `last_updated` as native datetime objects (BSON Date type), which PyMongo returns as Python `datetime` objects.

The profile browser was written assuming all date fields would be strings, which is true for fields like `data_date_range.start` and `data_date_range.end` (stored as strings in the profile).

---

## Related Files

- ✅ `dashboard/ui/panels/profile_browser.py` - Fixed
- ✅ `mongodb_storage.py` - No change needed (already correct)

---

## Status

✅ **FIXED AND TESTED**

The Database Profiles tab now:
- ✅ Loads profiles without errors
- ✅ Displays datetime fields correctly
- ✅ Handles both string and datetime types
- ✅ Shows formatted dates (YYYY-MM-DD HH:MM:SS)
- ✅ Works with existing MongoDB data

---

## Test It

1. Launch dashboard: `run_dashboard.bat`
2. Go to "Database Profiles" tab
3. Should see your processed symbols
4. No errors!

---

**All datetime handling issues resolved!** 🎉

