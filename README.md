# lambda-website-monitor
Yet another tool to monitor (non-AWS) websites using AWS Lambda, CloudWatch and CloudFormation

## Background
There are *a lot* of tutorials out there discussing how you can monitor website uptime using a simple Lambda function. 
Unfortunately a number of them have not kept up with recent AWS developments, use older languages and libraries or
encourage awful security practices or program behaviours:

* Hard-coding AWS credentials (AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY) directly in the Lambda function
* Giving publish permissions to the SNS topic to everyone
    * This is further complicated with SNS topic policies vs. IAM policies for SNS: 
    <https://docs.aws.amazon.com/sns/latest/dg/sns-using-identity-based-policies.html>

The goal with this project was to provide a simple `check-http` Nagios replacement for monitoring websites of friends,
family and well-wishers where the tool was not hosted in the same Newark, NJ datacenter as all the Linodes in question. 
An additional goal was not to pay $40 US/month/website for simple HTTP checks.

Along the way I figured I'd CloudFormation it up a bit, because managing AWS resources manually just means you'll
leave a few of them around when you're done and be very confused about your bill.

## Installation
* Run `python cloudformation/build_template.py` from the root directory to create the `lambda-website-monitor.yaml`
file, which will contain the inline Lambda code. 
    * Alternatively, pick a GitHub release of the .yaml template 
    (<https://github.com/jbillo/lambda-website-monitor/releases>) that seems reasonable, if you don't want to build
    locally.
* Deploy the `cloudformation/lambda-website-monitor.yaml` CloudFormation template to the desired region in your AWS 
account. Note that SMS support is only available in the following regions, so despite my love for us-east-2 I've
picked a different region:  
<https://docs.aws.amazon.com/sns/latest/dg/sms_supported-countries.html>
* The Lambda function creates a CloudWatch Logs log group with infinite retention. Adjust this afterward. Possible
feature request to AWS? (As well as being able to specify a specific CWL log group for Lambda output.)

## Upgrade notes
Follow the installation instructions, but instead of creating a new CloudFormation stack, update the existing stack.

## Running locally
* To run locally, build and activate a venv and then `pip install -r requirements.txt`. Then run `python bootstrap.py`
with the desired URL. See `bootstrap.py` for additional parameters.

## Development notes and decisions

### CloudWatch Alarms on error-like HTTP status codes
A somewhat-common behaviour in tutorials that I didn't understand was having the Lambda function publish failures to 
the SNS topic, rather than just raising an exception and letting the `Errors` metric for the function trigger a 
CloudWatch alarm. When I implemented this behaviour at first, the email message that came to the SNS topic had no 
additional details about the specific remote site, and you couldn't insert any custom messaging.

As a result, I've since changed my thinking on this, and errors (connection, HTTP, TLS) will now also poke the
SNS topic in question using boto3 with a friendlier message. Function invocation failures (none in past 10 minutes) and
other exceptions will still fire a generic CloudWatch alarm message to the topic, at which point the onus is on the
operator to investigate CloudWatch Logs and figure out what's going on.

### Previous use of `requests` library
We previously used `botocore.vendored.requests` (2.7.0) since botocore is a dependency of boto3, and `requests` was
included. However, this approach is deprecated, and we don't want to directly add a dependency on `requests`.
This lets us embed the Lambda code directly in the CloudFormation template without creating a zipped package and 
uploading it to S3. 

### Don't use global variables
Should go without saying, but CloudWatch Events at a 5-minute interval can keep the Firecracker container warm.
As a result, when we stored errors in a global variable outside the handler, the same failure message would fire every
5 minutes without clearing - even if URLs were updated or the error condition was clear.

## AWS costs
* *Lambda*: Should fall within the always-free tier of 1,000,000 requests/month and 400,000 GB/seconds of compute time 
per month.
    * At a 5-minute invocation interval, that's 12 times per hour, or 8,640 invocations in a 30-day month; 
    well under the million-request limit. 
    * At 128MB allocated memory, you get 3,200,000 seconds/month; assuming the function always times out at 35
    seconds of runtime and you do nothing to stop it, that's 302,400 seconds, so about 10% of your free tier.
    * My checks on a single crappily-optimized (but behaving) WordPress site take about 400-800ms, so your usage will 
     probably be closer to 7000 seconds (0.02%) of free compute time.
* *CloudWatch*: Always-free tier provides 10 custom metrics and 10 alarms, with 1M API requests. 
    * We create 2 CloudWatch Alarms and the metrics are provided natively by the Lambda function. 
    * CloudWatch Logs allows ingestion of 5GB per month plus 5GB log storage. While it's highly unlikely that the
    output from this script will ever approach those values, consider setting the retention on the CloudWatch Logs
    log group to something other than unlimited to avoid charges.
* *SNS*: 1 million publishes, 1000 email deliveries, 100 international SMS free.
    * SMS rates (not yet supported) are here: <https://aws.amazon.com/sns/sms-pricing/>
    * If you have an exceptionally noisy month in terms of outages, it's entirely possible that you could exceed the 
    email delivery tier (chargeable at $2/100K emails). Try to fix your websites quickly.
* *IAM*: Free. 
* *CloudFormation*: Free, but if you upload the YAML template through your browser, it will go into a newly created S3 
bucket (versioning disabled, but each template upload is stored as a new object.) 
    * Once you have uploaded the template, consider deleting the `cf-templates-*` bucket to avoid 1-2 cent charges.
* Bandwidth: The Lambda function has to reach out to the Internet to contact the remote servers. You get 1GB/month
free outbound traffic from AWS to the Internet.
    * Assuming those pages are not downloading large amounts of content with a GET request 
    (the check HTTP method defaults to HEAD), you should still be well within the free tier. 
 

## Possible improvements
Feel free to send a pull request for any improvements you might think of, including:
* Multiple checks of remote host in the function before firing an alert
    * Consider firing off to another Lambda or some queuing mechanism so that we don't spend more execution time
    in the same function
* Support for checking multiple websites/URLs with different targets - consider Lambda environment variables or
DynamoDB (free tier should be sufficient)
* If we're going as far as DynamoDB integration, consider tracking history of downtime there too
* Better minification of code in .yaml template, as well as removal of comments in final output file
* SMS support
* Link in email directly to CloudWatch Logs page (eg: 
<https://console.aws.amazon.com/cloudwatch/home?region=us-east-1#logStream:group=/aws/lambda/WebsiteMonitorLambda-WebsiteMonitorLambdaFunction-138TRY2UZTV9>) - 
might need a CloudFormation export to get the Lambda name
* CI deployment mechanism, or at least examples to get this stack deployed/updated over CLI
* Versioning of the code
* Tagging resources with attributes other than the stack tags
* Better timeout value (multiple websites may take over 35 seconds, especially with timeouts); fork/refork functionality
that continues the Lambda if we have a long timeout on one site 
* Class that stores state for single Lambda invocation

## References and resources
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
