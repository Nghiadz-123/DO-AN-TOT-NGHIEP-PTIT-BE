from decouple import config

SECRET_KEY = config('SECRET_KEY')
DEBUG = config('DEBUG', default=False, cast=bool)
ALLOWED_HOSTS = config('ALLOWED_HOSTS', default='localhost,127.0.0.1').split(',')

DJANGO_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
]

THIRD_PARTY_APPS = [
    'rest_framework',
    'rest_framework_simplejwt',
    'corsheaders',
]

LOCAL_APPS = [
    'apps.accounts',
]

INSTALLED_APPS = DJANGO_APPS + THIRD_PARTY_APPS + LOCAL_APPS

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

WSGI_APPLICATION = 'config.wsgi.application'

AUTH_USER_MODEL = 'accounts.User'

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator', 'OPTIONS': {'min_length': 6}},
]

LANGUAGE_CODE = 'vi'
TIME_ZONE = 'Asia/Ho_Chi_Minh'
USE_I18N = True
USE_TZ = True

STATIC_URL = '/static/'
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ),
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAuthenticated',
    ),
    'DEFAULT_RENDERER_CLASSES': (
        'rest_framework.renderers.JSONRenderer',
    ),
    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',
    'EXCEPTION_HANDLER': 'common.exceptions.custom_exception_handler',
    'DEFAULT_THROTTLE_RATES': {'auth': '20/min', 'cv_upload': '30/hour'},
    'COERCE_DECIMAL_TO_STRING': False,
}

from datetime import timedelta

SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(days=7),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=30),
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
