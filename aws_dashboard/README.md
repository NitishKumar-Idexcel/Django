# AWS Monitoring Dashboard 🚀

A comprehensive Django-based dashboard for monitoring AWS services and resources in real-time.

## Project Overview 📋

This dashboard provides real-time monitoring and management capabilities for various AWS services, helping DevOps teams and system administrators maintain their AWS infrastructure efficiently.

## Directory Structure 📂

```
aws_dashboard/
├── aws_dashboard/          # Main project directory
│   ├── __init__.py
│   ├── asgi.py
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── dashboard/             # Main application
│   ├── migrations/
│   ├── templates/
│   │   └── dashboard/
│   │       ├── partials/
│   │       │   ├── ami.html
│   │       │   ├── asg.html
│   │       │   ├── ec2.html
│   │       │   ├── ecs.html
│   │       │   ├── lambda.html
│   │       │   ├── load_balancer.html
│   │       │   ├── rds.html
│   │       │   └── snapshots.html
│   │       └── index.html
│   ├── __init__.py
│   ├── admin.py
│   ├── apps.py
│   ├── aws_utils.py
│   ├── models.py
│   ├── tests.py
│   ├── url_checker.py
│   ├── urls.py
│   └── views.py
├── manage.py
├── requirements.txt
└── db.sqlite3
```

## Features 🌟

### EC2 Monitoring 💻
- Instance status tracking
- CPU utilization metrics
- Launch time monitoring
- Export to Excel functionality

### RDS Monitoring 🗄️
- Database instance tracking
- CPU and memory utilization
- Performance metrics
- Excel report generation

### Auto Scaling Groups ⚖️
- Group capacity monitoring
- Instance count tracking
- Min/Max size monitoring
- Excel export capability

### Load Balancer Monitoring 🔄
- Load balancer status
- Type and state tracking
- Export functionality

### Lambda Functions ⚡
- Function listing
- Runtime information
- Memory allocation tracking
- Excel report generation

### URL Health Checking 🔍
- Endpoint monitoring
- Status code tracking
- Response time monitoring
- Health status exports

## Technical Requirements 🛠️

### Prerequisites
- Python 3.x
- Django
- AWS Account with appropriate permissions
- AWS CLI configured

### Required Python Packages
```
boto3==1.26.137
Django==4.2.1
requests==2.30.0
openpyxl==3.1.2
python-dotenv==1.0.0
```

## Installation Guide 📥

1. **Clone the Repository**
```bash
git clone <repository-url>
cd aws_dashboard
```

2. **Set Up Virtual Environment**
```bash
python -m venv venv
# Windows
.\venv\Scripts\activate
# Linux/Mac
source venv/bin/activate
```

3. **Install Dependencies**
```bash
pip install -r requirements.txt
```

4. **Configure AWS Credentials**
```bash
aws configure
# Enter your AWS Access Key ID
# Enter your AWS Secret Access Key
# Enter your default region
# Enter your output format (json)
```

5. **Environment Variables**
Create a `.env` file in the root directory:
```env
SECRET_KEY=your_django_secret_key
DEBUG=True
AWS_ACCESS_KEY_ID=your_aws_access_key
AWS_SECRET_ACCESS_KEY=your_aws_secret_key
AWS_DEFAULT_REGION=your_aws_region
```

6. **Database Setup**
```bash
python manage.py makemigrations
python manage.py migrate
```

7. **Run Development Server**
```bash
python manage.py runserver
```

## Usage Guide 📱

1. Access the dashboard at `http://localhost:8000`
2. Navigate through different services using the navigation tabs
3. View real-time metrics and status updates
4. Export reports as needed

## Key Components 🔧

### AWS Utils (`aws_utils.py`)
- Handles AWS service interactions
- Manages boto3 clients and resources
- Implements AWS API calls

### URL Checker (`url_checker.py`)
- Monitors endpoint health
- Tracks response times
- Manages URL status checks

### Views (`views.py`)
- Implements dashboard logic
- Handles data processing
- Manages page rendering

## Maintenance 🔄

### Regular Updates
```bash
git pull origin main
pip install -r requirements.txt
python manage.py migrate
```

### AWS Credential Verification
```bash
aws sts get-caller-identity
```

## Security Best Practices 🔒

1. Never commit AWS credentials
2. Use environment variables for sensitive data
3. Regularly rotate AWS access keys
4. Monitor AWS CloudTrail logs
5. Implement proper IAM roles and permissions

## Contributing 🤝

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Submit a Pull Request

## Troubleshooting 🔍

Common issues and solutions:
1. AWS credential errors: Verify `.aws/credentials`
2. Database migrations: Check migration history
3. Package conflicts: Update requirements.txt


## Acknowledgments 🙏

- AWS SDK for Python (Boto3)
- Django Framework
- Bootstrap for UI
- Community contributors
