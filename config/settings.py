import os
from pathlib import Path
import dj_database_url
from dotenv import load_dotenv
from django.core.exceptions import ImproperlyConfigured

BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / '.env')
def env_bool(name, default=False):
    return os.getenv(name, str(default)).lower() in ('1', 'true', 'yes')
def env_list(name, default=''):
    return [value.strip() for value in os.getenv(name, default).split(',') if value.strip()]
DEBUG = env_bool('DEBUG', True)
SECRET_KEY = os.getenv('SECRET_KEY', 'development-only-change-before-deploying')
if not DEBUG and (len(SECRET_KEY) < 50 or SECRET_KEY.startswith('development-')):
    raise ImproperlyConfigured('Set a unique SECRET_KEY of at least 50 characters for production.')
ALLOWED_HOSTS = env_list('ALLOWED_HOSTS', 'localhost,127.0.0.1,[::1]')
CSRF_TRUSTED_ORIGINS = env_list('CSRF_TRUSTED_ORIGINS')
INSTALLED_APPS = ['django.contrib.admin','django.contrib.auth','django.contrib.contenttypes',
    'django.contrib.sessions','django.contrib.messages','django.contrib.staticfiles','storages','portfolio']
MIDDLEWARE = ['django.middleware.security.SecurityMiddleware','whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware','django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware','django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware','django.middleware.clickjacking.XFrameOptionsMiddleware']
ROOT_URLCONF = 'config.urls'
TEMPLATES = [{'BACKEND':'django.template.backends.django.DjangoTemplates','DIRS':[BASE_DIR/'templates'],
    'APP_DIRS':True,'OPTIONS':{'context_processors':['django.template.context_processors.request',
    'django.contrib.auth.context_processors.auth','django.contrib.messages.context_processors.messages',
    'portfolio.context_processors.site_profile']}}]
WSGI_APPLICATION = 'config.wsgi.application'
DATABASE_URL = os.getenv('DATABASE_URL')
if not DEBUG and not DATABASE_URL:
    raise ImproperlyConfigured('DATABASE_URL is required in production.')
DATABASES = {'default': dj_database_url.parse(DATABASE_URL, conn_max_age=0,
    ssl_require=not DEBUG) if DATABASE_URL else {'ENGINE':'django.db.backends.sqlite3','NAME':BASE_DIR/'db.sqlite3'}}
# Supabase session pooler (5432) supports persistent sessions. conn_max_age=0 also works with transaction pooling.
if DATABASES['default']['ENGINE'].endswith('postgresql'):
    DATABASES['default']['DISABLE_SERVER_SIDE_CURSORS'] = True
AUTH_PASSWORD_VALIDATORS = [
    {'NAME':'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME':'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME':'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME':'django.contrib.auth.password_validation.NumericPasswordValidator'}]
LANGUAGE_CODE = 'en-us'
TIME_ZONE = os.getenv('TIME_ZONE', 'UTC')
USE_I18N = True
USE_TZ = True
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR/'staticfiles'
STATICFILES_DIRS = [BASE_DIR/'static']
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR/'media'
STORAGES = {'default':{'BACKEND':'django.core.files.storage.FileSystemStorage'},
    'staticfiles':{'BACKEND':'whitenoise.storage.CompressedManifestStaticFilesStorage'}}
if env_bool('USE_SUPABASE_STORAGE'):
    required = ['SUPABASE_S3_ENDPOINT_URL','SUPABASE_S3_ACCESS_KEY_ID','SUPABASE_S3_SECRET_ACCESS_KEY','SUPABASE_STORAGE_BUCKET']
    if any(not os.getenv(key) for key in required):
        raise ImproperlyConfigured('Supabase S3 endpoint, access key, secret and bucket are required.')
    STORAGES['default'] = {'BACKEND':'storages.backends.s3.S3Storage','OPTIONS':{
        'endpoint_url':os.environ['SUPABASE_S3_ENDPOINT_URL'],
        'access_key':os.environ['SUPABASE_S3_ACCESS_KEY_ID'],
        'secret_key':os.environ['SUPABASE_S3_SECRET_ACCESS_KEY'],
        'bucket_name':os.environ['SUPABASE_STORAGE_BUCKET'],
        'region_name':os.getenv('SUPABASE_S3_REGION_NAME','us-east-1'),
        'signature_version':'s3v4','addressing_style':'path',
        'default_acl':None,'file_overwrite':False,'querystring_auth':True,
        'object_parameters':{'CacheControl':'max-age=86400'}}}
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
SESSION_COOKIE_SECURE = not DEBUG
CSRF_COOKIE_SECURE = not DEBUG
SECURE_SSL_REDIRECT = env_bool('SECURE_SSL_REDIRECT', not DEBUG)
SECURE_HSTS_SECONDS = 31536000 if not DEBUG else 0
SECURE_HSTS_INCLUDE_SUBDOMAINS = not DEBUG
SECURE_HSTS_PRELOAD = not DEBUG
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'
# Enable only behind a trusted proxy that strips user-supplied X-Forwarded-Proto.
if env_bool('TRUST_PROXY_HEADERS'):
    SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO','https')
DATA_UPLOAD_MAX_MEMORY_SIZE = 64 * 1024
FILE_UPLOAD_MAX_MEMORY_SIZE = 5 * 1024 * 1024
CONTACT_RATE_LIMIT = int(os.getenv('CONTACT_RATE_LIMIT','5'))
CSRF_FAILURE_VIEW = 'portfolio.views.csrf_failure'
