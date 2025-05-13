import boto3

def lambda_handler(event, context):
    rds = boto3.client('rds')
    
    try:
        response = rds.create_db_instance(
            DBInstanceIdentifier='myresult-db',
            DBName='myresult',
            AllocatedStorage=20,
            DBInstanceClass='db.t3.micro',
            Engine='mysql',
            MasterUsername='admin',
            MasterUserPassword='csj123456',
            PubliclyAccessible=True,
            VpcSecurityGroupIds=['sg-0bab06c5cac52adfc'],  # ← ✅
            DBSubnetGroupName='public-db-subnet-group',  # ← ✅
            BackupRetentionPeriod=1,
            StorageType='gp2',
            MultiAZ=False,
            EngineVersion='8.0.35',
            AutoMinorVersionUpgrade=True,
            Tags=[
                {'Key': 'Name', 'Value': 'myresult-rds'}
            ]
        )

        return {
            "status": "success",
            "message": "✅ RDS instance creation initiated.",
            "db_instance_identifier": response['DBInstance']['DBInstanceIdentifier']
        }

    except rds.exceptions.DBInstanceAlreadyExistsFault:
        return {
            "status": "exists",
            "message": "⚠️ RDS instance already exists."
        }

    except Exception as e:
        return {
            "status": "error",
            "message": str(e)
        }
