from botocore.vendored.requests import request, HTTPError, ConnectionError, Timeout
from os import environ

ERRORS = {}


def _add_error(url, exception):
    if isinstance(exception, HTTPError):
        error_type = 'HTTP'
    elif isinstance(exception, ConnectionError):
        error_type = 'Connection'
    elif isinstance(exception, Timeout):
        error_type = 'Timeout'
    else:
        error_type = 'Unknown'

    code = 'N/A'
    headers = None
    if hasattr(exception, 'response') and exception.response is not None:
        code = exception.response.status_code
        headers = exception.response.headers

    msg = "{error_type} error contacting URL {url} (code:{code})" \
          "\nResponse headers: {headers}" \
          "\nOriginal exception: {exception}".format(url=url, code=code,
                                                     headers=headers, error_type=error_type,
                                                     exception=exception)
    print(msg)
    ERRORS[url] = msg


def _publish_errors():
    arn = environ.get('SNS_TOPIC_ARN')
    if not arn:
        raise EnvironmentError('Missing SNS_TOPIC_ARN environment variable')
    # boto3 operates with Lambda IAM role permissions
    from boto3 import resource
    topic = resource('sns').Topic(arn)

    publish_urls = ''
    for url in sorted(ERRORS.keys()):
        publish_urls = ', '.join(url)
        publish_urls = publish_urls[0:-2]

    publish_msg = ''
    for msg in ERRORS.values():
        publish_msg += msg + '\n\n'

    return topic.publish(
        Message=publish_msg,
        Subject='WebsiteMonitor: Error contacting {url}'.format(url=publish_urls)
    )


def handler(event, _context):
    url = event.get('url')
    # read from environment variable if not present in event
    if not url:
        url = environ.get('URL')

    # if still not present, bail
    if not url:
        raise ValueError("Missing URL in environment variable or event: {}".format(event))

    method = event.get('method', 'head').lower()
    timeout = float(event.get('timeout', 30.0))

    # split URL by spaces and repeat checks
    url = sorted(url.split(' '))
    for u in url:
        try:
            response = request(method, u, timeout=timeout)
            response.raise_for_status()
        except (HTTPError, ConnectionError, Timeout) as e:
            _add_error(u, e)
            continue

        print("HTTP success code {code} contacting URL {url} (headers: {headers})".format(
            code=response.status_code, url=u, headers=response.headers)
        )

    if ERRORS:
        _publish_errors()
