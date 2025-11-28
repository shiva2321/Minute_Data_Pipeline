# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.1.0] - 2025-11-28

### Added
- Compact metrics bar consolidating all stats in single line
- Auto-scroll functionality in processing queue
- "Remove All Selected" button in company selector
- "Load from Cache" button (renamed from "Fetch from EODHD")
- Top N company selector with user-customizable spinner (1-500)
- Proper symbol row tracking preventing duplicates
- Per-worker rate limiting (7/min, 8550/day per worker)
- 30-day chunk size for reduced API calls
- Smart cache loading (checks cache before fetching)

### Fixed
- Real-time metrics display (now in single-line compact format)
- ETA calculation and display format
- Success/Failed/Skipped stat tracking
- Processing queue showing all symbols (was only showing complete)
- Cache loading when company selector dialog opens
- Company data field name handling (API format vs cache format)
- Symbol row indices when removing items
- Table scrolling to show latest processing items

### Changed
- Dashboard layout reorganized (60% space saved)
- Font sizes optimized (11px metrics, 10px logs)
- Margins reduced from 15px to 5px
- Metrics bar spacing from 20px to 10px
- Queue to Logs ratio changed to 4:1 (more space for queue)
- Top 10 button → Top N with spinner input
- Metrics bar colors and styling

### Optimized
- Dashboard real estate utilization
- Processing queue display and scrolling
- Cache persistence (24-hour TTL)
- Symbol selection workflow
- Company selector performance

## [1.0.0] - 2025-11-27

### Added
- Complete PyQt6 desktop application for pipeline control
- Parallel processing with 10 worker threads
- Live monitoring dashboard with real-time metrics
- Processing queue table with 8-column detail view
- Symbol-level control (pause, resume, remove per ticker)
- Global pipeline controls (start, pause, resume, stop, clear)
- Company selector dialog with search and multi-select
- Database profile browser and editor
- Live colored log viewer (DEBUG, INFO, WARNING, ERROR, SUCCESS)
- Settings panel for configuration
- API usage rate limiter with visual gauge
- Adaptive rate limiting (80/min, 95k/day)
- 24-hour company list caching
- MongoDB profile storage and persistence
- Feature engineering pipeline (200+ indicators)
- Minute-level OHLCV data fetching
- Historical data backfilling (1-30 years)

### Features
- Incremental vs Full Rebuild modes
- Configurable history years (1-30)
- Configurable chunk size (1-30 days)
- Parallel processing with configurable workers
- Per-symbol backfill metadata tracking
- Auto-retry on failure
- Desktop notifications support
- System tray integration
- Settings persistence
- Dark theme UI

### Integration
- EODHD API for US exchange data
- MongoDB for data persistence
- Pydantic for configuration management
- Python 3.10+ support

---

## Summary of Versions

| Version | Date | Status | Focus |
|---------|------|--------|-------|
| 1.1.0 | Nov 28, 2025 | Production Ready | Dashboard Refinements & Queue Fixes |
| 1.0.0 | Nov 27, 2025 | Production Ready | Initial Complete Release |

---

## Migration Guide

### From v1.0.0 to v1.1.0

No breaking changes. Simply pull latest code:

```bash
git pull origin main
python dashboard/main.py
```

The dashboard will automatically use the improved layout and queue display.

All cached data (companies, selections) remains compatible.

---

## Future Roadmap

### v1.2.0 (Planned)
- [ ] Email notifications for completion/errors
- [ ] Export profiles to CSV/Parquet
- [ ] Incremental update strategies
- [ ] Multi-symbol correlation analysis
- [ ] Custom feature definitions

### v2.0.0 (Planned)
- [ ] Web dashboard (Flask/Django)
- [ ] REST API for external tools
- [ ] Advanced analytics and visualization
- [ ] Machine learning integration
- [ ] Cloud deployment support

---

For detailed release notes, see `docs/release_notes/v1.1.0.md`

