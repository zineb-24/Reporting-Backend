from .common import *

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-r-f&e)m318n9@3#prl$j8^5$(pws5fpod4q&1ft%0^py60bsu@'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = []

CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",
]

# Database
# https://docs.djangoproject.com/en/5.1/ref/settings/#databases

# Use SQLite for local development
DATABASES = {
    'default': {
        'ENGINE': os.getenv('DB_ENGINE_DEV'),
        'NAME': os.getenv('DB_NAME_DEV'),
        'USER': os.getenv('DB_USER_DEV'),  
        'PASSWORD': os.getenv('DB_PASSWORD_DEV'),  
        'HOST': os.getenv('DB_HOST_DEV'),  
        'PORT': os.getenv('DB_PORT_DEV'),  
        'OPTIONS': {
            'init_command': "SET sql_mode='STRICT_TRANS_TABLES'"
        }
    }
}