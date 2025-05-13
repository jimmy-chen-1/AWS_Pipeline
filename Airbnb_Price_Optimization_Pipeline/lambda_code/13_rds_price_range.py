import boto3
import pymysql
import time
import csv
from io import StringIO

rds = boto3.client('rds')
s3 = boto3.client('s3')

def lambda_handler(event, context):

    instance_id = event.get('rds_instance_id', 'myresult-db')
    db_name = event.get('db_name', 'myresult')
    table_name = event.get('table', 'price_range')
    bucket = event.get('bucket', 'myresult-sc171')
    key = event.get('key', 'price_range.csv')
    db_user = event.get('user', 'admin')
    db_password = event.get('password', 'csj123456')
    sg_id = event.get('security_group_id', 'sg-0bab06c5cac52adfc')  # ← ✅
    subnet_group = event.get('subnet_group', 'public-db-subnet-group')
    db_engine = event.get('engine', 'mysql')
    db_class = event.get('instance_class', 'db.t3.micro')


    if not bucket or not key or not sg_id:
        return {
            "status": "error",
            "message": "Missing required parameters: bucket, key, security_group_id"
        }

    try:

        try:
            rds.describe_db_instances(DBInstanceIdentifier=instance_id)
            print(f"✅ RDS instance '{instance_id}' already exists")
        except rds.exceptions.DBInstanceNotFoundFault:
            print(f"🚀 Creating RDS instance '{instance_id}'...")
            rds.create_db_instance(
                DBInstanceIdentifier=instance_id,
                DBName=db_name,
                AllocatedStorage=20,
                DBInstanceClass=db_class,
                Engine=db_engine,
                MasterUsername=db_user,
                MasterUserPassword=db_password,
                VpcSecurityGroupIds=[sg_id],
                DBSubnetGroupName=subnet_group,
                PubliclyAccessible=True,
                BackupRetentionPeriod=1,
                MultiAZ=False
            )




        endpoint = rds.describe_db_instances(DBInstanceIdentifier=instance_id)['DBInstances'][0]['Endpoint']['Address']
        print(f"✅ RDS endpoint: {endpoint}")


        conn_init = pymysql.connect(
            host=endpoint,
            user=db_user,
            password=db_password,
            database='mysql',
            connect_timeout=10
        )
        with conn_init.cursor() as cursor:
            cursor.execute(f"CREATE DATABASE IF NOT EXISTS {db_name};")
        conn_init.close()


        conn = pymysql.connect(
            host=endpoint,
            user=db_user,
            password=db_password,
            database=db_name,
            connect_timeout=10
        )


        response = s3.get_object(Bucket=bucket, Key=key)
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
            "status": "success",
            "message": f"✅ RDS {db_name}.{table_name} loaded from s3://{bucket}/{key}",
            "endpoint": endpoint
        }

    except Exception as e:
        return {
            "status": "error",
            "message": str(e)
        }
