# Setup and Deployment Guide

## Table of Contents

- [System Requirements](#system-requirements)
- [Installation](#installation)
- [Configuration](#configuration)
- [First Run](#first-run)
- [Docker Deployment](#docker-deployment)
- [Production Deployment](#production-deployment)
- [Maintenance](#maintenance)

---

## System Requirements

### Minimum Requirements

| Component | Minimum | Recommended |
|-----------|---------|-------------|
| **CPU** | 4 cores | 6+ cores |
| **RAM** | 8GB | 16GB+ |
| **Storage** | 10GB SSD | 50GB+ SSD |
| **Network** | 1 Mbps | 10 Mbps+ |
| **OS** | Windows 10, macOS 10.15, Ubuntu 18.04+ | Windows 11, macOS 12+, Ubuntu 22.04+ |
| **Python** | 3.10 | 3.11+ |

### Target System Profile

**Optimized for:**
- Ryzen 5 7600 (6 cores)
- RTX 3060 (optional)
- 32GB RAM
- Windows 11 / Linux

### Network Requirements

- **Internet**: Stable connection for API calls
- **Ports**: 
  - 80/443 for EODHD API
  - 27017 for MongoDB (if local)
- **Firewall**: Allow outbound HTTPS to eodhd.com
- **Bandwidth**: ~1-5 MB/day typical usage

---

## Installation

### Step 1: Prerequisites

**Python Setup:**
```bash
# Check Python version
python --version  # Should be 3.10+

# Upgrade pip
python -m pip install --upgrade pip
```

**Required Tools:**
- Git (for cloning repository)
- Virtual environment support

### Step 2: Clone Repository

```bash
# Clone the repository
git clone https://github.com/your-repo/Minute_Data_Pipeline.git
cd Minute_Data_Pipeline

# Create virtual environment
python -m venv .venv

# Activate virtual environment
# On Windows:
.venv\Scripts\activate
# On macOS/Linux:
source .venv/bin/activate
```

### Step 3: Install Dependencies

```bash
# Install required packages
pip install -r requirements.txt

# Verify installation
python -c "import PyQt6; import pandas; import pymongo; print('✓ Dependencies OK')"
```

### Step 4: Environment Configuration

```bash
# Copy example configuration
cp .env.example .env

# Edit .env with your settings
# Windows: notepad .env
# macOS/Linux: nano .env
```

**Required Environment Variables:**
```bash
# EODHD API (get from https://eodhd.com)
EODHD_API_KEY=your_api_key_here
EODHD_BASE_URL=https://eodhd.com/api

# MongoDB (use MongoDB Atlas for cloud)
MONGODB_URI=mongodb+srv://username:password@cluster.mongodb.net/?retryWrites=true&w=majority
MONGODB_DATABASE=stock_data
MONGODB_COLLECTION=profiles

# Optional: Email alerts
PIPELINE_ALERT_EMAIL=your-email@gmail.com
PIPELINE_ALERT_PASSWORD=your-app-password
```

### Step 5: Verify Installation

```bash
# Run diagnostics
python -c "from config import settings; print('✓ Config OK')"
python -c "from pipeline import MinuteDataPipeline; print('✓ Pipeline OK')"
python -c "from dashboard.main import main; print('✓ Dashboard OK')"
```

---

## Configuration

### EODHD API Setup

1. **Create Account**: https://eodhd.com/register
2. **Get API Key**: https://eodhd.com/account/api-token
3. **Add to .env**:
```bash
EODHD_API_KEY=your_api_key_here
```

### MongoDB Setup

#### Option A: MongoDB Atlas (Cloud - Recommended)

1. **Create Cluster**: https://www.mongodb.com/cloud/atlas
2. **Create Database User**:
   - User: `admin`
   - Password: Generate strong password
3. **Get Connection String**:
   - Include username and password
   - Format: `mongodb+srv://admin:password@cluster.mongodb.net/`
4. **Add to .env**:
```bash
MONGODB_URI=mongodb+srv://admin:password@cluster.mongodb.net/?retryWrites=true&w=majority
MONGODB_DATABASE=stock_data
MONGODB_COLLECTION=profiles
```

#### Option B: Local MongoDB

1. **Install MongoDB**: https://docs.mongodb.com/manual/installation/
2. **Start Service**:
   ```bash
   # Windows
   net start MongoDB
   
   # macOS
   brew services start mongodb-community
   
   # Linux
   sudo systemctl start mongod
   ```
3. **Connection String**:
   ```bash
   MONGODB_URI=mongodb://localhost:27017
   ```

### Email Alerts Configuration (Optional)

**Gmail Setup:**
1. Enable 2-factor authentication
2. Generate App Password: https://myaccount.google.com/apppasswords
3. Add to .env:
```bash
PIPELINE_ALERT_EMAIL=your-email@gmail.com
PIPELINE_ALERT_PASSWORD=your-16-char-app-password
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
```

### Pipeline Configuration

Edit `.env` to customize:

```bash
# Rate Limiting (per worker)
API_CALLS_PER_MINUTE=80
API_CALLS_PER_DAY=95000

# Data Fetching
DATA_FETCH_INTERVAL_DAYS=30
DEFAULT_CHUNK_SIZE=30      # Days per request
DEFAULT_HISTORY_YEARS=5    # Default history to fetch
DEFAULT_WORKERS=10         # Parallel workers

# Cache
CACHE_TTL_HOURS=24         # Company list cache duration
CACHE_PATH=~/.pipeline_cache.db

# Logging
LOG_LEVEL=INFO
LOG_RETENTION_DAYS=30
```

---

## First Run

### Step 1: Launch Dashboard

```bash
# Windows
run_dashboard.bat

# macOS/Linux
python dashboard/main.py
```

**Expected Output:**
```
Dashboard starting...
Cache store initialized
MongoDB connected
Loading UI...
Dashboard ready
```

### Step 2: Configure Settings

1. **Open Settings Tab**
2. **Verify all fields are populated**:
   - EODHD API Key: ✓
   - MongoDB URI: ✓
   - Workers: 10 (or as desired)
3. **Click "Save Settings"**

### Step 3: Add First Symbols

1. **Switch to Control Tab**
2. **Enter symbols** (comma-separated):
   ```
   AAPL, MSFT, GOOGL
   ```
3. **Select Mode**:
   - Incremental (recommended for first run)
4. **Click "Start"**

### Step 4: Monitor Progress

1. **Watch Monitor Tab**:
   - API Usage gauge
   - Processing queue
   - Live logs
2. **Check for errors** in log viewer
3. **First run may take 10-30 minutes**

---

## Docker Deployment

### Dockerfile

Create `Dockerfile` in project root:

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    qt6-base-private \
    libxkbcommon-x11-0 \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY . .

# Environment setup
ENV PYTHONUNBUFFERED=1
ENV QT_QPA_PLATFORM=offscreen

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "from config import settings; print('OK')"

# Run
CMD ["python", "pipeline.py"]
```

### Docker Compose

Create `docker-compose.yml`:

```yaml
version: '3.8'

services:
  pipeline:
    build: .
    environment:
      EODHD_API_KEY: ${EODHD_API_KEY}
      MONGODB_URI: mongodb://mongodb:27017
      MONGODB_DATABASE: stock_data
    depends_on:
      - mongodb
    volumes:
      - ./logs:/app/logs
      - ./.env:/app/.env:ro
    networks:
      - pipeline-network

  mongodb:
    image: mongo:6.0
    volumes:
      - mongodb-data:/data/db
    networks:
      - pipeline-network
    environment:
      MONGO_INITDB_ROOT_USERNAME: admin
      MONGO_INITDB_ROOT_PASSWORD: ${MONGO_ROOT_PASSWORD}

  mongo-express:
    image: mongo-express:latest
    ports:
      - "8081:8081"
    environment:
      ME_CONFIG_MONGODB_ADMINUSERNAME: admin
      ME_CONFIG_MONGODB_ADMINPASSWORD: ${MONGO_ROOT_PASSWORD}
      ME_CONFIG_MONGODB_URL: mongodb://admin:${MONGO_ROOT_PASSWORD}@mongodb:27017/
    depends_on:
      - mongodb
    networks:
      - pipeline-network

volumes:
  mongodb-data:

networks:
  pipeline-network:
```

### Deploy with Docker

```bash
# Build image
docker build -t minute-pipeline:latest .

# Run container
docker run -e EODHD_API_KEY=your_key \
           -e MONGODB_URI=mongodb://mongodb:27017 \
           -v $(pwd)/logs:/app/logs \
           minute-pipeline:latest

# Or with docker-compose
docker-compose up -d
```

---

## Production Deployment

### Pre-Deployment Checklist

- [ ] All tests pass: `pytest tests/`
- [ ] Configuration verified
- [ ] MongoDB backup configured
- [ ] Email alerts working
- [ ] Rate limits appropriate
- [ ] Log rotation configured
- [ ] Monitoring set up

### Deployment Steps

#### 1. On Server

```bash
# SSH into server
ssh user@server-ip

# Clone repository
git clone repo-url
cd Minute_Data_Pipeline

# Create virtual environment
python3.11 -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
nano .env  # Add production values
```

#### 2. Setup Systemd Service (Linux)

Create `/etc/systemd/system/pipeline.service`:

```ini
[Unit]
Description=Minute Data Pipeline
After=network.target mongodb.service

[Service]
Type=simple
User=pipeline
WorkingDirectory=/home/pipeline/Minute_Data_Pipeline
Environment="PATH=/home/pipeline/Minute_Data_Pipeline/.venv/bin"
ExecStart=/home/pipeline/Minute_Data_Pipeline/.venv/bin/python pipeline.py
Restart=on-failure
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Enable and start:
```bash
sudo systemctl enable pipeline
sudo systemctl start pipeline
sudo systemctl status pipeline
```

#### 3. Setup Windows Service

Use NSSM (Non-Sucking Service Manager):
```batch
nssm install PipelineService "C:\path\to\.venv\Scripts\python.exe" "C:\path\to\pipeline.py"
nssm start PipelineService
```

#### 4. Configure Log Rotation

Create `/etc/logrotate.d/pipeline`:

```
/home/pipeline/Minute_Data_Pipeline/logs/*.log {
    daily
    rotate 30
    compress
    delaycompress
    missingok
    notifempty
}
```

#### 5. Monitoring Setup

**Option A: Prometheus**

```bash
# Install Prometheus exporter
pip install prometheus-client
```

**Option B: CloudWatch**

```bash
# AWS CloudWatch monitoring
pip install boto3
```

### Backup Strategy

#### Daily Backup

```bash
#!/bin/bash
# backup_pipeline.sh

TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="/backups/pipeline"
MONGO_URI="mongodb://localhost:27017"

# Backup MongoDB
mongodump --uri="$MONGO_URI" \
          --out="$BACKUP_DIR/mongodb_$TIMESTAMP"

# Backup logs
tar -czf "$BACKUP_DIR/logs_$TIMESTAMP.tar.gz" /home/pipeline/Minute_Data_Pipeline/logs

# Keep only last 30 days
find $BACKUP_DIR -mtime +30 -delete

echo "Backup completed: $TIMESTAMP"
```

Schedule with cron:
```bash
0 2 * * * /home/pipeline/backup_pipeline.sh
```

---

## Maintenance

### Regular Tasks

#### Daily
- Monitor logs for errors
- Check API usage
- Verify database connectivity

#### Weekly
- Review processing statistics
- Check MongoDB disk usage
- Test email alerts

#### Monthly
- Backup MongoDB
- Update dependencies: `pip list --outdated`
- Review and archive old logs
- Performance analysis

### Performance Tuning

#### For High-Volume Processing

```bash
# Increase workers (if CPU available)
DEFAULT_WORKERS=16

# Optimize chunk size
DEFAULT_CHUNK_SIZE=30

# Increase rate limits (if API tier allows)
API_CALLS_PER_MINUTE=100
API_CALLS_PER_DAY=110000
```

#### For Limited Resources

```bash
# Reduce workers
DEFAULT_WORKERS=4

# Smaller chunks
DEFAULT_CHUNK_SIZE=7

# Lower rate limits
API_CALLS_PER_MINUTE=40
API_CALLS_PER_DAY=50000
```

### Troubleshooting

**Issue: Memory leak**
```bash
# Monitor memory
watch -n 1 'ps aux | grep python'

# Set memory limit (Docker)
docker run --memory="2g" minute-pipeline:latest
```

**Issue: Slow processing**
```bash
# Check database indexes
db.profiles.getIndexes()

# Rebuild if needed
db.profiles.reIndex()
```

**Issue: API rate limit errors**
```bash
# Reduce workers temporarily
DEFAULT_WORKERS=5

# Wait for reset (24-hour window)
```

### Monitoring Commands

```bash
# Check service status
systemctl status pipeline

# View recent logs
tail -f /home/pipeline/Minute_Data_Pipeline/logs/pipeline_$(date +%Y-%m-%d).log

# Database stats
mongosh
> use stock_data
> db.profiles.stats()

# Disk usage
du -sh /home/pipeline/Minute_Data_Pipeline/*
```

### Upgrade Process

```bash
# Stop service
systemctl stop pipeline

# Backup current code and database
git stash
mongodump --out=./backup

# Pull latest
git pull origin main

# Update dependencies
pip install -r requirements.txt

# Test
pytest tests/

# Restart service
systemctl start pipeline

# Verify
systemctl status pipeline
```

---

**Last Updated**: November 28, 2025  
**Version**: 1.1.0

