import boto3

elbv2 = boto3.client('elbv2')
ec2 = boto3.client('ec2')

def lambda_handler(event, context):
    try:

        lb_name = "alm-ml-sc171"
        target_group_name = "ml-tg-sc171"
        sg_name = "ml_sg"

        # ✅ Step 1
        vpcs = ec2.describe_vpcs(Filters=[{"Name": "isDefault", "Values": ["true"]}])
        if not vpcs['Vpcs']:
            return {"status": "error", "message": "❌ No default VPC found."}
        vpc_id = vpcs['Vpcs'][0]['VpcId']

        # ✅ Step 2
        subnets_response = ec2.describe_subnets(Filters=[
            {"Name": "vpc-id", "Values": [vpc_id]}
        ])
        subnet_ids = [s['SubnetId'] for s in subnets_response['Subnets'][:2]]
        if len(subnet_ids) < 2:
            return {"status": "error", "message": "❌ Not enough subnets found in default VPC."}
        print(f"✅ Using subnets: {subnet_ids}")

        # ✅ Step 3
        sg_response = ec2.describe_security_groups(
            Filters=[
                {"Name": "group-name", "Values": [sg_name]},
                {"Name": "vpc-id", "Values": [vpc_id]}
            ]
        )
        if not sg_response['SecurityGroups']:
            return {"status": "error", "message": f"❌ Security group '{sg_name}' not found."}
        sg_id = sg_response['SecurityGroups'][0]['GroupId']
        print(f"✅ Security group ID: {sg_id}")

        # ✅ Step 4
        tg_response = elbv2.describe_target_groups(Names=[target_group_name])
        target_group_arn = tg_response['TargetGroups'][0]['TargetGroupArn']
        print(f"✅ Target group ARN: {target_group_arn}")

        # ✅ Step 5
        lb_response = elbv2.create_load_balancer(
            Name=lb_name,
            Subnets=subnet_ids,
            SecurityGroups=[sg_id],
            Scheme='internet-facing',
            Type='application',
            IpAddressType='ipv4',
            Tags=[{'Key': 'Name', 'Value': lb_name}]
        )
        lb_arn = lb_response['LoadBalancers'][0]['LoadBalancerArn']
        dns_name = lb_response['LoadBalancers'][0]['DNSName']
        print(f"✅ Load balancer created: {lb_arn}")

        # ✅ Step 6
        listener_response = elbv2.create_listener(
            LoadBalancerArn=lb_arn,
            Protocol='HTTP',
            Port=80,
            DefaultActions=[
                {
                    'Type': 'forward',
                    'TargetGroupArn': target_group_arn
                }
            ]
        )
        listener_arn = listener_response['Listeners'][0]['ListenerArn']
        print(f"✅ Listener created: {listener_arn}")

        return {
            "status": "success",
            "message": f"✅ ALB {lb_name} created and forwarding to {target_group_name}",
            "dns_name": dns_name,
            "load_balancer_arn": lb_arn,
            "listener_arn": listener_arn
        }

    except Exception as e:
        return {
            "status": "error",
            "message": str(e)
        }
