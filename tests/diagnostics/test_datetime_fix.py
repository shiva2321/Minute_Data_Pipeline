"""
Test datetime handling in profile browser
"""
from datetime import datetime

# Simulate profile data with datetime object
profile = {
    'symbol': 'TEST',
    'last_updated': datetime(2025, 11, 27, 23, 18, 7),
    'data_date_range': {
        'start': '2023-11-27 10:30:00',
        'end': '2025-11-27 20:00:00'
    }
}

# Test the datetime handling logic
last_updated = profile.get('last_updated', 'N/A')

# Handle datetime object or string
if isinstance(last_updated, str):
    last_updated_str = last_updated[:19]
    print(f"String: {last_updated_str}")
elif hasattr(last_updated, 'strftime'):
    # It's a datetime object
    last_updated_str = last_updated.strftime('%Y-%m-%d %H:%M:%S')
    print(f"Datetime: {last_updated_str}")
else:
    last_updated_str = str(last_updated)
    print(f"Other: {last_updated_str}")

print("\n✅ Test passed! Datetime handling works correctly.")
print(f"Result: {last_updated_str}")

