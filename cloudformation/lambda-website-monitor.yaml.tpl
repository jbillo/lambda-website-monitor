AWSTemplateFormatVersion: "2010-09-09"
Description: Deploy the Lambda function and dependent resources to monitor websites.
Parameters:
  AlertEmail:
    Type: String
    Description: Email address that should be subscribed to the SNS topic for alerts.
  MonitorURL:
    Type: String
    Description: URL to monitor
Resources:
  WebsiteMonitorLambdaIAMRole:
    # https://docs.aws.amazon.com/lambda/latest/dg/lambda-intro-execution-role.html
    Type: AWS::IAM::Role
    Properties:
      AssumeRolePolicyDocument:
        Version: "2012-10-17"
        Statement:
          -
            Effect: "Allow"
            Principal:
              Service:
                - "lambda.amazonaws.com"
            Action:
              - "sts:AssumeRole"
      ManagedPolicyArns:
        # The managed policy here permits logs:CreateLogGroup, CreateLogStream and PutLogEvents to all resources.
        # This doesn't seem ideal from a security standpoint but there doesn't appear to be a way to direct
        # logged events from a Lambda to a specific CloudWatch Logs log group/stream.
        # See: https://docs.aws.amazon.com/IAM/latest/UserGuide/list_amazoncloudwatchlogs.html
        - "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
  WebsiteMonitorLambdaFunction:
    Type: AWS::Lambda::Function
    Properties:
      Handler: index.handler
      Role: !GetAtt WebsiteMonitorLambdaIAMRole.Arn
      Runtime: python3.7
      Description: Lambda function that checks HTTP status on a given URL
      MemorySize: 128
      Timeout: 35  # 30 second timeout, plus 5 for Lambda initialization, etc.
      Code:
        ZipFile: |
          raise Exception("Run build_template.py first to load code into CloudFormation template")
  WebsiteMonitorSNSTopic:
    Type: AWS::SNS::Topic
    Properties:
      Subscription:
        -
          Protocol: email
          Endpoint: !Sub "${AlertEmail}"

  WebsiteMonitorTriggerRule:
    Type: AWS::Events::Rule
    Properties:
      Description: Check the designated URL using the Lambda function on a schedule.
      ScheduleExpression: "rate(5 minutes)"
      Targets:
        -
          Arn: !GetAtt WebsiteMonitorLambdaFunction.Arn
          Id: WebsiteMonitorLambdaTarget
          Input: !Sub "{\"url\": \"${MonitorURL}\"}"

  # Applied on the Lambda function. Allow the CloudWatch Rule to invoke the function.
  # Note: The API calls for write are AddPermission/RemovePermission, but the read/retrieval equivalent is GetPolicy.
  WebsiteMonitorLambdaRulePermission:
    Type: AWS::Lambda::Permission
    Properties:
      Action: "lambda:InvokeFunction"
      FunctionName: !GetAtt WebsiteMonitorLambdaFunction.Arn
      Principal: "events.amazonaws.com"
      SourceArn: !GetAtt WebsiteMonitorTriggerRule.Arn

  WebsiteMonitorFailedCheckAlarm:
    Type: AWS::CloudWatch::Alarm
    Properties:
      AlarmActions:
        - !Ref WebsiteMonitorSNSTopic
      AlarmDescription: Alert when the website monitor Lambda function detects the remote site is down
      ComparisonOperator: GreaterThanThreshold
      Dimensions:
        -
          Name: FunctionName
          Value: !Ref WebsiteMonitorLambdaFunction
      EvaluationPeriods: 1
      MetricName: Errors
      Namespace: AWS/Lambda
      Period: 300
      Statistic: Sum
      Threshold: 0.0

  WebsiteMonitorFailedInvocationAlarm:
    # We indicate failure when there are no invocations within 10 minutes.
    Type: AWS::CloudWatch::Alarm
    Properties:
      AlarmActions:
        - !Ref WebsiteMonitorSNSTopic
      AlarmDescription: Alert when the website monitor Lambda function has not been invoked regularly
      ComparisonOperator: LessThanThreshold
      Dimensions:
        -
          Name: FunctionName
          Value: !Ref WebsiteMonitorLambdaFunction
      EvaluationPeriods: 1
      MetricName: Invocations
      Namespace: AWS/Lambda
      Period: 600
      Statistic: Sum
      Threshold: 1.0

Outputs:
  WebsiteMonitorLambdaIAMRoleOutput:
    Description: ARN of the IAM role used by the website monitoring Lambda function
    Value: !GetAtt WebsiteMonitorLambdaIAMRole.Arn
    Export:
      Name: !Sub "${AWS::StackName}-LambdaIAMRoleARN"
