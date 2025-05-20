# Use Python 3.9 slim base image
FROM python:3.9-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    DJANGO_SETTINGS_MODULE=aws_dashboard.settings \
    # Add gunicorn environment variables
    WORKERS=4 \
    PORT=8000 
    # Add AWS environment variables


# Set work directory
WORKDIR /app

# Install system dependencies
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements file
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt \
    # Add gunicorn
    && pip install --no-cache-dir gunicorn
# Copy project files
COPY . .


# Make port 8000 available
EXPOSE 8000

# Create a non-root user
RUN adduser --disabled-password --gecos '' appuser
RUN chown -R appuser:appuser /app
USER appuser

# Run gunicorn
CMD ["gunicorn", "aws_dashboard.wsgi:application", "--bind", "0.0.0.0:8000"]