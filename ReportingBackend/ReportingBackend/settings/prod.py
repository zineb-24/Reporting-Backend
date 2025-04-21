from .common import *
import dj_database_url

SECRET_KEY = os.getenv('SECRET_KEY')

DEBUG = False

ALLOWED_HOSTS = [os.getenv('DJANGO_ALLOWED_HOSTS')]

CORS_ALLOWED_ORIGINS = os.getenv('CORS_ALLOWED_ORIGINS').split(',')

CSRF_TRUSTED_ORIGINS = [os.getenv('CSRF_TRUSTED_ORIGINS')]

DATABASES = {
     'default': dj_database_url.config(
         default=os.environ.get('DATABASE_URL')
     )
 }