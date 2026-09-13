# Backend / Core Logic Changelog

All core script, packet capture, networking, and containerization changes.

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
