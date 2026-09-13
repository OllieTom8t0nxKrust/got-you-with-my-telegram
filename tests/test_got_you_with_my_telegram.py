import unittest
import socket
import os
import sys
import importlib.util
from unittest.mock import patch, MagicMock

# Load got-you-with-my-telegram.py dynamically because of hyphens in filename
script_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../got-you-with-my-telegram.py"))
spec = importlib.util.spec_from_file_location("got_you_with_my_telegram", script_path)
got_you_with_my_telegram = importlib.util.module_from_spec(spec)
sys.modules["got_you_with_my_telegram"] = got_you_with_my_telegram
spec.loader.exec_module(got_you_with_my_telegram)

class TestGotYouWithMyTelegram(unittest.TestCase):

    def test_is_excluded_ip(self):
        # Telegram excluded network example: 91.108.13.0/24
        self.assertTrue(got_you_with_my_telegram.is_excluded_ip("91.108.13.5"))
        # Non-excluded public IP
        self.assertFalse(got_you_with_my_telegram.is_excluded_ip("8.8.8.8"))
        # Invalid IP
        self.assertTrue(got_you_with_my_telegram.is_excluded_ip("invalid-ip"))

    def test_is_local_ip(self):
        self.assertTrue(got_you_with_my_telegram.is_local_ip("127.0.0.1"))
        self.assertTrue(got_you_with_my_telegram.is_local_ip("203.0.113.1", my_public_ip="203.0.113.1"))
        self.assertFalse(got_you_with_my_telegram.is_local_ip("8.8.8.8", my_public_ip="203.0.113.1"))

    def test_extract_telegram_geolocation_metadata(self):
        packet = MagicMock()
        packet.length = "150"
        meta = got_you_with_my_telegram.extract_telegram_geolocation_metadata(packet)
        self.assertIsNotNone(meta)
        self.assertEqual(meta["packet_size"], 150)

        packet.length = "50"
        meta_none = got_you_with_my_telegram.extract_telegram_geolocation_metadata(packet)
        self.assertIsNone(meta_none)

    @patch('got_you_with_my_telegram.subprocess.Popen')
    def test_perform_traceroute(self, mock_popen):
        mock_process = MagicMock()
        mock_process.stdout = [" 1  192.168.1.1  1ms\n"]
        mock_process.wait.return_value = 0
        mock_popen.return_value = mock_process

        got_you_with_my_telegram.perform_traceroute("8.8.8.8")
        mock_popen.assert_called_once()

    @patch('builtins.input', return_value='2')
    def test_show_operational_menu(self, mock_input):
        mode = got_you_with_my_telegram.show_operational_menu()
        self.assertEqual(mode, 2)

    @patch('got_you_with_my_telegram.socket.gethostbyaddr')
    def test_get_hostname(self, mock_gethostbyaddr):
        mock_gethostbyaddr.return_value = ("example.com", [], [])
        hostname = got_you_with_my_telegram.get_hostname("8.8.8.8")
        self.assertEqual(hostname, "example.com")

        mock_gethostbyaddr.side_effect = socket.herror
        self.assertIsNone(got_you_with_my_telegram.get_hostname("1.2.3.4"))

    @patch('got_you_with_my_telegram.requests.get')
    def test_get_my_ip(self, mock_requests_get):
        mock_response = MagicMock()
        mock_response.text = "203.0.113.195\n"
        mock_requests_get.return_value = mock_response

        ip = got_you_with_my_telegram.get_my_ip()
        self.assertEqual(ip, "203.0.113.195")

        mock_requests_get.side_effect = Exception("Network error")
        self.assertIsNone(got_you_with_my_telegram.get_my_ip())

    @patch('got_you_with_my_telegram.requests.get')
    @patch('got_you_with_my_telegram.get_hostname')
    def test_get_whois_info_freeware(self, mock_get_hostname, mock_requests_get):
        mock_response = MagicMock()
        mock_response.headers = {'X-Rl': '44', 'X-Ttl': '60'}
        mock_response.json.return_value = {"status": "success", "country": "Canada", "org": "Videotron"}
        mock_requests_get.return_value = mock_response
        mock_get_hostname.return_value = "videotron.ca"

        data = got_you_with_my_telegram.get_whois_info("24.48.0.1", api_key='n')
        self.assertEqual(data["country"], "Canada")
        self.assertEqual(data["org"], "Videotron")

    @patch('got_you_with_my_telegram.requests.get')
    @patch('got_you_with_my_telegram.get_hostname')
    def test_get_whois_info_freeware_rate_limit(self, mock_get_hostname, mock_requests_get):
        mock_response = MagicMock()
        mock_response.headers = {'X-Rl': '0', 'X-Ttl': '30'}
        mock_response.json.return_value = {"status": "fail", "message": "rate limit exceeded"}
        mock_requests_get.return_value = mock_response

        data = got_you_with_my_telegram.get_whois_info("8.8.8.8", api_key='n')
        self.assertIsNone(data)

    @patch('got_you_with_my_telegram.requests.get')
    @patch('got_you_with_my_telegram.get_hostname')
    def test_get_whois_info_pro(self, mock_get_hostname, mock_requests_get):
        mock_response = MagicMock()
        mock_response.json.return_value = {"status": "success", "country": "United States", "org": "Google"}
        mock_requests_get.return_value = mock_response
        mock_get_hostname.return_value = "dns.google"

        data = got_you_with_my_telegram.get_whois_info("8.8.8.8", api_key="test-pro-key")
        self.assertEqual(data["country"], "United States")

        mock_requests_get.side_effect = Exception("API error")
        self.assertIsNone(got_you_with_my_telegram.get_whois_info("8.8.8.8", api_key="test-pro-key"))

    @patch('builtins.input', return_value='n')
    @patch('got_you_with_my_telegram.load_config', return_value={})
    @patch('got_you_with_my_telegram.save_config')
    def test_configure_api_keys_decline(self, mock_save, mock_load, mock_input):
        config = got_you_with_my_telegram.configure_api_keys()
        self.assertEqual(config['ip_api'], 'n')

if __name__ == '__main__':
    unittest.main()
