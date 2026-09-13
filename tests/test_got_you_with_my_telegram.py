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
    def test_get_whois_info(self, mock_get_hostname, mock_requests_get):
        mock_response = MagicMock()
        mock_response.json.return_value = {"country": "United States", "countryCode": "US", "org": "Google"}
        mock_requests_get.return_value = mock_response
        mock_get_hostname.return_value = "dns.google"

        data = got_you_with_my_telegram.get_whois_info("8.8.8.8")
        self.assertEqual(data["country"], "United States")
        self.assertEqual(data["org"], "Google")

        mock_requests_get.side_effect = Exception("API error")
        self.assertIsNone(got_you_with_my_telegram.get_whois_info("8.8.8.8"))

if __name__ == '__main__':
    unittest.main()
