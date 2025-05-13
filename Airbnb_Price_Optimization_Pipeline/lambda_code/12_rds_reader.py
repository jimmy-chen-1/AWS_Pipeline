import json
import pymysql
import boto3
import csv
from io import StringIO

rds_client = boto3.client('rds')
s3_client = boto3.client('s3')


DEFAULT_BUCKET = 'myresult-sc171'
DEFAULT_KEY = 'property_insights.csv'
DEFAULT_DB_NAME = 'myresult'
DEFAULT_TABLE_NAME = 'property_insights'
DEFAULT_DB_USER = 'admin'
DEFAULT_DB_PASSWORD = 'csj123456'
DEFAULT_RDS_INSTANCE_ID = 'myresult-db'

def lambda_handler(event, context):
    try:
        # ✅ Step 1
        rds_instance_id = event.get('rds_instance_id', DEFAULT_RDS_INSTANCE_ID)
        db_user = event.get('user', DEFAULT_DB_USER)
        db_password = event.get('password', DEFAULT_DB_PASSWORD)
        db_name = event.get('database', DEFAULT_DB_NAME)
        table_name = event.get('table', DEFAULT_TABLE_NAME)
        bucket = event.get('bucket', DEFAULT_BUCKET)
        key = event.get('key', DEFAULT_KEY)

        # ✅ Step 2
        print(f"🔍 Fetching endpoint for RDS instance '{rds_instance_id}'...")
        rds_response = rds_client.describe_db_instances(DBInstanceIdentifier=rds_instance_id)
        db_host = rds_response['DBInstances'][0]['Endpoint']['Address']
        print(f"✅ RDS endpoint: {db_host}")

        # ✅ Step 3
        init_conn = pymysql.connect(
            host=db_host,
            user=db_user,
            password=db_password,
            database='mysql',
            connect_timeout=10
        )
        with init_conn.cursor() as cursor:
            cursor.execute(f"CREATE DATABASE IF NOT EXISTS {db_name};")
        init_conn.close()

        # ✅ Step 4
        conn = pymysql.connect(
            host=db_host,
            user=db_user,
            password=db_password,
            database=db_name,
            connect_timeout=10
        )

        # ✅ Step 5
        response = s3_client.get_object(Bucket=bucket, Key=key)
        content = response['Body'].read().decode('utf-8')
        csv_data = csv.reader(StringIO(content))
        header = next(csv_data)

        with conn.cursor() as cursor:
            create_table_sql = f"""
            CREATE TABLE IF NOT EXISTS {table_name} (
                {', '.join(f'`{col}` VARCHAR(255)' for col in header)}
            );
            """
            cursor.execute(create_table_sql)

            insert_sql = f"""
            INSERT INTO {table_name} ({', '.join(f'`{col}`' for col in header)})
            VALUES ({', '.join(['%s'] * len(header))});
            """
            for row in csv_data:
                cursor.execute(insert_sql, row)

        conn.commit()
        conn.close()

        return {
            'status': 'success',
            'endpoint': db_host,
            'message': f'✅ {table_name} imported from {bucket}/{key} into {db_name} @ {db_host}'
        }

    except Exception as e:
        return {
            'status': 'error',
            'message': str(e)
        }
