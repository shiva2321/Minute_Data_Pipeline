# Setup Guide for Minute Data Pipeline

This guide will walk you through setting up the Minute Data Pipeline from scratch.

## Prerequisites

- Python 3.8 or higher
- MongoDB (local installation or MongoDB Atlas account)
- EODHD API account and API key

## Step-by-Step Setup

### 1. Environment Setup

#### Windows (PowerShell)

```powershell
# Navigate to project directory
cd "D:\development project\Minute_Data_Pipeline"

# Create virtual environment
python -m venv .venv

# Activate virtual environment
.\.venv\Scripts\Activate.ps1

# If you get execution policy error, run:
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

#### Linux/Mac

```bash
cd "Minute_Data_Pipeline"
python3 -m venv .venv
source .venv/bin/activate
```

### 2. Install Dependencies

```powershell
# Upgrade pip
python -m pip install --upgrade pip

# Install all required packages
pip install -r requirements.txt
```

### 3. Configure Environment Variables

```powershell
# Copy the example environment file
Copy-Item .env.example .env

# Edit the .env file with your credentials
notepad .env
```

Update the following in `.env`:

```env
# Required: Get your API key from https://eodhd.com/
EODHD_API_KEY=your_actual_api_key_here

# MongoDB configuration
MONGODB_URI=mongodb://localhost:27017/
MONGODB_DATABASE=stock_data
MONGODB_COLLECTION=company_profiles

# Optional: Adjust these as needed
DATA_FETCH_INTERVAL_DAYS=30
MAX_WORKERS=5
BATCH_SIZE=100
```

### 4. MongoDB Setup

#### Option A: Local MongoDB Installation

1. **Download MongoDB**:
   - Visit: https://www.mongodb.com/try/download/community
   - Download MongoDB Community Server
   - Install with default settings

2. **Start MongoDB**:
   ```powershell
   # MongoDB should start automatically as a service
   # To check if it's running:
   Get-Service -Name MongoDB
   
   # To start manually if needed:
   Start-Service -Name MongoDB
   ```

3. **Verify Connection**:
   ```powershell
   # The default URI is:
   # mongodb://localhost:27017/
   ```

#### Option B: MongoDB Atlas (Cloud)

1. **Create Account**:
   - Visit: https://www.mongodb.com/cloud/atlas
   - Sign up for a free account

2. **Create Cluster**:
   - Create a free tier cluster (M0)
   - Choose your region
   - Wait for cluster to be created (~5 minutes)

3. **Configure Access**:
   - Add your IP address to whitelist (or use 0.0.0.0/0 for testing)
   - Create a database user with password
   - Get your connection string

4. **Update .env**:
   ```env
   MONGODB_URI=mongodb+srv://username:password@cluster0.xxxxx.mongodb.net/
   ```

### 5. Get EODHD API Key

1. **Sign Up**:
   - Visit: https://eodhd.com/
   - Create an account

2. **Get API Key**:
   - Navigate to your dashboard
   - Copy your API key

3. **Add to .env**:
   ```env
   EODHD_API_KEY=your_api_key_here
   ```

### 6. Test the Setup

```powershell
# Run the test script
python test_setup.py
```

You should see output like:
```
Running Pipeline Tests
================================================================================
Testing imports...
✓ config imported successfully
✓ data_fetcher imported successfully
...
✓ Core functionality is working!
```

### 7. Run Examples

```powershell
# Edit examples.py and uncomment the examples you want to run
notepad examples.py

# Run examples
python examples.py
```

Or run the main pipeline:

```powershell
python pipeline.py
```

## Troubleshooting

### Import Errors

If you get import errors:
```powershell
# Ensure virtual environment is activated
.\.venv\Scripts\Activate.ps1

# Reinstall requirements
pip install -r requirements.txt --force-reinstall
```

### MongoDB Connection Error

```
Error: Connection refused to MongoDB
```

**Solutions**:
1. Check if MongoDB service is running:
   ```powershell
   Get-Service -Name MongoDB
   ```

2. Try starting the service:
   ```powershell
   Start-Service -Name MongoDB
   ```

3. Check if the port 27017 is in use:
   ```powershell
   netstat -an | findstr "27017"
   ```

### EODHD API Errors

```
Error: Unauthorized / Invalid API key
```

**Solutions**:
1. Verify API key is correctly set in `.env`
2. Check for extra spaces or quotes
3. Verify your EODHD account is active
4. Check API usage limits

### Missing Environment Variables

```
Error: EODHD_API_KEY not set
```

**Solutions**:
1. Ensure `.env` file exists in project root
2. Check that the file is named `.env` not `.env.txt`
3. Verify variables are set correctly
4. Try loading environment manually:
   ```python
   from dotenv import load_dotenv
   load_dotenv()
   ```

## Verification Checklist

- [ ] Virtual environment created and activated
- [ ] All dependencies installed (`pip list` shows all packages)
- [ ] `.env` file created with API key
- [ ] MongoDB is running and accessible
- [ ] Test script passes (`python test_setup.py`)
- [ ] Can import all modules without errors

## Next Steps

Once setup is complete:

1. **Test with a Single Symbol**:
   ```python
   from pipeline import MinuteDataPipeline
   
   pipeline = MinuteDataPipeline()
   pipeline.process_symbol('AAPL', interval='5m')
   ```

2. **Check the Data**:
   ```python
   profile = pipeline.get_profile('AAPL')
   print(profile['company_name'])
   ```

3. **Process Multiple Symbols**:
   ```python
   symbols = ['AAPL', 'MSFT', 'GOOGL']
   results = pipeline.process_multiple_symbols(symbols)
   ```

4. **Explore the Data**:
   - Check MongoDB Compass or Atlas UI
   - Review the stored profiles
   - Analyze the features

## Common Use Cases

### Daily Data Collection

Create a script to run daily:

```python
# daily_update.py
from pipeline import MinuteDataPipeline
from datetime import datetime, timedelta

pipeline = MinuteDataPipeline()

symbols = ['AAPL', 'MSFT', 'GOOGL', 'TSLA', 'AMZN']
yesterday = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')
today = datetime.now().strftime('%Y-%m-%d')

results = pipeline.process_multiple_symbols(
    symbols=symbols,
    from_date=yesterday,
    to_date=today,
    interval='1m'
)

print(f"Updated {len(results['successful'])} symbols")
```

### Export to JSON

```python
import json
from pipeline import MinuteDataPipeline

pipeline = MinuteDataPipeline()
profile = pipeline.export_profile_to_dict('AAPL')

with open('aapl_data.json', 'w') as f:
    json.dump(profile, f, indent=2, default=str)
```

## Support

If you encounter issues:

1. Check the logs in `logs/` directory
2. Verify all configuration settings
3. Test individual components
4. Review the examples in `examples.py`

## Performance Tips

- Use 5-minute intervals instead of 1-minute for faster processing
- Limit date ranges when testing
- Use batch processing for multiple symbols
- Monitor API rate limits
- Index MongoDB collections for better query performance

## Security Notes

- Never commit `.env` file to version control
- Keep API keys secure
- Use environment-specific configurations
- Restrict MongoDB access in production
- Use MongoDB user authentication

---

**Ready to use the pipeline!** 🚀

For detailed API documentation, see the inline docstrings in each module.

