
from pathlib import Path
from decouple import config
from .logging import LOGGING
from django.utils.translation import gettext_lazy as _

# * ----------------------------------------------------------------------------------------------------------
# * variable setup
# * ----------------------------------------------------------------------------------------------------------
# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

DJANGO_SECRET_KEY = config('DJANGO_SECRET_KEY', cast=str)
DJANGO_IS_PRODUCTION = config('DJANGO_IS_PRODUCTION', default=True, cast=bool)
DJANGO_ALLOWED_HOSTS = [h.strip() for h in config('DJANGO_ALLOWED_HOSTS', default='').split(',') if h.strip()]
DB_TYPE = config('DB_TYPE')

if DJANGO_IS_PRODUCTION:    
    DJANGO_CUSTOM_ADMIN_URL ="some/custom/abstract/url/"
else:
    DJANGO_CUSTOM_ADMIN_URL ="admin/" # ? to keep logs readable in dev

DJANGO_BROWSER_RELOAD = config('DJANGO_BROWSER_RELOAD', default=False, cast=bool)

print(
    "[==================]\n"
    f"Production: {DJANGO_IS_PRODUCTION}\n"
    f"DATABASE: {DB_TYPE}\n"
    f"Hosts: {DJANGO_ALLOWED_HOSTS}\n"
    f"HMR: {DJANGO_BROWSER_RELOAD}\n"
    "[==================]\n"
)

# * ----------------------------------------------------------------------------------------------------
# * Security settings 
# * ----------------------------------------------------------------------------------------------------
SECRET_KEY = DJANGO_SECRET_KEY

DEBUG = not DJANGO_IS_PRODUCTION

HTML_MINIFY = True #django-htmlmin

ALLOWED_HOSTS = DJANGO_ALLOWED_HOSTS

INTERNAL_IPS = ["127.0.0.1"]

#this sends a critical email on production
if DJANGO_IS_PRODUCTION:
    ADMINS = [
        ("Administration", email.strip()) for email in config("DJANGO_ADMIN_EMAILS", cast=str).split(",") if email.strip()
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


# * ----------------------------------------------------------------------------------------------------------
# * app definitions
# * ----------------------------------------------------------------------------------------------------------
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
    'accounts.middlewares.Enforce2FAMiddleware',
    'accounts.middlewares.AdminAccessMiddleware',

    

]

ROOT_URLCONF = 'a_django_starter.urls'

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

WSGI_APPLICATION = 'a_django_starter.wsgi.application'



# * ----------------------------------------------------------------------------------------------------------
# * Database
# * ----------------------------------------------------------------------------------------------------------

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


# * ----------------------------------------------------------------------------------------------------------
# * Internationalization
# * ----------------------------------------------------------------------------------------------------------

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


# * ----------------------------------------------------------------------------------------------------------
# * AUthentication
# * ----------------------------------------------------------------------------------------------------------
AUTHENTICATION_BACKENDS = [
    'accounts.backends.AuthByEmailBackend',  # your email auth backend
]

AUTH_USER_MODEL = "accounts.User"

LOGIN_REDIRECT_URL = '/'
LOGIN_URL = 'accounts:login'  # Namespace is specified as 'accounts'
LOGOUT_REDIRECT_URL = 'accounts:login'



# * ----------------------------------------------------------------------------------------------------------
# * Static files (CSS, JavaScript, Images)
# * ----------------------------------------------------------------------------------------------------------

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

# * ----------------------------------------------------------------------------------------------------------
# * Mailing
# * ----------------------------------------------------------------------------------------------------------

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


# *--------------------------------------------------------------------
# * Payment 
# *--------------------------------------------------------------------
"""
#https://flouci.stoplight.io/docs/flouci-payment-apis/455b330c10e0d-en-flouci-payment-api
FLOUCI_APP_TOKEN = config('FLOUCI_APP_TOKEN', cast=str, default=None)
FLOUCI_APP_SECRET = config('FLOUCI_APP_SECRET', cast=str, default=None)

#https://www.paymee.tn/paymee-integration-with-redirection/
PAYMEE_API_KEY = config('PAYMEE_API_KEY', cast=str, default=None)
"""
# * ----------------------------------------------------------------------------------------------------------
# * Development auto reload
# * ----------------------------------------------------------------------------------------------------------
if DJANGO_BROWSER_RELOAD and DEBUG:
    INSTALLED_APPS += ['django_browser_reload']
    MIDDLEWARE += ["django_browser_reload.middleware.BrowserReloadMiddleware"]