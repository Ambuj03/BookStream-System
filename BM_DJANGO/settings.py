"""
Django settings for BM_DJANGO project.

Generated by 'django-admin startproject' using Django 4.2.11.

For more information on this file, see
https://docs.djangoproject.com/en/4.2/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/4.2/ref/settings/
"""

from pathlib import Path
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.getenv('SECRET_KEY')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = os.getenv('DEBUG', 'False') == 'True'

ALLOWED_HOSTS = os.getenv('ALLOWED_HOSTS', '',).split(',')
# ALLOWED_HOSTS = ('*',)


# Application definition

INSTALLED_APPS = [
    'bm_app',
    'jazzmin',
    # 'grappelli',  
    'nested_admin',
    'rangefilter',
    'import_export',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'widget_tweaks',
]

GRAPPELLI_ADMIN_TITLE = 'Bookstore Management'

# Custom authentication backend 
AUTHENTICATION_BACKENDS = [
    'django.contrib.auth.backends.ModelBackend',  # Keep the default backend
      # Add your custom backend
]


MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'BM_DJANGO.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],  # Updated to use BASE_DIR
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

WSGI_APPLICATION = 'BM_DJANGO.wsgi.application'


# Authentication Settings
LOGIN_URL = 'login'  # Where to redirect if user isn't logged in
LOGIN_REDIRECT_URL = 'home'  # Where to redirect after successful login
LOGOUT_REDIRECT_URL = 'main'  # Where to redirect after logout



# Database
# https://docs.djangoproject.com/en/4.2/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': os.getenv('DB_NAME'),
        'USER': os.getenv('DB_USER'),
        'PASSWORD': os.getenv('DB_PASSWORD'),
        'HOST': os.getenv('DB_HOST'),
        'PORT': os.getenv('DB_PORT'),
    }
}


# Password validation
# https://docs.djangoproject.com/en/4.2/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
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

# Internationalization
# https://docs.djangoproject.com/en/4.2/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'Asia/Kolkata'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.2/howto/static-files/

STATIC_ROOT = BASE_DIR/'staticfiles'
STATIC_URL = 'static/'
STATICFILES_DIRS = [
    BASE_DIR / "bm_app/static",
]

# Default primary key field type
# https://docs.djangoproject.com/en/4.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Find your existing JAZZMIN_SETTINGS dictionary and add/modify these keys:
JAZZMIN_SETTINGS = {
    # Your existing settings...

    "site_title": "Brihad Mridanga",
    "site_header": "Brihad Mridanga",
    "welcome_sign": "Hare Krsna",
    #  "login_logo": 'jazzmin/img/logo.jpg',
    #  /home/ambuj03/Desktop/BM_DJANGO/staticfiles/jazzmin/img
    
    # Add this section
    "custom_links": {
        "bm_app": [
            {
                "name": "Notifications",
                "url": "admin_notifications",
                "icon": "fas fa-bell",
                "new_window": False,
            }
        ]
    },
}


# Celery Configuration
CELERY_BROKER_URL = 'redis://localhost:6379/0'
CELERY_RESULT_BACKEND = 'redis://localhost:6379/0'
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TIMEZONE = 'UTC'  # Use your timezone

# Django Celery Beat Settings
INSTALLED_APPS += ['django_celery_beat']

# Add this after the other Celery settings
from celery.schedules import crontab

CELERY_BEAT_SCHEDULE = {
    'cleanup-old-notifications': {
        'task': 'bm_app.tasks.cleanup_old_notifications',
        'schedule': crontab(hour=0, minute=0),  # Run at midnight every day
    },
}