import os
from celery.schedules import crontab

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '9%k&=0ab7nfl%@+2bvix_*7=ckk6n=npqe8qs5csf3^2^0oya+'
# Build paths inside the project like this: os.path.join(BASE_DIR, ...)

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'iggnpk',
        'USER': 'postgres',
        'PASSWORD': '123',
        'HOST': 'postgres',
        'PORT': '',
    }
}

EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = '192.168.7.13'
EMAIL_PORT = 25
DEFAULT_FROM_EMAIL = 'noreply@iggnpk.ru'

