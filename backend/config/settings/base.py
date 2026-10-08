"""Cấu hình chung cho mọi môi trường. Biến môi trường đọc từ backend/.env (xem .env.example)."""
from datetime import timedelta
from pathlib import Path

import environ

BASE_DIR = Path(__file__).resolve().parent.parent.parent  # thư mục backend/

env = environ.Env()
if (BASE_DIR / '.env').exists():
    environ.Env.read_env(BASE_DIR / '.env')

SECRET_KEY = env('DJANGO_SECRET_KEY', default='django-insecure-dev-only-change-me')
DEBUG = env.bool('DJANGO_DEBUG', default=False)
ALLOWED_HOSTS = env.list('DJANGO_ALLOWED_HOSTS', default=['localhost', '127.0.0.1'])

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    # Third-party
    'rest_framework',
    'rest_framework_simplejwt.token_blacklist',
    'django_filters',
    'corsheaders',
    'drf_spectacular',
    # Module nghiệp vụ (theo thứ tự phụ thuộc). Giai đoạn AI sẽ thêm 'apps.ai'.
    'apps.accounts',
    'apps.catalog',
    'apps.employers',
    'apps.candidates',
    'apps.cvs',
    'apps.jobs',
    'apps.applications',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'config.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'config.wsgi.application'
ASGI_APPLICATION = 'config.asgi.application'

# --- Database: PostgreSQL là mặc định; DB_ENGINE=sqlite để chạy nhanh khi chưa cài PostgreSQL ---
DB_ENGINE = env('DB_ENGINE', default='postgresql')
if DB_ENGINE == 'sqlite':
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / env('DB_NAME', default='db.sqlite3'),
        }
    }
else:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': env('DB_NAME', default='ats_db'),
            'USER': env('DB_USER', default='postgres'),
            'PASSWORD': env('DB_PASSWORD', default=''),
            'HOST': env('DB_HOST', default='localhost'),
            'PORT': env('DB_PORT', default='5432'),
            'CONN_MAX_AGE': 60,
        }
    }

AUTH_USER_MODEL = 'accounts.User'

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

LANGUAGE_CODE = 'vi'
TIME_ZONE = 'Asia/Ho_Chi_Minh'
USE_I18N = True
USE_TZ = True

STATIC_URL = 'static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'

# File công khai (logo công ty) phục vụ qua MEDIA_URL
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'
# File riêng tư (CV): không có URL công khai, chỉ tải qua API có kiểm tra quyền
PRIVATE_MEDIA_ROOT = BASE_DIR / 'private_media'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# --- Django REST Framework ---
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': ('rest_framework_simplejwt.authentication.JWTAuthentication',),
    'DEFAULT_PERMISSION_CLASSES': ('rest_framework.permissions.IsAuthenticated',),
    'DEFAULT_PAGINATION_CLASS': 'common.pagination.StandardPagination',
    'PAGE_SIZE': 20,
    'DEFAULT_FILTER_BACKENDS': (
        'django_filters.rest_framework.DjangoFilterBackend',
        'rest_framework.filters.OrderingFilter',
    ),
    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',
    'EXCEPTION_HANDLER': 'common.exceptions.custom_exception_handler',
    'DEFAULT_THROTTLE_RATES': {'auth': '20/min', 'cv_upload': '30/hour'},
    'COERCE_DECIMAL_TO_STRING': False,
}

SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=env.int('JWT_ACCESS_MINUTES', default=30)),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=env.int('JWT_REFRESH_DAYS', default=7)),
    'ROTATE_REFRESH_TOKENS': True,
    'BLACKLIST_AFTER_ROTATION': True,
    'UPDATE_LAST_LOGIN': True,
    'AUTH_HEADER_TYPES': ('Bearer',),
}

CORS_ALLOWED_ORIGINS = env.list(
    'CORS_ALLOWED_ORIGINS', default=['http://localhost:3000', 'http://127.0.0.1:3000']
)
# Cho frontend đọc được tên file khi tải CV
CORS_EXPOSE_HEADERS = ['Content-Disposition']

SPECTACULAR_SETTINGS = {
    'TITLE': 'Smart ATS API',
    'DESCRIPTION': 'API nền tảng tuyển dụng (ATS). Giai đoạn 1: chức năng dành cho Nhà tuyển dụng. '
    'Giai đoạn 2: chức năng dành cho Ứng viên (hồ sơ, tải lên CV, ứng tuyển).',
    'VERSION': '1.0.0',
    'SERVE_INCLUDE_SCHEMA': False,
    'COMPONENT_SPLIT_REQUEST': True,
    'SCHEMA_PATH_PREFIX': r'/api/v1',
    'ENUM_NAME_OVERRIDES': {
        'JobStatusEnum': 'apps.jobs.models.JobStatus',
        'JobInitialStatusEnum': ['draft', 'published'],
        'JobLevelEnum': 'apps.catalog.choices.JobLevel',
        'JobTypeEnum': 'apps.catalog.choices.JobType',
        'WorkModeEnum': 'apps.catalog.choices.WorkMode',
        'ApplicationStatusEnum': 'apps.applications.models.ApplicationStatus',
        'ApplicationTargetStatusEnum': ['screening', 'interview', 'offer', 'hired', 'rejected'],
        'RecruiterStatusEnum': 'apps.employers.models.RecruiterStatus',
        'CVParseStatusEnum': 'apps.cvs.models.CVParseStatus',
    },
}

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {'console': {'class': 'logging.StreamHandler'}},
    'root': {'handlers': ['console'], 'level': 'INFO'},
}

# --- Nghiệp vụ ---
# True: công ty phải được admin xác minh mới được đăng tin (đúng thiết kế DB); False tiện cho dev/demo
EMPLOYER_REQUIRE_VERIFIED_COMPANY = env.bool('EMPLOYER_REQUIRE_VERIFIED_COMPANY', default=False)
COMPANY_LOGO_MAX_SIZE = 2 * 1024 * 1024
# CV ứng viên: PDF/DOCX tối đa 5 MB (UC-03); số CV tối đa một ứng viên được lưu (không tính CV đã xóa)
CV_MAX_SIZE = 5 * 1024 * 1024
CANDIDATE_MAX_CVS = env.int('CANDIDATE_MAX_CVS', default=10)
