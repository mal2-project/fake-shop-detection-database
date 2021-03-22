import re

from django.core.exceptions import (
    ImproperlyConfigured,
    ValidationError,
)
from django.db.models.query import QuerySet
from django.forms import (
    forms,
    models,
)
from django.utils.translation import (
    gettext_lazy as _,
    ngettext,
)

from mal2.utils import get_truth


################################################################################
# MIXINS

class GridFormMixin(object):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.grid = True
        self.init_grid()

    @property
    def grid_data(self):
        return {}

    def init_grid(self):
        for field_name in self.fields:
            grid = self.grid_data.get(field_name, "col-12")

            if isinstance(grid, tuple):
                field_grid = grid[0]
                multi_field_grid = grid[1]
            else:
                field_grid = grid
                multi_field_grid = []

            multi_widget = getattr(
                self.fields[field_name].widget, "widgets", []
            )

            for index, widget in enumerate(multi_widget):
                if index < len(multi_field_grid):
                    widget.attrs["data-col"] = multi_field_grid[index]
                else:
                    widget.attrs["data-col"] = "col"

            self.fields[field_name].grid = field_grid


class FieldDependenciesMixin(object):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self._requirements = {
            field_name: self.fields[field_name].required for field_name in self.fields
        }

        self._hidden_fields = self.field_dependencies_data.get("hidden", [])

        if self._hidden_fields:
            self._hide_field_dependencies()

        if self.initial:
            self._check_dependencies(self.initial)

    @property
    def field_dependencies_data(self):
        return {}

    @property
    def requirements(self):
        return self._requirements

    def _hide_field_dependencies(self):
        for field_name in self.fields:
            if field_name in self._hidden_fields:
                attrs = getattr(self.fields[field_name], "attrs", {})
                attrs["data-field-hidden"] = True
                self.fields[field_name].attrs = attrs

                classes = getattr(self.fields[field_name], "classes", [])
                classes.append("d-none")
                self.fields[field_name].classes = classes

    def _check_dependencies(self, field_data):
        for if_statements in self.field_dependencies_data.get("if_statements", []):
            if_field = field_data.get(if_statements["field"], None)

            if if_field is None:
                # empty hidden fields if field ist empty
                field_data = self._empty_hidden_fields(field_data, if_statements)
            else:
                operator_type = if_statements.get("operator", None)
                if_value = if_statements["if"]

                if isinstance(if_value, bool):
                    if if_value and if_field:
                        if isinstance(self._errors, dict):
                            self._update_error_messages(field_data, if_statements)
                        else:
                            self._update_required_fields(field_data, if_statements)
                else:
                    if isinstance(if_field, QuerySet):
                        # ModelMultipleChoiceField are querysets!
                        # Convert queryset to list and all values to strings
                        if_field = list(
                            map(str, if_field.values_list(flat=True))
                        )

                    if isinstance(if_field, list):
                        # Default operator for choice fields (select, checkbox, etc.)
                        operator_type = "in"

                        # Convert list if items are models
                        # Use always the primary key from model
                        if_field = [
                            item if isinstance(item, str) else str(item.pk) for item in if_field
                        ]

                    elif not operator_type:
                        # Default operator if not set
                        operator_type = "=="

                    # Input values are always strings!
                    # For comparison convert string (if it is a number) to a float
                    if isinstance(if_field, str):
                        if if_field.isdigit():
                            if_field = float(if_field)
                            if_value = float(if_value)

                    if get_truth(if_field, operator_type, if_value):
                        if isinstance(self._errors, dict):
                            self._update_error_messages(field_data, if_statements)
                        else:
                            self._update_required_fields(field_data, if_statements)
                    else:
                        # empty hidden fields if field dependency not fulfilled
                        field_data = self._empty_hidden_fields(field_data, if_statements)

        return field_data

    def _update_required_fields(self, field_data, if_statements):
        for then in if_statements["then"]:
            then_field = then["field"]
            required = then["required"]

            if then_field in self._hidden_fields:
                classes = getattr(self.fields[then_field], "classes", [])
                classes.remove("d-none")

            if required:
                if field_data.get(then_field):
                    self.fields[then_field].required = True
            else:
                self.fields[then_field].required = False

    def _update_error_messages(self, field_data, if_statements):
        for then in if_statements["then"]:
            then_field = then["field"]
            required = then["required"]

            if required:
                if then_field not in self._errors:
                    if not field_data.get(then_field):
                        self._errors[then_field] = self.error_class(
                            [self.fields[then_field].error_messages["required"]]
                        )

                self._requirements[then_field] = True
            else:
                validation_errors = []
                field_errors = self._errors.get(then_field, None)

                if field_errors:
                    for error in field_errors.as_data():
                        if error.code != "required":
                            validation_errors.append(error)

                    self._errors[then_field] = self.error_class(validation_errors)

                self._requirements[then_field] = False

    def _empty_hidden_fields(self, field_data, if_statements):
        hidden_fields = self.field_dependencies_data.get("hidden", None)

        if not hidden_fields:
            return field_data

        for then in if_statements["then"]:
            then_field = then["field"]

            if then_field in hidden_fields:
                field_data[then_field] = None

        return field_data

    def clean(self):
        cleaned_data = super().clean()
        cleaned_data = self._check_dependencies(cleaned_data)

        return cleaned_data


class BaseFormMixin(GridFormMixin, FieldDependenciesMixin):
    def __init__(self, *args, **kwargs):
        self.submit = kwargs.pop("submit", False)
        self.request = kwargs.pop("request", False)

        super().__init__(*args, **kwargs)

        if not self.prefix:
            self.prefix = self.get_default_prefix

        self._set_aria_description()
        self._show_errors()

    @property
    def get_default_prefix(self):
        prefix = re.sub(
            r"(?<!^)(?=[A-Z])", "",
            self.__class__.__name__
        ).lower()

        return prefix

    def _set_aria_description(self):
        for field_name in self.fields:
            aria_describedby = None

            field = self.fields[field_name]
            help_text = field.help_text

            group_prepend = getattr(field, "group_prepend", None)
            group_append = getattr(field, "group_append", None)

            if help_text:
                aria_describedby = "%s_%s" % (
                    field_name,
                    "help_text",
                )

            if group_prepend or group_append:
                aria_describedby = "%s%s_%s" % (
                    aria_describedby and "%s " % aria_describedby or "",
                    field_name,
                    "group",
                )

            if aria_describedby:
                field.widget.attrs.update({
                    "aria-describedby": aria_describedby
                })

    def _show_errors(self):
        for field_name in self.errors:
            field = self.fields.get(field_name, None)

            if field:
                attrs = field.widget.attrs
                classes = attrs.get("class", "")
                attrs["class"] = "is-invalid"

                if classes:
                    attrs["class"] = "%s %s" % (attrs["class"], classes)


################################################################################
# FORM


class ModelForm(BaseFormMixin, models.ModelForm):
    """
    Extends ``models.ModelForm`` with support for CSS grid classes
    and JavaScript form validation
    """

    pass


class Form(BaseFormMixin, forms.Form):
    """
    Extends ``forms.Form`` with support for CSS grid classes
    and JavaScript form validation
    """

    pass


################################################################################
# FIELDSET

class Fieldset(object):
    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)

    def __iter__(self):
        for field in self.fields:
            yield field


class BaseFieldsetMixin(BaseFormMixin):
    @property
    def fieldsets_data(self):
        return None

    def _hide_fieldset(self, fieldset_data):
        if fieldset_data.get("hidden"):
            attrs = fieldset_data.get("attrs", {})
            attrs["data-fieldset-hidden"] = True
            fieldset_data["attrs"] = attrs

            classes = fieldset_data.get("classes", [])
            classes.append("d-none")
            fieldset_data["classes"] = classes

        return fieldset_data

    def _fieldsets(self, fieldsets_data=None):
        if not fieldsets_data:
            fieldsets_data = self.fieldsets_data

        for data in fieldsets_data:
            fields = ()
            sub_fieldsets_data = data[1].pop("fieldsets", None)

            for field_name in data[1].get("fields", ()):
                field = self[field_name]

                if not field.is_hidden:
                    fields = fields + (field,)

            fieldset_data = {
                "title": data[0],
                "fields": fields,
            }

            if sub_fieldsets_data:
                fieldset_data.update({
                    "fieldsets": self._fieldsets(
                        fieldsets_data=sub_fieldsets_data,
                    )
                })

            data[1].pop("fields", None)
            fieldset_data.update(data[1])

            fieldset_data = self._hide_fieldset(fieldset_data)

            yield Fieldset(**fieldset_data)


class FieldsetMixin(BaseFieldsetMixin):
    """
    Adds fieldset support to ``catch_client.forms.Form`` and ``catch_client.forms.ModelForm``.

    Examples:
        >>> class ExampleForm(ModelFieldsetMixin):
        >>>     input_1 = forms.FileField()
        >>>     input_2 = forms.FileField()
        >>>     input_3 = forms.FileField()
        >>>
        >>>     class Meta:
        >>>         fields = "__all__"
        >>>
        >>>     @property
        >>>     def fieldsets_data(self):
        >>>         return [
        >>>             ("Fieldset", {
        >>>                 "classes": ["field-input", ],
        >>>                 "text": "A fieldset text",
        >>>                 "attrs": {
        >>>                   "data-tab": "",
        >>>                 },
        >>>                 "fields": [
        >>>                     "input_1",
        >>>                     "input_2",
        >>>                 ],
        >>>                 "fieldsets": [
        >>>                     ("Nested fieldset", {
        >>>                         "classes": ["field-input", ],
        >>>                         "text": "A fieldset text",
        >>>                         "attrs": {
        >>>                           "data-tab": "",
        >>>                         },
        >>>                         "fields": [
        >>>                             "input_1",
        >>>                             "input_2",
        >>>                         ],
        >>>                     }),
        >>>                 ],
        >>>             }),
        >>>             (None, {
        >>>                 "fields": [
        >>>                     "input_3",
        >>>                 ],
        >>>             }),
        >>>         ]
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if not self.fieldsets_data:
            raise ImproperlyConfigured(
                "%s requires an implementation of 'fieldsets_data()'" % self.__class__.__name__
            )

    @property
    def fieldsets(self):
        return self._fieldsets()


class FieldsetModelForm(FieldsetMixin, ModelForm):
    """A helper class for ``FieldsetMixin``"""

    pass


class FieldsetForm(FieldsetMixin, Form):
    """A helper class for ``FieldsetMixin``"""

    pass


################################################################################
# FORM WIZARD

class FormWizardMixin(BaseFieldsetMixin):
    """
    Adds form wizard support to ``catch_client.forms.Form``
    and ``catch_client.forms.ModelForm``.

    Examples:
        >>> class ExampleForm(FormWizardModelForm):
        >>>     input_1 = forms.FileField()
        >>>     input_2 = forms.FileField()
        >>>     input_3 = forms.FileField()
        >>>
        >>>     class Meta:
        >>>         fields = "__all__"
        >>>
        >>>     @property
        >>>     def wizard(self):
        >>>         return = [
        >>>             {
        >>>                 "text": _("Step 1"),
        >>>                 "fieldsets": [
        >>>                     ("Title 1", {
        >>>                         "fields": [
        >>>                             "input_1",
        >>>                             "input_2",
        >>>                         ],
        >>>                     }),
        >>>                 ],
        >>>             },
        >>>             {
        >>>                 "text": _("Step 2"),
        >>>                 "fieldsets": [
        >>>                     ("Title 2", {
        >>>                         "fields": [
        >>>                             "input_3",
        >>>                         ],
        >>>                     }),
        >>>                 ],
        >>>             },
        >>>         )
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if not self.wizard_data:
            raise ImproperlyConfigured(
                "%s requires an implementation of 'wizard_data()'" % self.__class__.__name__
            )

    @property
    def wizard_data(self):
        return None

    @property
    def wizard(self):
        for data in self.wizard_data:
            yield {
                "classes": data.get("classes"),
                "text": data.get("text"),
                "fieldsets": self._fieldsets(
                    fieldsets_data=data.get("fieldsets")
                ),
            }

    @property
    def steps_info(self):
        return {
            "steps": self._steps(),
            "steps_counter": len(self.wizard_data),
        }

    def _steps(self):
        for index, step in enumerate(self.wizard_data):
            text = step.get("text", None)

            yield {
                "step": index + 1,
                "text": text,
            }


class FormWizardModelForm(FormWizardMixin, ModelForm):
    """A helper class for ``FormWizardMixin``"""

    pass


class FormWizardForm(FormWizardMixin, Form):
    """A helper class for ``FormWizardMixin``"""

    pass


################################################################################
# INLINE FORM SET

class BaseInlineFormSet(models.BaseInlineFormSet):
    help_text = None

    @classmethod
    def get_default_prefix(cls):
        prefix = re.sub(
            r"(?<!^)(?=[A-Z])", "",
            cls.__name__
        ).lower()

        prefix = "%s-%s" % (prefix, super().get_default_prefix())

        return prefix

    def save_existing(self, form, instance, commit=True):
        """Save and return an existing model instance for the given form."""

        all_values_are_none = all(
            value is None for value in form.cleaned_data.values()
        )

        if all_values_are_none:
            # Delete empty entries from database
            self.delete_existing(form.instance)
        else:
            return form.save(commit=commit)

    def full_clean(self):
        self._errors = []
        self._non_form_errors = self.error_class()

        if not self.is_bound:
            return

        counter = 0

        for i in range(0, self.total_form_count()):
            form = self.forms[i]
            form_errors = form.errors

            if self.can_delete and self._should_delete_form(form):
                continue

            all_values_are_none = all(
                value is None for value in form.cleaned_data.values()
            )

            if len(form.cleaned_data) > 0 and not all_values_are_none:
                counter += 1

            self._errors.append(form_errors)

        try:
            if self.validate_max and counter > self.max_num:
                raise ValidationError(ngettext(
                    "A maximum of %d entry is allowed!",
                    "A maximum of %d entries are allowed!", self.max_num) % self.max_num,
                    code="too_many_forms",
                )

            if self.validate_min and counter < self.min_num:
                raise ValidationError(ngettext(
                    "At least %d entry is required!",
                    "At least %d entries are required!", self.min_num) % self.min_num,
                    code="too_few_forms",
                )

            self.clean()
        except ValidationError as e:
            self._non_form_errors = self.error_class(e.error_list)

    def clean(self):
        if any(self.errors):
            # Don't bother validating the formset unless each form is valid on its own
            return

        result_urls = []

        for form in self.forms:
            if self.can_delete and self._should_delete_form(form):
                continue

            result_url = str(form.cleaned_data)

            if result_url in result_urls and not all(value is None for value in form.cleaned_data.values()):
                raise ValidationError(
                    _("Duplicate entries were found!"),
                    code="duplicate_forms"
                )

            if len(form.cleaned_data) > 0:
                result_urls.append(result_url)
