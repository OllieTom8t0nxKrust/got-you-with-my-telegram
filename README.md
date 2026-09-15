# Got You With My Telegram (v3.1)

A robust Python utility to determine the IP address of an interlocutor in Telegram messenger via STUN packet capture and network traffic analysis.

## Forensic Features
- **v3.1 Mass Dependency Upgrades & Vulnerability Remediation:** Pinned all 15 Python modules in `requirements.txt` to their latest stable release versions (`numpy==2.5.3`, `requests==2.34.2`, `urllib3==2.7.0`, `pyshark==0.6`, etc.) with full compatibility adaptation for NumPy 2.x and modern APIs.
- Automatic logging of captured peer IP addresses, timestamps, and WHOIS data to `forensic_report.log`.
- Enhanced exception handling for network operations.
- Improved Docker build stability.

TechCrunch covered the vulnerability: [Telegram is still leaking user IP addresses to contacts](https://techcrunch.com/2023/10/19/telegram-is-still-leaking-user-ip-addresses-to-contacts/).

This tool leverages `pyshark` and `tshark` to analyze UDP traffic and extract STUN XOR-mapped addresses when initiating direct calls in Telegram.

*Attention: To determine the IP address, both users must be in each other's contacts.*

## Requirements

- Python 3.10+
- `tshark` (Wireshark command-line tool)
- Netifaces and Pyshark dependencies

## Installation & Usage

### Local Setup (Ubuntu 24.04 / Linux)

```sh
sudo apt update
sudo apt install -y python3 python3-pip python3-venv tshark
git clone https://github.com/OllieTom8t0nxKrust/got-you-with-my-telegram
cd got-you-with-my-telegram
python3 -m venv venv
source ./venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
sudo ./venv/bin/python got-you-with-my-telegram.py
```

### Usage Instructions
1. Run the script with `sudo` privileges (`sudo ./venv/bin/python got-you-with-my-telegram.py`) since packet capture requires root access.
2. When prompted whether to use an IP-API Pro key, entering `n` (or declining) defaults to the **free freeware IP-API method** (`http://ip-api.com/json/{ip}?fields=...`) with built-in rate-limit header checking (`X-Rl` and `X-Ttl`).
3. Select your active network interface (e.g. `wlan0` or `enp8s0`).
4. Open Telegram and initiate a direct voice or video call with your contact (both users must be in each other's contacts).
5. Once the P2P STUN connection is established, the peer's IP address and WHOIS details will be displayed and logged to `forensic_report.log`.

### Docker Setup

```sh
docker build ./ -t telegram-get-remote-ip
docker run -it --cap-add=NET_RAW --cap-add=NET_ADMIN telegram-get-remote-ip
```

## Evolution Roadmap (v2.0 .todo)
The project evolution plan is tracked in `.todo` and includes:
- Interactive Menu System (Simple Location Tracking, Triangle Tracking for 5+ min deep telemetry with Ctrl+C dump, and Forensic Audio Recording to `.wav`).
- Telegram Geolocation integration for exact positioning.
- Network traceroute and hop visualization strictly targeting the remote call answerer.
- Guaranteed target isolation (focusing exclusively on the call answerer, never the host machine).

## Credits

- Original creator: [n0a](https://github.com/n0a)
- Windows support & improvements: [WonderMr](https://github.com/WonderMr)
