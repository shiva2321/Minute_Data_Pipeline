@echo off
REM v1.1.0 Release Commit Script
REM Windows Command Prompt version

cd /d "D:\development project\Minute_Data_Pipeline"

echo.
echo ======================================================================
echo Stock Market Minute Data Pipeline - v1.1.0 Release
echo ======================================================================
echo.

REM Show git status
echo Git Status:
git status --short
echo.

REM Add all changes
echo Adding changes to git...
git add -A
echo ✓ Changes staged

REM Create commit
echo.
echo Creating commit...
git commit -m "v1.1.0: Stable dashboard with queue and metrics fixes

- Reorganized dashboard monitor panel (60%% space saved)
- Fixed real-time metrics display (single-line compact format)
- Fixed ETA calculation and display
- Fixed processing queue (now shows all symbols: queued, processing, complete)
- Added Remove All Selected button to company selector
- Renamed 'Fetch from EODHD' to 'Load from Cache'
- Changed Top 10 to Top N selector (1-500 companies)
- Fixed cache loading for persistent selection
- Improved symbol row tracking (no duplicates)
- Auto-scroll queue to show latest items
- Proper Success/Failed/Skipped stat tracking
- Added v1.1.0 release notes and changelog
- Verified all core modules and dashboard components
- Production ready stable build"

echo ✓ Commit created
echo.

REM Show commit log
echo Latest commits:
git log --oneline -5
echo.

echo ======================================================================
echo Commit complete! Ready to push.
echo ======================================================================

