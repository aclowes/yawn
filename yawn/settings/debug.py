from yawn.settings.base import *  # NOQA

SECRET_KEY = 'example secret key, change me'
DEBUG = True

# disable SSL settings
CSRF_COOKIE_SECURE = False
SECURE_PROXY_SSL_HEADER = None
SECURE_SSL_REDIRECT = False
