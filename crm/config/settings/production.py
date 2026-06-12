from .base import *  # noqa

DEBUG = False
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True

# Hosts and CSRF origins must be provided via environment in production.
ALLOWED_HOSTS = env.list('ALLOWED_HOSTS', default=[])  # noqa: F405
CSRF_TRUSTED_ORIGINS = env.list('CSRF_TRUSTED_ORIGINS', default=[])  # noqa: F405

# Refuse to boot with the insecure development secret key.
if SECRET_KEY == 'dev-insecure-secret-change-me':  # noqa: F405
    raise RuntimeError(
        'SECRET_KEY must be set to a secure value in production '
        '(the development default is not allowed).'
    )

# Additional HTTPS hardening.
SECURE_SSL_REDIRECT = env.bool('SECURE_SSL_REDIRECT', default=True)  # noqa: F405
SECURE_HSTS_SECONDS = env.int('SECURE_HSTS_SECONDS', default=31536000)  # noqa: F405
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
