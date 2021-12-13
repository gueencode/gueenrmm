import os
from datetime import timedelta
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

SCRIPTS_DIR = "/srv/salt/scripts"

DOCKER_BUILD = False

LOG_DIR = os.path.join(BASE_DIR, "gueenrmm/private/log")

EXE_DIR = os.path.join(BASE_DIR, "gueenrmm/private/exe")

AUTH_USER_MODEL = "accounts.User"

# latest release
GRMM_VERSION = "0.10.5"

# bump this version everytime vue code is changed
# to alert user they need to manually refresh their browser
APP_VER = "0.0.153"

# https://github.com/gueencode/rmmagent
LATEST_AGENT_VER = "1.7.1"

MESH_VER = "0.9.55"

NATS_SERVER_VER = "2.3.3"

# for the update script, bump when need to recreate venv or npm install
PIP_VER = "24"
NPM_VER = "26"

SETUPTOOLS_VER = "59.4.0"
WHEEL_VER = "0.37.0"

DL_64 = f"https://github.com/gueencode/rmmagent/releases/download/v{LATEST_AGENT_VER}/winagent-v{LATEST_AGENT_VER}.exe"
DL_32 = f"https://github.com/gueencode/rmmagent/releases/download/v{LATEST_AGENT_VER}/winagent-v{LATEST_AGENT_VER}-x86.exe"

EXE_GEN_URLS = [
    "https://exe2.gueenrmm.io",
    "https://exe.gueenrmm.io",
]

DEFAULT_AUTO_FIELD = "django.db.models.AutoField"

ASGI_APPLICATION = "gueenrmm.asgi.application"

REST_KNOX = {
    "TOKEN_TTL": timedelta(hours=5),
    "AUTO_REFRESH": True,
    "MIN_REFRESH_INTERVAL": 600,
}

try:
    from .local_settings import *
except ImportError:
    pass

REST_FRAMEWORK = {
    "DATETIME_FORMAT": "%b-%d-%Y - %H:%M",
    "DEFAULT_PERMISSION_CLASSES": ("rest_framework.permissions.IsAuthenticated",),
    "DEFAULT_AUTHENTICATION_CLASSES": (
        "knox.auth.TokenAuthentication",
        "gueenrmm.auth.APIAuthentication",
    ),
    "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",
}

SPECTACULAR_SETTINGS = {
    "TITLE": "Gueen RMM API",
    "DESCRIPTION": "Simple and Fast remote monitoring and management tool",
    "VERSION": grmm_VERSION,
}

if not "AZPIPELINE" in os.environ:
    if not DEBUG:  # type: ignore
        REST_FRAMEWORK.update(
            {"DEFAULT_RENDERER_CLASSES": ("rest_framework.renderers.JSONRenderer",)}
        )

INSTALLED_APPS = [
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.staticfiles",
    "channels",
    "rest_framework",
    "rest_framework.authtoken",
    "knox",
    "corsheaders",
    "accounts",
    "apiv3",
    "clients",
    "agents",
    "checks",
    "services",
    "winupdate",
    "software",
    "core",
    "automation",
    "autotasks",
    "logs",
    "scripts",
    "alerts",
    "drf_spectacular",
]

if not "AZPIPELINE" in os.environ:
    if DEBUG:  # type: ignore
        INSTALLED_APPS += ("django_extensions",)

    CHANNEL_LAYERS = {
        "default": {
            "BACKEND": "channels_redis.core.RedisChannelLayer",
            "CONFIG": {
                "hosts": [(REDIS_HOST, 6379)],  # type: ignore
            },
        },
    }

if "AZPIPELINE" in os.environ:
    ADMIN_ENABLED = False

if ADMIN_ENABLED:  # type: ignore
    INSTALLED_APPS += (
        "django.contrib.admin",
        "django.contrib.messages",
    )


MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "corsheaders.middleware.CorsMiddleware",  ##
    "gueenrmm.middleware.LogIPMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "gueenrmm.middleware.AuditMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

if ADMIN_ENABLED:  # type: ignore
    MIDDLEWARE += ("django.contrib.messages.middleware.MessageMiddleware",)


ROOT_URLCONF = "gueenrmm.urls"


TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "gueenrmm.wsgi.application"

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]


LANGUAGE_CODE = "en-us"

TIME_ZONE = "UTC"

USE_I18N = True

USE_L10N = True

USE_TZ = True


STATIC_URL = "/static/"

STATIC_ROOT = os.path.join(BASE_DIR, "static")
STATICFILES_DIRS = [os.path.join(BASE_DIR, "gueenrmm/static/")]

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {
        "file": {
            "level": "ERROR",
            "class": "logging.FileHandler",
            "filename": os.path.join(LOG_DIR, "django_debug.log"),
        }
    },
    "loggers": {
        "django.request": {"handlers": ["file"], "level": "ERROR", "propagate": True}
    },
}

if "AZPIPELINE" in os.environ:
    print("PIPELINE")
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.postgresql",
            "NAME": "pipeline",
            "USER": "pipeline",
            "PASSWORD": "pipeline123456",
            "HOST": "127.0.0.1",
            "PORT": "",
        }
    }

    REST_FRAMEWORK = {
        "DATETIME_FORMAT": "%b-%d-%Y - %H:%M",
        "DEFAULT_PERMISSION_CLASSES": ("rest_framework.permissions.IsAuthenticated",),
        "DEFAULT_AUTHENTICATION_CLASSES": (
            "knox.auth.TokenAuthentication",
            "gueenrmm.auth.APIAuthentication",
        ),
        "DEFAULT_RENDERER_CLASSES": ("rest_framework.renderers.JSONRenderer",),
    }

    ALLOWED_HOSTS = ["api.example.com"]
    DEBUG = True
    SECRET_KEY = "abcdefghijklmnoptravis123456789"

    ADMIN_URL = "abc123456/"

    SCRIPTS_DIR = os.path.join(Path(BASE_DIR).parents[1], "scripts")
    MESH_USERNAME = "pipeline"
    MESH_SITE = "https://example.com"
    MESH_TOKEN_KEY = "bd65e957a1e70c622d32523f61508400d6cd0937001a7ac12042227eba0b9ed625233851a316d4f489f02994145f74537a331415d00047dbbf13d940f556806dffe7a8ce1de216dc49edbad0c1a7399c"
    REDIS_HOST = "localhost"
