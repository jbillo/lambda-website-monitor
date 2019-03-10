# lambda-website-monitor
Yet another tool to monitor (non-AWS) websites using AWS Lambda

## Background
There are *a lot* of tutorials out there discussing how you can monitor website uptime using a simple Lambda function. 
Unfortunately a number of them have not kept up with recent AWS developments, use older languages and libraries or
encourage awful security practices or program behaviours:

* Hard-coding AWS credentials (AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY) directly in the Lambda function
* Giving publish permissions to the SNS topic permissions to everyone
* Having the Lambda function itself publish failures to SNS, rather than raising an exception and letting
CloudWatch handle what comes next

The goal with this project was to provide a simple `check-http` Nagios replacement for monitoring websites of friends,
family and well-wishers that was not hosted in the same Newark, NJ datacenter as all the Linodes in question. An
additional goal was not to pay $40 US/month/website for simple HTTP checks.

Along the way I figured I'd CloudFormation it up a bit, because managing AWS resources manually just means you'll
leave a few of them around when you're done and be very confused about your bill.

## Installation
* Run `python cloudformation/build_template.py` from the root directory to create the `lambda-website-monitor.yaml`
file, which will contain the inline Lambda code.
* Deploy the `cloudformation/lambda-website-monitor.yaml` CloudFormation template to the desired region in your AWS 
account. Note that SMS support is only available in the following regions:  
<https://docs.aws.amazon.com/sns/latest/dg/sms_supported-countries.html>


## Deployment Notes
* Lambda currently uses boto3 1.7.74: <https://docs.aws.amazon.com/lambda/latest/dg/current-supported-versions.html>.
We can use `botocore.vendored.requests` since botocore is a dependency.