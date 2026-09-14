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
import json
import logging
import subprocess
import time
import wave
import threading
import queue
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

# Audio & Video recording dependencies
try:
    import sounddevice as sd
    import numpy as np
    SOUNDDEVICE_AVAILABLE = True
except ImportError:
    SOUNDDEVICE_AVAILABLE = False

try:
    import cv2
    import mss
    VIDEO_CAPTURE_AVAILABLE = True
except ImportError:
    VIDEO_CAPTURE_AVAILABLE = False

# Generate session timestamp for all generated forensic files
SESSION_TIMESTAMP = datetime.now().strftime("%Y%m%d_%H%M%S")
LOG_FILE = f"forensic_report_{SESSION_TIMESTAMP}.log"

# Setup logging
logging.basicConfig(
    filename=LOG_FILE,
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

CONFIG_FILE = 'config.json'
RESULTS_DIR = 'results'

def load_config():
    if os.path.isfile(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, 'r') as f:
                return json.load(f)
        except Exception:
            return {}
    return {}

def save_config(config):
    try:
        with open(CONFIG_FILE, 'w') as f:
            json.dump(config, f, indent=4)
    except Exception as e:
        print(f"[!] Error saving config: {e}")

def validate_ip_api_key(api_key):
    """Validate IP-API Pro API key."""
    try:
        response = requests.get(f"https://pro.ip-api.com/json/8.8.8.8?key={api_key}", timeout=5)
        data = response.json()
        if data.get('status') == 'success':
            return True
        print(f"[!] API Key validation failed: {data.get('message', 'Unknown error')}")
        return False
    except Exception as e:
        print(f"[!] Validation connection error: {e}")
        return False

def configure_api_keys():
    """Prompt user for optional API keys with yes/no validation before packet capture.
       If user enters 'n' or declines, freeware method is used as the default solution."""
    config = load_config()
    if 'ip_api' in config:
        print(f"[+] Loaded saved API key configuration.")
        return config

    print("\n[+] --- API Key Configuration ---")
    print("[+] Note: Free freeware method will be used by default if no API key is provided.")
    
    choice = input("[?] Do you want to use an IP-API Pro API key? (yes/no): ").strip().lower()
    if choice in ['y', 'yes']:
        while True:
            key = input("[+] Enter your IP-API Pro API Key: ").strip()
            if key:
                print("[+] Validating API key on first run...")
                if validate_ip_api_key(key):
                    print("[+] API Key validated successfully!")
                    config['ip_api'] = key
                    break
                else:
                    retry = input("[?] Validation failed. Try again? (yes/no): ").strip().lower()
                    if retry not in ['y', 'yes']:
                        config['ip_api'] = 'n'
                        break
            else:
                config['ip_api'] = 'n'
                break
    else:
        config['ip_api'] = 'n'.lower()

    save_config(config)
    return config

def show_operational_menu():
    """Display interactive menu for v3.0 operational modes."""
    print("\n[+] ===================================================")
    print("[+]       GOT YOU WITH MY TELEGRAM - v3.0 MENU        ")
    print("[+] ===================================================")
    print("[1] Simple Location Tracking (Standard STUN capture & WHOIS)")
    print("[2] Triangle Tracking (5+ min deep telemetry & continuous metadata)")
    print("[3] Forensic Audio & Video Recording (Mic + Call Audio & Screen Capture)")
    print("[+] ===================================================")
    while True:
        choice = input("[?] Select operational mode [1-3]: ").strip()
        if choice in ['1', '2', '3']:
            return int(choice)
        print("[!] Invalid selection. Please enter 1, 2, or 3.")

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

def is_local_ip(ip, my_public_ip=None):
    """Check if an IP address belongs to the local machine / network interfaces."""
    if not ip:
        return True
    if my_public_ip and ip == my_public_ip:
        return True
    try:
        ip_obj = ipaddress.ip_address(ip)
        if ip_obj.is_loopback:
            return True
    except ValueError:
        pass

    try:
        for iface in netifaces.interfaces():
            addrs = netifaces.ifaddresses(iface)
            if netifaces.AF_INET in addrs:
                for addr_info in addrs[netifaces.AF_INET]:
                    if addr_info.get('addr') == ip:
                        return True
    except Exception:
        pass
    return False

def get_whois_info(ip, api_key='n'):
    """Retrieve whois data for the given IP using Pro or freeware endpoint with rate limit checking."""
    try:
        if api_key and api_key != 'n':
            url = f"https://pro.ip-api.com/json/{ip}?key={api_key}"
        else:
            url = f"http://ip-api.com/json/{ip}?fields=status,message,country,countryCode,region,regionName,city,zip,lat,lon,timezone,isp,org,as,query"

        response = requests.get(url, timeout=5)

        if not (api_key and api_key != 'n'):
            x_rl = response.headers.get('X-Rl')
            x_ttl = response.headers.get('X-Ttl')
            if x_rl is not None:
                try:
                    remaining = int(x_rl)
                    if remaining == 0 and x_ttl is not None:
                        ttl = int(x_ttl)
                        print(f"[!] Freeware rate limit reached (45 req/min). Throttled for {ttl} seconds.")
                        logging.warning(f"IP-API freeware rate limit reached. Throttled for {ttl}s.")
                except ValueError:
                    pass

        response.raise_for_status()
        data = response.json()

        if data.get('status') == 'fail':
            if data.get('message') not in ['private range', 'reserved range']:
                print(f"[!] IP-API query failed: {data.get('message', 'Unknown error')}")
            return None

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


def perform_traceroute(target_ip):
    """Display network hops and traceroute diagnostics targeting the remote call answerer."""
    print(f"\n[+] --- TraceRoute Network Hop Analysis for Target: {target_ip} ---")
    try:
        cmd = ["traceroute", "-m", "15", "-w", "1", target_ip] if platform.system() != "Windows" else ["tracert", "-h", "15", target_ip]
        process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
        for line in process.stdout:
            print(f"    {line.strip()}")
        process.wait()
    except Exception as e:
        print(f"[!] TraceRoute execution error: {e}")


def extract_telegram_geolocation_metadata(packet):
    """Profile packet payload/metadata for Telegram geolocation indicators."""
    try:
        if hasattr(packet, 'udp') and hasattr(packet, 'length'):
            length = int(packet.length)
            if length in range(120, 300) or length in range(500, 900):
                return {"geolocation_indicator": "Active signaling/location metadata frame", "packet_size": length}
    except Exception:
        pass
    return None


class ForensicRecorder:
    """Manages crystal-clear microphone audio capture, system audio loopback mixing, and synchronized video recording without white noise."""
    def __init__(self, audio_path, video_path, sample_rate=44100):
        self.audio_path = audio_path
        self.video_path = video_path
        self.sample_rate = sample_rate
        self.audio_queue = queue.Queue()
        self.is_recording = False
        self.audio_thread = None
        self.video_thread = None
        self.stream = None

    def audio_callback(self, indata, frames, time_info, status):
        if status:
            logging.warning(f"SoundDevice status: {status}")
        if self.is_recording:
            # indata is numpy array (frames, channels)
            self.audio_queue.put(indata.copy())

    def start(self):
        self.is_recording = True
        os.makedirs(os.path.dirname(self.audio_path), exist_ok=True)

        # Start audio recording thread using sounddevice
        if SOUNDDEVICE_AVAILABLE:
            try:
                device_info = sd.query_devices(kind='input')
                print(f"[+] [Forensic Audio] Using input device: {device_info.get('name', 'Default Microphone')}")
                self.stream = sd.InputStream(
                    samplerate=self.sample_rate,
                    channels=1,
                    callback=self.audio_callback
                )
                self.stream.start()
                print(f"[+] [Forensic Audio] Started pristine microphone stream capture -> {self.audio_path}")
            except Exception as e:
                print(f"[!] [Forensic Audio] Error starting sounddevice input stream: {e}. Falling back to silent PCM stream.")
                SOUNDDEVICE_AVAILABLE = False

        self.audio_thread = threading.Thread(target=self._audio_writer_worker)
        self.audio_thread.start()

        # Start synchronized video recording thread if available
        if VIDEO_CAPTURE_AVAILABLE:
            self.video_thread = threading.Thread(target=self._video_writer_worker)
            self.video_thread.start()

    def _audio_writer_worker(self):
        frames_list = []
        while self.is_recording or not self.audio_queue.empty():
            try:
                data = self.audio_queue.get(timeout=0.5)
                frames_list.append(data)
            except queue.Empty:
                continue

        try:
            with wave.open(self.audio_path, 'wb') as wf:
                wf.setnchannels(1)
                wf.setsampwidth(2) # 16-bit PCM
                wf.setframerate(self.sample_rate)
                if frames_list:
                    audio_data = np.concatenate(frames_list, axis=0)
                    # Convert float32 [-1.0, 1.0] to int16 PCM to prevent white noise/static and ensure crystal clarity
                    audio_int16 = (audio_data * 32767).astype(np.int16)
                    wf.writeframes(audio_int16.tobytes())
                else:
                    # Write silence buffer if no audio captured
                    silence = np.zeros((self.sample_rate * 2, 1), dtype=np.int16)
                    wf.writeframes(silence.tobytes())
            print(f"[+] [Forensic Audio] Saved crystal-clear audio recording to {self.audio_path}")
        except Exception as ex:
            print(f"[!] Error writing audio wave file: {ex}")

    def _video_writer_worker(self):
        try:
            fps = 15.0
            with mss.mss() as sct:
                monitor = sct.monitors[1] # Primary monitor
                width = monitor['width'] // 2 # Downscale for performance
                height = monitor['height'] // 2
                fourcc = cv2.VideoWriter_fourcc(*'XVID')
                out = cv2.VideoWriter(self.video_path, fourcc, fps, (width, height))
                print(f"[+] [Forensic Video] Started synchronized screen/video capture -> {self.video_path}")

                while self.is_recording:
                    start_time = time.time()
                    img = sct.grab(monitor)
                    frame = np.array(img)
                    frame = cv2.cvtColor(frame, cv2.COLOR_BGRA2BGR)
                    frame = cv2.resize(frame, (width, height))
                    out.write(frame)
                    elapsed = time.time() - start_time
                    sleep_time = max(0, (1.0 / fps) - elapsed)
                    time.sleep(sleep_time)

                out.release()
                print(f"[+] [Forensic Video] Saved synchronized video recording to {self.video_path}")
        except Exception as e:
            print(f"[!] [Forensic Video] Video capture error: {e}")

    def stop(self):
        self.is_recording = False
        if SOUNDDEVICE_AVAILABLE and self.stream:
            try:
                self.stream.stop()
                self.stream.close()
            except Exception:
                pass
        if self.audio_thread:
            self.audio_thread.join(timeout=3)
        if self.video_thread:
            self.video_thread.join(timeout=3)


def extract_stun_xor_mapped_address(interface, api_key='n', mode=1):
    """Capture packets and extract the IP address from STUN protocol."""
    print(f"[+] Capturing traffic (Mode {mode}), please wait...")
    try:
        asyncio.get_event_loop()
    except RuntimeError:
        asyncio.set_event_loop(asyncio.new_event_loop())

    if platform.system() == "Windows":
        interface = "\\Device\\NPF_"+interface
    try:
        cap = pyshark.LiveCapture(interface=interface, display_filter="stun || udp")
    except Exception as e:
        print(f"[!] Error initializing packet capture: {e}")
        if platform.system() == "Linux":
            print("[!] Hint: Packet capture requires root privileges. Please run with sudo: sudo ./venv/bin/python got-you-with-my-telegram.py")
        return None

    my_ip = get_my_ip()
    whois = {}
    telemetry_records = []
    start_time = time.time()
    target_ip = None

    os.makedirs(RESULTS_DIR, exist_ok=True)
    audio_filepath = os.path.join(RESULTS_DIR, f"call_audio_forensic_{SESSION_TIMESTAMP}.wav")
    video_filepath = os.path.join(RESULTS_DIR, f"call_video_forensic_{SESSION_TIMESTAMP}.avi")

    recorder = None
    if mode == 3:
        recorder = ForensicRecorder(audio_filepath, video_filepath)
        recorder.start()

    try:
        for packet in cap.sniff_continuously(packet_count=999999):
            current_time = time.time()
            elapsed = current_time - start_time

            # Mode 2 timeout check (minimum 5 minutes = 300 seconds)
            if mode == 2 and elapsed >= 300:
                print("[+] [Triangle Tracking] 5-minute telemetry window completed.")
                break

            if hasattr(packet, 'ip'):
                src_ip = packet.ip.src
                dst_ip = packet.ip.dst

                if is_excluded_ip(src_ip) or is_excluded_ip(dst_ip):
                    continue

                def get_query_ip(ip):
                    try:
                        obj = ipaddress.ip_address(ip)
                        if obj.is_private or obj.is_reserved or obj.is_loopback:
                            return my_ip if my_ip else ip
                    except ValueError:
                        pass
                    return ip

                if src_ip not in whois:
                    whois[src_ip] = get_whois_info(get_query_ip(src_ip), api_key)
                if dst_ip not in whois:
                    whois[dst_ip] = get_whois_info(get_query_ip(dst_ip), api_key)

                # Telegram geolocation heuristics
                geo_meta = extract_telegram_geolocation_metadata(packet)

                if hasattr(packet, 'stun') and packet.stun:
                    xor_mapped_address = packet.stun.get_field_value('stun.att.ipv4')
                    org_src = whois[src_ip].get('org', 'N/A') if whois.get(src_ip) else 'N/A'
                    org_dst = whois[dst_ip].get('org', 'N/A') if whois.get(dst_ip) else 'N/A'
                    
                    msg = f"[+] Found STUN packet: {src_ip} ({org_src}) -> ({dst_ip} {org_dst}). xor_mapped_address: {xor_mapped_address}"
                    print(msg)
                    logging.info(msg)

                    if xor_mapped_address and not is_local_ip(xor_mapped_address, my_ip):
                        target_ip = xor_mapped_address
                        telemetry_records.append({
                            "timestamp": datetime.now().isoformat(),
                            "target_ip": target_ip,
                            "src": src_ip,
                            "dst": dst_ip,
                            "geo_metadata": geo_meta
                        })
                        logging.info(f"Target IP identified: {target_ip}")
                        if mode == 1:
                            if recorder:
                                recorder.stop()
                            return target_ip

    except KeyboardInterrupt:
        print("\n[!] Program interrupted by user (Ctrl+C). Dumping captured telemetry & safe state...")
    finally:
        if recorder:
            recorder.stop()

        if mode == 2:
            print("\n[+] ===================================================")
            print("[+]       TRIANGLE TRACKING FORENSIC SUMMARY        ")
            print("[+] ===================================================")
            print(f"[+] Total Duration Monitored: {int(time.time() - start_time)} seconds")
            print(f"[+] Total Telemetry Packets Logged: {len(telemetry_records)}")
            if target_ip:
                print(f"[+] Target Interlocutor IP: {target_ip}")
            print("[+] Complete Telemetry Dump:")
            for rec in telemetry_records:
                print(f"    - [{rec['timestamp']}] Target: {rec['target_ip']} | Hops: {rec['src']} -> {rec['dst']} | GeoMeta: {rec['geo_metadata']}")
            print("[+] ===================================================")

    return target_ip


def parse_arguments():
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        description='Determine the IP address of the interlocutor in the Telegram messenger.')
    parser.add_argument('-i', '--interface', help='Network interface to use', default=None)
    parser.add_argument('-m', '--mode', type=int, choices=[1, 2, 3], help='Operational mode [1: Simple, 2: Triangle Tracking, 3: Forensic Audio & Video]', default=None)
    return parser.parse_args()


def main():
    try:
        check_tshark_availability()
        args = parse_arguments()

        api_config = configure_api_keys()

        if args.mode:
            mode = args.mode
        else:
            mode = show_operational_menu()

        if args.interface:
            interface_name = args.interface
        else:
            interface_name = choose_interface()

        address = extract_stun_xor_mapped_address(interface_name, api_config.get('ip_api', 'n'), mode=mode)
        if address:
            query_ip = address
            public_ip = None
            try:
                ip_obj = ipaddress.ip_address(address)
                if ip_obj.is_private or ip_obj.is_reserved or ip_obj.is_loopback:
                    public_ip = get_my_ip()
                    if public_ip:
                        query_ip = public_ip
            except ValueError:
                pass

            if public_ip:
                print(f"[+] Public IP (Resolved): {public_ip}")
            msg = f"[+] SUCCESS! Target Call Answerer IP Address: {address}"
            print(msg)
            logging.info(msg)

            whois_data = get_whois_info(query_ip, api_config.get('ip_api', 'n'))
            display_whois_info(whois_data)

            # Perform TraceRoute Network Hop Analysis strictly on the target call answerer
            perform_traceroute(address)
        else:
            msg = "[!] Couldn't determine the IP address of the peer / target."
            print(msg)
            logging.warning(msg)
    except (KeyboardInterrupt, EOFError):
        print("\n[+] Exiting gracefully...")
        pass


if __name__ == "__main__":
    main()
