# Deployment & Setup Guide

## Overview

This guide covers deploying the NDMA Volunteer API in different environments: Development, Staging, and Production.

---

## Prerequisites

### System Requirements
- Python 3.8+
- MySQL 5.7+ or MariaDB
- Redis (for caching)
- 2GB RAM minimum
- 10GB disk space

### Software
- Python 3.8+
- pip (Python package manager)
- virtualenv or venv
- git

---

## Development Setup (Local)

### 1. Clone Repository

```bash
git clone https://github.com/your-repo/ndma_api.git
cd ndma_api
```

### 2. Create Virtual Environment

```bash
# On Windows
python -m venv ndma-venv
ndma-venv\Scripts\activate

# On macOS/Linux
python3 -m venv ndma-venv
source ndma-venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

**Key packages:**
- Django==4.2.5
- djangorestframework==3.14.0
- djangorestframework-simplejwt==5.2.2
- mysqlclient==2.2.8
- redis==4.5.5

### 4. Configure Database

**Create `config/settings/dev.py`:**
```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'ndma_dev',
        'USER': 'root',
        'PASSWORD': 'password',
        'HOST': 'localhost',
        'PORT': '3306',
    }
}
```

### 5. Apply Migrations

```bash
python manage.py migrate
```

### 6. Create Superuser

```bash
python manage.py createsuperuser
```

### 7. Seed Initial Data

```bash
# Create states and districts
python manage.py shell < scripts/seed_states.py

# Create organizations
python manage.py shell < scripts/seed_organizations.py

# Create roles
python manage.py shell < scripts/seed_roles.py
```

### 8. Run Development Server

```bash
python manage.py runserver
```

**Access at:** http://localhost:8000

**API at:** http://localhost:8000/api/v1/

---

## Staging Setup

### 1. Server Setup

**On Ubuntu 20.04:**
```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install dependencies
sudo apt install python3.9 python3.9-venv python3-pip mysql-server redis-server nginx gunicorn -y

# Install mysqlclient dependencies
sudo apt install python3-dev default-libmysqlclient-dev -y
```

### 2. Create Deployment User

```bash
sudo useradd -m -s /bin/bash ndma
sudo usermod -aG sudo ndma
```

### 3. Clone & Setup Project

```bash
sudo su - ndma
git clone https://github.com/your-repo/ndma_api.git
cd ndma_api
python3.9 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

### 4. Configure Environment

**Create `.env` file:**
```bash
# Django
ENVIRONMENT=staging
DEBUG=False
SECRET_KEY=your-secret-key-here-very-long-and-random
ALLOWED_HOSTS=staging.ndma.gov.in,api-staging.ndma.gov.in

# Database
DB_ENGINE=django.db.backends.mysql
DB_NAME=ndma_staging
DB_USER=ndma_user
DB_PASSWORD=secure_password
DB_HOST=localhost
DB_PORT=3306

# JWT
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_LIFETIME_SECONDS=900
JWT_REFRESH_TOKEN_LIFETIME_DAYS=7

# Email
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-password

# Redis
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_DB=0

# API
API_LOG_LEVEL=INFO
API_DEBUG_MODE=False
```

### 5. Configure Settings

**Update `config/settings/staging.py`:**
```python
import os
from .base import *

DEBUG = os.getenv('DEBUG', False) == 'True'
ENVIRONMENT = 'staging'

ALLOWED_HOSTS = os.getenv('ALLOWED_HOSTS', '').split(',')

DATABASES = {
    'default': {
        'ENGINE': os.getenv('DB_ENGINE'),
        'NAME': os.getenv('DB_NAME'),
        'USER': os.getenv('DB_USER'),
        'PASSWORD': os.getenv('DB_PASSWORD'),
        'HOST': os.getenv('DB_HOST'),
        'PORT': os.getenv('DB_PORT'),
    }
}

# Cache
CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': 'redis://{}:{}/{}'.format(
            os.getenv('REDIS_HOST'),
            os.getenv('REDIS_PORT'),
            os.getenv('REDIS_DB')
        ),
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
        }
    }
}
```

### 6. Run Migrations

```bash
export DJANGO_SETTINGS_MODULE=config.settings.staging
python manage.py migrate
python manage.py collectstatic --noinput
```

### 7. Configure Gunicorn

**Create `/etc/systemd/system/ndma-api.service`:**
```ini
[Unit]
Description=NDMA API Gunicorn Service
After=network.target

[Service]
Type=notify
User=ndma
WorkingDirectory=/home/ndma/ndma_api
ExecStart=/home/ndma/ndma_api/venv/bin/gunicorn \
    --workers 4 \
    --worker-class uvicorn.workers.UvicornWorker \
    --bind unix:/run/ndma-api.sock \
    --timeout 120 \
    --access-logfile /var/log/ndma-api/access.log \
    --error-logfile /var/log/ndma-api/error.log \
    config.wsgi:application

Restart=on-failure
RestartSec=10

[Install]
WantedBy=multi-user.target
```

### 8. Configure Nginx

**Create `/etc/nginx/sites-available/ndma-api`:**
```nginx
upstream ndma_api {
    server unix:/run/ndma-api.sock;
}

server {
    listen 80;
    server_name staging.ndma.gov.in api-staging.ndma.gov.in;

    client_max_body_size 20M;

    location /api {
        proxy_pass http://ndma_api;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /static {
        alias /home/ndma/ndma_api/staticfiles;
    }

    location /media {
        alias /home/ndma/ndma_api/media;
    }
}
```

### 9. Enable Services

```bash
sudo systemctl enable ndma-api
sudo systemctl start ndma-api
sudo systemctl enable nginx
sudo systemctl restart nginx
```

### 10. Verify Deployment

```bash
curl http://staging.ndma.gov.in/api/v1/health/status/
```

---

## Production Setup

### 1. Server Configuration

**Recommended specs:**
- 4+ CPU cores
- 8GB+ RAM
- 50GB+ SSD
- Auto-scaling setup

### 2. Security Setup

**Create firewall rules:**
```bash
sudo ufw allow 22/tcp
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw enable
```

**Add SSL certificates (Let's Encrypt):**
```bash
sudo apt install certbot python3-certbot-nginx -y
sudo certbot certonly --nginx -d api.ndma.gov.in
```

### 3. Database Hardening

**Create database user:**
```bash
mysql -u root -p
CREATE USER 'ndma_prod'@'localhost' IDENTIFIED BY 'strong-password-here';
GRANT ALL PRIVILEGES ON ndma_prod.* TO 'ndma_prod'@'localhost';
FLUSH PRIVILEGES;
```

**Enable backups:**
```bash
# Daily backup script
0 2 * * * mysqldump -u ndma_prod -p'password' ndma_prod > /backups/db_$(date +\%Y\%m\%d).sql
```

### 4. Production Configuration

**Create `config/settings/prod.py`:**
```python
import os
from .base import *

DEBUG = False
ENVIRONMENT = 'production'

ALLOWED_HOSTS = os.getenv('ALLOWED_HOSTS', '').split(',')
CSRF_TRUSTED_ORIGINS = os.getenv('CSRF_TRUSTED_ORIGINS', '').split(',')

# HTTPS only
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True

# Security headers
SECURE_CONTENT_SECURITY_POLICY = {
    'default-src': ("'self'",),
    'script-src': ("'self'", "'unsafe-inline'"),
    'style-src': ("'self'", "'unsafe-inline'"),
}

# Database with connection pooling
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': os.getenv('DB_NAME'),
        'USER': os.getenv('DB_USER'),
        'PASSWORD': os.getenv('DB_PASSWORD'),
        'HOST': os.getenv('DB_HOST'),
        'PORT': os.getenv('DB_PORT'),
        'CONN_MAX_AGE': 600,
        'OPTIONS': {
            'charset': 'utf8mb4',
        }
    }
}

# Logging
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'file': {
            'level': 'ERROR',
            'class': 'logging.FileHandler',
            'filename': '/var/log/ndma-api/error.log',
        },
        'console': {
            'level': 'INFO',
            'class': 'logging.StreamHandler',
        },
    },
    'root': {
        'handlers': ['file', 'console'],
        'level': 'INFO',
    },
}
```

### 5. Advanced Gunicorn Config

**Create `gunicorn_config.py`:**
```python
import multiprocessing

bind = "unix:/run/ndma-api.sock"
workers = multiprocessing.cpu_count() * 2 + 1
worker_class = "uvicorn.workers.UvicornWorker"
worker_connections = 1000
max_requests = 1000
max_requests_jitter = 100
timeout = 120
keepalive = 5

# Logging
accesslog = "/var/log/ndma-api/access.log"
errorlog = "/var/log/ndma-api/error.log"
loglevel = "info"
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s" %(D)s'

# Process naming
proc_name = "ndma-api"
```

### 6. Health Checks

**Setup monitoring:**
```bash
# System metrics
curl http://api.ndma.gov.in/api/v1/health/status/
curl http://api.ndma.gov.in/api/v1/health/alive/
curl http://api.ndma.gov.in/api/v1/health/readiness/

# Database health
curl http://api.ndma.gov.in/api/v1/health/database/

# Cache health
curl http://api.ndma.gov.in/api/v1/health/cache/
```

### 7. Monitoring & Alerts

**Setup Prometheus/Grafana:**
```bash
# Install Prometheus
wget https://github.com/prometheus/prometheus/releases/download/v2.35.0/prometheus-2.35.0.linux-amd64.tar.gz
# Configure and start

# Install Grafana
sudo apt install grafana-server -y
```

### 8. Disaster Recovery

**Setup automated backups:**
```bash
# Database backup
0 2 * * * mysqldump -u ndma_prod -p'password' ndma_prod | gzip > /backups/db_$(date +\%Y\%m\%d).sql.gz

# Application backup
0 3 * * 0 tar -czf /backups/app_$(date +\%Y\%m\%d).tar.gz /home/ndma/ndma_api

# Retention: Keep 90 days
30 4 * * * find /backups -name "*.gz" -mtime +90 -delete
```

---

## Deployment Checklist

### Pre-Deployment
- [ ] Code reviewed and merged to main
- [ ] All tests passing
- [ ] Database migrations tested
- [ ] Security scan completed
- [ ] Performance benchmarks acceptable
- [ ] Documentation updated

### Deployment
- [ ] Backup database and code
- [ ] Deploy application code
- [ ] Run database migrations
- [ ] Collect static files
- [ ] Restart application service
- [ ] Clear cache
- [ ] Verify health checks
- [ ] Test critical endpoints

### Post-Deployment
- [ ] Monitor error logs
- [ ] Check performance metrics
- [ ] Verify user access
- [ ] Communicate status to team
- [ ] Plan rollback if needed

---

## Troubleshooting

### Application Won't Start

```bash
# Check logs
sudo journalctl -u ndma-api -n 50

# Test configuration
python manage.py check

# Test database connection
python manage.py shell
>>> from django.db import connection
>>> connection.ensure_connection()
```

### Database Connection Error

```bash
# Test MySQL connection
mysql -h localhost -u ndma_prod -p

# Check permissions
SHOW GRANTS FOR 'ndma_prod'@'localhost';

# Verify MySQL is running
sudo systemctl status mysql
```

### High Memory Usage

```bash
# Reduce gunicorn workers
# Edit /etc/systemd/system/ndma-api.service
# Change: --workers 2

# Clear cache
redis-cli FLUSHDB

# Monitor memory
free -h
ps aux --sort=-%mem | head
```

### Slow Queries

```bash
# Enable slow query log
SET GLOBAL slow_query_log = 'ON';
SET GLOBAL long_query_time = 2;

# Check MySQL logs
tail -f /var/log/mysql/slow.log

# Analyze with Django Debug Toolbar
# Add django_debug_toolbar to INSTALLED_APPS (dev only)
```

---

## Database Optimization

### Indexes

```sql
-- Volunteer indexes
CREATE INDEX idx_volunteer_mis_id ON volunteer(mis_id);
CREATE INDEX idx_volunteer_email ON volunteer(email);
CREATE INDEX idx_volunteer_organization ON volunteer(organization_id);
CREATE INDEX idx_volunteer_state ON volunteer(state_id);

-- User indexes
CREATE INDEX idx_user_email ON auth_user(email);

-- Role assignment indexes
CREATE INDEX idx_role_user ON role_assignment(user_id);
CREATE INDEX idx_role_state ON role_assignment(state_id);
```

### Query Optimization

```bash
# Enable query cache
SET GLOBAL query_cache_type = 1;
SET GLOBAL query_cache_size = 268435456; # 256MB

# Connection pooling
SET GLOBAL max_connections = 500;
SET GLOBAL max_allowed_packet = 64M;
```

---

## Scaling Considerations

### Horizontal Scaling (Multiple Servers)

```
Load Balancer
   ↓
API Server 1 (Gunicorn)
API Server 2 (Gunicorn)
API Server 3 (Gunicorn)
   ↓ (Shared)
Database Server (MySQL with replication)
Cache Server (Redis Cluster)
```

### Vertical Scaling (Single Server)

- Increase CPU cores
- Increase RAM
- Use SSD storage
- Enable connection pooling
- Optimize database indexes

### Auto-Scaling (Cloud)

```hcl
# Terraform example
resource "aws_autoscaling_group" "ndma_api" {
  name = "ndma-api-asg"
  min_size = 2
  max_size = 10
  desired_capacity = 3
  launch_template {
    id = aws_launch_template.ndma_api.id
    version = "$Latest"
  }
}
```

---

## Monitoring

### Key Metrics

- Response time (p50, p95, p99)
- Error rate (4xx, 5xx %)
- Throughput (requests/sec)
- Database query time
- Cache hit rate
- CPU usage
- Memory usage
- Disk I/O

### Alerting Rules

```
- CPU > 80% for 5 min → Alert
- Memory > 85% → Alert  
- Error rate > 1% → Alert
- Response time p95 > 1000ms → Alert
- Database connection pool > 80% → Alert
```

---

## Rollback Procedure

### If Deployment Fails

```bash
# 1. Stop current deployment
sudo systemctl stop ndma-api

# 2. Restore previous code
cd /home/ndma/ndma_api
git checkout previous-tag

# 3. Reinstall dependencies if needed
source venv/bin/activate
pip install -r requirements.txt

# 4. Rollback database (if migrations run)
python manage.py migrate previous-migration-number

# 5. Start application
sudo systemctl start ndma-api

# 6. Verify
curl http://api.ndma.gov.in/api/v1/health/status/
```

---

