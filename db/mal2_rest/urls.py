from django.conf.urls import (
    include,
    re_path,
)
from drf_yasg import openapi
from drf_yasg.views import get_schema_view

from mal2_rest import views


################################################################################
# URLS

schema_view = get_schema_view(
    openapi.Info(
        title="mal2DB API",
        default_version="v1",
    ),
    public=True,
)

urlpatterns = [
    re_path(r"^$", schema_view.with_ui("swagger", cache_timeout=0), name="swagger"),

    re_path(r"^auth/", include("rest_framework.urls", namespace="rest_framework")),
    re_path(r"^(?P<version>(v1))/token-auth/$", views.ObtainAuthToken.as_view()),

    re_path(r"^(?P<version>(v1))/user/$", views.UsersListView.as_view()),
    re_path(r"^(?P<version>(v1))/user/(?P<pk>\d+)$", views.UsersListView.as_view()),

    re_path(r"^(?P<version>(v1))/permission/group/$", views.GroupsListView.as_view()),
    re_path(r"^(?P<version>(v1))/permission/group/(?P<pk>\d+)$", views.GroupsListView.as_view()),

    re_path(r"^(?P<version>(v1))/website/$", views.AllWebsitesListView.as_view()),
    re_path(r"^(?P<version>(v1))/website/(?P<pk>\d+)$", views.AllWebsitesDetailView.as_view()),

    re_path(r"^(?P<version>(v1))/website/to_check/$", views.WebsitesToCheckListView.as_view()),
    re_path(r"^(?P<version>(v1))/website/to_check/(?P<pk>\d+)$", views.WebsitesToCheckDetailView.as_view()),

    re_path(r"^(?P<version>(v1))/website/no_verification_required/$", views.WebsitesNoVerificationRequiredListView.as_view()),
    re_path(r"^(?P<version>(v1))/website/no_verification_required/(?P<pk>\d+)$", views.WebsitesNoVerificationRequiredDetailView.as_view()),

    re_path(r"^(?P<version>(v1))/website/fake_shop/$", views.WebsitesFakeShopListView.as_view()),
    re_path(r"^(?P<version>(v1))/website/fake_shop/(?P<pk>\d+)$", views.WebsitesFakeShopDetailView.as_view()),

    re_path(r"^(?P<version>(v1))/website/brand_counterfeiter/$", views.WebsitesBrandCounterfeiterListView.as_view()),
    re_path(r"^(?P<version>(v1))/website/brand_counterfeiter/(?P<pk>\d+)$", views.WebsitesBrandCounterfeiterDetailView.as_view()),

    re_path(r"^(?P<version>(v1))/website/risk_score/$", views.WebsiteRiskScoreListView.as_view()),
    re_path(r"^(?P<version>(v1))/website/risk_score/(?P<pk>\d+)/$", views.WebsiteRiskScoreDetailView.as_view()),

    re_path(r"^(?P<version>(v1))/website/reporter/$", views.WebsiteReporterListView.as_view()),
    re_path(r"^(?P<version>(v1))/website/reporter/(?P<pk>\d+)/$", views.WebsiteReporterDetailView.as_view()),

    re_path(r"^(?P<version>(v1))/website/type/$", views.WebsiteTypeListView.as_view()),
    re_path(r"^(?P<version>(v1))/website/type/(?P<pk>\d+)/$", views.WebsiteTypeDetailView.as_view()),

    re_path(r"^(?P<version>(v1))/db/fake_shop/$", views.FakeShopDBListView.as_view()),
    re_path(r"^(?P<version>(v1))/db/fake_shop/(?P<pk>\d+)/$", views.FakeShopDBDetailView.as_view()),

    re_path(r"^(?P<version>(v1))/db/brand_counterfeiter/$", views.BrandCounterfeiterDBListView.as_view()),
    re_path(r"^(?P<version>(v1))/db/brand_counterfeiter/(?P<pk>\d+)/$", views.BrandCounterfeiterDBDetailView.as_view()),

    re_path(r"^(?P<version>(v1))/db/no_fake/$", views.WebsitesNoFakeListView.as_view()),
    re_path(r"^(?P<version>(v1))/db/no_fake/(?P<pk>\d+)/$", views.WebsitesNoFakeDetailView.as_view()),
]
