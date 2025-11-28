# Minute Data Pipeline & Desktop Dashboard

## Overview
This project provides a minute-level stock market data pipeline plus a native PyQt6 desktop dashboard for controlling, monitoring, and editing processed symbol profiles.

Core capabilities:
- Parallel per-symbol processing (each worker completes full lifecycle independently)
- Adaptive per-worker rate limiting (minute & daily quotas)
- 200+ engineered features (technical, statistical, microstructure, risk, multi-timeframe)
- MongoDB persistence of rich profile objects
- Real-time dashboard: queue table, micro-stage progress, logs, API usage, ETA
- Profile browser & editor with JSON view and feature tabs
- Incremental vs full historical backfill (30-day chunk strategy, adjustable years / up to 30 or full history)
- Persistent API usage counters across sessions
- Email alerts on critical errors (optional, with screenshot)

## Architecture
```
dashboard/
  main.py                # Entry point
  ui/                    # Panels and widgets
  controllers/           # Pipeline & database controllers
  services/              # Metrics, email alerts
  utils/                 # Signals, theme, helpers
pipeline.py              # Core pipeline orchestrator
feature_engineering.py   # Feature engineering engine
data_fetcher.py          # EODHD API integration & historical fetch logic
mongodb_storage.py       # MongoDB profile persistence
config.py                # Settings / env configuration
```

## Running the Dashboard (Windows)
```
run_dashboard.bat
```
The batch script will activate the virtual environment, ensure dependencies, and launch the UI. On normal close it reports "Dashboard closed normally." Errors display exit code.

## Email Alerts Configuration
Set in Settings tab or via environment variables for better security:
- PIPELINE_ALERT_EMAIL
- PIPELINE_ALERT_PASSWORD
These override sender email & password fields if present.
On ERROR / CRITICAL log events a single alert (rate-limited ~5 min) is sent with recent message and PNG screenshot.

## Incremental vs Full History
- Full backfill: Fetches history in 30-day batches up to selected years (or entire available history).
- Incremental update: Only fetches new data since last stored end date and recomputes features.

## Feature Tabs Mapping
If specific sections (price_features, volume_features, volatility_features) are absent, they are mapped to:
- Price -> statistical_features + performance_metrics
- Volume -> microstructure_features
- Volatility -> risk_metrics + performance_metrics

## Persistent API Usage
Daily API call counts persist via cache store and reset automatically when a new day starts.

## Roadmap / Next Enhancements
- Fine-grained feature engineering progress callbacks
- Re-process dialog (full vs incremental with preview)
- System tray & desktop notifications
- Advanced company universe management (auto-refresh listings)

## Requirements
See `requirements.txt` (ensure PyQt6, pymongo, requests, loguru, scipy, scikit-learn etc.).

## Security Notes
Use app-specific passwords (e.g., Gmail App Password) for SMTP. Avoid storing real credentials in plain text; prefer environment variables.

## Troubleshooting
- If dashboard shows no profiles: verify MongoDB connection & collection names in Settings.
- If rate limits are hit early: reduce workers or increase chunk days.
- Email not sent: confirm SMTP server/port and that env vars override UI fields correctly.

## License
Internal / Proprietary (update as needed).
