import boto3

elbv2 = boto3.client('elbv2')
ec2 = boto3.client('ec2')

def lambda_handler(event, context):
    try:
        
        target_group_name = "ml-tg-sc171"
        vpc_id = None

        # ✅ Step 1:VPC
        vpcs = ec2.describe_vpcs(Filters=[{"Name": "isDefault", "Values": ["true"]}])
        if not vpcs['Vpcs']:
            return {"status": "error", "message": "❌ No default VPC found."}
        vpc_id = vpcs['Vpcs'][0]['VpcId']
        print(f"✅ Default VPC: {vpc_id}")

        # ✅ Step 2: Target Group
        response = elbv2.create_target_group(
            Name=target_group_name,
            Protocol='HTTP',
            Port=8000,
            VpcId=vpc_id,
            TargetType='instance',
            ProtocolVersion='HTTP1',
            HealthCheckEnabled=True,
            HealthCheckProtocol='HTTP',
            HealthCheckPort='traffic-port',
            HealthCheckPath='/',
            HealthCheckIntervalSeconds=300,
            HealthCheckTimeoutSeconds=10,
            HealthyThresholdCount=5,
            UnhealthyThresholdCount=10,
            Matcher={
                'HttpCode': '200-400'
            },
            Tags=[
                {'Key': 'Name', 'Value': target_group_name}
            ]
        )

        tg_arn = response['TargetGroups'][0]['TargetGroupArn']
        print(f"✅ Target Group created: {tg_arn}")

        return {
            "status": "success",
            "target_group_arn": tg_arn,
            "message": f"✅ Target group '{target_group_name}' created successfully."
        }

    except Exception as e:
        return {
            "status": "error",
            "message": str(e)
        }
