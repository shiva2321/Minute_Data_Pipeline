# Minute Data Pipeline

A production-ready Python platform for fetching, engineering, storing, and exploring historical minute‑level equity data from the EODHD API. Includes:
- High‑performance feature engineering (technical, statistical, microstructure, regime, predictive labels)
- MongoDB persistence with indexing & profile lifecycle operations
- Adaptive rate limiting & chunked historical backfill (30‑day efficiency strategy)
- A PyQt6 Desktop Dashboard for orchestration, monitoring, editing profiles, and settings management
- Extensive documentation & release notes under `docs/`

---
## ✅ Highlights
| Area | What You Get |
|------|--------------|
| Data Ingestion | Minute history (multi-year), fundamentals, configurable intervals |
| Feature Engineering | 200+ derived indicators & metrics across technical/statistical/regime/labels |
| Storage | Structured company profiles in MongoDB with indexes & metadata |
| Desktop Dashboard | Parallel processing, live metrics, logs, API usage gauges, profile browser/editor |
| Reliability | Auto-reconnect MongoDB, exception handling, safe JSON editing, configurable rate limits |
| Performance | 30‑day chunk fetch (≈6× fewer API calls), multi-thread parallel symbol workers |
| Documentation | Quick reference, guides, architectural overview, release/fix notes |

---
## 📦 Repository Organization
```
Minute_Data_Pipeline/
├── dashboard/                # PyQt6 desktop application (UI, controllers, widgets, utils)
├── docs/                     # Core documentation & guides
│   ├── release_notes/        # Versioned & fix-focused markdown files
│   ├── ARCHITECTURE.md       # High-level system design
│   ├── API_REFERENCE.md      # Public APIs & usage
│   ├── QUICK_REF.md          # Fast start cheat sheet
│   ├── GETTING_STARTED.md    # Step-by-step onboarding
│   ├── DASHBOARD_GUIDE.md    # Full dashboard walkthrough
│   ├── README_DASHBOARD.md   # Technical dashboard internals
│   └── ... (additional guides & summaries)
├── feature_engineering.py    # FeatureEngineer class (full pipeline)
├── data_fetcher.py           # EODHD data retrieval & rate limiting integration
├── mongodb_storage.py        # MongoDBStorage class (CRUD + indexing)
├── pipeline.py               # MinuteDataPipeline orchestrator (symbol processing)
├── config.py                 # Pydantic settings from environment
├── utils/                    # Shared utility modules
├── scripts/                  # Operational scripts (backfill, benchmark, tests)
├── tests/                    # Test suite (unit/functional)
├── tmp/                      # Transient test outputs / generated artifacts (ignored)
├── logs/                     # Runtime logs (rotating)
├── requirements.txt          # Python dependencies
├── VERSION                   # Current semantic version
├── CHANGELOG.md              # Aggregated release notes
└── README.md                 # This overview
```

---
## 🚀 Quick Start
### 1. Clone & Environment
```powershell
# From desired parent directory
git clone https://github.com/shiva2321/Minute_Data_Pipeline.git
cd Minute_Data_Pipeline
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
Copy-Item .env.example .env  # then edit .env with your API key & MongoDB URI
```
Minimum required in `.env`:
```
EODHD_API_KEY=your_key_here
MONGODB_URI=mongodb://localhost:27017/
```
Optional overrides (defaults in `config.py`):
```
MONGODB_DATABASE=stock_data
MONGODB_COLLECTION=company_profiles
HISTORY_CHUNK_DAYS=30
API_CALLS_PER_MINUTE=80
API_CALLS_PER_DAY=95000
MAX_WORKERS=10
```

### 2. Run Desktop Dashboard
```powershell
# Launch dashboard (creates window)
run_dashboard.bat
```
Or directly:
```powershell
.\.venv\Scripts\python.exe dashboard\main.py
```

### 3. Programmatic Pipeline Usage
```python
from pipeline import MinuteDataPipeline
pipeline = MinuteDataPipeline()
# Full symbol processing (historical + features + storage)
pipeline.process_symbol(symbol='AAPL', exchange='US', interval='1m', from_date=None, to_date=None)
```

### 4. Tests
```powershell
pip install -r requirements.txt
python -m pytest -q tests
```

---
## 🖥 Dashboard Feature Summary
- Parallel symbol processing (independent rate limiters per worker)
- Live status table (queued, processing, success, failed) with progress updates
- API usage gauges (minute/day consumption with color thresholds)
- Log viewer (INFO/WARN/ERROR/SUCCESS color-coded, auto-scroll)
- Profile Browser (search, sort, view, edit, delete, export JSON)
- Profile Editor (overview + grouped feature tabs + raw JSON validation)
- Settings Panel (API keys, MongoDB connectivity test, pipeline defaults, UI theme)
- Automatic ETA calculation & 10s metrics refresh cadence

---
## 🧠 Feature Engineering Coverage (High-Level)
- Technical: SMA/EMA (multi window), Bollinger metrics, RSI, MACD, ATR, Stochastic, momentum, ROC
- Statistical: Price & return distributions, skewness, kurtosis, volatility clusters, ratios
- Microstructure: Volume patterns, liquidity proxies, imbalance, spread-derived metrics
- Time-Based: Session segmentation, rolling time-of-day behaviors
- Regime: Volatility/trend/liquidity regime signals
- Predictive Labels: Forward returns (multi-horizon), breakout classification, realized vol targets
- Quality: Missing/duplicate counts, completeness ratios

---
## 📄 Key Documentation (All under `docs/`)
| Guide | Path |
|-------|------|
| Quick Reference | `docs/QUICK_REF.md` |
| Getting Started | `docs/GETTING_STARTED.md` |
| Dashboard User Guide | `docs/DASHBOARD_GUIDE.md` |
| Dashboard Internals | `docs/README_DASHBOARD.md` |
| Architecture | `docs/ARCHITECTURE.md` |
| API Reference | `docs/API_REFERENCE.md` |
| Release Notes (Fixes) | `docs/release_notes/` |
| Setup & Environment | `docs/SETUP.md` |
| Index / Navigation | `docs/INDEX.md` |

---
## 📝 Release Notes & Fix History
Detailed fix and iteration records live in `docs/release_notes/` (e.g., `FEATURE_ENGINEERING_FIX.md`, `FINAL_CRITICAL_FIXES.md`). For consolidated version changes see `CHANGELOG.md` and semantic version in `VERSION`.

---
## ⚙️ Configuration Model
All runtime settings resolved via `config.py` (Pydantic). Override via environment / `.env`. Review `config.py` for accepted variables & defaults.

---
## 🔐 Safety & Data Integrity
- Defensive exception handling around profile CRUD & JSON edits
- Datetime normalization for UI components
- Auto-reconnect MongoDB wrapper with caching to reduce query load
- Rate limiter safeguards (minute/day quotas & backoff)

---
## 🧪 Testing Strategy
Current tests (see `tests/`):
- Feature engineering calculations
- Rate limiter behavior
- Dashboard import & structural integrity
Future improvements (PRs welcome): deeper integration tests (pipeline end-to-end), performance benchmarks, mock API latency harness.

---
## 🤝 Contributing
1. Fork & branch: `feat/your-feature` or `fix/issue-id`
2. Add/adjust tests where behavior changes
3. Run `pytest` locally before PR
4. Update `CHANGELOG.md` & docs if appropriate

Planned enhancements in roadmap (see `docs/PROJECT_SUMMARY.md` or release notes): streaming ingestion, scheduling, advanced ML labeling, visualization layer, cross-exchange expansion.

---
## 📬 Support & Troubleshooting
| Symptom | Check |
|---------|-------|
| Empty profiles | MongoDB URI & collection names; logs/ for exceptions |
| Slow fetch | Confirm chunk size = 30 days; rate limits not saturated |
| API errors | Validate `EODHD_API_KEY` and daily quota usage |
| Dashboard UI freeze | Ensure workers <= physical/logical cores (≤10 recommended here) |

Logs: `logs/pipeline_YYYY-MM-DD.log`

---
## 📄 License
MIT (see future LICENSE file if added). Use freely with attribution; contributions welcome.
