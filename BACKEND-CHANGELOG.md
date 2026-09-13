# Backend / Core Logic Changelog

All core script, packet capture, networking, and containerization changes.

## [1.2.0] - 2026-09-13

### Added
- Comprehensive unit test suite (`tests/test_got_you_with_my_telegram.py`) covering IP validation, host resolution, external IP fetching, and WHOIS lookup with mocking.
- Compatibility fallback for Python 3.12+ / 3.14 missing `asyncio.get_child_watcher`.
- Root privilege check and clean exception handling for `tshark` packet capture initialization.
- Optional IP-API Pro API key configuration prompt with validation on first run and yes/no handling (lowercased `'n'` fallback).

### Changed
- Standardized and renamed main executable script to `got-you-with-my-telegram.py`.
- Updated `Dockerfile` and `README.md` to reference `got-you-with-my-telegram.py` and added clear usage guidelines for capturing Telegram P2P calls with `sudo`.

## [1.1.0] - 2026-08-31

### Added
- Isolated Python virtual environment inside Docker container (`/telegram-get-remote-ip/venv`).

### Changed
- Upgraded Docker base image from `ubuntu:20.04` to `ubuntu:24.04`.
- Streamlined pip installation in Dockerfile with `--no-cache-dir`.
- Updated Python dependencies (`requirements.txt`) to newer secure and compatible package versions.
- Refined STUN packet capture and exclusion network filtering logic in `got-you-with-my-telegram.py`.
