from django.contrib import admin
from django.contrib.auth.models import Permission


################################################################################
# PERMISSIONS

@admin.register(Permission)
class PermissionAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "content_type",
        "codename",
    )

    search_fields = (
        "name",
        "codename",
    )
