import json
import boto3
import time
from urllib.parse import urlparse

athena = boto3.client('athena')
s3 = boto3.client('s3')

def lambda_handler(event, context):
    query = """
        SELECT 
            city,
            accommodates,
            room_type,
            bathrooms,
            bedrooms,
            CASE WHEN host_is_superhost = true THEN 1 ELSE 0 END AS is_superhost,
            CASE WHEN amenities LIKE '%Wireless%' THEN 1 ELSE 0 END AS has_wifi,
            CASE WHEN amenities LIKE '%Air Conditioning%' THEN 1 ELSE 0 END AS has_ac,
            CASE WHEN amenities LIKE '%Kitchen%' THEN 1 ELSE 0 END AS has_kitchen,
            CASE WHEN amenities LIKE '%Heating%' THEN 1 ELSE 0 END AS has_heating,
            CASE WHEN amenities LIKE '%Washer%' THEN 1 ELSE 0 END AS has_washer,
            CASE WHEN amenities LIKE '%Dryer%' THEN 1 ELSE 0 END AS has_dryer,
            CASE WHEN amenities LIKE '%TV%' THEN 1 ELSE 0 END AS has_tv,
            CASE WHEN amenities LIKE '%Shampoo%' THEN 1 ELSE 0 END AS has_shampoo,
            CASE WHEN amenities LIKE '%Essentials%' THEN 1 ELSE 0 END AS has_essentials,
            CASE WHEN amenities LIKE '%Hair Dryer%' THEN 1 ELSE 0 END AS has_hair_dryer,
            CASE WHEN amenities LIKE '%Elevator%' THEN 1 ELSE 0 END AS has_elevator,
            CASE WHEN amenities LIKE '%Gym%' THEN 1 ELSE 0 END AS has_gym,
            price
            FROM processed
            WHERE price > 15 AND price IS NOT NULL;
    """

    output_location = 's3://myresult-sc171/'

    # Start Athena query
    response = athena.start_query_execution(
        QueryString=query,
        QueryExecutionContext={'Database': 'data_db'},
        ResultConfiguration={'OutputLocation': output_location}
    )

    query_execution_id = response['QueryExecutionId']

    # Wait for query to complete
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

    # Get result path and parse it
    result_path = result['QueryExecution']['ResultConfiguration']['OutputLocation']
    parsed = urlparse(result_path)
    bucket_name = parsed.netloc
    source_key = parsed.path.lstrip('/')
    target_key = 'ml_data.csv'

    # Copy to fixed file name
    try:
        s3.copy_object(
            Bucket=bucket_name,
            CopySource={'Bucket': bucket_name, 'Key': source_key},
            Key=target_key
        )
        print(f"Copied {source_key} to {target_key}")
    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({'status': 'failed to copy', 'error': str(e)})
        }

    return {
        'statusCode': 200,
        'body': json.dumps({
            'status': 'success',
            'result_location': f's3://{bucket_name}/{target_key}'
        })
    }

