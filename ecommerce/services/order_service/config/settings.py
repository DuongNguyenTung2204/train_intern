import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

JWT_SIGNING_KEY        = os.environ.get("JWT_SIGNING_KEY", "dev-secret")
INTERNAL_SERVICE_TOKEN = os.environ.get("INTERNAL_SERVICE_TOKEN", "internal-svc-token")
CART_SERVICE_URL       = os.environ.get("CART_SERVICE_URL",    "http://localhost:8003")
PRODUCT_SERVICE_URL    = os.environ.get("PRODUCT_SERVICE_URL", "http://localhost:8002")

SECRET_KEY   = JWT_SIGNING_KEY
DEBUG        = os.environ.get("DEBUG", "true").lower() == "true"
ALLOWED_HOSTS = ["*"]

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "rest_framework",
    "apps.orders",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
]

ROOT_URLCONF     = "config.urls"
WSGI_APPLICATION = "config.wsgi.application"

TEMPLATES = [{
    "BACKEND": "django.template.backends.django.DjangoTemplates",
    "DIRS": [],
    "APP_DIRS": True,
    "OPTIONS": {"context_processors": [
        "django.template.context_processors.request",
        "django.contrib.auth.context_processors.auth",
        "django.contrib.messages.context_processors.messages",
    ]},
}]

DATABASES = {
    "default": {
        "ENGINE":   "django.db.backends.postgresql",
        "NAME":     os.environ.get("DB_NAME", "order_db"),
        "USER":     os.environ.get("DB_USER", "postgres"),
        "PASSWORD": os.environ.get("DB_PASSWORD", "postgres"),
        "HOST":     os.environ.get("DB_HOST", "localhost"),
        "PORT":     os.environ.get("DB_PORT", "5432"),
    }
}

LANGUAGE_CODE      = "en-us"
TIME_ZONE          = "Asia/Ho_Chi_Minh"
USE_TZ             = True
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
STATIC_URL         = "/static/"

REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": ("utils.authentication.MicroserviceJWTAuthentication",),
    "DEFAULT_PERMISSION_CLASSES": ("rest_framework.permissions.IsAuthenticated",),
}

# ── Celery ────────────────────────────────────────────────────────────────────
CELERY_BROKER_URL    = os.environ.get("REDIS_URL", "redis://localhost:6379/0")
CELERY_RESULT_BACKEND = CELERY_BROKER_URL
CELERY_ACCEPT_CONTENT = ["json"]
CELERY_TASK_SERIALIZER = "json"
CELERY_TIMEZONE       = TIME_ZONE

# ── Email ─────────────────────────────────────────────────────────────────────
EMAIL_BACKEND     = os.environ.get("EMAIL_BACKEND", "django.core.mail.backends.console.EmailBackend")
EMAIL_HOST        = os.environ.get("EMAIL_HOST", "smtp.gmail.com")
EMAIL_PORT        = int(os.environ.get("EMAIL_PORT", "587"))
EMAIL_USE_TLS     = True
EMAIL_HOST_USER   = os.environ.get("EMAIL_HOST_USER", "")
EMAIL_HOST_PASSWORD = os.environ.get("EMAIL_HOST_PASSWORD", "")
DEFAULT_FROM_EMAIL  = os.environ.get("DEFAULT_FROM_EMAIL", "noreply@ecommerce.local")
