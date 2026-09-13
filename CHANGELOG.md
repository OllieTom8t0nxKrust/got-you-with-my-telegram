# Master Changelog

All notable changes to this project will be documented in this file.

## [2.0.0] - 2026-09-13

### Added
- **Interactive Startup Menu:** Mode selection for [1] Simple Location Tracking, [2] Triangle Tracking (5+ min deep telemetry with Ctrl+C safe dump), and [3] Forensic Audio Recording (background RTP audio capture saved to `.wav`).
- **TraceRoute Network Hop Analysis:** Real-time hop visualization targeting the remote call answerer.
- **Telegram Geolocation Heuristics:** Signaling metadata profiling for precision positioning.
- **Strict Target Isolation:** Guaranteed focus exclusively on the remote call answerer, never leaking host machine metrics.
- **Expanded Test Suite:** Unit tests covering all v2.0 modules (`tests/test_got_you_with_my_telegram.py`).

## [1.2.0] - 2026-09-13

### Added
- Added comprehensive unit test suite in `tests/`.
- Added Python 3.12+ / 3.14 asyncio compatibility fix.
- Added optional IP-API Pro API key configuration and first-run validation.

### Changed
- Renamed script to `got-you-with-my-telegram.py` across project files, Dockerfile, and README.
- Enhanced root privilege checks and documentation for Telegram P2P call packet capture usage.

## [1.1.0] - 2026-08-31

### Added
- Created `develop` and `feature/initial-development` branches.
- Master changelog, frontend changelog, and backend changelog.

### Changed
- Updated `Dockerfile` to Ubuntu 24.04 with optimized python virtual environment setup and explicit dependency copying.
- Updated `README.md` with beautified project title, updated installation instructions for Ubuntu 24.04, and refined documentation.
- Updated `requirements.txt` with modern pinned dependency versions (`certifi`, `charset-normalizer`, `idna`, `lxml`, `packaging`, `requests`, `termcolor`, `urllib3`).
- Updated `.gitignore` to include `.vscode`, `.idea`, and `__pycache__`.
