import django_filters

from mal2_db import models


################################################################################
# USERS

class UsersFilter(django_filters.FilterSet):
    username = django_filters.CharFilter(lookup_expr="icontains")

    class Meta:
        model = models.User
        fields = "__all__"
