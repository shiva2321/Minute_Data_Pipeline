import requests
from datetime import datetime, timedelta
from config import settings

def test_api_response():
    symbol = "AAPL"
    end_date = datetime.now()
    start_date = end_date - timedelta(days=1)
    url = f"{settings.eodhd_base_url}/intraday/{symbol}.US"
    params = {
        'api_token': settings.eodhd_api_key,
        'interval': '1m',
        'from': int(start_date.timestamp()),
        'to': int(end_date.timestamp()),
        'fmt': 'json'
    }
    print(f"Testing API call for {symbol}...")
    print(f"URL: {url}")
    print(f"Date range: {start_date} to {end_date}")
    resp = requests.get(url, params=params, timeout=30)
    print(f"\nStatus code: {resp.status_code}")
    if resp.status_code == 200:
        try:
            data = resp.json()
        except Exception as e:
            print(f"JSON parse error: {e}")
            print(resp.text[:500])
            return
        print(f"Response type: {type(data)}")
        print(f"Number of records: {len(data) if isinstance(data, list) else 'N/A'}")
        if isinstance(data, list) and data:
            print("\nFirst record:")
            print(data[0])
            print("\nKeys in first record:")
            print(list(data[0].keys()))
    else:
        print(f"Error: {resp.text[:500]}")

if __name__ == '__main__':
    test_api_response()
