from django.conf import settings
from django.conf.urls import (
    include,
    re_path,
)
from django.contrib import admin
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.views.decorators.http import last_modified
from django.views.generic import (
    RedirectView,
    TemplateView,
)
from django.views.i18n import JavaScriptCatalog
from django.views.static import serve

from mal2 import views  # noqa


################################################################################
# URLS

last_modified_date = timezone.now()

urlpatterns = [
    re_path(r"^$", RedirectView.as_view(pattern_name="mal2_db:signin", permanent=False), name="index"),

    # Documentation:
    # https://docs.djangoproject.com/en/2.2/topics/i18n/translation/#internationalization-in-javascript-code
    re_path(r"^jsi18n/", last_modified(lambda req, **kw: last_modified_date)(JavaScriptCatalog.as_view()), name="javascript_catalog"),

    re_path(r"^admin/", admin.site.urls),
    re_path(r"^", include("mal2_db.urls")),
    re_path(r"^robots\.txt$", TemplateView.as_view(template_name="robots.txt", content_type="text/plain"), name="robots"),

    # Toaster
    re_path(r"^toaster/$", views.ToasterView.as_view(), name="toaster"),

    # Secure media folder
    # re_path(r"^media/(?P<path_str>.*)$", views.SecureMediaView.as_view()),
]

################################################################################
# LOGIN AS

if "loginas" in settings.INSTALLED_APPS:
    urlpatterns += [
        re_path(r"^admin/", include("loginas.urls")),
    ]

################################################################################
# REST

if "rest_framework" in settings.INSTALLED_APPS:
    urlpatterns += [
        re_path(r"^api/", include("mal2_rest.urls")),
    ]

################################################################################
# ERROR

handler403 = views.NoPermissionView.get_rendered_view()
handler404 = views.PageNotFoundView.get_rendered_view()
handler500 = views.ServerErrorView.get_rendered_view()

################################################################################
# DEBUG

if settings.DEBUG:
    urlpatterns += [
        re_path(r"^404/$", TemplateView.as_view(template_name="404.html")),
        re_path(r"^403/$", TemplateView.as_view(template_name="403.html")),
        re_path(r"^500/$", TemplateView.as_view(template_name="500.html")),
        re_path(r"^plate/", include("django_spaghetti.urls")),
        # Unsecure media folder
        re_path(r"^media\/(?P<path>.*)$", serve, {
            "document_root": settings.MEDIA_ROOT,
            "show_indexes": False,
        }),
    ]

    urlpatterns += staticfiles_urlpatterns()

################################################################################
# ADMIN

admin_title = _("%(name)s Administration") % {
    "name": "mal2DB"
}

admin.site.site_header = admin_title
admin.site.site_title = admin_title
admin.site.index_title = admin_title
