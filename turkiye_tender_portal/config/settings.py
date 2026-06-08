"""
Django settings for Türkiye İhale Takip Sistemi.

SQLite for MVP, PostgreSQL-ready via DATABASE_URL.
Configuration is read from environment variables (.env) using django-environ.
"""
from pathlib import Path
import environ

BASE_DIR = Path(__file__).resolve().parent.parent

env = environ.Env(
    DEBUG=(bool, False),
    ALLOWED_HOSTS=(list, ["127.0.0.1", "localhost"]),
    DATABASE_URL=(str, ""),
    FETCH_REQUEST_DELAY=(float, 1.5),
    FETCH_MAX_RETRIES=(int, 3),
    FETCH_TIMEOUT=(int, 30),
    FETCH_MANUAL_COOLDOWN=(int, 60),
    EKAP_DATA_MODE=(str, "live"),
    DEFAULT_TRIAL_DAYS=(int, 14),
)

# Read .env if present
environ.Env.read_env(BASE_DIR / ".env")

SECRET_KEY = env("SECRET_KEY", default="dev-insecure-change-me")
DEBUG = env("DEBUG")
ALLOWED_HOSTS = env("ALLOWED_HOSTS")

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    # Local apps
    "accounts",
    "tenders",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "config.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "accounts.context_processors.subscription_context",
            ],
        },
    },
]

WSGI_APPLICATION = "config.wsgi.application"
ASGI_APPLICATION = "config.asgi.application"

# Database: SQLite by default, PostgreSQL when DATABASE_URL is set.
_database_url = env("DATABASE_URL")
if _database_url:
    DATABASES = {"default": env.db("DATABASE_URL")}
else:
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": BASE_DIR / "db.sqlite3",
        }
    }

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

LANGUAGE_CODE = "tr"
TIME_ZONE = "Europe/Istanbul"
USE_I18N = True
USE_TZ = True

STATIC_URL = "static/"
STATICFILES_DIRS = [BASE_DIR / "tenders" / "static"]
STATIC_ROOT = BASE_DIR / "staticfiles"

MEDIA_URL = "media/"
MEDIA_ROOT = BASE_DIR / "media"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# Authentication
LOGIN_URL = "login"
LOGIN_REDIRECT_URL = "dashboard"
LOGOUT_REDIRECT_URL = "login"

# Exports
EXPORT_DIR = BASE_DIR / "exports" / "excel"
EXPORT_DIR.mkdir(parents=True, exist_ok=True)

# Fetch / scraping settings
FETCH_REQUEST_DELAY = env("FETCH_REQUEST_DELAY")
FETCH_MAX_RETRIES = env("FETCH_MAX_RETRIES")
FETCH_TIMEOUT = env("FETCH_TIMEOUT")
FETCH_MANUAL_COOLDOWN = env("FETCH_MANUAL_COOLDOWN")
EKAP_DATA_MODE = env("EKAP_DATA_MODE")
USE_MOCK_TENDER_SOURCE = (EKAP_DATA_MODE == "mock")
DEFAULT_TRIAL_DAYS = env("DEFAULT_TRIAL_DAYS")

# Logging
LOGS_DIR = BASE_DIR / "logs"
LOGS_DIR.mkdir(parents=True, exist_ok=True)
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "verbose": {
            "format": "{asctime} [{levelname}] {name}: {message}",
            "style": "{",
        },
    },
    "handlers": {
        "file": {
            "class": "logging.FileHandler",
            "filename": str(LOGS_DIR / "app.log"),
            "formatter": "verbose",
        },
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "verbose",
        },
    },
    "loggers": {
        "tenders": {"handlers": ["file", "console"], "level": "INFO", "propagate": False},
        "accounts": {"handlers": ["file", "console"], "level": "INFO", "propagate": False},
    },
}
