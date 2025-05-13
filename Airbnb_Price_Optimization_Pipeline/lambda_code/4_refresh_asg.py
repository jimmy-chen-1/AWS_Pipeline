import boto3

autoscaling = boto3.client('autoscaling')
ec2 = boto3.client('ec2')

def lambda_handler(event, context):
    try:
        asg_name = 'asg_ml'
        launch_template_name = 'ml_web'
        desired_capacity = 1
        min_size = 1
        max_size = 2

        # ✅ Step 1: fallback
        subnet_ids = event.get('subnet_ids')
        
        if not subnet_ids:
            print("🔍 No subnet_ids passed. Fetching default subnets...")
            response = ec2.describe_subnets(
                Filters=[{'Name': 'default-for-az', 'Values': ['true']}]
            )
            subnets = [s['SubnetId'] for s in response['Subnets']]
            if not subnets:
                return {
                    'status': 'error',
                    'message': '❌ No default subnets found and no subnet_ids provided.'
                }
            subnet_ids = ",".join(subnets)
            print(f"✅ Default subnet_ids: {subnet_ids}")
        else:
            print(f"✅ Using provided subnet_ids: {subnet_ids}")

        # ✅ Step 2: create Auto Scaling Group
        autoscaling.create_auto_scaling_group(
            AutoScalingGroupName=asg_name,
            LaunchTemplate={
                'LaunchTemplateName': launch_template_name,
                'Version': '$Default'
            },
            MinSize=min_size,
            MaxSize=max_size,
            DesiredCapacity=desired_capacity,
            VPCZoneIdentifier=subnet_ids,
            Tags=[
                {
                    'Key': 'Name',
                    'Value': 'ml-instance',
                    'PropagateAtLaunch': True
                }
            ]
        )

        return {
            'status': 'success',
            'message': f"✅ Auto Scaling Group '{asg_name}' created successfully."
        }

    except Exception as e:
        return {
            'status': 'error',
            'message': str(e)
        }
