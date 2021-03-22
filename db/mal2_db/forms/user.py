from django import forms
from django.contrib.auth import forms as auth_forms
from django.contrib.auth.models import Group
from django.utils.translation import gettext_lazy as _

from mal2.forms import (
    BaseFormMixin,
    FieldsetModelForm,
)
from mal2_db.forms.auth import UserFormMixin
from mal2_db.models import User


################################################################################
# ADD USER

class AddUserForm(UserFormMixin, FieldsetModelForm, auth_forms.UserCreationForm):
    groups = forms.ModelMultipleChoiceField(
        label=_("Groups"),
        queryset=Group.objects.all(),
        required=False,
    )

    class Meta:
        model = User

        fields = (
            "first_name",
            "last_name",
            "email",
            "username",
            "groups",
            "password1",
            "password2",
            "is_active",
            "is_superuser",
        )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields["first_name"].widget.attrs.update({
            "autofocus": True,
        })

        self.fields["username"].widget.attrs.update({
            "autocomplete": "username",
            "autofocus": True,
        })

        self.fields["password1"].help_text = self.password_help_text()

        self.fields["password1"].widget.attrs.update({
            "autocomplete": "new-password",
        })

        self.fields["password2"].widget.attrs.update({
            "autocomplete": "new-password",
        })

        self.fields["email"].label = _("Email")

    @property
    def grid_data(self):
        return {
            "first_name": "col-12 col-md-6",
            "last_name": "col-12 col-md-6",
            "email": "col-12 col-md-6",
            "username": "col-12 col-md-6",
            "groups": "col-12 col-md-6",
            "password1": "col-12 col-md-6",
            "password2": "col-12 col-md-6",
            "is_active": "col-12 col-md-6",
            "is_superuser": "col-12 col-md-6",
        }

    @property
    def fieldsets_data(self):
        return [
            (_("Contact details"), {
                "fields": [
                    "first_name",
                    "last_name",
                    "email",
                ],
            }),
            (_("Access data"), {
                "fields": [
                    "username",
                    "groups",
                    "password1",
                    "password2",
                ],
            }),
            (_("Access status"), {
                "fields": [
                    "is_active",
                    "is_superuser",
                ],
            }),
        ]

    def save(self, commit=True):
        cleaned_data = self.cleaned_data
        groups = cleaned_data.get("groups", [])

        instance = super().save()

        for group in groups:
            group.user_set.add(instance)

        return instance


################################################################################
# EDIT USER

class EditUserForm(UserFormMixin, FieldsetModelForm):
    groups = forms.ModelMultipleChoiceField(
        label=_("Groups"),
        queryset=Group.objects.all(),
        required=False,
    )

    class Meta:
        model = User

        fields = (
            "first_name",
            "last_name",
            "email",
            "username",
            "groups",
            "is_active",
            "is_superuser",
        )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields["first_name"].widget.attrs.update({
            "autofocus": True,
        })

        self.fields["email"].label = _("Email")

    @property
    def grid_data(self):
        return {
            "first_name": "col-12 col-md-6",
            "last_name": "col-12 col-md-6",
            "email": "col-12 col-md-6",
            "username": "col-12 col-md-6",
            "groups": "col-12 col-md-6",
            "is_active": "col-12 col-md-6",
            "is_superuser": "col-12 col-md-6",
        }

    @property
    def fieldsets_data(self):
        return [
            (_("Contact details"), {
                "fields": [
                    "first_name",
                    "last_name",
                    "email",
                ],
            }),
            (_("Access data"), {
                "fields": [
                    "username",
                    "groups",
                    "is_active",
                    "is_superuser",
                ],
            }),
        ]


################################################################################
# SET USER PASSWORD

class SetPasswordUserForm(BaseFormMixin, UserFormMixin, auth_forms.SetPasswordForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields["new_password1"].help_text = self.password_help_text()

        self.fields["new_password1"].widget.attrs.update({
            "autocomplete": "new-password",
        })

        self.fields["new_password2"].widget.attrs.update({
            "autocomplete": "new-password",
        })

        self.fields["new_password1"].label = _("New password")
        self.fields["new_password2"].label = _("Confirm new password")

    @property
    def grid_data(self):
        return {
            "new_password1": "col-12 col-md-6",
            "new_password2": "col-12 col-md-6",
        }
