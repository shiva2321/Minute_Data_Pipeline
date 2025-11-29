# Minute Data Pipeline & Desktop Dashboard

**Version 1.1.1** | Production Ready | Last Updated: November 28, 2025

A professional-grade minute-level stock market data pipeline with a native PyQt6 desktop dashboard for controlling, monitoring, and analyzing symbol profiles.

---

## 🚀 Quick Start

### 1. Installation (5 minutes)
```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
# Edit .env with your EODHD API key
```

### 2. Run Dashboard
```bash
run_dashboard.bat
```

### 3. Process Symbols
- Enter ticker symbols (e.g., `AAPL,MSFT,GOOGL`)
- Set history (2-30 years or "All Available")
- Click "Start Pipeline"
- Monitor in real-time

---

## 📚 Complete Documentation

**👉 [Read Full Documentation in `docs/` Folder](./docs/README.md)**

### Quick Links
- **[Getting Started Guide](./docs/GETTING_STARTED.md)** - Complete setup instructions
- **[Dashboard User Guide](./docs/DASHBOARD_USER_GUIDE.md)** - Dashboard features and operations
- **[Architecture](./docs/ARCHITECTURE.md)** - System design and threading model
- **[Quick Reference](./docs/QUICK_REFERENCE.md)** - Commands, shortcuts, troubleshooting
- **[API Reference](./docs/API_REFERENCE.md)** - Code documentation
- **[Troubleshooting](./docs/TROUBLESHOOTING.md)** - Common issues and solutions

---

## ✨ Key Features

- **Parallel Processing**: 10 independent worker threads with adaptive rate limiting
- **Smart Caching**: 2GB cache with 30-day TTL and date-range lookups
- **200+ Features**: Technical indicators, statistical analysis, microstructure features
- **Real-time Dashboard**: Live monitoring with micro-stage progress tracking
- **Thread-Safe**: Complete concurrent operation support
- **Performance**: 5-8× speedup with vectorized operations
- **MongoDB Storage**: Persistent profile objects with rich metadata
- **Incremental Updates**: Process only new data since last update
- **Email Alerts**: Optional notifications on critical events

---

## 🏗️ Architecture Overview

```
┌─────────────────────────────────┐
│   PyQt6 Desktop Dashboard       │
│  (Control + Monitor + Analysis) │
└────────────┬────────────────────┘
             │
      ┌──────┴──────┐
      ▼             ▼
┌───────────┐  ┌──────────────────────┐
│ Control   │  │ PipelineController   │
│ Panel     │  │  (QThread)           │
└───────────┘  │                      │
               │  ThreadPoolExecutor  │
               │  (10 workers)        │
               │                      │
               │  Each Worker:        │
               │  ├─ Rate Limiter    │
               │  ├─ Pipeline Inst.  │
               │  ├─ Features        │
               │  └─ MongoDB Save    │
               └────┬────────────────┘
                    │
         ┌──────────┼──────────┐
         ▼          ▼          ▼
      EODHD      Feature    MongoDB
       API      Engineering  Storage
```

---

## 📊 Core Capabilities

### Data Processing
- **Fetch**: Historical minute-level OHLCV data via EODHD API
- **Engineer**: 39+ features across 5 categories (technical, statistical, microstructure, risk, multi-timeframe)
- **Store**: Rich profiles in MongoDB with feature metadata
- **Update**: Incremental processing of new data without full recompute

### Dashboard
- **Real-time Monitoring**: Live processing queue with micro-stage progress
- **Profile Browsing**: View and analyze stored company profiles
- **Cache Management**: Browse, search, and manage cached data
- **API Monitoring**: Real-time API call tracking and rate limit display
- **Settings Panel**: Configure system behavior, API keys, database connections

### Performance
- **Parallel Workers**: Process 7+ symbols simultaneously
- **Adaptive Rate Limiting**: Per-worker throttling (7/min, 8550/day)
- **Vectorized Operations**: 5-8× speedup for feature engineering
- **Caching**: Date-range based smart caching, 30-day TTL
- **Incremental Processing**: Update only changed data

---

## 🎯 Use Cases

### Traders & Analysts
- Analyze minute-level price patterns across multiple stocks
- View technical indicators and statistical features
- Track portfolio performance metrics

### Data Scientists
- Access engineered features for ML model training
- Explore microstructure analysis
- Analyze cross-symbol correlations

### Developers
- Build custom analysis on top of the pipeline
- Extend feature engineering
- Integrate with external systems

### Operations
- Monitor data pipeline health
- Manage API quotas and rate limits
- Troubleshoot processing issues

---

## 💻 System Requirements

- **OS**: Windows 11 (or compatible)
- **Python**: 3.8 or higher
- **RAM**: 16GB minimum (32GB recommended)
- **Disk**: 10GB for cache and databases
- **MongoDB**: Running locally or accessible remotely
- **API**: EODHD API key (free or paid)

---

## 🔧 Configuration

### Environment Variables (.env)
```ini
EODHD_API_KEY=your_api_key_here
MONGODB_URI=mongodb://localhost:27017/
MONGODB_DB=Entities
LOG_LEVEL=INFO
```

### Dashboard Settings
- Workers: 10 (configurable based on CPU cores)
- Chunk Size: 30 days (recommended)
- Cache Size: 2GB
- Cache TTL: 30 days

---

## 📈 Performance Metrics (v1.1.1)

| Metric | Performance |
|--------|-------------|
| Feature Engineering (1.5M rows) | 2-3 minutes |
| Max Drawdown Calculation | 5-10 seconds |
| Parallel Processing | 7+ symbols stable |
| Dashboard Responsiveness | Real-time |
| Cache Hit Speed | <1 second |

---

## 🐛 What's New in v1.1.1

✅ **Bug Fixes**
- Fixed thread-safety issues in cache operations (5 locations)
- Fixed datetime parsing with timestamps
- Fixed date range display truncation

✅ **Performance**
- 5-8× speedup for feature engineering (vectorization)
- 200-300× faster max drawdown calculation
- Improved cache efficiency

✅ **UI Enhancements**
- Added Cache Manager with splitter
- Right-click context menu for cache deletion
- Better column sizing and date range display

[See full changelog](./CHANGELOG.md)

---

## 🚦 Getting Help

### For First-Time Setup
→ Start with **[Getting Started Guide](./docs/GETTING_STARTED.md)**

### For Dashboard Usage
→ Read **[Dashboard User Guide](./docs/DASHBOARD_USER_GUIDE.md)**

### For Technical Details
→ Review **[Architecture Guide](./docs/ARCHITECTURE.md)**

### For Common Problems
→ Check **[Troubleshooting](./docs/TROUBLESHOOTING.md)**

### For Quick Lookup
→ Use **[Quick Reference](./docs/QUICK_REFERENCE.md)**

---

## 📁 Project Structure

```
├── dashboard/          # PyQt6 dashboard application
│   ├── main.py        # Entry point
│   ├── ui/            # UI panels and widgets
│   ├── controllers/    # Pipeline & database control
│   ├── services/      # Metrics, alerts, cache
│   └── utils/         # Signals, theme, helpers
├── pipeline.py        # Core pipeline orchestrator
├── feature_engineering.py  # Feature extraction engine
├── data_fetcher.py    # EODHD API integration
├── mongodb_storage.py # Database layer
├── config.py          # Configuration settings
├── docs/              # Comprehensive documentation
├── tests/             # Unit and integration tests
├── logs/              # Application logs
└── requirements.txt   # Python dependencies
```

---

## 🔐 Security Notes

- Use **app-specific passwords** for SMTP (e.g., Gmail App Password)
- Store credentials in **environment variables** (`.env`)
- Never commit `.env` with real credentials
- Use **HTTPS** for MongoDB Atlas connections

---

## 📞 Support & Troubleshooting

**Common Issues**:

| Issue | Solution |
|-------|----------|
| Dashboard won't start | Check Python 3.8+, reinstall requirements.txt |
| MongoDB connection error | Verify MongoDB running, check connection string |
| API rate limit | Wait for reset, reduce workers, extend chunk days |
| Slow processing | Reduce workers, check system resources, increase RAM |
| Cache issues | Clear cache in Cache Manager, check disk space |

→ See [Troubleshooting Guide](./docs/TROUBLESHOOTING.md) for detailed help

---

## 📋 Version Information

- **Current**: 1.1.1
- **Release Date**: November 28, 2025
- **Status**: Production Ready
- **Type**: Patch Release (bug fixes + optimization)

---

## 📄 License

Internal / Proprietary - Update as needed

---

## 🔗 External Links

- **EODHD API**: https://eodhd.com
- **MongoDB**: https://www.mongodb.com
- **PyQt6**: https://pypi.org/project/PyQt6/

---

**Last Updated**: November 28, 2025  
**Status**: ✅ Stable & Production Ready
