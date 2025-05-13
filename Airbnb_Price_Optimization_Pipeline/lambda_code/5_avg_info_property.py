import json
import boto3
import time
from urllib.parse import urlparse

athena = boto3.client('athena')
s3 = boto3.client('s3')

ATHENA_DB = 'data_db'
OUTPUT_BUCKET = 'myresult-sc171'
OUTPUT_LOCATION = f's3://{OUTPUT_BUCKET}/'
TARGET_KEY = 'property_insights.csv'

def lambda_handler(event, context):
    query = """
    SELECT
        property_type,
        COUNT(*) AS number_of_listings,
        AVG(review_scores_accuracy) AS avg_accuracy,
        AVG(review_scores_communication) AS avg_communication,
        AVG(review_scores_location) AS avg_location,
        AVG(review_scores_value) AS avg_value
    FROM processed
    WHERE number_of_reviews > 5
    GROUP BY property_type
    ORDER BY number_of_listings DESC;
    """

 
    response = athena.start_query_execution(
        QueryString=query,
        QueryExecutionContext={'Database': ATHENA_DB},
        ResultConfiguration={'OutputLocation': OUTPUT_LOCATION}
    )

    query_execution_id = response['QueryExecutionId']

    while True:
        result = athena.get_query_execution(QueryExecutionId=query_execution_id)
        state = result['QueryExecution']['Status']['State']
        if state in ['SUCCEEDED', 'FAILED', 'CANCELLED']:
            break
        time.sleep(2)

    if state != 'SUCCEEDED':
        return {
            'statusCode': 500,
            'body': json.dumps({'status': 'failed', 'reason': state})
        }

 
    result_path = result['QueryExecution']['ResultConfiguration']['OutputLocation']
    parsed = urlparse(result_path)
    source_key = parsed.path.lstrip('/')

    try:
        s3.copy_object(
            Bucket=OUTPUT_BUCKET,
            CopySource={'Bucket': OUTPUT_BUCKET, 'Key': source_key},
            Key=TARGET_KEY
        )
    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({'status': 'copy_failed', 'error': str(e)})
        }

    return {
        'statusCode': 200,
        'bucket': OUTPUT_BUCKET,
        'key': TARGET_KEY
    }

