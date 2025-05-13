import json
import boto3

sns = boto3.client('sns')

FIXED_OUTPUT_BUCKET = 'myresult-sc171'
FIXED_TARGET_KEY = 'price_range.csv'
SNS_TOPIC_ARN = 'arn:aws:sns:us-east-1:514475511198:query_result'

def lambda_handler(event, context):
    subject = "CSV File Processed Successfully"
    message = f"The CSV file s3://{FIXED_OUTPUT_BUCKET}/{FIXED_TARGET_KEY} has been generated and contains content. Setup is complete."

    try:
        print(f"Publishing SNS to: {SNS_TOPIC_ARN}")
        print(f"Message: {message}")

        response = sns.publish(
            TopicArn=SNS_TOPIC_ARN,
            Message=message,
            Subject=subject
        )

        print("SNS Publish Response:", response)

        return {
            'status': 'Success notification sent',
            'message': message
        }

    except Exception as e:
        print(f"Error sending SNS notification: {str(e)}")
        raise e