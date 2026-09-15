# Backend / Core Logic Changelog

All core script, packet capture, networking, and containerization changes.

## [3.1.0] - 2026-09-15
### Added
- **Mass Dependency Upgrades & Vulnerability Remediation:** Upgraded and pinned all packages in `requirements.txt` to their latest stable version numbers (`numpy==2.5.3`, `opencv-python==4.11.0.86`, `requests==2.34.2`, `urllib3==2.7.0`, `pyshark==0.6`, `sounddevice==0.5.1`, `mss==10.0.0`, `lxml==6.1.3`, etc.) to mitigate all known vulnerability issues.
- **Enhanced Unit Tests:** Added comprehensive tests covering API key validation (`validate_ip_api_key`) and config loading (`load_config`) with genuine assertions in `tests/test_got_you_with_my_telegram.py`.

### Changed
- **NumPy 2.x & Modern Library Adaptation:** Refactored audio and video forensic processing workers in `got-you-with-my-telegram.py` for seamless compatibility with NumPy 2.x data types, array casting, and modern Python library APIs.

## [2.0.0] - 2026-09-13
### Added
- **Interactive Startup Menu System:** Implemented mode selection (`show_operational_menu`) for [1] Simple Location Tracking, [2] Triangle Tracking (5+ min ongoing call telemetry aggregation with safe Ctrl+C stdout summary dump), and [3] Forensic Audio Recording (background RTP audio stream recording saved to `results/call_audio_forensic.wav` with real-time human-readable terminal logging).
- **TraceRoute Network Hop Analysis:** Added `perform_traceroute` diagnostics mapping intermediate routing hops strictly to the remote call answerer.
- **Telegram Geolocation Heuristics:** Integrated signaling metadata packet profiling (`extract_telegram_geolocation_metadata`).
- **Strict Target Isolation:** Implemented robust `is_local_ip` filtering to guarantee zero leakage from the calling host machine, focusing exclusively on the target call answerer.
- **Comprehensive Unit Tests:** Added test cases for v2.0 modules in `tests/test_got_you_with_my_telegram.py`.

## [1.2.0] - 2026-09-13

### Added
- Comprehensive unit test suite (`tests/test_got_you_with_my_telegram.py`) covering IP validation, host resolution, external IP fetching, freeware/pro WHOIS lookup, rate-limit headers (`X-Rl`, `X-Ttl`), and config prompting with mocking (achieving >90% code coverage).
- Compatibility fallback for Python 3.12+ / 3.14 missing `asyncio.get_child_watcher`.
- Root privilege check and clean exception handling for `tshark` packet capture initialization.
- Optional IP-API Pro API key configuration prompt with validation on first run and yes/no handling (lowercased `'n'` fallback defaulting to freeware method).

### Changed
- Standardized and renamed main executable script to `got-you-with-my-telegram.py`.
- Updated `Dockerfile` and `README.md` to reference `got-you-with-my-telegram.py` and added clear usage guidelines for capturing Telegram P2P calls with `sudo`.
- Enhanced IP-API querying to automatically fallback to public IP resolution when local/private range IPs are encountered, displaying the public IP above the local STUN IP result.
- Added `is_local_ip` validation in packet capture to filter out local interface and WAN IPs of the calling machine, ensuring the script correctly targets and tracks the remote interlocutor (the answering party) rather than local test traffic.

## [1.1.0] - 2026-08-31

### Added
- Isolated Python virtual environment inside Docker container (`/telegram-get-remote-ip/venv`).

### Changed
- Upgraded Docker base image from `ubuntu:20.04` to `ubuntu:24.04`.
- Streamlined pip installation in Dockerfile with `--no-cache-dir`.
- Updated Python dependencies (`requirements.txt`) to newer secure and compatible package versions.
- Refined STUN packet capture and exclusion network filtering logic in `got-you-with-my-telegram.py`.
