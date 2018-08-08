"""
Django settings for fd_supply_services project.

Generated by 'django-admin startproject' using Django 1.11.13.

For more information on this file, see
https://docs.djangoproject.com/en/1.11/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.11/ref/settings/
"""

import os
import yaml

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CONFIG_DIR = os.path.join(BASE_DIR, 'config')

# read the deployment type fron the env variables
try:
    DEPLOYMENT_TYPE = os.environ["DEPLOYMENT_TYPE"]
    print("\nDetected {0} Deployment Type\n".format(DEPLOYMENT_TYPE))

except KeyError:

    # If deployment type is not set, default to local tool settings. this
    # should make it easier to directly invoke manage.py commands.
    DEPLOYMENT_TYPE = "LOCAL-UTILS"
    print("Deployment Type not set! Defaulting to {0}!".format(DEPLOYMENT_TYPE))

# Load environment specific settings
if DEPLOYMENT_TYPE == "DEV-LOCAL":
    print("Loading {0} Settings".format(DEPLOYMENT_TYPE))
    with open(os.path.join(CONFIG_DIR, "dev-local.yaml"), 'r') as stream:
        settings = yaml.load(stream)

elif DEPLOYMENT_TYPE == "DEV-REMOTE":
    print("Loading {0} Settings".format(DEPLOYMENT_TYPE))
    with open(os.path.join(CONFIG_DIR, "dev-remote.yaml"), 'r') as stream:
        settings = yaml.load(stream)

elif (DEPLOYMENT_TYPE == "PRODUCTION" or
        DEPLOYMENT_TYPE == "TEST-PIPELINE" or
        DEPLOYMENT_TYPE == "DEV-PIPELINE"):

    print("Loading {0} Settings".format(DEPLOYMENT_TYPE))
    with open(os.path.join(CONFIG_DIR, "production.yaml"), 'r') as stream:
        settings = yaml.load(stream)

    # TODO - storing database passwords in environment variables is not safe.
    # Eventually need to move to Docker secrets / AWS secrets
    settings['database']['name'] = os.environ['DB_NAME']
    settings['database']['user'] = os.environ['DB_USER']
    settings['database']['password'] = os.environ['DB_PASSWORD']
    settings['database']['host'] = os.environ['DB_HOST']

elif DEPLOYMENT_TYPE == "LOCAL-UTILS":
    print("Loading LOCAL-UTILS Settings")
    with open(os.path.join(CONFIG_DIR, "local-utils.yaml"), 'r') as stream:
        settings = yaml.load(stream)

else:
    print("ERROR: Failed to load {0} settings!".format(DEPLOYMENT_TYPE))
    raise SystemExit(1)

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.11/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '4&*-wc$!_%e=u&ti2&hd1-tr^!bx5#z&7k$dz))o8=5h=%h6$v'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False
try:
    DEBUG = settings['debug']
except KeyError:
    print("Unable to read debug settings value, defaulting to FALSE.")
print("DEBUG set to {0}".format(DEBUG))

# do some environment debug logging
if DEBUG:
    print("\nPrinting Environment Variables:")
    for key in sorted(os.environ.keys()):
        print("  ENV: {0}={1}".format(key, os.environ[key]))

# Setting allowed hosts to * basically disables this feature. This would
# probably be something we'd like to lockdown in prod. At least using AWS
# infrastructure you have other options (VPC, security groups, private subnets,
# etc) that would probably be more ideal. But we could still pin down the
# allowed host to *.elb.amazonaws.com since the traffic will be fronted by a
# ALB / ELB.
ALLOWED_HOSTS = ['*']

USE_X_FORWARDED_HOST = True

if 'HTTP_X_FORWARDED_PROTO' in settings:
    SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO',
                               settings['HTTP_X_FORWARDED_PROTO'])
else:
    SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'item_service.apps.ItemServiceConfig',
    'health_check',
    'health_check.cache',
    'health_check.storage',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'fd_supply_services.x509_middleware.ReverseProxyAuthMiddleware',
]

AUTHENTICATION_BACKENDS = [
    'django.contrib.auth.backends.RemoteUserBackend',
]

ROOT_URLCONF = 'fd_supply_services.urls'

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

WSGI_APPLICATION = 'fd_supply_services.wsgi.application'

REST_FRAMEWORK = {
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 10
}

# Database
# https://docs.djangoproject.com/en/1.11/ref/settings/#databases

if 'database' in settings:
    DATABASES = {
        'default': {
            'ENGINE':   settings["database"]["engine"],
            'NAME':     settings["database"]["name"],
            'USER':     settings["database"]["user"],
            'PASSWORD': settings["database"]["password"],
            'HOST':     settings["database"]["host"],
            'PORT':     settings["database"]["port"],
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

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.11/howto/static-files/

STATIC_URL = '/django-static/'

# Process static file collection settings
if 'collect-static' in settings:
    STATIC_ROOT = os.path.join(BASE_DIR, settings["collect-static"]["root"])
