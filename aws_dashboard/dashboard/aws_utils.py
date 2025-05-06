import boto3
from datetime import datetime, timedelta, timezone

def get_ec2_utilization():
    ec2 = boto3.client('ec2')
    cw = boto3.client('cloudwatch')

    instances = ec2.describe_instances(Filters=[{
        'Name': 'instance-state-name',
        'Values': ['running']
    }])

    metrics = []
    now = datetime.now(timezone.utc)
    start = now - timedelta(minutes=10)

    for reservation in instances['Reservations']:
        for inst in reservation['Instances']:
            instance_id = inst['InstanceId']
            name = next((tag['Value'] for tag in inst.get('Tags', []) if tag['Key'] == 'Name'), instance_id)

            # CPU utilization (average over last 5 minutes)
            cpu = cw.get_metric_statistics(
                Namespace='AWS/EC2',
                MetricName='CPUUtilization',
                Dimensions=[{'Name': 'InstanceId', 'Value': instance_id}],
                StartTime=start,
                EndTime=now,
                Period=300,
                Statistics=['Average']
            )

            cpu_avg = round(cpu['Datapoints'][0]['Average'], 2) if cpu['Datapoints'] else 0.0

            
            metrics.append({
                'instance_id': instance_id,
                'name': name,
                'cpu': cpu_avg
            })

    return metrics

def get_rds_utilization():
    rds = boto3.client('rds')
    cw = boto3.client('cloudwatch')
    now = datetime.now(timezone.utc)
    start = now - timedelta(minutes=10)

    instances = rds.describe_db_instances()['DBInstances']
    metrics = []

    for inst in instances:
        db_id = inst['DBInstanceIdentifier']

        # CPU Utilization
        cpu = cw.get_metric_statistics(
            Namespace='AWS/RDS',
            MetricName='CPUUtilization',
            Dimensions=[{'Name': 'DBInstanceIdentifier', 'Value': db_id}],
            StartTime=start,
            EndTime=now,
            Period=300,
            Statistics=['Average']
        )

        # FreeableMemory (used as a proxy for memory usage)
        memory = cw.get_metric_statistics(
            Namespace='AWS/RDS',
            MetricName='FreeableMemory',
            Dimensions=[{'Name': 'DBInstanceIdentifier', 'Value': db_id}],
            StartTime=start,
            EndTime=now,
            Period=300,
            Statistics=['Average']
        )

        cpu_val = round(cpu['Datapoints'][0]['Average'], 2) if cpu['Datapoints'] else 0.0
        mem_val = round(memory['Datapoints'][0]['Average'] / (1024 ** 2), 2) if memory['Datapoints'] else 0.0

        metrics.append({
            'db_id': db_id,
            'cpu': cpu_val,
            'memory': f"{mem_val} MB"
        })

    return metrics

def get_ecs_utilization():
    ecs = boto3.client('ecs')
    cw = boto3.client('cloudwatch')
    now = datetime.now(timezone.utc)
    start = now - timedelta(minutes=10)

    metrics = []

    # List all clusters
    clusters = ecs.list_clusters()['clusterArns']
    for cluster_arn in clusters:
        # List running services in the cluster
        services = ecs.list_services(cluster=cluster_arn, launchType='EC2')['serviceArns']
        if not services:
            continue

        service_details = ecs.describe_services(cluster=cluster_arn, services=services)['services']

        for service in service_details:
            service_name = service['serviceName']
            cluster_name = cluster_arn.split('/')[-1]

            # CPU Utilization
            cpu = cw.get_metric_statistics(
                Namespace='AWS/ECS',
                MetricName='CPUUtilization',
                Dimensions=[
                    {'Name': 'ClusterName', 'Value': cluster_name},
                    {'Name': 'ServiceName', 'Value': service_name}
                ],
                StartTime=start,
                EndTime=now,
                Period=300,
                Statistics=['Average']
            )

            # Memory Utilization
            memory = cw.get_metric_statistics(
                Namespace='AWS/ECS',
                MetricName='MemoryUtilization',
                Dimensions=[
                    {'Name': 'ClusterName', 'Value': cluster_name},
                    {'Name': 'ServiceName', 'Value': service_name}
                ],
                StartTime=start,
                EndTime=now,
                Period=300,
                Statistics=['Average']
            )

            cpu_val = round(cpu['Datapoints'][0]['Average'], 2) if cpu['Datapoints'] else 0.0
            mem_val = round(memory['Datapoints'][0]['Average'], 2) if memory['Datapoints'] else 0.0

            metrics.append({
                'cluster': cluster_name,
                'service': service_name,
                'cpu': cpu_val,
                'memory': mem_val
            })

    return metrics