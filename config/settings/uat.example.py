from .base import *
import os

# UAT settings example. Copy to `uat.py` and fill real secrets via env vars.

DEBUG = False

ALLOWED_HOSTS = os.environ.get('UAT_ALLOWED_HOSTS', 'localhost').split(',')

# Database configuration for MariaDB (compatible with MySQL)
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': os.environ.get('UAT_DB_NAME', 'ndma_uat'),
        'USER': os.environ.get('UAT_DB_USER', 'root'),
        'PASSWORD': os.environ.get('UAT_DB_PASSWORD', ''),
        'HOST': os.environ.get('UAT_DB_HOST', '127.0.0.1'),
        'PORT': os.environ.get('UAT_DB_PORT', '3306'),
        'OPTIONS': {
            'init_command': "SET sql_mode='STRICT_TRANS_TABLES'",
        },
    }
}

# Cache (example using local memory — replace with Redis for production/UAT)
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
    }
}

# Any additional UAT-specific settings can go here.
