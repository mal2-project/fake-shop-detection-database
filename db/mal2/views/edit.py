import logging

from django.http import JsonResponse
from django.utils.translation import gettext_lazy as _
from django.views.generic.edit import (
    FormView,
    CreateView,
    DeleteView,
    UpdateView,
)

from mal2.views.toaster import ToasterMixin


################################################################################
# LOGGER

logger = logging.getLogger(__name__)


################################################################################
# AJAX FORM VIEW

class AjaxFormView(ToasterMixin, FormView):
    formsets_data = []

    @property
    def error_message(self):
        return None

    @property
    def success_message(self):
        return None

    def dispatch(self, request, *args, **kwargs):
        self.submit = request.POST.get("submit", False)

        if self.submit:
            self.submit = True

        return super().dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        form = self.get_form()
        formset_data = self.get_formsets_data(data=request.POST)

        extra_errors = {}
        is_valid = True

        for item in formset_data:
            formset = item["formset_factory"]

            if not formset.is_valid():
                is_valid = False

                for index, errors in enumerate(formset.errors):
                    for field_name, error in errors.items():
                        prefix = "%s-%s-%s" % (
                            formset.prefix, index, field_name
                        )

                        extra_errors.update({
                            prefix: error
                        })

                if len(extra_errors) == 0:
                    extra_errors.update({
                        formset.prefix: formset.non_form_errors()
                    })

        if not form.is_valid():
            is_valid = False

        if self.submit and is_valid:
            return self.form_valid(form)

        return self.form_invalid(form, extra_errors)

    def form_valid(self, form, **kwargs):
        """
        If the form is valid, return a JSON response
        for the JavaScript toaster.
        """

        self.object = form.save(**kwargs)

        formset_data = self.get_formsets_data(
            data=self.request.POST,
            instance=self.object
        )

        for item in formset_data:
            formset = item["formset_factory"]

            if formset.has_changed():
                formset.save()

        context = {
            "submit": "success",
        }

        if self.success_message:
            context.update({
                "toaster": self.get_toaster(
                    request=self.request,
                    text=self.object and self.success_message or self.error_message,
                    success=self.object and True or False,
                ),
            })

        context.update({
            **(self.extra_context or {})
        })

        return JsonResponse(context)

    def form_invalid(self, form, extra_errors=None):
        """
        If the form is invalid, return a JSON response
        for the JavaScript form validation.
        """

        errors = form.errors
        formatted_errors = {}

        if extra_errors:
            errors.update(extra_errors)

        for field in errors:
            error_list = errors[field].as_ul()

            if "__all__" in field:
                formatted_errors["__all__"] = error_list
            else:
                formatted_errors[field] = error_list

        context = {
            "errors": formatted_errors,
            "requirements": form.requirements,
            "submit": "error",
        }

        return JsonResponse(context)

    def get_formsets_data(self, data=None, instance=None):
        return self.formsets_data

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()

        kwargs.update({
            "submit": self.submit,
            "request": self.request,
        })

        return kwargs

    def get_context_data(self, **kwargs):
        kwargs["formsets_data"] = self._get_formsets_data()

        return super().get_context_data(**kwargs)

    def _get_formsets_data(self):
        formsets = self.get_formsets_data(
            instance=getattr(self, "object", None)
        )

        formset_forms = []

        if formsets:
            for formset in formsets:
                formset_forms.append(
                    (formset["after_field"], formset["formset_factory"])
                )

        return formset_forms


################################################################################
# AJAX ADD VIEW

class AjaxAddView(AjaxFormView, CreateView):
    pk_url_kwarg = "pk"

    @property
    def success_message(self):
        """
        Return success message for JavaScript toaster
        """

        return _("%(verbose_name)s \"%(name)s\" has been added!") % {
            "verbose_name": self.model._meta.verbose_name,
            "name": self.object,
        }


################################################################################
# AJAX DELETE VIEW

class AjaxDeleteView(ToasterMixin, DeleteView):
    pk_url_kwarg = "pk"

    @property
    def error_message(self):
        """
        Return error message for JavaScript toaster
        """

        return _("%(verbose_name)s does not exist!") % {
            "verbose_name": self.model._meta.verbose_name,
        }

    @property
    def success_message(self):
        """
        Return success message for JavaScript toaster
        """

        return _("%(verbose_name)s \"%(name)s\" was deleted!") % {
            "verbose_name": self.model._meta.verbose_name,
            "name": self.object,
        }

    def get(self, request, *args, **kwargs):
        """
        Return a rendered template or a JSON object for the JavaScript toaster
        if `self.object` is empty.
        """

        self.object = self.get_object()

        if not self.object:
            context = {
                "toaster": self.get_toaster(
                    request=self.request,
                    text=self.error_message,
                    success=False,
                ),
                "submit": "error",
            }

            return JsonResponse(context)

        context = self.get_context_data(**kwargs)

        context.update({
            "instance": self.object,
        })

        return self.render_to_response(context)

    def post(self, request, *args, **kwargs):
        """
        Return a JSON object for the JavaScript toaster
        """
        submit = request.POST.get("submit", False)
        context = {}

        if submit:
            self.object = self.get_object()

            context = {
                "toaster": self.get_toaster(
                    request=self.request,
                    text=self.success_message,
                    success=True,
                ),
                "submit": "success",
            }

            self.delete_object()

            context.update({
                **(self.extra_context or {})
            })

        return JsonResponse(context)

    def delete_object(self):
        """
        Delete a model.
        """

        self.object.delete()


################################################################################
# AJAX EDIT VIEW

class AjaxEditView(AjaxFormView, UpdateView):
    pk_url_kwarg = "pk"

    @property
    def error_message(self):
        """
        Return error message for JavaScript toaster
        """

        return _("%(verbose_name)s does not exist!") % {
            "verbose_name": self.model._meta.verbose_name,
        }

    @property
    def success_message(self):
        """
        Return success message for JavaScript toaster
        """

        return _("%(verbose_name)s \"%(name)s\" has been updated!") % {
            "verbose_name": self.model._meta.verbose_name,
            "name": self.object,
        }

    def dispatch(self, request, *args, **kwargs):
        self.object = self.get_object()

        return super().dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        if not self.object:
            context = {
                "toaster": self.get_toaster(
                    request=self.request,
                    text=self.error_message,
                    success=False,
                ),
                "submit": "error",
            }

            return JsonResponse(context)

        context = self.get_context_data(**kwargs)

        context.update({
            "instance": self.object,
        })

        return self.render_to_response(context)
