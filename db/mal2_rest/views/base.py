from rest_framework.generics import GenericAPIView
from rest_framework.mixins import (
    CreateModelMixin,
    ListModelMixin,
    RetrieveModelMixin,
)

from mal2_db import models
from mal2_rest import (
    filters,
    serializers,
)
from mal2_rest.permissions import AllowPostMethod


################################################################################
# WEBSITE RISK SCORE

class WebsiteRiskScoreMixin(object):
    queryset = models.WebsiteRiskScore.objects.all()
    serializer_class = serializers.WebsiteRiskScoreSerializer


class WebsiteRiskScoreListView(WebsiteRiskScoreMixin, ListModelMixin, GenericAPIView):
    """
    get:
    Return a list of all website risk scores.
    """

    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)


class WebsiteRiskScoreDetailView(WebsiteRiskScoreMixin, RetrieveModelMixin, GenericAPIView):
    """
    get:
    Return website risk score informations.
    """

    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)


################################################################################
# WEBSITE REPORTER

class WebsiteReporterMixin(object):
    queryset = models.WebsiteReportedBy.objects.all()
    serializer_class = serializers.WebsiteReporterSerializer


class WebsiteReporterListView(WebsiteReporterMixin, ListModelMixin, GenericAPIView):
    """
    get:
    Return a list of all website reporters.
    """

    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)


class WebsiteReporterDetailView(WebsiteReporterMixin, RetrieveModelMixin, GenericAPIView):
    """
    get:
    Return website reporter informations.
    """

    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)


################################################################################
# WEBSITE TYPE

class WebsiteTypeMixin(object):
    queryset = models.WebsiteType.objects.all()
    serializer_class = serializers.WebsiteTypeSerializer


class WebsiteTypeListView(WebsiteTypeMixin, ListModelMixin, GenericAPIView):
    """
    get:
    Return a list of all website types.
    """

    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)


class WebsiteTypeDetailView(WebsiteTypeMixin, RetrieveModelMixin, GenericAPIView):
    """
    get:
    Return website type informations.
    """

    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)


################################################################################
# ALL WEBSITES

class WebsitesMixin(object):
    queryset = models.Website.objects.all()
    serializer_class = serializers.WebsiteSerializer

    ordering = [
        "-id",
        "url",
    ]


class WebsitesListMixin(WebsitesMixin):
    filterset_class = filters.AllWebsitesFilter
    filterset_fields = ["url", "website_type", "website_category", ]


class AllWebsitesListView(WebsitesListMixin, CreateModelMixin, ListModelMixin, GenericAPIView):
    """
    get:
    Return a list of all reported websites.

    post:
    Report a possible fraud website.
    """

    permission_classes = [
        AllowPostMethod,
    ]

    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)


class AllWebsitesDetailView(WebsitesMixin, RetrieveModelMixin, GenericAPIView):
    """
    get:
    Return website informations.
    """

    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)


################################################################################
# WEBSITES TO CHECK

class WebsitesToCheckListView(WebsitesListMixin, ListModelMixin, GenericAPIView):
    """
    get:
    Return a list of websites to check.
    """

    queryset = models.Website.objects.to_check()

    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)


class WebsitesToCheckDetailView(AllWebsitesDetailView):
    """
    get:
    Return website informations.
    """

    queryset = models.Website.objects.to_check()


################################################################################
# WEBSITES NO VERIFICATION REQUIRED

class WebsitesNoVerificationRequiredListView(WebsitesListMixin, ListModelMixin, GenericAPIView):
    """
    get:
    Return a list of websites that do not require verification.
    """

    queryset = models.Website.objects.without_verification()

    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)


class WebsitesNoVerificationRequiredDetailView(AllWebsitesDetailView):
    """
    get:
    Return website informations.
    """

    queryset = models.Website.objects.without_verification()


################################################################################
# WEBSITES FAKE SHOP

class WebsitesFakeShopListView(WebsitesListMixin, ListModelMixin, GenericAPIView):
    """
    get:
    Return a list of websites that are fakeshops.
    """

    queryset = models.Website.objects.is_fake_shop()

    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)


class WebsitesFakeShopDetailView(AllWebsitesDetailView):
    """
    get:
    Return website informations.
    """

    queryset = models.Website.objects.is_fake_shop()


################################################################################
# WEBSITES BRAND COUNTERFEITER

class WebsitesBrandCounterfeiterListView(WebsitesListMixin, ListModelMixin, GenericAPIView):
    """
    get:
    Return a list of websites that are brand counterfeiters.
    """

    queryset = models.Website.objects.is_brand_counterfeiter()

    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)


class WebsitesBrandCounterfeiterDetailView(AllWebsitesDetailView):
    """
    get:
    Return brand counterfeiter informations.
    """

    queryset = models.Website.objects.is_brand_counterfeiter()


################################################################################
# FAKE SHOP DB

class FakeShopDBMixin(object):
    queryset = models.mal2FakeShopDB.objects.all()
    serializer_class = serializers.FakeShopDBSerializer

    ordering = [
        "-id",
        "url",
    ]


class FakeShopDBListView(FakeShopDBMixin, ListModelMixin, GenericAPIView):
    """
    get:
    Return a list of fakeshops.
    """

    filterset_class = filters.FakeShopDBFilter
    filterset_fields = ["url", ]

    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)


class FakeShopDBDetailView(FakeShopDBMixin, RetrieveModelMixin, GenericAPIView):
    """
    get:
    Return fake shop informations.
    """

    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)


################################################################################
# BRAND COUNTETFEITER DB

class BrandCounterfeiterDBMixin(object):

    queryset = models.mal2CounterfeitersDB.objects.all()
    serializer_class = serializers.BrandCounterfeiterDBSerializer

    ordering = [
        "-id",
        "url",
    ]


class BrandCounterfeiterDBListView(BrandCounterfeiterDBMixin, ListModelMixin, GenericAPIView):
    """
    get:
    Return a list of brand counterfeiters.
    """

    filterset_class = filters.BrandCounterfeiterDBFilter
    filterset_fields = ["url", ]

    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)


class BrandCounterfeiterDBDetailView(BrandCounterfeiterDBMixin, RetrieveModelMixin, GenericAPIView):
    """
    get:
    Return brand counterfeiter informations.
    """

    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)


################################################################################
# CHECKED - NO FAKE

class WebsitesNoFakeListView(WebsitesListMixin, ListModelMixin, GenericAPIView):
    """
    get:
    Return a list of websites that are not fake.
    """

    queryset = models.Website.objects.is_no_fake()

    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)


class WebsitesNoFakeDetailView(AllWebsitesDetailView):
    """
    get:
    Return website informations.
    """

    queryset = models.Website.objects.is_no_fake()
