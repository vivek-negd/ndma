from .base import *
import os

DEBUG = True


# ==========================
# CORS SETTINGS - DEVELOPMENT
# ==========================

CORS_ALLOW_ALL_ORIGINS = True  # Allow all origins (ONLY for development)
ALLOWED_HOSTS = ["*"]
# Optional: If you want only local frontend
CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "http://127.0.0.1:8000",
]

# Allow ngrok and custom headers
CORS_ALLOW_HEADERS = [
    'accept',
    'accept-encoding',
    'authorization',
    'content-type',
    'dnt',
    'origin',
    'user-agent',
    'x-csrftoken',
    'x-requested-with',
    'ngrok-skip-browser-warning',  # Allow ngrok tunnel header
]


# ==========================
# DATABASE - DEVELOPMENT (override to MariaDB if env vars provided)
# ==========================
# If DB_NAME_DEV is set in environment or .env, use MariaDB (mysqlclient)
db_name = os.getenv('DB_NAME_DEV', os.getenv('DB_NAME', 'testdb'))
if db_name:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.mysql',
            'NAME': db_name,
            'USER': os.getenv('DB_USER_DEV', 'root'),
            'PASSWORD': os.getenv('DB_PASSWORD_DEV', ''),
            'HOST': os.getenv('DB_HOST_DEV', '127.0.0.1'),
            'PORT': os.getenv('DB_PORT_DEV', '3306'),
            'OPTIONS': {
                'init_command': "SET sql_mode='STRICT_TRANS_TABLES'",
            },
        }
    }
else:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'temp_migrations.sqlite3',
        }
    }


# ==========================
# LOGGING - DEVELOPMENT (see all API requests & database queries)
# ==========================
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '[{levelname}] {asctime} {name} {message}',
            'style': '{',
            'datefmt': '%Y-%m-%d %H:%M:%S',
        },
        'simple': {
            'format': '[{levelname}] {name}: {message}',
            'style': '{',
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
    },
    'loggers': {
        # Log all HTTP requests (GET, POST, PUT, DELETE, etc)
        'django.server': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': False,
        },
        # Log all database queries
        'django.db.backends': {
            'handlers': ['console'],
            'level': 'DEBUG',
            'propagate': False,
        },
        # Log Django framework messages
        'django': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': False,
        },
        # Log REST framework
        'rest_framework': {
            'handlers': ['console'],
            'level': 'DEBUG',
            'propagate': False,
        },
        # Log authentication
        'core.authentication': {
            'handlers': ['console'],
            'level': 'DEBUG',
            'propagate': False,
        },
        # Log all application logs
        '': {
            'handlers': ['console'],
            'level': 'DEBUG',
            'propagate': False,
        },
    },
}
