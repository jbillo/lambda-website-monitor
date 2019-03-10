# Note: These are not traditional unit tests - they require Internet connectivity.
# This is more just to prove out that the handler works.

import unittest

from botocore.vendored.requests import HTTPError

from website_monitor import handler


class TestWebsiteMonitor(unittest.TestCase):
    @staticmethod
    def run_event(url):
        return handler({'url': url}, None)

    def test_200(self):
        self.run_event('https://httpbin.org/status/200')

    def test_404(self):
        with self.assertRaises(HTTPError):
            self.run_event('https://httpbin.org/status/404')


if __name__ == '__main__':
    unittest.main()
