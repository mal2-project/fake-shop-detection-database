import logging

from django.conf import settings
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.tokens import default_token_generator
from django.contrib.auth.views import (
    INTERNAL_RESET_SESSION_TOKEN,
    LoginView,
    PasswordResetConfirmView,
    PasswordResetDoneView,
    PasswordResetView,
)
from django.core.exceptions import ValidationError
from django.http import (
    HttpResponseNotFound,
    JsonResponse,
)
from django.shortcuts import resolve_url
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.utils.http import urlsafe_base64_decode
from django.utils.translation import gettext_lazy as _
from django.views.decorators.cache import never_cache
from django.views.decorators.debug import sensitive_post_parameters
from django.views.generic import TemplateView

from mal2.views.edit import AjaxFormView
from mal2_db.forms.auth import (
    SignInForm,
    PasswordChangeForm,
    PasswordResetForm,
    PasswordResetConfirmForm,
    SignUpForm,
)
from mal2_db.models import User


################################################################################
# LOGGER

logger = logging.getLogger(__name__)


################################################################################
# MIXINS

class SignUpMixin(object):
    def get_user(self, uidb64):
        try:
            uid = urlsafe_base64_decode(uidb64).decode()
            user = User._default_manager.get(pk=uid)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist, ValidationError):
            user = None

        return user


################################################################################
# SIGN IN

class SignInView(LoginView):
    form_class = SignInForm
    template_name = "mal2_users/registration/signin.html"
    redirect_authenticated_user = True


################################################################################
# SIGN UP

class SignUpView(AjaxFormView):
    form_class = SignUpForm

    email_template_name = "mal2_users/registration/email/signup.html"
    subject_template_name = "mal2_users/registration/email/signup_subject.txt"

    template_name = "mal2_users/registration/signup.html"

    extra_context = {
        "redirect": reverse_lazy("mal2_db:signup_done")
    }

    @method_decorator(never_cache)
    @method_decorator(sensitive_post_parameters())
    def dispatch(self, request, *args, **kwargs):
        if not settings.CAN_SIGNUP:
            return HttpResponseNotFound()

        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        opts = {
            "request": self.request,
            "email_template_name": self.email_template_name,
            "subject_template_name": self.subject_template_name,
            "use_https": self.request.is_secure(),
        }

        return super().form_valid(form, **opts)


class SignUpDoneView(TemplateView):
    template_name = "mal2_users/registration/signup_done.html"

    def dispatch(self, request, *args, **kwargs):
        if not settings.CAN_SIGNUP or request.user.is_authenticated:
            return HttpResponseNotFound()

        return super().dispatch(request, *args, **kwargs)


################################################################################
# EMAIL VERIFICATION

class EmailVerificationView(SignUpMixin, TemplateView):
    template_name = "mal2_users/registration/email_verification.html"

    @method_decorator(never_cache)
    def get(self, request, *args, **kwargs):
        self.validlink = False

        verify = request.GET.get("verify", None)

        username = self.get_user(kwargs["uidb64"])
        token = kwargs["token"]

        user = User.objects.filter(username=username).first()

        if user and not user.is_active:
            if verify and default_token_generator.check_token(username, token):
                user.is_active = True
                user.save()

            self.validlink = True

        return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context.update({
            "token": kwargs["token"],
            "uid": kwargs["uidb64"],
            "validlink": self.validlink,
        })

        return context


################################################################################
# PASSWORD RESET

class PasswordResetView(PasswordResetView, AjaxFormView):
    form_class = PasswordResetForm
    email_template_name = "mal2_users/registration/email/password_reset.html"
    html_email_template_name = "mal2_users/registration/email/password_reset.html"
    subject_template_name = "mal2_users/registration/email/password_reset_subject.txt"
    template_name = "mal2_users/registration/password_reset.html"

    extra_context = {
        "redirect": reverse_lazy("mal2_db:password_reset_done")
    }

    def form_valid(self, form):
        opts = {
            "use_https": self.request.is_secure(),
            "token_generator": self.token_generator,
            "from_email": self.from_email,
            "email_template_name": self.email_template_name,
            "subject_template_name": self.subject_template_name,
            "request": self.request,
            "html_email_template_name": self.html_email_template_name,
            "extra_email_context": self.extra_email_context,
        }

        form.save(**opts)

        context = {
            "submit": "success",
        }

        if self.extra_context is not None:
            context.update(self.extra_context)

        return JsonResponse(context)


################################################################################
# PASSWORD RESET DONE

class PasswordResetDoneView(PasswordResetDoneView):
    template_name = "mal2_users/registration/password_reset_done.html"


################################################################################
# PASSWORD RESET CONFIRM

class PasswordResetConfirmView(PasswordResetConfirmView, AjaxFormView):
    form_class = PasswordResetConfirmForm
    template_name = "mal2_users/registration/password_reset_confirm.html"

    extra_context = {
        "redirect": reverse_lazy("mal2_db:password_reset_complete")
    }

    def form_valid(self, form):
        form.save()

        del self.request.session[INTERNAL_RESET_SESSION_TOKEN]

        context = {
            "submit": "success",
        }

        context.update(self.extra_context)

        return JsonResponse(context)


################################################################################
# PASSWORD CHANGE

@method_decorator(never_cache, name="dispatch")
@method_decorator(sensitive_post_parameters(), name="dispatch")
class PasswordChangeView(LoginRequiredMixin, AjaxFormView):
    form_class = PasswordChangeForm
    template_name = "mal2_users/registration/dialog/password_change.html"
    success_message = _("Password change successful")

    def form_valid(self, form):
        update_session_auth_hash(self.request, form.user)

        self.extra_context = {
            "redirect": resolve_url(settings.LOGIN_URL)
        }

        return super().form_valid(form)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["user"] = self.request.user

        return kwargs
