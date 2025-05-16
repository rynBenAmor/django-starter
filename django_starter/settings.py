
from pathlib import Path
from decouple import config
from .logging import LOGGING
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _


# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

DJANGO_SECRET_KEY = config('DJANGO_SECRET_KEY', cast=str)
DJANGO_IS_PRODUCTION = config('DJANGO_IS_PRODUCTION', default=True, cast=bool)
DB_TYPE = config('DB_TYPE')
print(DB_TYPE)
print(f"----production is set to : {DJANGO_IS_PRODUCTION}-----")


SECRET_KEY = DJANGO_SECRET_KEY

DEBUG = not DJANGO_IS_PRODUCTION

HTML_MINIFY = True #django-htmlmin

ALLOWED_HOSTS = []

INTERNAL_IPS = ["127.0.0.1"]

#this sends an exception email on production
if DJANGO_IS_PRODUCTION :
    ADMINS = [
        ("Administration", config('DJANGO_ADMIN_EMAIL_1', cast=str)),
    ]

SECURE_SSL_REDIRECT = DJANGO_IS_PRODUCTION #possible infinite redirect error
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')#when nginx does the SSL

SESSION_COOKIE_SAMESITE = 'Lax'
SESSION_COOKIE_AGE = 5184000 #60 days
SESSION_COOKIE_SECURE = DJANGO_IS_PRODUCTION # Ensure session cookies are only sent over HTTPS
SESSION_COOKIE_HTTPONLY = True

CSRF_COOKIE_SECURE = DJANGO_IS_PRODUCTION #Ensure CSRF cookies are only sent over HTTPS
CSRF_TRUSTED_ORIGINS = [    
        "http://localhost:8000",
        "http://127.0.0.1:8000",  
        #..add domain in production..#
    ]
CSRF_COOKIE_HTTPONLY = True
CSRF_FAILURE_VIEW = "accounts.views.csrf_failure"#to override django's 403_csrf.html in django.views.csrf.csrf_failure

X_FRAME_OPTIONS = 'DENY'  # or SAMEORIGIN

SECURE_HSTS_SECONDS = 31536000  # 1 year (adjust as needed)
SECURE_HSTS_INCLUDE_SUBDOMAINS = True  # Apply to all subdomains
SECURE_HSTS_PRELOAD = True  # Preload into browsers

#csp policy
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_REFERRER_POLICY = "strict-origin-when-cross-origin" # cuz 'strict-origin' breaks HTTP_REFERER


# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    
    #3rd party apps
   
    #local apps
    'accounts',
    'home',#can delete
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    
    #3rd party
    "htmlmin.middleware.HtmlMinifyMiddleware",
    "htmlmin.middleware.MarkRequestMiddleware",
    'django.middleware.locale.LocaleMiddleware',#translation
    
    #local
    'accounts.middlewares.EmailVerificationMiddleware',

]

ROOT_URLCONF = 'django_starter.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / "templates", BASE_DIR / "accounts/templates",],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',

                'accounts.context_processors.current_language_context',
            ],
        },
    },
]

WSGI_APPLICATION = 'django_starter.wsgi.application'


# Database
# https://docs.djangoproject.com/en/5.2/ref/settings/#databases


if DB_TYPE == 'sqlite':  # Switch to SQLite

    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }
else:  # Switch to PostgreSQL

    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': config('DB_NAME'),
            'USER': config('DB_USER'),
            'PASSWORD': config('DB_PASSWORD'),
            'HOST': config('DB_HOST'),
            'PORT': config('DB_PORT', default='5432', cast=int),
        }
    }


# Password validation
# https://docs.djangoproject.com/en/5.2/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/5.2/topics/i18n/

LANGUAGE_CODE = 'en'

# Supported languages (language codes must match the ones in locale folders)
LANGUAGES = [
    ('en', _('English')),
    ('fr', _('French')),
]

TIME_ZONE = 'Africa/Tunis'
USE_I18N = True
USE_L10N = True
USE_TZ = True

# https://docs.djangoproject.com/en/dev/ref/settings/#locale-paths
LOCALE_PATHS = [
    BASE_DIR / "locale",
]


# https://docs.djangoproject.com/en/dev/topics/auth/customizing/#substituting-a-custom-user-model
AUTHENTICATION_BACKENDS = [
    'accounts.backends.EmailBackend',  # your email auth backend
]

AUTH_USER_MODEL = "accounts.User"

LOGIN_REDIRECT_URL = '/'
LOGIN_URL = 'accounts:login'  # Namespace is specified as 'accounts'
LOGOUT_REDIRECT_URL = 'accounts:login'


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.2/howto/static-files/

# Static & Media
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_DIRS = [BASE_DIR / 'static']

#versioning (STATICFILES_STORAGE is deprecated since 5.1)
STORAGES = {
    "staticfiles": {
        "BACKEND": "django.contrib.staticfiles.storage.ManifestStaticFilesStorage",
    },
    "default": {
        "BACKEND": "django.core.files.storage.FileSystemStorage",
    },
}

# Media files
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# Default primary key field type
# https://docs.djangoproject.com/en/5.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'


# Email server configuration
if DJANGO_IS_PRODUCTION:
    
    EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
    EMAIL_HOST = 'smtp.gmail.com'
    EMAIL_USE_TLS = True

    EMAIL_HOST_USER = config('EMAIL_HOST_USER')
    EMAIL_HOST_PASSWORD = config('EMAIL_HOST_PASSWORD')
    EMAIL_PORT = config('EMAIL_PORT', cast=int)
    DEFAULT_FROM_EMAIL = config('DEFAULT_FROM_EMAIL')

else:
    EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"
