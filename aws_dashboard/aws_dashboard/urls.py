"""
URL configuration for aws_dashboard project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from dashboard import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.index, name='dashboard'),
    path('ec2/', views.ec2_today_status, name='ec2'),
    path('asg-summary/', views.asg_summary, name='asg_summary'),
    path('url-health/', views.url_health_check, name='url_health'),
    path('ec2-utilization/', views.ec2_utilization, name='ec2_utilization'),
    path('rds-utilization/', views.rds_utilization, name='rds_utilization'),
    path('ecs-utilization/', views.ecs_utilization, name='ecs_utilization'),
    path('ec2-utilization-ui/', views.ec2_utilization_ui, name='ec2_utilization_ui'),
    path('rds-utilization-ui/', views.rds_utilization_ui, name='rds_utilization_ui'),
    path('ecs-utilization-ui/', views.ecs_utilization_ui, name='ecs_utilization_ui'),
    path('export-ec2-excel/',views.export_ec2_excel, name='export_ec2_excel'),
    path('export/asg/', views.export_asg_excel, name='export_asg_excel'),
    path('export/ami/', views.export_ami_excel, name='export_ami_excel'),
    path('export/snapshot/', views.export_snapshot_excel, name='export_snapshot_excel'),
    path('export/url-health/', views.export_url_health_excel, name='export_url_health_excel'),
    path('ami-summary/', views.ami_summary, name='ami_summary'),
    path('snapshots-summary/', views.snapshots_summary, name='snapshots_summary'),
    path('lb-summary/',views.lb_summary, name='lb_summary'),
    path('export/lb/', views.export_lb_excel, name='export_lb_excel'),
    path('export/ec2_utilization/', views.export_ec2_utilization_excel,name='export_ec2_utilization_excel'),
    path('lambda-summary/',views.lambda_summary, name='lambda_summary'),
    path('export/lambda/', views.export_lambda_excel, name='export_lambda_excel'),
    path('export/rds_utilization/', views.export_rds_utilization_excel,name='export_rds_utilization_excel'),
    path('export/ecs_utilization/', views.export_ecs_utilization_excel,name='export_ecs_utilization_excel'),
]
