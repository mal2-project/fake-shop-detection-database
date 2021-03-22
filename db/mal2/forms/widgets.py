import os

from babel import Locale
from django.conf import settings
from django.forms import widgets
from django.utils.translation import (
    get_language,
    gettext_lazy as _,
    to_locale,
)
from phonenumber_field.phonenumber import PhoneNumber
from phonenumbers.data import _COUNTRY_CODE_TO_REGION_CODE


################################################################################
# RANGE

class RangeInput(widgets.Input):
    input_type = "range"
    template_name = "django/forms/widgets/range.html"


################################################################################
# DATE/TIME

class DateInput(widgets.DateInput):
    input_type = "date"


class TimeInput(widgets.TimeInput):
    input_type = "time"


################################################################################
# FILE

class ClearableFileInput(widgets.ClearableFileInput):
    clear_checkbox_label = _("clear")

    def get_context(self, name, value, attrs):
        context = super().get_context(name, value, attrs)

        widget = context["widget"]

        widget.update({
            "file_name": os.path.basename(
                str(widget["value"])
            ),
        })

        return context


################################################################################
# SELECT

class Select(widgets.Select):
    """
    https://www.abidibo.net/blog/2017/10/16/add-data-attributes-option-tags-django-admin-select-field/
    https://www.djangosnippets.org/snippets/2453/
    """

    template_name = "django/forms/widgets/select.html"
    option_template_name = "django/forms/widgets/select_option.html"

    def __init__(self, attrs=None, choices=(), data=None):
        super().__init__(attrs, choices)

        self.data = data

    def create_option(self, name, value, label, selected, index, subindex=None, attrs=None):
        disabled = False

        if isinstance(label, dict):
            label, disabled = label["label"], label["disabled"]

        option = super().create_option(name, value, label, selected, index, subindex=None, attrs=None)

        if disabled:
            option["attrs"]["disabled"] = "disabled"

        # Adds the data-attributes to the attrs context var

        if self.data:
            for data_attr, values in self.data.items():
                values = values.get(option["value"])

                if values is not None:
                    option["attrs"][data_attr] = values

        return option


################################################################################
# RADIO

class InlineRadioSelect(widgets.RadioSelect):
    template_name = "django/forms/widgets/inline_radio.html"
    option_template_name = "django/forms/widgets/inline_radio_option.html"


################################################################################
# CHECKBOX

class InlineCheckboxMultiple(widgets.CheckboxSelectMultiple):
    option_template_name = "django/forms/widgets/checkbox_option_inline.html"


################################################################################
# PHONE NUMBER

class PhonePrefixSelect(widgets.Select):
    initial = None

    def __init__(self, attrs=None, initial=None):
        choices = [("", "---------")]
        language = get_language() or settings.LANGUAGE_CODE

        if language:
            locale = Locale(to_locale(language))

            for prefix, values in _COUNTRY_CODE_TO_REGION_CODE.items():
                prefix = "+%d" % prefix

                if initial and initial in values:
                    self.initial = prefix

                for country_code in values:
                    country_name = locale.territories.get(country_code)

                    if country_name:
                        choices.append(
                            (prefix, "{} {}".format(country_name, prefix))
                        )

        super().__init__(
            attrs=attrs, choices=sorted(choices, key=lambda item: item[1])
        )

    def render(self, name, value, *args, **kwargs):
        return super().render(name, value or self.initial, *args, **kwargs)


class PhoneNumberPrefixWidget(widgets.MultiWidget):
    def __init__(self, attrs=None, initial=None):
        phone_number_widgets = (
            PhonePrefixSelect(
                attrs={
                    "aria-label": _("Country code"),
                },
                initial=initial
            ),
            widgets.TextInput(
                attrs={
                    "aria-label": _("Phone number"),
                },
            )
        )

        super().__init__(phone_number_widgets, attrs)

    def decompress(self, value):
        if value:
            if type(value) == PhoneNumber:
                if value.country_code and value.national_number:
                    return ["+%d" % value.country_code, value.national_number]
            else:
                return value.split(".")

        return [None, ""]

    def value_from_datadict(self, data, files, name):
        values = super().value_from_datadict(data, files, name)

        if all(values):
            return "%s.%s" % tuple(values)

        return ""


################################################################################
# TINY MCE

class TincyMCE(widgets.Textarea):
    def __init__(self, attrs=None):
        super().__init__(attrs)

        default_attrs = {
            "cols": "40",
            "rows": "10",
            "data-html-textarea": "1",
        }

        if attrs:
            default_attrs.update(attrs)

        super().__init__(default_attrs)


################################################################################
# FILE TREE

class FileTree(widgets.TextInput):
    def __init__(self, attrs=None):
        if not attrs:
            attrs = {}

        attrs.update({
            "readonly": "",
        })

        super().__init__(attrs)
