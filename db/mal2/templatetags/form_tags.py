from django import (
    forms,
    template,
)
from phonenumber_field.widgets import PhoneNumberInternationalFallbackWidget

from mal2 import forms as mal2_forms


register = template.Library()


################################################################################
# FORM

@register.filter
def is_checkbox(field):
    return isinstance(field.field.widget, forms.CheckboxInput)


@register.filter
def is_multiple_checkbox(field):
    return isinstance(field.field.widget, forms.CheckboxSelectMultiple)


@register.filter
def is_radio(field):
    return isinstance(field.field.widget, forms.RadioSelect)


@register.filter
def is_file(field):
    return isinstance(field.field.widget, forms.FileInput)


@register.filter
def is_multiple_files(field):
    return isinstance(field.field.widget, forms.FileInput) and field.field.widget.attrs.get("multiple")


@register.filter
def is_range(field):
    return isinstance(field.field.widget, mal2_forms.RangeInput)


@register.filter
def is_phone(field):
    return isinstance(field.field.widget, PhoneNumberInternationalFallbackWidget)


@register.filter
def is_file_tree(field):
    return isinstance(field.field.widget, mal2_forms.FileTree)


@register.filter
def get_col_class(attrs):
    col_class = attrs.get("data-col")
    attrs.pop("data-col", None)

    return col_class


################################################################################
# FORM SET

@register.simple_tag
def get_formset(formsets, field):
    for formset in formsets:
        if formset[0] == field.name:
            yield formset[1]


@register.filter
def get_formset_title(formset):
    return formset.model._meta.verbose_name_plural
