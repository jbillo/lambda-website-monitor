# 0.0.3
* Bump exact dependencies to match python3.7 Lambda execution environment (boto3 1.9.42)
* Add version number to template metadata

# 0.0.2
* Move to Python f'strings. Remove dependency on `requests` library as per deprecation warning (@rtkseagray)
* Remove global ERRORS dictionary as the Lambda container reuse caused the trigger to repeatedly fire, even after
an error condition was cleared.
* Limit subject when publishing to SNS to 100 characters.

# 0.0.1
* Initial tagged release for GitHub purposes. Just includes the built CloudFormation template. 