AWSTemplateFormatVersion: "2010-09-09"
Description: Deploy the Lambda function and dependent resources to monitor websites.
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
        # We could scope the permissions provided by this managed policy ARN down further, as it permits
        # logs:CreateLogGroup, CreateLogStream and PutLogEvents to all resources. If we instead created
        # a specific CloudWatch Logs log group as part of this template, we could just add permission to
        # PutLogEvents on a specific group or stream.
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

Outputs:
  WebsiteMonitorLambdaIAMRoleOutput:
    Description: ARN of the IAM role used by the website monitoring Lambda function
    Value: !GetAtt WebsiteMonitorLambdaIAMRole.Arn
    Export:
      Name: !Sub "${AWS::StackName}-LambdaIAMRoleARN"
