# Got You With My Telegram

A robust Python utility to determine the IP address of an interlocutor in Telegram messenger via STUN packet capture and network traffic analysis.

## Overview

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
sudo ./venv/bin/python tg_get_ip.py
```

### Docker Setup

```sh
docker build ./ -t telegram-get-remote-ip
docker run -it --cap-add=NET_RAW --cap-add=NET_ADMIN telegram-get-remote-ip
```

## Credits

- Original creator: [n0a](https://github.com/n0a)
- Windows support & improvements: [WonderMr](https://github.com/WonderMr)
