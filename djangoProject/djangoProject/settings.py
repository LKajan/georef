"""
Django settings for georef project.

For more information on this file, see
https://docs.djangoproject.com/en/1.6/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.6/ref/settings/
"""

import mimetypes

mimetypes.add_type("image/svg+xml", ".svg", True)
mimetypes.add_type("image/svg+xml", ".svgz", True)

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import os
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.6/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '!)z=&5x$riu)-=%q)3$6i3^hs_re4x+zsw*l&3ph*_=bq!23%a'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

TEMPLATE_DEBUG = True

ALLOWED_HOSTS = []

# Application definition

INSTALLED_APPS = (
    'bootstrap3',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.gis',
    'sorl.thumbnail',
    'taggit',
    'georef',
    'djgeojson'
)

LEAFLET_CONFIG = {
    'PLUGINS': {
        'draw': {
            'css': "leaflet/draw/leaflet.draw.css",
            'js': "leaflet/draw/leaflet.draw.js",
        },
    }
}


MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
)

ROOT_URLCONF = 'djangoProject.urls'

WSGI_APPLICATION = 'djangoProject.wsgi.application'


# Database
# https://docs.djangoproject.com/en/1.6/ref/settings/#databases

import dj_database_url
DATABASES = {'default': dj_database_url.config()}
POSTGIS_VERSION = (2, 1, 1)

# Internationalization
# https://docs.djangoproject.com/en/1.6/topics/i18n/

LANGUAGE_CODE = 'fi-fi'
LOCALE_CODE = 'fi_FI'

TIME_ZONE = 'Europe/Helsinki'

USE_I18N = True

USE_L10N = True

USE_TZ = False

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.6/howto/static-files/

STATIC_URL = '/static/'
STATICFILES_DIRS = (
    os.path.join(BASE_DIR, 'static'),
)

MEDIA_ROOT = "C:/georef/media/"
MEDIA_URL = '/media/'


ALKUPERAISET = u'C:/georef/alkuperaiset'
TAUSTA_MOSAIC = u'C:/georef/tausta_mosaic'
GEOSERVER = {'host': "http://localhost:8080/geoserver",
      'user': 'admin',
      'password': 'geoserver',
      'workspace': 'georef'}
