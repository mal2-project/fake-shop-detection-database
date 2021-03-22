from django.contrib.auth.models import Group
from rest_framework.generics import GenericAPIView
from rest_framework.mixins import ListModelMixin

from mal2_db.models import User
from mal2_rest import (
    filters,
    serializers,
)


################################################################################
# USERS

class UsersListView(ListModelMixin, GenericAPIView):
    queryset = User.objects.all()
    serializer_class = serializers.UserSerializer

    filterset_class = filters.UsersFilter
    filterset_fields = "__all__"

    ordering = [
        "username",
        "first_name",
        "last_name",
    ]

    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)


################################################################################
# GROUPS

class GroupsListView(ListModelMixin, GenericAPIView):
    queryset = Group.objects.all()
    serializer_class = serializers.GroupSerializer

    filterset_fields = "__all__"

    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)
