import boto3
import json

s3 = boto3.client('s3')
glue = boto3.client('glue')

def lambda_handler(event, context):
    data_crawler = "data_crawler"

    
    if isinstance(event, list):
        event = {k: v for d in event for k, v in d.items()}

   
    bucket = event.get("bucket", "raw-data-sc171")
    prefix = event.get("prefix", "airbnb_ratings_new.csv")
    key = f"processed/{prefix}"
    s3_path = f"s3://{bucket}/{key}"
    processed_prefix = "processed/"

    print(f"🔍 check S3 has 'processed/' file...")

 
    try:
        response = s3.list_objects_v2(Bucket=bucket, Prefix=processed_prefix)
        contents = response.get("Contents", [])

        if not contents:
            print(f"❌ 'processed/' don't exist")
            return {
                "statusCode": 404,
                "message": f"❌ S3 '{processed_prefix}' no file"
            }
        else:
            print(f"✅ S3 '{processed_prefix}' find {len(contents)} numbers of document")

    except Exception as e:
        print(f"❌ fail to check file exist: {str(e)}")
        return {
            "statusCode": 500,
            "error": str(e)
        }

 
    print(f"🔍 check if file exist: {s3_path}")
    try:
        s3.head_object(Bucket=bucket, Key=key)
        print("✅ file exist, launch Glue Crawler")

        try:
            glue.start_crawler(Name=data_crawler)
            print(f"🚀 launch Glue Crawler: {data_crawler}")
            return {
                "statusCode": 200,
                "message": f"✅ success launch Crawler '{data_crawler}'",
                "s3_path": s3_path
            }

        except glue.exceptions.CrawlerRunningException:
            print(f"⚠️ Crawler '{data_crawler}' running")
            return {
                "statusCode": 202,
                "message": f"⚠️ Crawler '{data_crawler}' running",
                "s3_path": s3_path
            }

    except s3.exceptions.ClientError as e:
        print(f"❌ file not exist: {s3_path} -> {str(e)}")
        return {
            "statusCode": 404,
            "message": f"❌ S3 file not exist: {s3_path}"
        }

