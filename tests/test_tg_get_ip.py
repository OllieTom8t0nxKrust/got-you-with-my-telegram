import unittest
import socket
from unittest.mock import patch, MagicMock
import tg_get_ip

class TestTgGetIp(unittest.TestCase):

    def test_is_excluded_ip(self):
        # Telegram excluded network example: 91.108.13.0/24
        self.assertTrue(tg_get_ip.is_excluded_ip("91.108.13.5"))
        # Non-excluded public IP
        self.assertFalse(tg_get_ip.is_excluded_ip("8.8.8.8"))
        # Invalid IP
        self.assertTrue(tg_get_ip.is_excluded_ip("invalid-ip"))

    @patch('tg_get_ip.socket.gethostbyaddr')
    def test_get_hostname(self, mock_gethostbyaddr):
        mock_gethostbyaddr.return_value = ("example.com", [], [])
        hostname = tg_get_ip.get_hostname("8.8.8.8")
        self.assertEqual(hostname, "example.com")

        mock_gethostbyaddr.side_effect = socket.herror
        self.assertIsNone(tg_get_ip.get_hostname("1.2.3.4"))

    @patch('tg_get_ip.requests.get')
    def test_get_my_ip(self, mock_requests_get):
        mock_response = MagicMock()
        mock_response.text = "203.0.113.195\n"
        mock_requests_get.return_value = mock_response

        ip = tg_get_ip.get_my_ip()
        self.assertEqual(ip, "203.0.113.195")

        mock_requests_get.side_effect = Exception("Network error")
        self.assertIsNone(tg_get_ip.get_my_ip())

    @patch('tg_get_ip.requests.get')
    @patch('tg_get_ip.get_hostname')
    def test_get_whois_info(self, mock_get_hostname, mock_requests_get):
        mock_response = MagicMock()
        mock_response.json.return_value = {"country": "United States", "countryCode": "US", "org": "Google"}
        mock_requests_get.return_value = mock_response
        mock_get_hostname.return_value = "dns.google"

        data = tg_get_ip.get_whois_info("8.8.8.8")
        self.assertEqual(data["country"], "United States")
        self.assertEqual(data["org"], "Google")

        mock_requests_get.side_effect = Exception("API error")
        self.assertIsNone(tg_get_ip.get_whois_info("8.8.8.8"))

if __name__ == '__main__':
    unittest.main()
