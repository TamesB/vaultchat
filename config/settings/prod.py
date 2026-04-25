from .base import *  # noqa

DEBUG = False

# In production you MUST set ALLOWED_HOSTS.
if not ALLOWED_HOSTS:
    raise RuntimeError("ALLOWED_HOSTS is required in production")

INSTALLED_APPS += ["storages"]

SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SESSION_COOKIE_HTTPONLY = True
CSRF_COOKIE_HTTPONLY = False
SESSION_COOKIE_SAMESITE = "Lax"
CSRF_COOKIE_SAMESITE = "Lax"

# Allow healthcheck endpoint to work over HTTP
SECURE_SSL_REDIRECT = not os.environ.get('RAILWAY_ENVIRONMENT_NAME')
# OR more explicitly:
if os.environ.get('RAILWAY_ENVIRONMENT_NAME'):
    SECURE_SSL_REDIRECT = False
else:
    SECURE_SSL_REDIRECT = True if SECURE_SSL_REDIRECT is None else SECURE_SSL_REDIRECT


SECURE_HSTS_SECONDS = int(env("SECURE_HSTS_SECONDS", default="2592000"))  # 30 days
SECURE_HSTS_INCLUDE_SUBDOMAINS = env.bool("SECURE_HSTS_INCLUDE_SUBDOMAINS", default=True)
SECURE_HSTS_PRELOAD = env.bool("SECURE_HSTS_PRELOAD", default=True)
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_REFERRER_POLICY = "same-origin"

# Admin hardening
SECURE_CROSS_ORIGIN_OPENER_POLICY = "same-origin"

# S3-compatible storage (Railway Bucket)
AWS_ACCESS_KEY_ID = env("AWS_ACCESS_KEY_ID", default="")
AWS_SECRET_ACCESS_KEY = env("AWS_SECRET_ACCESS_KEY", default="")
AWS_STORAGE_BUCKET_NAME = env("AWS_STORAGE_BUCKET_NAME", default="")
AWS_S3_ENDPOINT_URL = env("AWS_S3_ENDPOINT_URL", default="")
AWS_S3_REGION_NAME = env("AWS_S3_REGION_NAME", default="")
AWS_S3_SIGNATURE_VERSION = env("AWS_S3_SIGNATURE_VERSION", default="s3v4")
AWS_S3_ADDRESSING_STYLE = env("AWS_S3_ADDRESSING_STYLE", default="path")
AWS_S3_CUSTOM_DOMAIN = env("AWS_S3_CUSTOM_DOMAIN", default="")

AWS_DEFAULT_ACL = None
AWS_S3_OBJECT_PARAMETERS = {"CacheControl": "max-age=31536000, immutable"}

# Static: public-read, no query strings (cacheable)
# Media: private, presigned only
STORAGES = {
    "staticfiles": {"BACKEND": "config.storage_backends.StaticStorage"},
    "default": {"BACKEND": "config.storage_backends.PrivateMediaStorage"},
}

if AWS_S3_CUSTOM_DOMAIN:
    STATIC_URL = f"https://{AWS_S3_CUSTOM_DOMAIN}/static/"
    MEDIA_URL = f"https://{AWS_S3_CUSTOM_DOMAIN}/media/"
else:
    # Many S3-compatible providers support virtual-hosted style; if not, you can still keep MEDIA_URL unused
    # since we serve media via presigned download endpoint.
    STATIC_URL = f"{AWS_S3_ENDPOINT_URL.rstrip('/')}/{AWS_STORAGE_BUCKET_NAME}/static/"
    MEDIA_URL = f"{AWS_S3_ENDPOINT_URL.rstrip('/')}/{AWS_STORAGE_BUCKET_NAME}/media/"

