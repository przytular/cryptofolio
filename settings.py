"""
Django settings for cryptofolio project.

Generated by 'django-admin startproject' using Django 1.11.5.

For more information on this file, see
https://docs.djangoproject.com/en/1.11/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.11/ref/settings/
"""

import os
import raven

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SECRET_KEY = os.environ.get('SECRET_KEY', 'secret_key')

DEBUG = True
ALLOWED_HOSTS = [
    # local testing
    '0.0.0.0',
    '127.0.0.1',
    'localhost',
    # production
    'moonfolio-dev.herokuapp.com',
    'warren-application.herokuapp.com',
    'app.getwarren.io'
]

# Application definition

STATICFILES_FINDERS = (
   'django.contrib.staticfiles.finders.FileSystemFinder',
   'django.contrib.staticfiles.finders.AppDirectoriesFinder',
   'djangobower.finders.BowerFinder',
)

INSTALLED_APPS = [
    'cryptofolio.apps.CryptofolioConfig',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django_nvd3',
    'djangobower',
    'encrypted_model_fields',
    'raven.contrib.django.raven_compat',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
]

ROOT_URLCONF = 'urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'cryptofolio/templates')],
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

WSGI_APPLICATION = 'wsgi.application'

# redirect to home after login
LOGIN_REDIRECT_URL = 'home'
LOGIN_URL = 'login'

# password reset email backend
# EMAIL_BACKEND = 'sendgrid_backend.SendgridBackend'
DEFAULT_FROM_EMAIL = 'no-reply@cryptofol.io'
SERVER_EMAIL = 'system@cryptofol.io'
# SENDGRID_API_KEY = os.environ.get('SENDGRID_API_KEY', '123')

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': os.environ['DB_NAME'],
        'USER': os.environ['DB_USER'],
        'PASSWORD': os.environ['DB_PASSWORD'],
        'HOST': os.environ['DB_HOST'],
        'PORT': os.environ['DB_PORT'],
    }
}


# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.sqlite3',
#         'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
#     }
# }



AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME':
        'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'Europe/Zagreb'
USE_I18N = True
USE_L10N = True
USE_TZ = True

STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
STATIC_URL = '/static/'

# Extra places for collectstatic to find static files.
STATICFILES_DIRS=(
    os.path.join(BASE_DIR, 'cryptofolio/static'),
)

# STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

BOWER_INSTALLED_APPS = (
    'd3#3.3.13',
    'nvd3#1.7.1',
    'popper.js#1.12.5',
    'jquery#3.2.1',
    'tether#1.4.0',
    'bootstrap#4.0.0-alpha.6',
)

ETHERSCAN_API_KEY = os.environ.get('ETHERSCAN_API_KEY', '')

BOWER_COMPONENTS_ROOT = os.path.join(BASE_DIR, 'components')
BOWER_PATH = '/usr/local/bin/bower'

FIELD_ENCRYPTION_KEY = os.environ.get('FIELD_ENCRYPTION_KEY', b'ldzsKjRTyxegFwq8PvWxmsFeWWtAv97bzJ66hfr0hl8=')

SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

try:
    git_commit_hash = raven.fetch_git_sha(os.path.abspath(BASE_DIR))
except:
    git_commit_hash = 'unknown hash'

if not DEBUG:
    SENTRY_DSN = os.environ.get('SENTRY_DSN', '')
    RAVEN_CONFIG = {
        'dsn': SENTRY_DSN,
        'release': os.environ.get(
            'HEROKU_SLUG_COMMIT',
            git_commit_hash
            ),
        }

