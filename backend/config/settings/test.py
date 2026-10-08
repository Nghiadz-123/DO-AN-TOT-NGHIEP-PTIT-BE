import tempfile
from pathlib import Path

from .base import *  # noqa: F401,F403
from .base import REST_FRAMEWORK, env

# Mặc định test chạy trên SQLite in-memory cho nhanh.
# Chạy trên PostgreSQL: đặt TEST_DB_ENGINE=postgresql (dùng các biến DB_* trong .env).
if env('TEST_DB_ENGINE', default='sqlite') == 'sqlite':
    DATABASES = {'default': {'ENGINE': 'django.db.backends.sqlite3', 'NAME': ':memory:'}}

PASSWORD_HASHERS = ['django.contrib.auth.hashers.MD5PasswordHasher']

_tmp = Path(tempfile.mkdtemp(prefix='ats-test-'))
MEDIA_ROOT = _tmp / 'media'
PRIVATE_MEDIA_ROOT = _tmp / 'private_media'

REST_FRAMEWORK['DEFAULT_THROTTLE_RATES'] = {'auth': None}
EMPLOYER_REQUIRE_VERIFIED_COMPANY = False
