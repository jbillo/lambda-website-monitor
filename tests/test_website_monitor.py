# Note: These are not unit tests - they require Internet connectivity and depend on external resources.
# This is more just to prove out that the handler works locally.

import unittest
from unittest.mock import patch

import website_monitor


class TestWebsiteMonitor(unittest.TestCase):
    @staticmethod
    def _run_event(url, timeout=None):
        # reset global errors each time
        website_monitor.ERRORS = {}
        event = {'url': url}
        if timeout:
            event['timeout'] = timeout
        return website_monitor.handler(event, None)

    def test_200(self):
        self._run_event('https://httpbin.org/status/200')

    def test_multi_200(self):
        self._run_event('http://example.com http://example.org')

    @patch.object(website_monitor, '_publish_errors')
    def test_404(self, pub_error):
        self._run_event('https://httpbin.org/status/404')
        pub_error.assert_called_once()

    @patch.object(website_monitor, '_publish_errors')
    def test_dns_failure(self, pub_error):
        self._run_event('http://dnsfailure.example')
        pub_error.assert_called_once()

    @patch.object(website_monitor, '_publish_errors')
    def test_bad_ssl(self, pub_error):
        self._run_event('https://self-signed.badssl.com/')
        pub_error.assert_called_once()

    @patch.object(website_monitor, '_publish_errors')
    def test_timeout(self, pub_error):
        self._run_event('https://google.com', timeout=0.00001)
        pub_error.assert_called_once()

    @patch.object(website_monitor, '_publish_errors')
    def test_multi_error(self, pub_error):
        self._run_event('https://httpbin.org/status/403 https://httpbin.org/status/404')
        pub_error.assert_called_once()
        self.assertIn('https://httpbin.org/status/403', website_monitor.ERRORS)
        self.assertIn('https://httpbin.org/status/404', website_monitor.ERRORS)


if __name__ == '__main__':
    unittest.main()
