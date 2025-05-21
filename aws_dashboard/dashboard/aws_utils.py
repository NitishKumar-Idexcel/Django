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
    start = now - timedelta(minutes=5)

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

def get_redis_utilization():
    client = boto3.client('elasticache')
    cw = boto3.client('cloudwatch')
    now = datetime.now(timezone.utc)
    start = now - timedelta(minutes=5)

    metrics = []

    # List all Redis (ElastiCache) clusters
    clusters = client.describe_cache_clusters(ShowCacheNodeInfo=True)['CacheClusters']
    for cluster in clusters:
        if cluster['Engine'] != 'redis':
            continue

        cluster_id = cluster['CacheClusterId']
        node_ids = [node['CacheNodeId'] for node in cluster['CacheNodes']]

        for node_id in node_ids:
            # CPU Utilization
            cpu_data = cw.get_metric_statistics(
                Namespace='AWS/ElastiCache',
                MetricName='CPUUtilization',
                Dimensions=[
                    {'Name': 'CacheClusterId', 'Value': cluster_id},
                    {'Name': 'CacheNodeId', 'Value': node_id}
                ],
                StartTime=start,
                EndTime=now,
                Period=300,
                Statistics=['Average']
            )

            # FreeableMemory (proxy for memory usage)
            mem_data = cw.get_metric_statistics(
                Namespace='AWS/ElastiCache',
                MetricName='FreeableMemory',
                Dimensions=[
                    {'Name': 'CacheClusterId', 'Value': cluster_id},
                    {'Name': 'CacheNodeId', 'Value': node_id}
                ],
                StartTime=start,
                EndTime=now,
                Period=300,
                Statistics=['Average']
            )

            cpu = round(cpu_data['Datapoints'][0]['Average'], 2) if cpu_data['Datapoints'] else 0.0
            mem = round(mem_data['Datapoints'][0]['Average'] / (1024 ** 2), 2) if mem_data['Datapoints'] else 0.0

            metrics.append({
                'cluster': cluster_id,
                'node': node_id,
                'cpu': cpu,
                'memory': f"{mem} MB" 
            })

    return metrics


def get_ecs_utilization():
    ecs = boto3.client('ecs')
    cw = boto3.client('cloudwatch')
    now = datetime.now(timezone.utc)
    start = now - timedelta(minutes=5)

    metrics = []

    # Use paginator to get all cluster ARNs
    paginator = ecs.get_paginator('list_clusters')
    cluster_arns = []
    for page in paginator.paginate():
        cluster_arns.extend(page['clusterArns'])

    for cluster_arn in cluster_arns:
        cluster_name = cluster_arn.split('/')[-1]

        # Use paginator to get all service ARNs in each cluster
        service_arns = []
        service_paginator = ecs.get_paginator('list_services')
        for page in service_paginator.paginate(cluster=cluster_arn):
            service_arns.extend(page['serviceArns'])

        if not service_arns:
            continue

        # Batch describe services (max 10 at a time)
        for i in range(0, len(service_arns), 10):
            batch = service_arns[i:i + 10]
            services = ecs.describe_services(cluster=cluster_arn, services=batch)['services']

            for service in services:
                service_name = service['serviceName']

                # CloudWatch metric queries
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

def get_asg_utilization():
    cw = boto3.client('cloudwatch')
    autoscaling = boto3.client('autoscaling')
    now = datetime.now(timezone.utc)
    start = now - timedelta(minutes=5)

    metrics = []

    paginator = autoscaling.get_paginator('describe_auto_scaling_groups')
    for page in paginator.paginate():
        for asg in page['AutoScalingGroups']:
            asg_name = asg['AutoScalingGroupName']

            # CPU
            cpu = cw.get_metric_statistics(
                Namespace='AWS/EC2',
                MetricName='CPUUtilization',
                Dimensions=[{'Name': 'AutoScalingGroupName', 'Value': asg_name}],
                StartTime=start,
                EndTime=now,
                Period=300,
                Statistics=['Average']
            )

            # Memory
            mem = cw.get_metric_statistics(
                Namespace='CWAgent',
                MetricName='mem_used_percent',
                Dimensions=[{'Name': 'AutoScalingGroupName', 'Value': asg_name}],
                StartTime=start,
                EndTime=now,
                Period=300,
                Statistics=['Average']
            )

            # Disk
            disk = cw.get_metric_statistics(
                Namespace='CWAgent',
                MetricName='disk_used_percent',
                Dimensions=[
                    {'Name': 'path', 'Value': '/'},
                    {'Name': 'AutoScalingGroupName', 'Value': asg_name},
                    {'Name': 'device', 'Value': 'nvme0n1p1'},
                    {'Name': 'fstype', 'Value': 'ext4'}
                ],
                StartTime=start,
                EndTime=now,
                Period=300,
                Statistics=['Average']
            )

            metrics.append({
                'asg_name': asg_name,
                'cpu': round(cpu['Datapoints'][0]['Average'], 2) if cpu['Datapoints'] else 0.0,
                'memory': round(mem['Datapoints'][0]['Average'], 2) if mem['Datapoints'] else 0.0,
                'disk': round(disk['Datapoints'][0]['Average'], 2) if disk['Datapoints'] else 0.0
            })

    return metrics
