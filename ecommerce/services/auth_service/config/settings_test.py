"""
Test-specific Django settings.
Uses SQLite in-memory so no PostgreSQL instance is needed to run tests.
"""
from .settings import *  # noqa: F401, F403

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": ":memory:",
    }
}

# Speed up password hashing in tests
PASSWORD_HASHERS = ["django.contrib.auth.hashers.MD5PasswordHasher"]

# Disable token blacklist to avoid migration issues in tests
INSTALLED_APPS = [app for app in INSTALLED_APPS if app != "rest_framework_simplejwt.token_blacklist"]  # noqa: F405

# Use a fixed secret/signing key
SECRET_KEY = "test-secret-key-not-for-production"
JWT_SIGNING_KEY = SECRET_KEY

SIMPLE_JWT = {
    **SIMPLE_JWT,  # noqa: F405
    "SIGNING_KEY": SECRET_KEY,
    "BLACKLIST_AFTER_ROTATION": False,
    "ROTATE_REFRESH_TOKENS": False,
}

INTERNAL_SERVICE_TOKEN = "test-internal-token"

# Suppress logging noise during tests
import logging  # noqa: E402
logging.disable(logging.CRITICAL)
