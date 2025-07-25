#
# Copyright (c) nexB Inc. and others. All rights reserved.
# VulnerableCode is a trademark of nexB Inc.
# SPDX-License-Identifier: Apache-2.0
# See http://www.apache.org/licenses/LICENSE-2.0 for the license text.
# See https://github.com/aboutcode-org/vulnerablecode for support or download.
# See https://aboutcode.org for more information about nexB OSS projects.
#

import sys
from pathlib import Path

import environ

from vulnerablecode import __version__

VULNERABLECODE_VERSION = __version__

PROJECT_DIR = Path(__file__).resolve().parent
ROOT_DIR = PROJECT_DIR.parent

# Environment

ENV_FILE = "/etc/vulnerablecode/.env"
if not Path(ENV_FILE).exists():
    ENV_FILE = ROOT_DIR / ".env"

env = environ.Env()
environ.Env.read_env(str(ENV_FILE))

# Security

SECRET_KEY = env.str("SECRET_KEY")

ALLOWED_HOSTS = env.list("ALLOWED_HOSTS", default=[".localhost", "127.0.0.1", "[::1]"])

VULNERABLECODE_PASSWORD_MIN_LENGTH = env.int("VULNERABLECODE_PASSWORD_MIN_LENGTH", default=14)

CSRF_TRUSTED_ORIGINS = env.list("CSRF_TRUSTED_ORIGINS", default=[])

# Altcha 32-byte hexadecimal key

ALTCHA_HMAC_KEY = env.str("ALTCHA_HMAC_KEY")

# SECURITY WARNING: do not run with debug turned on in production
DEBUG = env.bool("VULNERABLECODE_DEBUG", default=False)

# SECURITY WARNING: do not  run with debug turned on in production
DEBUG_TOOLBAR = env.bool("VULNERABLECODE_DEBUG_TOOLBAR", default=False)

# SECURITY WARNING: do not  run with debug turned on in production
DEBUG_UI = env.bool("VULNERABLECODE_DEBUG_UI", default=False)

EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
EMAIL_HOST = env.str("EMAIL_HOST", default="")
EMAIL_USE_TLS = True
EMAIL_PORT = 587
EMAIL_HOST_USER = env.str("EMAIL_HOST_USER", default="")
EMAIL_HOST_PASSWORD = env.str("EMAIL_HOST_PASSWORD", default="")
FROM_EMAIL = env.str("FROM_EMAIL", default="")

VULNERABLECODE_LOG_LEVEL = env.str("VULNERABLECODE_LOG_LEVEL", "INFO")

# Application definition

INSTALLED_APPS = (
    # Local apps
    # Must come before Third-party apps for proper templates override
    "vulnerabilities",
    # Django built-in
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.admin",
    "django.contrib.humanize",
    # Third-party apps
    "django_extensions",
    "django_filters",
    "rest_framework",
    "rest_framework.authtoken",
    "widget_tweaks",
    "crispy_forms",
    "crispy_bootstrap4",
    # for API doc
    "drf_spectacular",
    # required for Django collectstatic discovery
    "drf_spectacular_sidecar",
    "django_rq",
    "django_altcha",
)


MIDDLEWARE = (
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "vulnerabilities.middleware.ban_user_agent.BanUserAgent",
    "vulnerabilities.middleware.timezone.UserTimezoneMiddleware",
)

ROOT_URLCONF = "vulnerablecode.urls"

WSGI_APPLICATION = "vulnerablecode.wsgi.application"

# Database

DATABASES = {
    "default": {
        "ENGINE": env.str("VULNERABLECODE_DB_ENGINE", "django.db.backends.postgresql"),
        "HOST": env.str("VULNERABLECODE_DB_HOST", "localhost"),
        "NAME": env.str("VULNERABLECODE_DB_NAME", "vulnerablecode"),
        "USER": env.str("VULNERABLECODE_DB_USER", "vulnerablecode"),
        "PASSWORD": env.str("VULNERABLECODE_DB_PASSWORD", "vulnerablecode"),
        "PORT": env.str("VULNERABLECODE_DB_PORT", "5432"),
        "ATOMIC_REQUESTS": True,
    }
}

DEFAULT_AUTO_FIELD = "django.db.models.AutoField"

# Templates

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [str(PROJECT_DIR.joinpath("templates"))],
        "APP_DIRS": True,
        "OPTIONS": {
            "debug": DEBUG,
            "context_processors": [
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "django.template.context_processors.request",
                "django.template.context_processors.static",
                "vulnerablecode.context_processors.versions",
            ],
        },
    },
]

# Passwords

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
        "OPTIONS": {
            "min_length": VULNERABLECODE_PASSWORD_MIN_LENGTH,
        },
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]

# Internationalization

LANGUAGE_CODE = "en-us"

TIME_ZONE = env.str("TIME_ZONE", default="UTC")

USE_I18N = True

IS_TESTS = False

if len(sys.argv) > 0:
    IS_TESTS = "pytest" in sys.argv[0]

VULNERABLECODEIO_REQUIRE_AUTHENTICATION = env.bool(
    "VULNERABLECODEIO_REQUIRE_AUTHENTICATION", default=False
)

LOGIN_REDIRECT_URL = "/"
LOGOUT_REDIRECT_URL = "/"

THROTTLE_RATE_ANON = env.str("THROTTLE_RATE_ANON", default="3600/hour")
THROTTLE_RATE_USER_HIGH = env.str("THROTTLE_RATE_USER_HIGH", default="18000/hour")
THROTTLE_RATE_USER_MEDIUM = env.str("THROTTLE_RATE_USER_MEDIUM", default="14400/hour")
THROTTLE_RATE_USER_LOW = env.str("THROTTLE_RATE_USER_LOW", default="10800/hour")

REST_FRAMEWORK_DEFAULT_THROTTLE_RATES = {
    "anon": THROTTLE_RATE_ANON,
    "low": THROTTLE_RATE_USER_LOW,
    "medium": THROTTLE_RATE_USER_MEDIUM,
    "high": THROTTLE_RATE_USER_HIGH,
}


if IS_TESTS:
    VULNERABLECODEIO_REQUIRE_AUTHENTICATION = False

USE_L10N = True

USE_TZ = True

# Static files (CSS, JavaScript, Images)

STATIC_URL = "/static/"
# STATIC_ROOT = "/var/vulnerablecode/static/"
STATIC_ROOT = env.str("VULNERABLECODE_STATIC_ROOT", "./")

STATICFILES_DIRS = [
    str(PROJECT_DIR / "static"),
]

CRISPY_ALLOWED_TEMPLATE_PACKS = "bootstrap4"

CRISPY_TEMPLATE_PACK = "bootstrap4"

# Third-party apps

# Django restframework

REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": (
        "rest_framework.authentication.SessionAuthentication",
        "rest_framework.authentication.TokenAuthentication",
    ),
    "DEFAULT_PERMISSION_CLASSES": ("rest_framework.permissions.IsAuthenticated",),
    "DEFAULT_RENDERER_CLASSES": (
        "rest_framework.renderers.JSONRenderer",
        "rest_framework.renderers.BrowsableAPIRenderer",
        "rest_framework.renderers.AdminRenderer",
    ),
    "DEFAULT_FILTER_BACKENDS": (
        "django_filters.rest_framework.DjangoFilterBackend",
        "rest_framework.filters.SearchFilter",
    ),
    "DEFAULT_THROTTLE_CLASSES": [
        "vulnerabilities.throttling.PermissionBasedUserRateThrottle",
    ],
    "DEFAULT_THROTTLE_RATES": REST_FRAMEWORK_DEFAULT_THROTTLE_RATES,
    "EXCEPTION_HANDLER": "vulnerabilities.throttling.throttled_exception_handler",
    "DEFAULT_PAGINATION_CLASS": "vulnerabilities.pagination.SmallResultSetPagination",
    # Limit the load on the Database returning a small number of records by default. https://github.com/nexB/vulnerablecode/issues/819
    "PAGE_SIZE": 10,
    # for API docs
    "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",
    "DATETIME_FORMAT": "%Y-%m-%dT%H:%M:%SZ",
}

api_doc_intro = """
<div>
    <p><strong>VulnerableCode</strong> is open data and free software by
    <a href="https://github.com/nexB/vulnerablecode"> nexB Inc. and others.</a>
    </p>
    <p>The VulnerableCode API exposes these endpoints:</p>
    <ul>
        <li>
            <strong>packages/</strong>: main endpoint to lookup for vulnerable packages.
        </li>
        <li>
            <strong>vulnerabilities/</strong>: secondary endpoint to lookup by vulnerabilities.
        </li>
        <li>
            <strong>alias/</strong>: secondary endpoint to lookup vulnerabilities by aliases (e.g., CVE)
        </li>
        <li>
            <strong>cpes/</strong>: secondary endpoint to lookup vulnerabilities by CPE.
        </li>
    </ul>
</div>
"""

# for API docs
SPECTACULAR_SETTINGS = {
    "TITLE": "VulnerableCode API",
    "DESCRIPTION": api_doc_intro,
    "VERSION": VULNERABLECODE_VERSION,
    "TOS": "/tos/",
    "CONTACT": {
        "name": "nexB Inc.",
        "url": "https://public.vulnerablecode.io",
        "email": "mailto:info@nexb.com",
    },
    "LICENSE": {
        "name": "Source code: Apache-2.0 | Data: CC-BY-SA-4.0",
        "url": "https://github.com/nexb/vulnerablecode#license",
    },
    "SERVE_INCLUDE_SCHEMA": False,
    # shorthand to use the sidecar instead
    "SWAGGER_UI_DIST": "SIDECAR",
    "SWAGGER_UI_FAVICON_HREF": "/static/images/favicon.ico",
    # See https://swagger.io/docs/open-source-tools/swagger-ui/usage/configuration/
    "SWAGGER_UI_SETTINGS": {
        "deepLinking": True,
        "displayOperationId": True,
        "defaultModelsExpandDepth": 1,
        "displayRequestDuration": True,
        "docExpansion": "list",
    },
    "SORT_OPERATIONS": False,
    "TAGS_SORTER": False,
}


if not VULNERABLECODEIO_REQUIRE_AUTHENTICATION:
    REST_FRAMEWORK["DEFAULT_PERMISSION_CLASSES"] = ("rest_framework.permissions.AllowAny",)


if DEBUG_TOOLBAR:
    # Uncomment this to get pyinstrument profiles
    # PYINSTRUMENT_PROFILE_DIR = "profiles"

    INSTALLED_APPS += ("debug_toolbar",)

    MIDDLEWARE += (
        "debug_toolbar.middleware.DebugToolbarMiddleware",
        "pyinstrument.middleware.ProfilerMiddleware",
    )

    DEBUG_TOOLBAR_PANELS = (
        "debug_toolbar.panels.history.HistoryPanel",
        "debug_toolbar.panels.versions.VersionsPanel",
        "debug_toolbar.panels.timer.TimerPanel",
        "debug_toolbar.panels.settings.SettingsPanel",
        "debug_toolbar.panels.headers.HeadersPanel",
        "debug_toolbar.panels.request.RequestPanel",
        "debug_toolbar.panels.sql.SQLPanel",
        "debug_toolbar.panels.staticfiles.StaticFilesPanel",
        "debug_toolbar.panels.templates.TemplatesPanel",
        "debug_toolbar.panels.cache.CachePanel",
        "debug_toolbar.panels.signals.SignalsPanel",
        "debug_toolbar.panels.logging.LoggingPanel",
        "debug_toolbar.panels.redirects.RedirectsPanel",
        "debug_toolbar.panels.profiling.ProfilingPanel",
    )

    INTERNAL_IPS = [
        "127.0.0.1",
    ]


LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "simple": {
            "format": "{levelname} {message}",
            "style": "{",
        },
    },
    "handlers": {
        "null": {
            "class": "logging.NullHandler",
        },
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "simple",
        },
    },
    "loggers": {
        "vulnerabilities.pipelines": {
            "handlers": ["console"],
            "level": VULNERABLECODE_LOG_LEVEL,
            "propagate": False,
        },
    },
}

if DEBUG:
    LOGGING["django"] = {
        "handlers": ["console"],
        "level": "ERROR",
    }


VULNERABLECODE_PIPELINE_TIMEOUT = env.int("VULNERABLECODE_PIPELINE_TIMEOUT", default=24)
RQ_QUEUES = {
    "default": {
        "HOST": env.str("VULNERABLECODE_REDIS_HOST", default="localhost"),
        "PORT": env.str("VULNERABLECODE_REDIS_PORT", default="6379"),
        "PASSWORD": env.str("VULNERABLECODE_REDIS_PASSWORD", default=""),
        "DEFAULT_TIMEOUT": env.int("VULNERABLECODE_REDIS_DEFAULT_TIMEOUT", default=3600),
    }
}
