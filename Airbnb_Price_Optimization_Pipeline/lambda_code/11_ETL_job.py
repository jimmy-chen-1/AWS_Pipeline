import json
import boto3
import os


glue = boto3.client('glue')


GLUE_JOB_NAME = os.environ.get('GLUE_JOB_NAME', 'etl_job')


INPUT_PATH = 's3://raw-data-sc171/airbnb_ratings_new.csv'
OUTPUT_PATH = 's3://raw-data-sc171/airbnb_ratings_new.csv'

def lambda_handler(event, context):
    try:
        response = glue.start_job_run(
            JobName=GLUE_JOB_NAME,
            Arguments={
                '--input_path': INPUT_PATH,
                '--output_path': OUTPUT_PATH
            }
        )

        return {
            'statusCode': 200,
            'body': json.dumps({
                'message': 'Glue ETL job started successfully.',
                'jobName': GLUE_JOB_NAME,
                'jobRunId': response['JobRunId']
            })
        }

    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({
                'message': 'Failed to start Glue job.',
                'error': str(e)
            })
        }
