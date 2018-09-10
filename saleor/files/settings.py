{%- set store = salt['pillar.get']('saleor:server:store:'+store_name) %}

import ast
import os.path

import dj_database_url
import dj_email_url
import django_cache_url
from django.contrib.messages import constants as messages
from django.utils.translation import gettext_lazy as _, pgettext_lazy
from django_prices.templatetags.prices_i18n import get_currency_fraction


def get_list(text):
    return [item.strip() for item in text.split(',')]


def get_bool_from_env(name, default_value):
    if name in os.environ:
        value = os.environ[name]
        try:
            return ast.literal_eval(value)
        except ValueError as e:
            raise ValueError(
                '{} is an invalid value for {}'.format(value, name)) from e
    return default_value


DEBUG = {{ store.get('debug', True) }}

SITE_ID = 1

PROJECT_ROOT = os.path.normpath(os.path.join(os.path.dirname(__file__), '..', 'source'))

ROOT_URLCONF = 'saleor.urls'

WSGI_APPLICATION = 'saleor.wsgi.application'

ADMINS = (
    # ('Your Name', 'your_email@example.com'),
)
MANAGERS = ADMINS

INTERNAL_IPS = get_list('{{ store.get('internal_ips', '127.0.0.1') }}')

# Some cloud providers like Heroku export REDIS_URL variable instead of CACHE_URL
{%- if store.redis is defined %}
REDIS_URL = '{{ store.redis.url }}'
if REDIS_URL:
    CACHE_URL = os.environ.setdefault('CACHE_URL', REDIS_URL)
{%- endif %}

CACHES = {'default': django_cache_url.config()}

DATABASES = {
    'default': {
        {%- if store.database.engine == 'mysql' %}
        'ENGINE': 'django.db.backends.mysql',
        'PORT': '3306',
        'OPTIONS': {'init_command': 'SET storage_engine=INNODB,character_set_connection=utf8,collation_connection=utf8_unicode_ci', },
        {%- elif store.database.engine == 'postgresql' %}
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        {%- elif store.database.engine == 'postgis' %}
        'ENGINE': 'django.contrib.gis.db.backends.postgis',
        {%- endif %}
        'HOST': '{{ store.database.host }}',
        'NAME': '{{ store.database.name }}',
        'PASSWORD': '{{ store.database.password }}',
        'USER': '{{ store.database.user }}'
    }
}

TIME_ZONE = '{{ store.get('time_zone', 'Europe/Prague') }}'
LANGUAGE_CODE = '{{ store.get('lang_code', 'en') }}'
LANGUAGES = [
    {%- for lang in store.get('languages', 'en') %}
    {%- if lang is defined %}
    ('{{ lang|lower }}', '{{ lang|lower }}'),
    {%- endif %}
    {%- endfor %}
]
LOCALE_PATHS = [os.path.join(PROJECT_ROOT, 'locale')]
USE_I18N = True
USE_L10N = True
USE_TZ = True

FORM_RENDERER = 'django.forms.renderers.TemplatesSetting'

{%- if store.sendgrid is defined %}
SENDGRID_USERNAME = '{{ store.sendgrid.username }}'
SENDGRID_PASSWORD = '{{ store.sendgrid.password }}'
if SENDGRID_USERNAME and SENDGRID_PASSWORD:
    EMAIL_URL = 'smtp://%s:%s@smtp.sendgrid.net:587/?tls=True' % (
        SENDGRID_USERNAME, SENDGRID_PASSWORD)
    email_config = dj_email_url.parse(EMAIL_URL or 'console://')

    EMAIL_FILE_PATH = email_config['EMAIL_FILE_PATH']
    EMAIL_BACKEND = email_config['EMAIL_BACKEND']
    EMAIL_HOST = email_config['EMAIL_HOST']
    EMAIL_HOST_USER = email_config['EMAIL_HOST_USER']
    EMAIL_HOST_PASSWORD = email_config['EMAIL_HOST_PASSWORD']
    EMAIL_PORT = email_config['EMAIL_PORT']
    EMAIL_USE_TLS = email_config['EMAIL_USE_TLS']
    EMAIL_USE_SSL = email_config['EMAIL_USE_SSL']

{%- else %}

{%- if store.email is defined and store.email.url is defined %}
EMAIL_URL = '{{ store.email.url }}'
{%- endif %}
# default is for email profi by Seznam.cz
{%- if store.email is defined %}
EMAIL_BACKEND = '{{ store.email.backend }}'
EMAIL_HOST = '{{ store.email.host_url }}'
EMAIL_HOST_USER = '{{ store.email.host.user }}'
EMAIL_HOST_PASSWORD = '{{ store.email.host.password }}'
EMAIL_PORT = {{ store.email.port }}
EMAIL_USE_TLS = {{ store.email.use_tls }}
EMAIL_USE_SSL = {{ store.email.use_ssl }}
{%- else %}
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.seznam.cz'
EMAIL_PORT = 465
EMAIL_USE_TLS = False
EMAIL_USE_SSL = True
{%- endif %}

{%- endif %}

ENABLE_SSL = {{ store.get('enable_ssl', False) }}

if ENABLE_SSL:
    SECURE_SSL_REDIRECT = not DEBUG

{%- if store.from_email is defined %}
DEFAULT_FROM_EMAIL = '{{ store.from_email.default }}'
ORDER_FROM_EMAIL = '{{ store.from_email.order }}'
{%- else %}
DEFAULT_FROM_EMAIL = os.environ.get('DEFAULT_FROM_EMAIL')
ORDER_FROM_EMAIL = os.getenv('ORDER_FROM_EMAIL', DEFAULT_FROM_EMAIL)
{%- endif %}

MEDIA_ROOT = os.path.join(PROJECT_ROOT, 'media')
MEDIA_URL = '/media/'

STATIC_ROOT = os.path.normpath(os.path.join(PROJECT_ROOT, '..', 'static'))
STATIC_URL = '/static/'
STATICFILES_DIRS = [
    ('assets', os.path.join(PROJECT_ROOT, 'saleor', 'static', 'assets')),
    ('favicons', os.path.join(PROJECT_ROOT, 'saleor', 'static', 'favicons')),
    ('images', os.path.join(PROJECT_ROOT, 'saleor', 'static', 'images')),
    ('dashboard', os.path.join(PROJECT_ROOT, 'saleor', 'static', 'dashboard'))]
STATICFILES_FINDERS = [
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder']

context_processors = [
    'django.contrib.auth.context_processors.auth',
    'django.template.context_processors.debug',
    'django.template.context_processors.i18n',
    'django.template.context_processors.media',
    'django.template.context_processors.static',
    'django.template.context_processors.tz',
    'django.contrib.messages.context_processors.messages',
    'django.template.context_processors.request',
    'saleor.core.context_processors.default_currency',
    'saleor.checkout.context_processors.cart_counter',
    'saleor.core.context_processors.search_enabled',
    'saleor.site.context_processors.site',
    'social_django.context_processors.backends',
    'social_django.context_processors.login_redirect']

loaders = [
    'django.template.loaders.app_directories.Loader',
    'django.template.loaders.filesystem.Loader',
]

if not DEBUG:
    loaders = [('django.template.loaders.cached.Loader', loaders)]

TEMPLATES = [{
    'BACKEND': 'django.template.backends.django.DjangoTemplates',
    'DIRS': [os.path.join(PROJECT_ROOT, 'templates')],
    'OPTIONS': {
        'debug': DEBUG,
        'context_processors': context_processors,
        'loaders': loaders,
        'string_if_invalid': '<< MISSING VARIABLE "%s" >>' if DEBUG else ''}}]

# Make this unique, and don't share it with anybody.
SECRET_KEY = '{{ store.get('secret_key', '87941asd897897asd987') }}'

MIDDLEWARE = [
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'django_babel.middleware.LocaleMiddleware',
    'saleor.core.middleware.discounts',
    'saleor.core.middleware.google_analytics',
    'saleor.core.middleware.country',
    'saleor.core.middleware.currency',
    'saleor.core.middleware.site',
    'saleor.core.middleware.taxes',
    'social_django.middleware.SocialAuthExceptionMiddleware',
    'impersonate.middleware.ImpersonateMiddleware',
    'saleor.graphql.middleware.jwt_middleware'
]

INSTALLED_APPS = [
    # External apps that need to go before django's
    'storages',

    # Django modules
    'django.contrib.admin',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.sitemaps',
    'django.contrib.sites',
    'django.contrib.staticfiles',
    'django.contrib.auth',
    'django.contrib.postgres',
    'django.forms',

    # Local apps
    'saleor.account',
    'saleor.discount',
    'saleor.product',
    'saleor.checkout',
    'saleor.core',
    'saleor.graphql',
    'saleor.menu',
    'saleor.order.OrderAppConfig',
    'saleor.dashboard',
    'saleor.seo',
    'saleor.shipping',
    'saleor.search',
    'saleor.site',
    'saleor.data_feeds',
    'saleor.page',

    # External apps
    'versatileimagefield',
    'django_babel',
    'bootstrap4',
    'django_prices',
    'django_prices_openexchangerates',
    'django_prices_vatlayer',
    'graphene_django',
    'mptt',
    'payments',
    'webpack_loader',
    'social_django',
    'django_countries',
    'django_filters',
    'django_celery_results',
    'impersonate',
    'phonenumber_field',
    'captcha',
    {%- for extra_app in store.get('extra_apps', []) %}
    {%- if extra_app is defined %}
    '{{ extra_app }}',
    {%- endif %}
    {%- endfor %}
]

DEBUG_TOOLBAR = False

if DEBUG_TOOLBAR:
    MIDDLEWARE.append(
        'debug_toolbar.middleware.DebugToolbarMiddleware')
    INSTALLED_APPS.append('debug_toolbar')
    DEBUG_TOOLBAR_PANELS = [
        # adds a request history to the debug toolbar
        'ddt_request_history.panels.request_history.RequestHistoryPanel',

        'debug_toolbar.panels.versions.VersionsPanel',
        'debug_toolbar.panels.timer.TimerPanel',
        'debug_toolbar.panels.settings.SettingsPanel',
        'debug_toolbar.panels.headers.HeadersPanel',
        'debug_toolbar.panels.request.RequestPanel',
        'debug_toolbar.panels.sql.SQLPanel',
        'debug_toolbar.panels.templates.TemplatesPanel',
        'debug_toolbar.panels.staticfiles.StaticFilesPanel',
        'debug_toolbar.panels.cache.CachePanel',
        'debug_toolbar.panels.signals.SignalsPanel',
        'debug_toolbar.panels.logging.LoggingPanel',
        'debug_toolbar.panels.redirects.RedirectsPanel',
        'debug_toolbar.panels.profiling.ProfilingPanel',
    ]
    DEBUG_TOOLBAR_CONFIG = {
        'RESULTS_STORE_SIZE': 100}

ENABLE_SILK = {{ store.get('silk.enabled', False) }}
if ENABLE_SILK:
    MIDDLEWARE.insert(0, 'silk.middleware.SilkyMiddleware')
    INSTALLED_APPS.append('silk')

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'root': {
        'level': 'INFO',
        'handlers': ['console']},
    'formatters': {
        'verbose': {
            'format': (
                '%(levelname)s %(name)s %(message)s'
                ' [PID:%(process)d:%(threadName)s]')},
        'simple': {
            'format': '%(levelname)s %(message)s'}},
    'filters': {
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse'}},
    'handlers': {
        'mail_admins': {
            'level': 'ERROR',
            'filters': ['require_debug_false'],
            'class': 'django.utils.log.AdminEmailHandler'},
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'verbose'}},
    'loggers': {
        'django': {
            'handlers': ['console', 'mail_admins'],
            'level': 'INFO',
            'propagate': True},
        'django.server': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': True},
        'saleor': {
            'handlers': ['console'],
            'level': 'DEBUG',
            'propagate': True}}}

AUTH_USER_MODEL = 'account.User'

LOGIN_URL = '/account/login/'

DEFAULT_COUNTRY = '{{ store.get('country', 'CZ') }}'
DEFAULT_CURRENCY = '{{ store.get('currency', 'CZK') }}'
DEFAULT_DECIMAL_PLACES = get_currency_fraction(DEFAULT_CURRENCY)
AVAILABLE_CURRENCIES = [DEFAULT_CURRENCY]
COUNTRIES_OVERRIDE = {
    'EU': pgettext_lazy(
        'Name of political and economical union of european countries',
        'European Union')}

{%- if store.openexchangerates is defined %}
OPENEXCHANGERATES_API_KEY = '{{ store.openexchangerates.api_key }}'
{%- else %}
OPENEXCHANGERATES_API_KEY = os.environ.get('OPENEXCHANGERATES_API_KEY')
{%- endif %}

ACCOUNT_ACTIVATION_DAYS = {{ store.get('account_activation_days', 3) }}

LOGIN_REDIRECT_URL = 'home'

{%- if store.google is defined %}
GOOGLE_ANALYTICS_TRACKING_ID = '{{ store.google.analytics_tracking_id }}'
{%- else %}
GOOGLE_ANALYTICS_TRACKING_ID = os.environ.get('GOOGLE_ANALYTICS_TRACKING_ID')
{%- endif %}

def get_host():
    from django.contrib.sites.models import Site
    return Site.objects.get_current().domain

PAYMENT_HOST = get_host

PAYMENT_MODEL = 'order.Payment'

PAYMENT_VARIANTS = {

{%- if store.paypal is defined %}
    'paypal': ('payments.paypal.PaypalProvider', {
        'client_id': '{{ store.paypal.client_id }}',
        'secret': '{{ store.paypal.secret }}',
        'endpoint': '{{ store.paypal.api_endpoint }}',
        'capture': {{ store.paypal.capture }} }),
{%- endif %}

{%- if store.cod is defined %}
    'cod': ('django_payments_cod.CODProvider', {}),
{%- endif %}

{%- if store.payment_choices is not defined %}
    'dummy': ('payments.dummy.DummyProvider', {})
{%- endif %}

}

{%- if store.vatlayer is defined %}
# VAT configuration
# Enabling vat requires valid vatlayer access key.
VATLAYER_ACCESS_KEY = '{{ store.vatlayer.access_key }}'
VATLAYER_API = '{{ store.vatlayer.api_endpoint }}'
{%- endif %}

CHECKOUT_PAYMENT_CHOICES = [
{%- if store.payment_choices is defined %}
{%- for payment_choice in store.get('payment_choices', []) %}
    ('{{ payment_choice.engine }}', '{{ payment_choice.display_name }}'),
{%- endfor %}
{%- else %}
    ('default', 'Dummy provider'),
{%- endif%}
]

SESSION_SERIALIZER = 'django.contrib.sessions.serializers.JSONSerializer'

# Do not use cached session if locmem cache backend is used but fallback to use
# default django.contrib.sessions.backends.db instead
if not CACHES['default']['BACKEND'].endswith('LocMemCache'):
    SESSION_ENGINE = 'django.contrib.sessions.backends.cached_db'

MESSAGE_TAGS = {
    messages.ERROR: 'danger'}

LOW_STOCK_THRESHOLD = {{ store.get('low_stock_threshold', 10) }}
MAX_CART_LINE_QUANTITY = int({{ store.get('max_cart_line_quantity', 50) }})

PAGINATE_BY = {{ store.get('paginate_by', 16) }}
DASHBOARD_PAGINATE_BY = {{ store.get('dashboard_paginate_by', 30) }}
DASHBOARD_SEARCH_LIMIT = {{ store.get('dashboard_search_limit', 5) }}

bootstrap4 = {
    'set_placeholder': False,
    'set_required': False,
    'success_css_class': '',
    'form_renderers': {
        'default': 'saleor.core.utils.form_renderer.FormRenderer'}}

TEST_RUNNER = ''

ALLOWED_HOSTS = get_list('{{ store.get('allowed_hosts', '*') }}')

SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

{%- if store.aws is defined %}
# Amazon S3 configuration
AWS_ACCESS_KEY_ID = '{{ store.aws.access_key_id }}'
AWS_LOCATION = '{{ store.aws.location }}'
AWS_MEDIA_BUCKET_NAME = '{{ store.aws.media_bucket_name }}'
AWS_MEDIA_CUSTOM_DOMAIN = '{{ store.aws.media_custom_domain }}'
AWS_QUERYSTRING_AUTH = {{ store.aws.querystring_auth }}
AWS_S3_CUSTOM_DOMAIN = '{{ store.aws.static_custom_domain }}'
AWS_SECRET_ACCESS_KEY = '{{ store.aws.secret_access_key }}'
AWS_STORAGE_BUCKET_NAME = '{{ store.aws.storage_bucket_name }}'
if AWS_STORAGE_BUCKET_NAME:
    STATICFILES_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'

if AWS_MEDIA_BUCKET_NAME:
    DEFAULT_FILE_STORAGE = 'saleor.core.storages.S3MediaStorage'
    THUMBNAIL_DEFAULT_STORAGE = DEFAULT_FILE_STORAGE
{%- else %}
# Amazon S3 configuration
AWS_ACCESS_KEY_ID = os.environ.get('AWS_ACCESS_KEY_ID')
AWS_LOCATION = os.environ.get('AWS_LOCATION', '')
AWS_MEDIA_BUCKET_NAME = os.environ.get('AWS_MEDIA_BUCKET_NAME')
AWS_MEDIA_CUSTOM_DOMAIN = os.environ.get('AWS_MEDIA_CUSTOM_DOMAIN')
AWS_QUERYSTRING_AUTH = get_bool_from_env('AWS_QUERYSTRING_AUTH', False)
AWS_S3_CUSTOM_DOMAIN = os.environ.get('AWS_STATIC_CUSTOM_DOMAIN')
AWS_SECRET_ACCESS_KEY = os.environ.get('AWS_SECRET_ACCESS_KEY')
AWS_STORAGE_BUCKET_NAME = os.environ.get('AWS_STORAGE_BUCKET_NAME')

if AWS_STORAGE_BUCKET_NAME:
    STATICFILES_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'

if AWS_MEDIA_BUCKET_NAME:
    DEFAULT_FILE_STORAGE = 'saleor.core.storages.S3MediaStorage'
    THUMBNAIL_DEFAULT_STORAGE = DEFAULT_FILE_STORAGE
{%- endif %}

MESSAGE_STORAGE = 'django.contrib.messages.storage.session.SessionStorage'

VERSATILEIMAGEFIELD_RENDITION_KEY_SETS = {
    'products': [
        ('product_gallery', 'crop__540x540'),
        ('product_gallery_2x', 'crop__1080x1080'),
        ('product_small', 'crop__60x60'),
        ('product_small_2x', 'crop__120x120'),
        ('product_list', 'crop__255x255'),
        ('product_list_2x', 'crop__510x510')]}

VERSATILEIMAGEFIELD_SETTINGS = {
    # Images should be pre-generated on Production environment
    'create_images_on_demand': DEBUG,
}

PLACEHOLDER_IMAGES = {
    60: 'images/placeholder60x60.png',
    120: 'images/placeholder120x120.png',
    255: 'images/placeholder255x255.png',
    540: 'images/placeholder540x540.png',
    1080: 'images/placeholder1080x1080.png'}

DEFAULT_PLACEHOLDER = 'images/placeholder255x255.png'

WEBPACK_LOADER = {
    'DEFAULT': {
        'CACHE': not DEBUG,
        'BUNDLE_DIR_NAME': 'assets/',
        'STATS_FILE': os.path.join(PROJECT_ROOT, 'webpack-bundle.json'),
        'POLL_INTERVAL': 0.1,
        'IGNORE': [
            r'.+\.hot-update\.js',
            r'.+\.map']
    }
}


LOGOUT_ON_PASSWORD_CHANGE = {{ store.get('logout_on_password_change', False) }}

# SEARCH CONFIGURATION
DB_SEARCH_ENABLED = {{ store.get('db_search_enabled', True) }}

# support deployment-dependant elastic enviroment variable
{%- if store.elasticsearch is defined or store.searchbox is defined or store.bonsai is defined %}
ES_URL = ('{{ store.elasticsearch.url }}' or
          '{{ store.searchbox.url }}' or '{{ store.bonsai.url }}')

ENABLE_SEARCH = bool(ES_URL) # global search disabling

if ES_URL:
    SEARCH_BACKEND = 'saleor.search.backends.elasticsearch'
    INSTALLED_APPS.append('django_elasticsearch_dsl')
    ELASTICSEARCH_DSL = {
        'default': {
            'hosts': ES_URL}}
{%- else %}
ES_URL = (os.environ.get('ELASTICSEARCH_URL') or
          os.environ.get('SEARCHBOX_URL') or os.environ.get('BONSAI_URL'))

ENABLE_SEARCH = bool(ES_URL) or DB_SEARCH_ENABLED  # global search disabling

SEARCH_BACKEND = 'saleor.search.backends.postgresql'

if ES_URL:
    SEARCH_BACKEND = 'saleor.search.backends.elasticsearch'
    INSTALLED_APPS.append('django_elasticsearch_dsl')
    ELASTICSEARCH_DSL = {
        'default': {
            'hosts': ES_URL}}
{%- endif %}

SEARCH_BACKEND = 'saleor.search.backends.postgresql'

AUTHENTICATION_BACKENDS = [
    'saleor.account.backends.facebook.CustomFacebookOAuth2',
    'saleor.account.backends.google.CustomGoogleOAuth2',
    'graphql_jwt.backends.JSONWebTokenBackend',
    'django.contrib.auth.backends.ModelBackend']

SOCIAL_AUTH_PIPELINE = [
    'social_core.pipeline.social_auth.social_details',
    'social_core.pipeline.social_auth.social_uid',
    'social_core.pipeline.social_auth.auth_allowed',
    'social_core.pipeline.social_auth.social_user',
    'social_core.pipeline.social_auth.associate_by_email',
    'social_core.pipeline.user.create_user',
    'social_core.pipeline.social_auth.associate_user',
    'social_core.pipeline.social_auth.load_extra_data',
    'social_core.pipeline.user.user_details']

SOCIAL_AUTH_USERNAME_IS_FULL_EMAIL = True
SOCIAL_AUTH_USER_MODEL = AUTH_USER_MODEL
SOCIAL_AUTH_FACEBOOK_SCOPE = ['email']
SOCIAL_AUTH_FACEBOOK_PROFILE_EXTRA_PARAMS = {
    'fields': 'id, email'}

# As per March 2018, Facebook requires all traffic to go through HTTPS only
SOCIAL_AUTH_REDIRECT_IS_HTTPS = True

# CELERY SETTINGS
{%- if store.celery is defined %}
CELERY_BROKER_URL = {{ store.get('celery.broker_url', 'celery.cloudamqp_url') }} or ''
CELERY_TASK_ALWAYS_EAGER = False if CELERY_BROKER_URL else True
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_RESULT_BACKEND = 'django-db'
{%- else %}
CELERY_BROKER_URL = os.environ.get(
    'CELERY_BROKER_URL', os.environ.get('CLOUDAMQP_URL')) or ''
CELERY_TASK_ALWAYS_EAGER = False if CELERY_BROKER_URL else True
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_RESULT_BACKEND = 'django-db'
{%- endif %}

# Impersonate module settings
IMPERSONATE = {
    'URI_EXCLUSIONS': [r'^dashboard/'],
    'CUSTOM_USER_QUERYSET': 'saleor.account.impersonate.get_impersonatable_users',  # noqa
    'USE_HTTP_REFERER': True,
    'CUSTOM_ALLOW': 'saleor.account.impersonate.can_impersonate'}


# Rich-text editor
ALLOWED_TAGS = [
    'a',
    'b',
    'blockquote',
    'br',
    'em',
    'h2',
    'h3',
    'i',
    'img',
    'li',
    'ol',
    'p',
    'strong',
    'ul']
ALLOWED_ATTRIBUTES = {
    '*': ['align', 'style'],
    'a': ['href', 'title'],
    'img': ['src']}
ALLOWED_STYLES = ['text-align']


# Slugs for menus precreated in Django migrations
DEFAULT_MENUS = {
    'top_menu_name': 'navbar',
    'bottom_menu_name': 'footer'}

# This enable the new 'No Captcha reCaptcha' version (the simple checkbox)
# instead of the old (deprecated) one. For more information see:
#   https://github.com/praekelt/django-recaptcha/blob/34af16ba1e/README.rst
NOCAPTCHA = True

# Set Google's reCaptcha keys
{%- if store.recaptcha is defined %}
RECAPTCHA_PUBLIC_KEY = '{{ store.recaptcha.public_key }}'
RECAPTCHA_PRIVATE_KEY = '{{ store.recaptcha.private_key }}'
{%- else %}
RECAPTCHA_PUBLIC_KEY = ''
RECAPTCHA_PUBLIC_KEY = ''
{%- endif %}

#  Sentry
{%- if sentry is defined %}
SENTRY_DSN = '{{ store.sentry.dsn }}'
if SENTRY_DSN:
    INSTALLED_APPS.append('raven.contrib.django.raven_compat')
    RAVEN_CONFIG = {
        'dsn': SENTRY_DSN}
{%- else %}
SENTRY_DSN = os.environ.get('SENTRY_DSN')
if SENTRY_DSN:
    INSTALLED_APPS.append('raven.contrib.django.raven_compat')
    RAVEN_CONFIG = {
        'dsn': SENTRY_DSN,}
{%- endif %}

SERIALIZATION_MODULES = {
    'json': 'saleor.core.utils.json_serializer'}
