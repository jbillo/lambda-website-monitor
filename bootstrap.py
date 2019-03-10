import argparse

from website_monitor import handler

if __name__ == '__main__':
    # bootstrap a request, for testing the code locally
    parser = argparse.ArgumentParser(description='Bootstrap website_monitor script locally')
    parser.add_argument('url', help='Full URL to check')
    parser.add_argument('--method', default='HEAD', help='HTTP method to use to check URL')

    args = parser.parse_args()
    handler({
        'url': args.url,
        'method': args.method
    }, None)
