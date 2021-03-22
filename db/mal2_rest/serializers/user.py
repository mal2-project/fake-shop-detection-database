from django.contrib.auth.models import Group
from rest_framework import serializers

from mal2_db.models import User


################################################################################
# USERS

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        exclude = ("user_permissions", "password", )


################################################################################
# GROUPS

class GroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = Group
        exclude = ("permissions", )
