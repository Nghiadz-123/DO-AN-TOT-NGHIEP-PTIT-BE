import tempfile
from pathlib import Path

from .base import *  # noqa: F401,F403
from .base import REST_FRAMEWORK

# Test chạy trên PostgreSQL theo các biến DB_* trong .env: Django tự tạo database riêng `test_<DB_NAME>`
# rồi xóa sau khi chạy xong, không đụng tới dữ liệu thật. User DB cần quyền CREATEDB.

PASSWORD_HASHERS = ['django.contrib.auth.hashers.MD5PasswordHasher']

_tmp = Path(tempfile.mkdtemp(prefix='ats-test-'))
MEDIA_ROOT = _tmp / 'media'
PRIVATE_MEDIA_ROOT = _tmp / 'private_media'

REST_FRAMEWORK['DEFAULT_THROTTLE_RATES'] = {key: None for key in REST_FRAMEWORK['DEFAULT_THROTTLE_RATES']}
EMPLOYER_REQUIRE_VERIFIED_COMPANY = False
CANDIDATE_MAX_CVS = 10
# Test không bao giờ gọi Gemini thật (kể cả khi .env có key): test AI thay LLM bằng provider giả
GEMINI_API_KEY = ''
