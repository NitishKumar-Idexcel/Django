from django.shortcuts import render
from django.http import JsonResponse, HttpResponse
import boto3
from openpyxl import Workbook
from datetime import datetime, timezone
from .aws_utils import *
from .url_checker import *

def index(request):
    return render(request, 'dashboard/index.html')

# ----------- Utility Functions -----------

def write_excel(headers, data_rows, sheet_name, filename):
    wb = Workbook()
    ws = wb.active
    ws.title = sheet_name
    ws.append(headers)
    for row in data_rows:
        ws.append(row)
    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    wb.save(response)
    return response

# ----------- EC2 Views -----------

def ec2_today_status(request):
    ec2 = boto3.client('ec2')
    instances = ec2.describe_instances()
    today = datetime.now(timezone.utc).date()
    today_instances, other_instances = [], []

    for res in instances['Reservations']:
        for inst in res['Instances']:
            launch_time = inst['LaunchTime'].date()
            info = {
                'id': inst['InstanceId'],
                'state': inst['State']['Name'],
                'launch_time': inst['LaunchTime'],
                'name': next((t['Value'] for t in inst.get('Tags', []) if t['Key'] == 'Name'), 'N/A')
            }
            (today_instances if launch_time == today else other_instances).append(info)

    return render(request, 'dashboard/partials/ec2.html', {'today_instances': today_instances, 'other_instances': other_instances})

def export_ec2_excel(request):
    ec2 = boto3.client('ec2')
    reservations = ec2.describe_instances()['Reservations']
    today = datetime.now(timezone.utc).date()
    data = []

    for res in reservations:
        for inst in res['Instances']:
            data.append([
                inst['InstanceId'],
                next((t['Value'] for t in inst.get('Tags', []) if t['Key'] == 'Name'), ''),
                str(inst['LaunchTime']),
                inst['State']['Name'],
                'Yes' if inst['LaunchTime'].date() == today else 'No'
            ])

    return write_excel(['Instance ID', 'Name', 'Launch Time', 'Status', 'Launched Today'], data, "EC2 Status (Today)", "ec2_instances.xlsx")

# ----------- ASG Views -----------

def get_all_auto_scaling_groups():
    client = boto3.client('autoscaling')
    asgs, token = [], None
    while True:
        response = client.describe_auto_scaling_groups(**({'NextToken': token} if token else {}))
        asgs.extend(response['AutoScalingGroups'])
        token = response.get('NextToken')
        if not token: break
    return asgs

def asg_summary(request):
    asgs = get_all_auto_scaling_groups()
    return render(request, 'dashboard/partials/asg.html', {
        'asg_list': [{'name': a['AutoScalingGroupName'], 'min_size': a['MinSize'], 'max_size': a['MaxSize'], 'desired_capacity': a['DesiredCapacity'], 'instance_count': len(a['Instances'])} for a in asgs],
        'asg_count': len(asgs)
    })

def export_asg_excel(request):
    asgs = get_all_auto_scaling_groups()
    data = [[a['AutoScalingGroupName'], a['MinSize'], a['MaxSize'], a['DesiredCapacity'], len(a['Instances'])] for a in asgs]
    return write_excel(["Name", "Min Size", "Max Size", "Desired Capacity", "Instance Count"], data, "Auto Scaling Groups", "asg_summary.xlsx")

# ----------- AMI & Snapshots Views -----------

def ami_summary(request):
    ec2 = boto3.client('ec2')
    amis = ec2.describe_images(Owners=['self'])['Images']
    return render(request, 'dashboard/partials/ami.html', {
        'ami_list': [{'image_id': a['ImageId'], 'name': a['Name'], 'creation_date': a['CreationDate'], 'state': a['State']} for a in amis],
        'ami_count': len(amis)
    })

def export_ami_excel(request):
    ec2 = boto3.client('ec2')
    amis = ec2.describe_images(Owners=['self'])['Images']
    data = [[a['ImageId'], a['Name'], a['CreationDate'], a['State']] for a in amis]
    return write_excel(["Image ID", "Name", "Creation Date", "State"], data, "AMIs", f"ami_summary_{datetime.now().strftime('%Y%m%d')}.xlsx")

def snapshots_summary(request):
    ec2 = boto3.client('ec2')
    snaps = ec2.describe_snapshots(OwnerIds=['self'])['Snapshots']
    return render(request, 'dashboard/partials/snapshots.html', {
        'snapshot_list': [{'snapshot_id': s['SnapshotId'], 'start_time': str(s['StartTime']), 'volume_size': s['VolumeSize'], 'state': s['State']} for s in snaps],
        'snapshots_count': len(snaps)
    })

def export_snapshot_excel(request):
    ec2 = boto3.client('ec2')
    snaps = ec2.describe_snapshots(OwnerIds=['self'])['Snapshots']
    data = [[s['SnapshotId'], str(s['StartTime']), s['VolumeSize'], s['State']] for s in snaps]
    return write_excel(["Snapshot ID", "Start Time", "Size (GB)", "State"], data, "Snapshots", f"snapshots_summary_{datetime.now().strftime('%Y%m%d')}.xlsx")

# ----------- Load Balancer Views -----------

def lb_summary(request):
    lbs = boto3.client('elbv2').describe_load_balancers()['LoadBalancers']
    return render(request, 'dashboard/partials/load_balancer.html', {
        'lb_list': [{'name': l['LoadBalancerName'], 'type': l['Type'], 'state': l['State']['Code']} for l in lbs]
    })

def export_lb_excel(request):
    lbs = boto3.client('elbv2').describe_load_balancers()['LoadBalancers']
    data = [[l['LoadBalancerName'], l['Type'], l['State']['Code']] for l in lbs]
    return write_excel(["Name", "Type", "State"], data, "Load Balancers", "load_balancers.xlsx")

# ----------- Lambda Views -----------

def get_all_lambda_functions(client):
    functions, marker = [], None
    while True:
        resp = client.list_functions(**({'Marker': marker} if marker else {}))
        functions.extend(resp['Functions'])
        marker = resp.get('NextMarker')
        if not marker: break
    return functions

def lambda_summary(request):
    funcs = get_all_lambda_functions(boto3.client('lambda'))
    return render(request, 'dashboard/partials/lambda.html', {
        'lambda_list': [{'name': f['FunctionName'], 'runtime': f['Runtime'], 'last_modified': f['LastModified'], 'memory_size': f['MemorySize']} for f in funcs]
    })

def export_lambda_excel(request):
    funcs = get_all_lambda_functions(boto3.client('lambda'))
    data = [[f['FunctionName'], f['Runtime'], f['Handler'], f['MemorySize'], f['LastModified']] for f in funcs]
    return write_excel(['Function Name', 'Runtime', 'Handler', 'Memory (MB)', 'Last Modified'], data, "Lambda Functions", "Lambda_Summary.xlsx")

# ----------- URL Health Check -----------

def url_health_check(request):
    return render(request, 'dashboard/partials/url.html', {
        'url_stgsqlup': check_urls_from_file('dashboard/stgsqlupurl.txt'),
        'url_results': check_urls_from_file('dashboard/dev2url.txt')
    })

def export_url_health_excel(request):
    urls = check_urls_from_file('dashboard/stgsqlupurl.txt') + check_urls_from_file('dashboard/dev2url.txt')
    data = [[u['url'], u['status'], u['status_code']] for u in urls]
    filename = f"url_health_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
    return write_excel(["URL", "Status", "Status Code"], data, "URL Health Status", filename)

# ----------- Utilization Views -----------

def utilization_json_view(request, fetch_func):
    data = fetch_func()
    return JsonResponse({'metrics': data, 'instances': data})

def ec2_utilization(request): 
    return utilization_json_view(request, get_ec2_utilization)
def rds_utilization(request): 
    return utilization_json_view(request, get_rds_utilization)
def redis_utilization(request): 
    return JsonResponse({'metrics': get_redis_utilization()})
def ecs_utilization(request): 
    return JsonResponse({'metrics': get_ecs_utilization()})
def asg_utilization(request): 
    return JsonResponse({'metrics': get_asg_utilization()})

def ec2_utilization_ui(request): 
    return render(request, 'dashboard/partials/ec2_util.html')
def rds_utilization_ui(request): 
    return render(request, 'dashboard/partials/rds_redis.html')
def redis_utilization_ui(request): 
    return render(request, 'dashboard/partials/rds_redis.html')
def ecs_utilization_ui(request): 
    return render(request, 'dashboard/partials/ecs.html')
def asg_utilization_ui(request): 
    return render(request, 'dashboard/partials/asg_util.html')

def export_ec2_utilization_excel(request):
    data = get_ec2_utilization()
    rows = [[d['instance_id'], d['name'], d['cpu']] for d in data]
    return write_excel(["Instance ID", "Name", "CPU Utilization (%)"], rows, "EC2 Utilization", "ec2_utilization.xlsx")

def export_rds_utilization_excel(request):
    rds = get_rds_utilization()
    redis = get_redis_utilization()
    rows = [[r['Resources'], r['Name'], r['cpu'], r['memory']] for r in [{'Resources': 'Redis', **d} for d in redis] + [{'Resources': 'RDS', **d} for d in rds]]
    return write_excel(['Resources', 'Name', 'CPU Utilization (%)', 'Memory'], rows, "Rds&Redis Utilization", "Rds&Redis_Utilization.xlsx")

def export_ecs_utilization_excel(request):
    data = get_ecs_utilization()
    rows = [[d['cluster'], d['service'], d['cpu'], d['memory']] for d in data]
    return write_excel(['Cluster', 'Service', 'CPU Utilization (%)', 'Memory Utilization (%)'], rows, "ECS Utilization", "ECS_Utilization.xlsx")

# ----------- Target Group Summary -----------

def list_target_groups_with_health_and_lb():
    elbv2 = boto3.client('elbv2')
    result = []
    for page in elbv2.get_paginator('describe_target_groups').paginate():
        for tg in page['TargetGroups']:
            lb_names = ['Not associated']
            if tg['LoadBalancerArns']:
                lb_info = elbv2.describe_load_balancers(LoadBalancerArns=tg['LoadBalancerArns'])
                lb_names = [lb['LoadBalancerName'] for lb in lb_info['LoadBalancers']]

            try:
                health = elbv2.describe_target_health(TargetGroupArn=tg['TargetGroupArn'])['TargetHealthDescriptions']
                targets = [{'id': th['Target']['Id'], 'port': th['Target']['Port'], 'state': th['TargetHealth']['State'], 'reason': th['TargetHealth'].get('Reason', ''), 'description': th['TargetHealth'].get('Description', '')} for th in health]
            except Exception as e:
                targets = [{'id': 'Error', 'port': '-', 'state': str(e), 'reason': '', 'description': ''}]

            result.append({
                'name': tg['TargetGroupName'],
                'protocol': tg['Protocol'],
                'port': tg['Port'],
                'vpc_id': tg['VpcId'],
                'target_type': tg['TargetType'],
                'load_balancers': lb_names,
                'targets': targets
            })
    return result

def target_group_list(request):
    groups = list_target_groups_with_health_and_lb()
    return render(request, 'dashboard/partials/target_groups.html', {
        'target_groups': groups, 'tg_count': len(groups)
    })
