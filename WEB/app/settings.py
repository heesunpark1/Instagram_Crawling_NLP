import os
import json
import csv
import re

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.11/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'u#e1w0_hx^0k%%#^gms)jba^4faz38ax=)*sa(!a__%k4b)ou0'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['*']


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'app.apps.AppConfig',
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

ROOT_URLCONF = 'app.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': ['app/templates'],
        # 'APP_DIRS': True,
        'OPTIONS': {
            'debug': True,
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
            'loaders': ['django.template.loaders.filesystem.Loader','django.template.loaders.app_directories.Loader']
        },
    },
]

STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'app/static'),
]

WSGI_APPLICATION = 'app.wsgi.application'


# Database
# https://docs.djangoproject.com/en/1.11/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}


# Password validation
# https://docs.djangoproject.com/en/1.11/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/1.11/topics/i18n/

LANGUAGE_CODE = 'ko'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.11/howto/static-files/
STATIC_ROOT = 'static' 
STATIC_URL = '/static/'

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework.authentication.BasicAuthentication',
        'rest_framework.authentication.SessionAuthentication',
    ),
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAdminUser',
    ],
    'PAGE_SIZE': 10
}

APPEND_SLASH = False

GO_CRAWL_CMD = "python3"
CRAWL_PROJ_PATH = "{}/".format(BASE_DIR)

GO_CRAWL_IN_PATH = "{}gocrawl_in.py".format(CRAWL_PROJ_PATH)

# MODEL
VERSION_JSON = "versions.json"
MODEL_BASE_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),'../MODEL')
MODEL_FILENAME = "vectors.bin"

MODEL_DIR = os.path.join(MODEL_BASE_DIR, 'model')

# INPUT_DIR = os.path.join(MODEL_BASE_DIR, 'in')
# OUTPUT_DIR = os.path.join(MODEL_BASE_DIR, 'out')
#
# CSV_FILENAME = "lstm_data.{}.csv"
#
# MODEL_WEIGHT_FILENAME = "model.weight.{}.h5"
# MODEL_ARCH_FILENAME = "model.arch.{}.json"

# DATA SET
TRAIN_TEST_RATIO = 0.25
DATASET_RANTOM_STATE = 42

INSTA_DOMAIN = "http://www.instagram.com"

#### GLOBAL VARIABLES ####

