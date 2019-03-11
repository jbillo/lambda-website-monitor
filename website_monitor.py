import socket
from http.client import HTTPConnection
from http.client import HTTPException
from http.client import HTTPSConnection
from os import environ
from ssl import SSLError
from urllib.parse import urlparse

from boto3 import resource

ERRORS = {}


def request(method, url, timeout=None):
    scheme, host, path, params, query, fragment = urlparse(url)
    connection = None
    try:
        if scheme == 'https':
            connection = HTTPSConnection(host, timeout=timeout)
        else:
            connection = HTTPConnection(host, timeout=timeout)

        connection.request(method, url)
        return connection.getresponse()
    finally:
        if connection:
            connection.close()


def _add_error(url, exception):
    if isinstance(exception, HTTPException):
        error_type = 'HTTP'
    elif isinstance(exception, ConnectionError):
        error_type = 'Connection'
    elif isinstance(exception, socket.timeout):
        error_type = 'Timeout'
    elif isinstance(exception, SSLError):
        error_type = 'SSL'
    else:
        error_type = 'Unknown'

    code = 'N/A'
    headers = None
    if getattr(exception, 'response', None):
        code = exception.response.status_code
        headers = exception.response.headers

    msg = (
        f"{error_type} error contacting URL {url} (code:{code})"
        f"\nResponse headers: {headers}"
        f"\nOriginal exception: {exception}"
    )
    print(msg)
    ERRORS[url] = msg


def _publish_errors():
    arn = environ.get('SNS_TOPIC_ARN')
    if not arn:
        raise EnvironmentError('Missing SNS_TOPIC_ARN environment variable')

    topic = resource('sns').Topic(arn)

    publish_urls = ', '.join(sorted(ERRORS.keys()))
    publish_urls = publish_urls[0:-2]

    publish_msg = ''
    for msg in ERRORS.values():
        publish_msg += msg + '\n\n'

    return topic.publish(
        Message=publish_msg,
        Subject=f'WebsiteMonitor: Error contacting {publish_urls}'
    )


def handler(event, _context):
    url = event.get('url')
    # read from environment variable if not present in event
    if not url:
        url = environ.get('URL')

    # if still not present, bail
    if not url:
        raise ValueError(
            f"Missing URL in environment variable or event: {event}"
        )

    method = event.get('method', 'head').upper()
    timeout = float(event.get('timeout', 30.0))

    # split URL by spaces and repeat checks
    url = sorted(url.split(' '))
    for u in url:
        try:
            response = request(method, u, timeout=timeout)
            if response.status not in (200, 204):
                raise HTTPException()
        except Exception as e:
            _add_error(u, e)
            continue

        print(
            f"HTTP success code {response.status} contacting URL {u} "
            f"(headers: {response.headers})"
        )

    if ERRORS:
        _publish_errors()
