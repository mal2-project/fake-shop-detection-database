import os

from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _

from mal2 import version
from mal2.utils import get_secret_key


################################################################################
# BASE

BASE_DIR = os.path.dirname(
    os.path.dirname(
        os.path.abspath(os.path.join(__file__, os.pardir))
    )
)

################################################################################
# ENVIRONMENT

VERSION = version.VERSION

DJANGO_ENV = "DEVELOP"

PROJECT_NAME = "mal2_db"

DB_HOST = "localhost"
DB_USER = "mal2db"
DB_NAME = "mal2db"
DB_PASSWORD = "MY_SECRET_PASSWORD"

################################################################################
# DEFAULTS

SECRET_KEY = get_secret_key()

DEBUG = True

ROOT_URLCONF = "mal2.urls"

ADMINS = (
    ("Name", "name@domain.tld"),
)

MANAGERS = ADMINS
ALLOWED_HOSTS = ["*"]

################################################################################
# MEDIA / STATIC / LOCALE

STATIC_URL = "/static/"

STATICFILES_DIRS = (
    os.path.join(BASE_DIR, "mal2", "static"),
)

STATIC_ROOT = os.path.join(BASE_DIR, "static")

MEDIA_URL = "/media/"
MEDIA_ROOT = os.path.join(BASE_DIR, "media")
SCREENSHOTS_PATH = os.path.join(MEDIA_ROOT, "websites", "screenshots")

LOCALE_PATHS = (
    os.path.join(BASE_DIR, "locale/"),
)

MAX_UPLOAD_SIZE = 1048576

################################################################################
# LANGUAGE/DATE/TIME

LANGUAGE_CODE = "en-GB"

TIME_ZONE = "Europe/Vienna"

USE_I18N = True
USE_L10N = True
USE_TZ = True
USE_THOUSAND_SEPARATOR = True

# for django-modeltranslation

LANGUAGES = (
    ("de", _("German")),
    ("en-GB", _("English")),
)

################################################################################
# DATABASE

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "HOST": DB_HOST,
        "NAME": DB_NAME,
        "USER": DB_USER,
        "PASSWORD": DB_PASSWORD,
    }
}

################################################################################
# INSTALLED APPS

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.humanize",
    "django.contrib.messages",
    "django.contrib.sessions",
    "django.contrib.staticfiles",
    "django.forms",
    "django_countries",
    "loginas",
    "modeltranslation",
    "phonenumber_field",
    # apps
    "mal2",
    "mal2_db",
]

CAN_SIGNUP = False

################################################################################
# MIDDLEWARE

MIDDLEWARE = [
    # django
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.http.ConditionalGetMiddleware",
    "django.middleware.locale.LocaleMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.common.BrokenLinkEmailsMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "mal2.middleware.user.CurrentUserMiddleware",
]

################################################################################
# TEMPLATES

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "APP_DIRS": True,
        'DIRS': [
            os.path.join(BASE_DIR, "templates"),
        ],
        "OPTIONS": {
            "context_processors": [
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "django.template.context_processors.csrf",
                "django.template.context_processors.debug",
                "django.template.context_processors.i18n",
                "django.template.context_processors.media",
                "django.template.context_processors.request",
                "django_settings_export.settings_export",
            ],
        },
    },
]

FORM_RENDERER = "django.forms.renderers.TemplatesSetting"

WSGI_APPLICATION = "mal2.wsgi.application"

################################################################################
# AUTHENTICATION

AUTH_USER_MODEL = "mal2_db.User"

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]

################################################################################
# LOGIN

LOGIN_REDIRECT_URL = "mal2_db:check_websites"
LOGIN_URL = "mal2_db:signin"

LOGOUT_REDIRECT_URL = "mal2_db:signin"
LOGOUT_URL = "mal2_db:signout"

################################################################################
# EMAIL

SERVER_EMAIL = "name@domain.tld"

EMAIL_HOST = "mail.domain.tld"
EMAIL_HOST_USER = "mal2DB"
EMAIL_HOST_PASSWORD = "MY_SECRET_PASSWORD"
EMAIL_PORT = 25
EMAIL_USE_TLS = True

DEFAULT_FROM_EMAIL = "noreply@domain.tld"

EMAIL_SUBJECT_PREFIX = "[%s%s]" % (
    PROJECT_NAME,
    DEBUG and "-DEV" or "",
)

################################################################################
# LOGGING

LOG_PATH = "/var/log/%s" % (
    PROJECT_NAME,
)

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "normal": {
            "format": "[%(levelname)s] %(asctime)s - %(name)s - %(message)s"
        },
    },
    "handlers": {
        "error": {
            "class": "logging.FileHandler",
            "filename": os.path.join(LOG_PATH, "error.log"),
            "formatter": "normal",
            "level": "ERROR",
        },
        "debug": {
            "class": "logging.FileHandler",
            "filename": os.path.join(LOG_PATH, "debug.log"),
            "formatter": "normal",
            "level": "DEBUG",
        },
        "mail_admins": {
            "class": "django.utils.log.AdminEmailHandler",
            "include_html": True,
        },
    },
    "loggers": {
        "": {
            "handlers": ["error", "debug", ],
            "level": "DEBUG",
        },
        "requests": {
            "handlers": ["error"],
            "level": "ERROR",
            "propagate": False,
        },
        "urllib3": {
            "handlers": ["error"],
            "level": "ERROR",
            "propagate": False,
        },
        "django.request": {
            "handlers": ["mail_admins", ],
            "level": "ERROR",
            "propagate": False,
        },
    },
}

################################################################################
# CACHE

SESSION_ENGINE = "django.contrib.sessions.backends.cached_db"
SESSION_EXPIRE_AT_BROWSER_CLOSE = True
SESSION_COOKIE_NAME = "sessionid_%s" % (PROJECT_NAME,)

CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.memcached.MemcachedCache",
        "LOCATION": "127.0.0.1:11211",
        "TIMEOUT": 3600,
    },
}

################################################################################
# NAVIGATION

DJANGO_NAVBAR_EXPAND = "lg"  # Possible values: md, lg or xl

DJANGO_NAVBAR = [
    {
        "align": "left",
        "title": _("Websites"),
        "href": reverse_lazy("mal2_db:websites"),
        "icon": "web",
        "dropdown_items": [
            {
                "title": _("All"),
                "href": reverse_lazy("mal2_db:all_websites"),
                "permissions": [
                    "mal2_db.view_website",
                ],
            },
            {
                "title": _("to check"),
                "href": reverse_lazy("mal2_db:check_websites"),
                "permissions": [
                    "mal2_db.view_website",
                ],
            },
            # {
            #     "title": _("no verification"),
            #     "href": reverse_lazy("mal2_db:safe_websites"),
            #     "permissions": [
            #         "mal2_db.view_website",
            #     ],
            # },
            # {
            #     "title": _("checked - no fake"),
            #     "href": reverse_lazy("mal2_db:no_fake_websites"),
            #     "permissions": [
            #         "mal2_db.view_website",
            #     ],
            # },
            # {
            #     "title": _("Unsure"),
            #     "href": reverse_lazy("mal2_db:unsure_websites"),
            #     "permissions": [
            #         "mal2_db.view_website",
            #     ],
            # },
            {
                "title": _("Disagreement"),
                "href": reverse_lazy("mal2_db:disagreement_websites"),
                "permissions": [
                    "mal2_db.view_website",
                ],
            },
            # {
            #     "title": _("other websites"),
            #     "href": reverse_lazy("mal2_db:other_websites"),
            #     "permissions": [
            #         "mal2_db.view_website",
            #     ],
            # },
            # {
            #     "title": _("online shops"),
            #     "href": reverse_lazy("mal2_db:online_shop"),
            #     "permissions": [
            #         "mal2_db.view_website",
            #     ],
            # },
        ]
    },
    {
        "align": "left",
        "title": _("Database"),
        "href": reverse_lazy("mal2_db:db"),
        "icon": "view-dashboard",
        "dropdown_items": [
            {
                "title": _("Fake shop"),
                "href": reverse_lazy("mal2_db:fake_shop"),
                "permissions": [
                    "mal2_db.view_mal2fakeshopdb",
                ],
            },
            {
                "title": _("Brand counterfeiters"),
                "href": reverse_lazy("mal2_db:counterfeiters"),
                "permissions": [
                    "mal2_db.view_mal2counterfeitersdb",
                ],
            },
        ]
    },
    {
        "align": "right",
        "title": _("System control"),
        "icon": "settings-outline",
        "dropdown_items": [
            {
                "title": _("User management"),
                "href": reverse_lazy("mal2_db:users_data_table"),
                "permissions": [
                    "mal2_db.view_user",
                ],
            },
        ],
    },
    {
        "align": "right",
        "title": "%USERNAME%",
        "icon": "account-box",
        "dropdown_items": [
            {
                "title": _("Django-Admin"),
                "attrs": {
                    "target": "_blank",
                },
                "href": reverse_lazy("admin:index"),
                "permissions": [
                    "is_superuser",
                ],
            },
            {
                "title": _("API documentation"),
                "attrs": {
                    "target": "_blank",
                },
                "href": reverse_lazy("swagger"),
            },
            {
                "divider": True,
            },
            {
                "attrs": {
                    "data-modal-link": True
                },
                "href": reverse_lazy("mal2_db:password_change"),
                "title": _("Change password"),
            },
            {
                "divider": True,
            },
            {
                "title": _("Sign out"),
                "href": reverse_lazy("mal2_db:signout"),
            },
        ]
    },
]

################################################################################
# DJANGO SETTING EXPORT

SETTINGS_EXPORT = [
    "CAN_SIGNUP",
    "DEBUG",
    "EMAIL_SUBJECT_PREFIX",
    "VERSION",
]
