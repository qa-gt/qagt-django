"""
Django settings for QAGT project.

Generated by 'django-admin startproject' using Django 4.0.3.

For more information on this file, see
https://docs.djangoproject.com/en/4.0/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/4.0/ref/settings/
"""

from pathlib import Path
import os
import time

QAGT_SERVER = os.environ.get('QAGTSERVER', "DEVELOPMENT")
QAGT_POSTGRESQL = {
    "HOST": os.environ.get('QAGTPOSTGRESQLHOST',
                           "yxzlownserveraddress.yxzl.top"),
    "PORT": os.environ.get('QAGTPOSTGRESQLPORT', "5432"),
    "USER": os.environ.get('QAGTPOSTGRESQLUSER', "yxzl"),
    "PASSWORD": os.environ.get('QAGTPOSTGRESQLPASSWORD', "@yixiangzhilv"),
}

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

if QAGT_SERVER.startswith("DEVELOPMENT"):
    QAGT_SERVER = "DEVELOPMENT"
    print("-----QAGT_SERVER is DEVELOPMENT-----")
    DEBUG = True
    DATABASES = {
        "default": {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        },
    }
elif QAGT_SERVER.startswith("TEST"):
    QAGT_SERVER = "TEST"
    print("-----QAGT_SERVER is TEST-----")
    DEBUG = True
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': 'qagttest',
            'USER': QAGT_POSTGRESQL["USER"],
            'PASSWORD': QAGT_POSTGRESQL['PASSWORD'],
            'HOST': QAGT_POSTGRESQL["HOST"],
            'PORT': QAGT_POSTGRESQL["PORT"],
        },
    }
else:
    QAGT_SERVER = "PRODUCTION"
    print("-----QAGT_SERVER is PRODUCTION-----")
    DEBUG = False
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': 'qagt',
            'USER': QAGT_POSTGRESQL["USER"],
            'PASSWORD': QAGT_POSTGRESQL['PASSWORD'],
            'HOST': QAGT_POSTGRESQL["HOST"],
            'PORT': QAGT_POSTGRESQL["PORT"],
        },
    }
# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-6gq34i&n0-nqdndwa*@4+#(g_@i$5zsnume4zdj9r^5p4*1x4z'

ALLOWED_HOSTS = ["*"]

# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    "QAGT.apps.QAGTConfig",
    "main.apps.MainConfig",
    "qagt_user.apps.QagtUserConfig",
    "qagt_admin.apps.QagtAdminConfig",
    "qagt_article.apps.QagtArticleConfig",
    "qagt_report.apps.QagtReportConfig",
    "qagt_notice.apps.QagtNoticeConfig",
]

MIDDLEWARE = [
    "QAGT.middleware.FirstCheck",
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    # 'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    "qagt_user.middleware.LoginRequired",
    "qagt_admin.middleware.AdminRequired",
    "QAGT.middleware.PostCheckV1",
]
if QAGT_SERVER == "TEST":
    MIDDLEWARE = ["QAGT.middleware_test.TestServerChecker"] + MIDDLEWARE

ROOT_URLCONF = 'QAGT.urls'

TEMPLATES = [
    {
        'BACKEND':
        'django.template.backends.jinja2.Jinja2',
        'DIRS': [
            BASE_DIR / 'templates',
            BASE_DIR / 'main/templates',
            BASE_DIR / 'qagt_user/templates',
            BASE_DIR / 'qagt_article/templates',
            BASE_DIR / 'qagt_admin/templates',
            BASE_DIR / 'qagt_report/templates',
        ],
        'APP_DIRS':
        True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                "QAGT.context_processors.global_context",
            ],
            'environment':
            'QAGT.jinja2_env.environment'
        },
    },
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

WSGI_APPLICATION = 'QAGT.wsgi.application'

# Password validation
# https://docs.djangoproject.com/en/4.0/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME':
        'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME':
        'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME':
        'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME':
        'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

LOG_PATH = BASE_DIR / "logs"

if not LOG_PATH.exists():
    LOG_PATH.mkdir()

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'standard': {
            'format':
            '[%(asctime)s] [%(filename)s:%(lineno)d] [%(module)s:%(funcName)s] '
            '[%(levelname)s]- %(message)s'
        },
        'simple': {
            'format':
            '[%(levelname)s] %(message)s [%(asctime)s] [%(req_method)s "%(req_path)s" %(req_user)d@%(req_ip)s]',
            "datefmt": '%Y-%m-%d %H:%M:%S',
        },
        'verbose': {
            'format':
            '%(levelname)s %(asctime)s %(module)s %(lineno)d %(message)s'
        }
    },
    'filters': {
        'require_debug_true': {
            '()': 'django.utils.log.RequireDebugTrue'
        }
    },
    'handlers': {
        'file': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': LOG_PATH / ('%s.log' % time.strftime("%Y-%m-%d")),
            'formatter': 'simple',
            "encoding": "utf-8",
        },
    },
    'loggers': {
        'log': {
            'handlers': ['file'],
            'level': 'INFO',
            'propagate': True,
        },
    }
}

# AUTH_USER_MODEL = 'QAGT.Users'

# Internationalization
# https://docs.djangoproject.com/en/4.0/topics/i18n/

LANGUAGE_CODE = 'zh-hans'

TIME_ZONE = 'Asia/Shanghai'

USE_I18N = True

USE_TZ = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.0/howto/static-files/

STATIC_URL = 'static/'

STATIC_ROOT = os.path.join(BASE_DIR, 'static_root')

STATICFILES_DIRS = [
    BASE_DIR / "static",
]

# Default primary key field type
# https://docs.djangoproject.com/en/4.0/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

APPEND_SLASH = False
