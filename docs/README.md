# Minute Data Pipeline - Complete Documentation

## 📚 Documentation Index

Welcome! This is your complete guide to the Minute Data Pipeline system. Start below based on your needs.

---

## 🚀 Quick Links

### For First-Time Users
- **[Getting Started Guide](./GETTING_STARTED.md)** - Installation and basic setup
- **[Quick Reference](./QUICK_REFERENCE.md)** - Common tasks and commands
- **[Dashboard User Guide](./DASHBOARD_USER_GUIDE.md)** - Dashboard walkthrough

### For Developers
- **[Architecture](./ARCHITECTURE.md)** - System design and components
- **[API Reference](./API_REFERENCE.md)** - Core classes and methods
- **[Development Guide](./DEVELOPMENT_GUIDE.md)** - Contributing and extending

### For Deployment
- **[Setup & Deployment](./SETUP_AND_DEPLOYMENT.md)** - Production setup
- **[Performance Tuning](./PERFORMANCE_TUNING.md)** - Optimization tips
- **[Troubleshooting](./TROUBLESHOOTING.md)** - Common issues and solutions

### For Analysis
- **[Feature Engineering](./FEATURE_ENGINEERING_GUIDE.md)** - Feature details
- **[ML Training](./ML_TRAINING_AND_INCREMENTAL_UPDATES.md)** - Model training
- **[Data Cache System](./DATA_CACHE_SYSTEM.md)** - Caching mechanism

---

## 📖 Complete Documentation List

### Core Documentation
1. **ARCHITECTURE.md** - System architecture, threading model, data flow
2. **API_REFERENCE.md** - Complete API documentation
3. **GETTING_STARTED.md** - Step-by-step setup guide
4. **QUICK_REFERENCE.md** - Quick lookup for common tasks

### Feature Guides
5. **DASHBOARD_USER_GUIDE.md** - Dashboard features and operations
6. **FEATURE_ENGINEERING_GUIDE.md** - Feature engineering pipeline
7. **DATA_CACHE_SYSTEM.md** - Caching and data management
8. **ML_TRAINING_AND_INCREMENTAL_UPDATES.md** - ML models and incremental processing

### Operations & Deployment
9. **SETUP_AND_DEPLOYMENT.md** - Production setup and deployment
10. **PERFORMANCE_TUNING.md** - Performance optimization
11. **TROUBLESHOOTING.md** - Common issues and solutions
12. **TESTING_GUIDE.md** - Testing and quality assurance

---

## 🎯 Documentation By Use Case

### "I want to run the pipeline"
1. Read: [Getting Started](./GETTING_STARTED.md)
2. Review: [Dashboard User Guide](./DASHBOARD_USER_GUIDE.md)
3. Check: [Quick Reference](./QUICK_REFERENCE.md)

### "I need to understand the architecture"
1. Read: [Architecture](./ARCHITECTURE.md)
2. Review: [Threading Model](./ARCHITECTURE.md#threading-model)
3. Check: [API Reference](./API_REFERENCE.md)

### "I want to extend the system"
1. Read: [Development Guide](./DEVELOPMENT_GUIDE.md)
2. Review: [Architecture](./ARCHITECTURE.md)
3. Implement and test

### "I'm having issues"
1. Check: [Troubleshooting](./TROUBLESHOOTING.md)
2. Review: [Performance Tuning](./PERFORMANCE_TUNING.md)
3. Check: [Testing Guide](./TESTING_GUIDE.md)

### "I want to understand the data"
1. Read: [Feature Engineering](./FEATURE_ENGINEERING_GUIDE.md)
2. Review: [Data Cache System](./DATA_CACHE_SYSTEM.md)
3. Check: [ML Training](./ML_TRAINING_AND_INCREMENTAL_UPDATES.md)

---

## 🔗 Related Files

### Configuration
- `config.py` - Configuration settings
- `requirements.txt` - Python dependencies
- `.env.example` - Environment variable template

### Scripts
- `run_dashboard.bat` - Windows dashboard launcher
- `run_dashboard.ps1` - PowerShell launcher
- `quick_start.py` - Quick start script

### Data
- `samples/` - Sample data files
- `logs/` - Pipeline logs
- `tests/` - Unit and integration tests

---

## 📊 Version Information

- **Current Version**: 1.1.1
- **Release Date**: November 28, 2025
- **Status**: Production Ready
- **Last Updated**: November 28, 2025

---

## 🎓 Learning Path

### Beginner
1. [Getting Started](./GETTING_STARTED.md)
2. [Dashboard User Guide](./DASHBOARD_USER_GUIDE.md)
3. [Quick Reference](./QUICK_REFERENCE.md)

### Intermediate
4. [Architecture](./ARCHITECTURE.md)
5. [Feature Engineering](./FEATURE_ENGINEERING_GUIDE.md)
6. [Data Cache System](./DATA_CACHE_SYSTEM.md)

### Advanced
7. [Development Guide](./DEVELOPMENT_GUIDE.md)
8. [API Reference](./API_REFERENCE.md)
9. [ML Training](./ML_TRAINING_AND_INCREMENTAL_UPDATES.md)

### Expert
10. [Performance Tuning](./PERFORMANCE_TUNING.md)
11. [Troubleshooting](./TROUBLESHOOTING.md)
12. [Testing Guide](./TESTING_GUIDE.md)

---

## ⚡ Key Features

- **Parallel Processing**: 10 independent worker threads
- **Smart Caching**: 2GB cache with 30-day TTL, date-range lookups
- **Rate Limiting**: Per-worker adaptive rate limiting (7/min, 8550/day)
- **Real-time Dashboard**: PyQt6-based live monitoring
- **Feature Engineering**: 39+ statistical features with ML integration
- **Thread-Safe**: Complete thread-safety for concurrent operations
- **Performance**: 5-8× speedup with vectorized operations

---

## 🚀 Getting Started Now

### Quick Start (5 minutes)
```bash
# 1. Clone and setup
git clone <repo>
cd Minute_Data_Pipeline
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt

# 2. Configure
cp .env.example .env
# Edit .env with your API key

# 3. Run
python dashboard/main.py
```

For detailed instructions, see [Getting Started](./GETTING_STARTED.md)

---

## 📞 Support

- **Issues**: Check [Troubleshooting](./TROUBLESHOOTING.md)
- **Questions**: See [Quick Reference](./QUICK_REFERENCE.md)
- **Development**: Read [Development Guide](./DEVELOPMENT_GUIDE.md)

---

## 📋 Changelog

See [../CHANGELOG.md](../CHANGELOG.md) for version history and changes.

---

**Last Updated**: November 28, 2025  
**Status**: ✅ Complete and Production Ready

