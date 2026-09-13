# Master Changelog

All notable changes to this project will be documented in this file.

## [1.2.0] - 2026-09-13

### Added
- Added comprehensive unit test suite in `tests/`.
- Added Python 3.12+ / 3.14 asyncio compatibility fix.

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
