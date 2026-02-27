from .base import *

DEBUG = False


# ==========================
# CORS SETTINGS - PRODUCTION
# ==========================

# ❌ Never enable this in production
# CORS_ALLOW_ALL_ORIGINS = True

# CORS_ALLOWED_ORIGINS = [
#     "https://ndma.gov.in",
#     "https://admin.ndma.gov.in",
# ]

CORS_ALLOW_CREDENTIALS = True