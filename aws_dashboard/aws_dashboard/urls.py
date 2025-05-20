"""
URL configuration for aws_dashboard project.

The `urlpatterns` list routes URLs to  For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from dashboard.views import *

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', index, name='dashboard'),
    path('ec2/', ec2_today_status, name='ec2'),
    path('asg-summary/', asg_summary, name='asg_summary'),
    path('url-health/', url_health_check, name='url_health'),
    path('ec2-utilization/', ec2_utilization, name='ec2_utilization'),
    path('rds-utilization/', rds_utilization, name='rds_utilization'),
    path('redis-utilization/', redis_utilization, name='redis_utilization'),
    path('ecs-utilization/', ecs_utilization, name='ecs_utilization'),
    path('ec2-utilization-ui/', ec2_utilization_ui, name='ec2_utilization_ui'),
    path('rds-utilization-ui/', rds_utilization_ui, name='rds_utilization_ui'),
    path('redis-utilization-ui/', redis_utilization_ui, name='redis_utilization_ui'),
    path('ecs-utilization-ui/', ecs_utilization_ui, name='ecs_utilization_ui'),
    path('export-ec2-excel/',export_ec2_excel, name='export_ec2_excel'),
    path('export/asg/', export_asg_excel, name='export_asg_excel'),
    path('export/ami/', export_ami_excel, name='export_ami_excel'),
    path('export/snapshot/', export_snapshot_excel, name='export_snapshot_excel'),
    path('export/url-health/', export_url_health_excel, name='export_url_health_excel'),
    path('ami-summary/', ami_summary, name='ami_summary'),
    path('snapshots-summary/', snapshots_summary, name='snapshots_summary'),
    path('lb-summary/',lb_summary, name='lb_summary'),
    path('export/lb/', export_lb_excel, name='export_lb_excel'),
    path('export/ec2_utilization/', export_ec2_utilization_excel,name='export_ec2_utilization_excel'),
    path('lambda-summary/',lambda_summary, name='lambda_summary'),
    path('export/lambda/', export_lambda_excel, name='export_lambda_excel'),
    path('export/rds_utilization/', export_rds_utilization_excel,name='export_rds_utilization_excel'),
    path('export/ecs_utilization/', export_ecs_utilization_excel,name='export_ecs_utilization_excel'),
    path('target-group-summary/', target_group_list,name='target_group_list'),
    path('asg-utilization/', asg_utilization, name='asg_utilization'),
    path('asg-utilization-ui/', asg_utilization_ui, name='asg_utilization_ui'),

]
