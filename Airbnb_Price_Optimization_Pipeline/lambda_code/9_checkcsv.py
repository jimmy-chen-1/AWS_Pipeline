import json
import boto3
import pandas as pd
import io

s3 = boto3.client('s3')

FIXED_OUTPUT_BUCKET = 'myresult-sc171'
FIXED_TARGET_KEY = 'price_range.csv'

def lambda_handler(event, context):
    is_empty_flag = True

    try:
        response = s3.get_object(Bucket=FIXED_OUTPUT_BUCKET, Key=FIXED_TARGET_KEY)
        content = response['Body'].read()
        df = pd.read_csv(io.BytesIO(content))

        if not df.empty and df.shape[0] > 1:
            is_empty_flag = False

    except s3.exceptions.NoSuchKey:
        print(f"File not found: s3://{FIXED_OUTPUT_BUCKET}/{FIXED_TARGET_KEY}")
    except Exception as e:
        print(f"Error processing file: {str(e)}")

    result = {
        "csvIsEmpty": is_empty_flag,
        "bucket": FIXED_OUTPUT_BUCKET,
        "key": FIXED_TARGET_KEY
    }

    print("Lambda output:", json.dumps(result)) 

    return result
