# Getting Started with Minute Data Pipeline

A comprehensive guide to set up and run the Minute Data Pipeline system.

## Prerequisites

- **Python**: 3.8 or higher
- **MongoDB**: Running locally or remote connection
- **API Key**: EODHD Historical Data API (https://eodhd.com)
- **System**: Windows 11 (or compatible OS)
- **RAM**: 16GB minimum (32GB recommended)
- **Disk Space**: 10GB for cache and databases

## Installation Steps

### 1. Clone the Repository

```bash
cd "D:\development project"
git clone <repository-url>
cd Minute_Data_Pipeline
```

### 2. Create Virtual Environment

```bash
python -m venv .venv
.venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Environment

```bash
# Copy example configuration
copy .env.example .env

# Edit .env with your settings
notepad .env
```

**Required settings in .env**:
```
EODHD_API_KEY=your_api_key_here
MONGODB_URI=mongodb://localhost:27017/
MONGODB_DB=Entities
```

### 5. Verify Installation

```bash
python -c "import dashboard; print('✅ Dashboard imported successfully')"
```

## Running the Pipeline

### Start the Dashboard

```bash
# Method 1: Using batch file (Windows)
run_dashboard.bat

# Method 2: Using PowerShell
.venv\Scripts\python dashboard/main.py

# Method 3: Quick start script
python quick_start.py
```

### Initial Setup

1. **Add Symbols**:
   - Enter ticker symbols in "Ticker Symbol(s)" field
   - Use comma-separated values: `AAPL,MSFT,GOOGL,NVDA`
   - Or use "Browse Companies" to select from full list

2. **Select History**:
   - Choose years of history (1-30 or "All Available")
   - Set chunk size (30 days recommended)
   - Default: All available data from establishment date

3. **Configure Processing**:
   - Set number of workers (10 recommended for 32GB RAM)
   - Enable/disable parallel processing
   - Choose update mode:
     - **Incremental**: Update existing profiles
     - **Full Rebuild**: Reprocess from scratch

4. **Start Pipeline**:
   - Click "Start Pipeline" button
   - Monitor progress in real-time
   - Check logs for any issues

## Dashboard Overview

### Main Tabs

1. **Pipeline Control**:
   - Symbol input and company selection
   - Processing options and settings
   - Start/Pause/Stop buttons
   - Real-time metrics display

2. **Database Profiles**:
   - View stored company profiles
   - Profile details and statistics
   - Export and sharing options

3. **Settings**:
   - System configuration
   - Performance tuning
   - API key management

4. **Cache Manager**:
   - View cached data
   - Cache statistics
   - Selective cache deletion
   - Cache cleanup options

## Common Tasks

### Processing a Single Symbol

1. Enter ticker in "Ticker Symbol(s)" field
2. Set "History Years" to desired period
3. Click "Start Pipeline"
4. Monitor progress in Processing Queue

### Processing Multiple Symbols

1. Enter comma-separated tickers: `AAPL,MSFT,GOOGL`
2. Or use "Select Top N" to choose from market leaders
3. Click "Start Pipeline"
4. All symbols process in parallel

### Updating Existing Data

1. Enable "Incremental (update existing)" mode
2. Enter symbol ticker
3. Click "Start Pipeline"
4. Only new data since last update is processed

### Managing Cache

1. Open "Cache Manager" tab
2. View cached symbols and date ranges
3. Right-click to delete specific symbol cache
4. Use "Clear All Cache" to reset entire cache

## Troubleshooting

### Dashboard Won't Start
```bash
# Check Python installation
python --version

# Verify dependencies
pip install -r requirements.txt

# Check for errors
python dashboard/main.py
```

### MongoDB Connection Error
```bash
# Verify MongoDB is running
# Windows: Check MongoDB service or start locally
mongod --dbpath "C:\data\db"

# Test connection
python -c "from pymongo import MongoClient; MongoClient('mongodb://localhost:27017/')"
```

### API Limit Errors
- Check EODHD API key in .env
- Verify API subscription includes historical data
- Wait for rate limit to reset (minute limits reset every minute)

### Pipeline Crashes
1. Check logs in `logs/` directory
2. Review error message in dashboard logs
3. Try with fewer symbols first
4. Increase system resources if needed

## Performance Tips

### For Optimal Performance

1. **Worker Threads**: 
   - Formula: `Available Cores × 1.5` (up to 16 max)
   - Example: 6-core system = 9 workers

2. **History Years**:
   - Start with 2-3 years for testing
   - Build up to 10+ years once tested

3. **Batch Size**:
   - 30 days is optimal for API
   - Smaller batches = more API calls
   - Larger batches = slower processing

4. **Parallel Processing**:
   - Enable for 4+ symbols
   - Disable for 1-2 symbols (faster)
   - More workers = more RAM usage

5. **System Resources**:
   - Close unnecessary applications
   - Allocate sufficient RAM
   - Use SSD for better performance

## API Rate Limits

- **Per Minute**: 80 requests/minute total
- **Per Day**: 95,000 requests/day total
- **Per Worker**: ~7/minute (with 10 workers)
- **Daily Allocation**: ~8,550/day per worker

### Rate Limit Strategy

1. **Adaptive Limiting**: System automatically throttles as limit approaches
2. **Per-Worker Quotas**: Each worker gets independent limit allocation
3. **Backoff on Error**: Exponential backoff when hitting limits
4. **Daily Resets**: Counts reset daily at midnight UTC

## Data Storage

### Cache Storage
- **Location**: `~/.pipeline_data_cache/`
- **Size**: 2GB max (supports 10-15 symbols)
- **TTL**: 30 days
- **Format**: Pickled DataFrames

### MongoDB Storage
- **Database**: `Entities`
- **Collections**:
  - `minute_profiles` - Statistical profiles
  - `ml_profiles` - ML model data
  - `processing_logs` - Audit trail

## Next Steps

1. **Complete First Run**: Process 2-3 symbols end-to-end
2. **Review Results**: Check Database Profiles tab for outputs
3. **Scale Up**: Process larger symbol sets
4. **Optimize**: Adjust workers and settings based on performance
5. **Automate**: Schedule regular updates with task scheduler

## Additional Resources

- **Main Documentation**: [../README.md](../README.md)
- **Architecture Guide**: [ARCHITECTURE.md](./ARCHITECTURE.md)
- **Dashboard Guide**: [DASHBOARD_USER_GUIDE.md](./DASHBOARD_USER_GUIDE.md)
- **API Reference**: [API_REFERENCE.md](./API_REFERENCE.md)
- **Troubleshooting**: [TROUBLESHOOTING.md](./TROUBLESHOOTING.md)

## Support

For issues and troubleshooting, see:
- [Troubleshooting Guide](./TROUBLESHOOTING.md)
- [Quick Reference](./QUICK_REFERENCE.md)
- [FAQ](./FAQ.md) (if available)

---

**Last Updated**: November 28, 2025  
**Version**: 1.1.1

