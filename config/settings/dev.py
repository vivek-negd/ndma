from .base import *

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