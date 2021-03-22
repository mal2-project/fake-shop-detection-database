import django_filters

from mal2_db import models


################################################################################
# WEBSITES

class AllWebsitesFilter(django_filters.FilterSet):
    url = django_filters.CharFilter(lookup_expr="icontains")

    class Meta:
        model = models.Website
        fields = ["url", ]


################################################################################
# FAKE SHOP DB

class FakeShopDBFilter(django_filters.FilterSet):
    url = django_filters.CharFilter(lookup_expr="icontains")

    class Meta:
        model = models.mal2FakeShopDB

        fields = [
            "url",
            "website_id",
        ]


################################################################################
# BRAND COUNTETFEITER DB

class BrandCounterfeiterDBFilter(django_filters.FilterSet):
    url = django_filters.CharFilter(lookup_expr="icontains")

    class Meta:
        model = models.mal2CounterfeitersDB

        fields = [
            "url",
            "website_id",
        ]
