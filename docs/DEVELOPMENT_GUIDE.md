# Development Guide

Guide for developers contributing to or extending the pipeline.

## Development Environment Setup

### 1. Clone Repository

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

### 3. Install Development Dependencies

```bash
pip install -r requirements.txt
pip install pytest pytest-cov pytest-html black flake8
```

### 4. Configure Git

```bash
git config user.email "your.email@example.com"
git config user.name "Your Name"
```

---

## Project Structure

```
Minute_Data_Pipeline/
├── dashboard/                    # Main application
│   ├── main.py                  # Entry point
│   ├── __init__.py
│   ├── ui/                      # User interface
│   │   ├── panels/              # Dashboard tabs/panels
│   │   ├── widgets/             # Reusable UI components
│   │   └── dialogs/             # Dialog windows
│   ├── controllers/             # Business logic
│   │   ├── pipeline_controller.py
│   │   └── database_controller.py
│   ├── services/                # Background services
│   │   ├── ml_model_trainer.py
│   │   ├── metrics_calculator.py
│   │   ├── data_fetch_cache.py
│   │   └── incremental_update.py
│   ├── models/                  # Data models
│   │   └── cache_store.py
│   └── utils/                   # Utilities
│       ├── qt_signals.py
│       ├── rate_limiter.py
│       └── theme.py
│
├── pipeline.py                  # Core pipeline
├── feature_engineering.py       # Feature extraction
├── data_fetcher.py              # API integration
├── mongodb_storage.py           # Database layer
├── config.py                    # Configuration
├── tests/                       # Test suite
├── docs/                        # Documentation
├── logs/                        # Log files
└── samples/                     # Sample data
```

---

## Code Style & Standards

### Python Style Guide

Follow PEP 8 with these guidelines:

```python
# Use 4 spaces for indentation
# Maximum line length: 100 characters
# Use snake_case for functions/variables
# Use PascalCase for classes
# Use UPPER_CASE for constants
```

### Code Formatting

Format code before committing:

```bash
black dashboard/ pipeline.py feature_engineering.py
flake8 dashboard/ pipeline.py --max-line-length=100
```

### Docstrings

Use Google-style docstrings:

```python
def calculate_feature(data: pd.DataFrame) -> dict:
    """Calculate technical features from OHLCV data.
    
    Args:
        data: DataFrame with columns [open, high, low, close, volume]
        
    Returns:
        Dictionary mapping feature names to calculated values
        
    Raises:
        ValueError: If required columns missing
    """
```

---

## Core Modules

### pipeline.py

**Purpose**: Core pipeline orchestration

**Key Classes**:
- `MinuteDataPipeline`: Main pipeline class
- Handles: fetch → engineer → store workflow
- Per-symbol processing

**Extension Points**:
- Override `process_symbol()` for custom processing
- Add new stages to pipeline flow

---

### feature_engineering.py

**Purpose**: Feature extraction and engineering

**Key Classes**:
- `FeatureEngineer`: Feature computation
- Supports: 39+ features across 5 categories

**Features**:
- Technical indicators (SMA, EMA, RSI, etc.)
- Statistical analysis (mean, std, skewness, etc.)
- Microstructure metrics (spread, liquidity, etc.)
- Multi-timeframe analysis (5m, 15m, 1h, 1d)
- Risk metrics (VaR, CVaR, drawdown, etc.)

**To Add Feature**:
1. Create new method in `FeatureEngineer`
2. Call from `process_full_pipeline()`
3. Add to feature_metadata
4. Test with unit tests

---

### data_fetcher.py

**Purpose**: EODHD API integration

**Key Classes**:
- `EODHDDataFetcher`: Handles API calls
- Manages: batching, rate limiting, retries

**Features**:
- Adaptive batching (30-day chunks)
- Exponential backoff on rate limits
- Automatic retry logic
- Date range splitting

**To Extend**:
1. Add new API endpoints
2. Implement custom batching strategy
3. Add error handling for new cases

---

### mongodb_storage.py

**Purpose**: Database operations

**Key Classes**:
- `MongoDBStorage`: MongoDB client
- Handles: CRUD operations, indexing

**Collections**:
- `minute_profiles`: Statistical profiles
- `ml_profiles`: ML model data
- `processing_logs`: Audit trail

**To Extend**:
1. Add new collections
2. Implement custom queries
3. Add database migrations

---

## Dashboard Architecture

### PyQt6 Application Structure

```
dashboard/main.py (Entry point)
    ↓
MainWindow (ui/main_window.py)
    ├── ControlPanel (ui/panels/control_panel.py)
    ├── MonitorPanel (ui/panels/monitor_panel.py)
    ├── ProfileBrowser (ui/panels/profile_browser.py)
    └── SettingsPanel (ui/panels/settings_panel.py)
    
Controllers:
    ├── PipelineController (Thread management)
    └── DatabaseController (Database operations)
    
Services:
    ├── MetricsCalculator
    ├── DataFetchCache
    └── MLModelTrainer
```

### Adding a New Panel

1. **Create panel class**:
```python
# dashboard/ui/panels/my_panel.py
from PyQt6.QtWidgets import QWidget, QVBoxLayout

class MyPanel(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout()
        # Add widgets
        self.setLayout(layout)
```

2. **Add to main window**:
```python
# dashboard/ui/main_window.py
from dashboard.ui.panels.my_panel import MyPanel

class MainWindow(QMainWindow):
    def __init__(self):
        # ...
        self.tab_widget.addTab(MyPanel(), "My Tab")
```

3. **Connect signals if needed**:
```python
# Connect to pipeline signals
self.pipeline_controller.progress_updated.connect(self.on_progress)
```

---

## Threading Model

### Worker Thread Pattern

```python
# Background work
class WorkerThread(QThread):
    progress = pyqtSignal(str, int)  # Data, percentage
    
    def run(self):
        # Do work in background
        for i, item in enumerate(items):
            result = process(item)
            self.progress.emit(str(result), int(100*i/len(items)))

# Main thread connection
thread = WorkerThread()
thread.progress.connect(on_progress)
thread.start()
```

---

## Testing

### Writing Unit Tests

```python
# tests/unit/test_my_module.py
import pytest
from dashboard.services.my_service import MyService

class TestMyService:
    def setup_method(self):
        self.service = MyService()
    
    def test_feature_calculation(self):
        result = self.service.calculate(data)
        assert result > 0
        
    def test_error_handling(self):
        with pytest.raises(ValueError):
            self.service.calculate(invalid_data)
```

### Running Tests

```bash
# All tests
pytest tests/ -v

# Specific file
pytest tests/unit/test_my_module.py -v

# With coverage
pytest --cov=dashboard tests/ -v
```

---

## Git Workflow

### Feature Development

```bash
# 1. Create feature branch
git checkout -b feature/my-feature

# 2. Make changes
# Edit files...
# Add tests...
# Update documentation...

# 3. Test everything
pytest tests/ -v
black dashboard/

# 4. Commit changes
git add .
git commit -m "feat: add my feature

- Description of changes
- Related to issue #123"

# 5. Push and create PR
git push origin feature/my-feature
# Create pull request on GitHub
```

### Commit Message Format

```
<type>: <subject>

<body>

<footer>
```

**Types**:
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation
- `style`: Code style
- `refactor`: Refactoring
- `test`: Test additions
- `perf`: Performance improvements

---

## Performance Optimization

### Profiling

```python
# Profile specific function
import cProfile
import pstats

def profile_function():
    profiler = cProfile.Profile()
    profiler.enable()
    
    # Run code
    function_to_profile()
    
    profiler.disable()
    stats = pstats.Stats(profiler)
    stats.sort_stats('cumulative')
    stats.print_stats(20)  # Top 20 functions
```

### Memory Optimization

```python
# Use generators for large datasets
def process_large_dataset(items):
    for item in items:  # Don't load all at once
        yield expensive_operation(item)

# Use numpy for numerical operations
import numpy as np
# Vectorized operations are 100x+ faster than Python loops
```

### Caching

```python
from functools import lru_cache

@lru_cache(maxsize=128)
def expensive_calculation(x):
    # Result cached for same arguments
    return x ** 2
```

---

## Debugging

### Debug Logging

```python
from loguru import logger

logger.debug("Variable value: {}", x)
logger.info("Starting process")
logger.warning("Potential issue")
logger.error("Error occurred")
```

### PyQt Debugging

```python
# Check signal connections
from PyQt6.QtCore import QObject
obj.destroyed.connect(lambda: print("Object destroyed"))

# Check thread
from PyQt6.QtCore import QThread
print(f"Current thread: {QThread.currentThread().objectName()}")
```

---

## Documentation

### Adding Documentation

1. **Docstrings in code**:
   - Google-style format
   - Describe purpose, args, returns

2. **Markdown files**:
   - Create in `docs/` folder
   - Use clear structure with headers
   - Include code examples

3. **README files**:
   - Add to module folders
   - Describe module purpose
   - Link to related docs

---

## Common Tasks

### Add New Configuration Option

1. **Add to config.py**:
```python
# config.py
NEW_OPTION = os.getenv('NEW_OPTION', 'default_value')
```

2. **Add to .env.example**:
```
NEW_OPTION=default_value
```

3. **Use in code**:
```python
from config import NEW_OPTION
```

---

### Add New API Endpoint

1. **Update data_fetcher.py**:
```python
def fetch_new_data(self, symbol):
    endpoint = f"{self.base_url}/new_endpoint"
    # Make API call
    # Handle response
```

2. **Add error handling**:
```python
try:
    data = self.fetch_new_data(symbol)
except APIError as e:
    logger.error(f"API error: {e}")
```

3. **Test thoroughly**:
```python
def test_fetch_new_data():
    # Mock API response
    # Test success case
    # Test error cases
```

---

## Release Process

### Preparing a Release

1. **Update version**:
   - Edit `VERSION` file
   - Update `CHANGELOG.md`

2. **Run tests**:
   ```bash
   pytest tests/ -v
   ```

3. **Create commit**:
   ```bash
   git commit -m "release: v1.1.2"
   ```

4. **Tag release**:
   ```bash
   git tag -a v1.1.2 -m "Release version 1.1.2"
   git push origin v1.1.2
   ```

---

## Resources

### Documentation
- [Architecture](./ARCHITECTURE.md)
- [API Reference](./API_REFERENCE.md)
- [Quick Reference](./QUICK_REFERENCE.md)

### External Links
- [PyQt6 Docs](https://www.riverbankcomputing.com/static/Docs/PyQt6/)
- [MongoDB Docs](https://docs.mongodb.com/)
- [Python Best Practices](https://pep8.org/)

---

**Last Updated**: November 28, 2025  
**Version**: 1.1.1

