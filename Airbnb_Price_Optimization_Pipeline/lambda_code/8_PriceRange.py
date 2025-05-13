import json
import boto3
import time
from urllib.parse import urlparse

athena = boto3.client('athena')
s3 = boto3.client('s3')

ATHENA_DB = 'data_db'
OUTPUT_BUCKET = 'myresult-sc171'
OUTPUT_LOCATION = f's3://{OUTPUT_BUCKET}/'
TARGET_KEY = 'price_range.csv'

def lambda_handler(event, context):
    query = """
    SELECT
    CASE
        WHEN price < 50 THEN 'Budget (Under $50)'
        WHEN price >= 50 AND price < 150 THEN 'Mid-range ($50-$149)'
        WHEN price >= 150 AND price < 300 THEN 'Upper Mid-range ($150-$299)'
        ELSE 'Luxury ($300+)'
        END AS price_tier,
        COUNT(*) AS number_of_listings,
        AVG(review_scores_accuracy) AS avg_accuracy,
        AVG(review_scores_value) AS avg_value
    FROM
        processed
    WHERE
        number_of_reviews > 5 AND price IS NOT NULL
    GROUP BY
        CASE
            WHEN price < 50 THEN 'Budget (Under $50)'
            WHEN price >= 50 AND price < 150 THEN 'Mid-range ($50-$149)'
            WHEN price >= 150 AND price < 300 THEN 'Upper Mid-range ($150-$299)'
            ELSE 'Luxury ($300+)'
        END
    ORDER BY
        MIN(price);
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
