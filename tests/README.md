# Tests Directory

This directory contains the test suite for the Minute Data Pipeline project. Tests are organized into three categories for better maintainability and clarity.

## Directory Structure

```
tests/
├── __init__.py                    # Tests package initialization
├── conftest.py                    # Pytest configuration and shared fixtures
├── README.md                      # This file
├── unit/                          # Unit tests - Isolated module tests
│   ├── __init__.py
│   ├── test_feature_engineering.py
│   ├── test_rate_limiter.py
│   └── test_setup.py
├── integration/                   # Integration tests - Multi-component tests
│   ├── __init__.py
│   ├── test_dashboard_imports.py
│   ├── test_integration_phase1.py
│   ├── test_pipeline_fix.py
│   ├── test_advanced_control.py
│   └── test_per_symbol_fix.py
├── diagnostics/                   # Diagnostic tests - System validation & debugging
│   ├── __init__.py
│   ├── test_diagnostic.py
│   ├── test_datetime_fix.py
│   └── test_v1_1_0_stability.py
├── archived_outputs/              # Legacy test output files (archived)
│   ├── import_test_output.txt
│   ├── test_dt_output.txt
│   ├── test_fix_output.txt
│   ├── test_pc.txt
│   ├── test_result.txt
│   └── test_updates.txt
└── logs/                          # Test execution logs
```

## Test Categories

### 1. **Unit Tests** (`unit/`)
Tests for isolated modules and components with minimal external dependencies.

- **test_feature_engineering.py** - Feature calculation pipeline
  - Tests empty DataFrame handling
  - Tests single row behavior
  - Tests statistical feature bounds
  - Tests multi-timeframe features
  
- **test_rate_limiter.py** - API rate limiting
  - Tests per-minute throttling
  - Tests daily quota enforcement
  - Tests exponential backoff
  
- **test_setup.py** - Pipeline initialization
  - Tests module imports
  - Tests configuration loading
  - Tests basic component setup

### 2. **Integration Tests** (`integration/`)
Tests for multi-component interactions and system-level functionality.

- **test_dashboard_imports.py** - Dashboard component verification
  - Tests PyQt6 dependencies
  - Tests dashboard utilities (theme, signals)
  - Tests controllers (queue, database, pipeline)
  - Tests UI components and panels
  
- **test_integration_phase1.py** - Phase 1 component integration
  - Tests CacheStore initialization
  - Tests LogEmailAlerter
  - Tests MetricsCalculator
  
- **test_pipeline_fix.py** - Pipeline controller verification
  - Tests PipelineController import
  - Tests MinuteDataPipeline import
  - Tests FeatureEngineer methods
  
- **test_advanced_control.py** - Process control system
  - Tests per-symbol control dictionary
  - Tests global control events
  - Tests symbol-level control events
  
- **test_per_symbol_fix.py** - Symbol queue UI
  - Tests symbol queue table creation
  - Tests status management
  - Tests context menu behavior

### 3. **Diagnostic Tests** (`diagnostics/`)
Tests for system validation, troubleshooting, and stability verification.

- **test_diagnostic.py** - Quick system diagnostics
  - Tests CacheStore operations
  - Tests API usage tracking
  
- **test_datetime_fix.py** - DateTime handling validation
  - Tests datetime object parsing
  - Tests string datetime formatting
  - Tests profile data handling
  
- **test_v1_1_0_stability.py** - Comprehensive stability test
  - Tests all core module imports
  - Tests dashboard components
  - Tests database connectivity
  - Tests API integration

## Running Tests

### Run All Tests
```bash
pytest tests/
```

### Run Tests by Category
```bash
# Unit tests only
pytest tests/unit/

# Integration tests only
pytest tests/integration/

# Diagnostic tests only
pytest tests/diagnostics/
```

### Run Tests with Markers
```bash
# Run all unit tests
pytest -m unit

# Run all integration tests
pytest -m integration

# Run all diagnostic tests
pytest -m diagnostic

# Run tests excluding slow ones
pytest -m "not slow"
```

### Run Specific Test File
```bash
pytest tests/unit/test_rate_limiter.py
pytest tests/integration/test_dashboard_imports.py::test_dashboard_controllers
```

### Run Tests with Verbose Output
```bash
pytest -v tests/
```

### Run Tests with Coverage Report
```bash
pytest --cov=. --cov-report=html tests/
```

## Pytest Configuration

The `conftest.py` file provides:

### Shared Fixtures
- **qapp** - PyQt6 QApplication instance (session scope)
- **qapp_with_cleanup** - QApplication with test cleanup
- **in_memory_cache** - In-memory SQLite CacheStore
- **temp_cache_file** - Temporary cache database file
- **pipeline_config** - Default pipeline configuration
- **test_symbols** - Test stock symbols
- **sample_price_data** - Sample OHLCV price data
- **feature_engineer** - FeatureEngineer instance
- **rate_limiter** - AdaptiveRateLimiter instance
- **log_output** - Log capture for test debugging

### Pytest Markers
- `@pytest.mark.unit` - Unit tests
- `@pytest.mark.integration` - Integration tests
- `@pytest.mark.diagnostic` - Diagnostic tests
- `@pytest.mark.slow` - Slow running tests
- `@pytest.mark.requires_pyqt` - Tests requiring PyQt6

## Test Dependencies

### Required
- pytest
- loguru
- pandas
- numpy

### Optional (for specific tests)
- PyQt6 (for dashboard tests)
- motor (for async MongoDB operations)

Install all test dependencies:
```bash
pip install -r requirements.txt
```

## Writing New Tests

1. **Place test files in appropriate directory**
   - Unit tests → `tests/unit/test_*.py`
   - Integration tests → `tests/integration/test_*.py`
   - Diagnostic tests → `tests/diagnostics/test_*.py`

2. **Use appropriate fixtures from conftest.py**
   ```python
   def test_something(sample_price_data, feature_engineer):
       """Test description"""
       result = feature_engineer.process_full_pipeline(sample_price_data)
       assert result is not None
   ```

3. **Add pytest marker**
   ```python
   @pytest.mark.unit
   def test_something():
       """Test description"""
       pass
   ```

4. **Follow naming conventions**
   - Test files: `test_*.py`
   - Test functions: `test_*`
   - Test classes: `Test*`

## Path Configuration

All test files use relative path setup to handle being run from different directories:

```python
import sys
from pathlib import Path

# Add parent directory to Python path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
```

This allows tests to be run:
- From project root: `pytest tests/`
- From tests directory: `cd tests && pytest`
- From IDE: Direct test execution

## Continuous Integration

Tests are designed to run in CI/CD pipelines:

```bash
# Run with minimal output for CI
pytest tests/ -q --tb=short

# Generate JUnit XML for CI integration
pytest tests/ --junit-xml=test-results.xml

# Generate coverage report for CI
pytest tests/ --cov=. --cov-report=xml
```

## Troubleshooting

### Import Errors
Ensure you're running from the project root or the tests have proper path configuration.

### PyQt6 Errors
Make sure PyQt6 is installed and the QApplication fixture is used properly.

### Database/Cache Errors
Check that the CacheStore fixture is properly initialized and cleaned up.

### Slow Tests
Some tests may run slower due to:
- Database initialization
- Feature calculations on large datasets
- API mock delays

Use `@pytest.mark.slow` to mark long-running tests and exclude them from quick test runs.

## Archived Outputs

Legacy test output files are preserved in `archived_outputs/` for reference but should not be used for active testing. These represent previous test runs and are kept for historical purposes.

