import logging

from django.conf import settings
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.http import Http404
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.utils.translation import gettext_lazy as _
from django.views.decorators.cache import never_cache
from django.views.decorators.debug import sensitive_post_parameters

from mal2.constants import OPTIONS_BOOLEAN
from mal2.views.data_table import (
    DataTableDataView,
    DataTableView,
)
from mal2.views.edit import (
    AjaxAddView,
    AjaxDeleteView,
    AjaxEditView,
    AjaxFormView,
)
from mal2_db.forms.user import (
    AddUserForm,
    EditUserForm,
    SetPasswordUserForm,
)
from mal2_db.models import User


################################################################################
# LOGGER

logger = logging.getLogger(__name__)


################################################################################
# USERS DATA TABLE MIXIN

class UsersDataTableMixin(object):
    def get_data_table(self):
        field_names = [
            "id",
            "username",
            "first_name",
            "last_name",
            "email",
            "date_joined",
            "is_superuser",
            "is_active",
        ]

        if "rest_framework" in settings.INSTALLED_APPS:
            field_names += ["auth_token__key"]

        return {
            "table": "users",
            "urls": {
                "defaults": {
                    "attrs": {
                        "data-modal-link": True,
                    },
                    "template": "data_table/link.html",
                },
                "data": reverse_lazy("mal2_db:users_data_table_data"),
                "add": {
                    "href": "mal2_db:add_user",
                    "permissions": [
                        "mal2_users.add_user",
                    ],
                    "text": _("Add user"),
                    "template": "data_table/add.html",
                },
                "item": [
                    {
                        "field_name": "edit",
                        "href": "mal2_db:edit_user",
                        "permissions": [
                            "mal2_users.change_user",
                        ],
                        "context": {
                            "svg": "pencil",
                            "text": _("Edit"),
                        },
                    },
                    {
                        "field_name": "set_user_password",
                        "href": "mal2_db:set_user_password",
                        "permissions": [
                            "mal2_users.change_user",
                        ],
                        "context": {
                            "svg": "shield-key",
                            "text": _("Set password"),
                        },
                    },
                    {
                        "field_name": "delete",
                        "href": "mal2_db:delete_user",
                        "permissions": [
                            "mal2_users.delete_user",
                        ],
                        "template": "mal2_users/data_table/delete_user.html",
                        "context": {
                            "icon_color": "danger",
                            "svg": "delete",
                            "text": _("Delete"),
                        },
                    },
                ],
            },
            "row_id": "id",
            "field_names": field_names,
            "field_hidden": [
            ],
            "field_labels": {
                "is_superuser": _("Admin"),
                "email": _("Email"),
            },
            "field_filters": {
                "regex_enabled": [
                ],
                "type": "collapse",
                # exclude is optional - it is possible to hide search fields for
                # specific columns (in collapse and columns mode)
                "exclude": [
                ],
                # default_classes is optional col for all columns
                # you can specify specific columns class inside "custom" with
                # "classes" --> if nothing is provided default is "col-12 col-md-3"
                "default_classes": "col-12 col-md-3",
                # custom is optional -
                # filters get automatically created by field_names above
                # custom can customize a type of a field and add options for
                # type select or customize col classes with "classes"
                "custom": {
                    "id": {
                        "type": "number",
                    },
                    "username": {
                        "type": "text",
                    },
                    "first_name": {
                        "type": "text",
                    },
                    "last_name": {
                        "type": "text",
                    },
                    "email": {
                        "type": "text",
                    },
                    "date_joined": {
                        "type": "date",
                    },
                    "is_superuser": {
                        "classes": "col-12 col-md-3",
                        "options": OPTIONS_BOOLEAN,
                        "type": "select",
                    },
                    "is_active": {
                        "options": OPTIONS_BOOLEAN,
                        "type": "select",
                    },
                },
            },
            "field_templates": {
                "email": "data_table/email.html",
                "is_superuser": "data_table/boolean.html",
                "is_active": "data_table/boolean.html",
                "date_joined": "data_table/datetime.html",
                "auth_token__key": "data_table/clipboard.html",
            },
            "field_classes": {
                "email": [
                    "text-nowrap",
                ],
            },
            "select_relations": [],
            "responsive_priorities": {
                "id": 9994,
                "username": 9990,
                "is_active": 9997,
                "is_superuser": 9996,
                "auth_token__key": 9995,
                "set_user_password": 9993,
                "edit": 9992,
                "delete": 9991,
            },
        }


################################################################################
# USERS DATA TABLE

class UsersDataTableView(PermissionRequiredMixin, UsersDataTableMixin, DataTableView):
    permission_required = "is_superuser"

    model = User
    template_name = "mal2_users/data_table/users.html"


class UsersDataTableDataView(PermissionRequiredMixin, UsersDataTableMixin, DataTableDataView):
    permission_required = "is_superuser"

    model = User


################################################################################
# ADD USER

@method_decorator(never_cache, name="dispatch")
@method_decorator(sensitive_post_parameters(), name="dispatch")
class AddUserView(PermissionRequiredMixin, AjaxAddView):
    permission_required = "mal2_users.add_user"

    template_name = "mal2_users/dialog/add_user.html"
    model = User

    form_class = AddUserForm

    extra_context = {
        "datatable": True,
    }


################################################################################
# DELETE USER

class DeleteUserView(PermissionRequiredMixin, AjaxDeleteView):
    permission_required = "mal2_users.delete_user"

    template_name = "mal2_users/dialog/delete_user.html"
    model = User

    extra_context = {
        "datatable": True,
    }

    def dispatch(self, request, *args, **kwargs):
        if self.request.user.id == int(kwargs.get("pk")):
            raise Http404()

        return super().dispatch(request, *args, **kwargs)


################################################################################
# EDIT USER

class EditUserView(PermissionRequiredMixin, AjaxEditView):
    permission_required = "mal2_users.change_user"

    template_name = "mal2_users/dialog/edit_user.html"
    model = User

    form_class = EditUserForm

    extra_context = {
        "datatable": True,
    }


################################################################################
# SET USER PASSWORD

@method_decorator(never_cache, name="dispatch")
@method_decorator(sensitive_post_parameters(), name="dispatch")
class SetPasswordUserView(PermissionRequiredMixin, AjaxFormView):
    permission_required = "mal2_users.change_user"

    template_name = "mal2_users/dialog/set_user_password.html"
    model = User

    form_class = SetPasswordUserForm
    pk_url_kwarg = "pk"

    extra_context = {
        "datatable": True,
    }

    @property
    def success_message(self):
        return _("Password for %(verbose_name)s \"%(name)s\" was set.") % {
            "verbose_name": self.model._meta.verbose_name,
            "name": self.object,
        }

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()

        kwargs["user"] = self.model.objects.get(
            id=self.kwargs.get(self.pk_url_kwarg)
        )

        return kwargs
