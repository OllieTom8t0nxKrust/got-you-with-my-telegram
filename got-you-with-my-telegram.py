# This script is intended to be used to determine the IP address of the interlocutor in the telegram messenger.
# You must have tshark installed to use it.
# Tested on macOS 13.4.1 and Ubuntu Linux 20.
# Probably will be working on android phone with root permissions and termux.
# by n0a 2020-2023
# https://n0a.pw

import ipaddress
import netifaces
import requests
import argparse
import platform
import pyshark
import socket
import sys
import os
import logging
import asyncio
if not hasattr(asyncio, 'SafeChildWatcher'):
    class SafeChildWatcher:
        pass
    asyncio.SafeChildWatcher = SafeChildWatcher
if not hasattr(asyncio, 'set_child_watcher'):
    def set_child_watcher(watcher):
        pass
    asyncio.set_child_watcher = set_child_watcher
if not hasattr(asyncio, 'get_child_watcher'):
    class DummyWatcher:
        def attach_loop(self, loop):
            pass
    def get_child_watcher():
        return DummyWatcher()
    asyncio.get_child_watcher = get_child_watcher
from datetime import datetime

# Setup logging
logging.basicConfig(
    filename='forensic_report.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def get_wireshark_install_path_from_registry():
    try:
        import winreg
        registry_key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r"Software\\Wow6432Node\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\Wireshark")
        value, _ = winreg.QueryValueEx(registry_key, "InstallLocation")
        winreg.CloseKey(registry_key)
        return value
    except WindowsError:
        return None

def check_tshark_availability():
    """Check Tshark install."""
    if platform.system() == "Linux" and os.geteuid() != 0:
        print("[!] Warning: You are not running as root. Packet capture on Linux requires root privileges. Please run with sudo.")

    wireshark_path = None
    if platform.system() == "Windows":
        wireshark_path = get_wireshark_install_path_from_registry()
    elif platform.system() == "Darwin":
        wireshark_path = "/Applications/Wireshark.app/Contents/MacOS"
    elif platform.system() == "Linux":
        wireshark_path = os.popen('which wireshark').read().strip()
        tshark_path = os.popen('which tshark').read().strip()
        if os.path.isfile(wireshark_path):
            wireshark_path = os.path.dirname(wireshark_path)
        elif os.path.isfile(tshark_path):
            wireshark_path = os.path.dirname(tshark_path)

    if not wireshark_path:
        os_type = platform.system()
        if os_type == "Linux":
            print("Install tshark first: sudo apt update && apt install tshark")
        elif os_type == "Darwin":  # macOS
            print("Install Wireshark first: https://www.wireshark.org/download.html")
        else:
            print("Please install tshark.")
        sys.exit(1)
    else:
        print("[+] tshark is available.")

# Telegram AS list of excluded IP ranges
EXCLUDED_NETWORKS = ['91.108.13.0/24', '149.154.160.0/21', '149.154.160.0/22',
                     '149.154.160.0/23', '149.154.162.0/23', '149.154.164.0/22',
                     '149.154.164.0/23', '149.154.166.0/23', '149.154.168.0/22',
                     '149.154.172.0/22', '185.76.151.0/24', '91.105.192.0/23',
                     '91.108.12.0/22', '91.108.16.0/22', '91.108.20.0/22',
                     '91.108.4.0/22', '91.108.56.0/22', '91.108.56.0/23',
                     '91.108.58.0/23', '91.108.8.0/22', '95.161.64.0/20']


def get_hostname(ip):
    """Retrieve hostname for the given IP."""
    try:
        return socket.gethostbyaddr(ip)[0]
    except (socket.herror, socket.gaierror, socket.timeout):
        return None

def get_my_ip():
    """Retrieve the external IP address."""
    try:
        response = requests.get('https://icanhazip.com', timeout=5)
        response.raise_for_status()
        return response.text.strip()
    except Exception as e:
        print(f"[!] Error fetching external IP: {e}")
        logging.error(f"Error fetching external IP: {e}")
        return None

def get_whois_info(ip):
    """Retrieve whois data for the given IP."""
    try:
        response = requests.get(f"http://ip-api.com/json/{ip}", timeout=5)
        response.raise_for_status()
        data = response.json()

        # Get the hostname using the socket library
        hostname = get_hostname(ip)
        if hostname:
            print(f"[+] Hostname: {hostname}")

        return data
    except Exception as e:
        print(f"[!] Error fetching whois data: {e}")
        logging.error(f"Error fetching whois data for {ip}: {e}")
        return None


def display_whois_info(data, log=True):
    """Display the fetched whois data."""
    if not data:
        return

    info = f"""
[!] Country: {data.get('country', 'N/A')}
[!] Country Code: {data.get('countryCode', 'N/A')}
[!] Region: {data.get('region', 'N/A')}
[!] Region Name: {data.get('regionName', 'N/A')}
[!] City: {data.get('city', 'N/A')}
[!] Zip Code: {data.get('zip', 'N/A')}
[!] Latitude: {data.get('lat', 'N/A')}
[!] Longitude: {data.get('lon', 'N/A')}
[!] Time Zone: {data.get('timezone', 'N/A')}
[!] ISP: {data.get('isp', 'N/A')}
[!] Organization: {data.get('org', 'N/A')}
[!] AS: {data.get('as', 'N/A')}
"""
    print(info)
    if log:
        logging.info(f"Whois data: {info}")


def is_excluded_ip(ip):
    """Check if IP is in the excluded list."""
    try:
        ip_obj = ipaddress.ip_address(ip)
        for network in EXCLUDED_NETWORKS:
            if ip_obj in ipaddress.ip_network(network):
                return True
        return False
    except ValueError:
        return True


def choose_interface():
    """Prompt the user to select a network interface."""
    interfaces = netifaces.interfaces()
    print("[+] Available interfaces:")
    for idx, iface in enumerate(interfaces, 1):
        print(f"{idx}. {iface}")
        try:
            ip_address = netifaces.ifaddresses(iface)[netifaces.AF_INET][0]['addr']
            print(f"[+] Selected interface: {iface} IP address: {ip_address}")
        except KeyError:
            print("[!] Unable to retrieve IP address for the selected interface.")

    choice = int(input("[+] Enter the number of the interface you want to use: "))
    return interfaces[choice - 1]


def extract_stun_xor_mapped_address(interface):
    """Capture packets and extract the IP address from STUN protocol."""
    print("[+] Capturing traffic, please wait...")
    try:
        asyncio.get_event_loop()
    except RuntimeError:
        asyncio.set_event_loop(asyncio.new_event_loop())

    if platform.system() == "Windows":
        interface = "\\Device\\NPF_"+interface
    try:
        cap = pyshark.LiveCapture(interface=interface, display_filter="stun")
    except Exception as e:
        print(f"[!] Error initializing packet capture: {e}")
        if platform.system() == "Linux":
            print("[!] Hint: Packet capture requires root privileges. Please run with sudo: sudo ./venv/bin/python got-you-with-my-telegram.py")
        return None
    my_ip = get_my_ip()
    resolved = {}
    whois = {}

    for packet in cap.sniff_continuously(packet_count=999999):
        if hasattr(packet, 'ip'):
            src_ip = packet.ip.src
            dst_ip = packet.ip.dst

            if is_excluded_ip(src_ip) or is_excluded_ip(dst_ip):
                continue

            if src_ip not in resolved:
                resolved[src_ip] = f"{src_ip}({get_hostname(src_ip)})"
            if dst_ip not in resolved:
                resolved[dst_ip] = f"{dst_ip}({get_hostname(dst_ip)})"
            if src_ip not in whois:
                whois[src_ip] = get_whois_info(src_ip)
            if dst_ip not in whois:
                whois[dst_ip] = get_whois_info(dst_ip)
            if hasattr(packet, 'stun') and packet.stun:
                xor_mapped_address = packet.stun.get_field_value('stun.att.ipv4')
                org_src = whois[src_ip].get('org', 'N/A') if whois.get(src_ip) else 'N/A'
                org_dst = whois[dst_ip].get('org', 'N/A') if whois.get(dst_ip) else 'N/A'
                msg = f"[+] Found STUN packet: {resolved[src_ip]} ({org_src}) -> ({resolved[dst_ip]} {org_dst}). it's xor_mapped_address: {xor_mapped_address}"
                print(msg)
                logging.info(msg)
                if xor_mapped_address:
                    if xor_mapped_address != my_ip:
                        logging.info(f"Target IP identified: {xor_mapped_address}")
                        return xor_mapped_address
    return None


def parse_arguments():
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        description='Determine the IP address of the interlocutor in the Telegram messenger.')
    parser.add_argument('-i', '--interface', help='Network interface to use', default=None)
    return parser.parse_args()


def main():
    try:
        check_tshark_availability()
        args = parse_arguments()

        if args.interface:
            interface_name = args.interface
        else:
            interface_name = choose_interface()

        address = extract_stun_xor_mapped_address(interface_name)
        if address:
            msg = f"[+] SUCCESS! IP Address: {address}"
            print(msg)
            logging.info(msg)
            whois_data = get_whois_info(address)
            display_whois_info(whois_data)
        else:
            msg = "[!] Couldn't determine the IP address of the peer."
            print(msg)
            logging.warning(msg)
    except (KeyboardInterrupt, EOFError):
        print("\n[+] Exiting gracefully...")
        pass


if __name__ == "__main__":
    main()
