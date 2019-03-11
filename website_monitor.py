from botocore.vendored.requests import request, HTTPError, ConnectionError


def _pub_error(url, response, exception):
    from os import environ
    arn = environ.get('SNS_TOPIC_ARN')
    if not arn:
        raise EnvironmentError('Missing SNS_TOPIC_ARN environment variable')
    # boto3 operates with Lambda IAM role permissions
    from boto3 import resource
    topic = resource('sns').Topic(arn)
    if isinstance(exception, HTTPError):
        error_type = 'HTTP'
    elif isinstance(exception, ConnectionError):
        error_type = 'Connection'
    else:
        error_type = 'Unknown'

    if response and response.hasattr('status_code'):
        code = response.status_code
    else:
        code = 'N/A'

    msg = "{error_type} error contacting URL {url} (code:{code}): \n{exception}".format(
        url=url, error_type=error_type, code=code, exception=exception
    )
    print(msg)
    return topic.publish(
        Message=msg,
        Subject='WebsiteMonitor: {error_type} error {code} contacting {url}'.format(
            error_type=error_type, code=code, url=url
        )
    )


def handler(event, _context):
    if 'url' not in event:
        raise ValueError("Missing 'url' in event: {}".format(event))

    method = event.get('method', 'head').lower()
    timeout = int(event.get('timeout', 30))
    try:
        response = request(method, event['url'], timeout=timeout)
        response.raise_for_status()
    except (HTTPError, ConnectionError) as e:
        return _pub_error(event['url'], e.response, e)

    print("HTTP success code {code} contacting URL {url}".format(
        code=response.status_code, url=event['url'])
    )
