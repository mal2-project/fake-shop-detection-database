import logging

from django.contrib.auth import forms as auth_forms
from django.contrib.auth.password_validation import password_validators_help_texts
from django.contrib.auth.tokens import default_token_generator
from django.contrib.sites.shortcuts import get_current_site
from django.utils.encoding import force_bytes
from django.utils.html import (
    format_html,
    format_html_join,
)
from django.utils.http import urlsafe_base64_encode
from django.utils.translation import gettext_lazy as _

from mal2.forms import (
    BaseFormMixin,
    FieldsetMixin,
)
from mal2.utils import send_html_mail
from mal2_db.models import User


################################################################################
# LOGGER

logger = logging.getLogger(__name__)


################################################################################
# HELPERS

class UserFormMixin(object):
    def password_help_text(self):
        help_texts = password_validators_help_texts()
        help_items = format_html_join("", "<li>{}</li>", ((help_text,) for help_text in help_texts))

        return format_html("<ul class=\"list-styled\">{}</ul>", help_items) if help_items else ""


################################################################################
# SIGN IN

class SignInForm(BaseFormMixin, auth_forms.AuthenticationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields["username"].widget.attrs.update({
            "autocomplete": "username",
        })

        self.fields["password"].widget.attrs.update({
            "autocomplete": "current-password",
        })

    @property
    def grid_data(self):
        return {
            "username": "col-12 col-lg-6",
            "password": "col-12 col-lg-6",
        }


################################################################################
# SIGN UP

class SignUpForm(UserFormMixin, FieldsetMixin, auth_forms.UserCreationForm):
    class Meta:
        model = User

        exclude = (
            "password",
            "date_joined",
        )

        field_classes = {
            "username": auth_forms.UsernameField
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields["first_name"].widget.attrs.update({
            "autofocus": True,
        })

        self.fields["username"].widget.attrs.update({
            "autocomplete": "username",
            "autofocus": False,
        })

        self.fields["password1"].help_text = self.password_help_text()

        self.fields["password1"].widget.attrs.update({
            "autocomplete": "new-password",
        })

        self.fields["password2"].widget.attrs.update({
            "autocomplete": "new-password",
        })

        self.fields["password2"].label = _("Confirm password")

    @property
    def grid_data(self):
        return {
            "first_name": "col-12 col-sm-6 col-md-6 col-xl-4",
            "last_name": "col-12 col-sm-6 col-md-6 col-xl-4",
            "email": "col-12 col-xl-4",

            "username": "col-12 col-md-12 col-xl-4",
            "password1": "col-12 col-md-6 col-xl-4",
            "password2": "col-12 col-md-6 col-xl-4",
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
                    "password1",
                    "password2",
                ],
            }),
        ]

    def save(self, commit=True, **kwargs):
        user = super().save(commit=commit)
        user.is_active = False
        user.save()

        current_site = get_current_site(kwargs.get("request"))

        email_template_name = kwargs.get("email_template_name")
        subject_template_name = kwargs.get("subject_template_name")

        user_email = (user.email,)

        send_html_mail(
            subject_template_name,
            email_template_name,
            user_email,
            context={
                "domain": current_site.domain,
                "protocol": "https" if kwargs.get("use_https") else "http",
                "token": default_token_generator.make_token(user),
                "uid": urlsafe_base64_encode(force_bytes(user.pk)),
            }
        )

        return user


################################################################################
# PASSWORD RESET

class PasswordResetForm(BaseFormMixin, auth_forms.PasswordResetForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields["email"].label = _("Email")

    @property
    def grid_data(self):
        return {
            "email": "col-12",
        }


################################################################################
# PASSWORD RESET CONFIRM

class PasswordResetConfirmForm(BaseFormMixin, UserFormMixin, auth_forms.SetPasswordForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields["new_password1"].help_text = self.password_help_text()

        self.fields["new_password1"].label = _("New password")
        self.fields["new_password2"].label = _("Confirm new password")

    @property
    def grid_data(self):
        return {
            "new_password1": "col-6",
            "new_password2": "col-6",
        }


################################################################################
# PASSWORD CHANGE

class PasswordChangeForm(BaseFormMixin, UserFormMixin, auth_forms.PasswordChangeForm):
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
            "old_password": "col-12",
            "new_password1": "col-12 col-md-6",
            "new_password2": "col-12 col-md-6",
        }
