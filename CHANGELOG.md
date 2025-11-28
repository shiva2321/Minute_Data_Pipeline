# Changelog

## [1.0.0] - 2025-11-28
### Added
- Initial PyQt6 desktop dashboard for Minute Data Pipeline.
- Parallel symbol processing with per-worker adaptive rate limiting.
- 30-day chunk data fetching strategy.
- Real-time metrics: queue, successes, failures, ETA, API usage.
- Live color-coded log viewer.
- Database Profiles browser with view, edit, delete, export.
- Profile editor with multi-tab feature groups and raw JSON editing.
- Settings panel (API, MongoDB, pipeline defaults, UI preferences).
- Auto-reconnect & caching for MongoDB operations.
- Robust error handling for profile viewing, exporting, deleting.
- Feature engineering pipeline integration (technical, statistical, regimes, predictive labels).
- Extensive documentation: GETTING_STARTED, UPDATED_DASHBOARD_GUIDE, FEATURE_ENGINEERING_FIX, etc.

### Fixed
- Datetime rendering issues in Profile Editor overview (converted to string).
- Incorrect pipeline attribute usage (`fetcher` -> `data_fetcher`).
- Crashes when viewing/deleting/exporting profiles (added defensive checks & serialization).
- Missing methods in storage (`list_all_profiles`, `update_profile`).
- Non-existent feature method references replaced with existing pipeline methods.

### Changed
- Default chunk size set to 30 days for API efficiency.
- True parallel processing architecture (independent rate limiters per worker).
- Enhanced .gitignore for clean repository state.

### Removed
- Temporary sample text artifacts and transient test output from tracking.

---

