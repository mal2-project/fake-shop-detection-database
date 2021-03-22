from mal2.settings.base import (
    INSTALLED_APPS,
)


################################################################################
# REST

REST_FRAMEWORK = {
    "DEFAULT_PERMISSION_CLASSES": [
        "mal2_rest.permissions.CustomDjangoModelPermissions",
    ],
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "rest_framework.authentication.TokenAuthentication",
    ],
    'DEFAULT_THROTTLE_CLASSES': [
        'rest_framework.throttling.AnonRateThrottle',
        'rest_framework.throttling.UserRateThrottle'
    ],
    "DEFAULT_THROTTLE_RATES": {
        # https://www.django-rest-framework.org/api-guide/throttling/
        "anon": "100/second",
        "user": "1000/second",
    },
    "DEFAULT_RENDERER_CLASSES": [
        "rest_framework.renderers.JSONRenderer",
        "rest_framework.renderers.OpenAPIRenderer",
        "rest_framework.renderers.BrowsableAPIRenderer",
    ],
    "DEFAULT_FILTER_BACKENDS": [
        "django_filters.rest_framework.DjangoFilterBackend",
        "rest_framework.filters.OrderingFilter",
    ],
    "DEFAULT_SCHEMA_CLASS": "rest_framework.schemas.coreapi.AutoSchema",
    "DEFAULT_VERSIONING_CLASS": "rest_framework.versioning.URLPathVersioning",
    "DEFAULT_PAGINATION_CLASS": "rest_framework.pagination.PageNumberPagination",
    "PAGE_SIZE": 50,
}

################################################################################
# SWAGGER

SWAGGER_SETTINGS = {
    "VALIDATOR_URL": None,
    "USE_SESSION_AUTH": False,
    "SECURITY_DEFINITIONS": {
        "Bearer": {
            "type": "apiKey",
            "name": "Authorization",
            "in": "header",
        }
    },
}

################################################################################
# INSTALLED APPS

INSTALLED_APPS += [
    "django_filters",
    "drf_yasg",
    "rest_framework",
    "rest_framework.authtoken",
]
