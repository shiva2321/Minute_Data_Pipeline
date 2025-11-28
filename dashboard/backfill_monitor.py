import streamlit as st
import pandas as pd
import json
from pathlib import Path
from mongodb_storage import MongoDBStorage
from config import settings

st.set_page_config(page_title="Backfill Monitor", layout="wide")

st.title("\ud83d\udcca Backfill Progress Monitor")

storage = MongoDBStorage(settings.mongodb_uri, settings.mongodb_database, settings.mongodb_collection)

results_dir = Path('logs')
result_files = sorted(results_dir.glob('backfill_results_*.json'), reverse=True)

if result_files:
    with open(result_files[0]) as f:
        latest_results = json.load(f)
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Symbols", latest_results['summary']['total'])
    with col2:
        st.metric("Success", latest_results['summary']['success'])
    with col3:
        st.metric("Failed", latest_results['summary']['failed'])
    with col4:
        st.metric("Skipped", latest_results['summary']['skipped'])
    st.subheader("Symbol Details")
    symbols_data = []
    for symbol, info in latest_results['symbols'].items():
        profile = storage.get_profile(symbol)
        if profile:
            backfill = profile.get('backfill_metadata', {})
            symbols_data.append({
                'Symbol': symbol,
                'Status': info['status'],
                'Data Points': info.get('data_points', 0),
                'Date Range': f"{info.get('date_range', {}).get('start', 'N/A')} to {info.get('date_range', {}).get('end', 'N/A')}",
                'API Calls': backfill.get('api_calls_used', 0),
                'Duration (s)': backfill.get('fetch_duration_seconds', 0)
            })
    df = pd.DataFrame(symbols_data)
    st.dataframe(df, use_container_width=True)
    st.subheader("API Usage")
    if not df.empty:
        st.bar_chart(df.set_index('Symbol')['API Calls'])
else:
    st.warning("No backfill results found. Run a backfill first.")

st.subheader("Recent Logs")
log_file = Path('logs/backfill.log')
if log_file.exists():
    with open(log_file) as f:
        logs = f.readlines()
    st.text_area("Log Output", ''.join(logs[-50:]), height=300)

