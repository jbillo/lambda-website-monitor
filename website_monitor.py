from botocore.vendored.requests import request, HTTPError


def handler(event, _context):
    if 'url' not in event:
        raise ValueError("Missing 'url' in event: {}".format(event))

    method = event.get('method', 'head').lower()
    timeout = int(event.get('timeout', 30))
    response = request(method, event['url'], timeout=timeout)
    try:
        response.raise_for_status()
    except HTTPError as e:
        print("HTTP failure code {code} contacting URL {url}".format(
            code=response.status_code,
            url=event['url']
        ))
        raise e

    print("HTTP success code {code} contacting URL {url}".format(
        code=response.status_code, url=event['url'])
    )
