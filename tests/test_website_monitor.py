# Note: These are not unit tests - they require Internet connectivity and depend on external resources.
# This is more just to prove out that the handler works locally.

import unittest
from unittest.mock import patch

import website_monitor


class TestWebsiteMonitor(unittest.TestCase):
    @staticmethod
    def _run_event(url, timeout=None):
        event = {'url': url}
        if timeout:
            event['timeout'] = timeout
        return website_monitor.handler(event, None)

    def test_200(self):
        url = 'https://httpbin.org/status/200'
        result = self._run_event(url)
        self.assertIn(url, result['successes'])

    def test_multi_200(self):
        result = self._run_event('http://example.com http://example.org')
        self.assertIn('http://example.com', result['successes'])
        self.assertIn('http://example.org', result['successes'])

    @patch.object(website_monitor, '_publish_errors')
    def test_404(self, pub_error):
        url = 'https://httpbin.org/status/404'
        result = self._run_event(url)
        pub_error.assert_called_once()
        self.assertIn(url, result['errors'])

    @patch.object(website_monitor, '_publish_errors')
    def test_dns_failure(self, pub_error):
        url = 'http://dnsfailure.example'
        result = self._run_event(url)
        pub_error.assert_called_once()
        self.assertIn(url, result['errors'])

    @patch.object(website_monitor, '_publish_errors')
    def test_bad_ssl(self, pub_error):
        url = 'https://self-signed.badssl.com/'
        result = self._run_event(url)
        pub_error.assert_called_once()
        self.assertIn(url, result['errors'])

    @patch.object(website_monitor, '_publish_errors')
    def test_timeout(self, pub_error):
        url = 'https://google.com'
        result = self._run_event(url, timeout=0.00001)
        pub_error.assert_called_once()
        self.assertIn(url, result['errors'])

    @patch.object(website_monitor, '_publish_errors')
    def test_multi_error(self, pub_error):
        result = self._run_event('https://httpbin.org/status/403 https://httpbin.org/status/404')
        pub_error.assert_called_once()
        self.assertIn('https://httpbin.org/status/403', result['errors'])
        self.assertIn('https://httpbin.org/status/404', result['errors'])


if __name__ == '__main__':
    unittest.main()
