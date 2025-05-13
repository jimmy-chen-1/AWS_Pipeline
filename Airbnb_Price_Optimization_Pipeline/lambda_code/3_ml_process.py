import boto3
import time

def lambda_handler(event, context):
    timestamp = time.strftime("%Y-%m-%d-%H-%M-%S")
    job_name = f"ml-process-job-{timestamp}"

    sagemaker = boto3.client("sagemaker")

    response = sagemaker.create_processing_job(
        ProcessingJobName=job_name,
        RoleArn="arn:aws:iam::514475511198:role/LabRole",  
        AppSpecification={
            "ImageUri": "683313688378.dkr.ecr.us-east-1.amazonaws.com/sagemaker-scikit-learn:1.2-1",
            "ContainerEntrypoint": ["python3", "/opt/ml/processing/input/code/ml_code.py"] 
        },
        ProcessingResources={
            "ClusterConfig": {
                "InstanceCount": 1,
                "InstanceType": "ml.m5.large",
                "VolumeSizeInGB": 20
            }
        },
        ProcessingInputs=[
            {
                "InputName": "code",
                "S3Input": {
                    "S3Uri": "s3://my-code-sc171/ml_code.py",  
                    "LocalPath": "/opt/ml/processing/input/code/", 
                    "S3DataType": "S3Prefix",
                    "S3InputMode": "File"
                }
            },
            {
                "InputName": "input-data",
                "S3Input": {
                    "S3Uri": "s3://myresult-sc171/ml_data.csv",    
                    "LocalPath": "/opt/ml/processing/input/", 
                    "S3DataType": "S3Prefix",
                    "S3InputMode": "File"
                }
            }
        ],
        ProcessingOutputConfig={
            "Outputs": [
                {
                    "OutputName": "model-output",
                    "S3Output": {
                        "S3Uri": "s3://ml-model-sc171/",              
                        "LocalPath": "/opt/ml/processing/output/",     
                        "S3UploadMode": "EndOfJob"
                    }
                }
            ]
        }
    )

    return {
        "statusCode": 200,
        "body": f"SageMaker Processing Job started: {job_name}"
    }
