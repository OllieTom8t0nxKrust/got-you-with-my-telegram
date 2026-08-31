# Backend / Core Logic Changelog

All core script, packet capture, networking, and containerization changes.

## [1.1.0] - 2026-08-31

### Added
- Isolated Python virtual environment inside Docker container (`/telegram-get-remote-ip/venv`).

### Changed
- Upgraded Docker base image from `ubuntu:20.04` to `ubuntu:24.04`.
- Streamlined pip installation in Dockerfile with `--no-cache-dir`.
- Updated Python dependencies (`requirements.txt`) to newer secure and compatible package versions.
- Refined STUN packet capture and exclusion network filtering logic in `tg_get_ip.py`.
