# Note: These are not traditional unit tests - they require Internet connectivity.
# This is more just to prove out that the handler works.

import unittest
from unittest.mock import patch

import website_monitor


class TestWebsiteMonitor(unittest.TestCase):
    @staticmethod
    def _run_event(url):
        return website_monitor.handler({'url': url}, None)

    def test_200(self):
        self._run_event('https://httpbin.org/status/200')

    @patch.object(website_monitor, '_pub_error')
    def test_404(self, pub_error):
        self._run_event('https://httpbin.org/status/404')
        pub_error.assert_called_once()

    @patch.object(website_monitor, '_pub_error')
    def test_dns_failure(self, pub_error):
        self._run_event('http://dnsfailure.example')
        pub_error.assert_called_once()


if __name__ == '__main__':
    unittest.main()
