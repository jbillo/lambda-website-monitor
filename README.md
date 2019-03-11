# lambda-website-monitor
Yet another tool to monitor (non-AWS) websites using AWS Lambda

## Background
There are *a lot* of tutorials out there discussing how you can monitor website uptime using a simple Lambda function. 
Unfortunately a number of them have not kept up with recent AWS developments, use older languages and libraries or
encourage awful security practices or program behaviours:

* Hard-coding AWS credentials (AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY) directly in the Lambda function
* Giving publish permissions to the SNS topic to everyone
* Having the Lambda function itself publish failures to SNS, rather than raising an exception and letting
CloudWatch handle what comes next

The goal with this project was to provide a simple `check-http` Nagios replacement for monitoring websites of friends,
family and well-wishers where the tool was not hosted in the same Newark, NJ datacenter as all the Linodes in question. 
An additional goal was not to pay $40 US/month/website for simple HTTP checks.

Along the way I figured I'd CloudFormation it up a bit, because managing AWS resources manually just means you'll
leave a few of them around when you're done and be very confused about your bill.

## Installation
* Run `python cloudformation/build_template.py` from the root directory to create the `lambda-website-monitor.yaml`
file, which will contain the inline Lambda code.
* Deploy the `cloudformation/lambda-website-monitor.yaml` CloudFormation template to the desired region in your AWS 
account. Note that SMS support is only available in the following regions, so despite my love for us-east-2 I've
picked a different region:  
<https://docs.aws.amazon.com/sns/latest/dg/sms_supported-countries.html>

## Deployment Notes
* To run locally, build and activate a venv and then `pip install boto3==1.7.74`. Then run `python bootstrap.py`
with the desired URL. See `bootstrap.py` for additional parameters.
* The Lambda function creates a CloudWatch Logs log group with infinite retention. Adjust this afterward. Possible
feature request to AWS? (As well as being able to specify a specific CWL log group for Lambda output.)

## Code Notes
* Lambda currently uses boto3 1.7.74: <https://docs.aws.amazon.com/lambda/latest/dg/current-supported-versions.html>.
We can use `botocore.vendored.requests` (2.7.0) since botocore is a dependency. 

## Possible Improvements
Feel free to send a pull request for any improvements you might think of, including:
* Multiple checks of remote host before firing an alert
* Support for checking multiple websites/URLs
* Minification of code in .yaml template, as well as removal of comments in final output file

## References and Resources
Other solutions and documentation I reviewed while developing this included:

* AWS documentation (mainly CloudFormation, Lambda and IAM)
* <https://marcelog.github.io/articles/aws_lambda_check_website_http_online.html>
* <https://medium.com/@mrdoro/aws-lambda-as-the-website-monitoring-tool-184b09202ae2>
* <https://github.com/mrdoro/AWS-Lambda-website-monitoring/blob/master/WebsiteCheck.py>
* <https://medium.com/@pentacent/serverless-monitoring-of-apps-websites-with-aws-lambda-5431e6713a66>
* <https://hackernoon.com/creating-a-website-monitoring-service-in-half-an-hour-using-lambdas-4f64fb199df3>
* <https://github.com/neilspink/aws-lambda-website-status-checking/blob/master/online-check.py>
* <https://github.com/base2Services/aws-lambda-http-check/blob/develop/handler.py>
* <https://stackoverflow.com/questions/37786384/how-to-call-a-list-of-aws-lambda-permissions-for-a-function>
