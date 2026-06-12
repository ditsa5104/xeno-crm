import os
from pathlib import Path
import environ
from kombu import Queue

BASE_DIR = Path(__file__).resolve().parent.parent.parent

env = environ.Env(
    DEBUG=(bool, False),
)
# Only read .env file if it exists (local dev). On Render, env vars are injected directly.
_env_file = os.path.join(BASE_DIR.parent, '.env')
if os.path.exists(_env_file):
    environ.Env.read_env(_env_file)

SECRET_KEY = env('SECRET_KEY', default='dev-insecure-secret-change-me')
DEBUG = env.bool('DEBUG', default=False)
ALLOWED_HOSTS = env.list('ALLOWED_HOSTS', default=['localhost', '127.0.0.1', '0.0.0.0'])

INSTALLED_APPS = [
    'daphne',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'rest_framework.authtoken',
    'channels',
    'corsheaders',
    'drf_spectacular',
    'django_celery_beat',
    'django_celery_results',
    'apps.core',
    'apps.auth_app',
    'apps.customers',
    'apps.segments',
    'apps.campaigns',
    'apps.analytics',
    'apps.copilot',
    'apps.webhooks',
]

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'config.urls'
WSGI_APPLICATION = 'config.wsgi.application'
ASGI_APPLICATION = 'config.asgi.application'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

DATABASES = {'default': env.db('DATABASE_URL', default='postgresql://xeno:xeno@db:5432/xeno_crm')}

REDIS_URL = env('REDIS_URL', default='redis://redis:6379/0')

CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels_redis.core.RedisChannelLayer",
        "CONFIG": {"hosts": [REDIS_URL]},
    }
}

CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": REDIS_URL,
    }
}

CELERY_BROKER_URL = REDIS_URL
CELERY_RESULT_BACKEND = REDIS_URL
CELERY_TASK_DEFAULT_QUEUE = 'default'
CELERY_TASK_QUEUES = (
    Queue('default'),
    Queue('campaigns'),
    Queue('scoring'),
)
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TIMEZONE = 'UTC'

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework.authentication.TokenAuthentication',
        'rest_framework.authentication.SessionAuthentication',
    ),
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAuthenticatedOrReadOnly',
    ),
    'DEFAULT_PAGINATION_CLASS': 'apps.core.pagination.CrmPageNumberPagination',
    'PAGE_SIZE': 25,
    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',
}

SPECTACULAR_SETTINGS = {
    'TITLE': 'Xeno CRM API',
    'DESCRIPTION': (
        'AI-native Mini CRM — REST API for customers, segments, campaigns, '
        'analytics, copilot, and webhook ingestion.\n\n'
        'Authenticate via `POST /api/v1/auth/login/` to receive a token, then send '
        '`Authorization: Token <key>` on protected endpoints.'
    ),
    'VERSION': '1.0.0',
    'SERVE_INCLUDE_SCHEMA': False,
    'COMPONENT_SPLIT_REQUEST': True,
    'SCHEMA_PATH_PREFIX': r'/api/v1',
    'TAGS': [
        {'name': 'auth', 'description': 'Register, login, logout, current user.'},
        {'name': 'customers', 'description': 'Customer profiles, orders, timelines, CSV import/export.'},
        {'name': 'segments', 'description': 'Filter-DSL segments and AI segment builder.'},
        {'name': 'campaigns', 'description': 'Campaigns, dispatch, A/B, preflight, analytics.'},
        {'name': 'campaign-templates', 'description': 'Reusable message templates.'},
        {'name': 'analytics', 'description': 'Dashboard, cohort, channel performance.'},
        {'name': 'copilot', 'description': 'AI copilot chat and agent endpoints.'},
        {'name': 'webhooks', 'description': 'Channel-event ingestion (HMAC-signed).'},
    ],
    'SWAGGER_UI_SETTINGS': {
        'persistAuthorization': True,
        'displayRequestDuration': True,
        'docExpansion': 'list',
        'filter': True,
    },
    # If API_SERVER_URL is set (e.g. the Render URL), advertise it explicitly.
    # Otherwise leave SERVERS empty so drf-spectacular infers the server from
    # the request origin — correct for both local dev and production.
    'SERVERS': (
        [{'url': env('API_SERVER_URL'), 'description': 'API server'}]
        if env('API_SERVER_URL', default='')
        else []
    ),
}

CORS_ALLOWED_ORIGINS = env.list('CORS_ALLOWED_ORIGINS', default=['http://localhost:5173'])
CORS_ALLOW_CREDENTIALS = True

AUTH_PASSWORD_VALIDATORS = []

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

STATIC_URL = 'static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# AI / OpenRouter
OPENROUTER_API_KEY = env('OPENROUTER_API_KEY', default='')
OPENROUTER_MODEL = env('OPENROUTER_MODEL', default='anthropic/claude-sonnet-4-5')
SITE_URL = env('SITE_URL', default='http://localhost:8000')

# Channel stub
CHANNEL_STUB_URL = env('CHANNEL_STUB_URL', default='http://channel_stub:8001')
CHANNEL_STUB_SECRET = env('CHANNEL_STUB_SECRET', default='dev-stub-secret')
# URL the channel stub calls back to. Must be reachable from the stub container,
# so it differs from SITE_URL (which may be localhost for browser-facing links).
CRM_WEBHOOK_URL = env(
    'CRM_WEBHOOK_URL',
    default='http://crm:8000/api/v1/webhooks/channel-event/',
)
